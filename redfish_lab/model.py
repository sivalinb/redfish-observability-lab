"""Deterministic teaching model. No methods in this module touch real hardware."""

from __future__ import annotations

import math
import threading
import time
from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def resource(kind: str, path: str, **data: Any) -> dict:
    return {"@odata.type": f"#{kind}", "@odata.id": path, **data}


def collection(kind: str, path: str, members: list[str]) -> dict:
    return resource(
        f"{kind}Collection.{kind}Collection",
        path,
        Name=f"{kind} collection",
        Members=[{"@odata.id": uri} for uri in members],
        **{"Members@odata.count": len(members)},
    )


@dataclass
class ServerModel:
    session_id: str
    temperature: float = 49.0
    cpu_load: int = 40
    power_state: str = "On"
    power_limit: int = 450
    fault: str = "Healthy"
    firmware: str = "2.0.0"
    bios: dict = field(
        default_factory=lambda: {"ProcVirtualization": "Enabled", "BootMode": "Uefi"}
    )
    pending_bios: dict = field(default_factory=dict)
    boot_target: str = "Hdd"
    boot_enabled: str = "Disabled"
    media: str | None = None
    installed_os: str = "Demo Linux"
    os_running: bool = True
    volumes: list = field(
        default_factory=lambda: [
            {
                "Id": "1",
                "Name": "system-volume",
                "RAIDType": "RAID1",
                "CapacityBytes": 512_000_000_000,
            },
        ]
    )
    accounts: list = field(
        default_factory=lambda: [
            {"Id": "1", "UserName": "lab-admin", "RoleId": "Administrator", "Enabled": True},
        ]
    )
    events: deque = field(default_factory=lambda: deque(maxlen=120))
    outbox: deque = field(default_factory=lambda: deque(maxlen=500))
    tasks: dict = field(default_factory=dict)
    subscriptions: dict = field(default_factory=dict)
    telemetry_interval: float = 3.0
    telemetry_enabled: bool = True
    last_report: float = 0.0
    sensor_sampled_at: str = field(default_factory=utcnow)
    ticks: int = 0
    event_seq: int = 0
    task_seq: int = 0
    high_temperature_reported: bool = False
    last_request: dict = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    @property
    def host_name(self) -> str:
        return "server-42"

    @property
    def health(self) -> str:
        if self.fault in {"Fan failure", "Power supply failure", "Disk failure"}:
            return "Critical"
        return "Warning" if self.temperature >= 75 else "OK"

    @property
    def fan_rpm(self) -> int:
        if self.power_state == "Off" or self.fault == "Fan failure":
            return 0
        return int(2600 + max(0, self.temperature - 40) * 65)

    @property
    def power_watts(self) -> float:
        if self.power_state == "Off":
            return 12.0  # BMC standby power remains present in this teaching model.
        return round(min(self.power_limit, 95 + self.cpu_load * 3.4), 1)

    @property
    def latency_ms(self) -> float:
        return round(25 + self.cpu_load * 0.6 + max(0, self.temperature - 68) * 12, 1)

    def emit(self, message: str, severity: str = "OK", origin: str = "/redfish/v1/Systems/1"):
        self.event_seq += 1
        entry = {
            "EventId": str(self.event_seq),
            "MemberId": str(self.event_seq),
            "EventTimestamp": utcnow(),
            "Severity": severity,
            "MessageId": f"Lab.1.0.{severity}",
            "Message": message,
            "OriginOfCondition": {"@odata.id": origin},
        }
        self.events.append(entry)
        self.outbox.append(
            {
                "kind": "event",
                "payload": {
                    "@odata.type": "#Event.v1_10_0.Event",
                    "Id": str(self.event_seq),
                    "Name": "Simulated Redfish event",
                    "Events": [deepcopy(entry)],
                },
            }
        )

    def set_fault(self, fault: str):
        if fault not in {
            "Healthy",
            "Fan failure",
            "Power supply failure",
            "Disk failure",
            "OS crash",
        }:
            raise ValueError("Unknown scenario")
        with self.lock:
            if self.fault == fault:
                return
            self.fault = fault
            self.os_running = self.power_state == "On" and fault != "OS crash"
            self.emit(
                "Hardware recovered; normal cooling restored"
                if fault == "Healthy"
                else f"{fault} detected on {self.host_name}",
                "OK" if fault == "Healthy" else "Critical",
            )

    def tick(self, now: float | None = None):
        now = time.monotonic() if now is None else now
        with self.lock:
            self.ticks += 1
            target = 27 if self.power_state == "Off" else 38 + self.cpu_load * 0.30
            if self.fault == "Fan failure" and self.power_state == "On":
                target += 42
            self.temperature += max(-2.0, min(2.5, (target - self.temperature) * 0.14))
            self.temperature += math.sin(self.ticks / 4) * 0.12
            self.temperature = round(self.temperature, 2)
            self.sensor_sampled_at = utcnow()
            if self.temperature >= 75 and not self.high_temperature_reported:
                self.high_temperature_reported = True
                self.emit("CPU temperature exceeded the demo 75 °C threshold", "Warning")
            elif self.temperature < 70 and self.high_temperature_reported:
                self.high_temperature_reported = False
                self.emit("CPU temperature returned below 70 °C", "OK")
            for task in self.tasks.values():
                if task["TaskState"] != "Running":
                    continue
                elapsed = max(0, now - task["_started"])
                task["PercentComplete"] = min(100, int(elapsed / task["_duration"] * 100))
                if task["PercentComplete"] == 100:
                    task["TaskState"] = "Completed"
                    task["TaskStatus"] = "OK"
                    if task["_kind"] == "firmware":
                        self.firmware = task["_value"]
                    elif task["_kind"] == "os-install":
                        self.installed_os = task["_value"]
                        self.os_running = self.power_state == "On" and self.fault != "OS crash"
                    self.emit(f"{task['Name']} completed successfully")
            if self.telemetry_enabled and now - self.last_report >= self.telemetry_interval:
                self.last_report = now
                self.outbox.append({"kind": "metric", "payload": self.metric_report()})

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "host": self.host_name,
                "temperature": self.temperature,
                "fan_rpm": self.fan_rpm,
                "power_watts": self.power_watts,
                "power_limit": self.power_limit,
                "cpu_load": self.cpu_load,
                "latency_ms": self.latency_ms,
                "power_state": self.power_state,
                "health": self.health,
                "fault": self.fault,
                "os_running": self.os_running,
                "installed_os": self.installed_os,
                "firmware": self.firmware,
                "bios": deepcopy(self.bios),
                "pending_bios": deepcopy(self.pending_bios),
                "boot_target": self.boot_target,
                "media": self.media,
                "volumes": deepcopy(self.volumes),
                "accounts": deepcopy(self.accounts),
                "events": deepcopy(list(self.events)),
                "tasks": [self.public_task(t) for t in self.tasks.values()],
                "subscriptions": len(self.subscriptions),
                "sample_time": self.sensor_sampled_at,
            }

    def public_task(self, task: dict) -> dict:
        return {k: deepcopy(v) for k, v in task.items() if not k.startswith("_")}

    def start_task(self, kind: str, name: str, value: str, now: float | None = None) -> dict:
        if any(t["TaskState"] == "Running" and t["_kind"] == kind for t in self.tasks.values()):
            raise ValueError(f"A {kind} task is already running")
        self.task_seq += 1
        tid = str(self.task_seq)
        task = resource(
            "Task.v1_7_4.Task",
            f"/redfish/v1/TaskService/Tasks/{tid}",
            Id=tid,
            Name=name,
            TaskState="Running",
            TaskStatus="OK",
            PercentComplete=0,
            StartTime=utcnow(),
            _kind=kind,
            _value=value,
            _started=time.monotonic() if now is None else now,
            _duration=6.0,
        )
        self.tasks[tid] = task
        self.emit(f"{name} scheduled")
        return self.public_task(task)

    def reset(self, reset_type: str):
        with self.lock:
            if reset_type in {"On", "ForceOn"}:
                self.power_state = "On"
            elif reset_type in {"ForceOff", "GracefulShutdown"}:
                self.power_state = "Off"
            elif reset_type not in {"GracefulRestart", "ForceRestart"}:
                raise ValueError("Unsupported ResetType")
            if reset_type in {"GracefulRestart", "ForceRestart"}:
                if self.power_state == "Off":
                    raise ValueError("Turn the server on before restarting it")
                self.bios.update(self.pending_bios)
                self.pending_bios.clear()
            self.os_running = self.power_state == "On" and self.fault != "OS crash"
            if self.media and self.boot_enabled == "Once" and self.boot_target in {"Cd", "Usb"}:
                if self.power_state == "On":
                    self.start_task(
                        "os-install", "Demo operating system installation", "Fresh Demo Linux"
                    )
                    self.boot_enabled = "Disabled"
            self.emit(f"Power action: {reset_type}. BMC management remains available")

    def metric_report(self) -> dict:
        stamp = utcnow()
        return resource(
            "MetricReport.v1_5_1.MetricReport",
            "/redfish/v1/TelemetryService/MetricReports/LiveHardware",
            Id="LiveHardware",
            Name="Simulated hardware readings",
            Timestamp=stamp,
            MetricReportDefinition={
                "@odata.id": "/redfish/v1/TelemetryService/MetricReportDefinitions/LiveHardware"
            },
            MetricValues=[
                {
                    "MetricId": name,
                    "MetricValue": str(value),
                    "Timestamp": self.sensor_sampled_at,
                    "MetricProperty": f"/redfish/v1/Chassis/1/Sensors/{name}#/Reading",
                }
                for name, value in [
                    ("CPU1Temp", self.temperature),
                    ("Fan1", self.fan_rpm),
                    ("SystemPower", self.power_watts),
                ]
            ],
        )

    def read(self, path: str) -> dict:
        """Return a representative subset of Redfish resources, not a conformant service."""
        with self.lock:
            status = {"State": "Enabled", "Health": self.health}
            if path == "/redfish/v1":
                return resource(
                    "ServiceRoot.v1_17_0.ServiceRoot",
                    path,
                    Id="RootService",
                    Name="Redfish Observatory simulator",
                    RedfishVersion="1.20.0",
                    **{
                        name: {"@odata.id": f"/redfish/v1/{name}"}
                        for name in [
                            "Systems",
                            "Chassis",
                            "Managers",
                            "UpdateService",
                            "TaskService",
                            "AccountService",
                            "EventService",
                            "TelemetryService",
                        ]
                    },
                )
            if path in {"/redfish/v1/Systems", "/redfish/v1/Chassis", "/redfish/v1/Managers"}:
                kind = {"Systems": "ComputerSystem", "Chassis": "Chassis", "Managers": "Manager"}[
                    path.split("/")[-1]
                ]
                return collection(kind, path, [path + "/1"])
            if path == "/redfish/v1/Systems/1":
                return resource(
                    "ComputerSystem.v1_22_0.ComputerSystem",
                    path,
                    Id="1",
                    Name=self.host_name,
                    HostName=self.host_name,
                    Manufacturer="Learning Lab",
                    Model="Atlas R42",
                    SerialNumber="SIM-R42-0001",
                    PowerState=self.power_state,
                    Status=status,
                    BiosVersion="1.8.0",
                    ProcessorSummary={"Count": 2, "Model": "Simulated 16-core CPU"},
                    MemorySummary={"TotalSystemMemoryGiB": 128},
                    Boot={
                        "BootSourceOverrideTarget": self.boot_target,
                        "BootSourceOverrideEnabled": self.boot_enabled,
                    },
                    Bios={"@odata.id": path + "/Bios"},
                    Storage={"@odata.id": path + "/Storage"},
                    Actions={
                        "#ComputerSystem.Reset": {"target": path + "/Actions/ComputerSystem.Reset"}
                    },
                )
            if path == "/redfish/v1/Chassis/1":
                return resource(
                    "Chassis.v1_25_0.Chassis",
                    path,
                    Id="1",
                    Name="Rack 07 • Unit 12",
                    ChassisType="RackMount",
                    Manufacturer="Learning Lab",
                    Model="Atlas R42",
                    SerialNumber="SIM-R42-0001",
                    PowerState=self.power_state,
                    Status=status,
                    Sensors={"@odata.id": path + "/Sensors"},
                    Thermal={"@odata.id": path + "/Thermal"},
                    Power={"@odata.id": path + "/Power"},
                )
            if path == "/redfish/v1/Chassis/1/Sensors":
                return collection(
                    "Sensor", path, [path + "/" + x for x in ["CPU1Temp", "Fan1", "SystemPower"]]
                )
            if path.startswith("/redfish/v1/Chassis/1/Sensors/"):
                sid = path.split("/")[-1]
                sensor = {
                    "CPU1Temp": ("Temperature", "Cel", self.temperature),
                    "Fan1": ("Rotational", "RPM", self.fan_rpm),
                    "SystemPower": ("Power", "W", self.power_watts),
                }
                if sid in sensor:
                    kind, units, value = sensor[sid]
                    return resource(
                        "Sensor.v1_9_0.Sensor",
                        path,
                        Id=sid,
                        Name=sid,
                        ReadingType=kind,
                        ReadingUnits=units,
                        Reading=value,
                        Status=status,
                    )
            if path == "/redfish/v1/Chassis/1/Thermal":
                return resource(
                    "Thermal.v1_7_3.Thermal",
                    path,
                    Id="Thermal",
                    Name="Cooling",
                    Temperatures=[
                        {
                            "MemberId": "CPU1Temp",
                            "Name": "CPU 1",
                            "ReadingCelsius": self.temperature,
                            "Status": status,
                        }
                    ],
                    Fans=[
                        {
                            "MemberId": "Fan1",
                            "Name": "Fan 1",
                            "Reading": self.fan_rpm,
                            "ReadingUnits": "RPM",
                            "Status": status,
                        }
                    ],
                )
            if path == "/redfish/v1/Chassis/1/Power":
                return resource(
                    "Power.v1_7_3.Power",
                    path,
                    Id="Power",
                    Name="Power",
                    PowerControl=[
                        {
                            "MemberId": "0",
                            "PowerConsumedWatts": self.power_watts,
                            "PowerLimit": {"LimitInWatts": self.power_limit},
                        }
                    ],
                    PowerSupplies=[
                        {
                            "MemberId": "PSU1",
                            "Status": {
                                "State": "Enabled",
                                "Health": "Critical"
                                if self.fault == "Power supply failure"
                                else "OK",
                            },
                        }
                    ],
                )
            if path == "/redfish/v1/Systems/1/Bios":
                return resource(
                    "Bios.v1_2_3.Bios",
                    path,
                    Id="Bios",
                    Name="Startup settings",
                    Attributes=deepcopy(self.bios),
                    **{"@Redfish.Settings": {"SettingsObject": {"@odata.id": path + "/Settings"}}},
                )
            if path == "/redfish/v1/Systems/1/Bios/Settings":
                return resource(
                    "Bios.v1_2_3.Bios",
                    path,
                    Id="Settings",
                    Name="Pending settings",
                    Attributes={**self.bios, **self.pending_bios},
                )
            if path == "/redfish/v1/Managers/1":
                return resource(
                    "Manager.v1_20_0.Manager",
                    path,
                    Id="1",
                    Name="BMC",
                    ManagerType="BMC",
                    FirmwareVersion=self.firmware,
                    PowerState="On",
                    Status={"State": "Enabled", "Health": "OK"},
                    VirtualMedia={"@odata.id": path + "/VirtualMedia"},
                    LogServices={"@odata.id": path + "/LogServices"},
                )
            if path == "/redfish/v1/Managers/1/VirtualMedia":
                return collection("VirtualMedia", path, [path + "/CD"])
            if path == "/redfish/v1/Managers/1/VirtualMedia/CD":
                return resource(
                    "VirtualMedia.v1_6_4.VirtualMedia",
                    path,
                    Id="CD",
                    Name="Virtual installer",
                    Inserted=bool(self.media),
                    Image=self.media,
                    MediaTypes=["CD", "DVD"],
                )
            if path == "/redfish/v1/Systems/1/Storage":
                return collection("Storage", path, [path + "/1"])
            if path == "/redfish/v1/Systems/1/Storage/1":
                return resource(
                    "Storage.v1_16_0.Storage",
                    path,
                    Id="1",
                    Name="Demo controller",
                    Drives=[{"@odata.id": path + "/Drives/" + str(x)} for x in [1, 2]],
                    Volumes={"@odata.id": path + "/Volumes"},
                )
            if path.startswith("/redfish/v1/Systems/1/Storage/1/Drives/"):
                did = path.split("/")[-1]
                if did in {"1", "2"}:
                    return resource(
                        "Drive.v1_20_0.Drive",
                        path,
                        Id=did,
                        Name=f"SSD {did}",
                        CapacityBytes=512_000_000_000,
                        MediaType="SSD",
                        Status={
                            "State": "Enabled",
                            "Health": "Critical"
                            if did == "1" and self.fault == "Disk failure"
                            else "OK",
                        },
                    )
            if path == "/redfish/v1/Systems/1/Storage/1/Volumes":
                return collection("Volume", path, [path + "/" + v["Id"] for v in self.volumes])
            if path.startswith("/redfish/v1/Systems/1/Storage/1/Volumes/"):
                for volume in self.volumes:
                    if volume["Id"] == path.split("/")[-1]:
                        return resource("Volume.v1_10_0.Volume", path, **deepcopy(volume))
            if path == "/redfish/v1/UpdateService":
                return resource(
                    "UpdateService.v1_11_0.UpdateService",
                    path,
                    Id="UpdateService",
                    Name="Firmware updates",
                    FirmwareInventory={"@odata.id": path + "/FirmwareInventory"},
                    Actions={
                        "#UpdateService.SimpleUpdate": {
                            "target": path + "/Actions/UpdateService.SimpleUpdate"
                        }
                    },
                )
            if path == "/redfish/v1/UpdateService/FirmwareInventory":
                return collection("SoftwareInventory", path, [path + "/BMC"])
            if path == "/redfish/v1/UpdateService/FirmwareInventory/BMC":
                return resource(
                    "SoftwareInventory.v1_10_0.SoftwareInventory",
                    path,
                    Id="BMC",
                    Name="BMC firmware",
                    Version=self.firmware,
                    Updateable=True,
                )
            if path == "/redfish/v1/TaskService":
                return resource(
                    "TaskService.v1_2_0.TaskService",
                    path,
                    Id="TaskService",
                    Name="Tasks",
                    Tasks={"@odata.id": path + "/Tasks"},
                )
            if path == "/redfish/v1/TaskService/Tasks":
                return collection("Task", path, [path + "/" + tid for tid in self.tasks])
            if path.startswith("/redfish/v1/TaskService/Tasks/"):
                tid = path.split("/")[-1]
                if tid in self.tasks:
                    return self.public_task(self.tasks[tid])
            if path == "/redfish/v1/AccountService":
                return resource(
                    "AccountService.v1_15_0.AccountService",
                    path,
                    Id="AccountService",
                    Name="Demo accounts",
                    Accounts={"@odata.id": path + "/Accounts"},
                    Roles={"@odata.id": path + "/Roles"},
                )
            if path == "/redfish/v1/AccountService/Roles":
                return collection(
                    "Role",
                    path,
                    [path + "/" + role for role in ["Administrator", "Operator", "ReadOnly"]],
                )
            if path.startswith("/redfish/v1/AccountService/Roles/"):
                role = path.split("/")[-1]
                if role in {"Administrator", "Operator", "ReadOnly"}:
                    privileges = {
                        "Administrator": [
                            "Login",
                            "ConfigureManager",
                            "ConfigureUsers",
                            "ConfigureComponents",
                        ],
                        "Operator": ["Login", "ConfigureComponents"],
                        "ReadOnly": ["Login"],
                    }
                    return resource(
                        "Role.v1_3_3.Role",
                        path,
                        Id=role,
                        Name=role,
                        AssignedPrivileges=privileges[role],
                    )
            if path == "/redfish/v1/AccountService/Accounts":
                return collection(
                    "ManagerAccount", path, [path + "/" + a["Id"] for a in self.accounts]
                )
            if path.startswith("/redfish/v1/AccountService/Accounts/"):
                for account in self.accounts:
                    if account["Id"] == path.split("/")[-1]:
                        return resource(
                            "ManagerAccount.v1_13_0.ManagerAccount", path, **deepcopy(account)
                        )
            if path == "/redfish/v1/EventService":
                return resource(
                    "EventService.v1_10_0.EventService",
                    path,
                    Id="EventService",
                    Name="Hardware events",
                    ServiceEnabled=True,
                    Subscriptions={"@odata.id": path + "/Subscriptions"},
                )
            if path == "/redfish/v1/EventService/Subscriptions":
                return collection(
                    "EventDestination", path, [path + "/" + sid for sid in self.subscriptions]
                )
            if path.startswith("/redfish/v1/EventService/Subscriptions/"):
                sid = path.split("/")[-1]
                if sid in self.subscriptions:
                    return resource(
                        "EventDestination.v1_15_0.EventDestination",
                        path,
                        Id=sid,
                        **deepcopy(self.subscriptions[sid]),
                    )
            if path == "/redfish/v1/TelemetryService":
                return resource(
                    "TelemetryService.v1_3_4.TelemetryService",
                    path,
                    Id="TelemetryService",
                    Name="Hardware reports",
                    ServiceEnabled=True,
                    MetricReportDefinitions={"@odata.id": path + "/MetricReportDefinitions"},
                    MetricReports={"@odata.id": path + "/MetricReports"},
                )
            if path in {
                "/redfish/v1/TelemetryService/MetricReports",
                "/redfish/v1/TelemetryService/MetricReportDefinitions",
            }:
                kind = "MetricReport" if path.endswith("Reports") else "MetricReportDefinition"
                return collection(kind, path, [path + "/LiveHardware"])
            if path == "/redfish/v1/TelemetryService/MetricReports/LiveHardware":
                return self.metric_report()
            if path == "/redfish/v1/TelemetryService/MetricReportDefinitions/LiveHardware":
                return resource(
                    "MetricReportDefinition.v1_4_7.MetricReportDefinition",
                    path,
                    Id="LiveHardware",
                    Name="Hardware every few seconds",
                    MetricReportDefinitionType="Periodic",
                    MetricReportDefinitionEnabled=self.telemetry_enabled,
                    Schedule={"RecurrenceInterval": f"PT{self.telemetry_interval:g}S"},
                    ReportActions=["RedfishEvent", "LogToMetricReportsCollection"],
                )
            if path == "/redfish/v1/Managers/1/LogServices":
                return collection("LogService", path, [path + "/Hardware"])
            if path == "/redfish/v1/Managers/1/LogServices/Hardware":
                return resource(
                    "LogService.v1_3_0.LogService",
                    path,
                    Id="Hardware",
                    Name="Hardware log",
                    Entries={"@odata.id": path + "/Entries"},
                )
            if path == "/redfish/v1/Managers/1/LogServices/Hardware/Entries":
                return {
                    "@odata.id": path,
                    "Name": "Hardware log entries",
                    "Members@odata.count": len(self.events),
                    "Members": [
                        resource(
                            "LogEntry.v1_17_0.LogEntry",
                            path + "/" + e["EventId"],
                            Id=e["EventId"],
                            Name="Hardware event",
                            Message=e["Message"],
                            Severity=e["Severity"],
                            Created=e["EventTimestamp"],
                            EntryType="Event",
                        )
                        for e in self.events
                    ],
                }
            raise KeyError(path)
