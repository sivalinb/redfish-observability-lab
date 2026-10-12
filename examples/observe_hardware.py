"""Read real hardware over HTTPS and export metrics. No control/write methods exist."""

import argparse
import os
import time
import uuid

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource

from redfish_lab.readonly import ReadOnlyRedfishClient


def main():
    parser = argparse.ArgumentParser(description="Opt-in read-only Redfish → OpenTelemetry bridge")
    parser.add_argument(
        "--once", action="store_true", help="Collect one inventory/readings snapshot and exit"
    )
    parser.add_argument(
        "--interval", type=float, default=30, help="Polling interval in seconds (default: 30)"
    )
    args = parser.parse_args()
    if args.interval < 5:
        parser.error(
            "Use an interval of at least five seconds; validate BMC capacity before faster polling"
        )
    required = [key for key in ["BMC_URL", "BMC_USERNAME", "BMC_PASSWORD"] if not os.getenv(key)]
    if required:
        parser.error("Set environment variables: " + ", ".join(required))
    client = ReadOnlyRedfishClient(
        os.environ["BMC_URL"],
        os.environ["BMC_USERNAME"],
        os.environ["BMC_PASSWORD"],
        os.getenv("BMC_CA_BUNDLE"),
    )
    provider = None
    try:
        resource = Resource.create(
            {
                "service.name": "redfish-readonly-bridge",
                "lab.simulated": False,
                "service.instance.id": uuid.uuid4().hex,
                **client.identity(),
            }
        )
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        exporter = (
            OTLPMetricExporter(endpoint=endpoint.rstrip("/") + "/v1/metrics", timeout=10)
            if endpoint
            else ConsoleMetricExporter()
        )
        provider = MeterProvider(
            resource=resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    exporter, export_interval_millis=max(5000, int(args.interval * 1000))
                )
            ],
        )
        meter = provider.get_meter("redfish_lab.readonly")
        gauges = {}
        while True:
            readings = client.readings()
            for reading in readings:
                metric = reading["name"]
                if metric not in gauges:
                    gauges[metric] = meter.create_gauge(metric, unit=reading["unit"])
                gauges[metric].set(reading["value"], reading["attributes"])
            if not readings:
                print("No supported temperature, fan RPM or power readings were advertised.")
            provider.force_flush(timeout_millis=12000)
            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        if provider:
            provider.shutdown()
        client.close()


if __name__ == "__main__":
    main()
