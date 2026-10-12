"""A deliberately small Redfish-shaped HTTP simulator and a real workload emitter."""

from __future__ import annotations

import asyncio
import re
import time
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from opentelemetry._logs import SeverityNumber
from opentelemetry.trace import Status, StatusCode

from .model import resource
from .runtime import LabRegistry


def error(message, status=400):
    return JSONResponse(
        {"error": {"code": "Lab.1.0.Error", "message": message}}, status_code=status
    )


def image_url(value):
    if (
        not isinstance(value, str)
        or urlparse(value).scheme != "https"
        or not urlparse(value).netloc
    ):
        raise ValueError(
            "Use an https:// image URL. The simulator records it without downloading it."
        )
    return value


def make_api(registry: LabRegistry | None = None, background=True):
    registry = registry or LabRegistry()

    @asynccontextmanager
    async def lifespan(app):
        runner = asyncio.create_task(registry.run()) if background else None
        yield
        registry.stop.set()
        if runner:
            await runner
        registry.close()

    app = FastAPI(title="Redfish Observatory API", version="0.1.0", lifespan=lifespan)
    app.state.registry = registry
    registry.app = app

    def session(request):
        return registry.get(request.headers.get("X-Lab-Session", "public-demo"), touch=False)

    @app.get("/healthz")
    async def health():
        return {"status": "ok", "hardware": "simulated", "telemetry": "real OpenTelemetry SDK"}

    @app.post("/lab/scenario")
    async def scenario(request: Request):
        s = session(request)
        try:
            body = await request.json()
            if "fault" in body:
                s.model.set_fault(body["fault"])
            if "load" in body:
                load = int(body["load"])
                if not 0 <= load <= 100:
                    raise ValueError("Load must be between 0 and 100")
                s.model.cpu_load = load
        except (ValueError, TypeError) as exc:
            return error(str(exc))
        return s.model.snapshot()

    @app.get("/lab/snapshot")
    async def snapshot(request: Request):
        s = session(request)
        return {
            "hardware": s.model.snapshot(),
            "telemetry": s.bridge.buffer.snapshot(),
            "transport": s.mode,
        }

    @app.post("/ingest/redfish/{session_id}")
    async def receive_redfish(session_id: str, request: Request):
        # Internal teaching callback. Never forwards to arbitrary external destinations.
        if request.headers.get("X-Lab-Session", "public-demo") != session_id:
            return error("Callback belongs to another lab session", 403)
        s = registry.get(session_id, touch=False)
        payload = await request.json()
        if "MetricValues" in payload:
            values = {}
            keys = {"CPU1Temp": "temperature", "Fan1": "fan_rpm", "SystemPower": "power_watts"}
            for metric in payload["MetricValues"]:
                if metric["MetricId"] in keys:
                    values[keys[metric["MetricId"]]] = float(metric["MetricValue"])
            values["health_code"] = {"OK": 0, "Warning": 1, "Critical": 2}[s.model.health]
            source_time = payload.get("MetricValues", [{}])[0].get("Timestamp")
            s.bridge.hardware(values, "Pushed metric report", source_time)
        elif "Events" in payload:
            for entry in payload["Events"]:
                s.bridge.event(entry, "HTTP event callback")
        else:
            return error("Expected Redfish Events or MetricValues")
        return {"accepted": True}

    @app.get("/workload/checkout")
    async def checkout(request: Request):
        s = session(request)
        data = s.model.snapshot()
        start = time.perf_counter()
        status = 200 if data["os_running"] else 503
        with s.bridge.tracer.start_as_current_span("checkout.request") as root:
            root.set_attribute("http.route", "/workload/checkout")
            root.set_attribute("http.response.status_code", status)
            root.set_attribute("lab.physical_server.id", "SIM-R42-0001")
            if status == 200:
                with s.bridge.tracer.start_as_current_span("inventory.lookup"):
                    await asyncio.sleep(data["latency_ms"] * 0.30 / 1000)
                with s.bridge.tracer.start_as_current_span("database.write"):
                    await asyncio.sleep(data["latency_ms"] * 0.70 / 1000)
            else:
                root.set_status(Status(StatusCode.ERROR, "Simulated host unavailable"))
                s.bridge.logger.emit(
                    body="Checkout unavailable: simulated host OS is down",
                    severity_number=SeverityNumber.ERROR,
                    severity_text="ERROR",
                    attributes={"http.response.status_code": 503},
                )
            elapsed = time.perf_counter() - start
            s.bridge.record_request(elapsed, status)
            if status == 200 and elapsed > 0.20:
                s.bridge.logger.emit(
                    body="Checkout request exceeded the demo 200 ms budget",
                    severity_number=SeverityNumber.WARN,
                    severity_text="WARN",
                    attributes={"duration_ms": round(elapsed * 1000, 2)},
                )
            trace_id = f"{root.get_span_context().trace_id:032x}"
        return JSONResponse(
            {
                "status": "ok" if status == 200 else "host-unavailable",
                "duration_ms": round(elapsed * 1000, 2),
                "trace_id": trace_id,
                "host": "server-42",
                "simulated": True,
            },
            status_code=status,
        )

    @app.api_route("/redfish/v1", methods=["GET"])
    @app.api_route("/redfish/v1/{rest:path}", methods=["GET", "POST", "PATCH", "DELETE"])
    async def redfish(request: Request, rest: str = ""):
        s = session(request)
        model = s.model
        path = request.url.path.rstrip("/")
        method = request.method
        role = request.headers.get("X-Lab-Role", "Administrator")
        if role not in {"Administrator", "Operator", "ReadOnly"}:
            return error("Unknown teaching role", 403)
        if method != "GET":
            if role == "ReadOnly":
                return error("ReadOnly role can inspect resources but cannot change them", 403)
            if role == "Operator" and not (
                "ComputerSystem.Reset" in path or "/VirtualMedia/" in path
            ):
                return error("This simulated action requires the Administrator role", 403)
        try:
            if method == "GET":
                return JSONResponse(model.read(path), headers={"OData-Version": "4.0"})
            body = await request.json() if method != "DELETE" else {}
            with model.lock:
                if method == "POST" and path.endswith("/Actions/ComputerSystem.Reset"):
                    model.reset(body["ResetType"])
                    return Response(status_code=204)
                if method == "PATCH" and path == "/redfish/v1/Chassis/1/Power":
                    watts = body["PowerControl"][0]["PowerLimit"]["LimitInWatts"]
                    if (
                        isinstance(watts, bool)
                        or not isinstance(watts, int)
                        or not 150 <= watts <= 600
                    ):
                        raise ValueError("Power limit must be an integer between 150 and 600 W")
                    model.power_limit = watts
                    model.emit(f"Power cap set to {watts} W")
                    return Response(status_code=204)
                if method == "PATCH" and path == "/redfish/v1/Systems/1/Bios/Settings":
                    attrs = body["Attributes"]
                    allowed = {
                        "ProcVirtualization": {"Enabled", "Disabled"},
                        "BootMode": {"Uefi", "LegacyBios"},
                    }
                    if not attrs or any(
                        k not in allowed or v not in allowed[k] for k, v in attrs.items()
                    ):
                        raise ValueError("Invalid simulated BIOS setting")
                    model.pending_bios.update(attrs)
                    model.emit("BIOS settings staged; restart the server to apply them")
                    return Response(status_code=204)
                if method == "PATCH" and path == "/redfish/v1/Systems/1":
                    boot = body["Boot"]
                    if boot.get("BootSourceOverrideTarget") not in {"Hdd", "Pxe", "Cd", "Usb"}:
                        raise ValueError("Choose Hdd, Pxe, Cd or Usb")
                    if boot.get("BootSourceOverrideEnabled", "Once") not in {"Once", "Disabled"}:
                        raise ValueError("Boot override must be Once or Disabled")
                    model.boot_target = boot["BootSourceOverrideTarget"]
                    model.boot_enabled = boot.get("BootSourceOverrideEnabled", "Once")
                    model.emit(f"Next boot source set to {model.boot_target}")
                    return Response(status_code=204)
                if (
                    method == "POST"
                    and path == "/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate"
                ):
                    image_url(body["ImageURI"])
                    version = body.get("Oem", {}).get("Lab", {}).get("Version", "2.1.0")
                    if not re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,3}", version):
                        raise ValueError("Use a version such as 2.1.0")
                    task = model.start_task(
                        "firmware", f"BMC firmware update to {version}", version
                    )
                    return JSONResponse(
                        task,
                        status_code=202,
                        headers={"Location": task["@odata.id"], "Retry-After": "1"},
                    )
                if method == "POST" and path.endswith(
                    "/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia"
                ):
                    model.media = image_url(body["Image"])
                    model.emit("Installer image attached as a virtual DVD; no file is downloaded")
                    return Response(status_code=204)
                if method == "POST" and path.endswith(
                    "/VirtualMedia/CD/Actions/VirtualMedia.EjectMedia"
                ):
                    model.media = None
                    model.emit("Virtual installer ejected")
                    return Response(status_code=204)
                if method == "POST" and path == "/redfish/v1/Systems/1/Storage/1/Volumes":
                    name = body["Name"]
                    raid = body["RAIDType"]
                    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name) or raid not in {
                        "RAID0",
                        "RAID1",
                    }:
                        raise ValueError("Use a short volume name and RAID0 or RAID1")
                    if any(v["Name"] == name for v in model.volumes):
                        raise ValueError("A volume with that name already exists")
                    if len(model.volumes) >= 8:
                        raise ValueError("Demo volume limit reached")
                    volume = {
                        "Id": str(len(model.volumes) + 1),
                        "Name": name,
                        "RAIDType": raid,
                        "CapacityBytes": 256_000_000_000,
                    }
                    model.volumes.append(volume)
                    model.emit(f"Simulated {raid} volume {name} created")
                    uri = path + "/" + volume["Id"]
                    return JSONResponse(
                        resource("Volume.v1_10_0.Volume", uri, **volume),
                        status_code=201,
                        headers={"Location": uri},
                    )
                if method == "POST" and path == "/redfish/v1/AccountService/Accounts":
                    name = body["UserName"]
                    selected_role = body["RoleId"]
                    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name) or selected_role not in {
                        "Administrator",
                        "Operator",
                        "ReadOnly",
                    }:
                        raise ValueError("Use a short username and a supported role")
                    if any(a["UserName"] == name for a in model.accounts):
                        raise ValueError("An account with that username already exists")
                    if len(model.accounts) >= 12:
                        raise ValueError("Demo account limit reached")
                    account = {
                        "Id": str(len(model.accounts) + 1),
                        "UserName": name,
                        "RoleId": selected_role,
                        "Enabled": True,
                    }
                    model.accounts.append(account)  # Passwords are never retained or returned.
                    model.emit(f"Demo account {name} created with {selected_role} permissions")
                    uri = path + "/" + account["Id"]
                    return JSONResponse(
                        resource("ManagerAccount.v1_13_0.ManagerAccount", uri, **account),
                        status_code=201,
                        headers={"Location": uri},
                    )
                if method == "POST" and path == "/redfish/v1/EventService/Subscriptions":
                    expected = f"http://lab.local/ingest/redfish/{s.id}"
                    if body["Destination"] != expected:
                        raise ValueError("The simulator only delivers to its internal lab callback")
                    if len(model.subscriptions) >= 1:
                        raise ValueError("A demo callback subscription already exists")
                    model.subscriptions["1"] = {
                        "Destination": expected,
                        "Protocol": "Redfish",
                        "Context": body.get("Context", "lab"),
                    }
                    uri = path + "/1"
                    return JSONResponse(model.read(uri), status_code=201, headers={"Location": uri})
                if method == "DELETE" and path.startswith(
                    "/redfish/v1/EventService/Subscriptions/"
                ):
                    sid = path.split("/")[-1]
                    if sid not in model.subscriptions:
                        return error("Subscription not found", 404)
                    del model.subscriptions[sid]
                    return Response(status_code=204)
                if (
                    method == "PATCH"
                    and path == "/redfish/v1/TelemetryService/MetricReportDefinitions/LiveHardware"
                ):
                    interval = body.get("Schedule", {}).get("RecurrenceInterval")
                    if interval is not None:
                        match = re.fullmatch(r"PT(\d+(?:\.\d+)?)S", interval)
                        if not match or not 1 <= float(match[1]) <= 60:
                            raise ValueError("Demo report interval must be PT1S through PT60S")
                        model.telemetry_interval = float(match[1])
                    if "MetricReportDefinitionEnabled" in body:
                        if not isinstance(body["MetricReportDefinitionEnabled"], bool):
                            raise ValueError("Enabled must be a boolean")
                        model.telemetry_enabled = body["MetricReportDefinitionEnabled"]
                    return Response(status_code=204)
                return error("This method/resource combination is outside the teaching subset", 405)
        except KeyError as exc:
            return error(
                f"Resource or required property not found: {exc.args[0]}",
                404 if method == "GET" else 400,
            )
        except (ValueError, TypeError, IndexError) as exc:
            return error(str(exc))

    return app
