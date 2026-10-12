"""One-shot real OpenTelemetry SDK exporters used by the catalog examples."""

from __future__ import annotations

import math
import os
import sys
import time
import uuid
from datetime import datetime
from urllib.parse import urlsplit

from opentelemetry._logs import LogRecord, SeverityNumber
from opentelemetry.metrics import Observation
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    ConsoleLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


def source_timestamp(value):
    """Preserve a timezone-qualified device timestamp; do not invent one."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return int(parsed.timestamp() * 1e9) if parsed.tzinfo else None
    except (ValueError, TypeError, AttributeError):
        return None


def hardware_resource(system, service_name="redfish-recipes"):
    identity = system.get("UUID") or system.get("SerialNumber")
    if not identity:
        raise ValueError("A stable system UUID or serial number is needed for correlation")
    return Resource.create(
        {
            "service.name": service_name,
            "service.instance.id": str(uuid.uuid4()),
            "host.id": str(identity),
            "host.name": system.get("HostName") or system.get("Id", "unknown"),
        }
    )


class RecipeTelemetry:
    def __init__(self, system):
        resource = hardware_resource(system)
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").rstrip("/")
        if endpoint:
            parsed = urlsplit(endpoint)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.path not in {"", "/"}
            ):
                raise ValueError("Set OTEL_EXPORTER_OTLP_ENDPOINT to the Collector origin")
            from opentelemetry.exporter.otlp.proto.http._log_exporter import (
                OTLPLogExporter,
            )
            from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            metrics = OTLPMetricExporter(endpoint=endpoint + "/v1/metrics")
            logs = OTLPLogExporter(endpoint=endpoint + "/v1/logs")
            spans = OTLPSpanExporter(endpoint=endpoint + "/v1/traces")
        else:
            metrics = ConsoleMetricExporter(out=sys.stdout)
            logs = ConsoleLogRecordExporter(out=sys.stdout)
            spans = ConsoleSpanExporter(out=sys.stdout)
        self.metrics = MeterProvider(
            resource=resource,
            metric_readers=[PeriodicExportingMetricReader(metrics, export_interval_millis=60000)],
        )
        self.logs = LoggerProvider(resource=resource)
        self.logs.add_log_record_processor(SimpleLogRecordProcessor(logs))
        self.traces = TracerProvider(resource=resource)
        self.traces.add_span_processor(SimpleSpanProcessor(spans))
        self.meter = self.metrics.get_meter("redfish-recipes")
        self.logger = self.logs.get_logger("redfish-recipes")
        self.tracer = self.traces.get_tracer("redfish-recipes")
        self._points = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.metrics.force_flush()
        self.logs.force_flush()
        self.traces.force_flush()
        self.metrics.shutdown()
        self.logs.shutdown()
        self.traces.shutdown()

    def gauge(self, name, value, unit, attributes=None):
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("A gauge requires a finite measurement")
        if name not in self._points:
            self._points[name] = (unit, {})
            self.meter.create_observable_gauge(
                name,
                unit=unit,
                callbacks=[
                    lambda _, key=name: [
                        Observation(v, attrs) for v, attrs in self._points[key][1].values()
                    ]
                ],
            )
        existing_unit, points = self._points[name]
        if existing_unit != unit:
            raise ValueError("Do not mix units within one metric")
        attributes = dict(attributes or {})
        points[tuple(sorted(attributes.items()))] = (value, attributes)

    def log(self, message, severity="OK", timestamp=None, attributes=None):
        severity_number = {
            "OK": SeverityNumber.INFO,
            "Warning": SeverityNumber.WARN,
            "Critical": SeverityNumber.ERROR,
        }.get(severity, SeverityNumber.INFO)
        self.logger.emit(
            LogRecord(
                timestamp=source_timestamp(timestamp),
                observed_timestamp=time.time_ns(),
                severity_number=severity_number,
                severity_text=severity,
                body=message,
                attributes=attributes or {},
            )
        )
