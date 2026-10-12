# How the lab works

The app hosts a hardware simulation, a Redfish-shaped HTTP API, a collection gateway, real OpenTelemetry SDK providers and a Gradio viewer in one Python process. Optional OTLP export crosses the process boundary to a separate Collector.

## The two computers

The **host** runs the synthetic checkout application. The **BMC** is the independent hardware management controller. Turning off the host or crashing its OS does not make the BMC disappear. The simulator uses 12 W of standby power when the host is off; that number is illustrative.

`ServerModel` holds power state, sensor values, health, pending/active BIOS settings, media, boot overrides, firmware, Tasks, volumes and accounts. A fan failure increases the modeled temperature gradually. Above a temperature threshold, the checkout route waits longer in actual `asyncio.sleep` calls. This produces measured durations and real trace timing from a deliberately simplified workload.

## The request path

Management studio constructs JSON from the selected lesson and sends it through `LabRegistry.request` using httpx's ASGI transport to FastAPI. Thus validation, permissions, HTTP status and state changes go through the API. External clients use the identical routes via TCP. No Gradio action can send a management write to a physical BMC.

The API returns 204 for accepted immediate changes, 201 with a resource Location for creation and 202 with a Task Location for long-running demo operations. Firmware version changes at Task completion, not acceptance. Pending BIOS settings become active on a restart. Virtual media + one-time CD/USB boot + power action creates a simplified installation Task.

The server is intentionally not Redfish-conformant: schemas, authentication, message registries, Task monitors, action discovery and OEM behavior are incomplete. IDs are fixed for readability. The optional real-hardware client follows advertised links instead.

## Three collection modes

| Mode | Sensor readings | Fault events |
| --- | --- | --- |
| Polling + push | GET Thermal/Power/System on interval | EventService callback on the next gateway cycle |
| Polling only | Same GETs on interval | Read stored log entries on that interval |
| Push reports + events | Periodic MetricReport callback | EventService callback on the next gateway cycle |

The gateway creates a subscription through the actual simulator API. Callback destinations are restricted to the simulator's internal path. No arbitrary outbound webhook is possible. Pushed payloads cross a FastAPI callback boundary using in-process HTTP transport; they are not a separate networked BMC.

The gateway cycle is approximately one second. It updates hardware, delivers callbacks, polls if due and issues one instrumented checkout per active session. Longer synthetic requests can lengthen the cycle. Event IDs are deduplicated when a pushed event is later encountered in log polling. MetricReport numeric strings are decoded before becoming SDK observations.

## OpenTelemetry providers

Each session owns its own `MeterProvider`, `TracerProvider` and `LoggerProvider`; none changes global providers. Bounded local exporters receive actual SDK objects. An optional second path sends HTTP/protobuf OTLP to `/v1/metrics`, `/v1/logs` and `/v1/traces`.

Hardware gauges observe the latest acquired values. Their SDK timestamps describe the collection/export observation; source sample time is kept separately on the bridge. Hardware log records preserve the original event time. Application request histograms use measured seconds. Application spans include real start/end times, IDs and parent context; application logs inside the span carry that context.

The correlation attributes are `host.name`, `lab.physical_server.id` and time. The custom physical ID avoids equating a hardware serial number with an OS machine ID. `service.instance.id` separates browser sessions in Prometheus. Hardware events have no fabricated trace context. Resource attributes include `lab.simulated=true`; the hardware observer uses false.

## Memory and lifetime

The local buffer retains at most 600 metric points, 200 logs and 200 spans, plus 90 acquired hardware and workload samples. Charts show the last 85 seconds. At most 32 simulated sessions are kept; the least recently touched is evicted at that limit, and inactive UI sessions expire after 30 minutes. Restarting the process resets all data. The shared external REST default is `public-demo`.

This behavior is suitable for a learning lab. Long-lived multi-user services would need authentication, rate limits, durable storage and a different resource-label policy. The optional Docker stack binds host ports to loopback and is disposable.

## External stack

The lab's SDK exporters → standalone Collector (`infra/collector.yaml`) → LGTM ingest Collector → Prometheus metrics, Loki logs and Tempo traces → Grafana. The double Collector hop keeps the independently editable gateway configuration visible while reusing Grafana's development bundle. The supplied Grafana provider imports the lab dashboard automatically.

SDK metric export is every 3 seconds; the standalone Collector batches for up to 1 second; the dashboard refreshes every 5 seconds. External log/span batch processors also add delay. A moving arrow is an illustration, not an acknowledgement. End-to-end health must be checked in the backend.

## Physical hardware example

`ReadOnlyRedfishClient` accepts an HTTPS origin, verified CA and separate credentials. It supports Basic authentication, GET-only reads, link discovery and modern Sensors or legacy Thermal/Power. It rejects external links and does not follow redirects. It has no reset, firmware, storage or account APIs. Missing or unsupported units produce no invented measurements. The CLI exports hardware metrics only; real application traces require separately instrumenting the real application with matching resource identity.
