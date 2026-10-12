import time

from redfish_lab import visuals


async def test_polling_maps_hardware_to_real_sdk_metrics(lab):
    registry, session = lab
    await registry.set_transport(session, "Polling only", 3)
    await registry.step(session)
    session.bridge.flush()
    records = session.bridge.buffer.snapshot()
    assert {"lab.hardware.temperature", "lab.hardware.fan.speed", "lab.hardware.power"} <= {
        m["name"] for m in records["metrics"]
    }
    assert records["metrics"][0]["resource"]["host.name"] == "server-42"
    assert session.bridge.polls == 1
    assert session.bridge.pushes == 0


async def test_push_reports_arrive_through_callback_without_polls(lab):
    registry, session = lab
    await registry.set_transport(session, "Push reports + events", 1)
    session.model.set_fault("Fan failure")
    await registry.step(session)
    session.bridge.flush()
    assert session.bridge.latest_hardware["fan_rpm"] == 0
    assert session.bridge.polls == 0
    assert session.bridge.pushes >= 2
    assert session.bridge.last_transport == "Pushed metric report"
    logs = session.bridge.buffer.snapshot()["logs"]
    assert any(
        "Fan failure" in log["body"]
        and log["attributes"]["redfish.transport"] == "HTTP event callback"
        for log in logs
    )
    hardware_logs = [log for log in logs if "redfish.event.id" in log["attributes"]]
    assert all(log["trace_id"] is None for log in hardware_logs)


async def test_poll_interval_delays_discovery_and_preserves_event_deduplication(lab):
    registry, session = lab
    await registry.set_transport(session, "Polling only", 12)
    now = time.monotonic()
    await registry.step(session, now)
    rpm = session.bridge.latest_hardware["fan_rpm"]
    session.model.set_fault("Fan failure")
    await registry.step(session, now + 1)
    assert session.bridge.latest_hardware["fan_rpm"] == rpm
    await registry.step(session, now + 13)
    assert session.bridge.latest_hardware["fan_rpm"] == 0
    count = session.bridge.buffer.counts["logs"]
    await registry.step(session, now + 26)
    assert session.bridge.buffer.counts["logs"] == count


async def test_request_spans_have_real_durations_and_shared_trace_context(lab):
    registry, session = lab
    response = await registry.request(session, "GET", "/workload/checkout")
    assert response.status_code == 200
    spans = session.bridge.buffer.snapshot()["spans"]
    root = next(s for s in spans if s["name"] == "checkout.request")
    children = [s for s in spans if s["parent_id"]]
    assert len(children) == 2
    assert all(
        s["trace_id"] == root["trace_id"] and s["parent_id"] == root["span_id"] for s in children
    )
    assert root["duration_ms"] >= session.model.latency_ms
    assert response.json()["trace_id"] == root["trace_id"]


async def test_cooling_failure_causes_temperature_and_request_duration_to_rise(lab):
    registry, session = lab
    healthy = (await registry.request(session, "GET", "/workload/checkout")).json()["duration_ms"]
    session.model.set_fault("Fan failure")
    for _ in range(24):
        session.model.tick()
    assert session.model.temperature > 75
    failed = (await registry.request(session, "GET", "/workload/checkout")).json()["duration_ms"]
    assert failed > healthy * 3
    session.bridge.flush()
    assert any("200 ms" in log["body"] for log in session.bridge.buffer.snapshot()["logs"])


async def test_os_crash_keeps_hardware_visible_and_emits_failed_application_span(lab):
    registry, session = lab
    session.model.set_fault("OS crash")
    await registry.step(session)
    session.bridge.flush()
    assert "temperature" in session.bridge.latest_hardware
    assert session.last_workload["status"] == "host-unavailable"
    assert any(span["status"] == "ERROR" for span in session.bridge.buffer.snapshot()["spans"])


def test_user_content_is_escaped_and_motion_can_be_disabled(lab):
    _, session = lab
    session.model.emit("<script>alert('example')</script>")
    session.bridge.event(session.model.events[-1], "HTTP event callback")
    html = visuals.signals(session)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "rf-paused" in visuals.dashboard(session, motion=False)
