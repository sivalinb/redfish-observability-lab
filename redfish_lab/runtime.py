"""Session isolation and a background gateway independent of the simulated host OS."""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from dataclasses import dataclass, field

import httpx

from .model import ServerModel
from .telemetry import TelemetryBridge


@dataclass
class LabSession:
    id: str
    model: ServerModel
    bridge: TelemetryBridge
    mode: str = "Polling + push"
    polling_interval: float = 3.0
    last_poll: float = 0.0
    touched: float = field(default_factory=time.monotonic)
    last_workload: dict = field(default_factory=dict)
    traffic: list = field(default_factory=list)
    note: str = "Welcome. Try a scenario, then watch the hardware and telemetry change."


class LabRegistry:
    def __init__(self, otlp_endpoint=None):
        self.sessions = {}
        self.lock = threading.RLock()
        self.otlp_endpoint = otlp_endpoint
        self.app = None
        self.stop = asyncio.Event()

    def get(self, session_id=None, touch=True):
        session_id = session_id or "public-demo"
        with self.lock:
            if session_id not in self.sessions:
                # Session keys are unguessable for the UI; the default is intentionally a public lab.
                if len(self.sessions) >= 32:
                    oldest = min(self.sessions.values(), key=lambda s: s.touched)
                    self.sessions.pop(oldest.id).bridge.shutdown()
                model = ServerModel(session_id)
                self.sessions[session_id] = LabSession(
                    session_id, model, TelemetryBridge(session_id, otlp_endpoint=self.otlp_endpoint)
                )
                model.emit("BMC online. Your private simulated rack is ready")
            session = self.sessions[session_id]
            if touch:
                session.touched = time.monotonic()
            return session

    def new(self):
        return self.get(uuid.uuid4().hex)

    async def request(self, session, method, path, body=None, role="Administrator", record=True):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.app), base_url="http://lab.local"
        ) as client:
            start = time.monotonic()
            response = await client.request(
                method, path, json=body, headers={"X-Lab-Session": session.id, "X-Lab-Role": role}
            )
            if record:
                item = {
                    "method": method,
                    "path": path,
                    "body": body,
                    "status": response.status_code,
                    "headers": {
                        key: response.headers[key]
                        for key in ("location", "retry-after", "odata-version")
                        if key in response.headers
                    },
                    "response": response.json() if response.content else {},
                    "elapsed_ms": round((time.monotonic() - start) * 1000, 1),
                }
                session.model.last_request = item
                session.traffic.append(item)
                session.traffic[:] = session.traffic[-20:]
            return response

    async def set_transport(self, session, mode, interval):
        session.mode = mode
        session.polling_interval = float(interval)
        session.model.telemetry_interval = float(interval)
        if mode == "Polling only":
            for sid in list(session.model.subscriptions):
                await self.request(
                    session, "DELETE", f"/redfish/v1/EventService/Subscriptions/{sid}"
                )
        elif not session.model.subscriptions:
            await self.request(
                session,
                "POST",
                "/redfish/v1/EventService/Subscriptions",
                {
                    "Destination": f"http://lab.local/ingest/redfish/{session.id}",
                    "Protocol": "Redfish",
                    "Context": "opentelemetry-bridge",
                },
            )

    async def poll(self, session):
        system = (await self.request(session, "GET", "/redfish/v1/Systems/1", record=False)).json()
        thermal = (
            await self.request(session, "GET", "/redfish/v1/Chassis/1/Thermal", record=False)
        ).json()
        power = (
            await self.request(session, "GET", "/redfish/v1/Chassis/1/Power", record=False)
        ).json()
        session.bridge.hardware(
            {
                "temperature": thermal["Temperatures"][0]["ReadingCelsius"],
                "fan_rpm": thermal["Fans"][0]["Reading"],
                "power_watts": power["PowerControl"][0]["PowerConsumedWatts"],
                "health_code": {"OK": 0, "Warning": 1, "Critical": 2}[system["Status"]["Health"]],
            },
            "REST polling",
            source_time=session.model.snapshot()["sample_time"],
        )
        logs = (
            await self.request(
                session, "GET", "/redfish/v1/Managers/1/LogServices/Hardware/Entries", record=False
            )
        ).json()
        for entry in logs["Members"]:
            session.bridge.event(entry, "REST polling")

    async def step(self, session, now=None):
        now = time.monotonic() if now is None else now
        session.model.tick(now)
        if session.mode != "Polling only" and not session.model.subscriptions:
            await self.set_transport(session, session.mode, session.polling_interval)
        pending = []
        with session.model.lock:
            while session.model.outbox:
                pending.append(session.model.outbox.popleft())
        for item in pending:
            if session.mode == "Polling only":
                continue
            if item["kind"] == "metric" and session.mode != "Push reports + events":
                continue
            for subscription in list(session.model.subscriptions.values()):
                path = httpx.URL(subscription["Destination"]).path
                await self.request(session, "POST", path, item["payload"], record=False)
        if (
            session.mode != "Push reports + events"
            and now - session.last_poll >= session.polling_interval
        ):
            session.last_poll = now
            await self.poll(session)
        response = await self.request(session, "GET", "/workload/checkout", record=False)
        session.last_workload = response.json()

    async def run(self):
        while not self.stop.is_set():
            start = time.monotonic()
            with self.lock:
                expired = [
                    sid
                    for sid, s in self.sessions.items()
                    if sid != "public-demo" and start - s.touched > 1800
                ]
                for sid in expired:
                    self.sessions.pop(sid).bridge.shutdown()
                active = list(self.sessions.values())
            await asyncio.gather(*(self.step(s) for s in active))
            try:
                await asyncio.wait_for(
                    self.stop.wait(), timeout=max(0.1, 1 - (time.monotonic() - start))
                )
            except asyncio.TimeoutError:
                pass

    def close(self):
        self.stop.set()
        with self.lock:
            for session in self.sessions.values():
                session.bridge.shutdown()
            self.sessions.clear()
