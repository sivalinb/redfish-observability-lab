"""Ten executable, parameterized management lessons."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Lesson:
    title: str
    verb: str
    path: str
    meaning: str
    explanation: str
    next_step: str


LESSONS = {
    "01 · Hardware inventory": Lesson(
        "Hardware inventory",
        "GET",
        "/redfish/v1/Systems/1",
        "Ask the management controller what is installed.",
        "The response describes the physical server: processors, memory, serial number and links to its components. Discovery starts at /redfish/v1 and follows @odata.id links.",
        "Explore Storage/1/Drives/1 in the API explorer to inspect an individual drive.",
    ),
    "02 · Health and sensors": Lesson(
        "Health and sensors",
        "GET",
        "/redfish/v1/Chassis/1/Thermal",
        "Read temperatures, fan speeds and health.",
        "The BMC samples hardware sensors even when the simulated host OS is unavailable. This lab exposes Sensors plus legacy Thermal/Power resources to teach both styles.",
        "Inject a fan failure in Live rack. Read again and watch Fan1 fall to zero.",
    ),
    "03 · Remote power": Lesson(
        "Remote power",
        "POST",
        "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset",
        "Press the server's power button over the network.",
        "An action changes power state. The BMC stays online on standby power, so the API continues to answer while the main server is off. GracefulRestart applies the staged BIOS settings in this simulator.",
        "Choose GracefulShutdown, run it, then read Managers/1 to see the BMC is still On.",
    ),
    "04 · Energy and power caps": Lesson(
        "Energy and power caps",
        "PATCH",
        "/redfish/v1/Chassis/1/Power",
        "Set a budget for the simulated server's electricity use.",
        "PowerConsumedWatts is a measurement. LimitInWatts is a control. The teaching model clamps simulated power to the chosen cap; real systems may lower performance to enforce a cap.",
        "Set 150 W under high load. Watch power consumption stop rising above the cap.",
    ),
    "05 · BIOS configuration": Lesson(
        "BIOS configuration",
        "PATCH",
        "/redfish/v1/Systems/1/Bios/Settings",
        "Stage a startup setting, then restart to apply it.",
        "Redfish Settings separates desired settings from active settings. Changing a pending BIOS attribute does not immediately change the currently running server.",
        "Stage ProcVirtualization = Disabled, then use Remote power → GracefulRestart.",
    ),
    "06 · Firmware updates": Lesson(
        "Firmware updates",
        "POST",
        "/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate",
        "Schedule an update and follow its progress.",
        "HTTP 202 means accepted, not completed. The Location header points to a Task resource. Watch PercentComplete and TaskState. ImageURI is recorded only; this lab never downloads or flashes firmware.",
        "Wait six seconds and read the task. The BMC version changes only after completion.",
    ),
    "07 · Boot source": Lesson(
        "Boot source",
        "PATCH",
        "/redfish/v1/Systems/1",
        "Choose what the server should boot from next.",
        "A one-time boot override can select a local disk, virtual DVD, USB or network boot. Selecting a source prepares a boot; it does not install an operating system by itself.",
        "Attach the virtual installer, choose Cd here, then restart to trigger the demo installation.",
    ),
    "08 · Virtual installer": Lesson(
        "Virtual installer",
        "POST",
        "/redfish/v1/Managers/1/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia",
        "Attach a virtual DVD without visiting the server.",
        "Virtual media exposes an installer image as if a DVD were plugged in. This simulator records the URL. The simplified installer runs only after a one-time Cd/Usb boot and a power action.",
        "Next choose Boot source → Cd, then Remote power → GracefulRestart. Watch the installation task.",
    ),
    "09 · Storage volumes": Lesson(
        "Storage volumes",
        "POST",
        "/redfish/v1/Systems/1/Storage/1/Volumes",
        "Create a simulated disk group and logical volume.",
        "RAID1 mirrors data; RAID0 stripes data for capacity/speed without redundancy. This lab models volume metadata only, not disk allocation, data movement or fault-tolerant recovery.",
        "Create learning-volume, then follow the returned @odata.id to inspect its RAID type.",
    ),
    "10 · Accounts and permissions": Lesson(
        "Accounts and permissions",
        "POST",
        "/redfish/v1/AccountService/Accounts",
        "Create a demo account with a management role.",
        "Administrator can configure everything; Operator can perform the demo power/media actions; ReadOnly can inspect. X-Lab-Role illustrates enforcement and is not authentication. Passwords are not stored.",
        "Select ReadOnly as the request role and try a write. It should return HTTP 403.",
    ),
}


def payload_for(choice, power_action, cap, virtualization, version, boot, image, name, raid, role):
    index = list(LESSONS).index(choice)
    return {
        0: None,
        1: None,
        2: {"ResetType": power_action},
        3: {"PowerControl": [{"MemberId": "0", "PowerLimit": {"LimitInWatts": int(cap)}}]},
        4: {"Attributes": {"ProcVirtualization": virtualization}},
        5: {"ImageURI": "https://example.com/demo-bmc.bin", "Oem": {"Lab": {"Version": version}}},
        6: {"Boot": {"BootSourceOverrideTarget": boot, "BootSourceOverrideEnabled": "Once"}},
        7: {"Image": image, "Inserted": True, "WriteProtected": True},
        8: {"Name": name, "RAIDType": raid},
        9: {"UserName": name, "RoleId": role, "Enabled": True},
    }[index]


TOUR = [
    (
        "01 / MEET THE TWO COMPUTERS",
        "The host runs your application. The BMC manages the hardware independently.",
        "Go to Live rack, choose OS crash, and inject it. Application requests return 503 while Redfish continues to report temperatures and power.",
    ),
    (
        "02 / BREAK A FAN",
        "Hardware trouble becomes an observable event.",
        "Restore Healthy first. Select Polling + push, inject Fan failure, then watch the fan stop, the CPU heat up and hardware logs appear.",
    ),
    (
        "03 / FOLLOW THE SIGNAL",
        "A number is a metric. A fault message is a log. A request journey is a trace.",
        "Open Signal pipeline. Compare hardware metrics with checkout spans and slow-request logs. The synthetic cooling scenario increases actual sleep time in the checkout endpoint.",
    ),
    (
        "04 / TEST THE COLLECTION DELAY",
        "Near real time has several clocks.",
        "Set Polling only and a 12-second interval. Restore the fan, then fail it. Compare the live sensor against the collected chart. Switch to Push reports + events for report-driven collection.",
    ),
    (
        "05 / OPERATE THROUGH HTTP",
        "Redfish operations are ordinary web requests with defined meanings.",
        "Try each management lesson. Watch the verb, payload, status code and resulting state. A 202 firmware response is still running; inspect the Task before treating it as successful.",
    ),
    (
        "06 / CONNECT A BACKEND",
        "The OpenTelemetry Collector routes signals; a backend stores and visualizes them.",
        "Use Docker Compose for an optional Collector plus Grafana/Loki/Tempo/Prometheus stack. Until configured, this app uses real SDK exporters into a bounded in-memory viewer.",
    ),
]
