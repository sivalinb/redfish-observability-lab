"""Verify the actual OTLP exporters serialize all three signals as valid protobuf."""

import threading
from collections import defaultdict

import requests
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
    ExportMetricsServiceRequest,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)

from redfish_lab.telemetry import TelemetryBridge


def test_optional_otlp_exporters_send_metrics_logs_and_traces(monkeypatch):
    captured = defaultdict(list)
    lock = threading.RLock()
    decoders = {
        "metrics": ExportMetricsServiceRequest,
        "logs": ExportLogsServiceRequest,
        "traces": ExportTraceServiceRequest,
    }

    def request(self, method, url, data=None, **kwargs):
        assert method == "POST"
        assert kwargs["headers"]["content-type"] == "application/x-protobuf"
        signal = url.rsplit("/", 1)[-1]
        payload = decoders[signal]()
        payload.ParseFromString(data)
        with lock:
            captured[signal].append(payload)
        response = requests.Response()
        response.status_code = 200
        response._content = b""
        return response

    monkeypatch.setattr(requests.Session, "request", request)
    bridge = TelemetryBridge(
        "otlp-test", export_interval_ms=60000, otlp_endpoint="http://collector.example:4318"
    )
    try:
        bridge.hardware(
            {"temperature": 52, "fan_rpm": 3200, "power_watts": 220, "health_code": 0},
            "REST polling",
        )
        bridge.event(
            {"EventId": "1", "Message": "Fan failure", "Severity": "Critical"},
            "HTTP event callback",
        )
        with bridge.tracer.start_as_current_span("example.request"):
            bridge.record_request(0.15, 200)
        bridge.flush()
        assert set(captured) == {"metrics", "logs", "traces"}
        assert captured["metrics"][0].resource_metrics
        assert captured["logs"][0].resource_logs
        assert captured["traces"][0].resource_spans
    finally:
        bridge.shutdown()
