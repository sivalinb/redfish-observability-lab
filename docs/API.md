# Simulator HTTP guide

Base URL: `http://127.0.0.1:7860`. Start with `GET /redfish/v1` and follow `@odata.id` links. The fixed IDs below belong to this teaching simulator; real BMCs advertise different paths, capabilities and permissible values.

The default session is `public-demo`. Supply `X-Lab-Session: my-experiment` for an isolated external simulation. `X-Lab-Role` accepts Administrator (default), Operator or ReadOnly; it is a teaching switch, not login authentication. Operator can perform power/media actions; Administrator can perform all demo writes.

## Read inventory and observations

```bash
curl http://127.0.0.1:7860/redfish/v1/Systems/1
curl http://127.0.0.1:7860/redfish/v1/Systems/1/Storage/1/Drives/1
curl http://127.0.0.1:7860/redfish/v1/Chassis/1/Sensors/CPU1Temp
curl http://127.0.0.1:7860/redfish/v1/Chassis/1/Thermal
curl http://127.0.0.1:7860/redfish/v1/Chassis/1/Power
curl http://127.0.0.1:7860/redfish/v1/Managers/1/LogServices/Hardware/Entries
```

## Stage BIOS, then apply on restart

```bash
curl -X PATCH http://127.0.0.1:7860/redfish/v1/Systems/1/Bios/Settings \
  -H 'Content-Type: application/json' \
  -d '{"Attributes":{"ProcVirtualization":"Disabled"}}'
curl http://127.0.0.1:7860/redfish/v1/Systems/1/Bios
curl -X POST http://127.0.0.1:7860/redfish/v1/Systems/1/Actions/ComputerSystem.Reset \
  -H 'Content-Type: application/json' -d '{"ResetType":"GracefulRestart"}'
curl http://127.0.0.1:7860/redfish/v1/Systems/1/Bios
```

## Start an asynchronous firmware Task

```bash
curl -i -X POST http://127.0.0.1:7860/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate \
  -H 'Content-Type: application/json' \
  -d '{"ImageURI":"https://example.com/demo-bmc.bin","Oem":{"Lab":{"Version":"2.1.0"}}}'
curl http://127.0.0.1:7860/redfish/v1/TaskService/Tasks
```

Follow the **Location** response header; do not assume a fixed Task ID. Poll it until `TaskState=Completed`. Completion takes roughly six seconds while the gateway is running. `Oem.Lab.Version` is an illustrative lab extension. The URL is recorded without download or flashing.

## Prepare a virtual installer

```bash
curl -X POST http://127.0.0.1:7860/redfish/v1/Managers/1/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia \
  -H 'Content-Type: application/json' -d '{"Image":"https://example.com/demo-linux.iso"}'
curl -X PATCH http://127.0.0.1:7860/redfish/v1/Systems/1 \
  -H 'Content-Type: application/json' \
  -d '{"Boot":{"BootSourceOverrideTarget":"Cd","BootSourceOverrideEnabled":"Once"}}'
curl -X POST http://127.0.0.1:7860/redfish/v1/Systems/1/Actions/ComputerSystem.Reset \
  -H 'Content-Type: application/json' -d '{"ResetType":"GracefulRestart"}'
curl http://127.0.0.1:7860/redfish/v1/TaskService/Tasks
```

This models a simplified installation Task, not actual OS provisioning. The media URL is not fetched.

## Power cap, volume and account

```bash
curl -X PATCH http://127.0.0.1:7860/redfish/v1/Chassis/1/Power \
  -H 'Content-Type: application/json' \
  -d '{"PowerControl":[{"MemberId":"0","PowerLimit":{"LimitInWatts":150}}]}'
curl -X POST http://127.0.0.1:7860/redfish/v1/Systems/1/Storage/1/Volumes \
  -H 'Content-Type: application/json' -d '{"Name":"learning-volume","RAIDType":"RAID1"}'
curl -X POST http://127.0.0.1:7860/redfish/v1/AccountService/Accounts \
  -H 'Content-Type: application/json' -d '{"UserName":"observer","RoleId":"ReadOnly","Enabled":true}'
```

Volume creation models metadata. Account creation models a role; no password is retained. A write with `X-Lab-Role: ReadOnly` returns 403.

## Events and metric reports

```bash
curl http://127.0.0.1:7860/redfish/v1/EventService/Subscriptions
curl http://127.0.0.1:7860/redfish/v1/TelemetryService/MetricReportDefinitions/LiveHardware
curl http://127.0.0.1:7860/redfish/v1/TelemetryService/MetricReports/LiveHardware
curl -X PATCH http://127.0.0.1:7860/redfish/v1/TelemetryService/MetricReportDefinitions/LiveHardware \
  -H 'Content-Type: application/json' \
  -d '{"Schedule":{"RecurrenceInterval":"PT5S"},"MetricReportDefinitionEnabled":true}'
```

The collection gateway maintains one internal callback subscription in push modes. Incoming events and reports use `POST /ingest/redfish/{session_id}` and require the same `X-Lab-Session` header. Arbitrary external callback destinations are rejected. The UI's Signal pipeline selects polling, event push or metric-report push. Editing a report schedule through HTTP affects report generation; it does not change the UI's separate polling interval.

## Lab-specific routes

| Route | Purpose |
| --- | --- |
| `GET /healthz` | Process readiness |
| `POST /lab/scenario` | JSON `{"fault":"Fan failure","load":40}`; choose Healthy, Fan failure, Power supply failure, Disk failure or OS crash |
| `GET /lab/snapshot` | Hardware plus bounded exported telemetry for this session |
| `GET /workload/checkout` | Actual instrumented synthetic HTTP request; 200 when host is available, 503 when unavailable |

These routes are lab utilities, outside Redfish. Unsupported teaching resource/method combinations return 405, unknown read resources return 404 and invalid parameters return 400. The simulator is not an authenticated or complete implementation of the standard.
