import pytest


async def test_discover_inventory_and_sensors(lab):
    registry, session = lab
    root = (await registry.request(session, "GET", "/redfish/v1")).json()
    systems = (await registry.request(session, "GET", root["Systems"]["@odata.id"])).json()
    server = (await registry.request(session, "GET", systems["Members"][0]["@odata.id"])).json()
    assert server["MemorySummary"]["TotalSystemMemoryGiB"] == 128
    assert server["SerialNumber"] == "SIM-R42-0001"
    sensors = (await registry.request(session, "GET", "/redfish/v1/Chassis/1/Sensors")).json()
    for member in sensors["Members"]:
        response = await registry.request(session, "GET", member["@odata.id"])
        assert response.status_code == 200
        assert isinstance(response.json()["Reading"], (float, int))


async def test_host_off_keeps_bmc_and_hardware_polling_online(lab):
    registry, session = lab
    response = await registry.request(
        session,
        "POST",
        "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset",
        {"ResetType": "GracefulShutdown"},
    )
    assert response.status_code == 204
    await registry.step(session)
    bmc = (await registry.request(session, "GET", "/redfish/v1/Managers/1")).json()
    assert bmc["PowerState"] == "On"
    assert session.bridge.latest_hardware["power_watts"] == 12
    assert session.last_workload["status"] == "host-unavailable"
    response = await registry.request(
        session, "POST", "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset", {"ResetType": "On"}
    )
    assert response.status_code == 204
    assert session.model.os_running


async def test_power_cap_limits_simulated_consumption(lab):
    registry, session = lab
    session.model.cpu_load = 100
    response = await registry.request(
        session,
        "PATCH",
        "/redfish/v1/Chassis/1/Power",
        {"PowerControl": [{"PowerLimit": {"LimitInWatts": 150}}]},
    )
    assert response.status_code == 204
    assert session.model.power_watts == 150


async def test_bios_is_staged_until_restart(lab):
    registry, session = lab
    response = await registry.request(
        session,
        "PATCH",
        "/redfish/v1/Systems/1/Bios/Settings",
        {"Attributes": {"ProcVirtualization": "Disabled"}},
    )
    assert response.status_code == 204
    assert session.model.bios["ProcVirtualization"] == "Enabled"
    assert session.model.pending_bios["ProcVirtualization"] == "Disabled"
    await registry.request(
        session,
        "POST",
        "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset",
        {"ResetType": "GracefulRestart"},
    )
    assert session.model.bios["ProcVirtualization"] == "Disabled"
    assert not session.model.pending_bios


async def test_firmware_accepted_then_completes(lab):
    registry, session = lab
    response = await registry.request(
        session,
        "POST",
        "/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate",
        {"ImageURI": "https://example.com/demo.bin", "Oem": {"Lab": {"Version": "2.2.0"}}},
    )
    assert response.status_code == 202
    assert session.model.firmware == "2.0.0"
    path = response.headers["Location"]
    task_id = response.json()["Id"]
    session.model.tick(session.model.tasks[task_id]["_started"] + 7)
    task = (await registry.request(session, "GET", path)).json()
    assert task["TaskState"] == "Completed"
    assert task["PercentComplete"] == 100
    assert session.model.firmware == "2.2.0"
    assert not any(k.startswith("_") for k in task)


async def test_installer_requires_media_and_boot_override(lab):
    registry, session = lab
    reset = "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"
    await registry.request(session, "POST", reset, {"ResetType": "GracefulRestart"})
    assert not session.model.tasks
    response = await registry.request(
        session,
        "POST",
        "/redfish/v1/Managers/1/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia",
        {"Image": "https://example.com/demo.iso"},
    )
    assert response.status_code == 204
    await registry.request(
        session,
        "PATCH",
        "/redfish/v1/Systems/1",
        {"Boot": {"BootSourceOverrideTarget": "Cd", "BootSourceOverrideEnabled": "Once"}},
    )
    await registry.request(session, "POST", reset, {"ResetType": "GracefulRestart"})
    task = next(iter(session.model.tasks.values()))
    assert task["_kind"] == "os-install"
    session.model.tick(task["_started"] + 7)
    assert session.model.installed_os == "Fresh Demo Linux"
    assert session.model.boot_enabled == "Disabled"


async def test_volume_creation_returns_discoverable_resource(lab):
    registry, session = lab
    path = "/redfish/v1/Systems/1/Storage/1/Volumes"
    response = await registry.request(
        session, "POST", path, {"Name": "learning-volume", "RAIDType": "RAID1"}
    )
    assert response.status_code == 201
    volume = (await registry.request(session, "GET", response.headers["Location"])).json()
    assert volume["RAIDType"] == "RAID1"
    duplicate = await registry.request(
        session, "POST", path, {"Name": "learning-volume", "RAIDType": "RAID1"}
    )
    assert duplicate.status_code == 400
    assert len(session.model.volumes) == 2


async def test_accounts_do_not_return_or_retain_passwords(lab):
    registry, session = lab
    response = await registry.request(
        session,
        "POST",
        "/redfish/v1/AccountService/Accounts",
        {"UserName": "viewer", "RoleId": "ReadOnly", "Password": "placeholder"},
    )
    assert response.status_code == 201
    assert response.json()["RoleId"] == "ReadOnly"
    assert "Password" not in response.json()
    assert all("Password" not in a for a in session.model.accounts)


@pytest.mark.parametrize(
    "role,path,expected",
    [
        ("ReadOnly", "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset", 403),
        ("Operator", "/redfish/v1/AccountService/Accounts", 403),
        ("Operator", "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset", 204),
    ],
)
async def test_teaching_roles_enforce_write_boundaries(lab, role, path, expected):
    registry, session = lab
    response = await registry.request(
        session,
        "POST",
        path,
        {"ResetType": "On", "UserName": "viewer", "RoleId": "ReadOnly"},
        role=role,
    )
    assert response.status_code == expected


@pytest.mark.parametrize(
    "method,path,body",
    [
        (
            "PATCH",
            "/redfish/v1/Chassis/1/Power",
            {"PowerControl": [{"PowerLimit": {"LimitInWatts": -1}}]},
        ),
        ("PATCH", "/redfish/v1/Systems/1/Bios/Settings", {"Attributes": {"Unexpected": "Enabled"}}),
        (
            "POST",
            "/redfish/v1/Managers/1/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia",
            {"Image": "file:///etc/passwd"},
        ),
        (
            "POST",
            "/redfish/v1/AccountService/Accounts",
            {"UserName": "<script>", "RoleId": "ReadOnly"},
        ),
        (
            "POST",
            "/redfish/v1/EventService/Subscriptions",
            {"Destination": "http://example.com/receiver"},
        ),
    ],
)
async def test_invalid_mutations_return_errors_without_changes(lab, method, path, body):
    registry, session = lab
    before = session.model.snapshot()
    response = await registry.request(session, method, path, body)
    assert response.status_code == 400
    after = session.model.snapshot()
    for key in ["power_limit", "bios", "media", "accounts", "volumes", "subscriptions"]:
        assert before[key] == after[key]


async def test_sessions_are_isolated(lab):
    registry, session = lab
    other = registry.new()
    await registry.request(session, "POST", "/lab/scenario", {"fault": "Fan failure"})
    assert session.model.fan_rpm == 0
    assert other.model.fault == "Healthy"
    assert (
        session.bridge.resource.attributes["lab.session.id"]
        != other.bridge.resource.attributes["lab.session.id"]
    )
