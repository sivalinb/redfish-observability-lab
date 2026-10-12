"""Real OpenTelemetry SDK providers with bounded local exporters and optional OTLP."""

from __future__ import annotations

import os
import threading
import time
from collections import deque
from datetime import datetime, timezone

from opentelemetry._logs import SeverityNumber
from opentelemetry.metrics import Observation
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    LogRecordExporter,
    LogRecordExportResult,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExporter,
    MetricExportResult,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)


def stamp(ns: int) -> str:
    return datetime.fromtimestamp(ns / 1e9, timezone.utc).isoformat(timespec="milliseconds")


class TelemetryBuffer:
    def __init__(self):
        self.metrics = deque(maxlen=600)
        self.logs = deque(maxlen=200)
        self.spans = deque(maxlen=200)
        self.history = deque(maxlen=90)
        self.durations = deque(maxlen=90)
        self.counts = {"metrics": 0, "logs": 0, "spans": 0}
        self.lock = threading.RLock()
        self.last_export = 0.0

    def add(self, kind, item):
        with self.lock:
            getattr(self, kind).append(item)
            self.counts[kind] += 1
            self.last_export = time.time()

    def snapshot(self):
        with self.lock:
            return {
                "counts": dict(self.counts),
                "metrics": list(self.metrics)[-24:],
                "logs": list(self.logs)[-20:],
                "spans": list(self.spans)[-20:],
                "history": list(self.history),
                "durations": list(self.durations),
                "last_export": self.last_export,
            }


class MemoryMetrics(MetricExporter):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def export(self, metrics_data, timeout_millis=10000, **kwargs):
        for rm in metrics_data.resource_metrics:
            for scope in rm.scope_metrics:
                for metric in scope.metrics:
                    for point in metric.data.data_points:
                        value = getattr(point, "value", None)
                        if value is None:
                            value = {"count": point.count, "sum": point.sum}
                        self.buffer.add(
                            "metrics",
                            {
                                "name": metric.name,
                                "unit": metric.unit,
                                "value": value,
                                "timestamp": stamp(point.time_unix_nano),
                                "attributes": dict(point.attributes or {}),
                                "resource": dict(rm.resource.attributes),
                            },
                        )
        return MetricExportResult.SUCCESS

    def force_flush(self, timeout_millis=10000):
        return True

    def shutdown(self, timeout_millis=30000, **kwargs):
        pass


class MemorySpans(SpanExporter):
    def __init__(self, buffer):
        self.buffer = buffer

    def export(self, spans):
        for span in spans:
            self.buffer.add(
                "spans",
                {
                    "name": span.name,
                    "trace_id": f"{span.context.trace_id:032x}",
                    "span_id": f"{span.context.span_id:016x}",
                    "parent_id": f"{span.parent.span_id:016x}" if span.parent else None,
                    "duration_ms": round((span.end_time - span.start_time) / 1e6, 2),
                    "timestamp": stamp(span.start_time),
                    "attributes": dict(span.attributes or {}),
                    "resource": dict(span.resource.attributes),
                    "status": span.status.status_code.name,
                },
            )
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


class MemoryLogs(LogRecordExporter):
    def __init__(self, buffer):
        self.buffer = buffer

    def export(self, batch):
        for record in batch:
            log = record.log_record
            self.buffer.add(
                "logs",
                {
                    "body": str(log.body),
                    "severity": log.severity_text,
                    "timestamp": stamp(log.timestamp or time.time_ns()),
                    "attributes": dict(log.attributes or {}),
                    "trace_id": f"{log.trace_id:032x}" if log.trace_id else None,
                    "resource": dict(record.resource.attributes),
                },
            )
        return LogRecordExportResult.SUCCESS

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=30000):
        return True


class TelemetryBridge:
    def __init__(self, session_id, export_interval_ms=1000, otlp_endpoint=None):
        self.buffer = TelemetryBuffer()
        self.latest_hardware = {}
        self.lock = threading.RLock()
        self.source_time = None
        self.acquired_at = None
        self.last_transport = "Waiting for a reading"
        self.last_event_id = 0
        self.polls = 0
        self.pushes = 0
        self.resource = Resource.create(
            {
                "service.name": "redfish-observatory",
                "service.version": "0.1.0",
                "service.instance.id": session_id,
                "host.name": "server-42",
                "lab.physical_server.id": "SIM-R42-0001",
                "lab.session.id": session_id,
                "lab.simulated": True,
            }
        )
        readers = [
            PeriodicExportingMetricReader(
                MemoryMetrics(self.buffer), export_interval_millis=export_interval_ms
            )
        ]
        self.traces = TracerProvider(resource=self.resource)
        self.traces.add_span_processor(SimpleSpanProcessor(MemorySpans(self.buffer)))
        self.logs = LoggerProvider(resource=self.resource)
        self.logs.add_log_record_processor(SimpleLogRecordProcessor(MemoryLogs(self.buffer)))
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if self.otlp_endpoint:
            from opentelemetry.exporter.otlp.proto.http._log_exporter import (
                OTLPLogExporter,
            )
            from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            base = self.otlp_endpoint.rstrip("/")
            readers.append(
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=base + "/v1/metrics", timeout=3),
                    export_interval_millis=3000,
                )
            )
            self.traces.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=base + "/v1/traces", timeout=3))
            )
            self.logs.add_log_record_processor(
                BatchLogRecordProcessor(OTLPLogExporter(endpoint=base + "/v1/logs", timeout=3))
            )
        self.meters = MeterProvider(resource=self.resource, metric_readers=readers)
        meter = self.meters.get_meter("redfish_lab.hardware")
        self.tracer = self.traces.get_tracer("redfish_lab.workload")
        self.logger = self.logs.get_logger("redfish_lab.events")
        for metric, key, unit, description in [
            ("lab.hardware.temperature", "temperature", "Cel", "Simulated CPU temperature"),
            ("lab.hardware.fan.speed", "fan_rpm", "{revolution}/min", "Simulated fan speed"),
            ("lab.hardware.power", "power_watts", "W", "Simulated server power including standby"),
            ("lab.hardware.health", "health_code", "1", "0 OK, 1 warning, 2 critical"),
        ]:
            meter.create_observable_gauge(
                metric, callbacks=[self._callback(key)], unit=unit, description=description
            )
        self.duration = meter.create_histogram(
            "lab.application.request.duration",
            unit="s",
            description="Actual duration of the simulated checkout HTTP request",
        )
        self.requests = meter.create_counter("lab.application.requests", unit="{request}")

    def _callback(self, key):
        def observe(options):
            with self.lock:
                if key in self.latest_hardware:
                    yield Observation(self.latest_hardware[key], {"sensor": key})

        return observe

    def hardware(self, data, transport, source_time=None):
        """Set measurements after an HTTP poll or an incoming Redfish metric report."""
        with self.lock:
            self.latest_hardware.update(data)
            self.source_time = source_time
            self.acquired_at = time.time()
            self.last_transport = transport
            if transport == "REST polling":
                self.polls += 1
            else:
                self.pushes += 1
            with self.buffer.lock:
                self.buffer.history.append({"time": time.time(), **self.latest_hardware})

    def event(self, entry, transport):
        event_id = int(entry.get("EventId", entry.get("Id", 0)))
        if event_id <= self.last_event_id:
            return False
        self.last_event_id = event_id
        severity = entry.get("Severity", "OK")
        source_timestamp = entry.get("EventTimestamp", entry.get("Created"))
        try:
            timestamp_ns = int(datetime.fromisoformat(source_timestamp).timestamp() * 1e9)
        except (TypeError, ValueError):
            timestamp_ns = time.time_ns()
        self.logger.emit(
            body=entry["Message"],
            severity_text=severity,
            severity_number={
                "OK": SeverityNumber.INFO,
                "Warning": SeverityNumber.WARN,
                "Critical": SeverityNumber.ERROR,
            }.get(severity, SeverityNumber.INFO),
            timestamp=timestamp_ns,
            attributes={
                "redfish.event.id": str(event_id),
                "redfish.transport": transport,
                "redfish.event.timestamp": entry.get("EventTimestamp", entry.get("Created", "")),
                "redfish.origin": entry.get("OriginOfCondition", {}).get("@odata.id", ""),
            },
        )
        if transport != "REST polling":
            self.pushes += 1
        return True

    def record_request(self, elapsed, status):
        attrs = {
            "http.request.method": "GET",
            "http.response.status_code": status,
            "http.route": "/workload/checkout",
        }
        self.duration.record(elapsed, attrs)
        self.requests.add(1, attrs)
        with self.buffer.lock:
            self.buffer.durations.append(
                {"time": time.time(), "duration_ms": elapsed * 1000, "status": status}
            )

    def flush(self):
        self.meters.force_flush(timeout_millis=3000)
        self.traces.force_flush(timeout_millis=3000)
        self.logs.force_flush(timeout_millis=3000)

    def shutdown(self):
        self.meters.shutdown(timeout_millis=3000)
        self.traces.shutdown()
        self.logs.shutdown()
