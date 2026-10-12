import pytest

from redfish_lab.recipe_telemetry import (
    RecipeTelemetry,
    hardware_resource,
    source_timestamp,
)


def test_hardware_identity_and_source_time_are_preserved():
    resource = hardware_resource({"UUID": "physical-42", "HostName": "server-42"})
    assert resource.attributes["host.id"] == "physical-42"
    assert source_timestamp("2026-10-12T10:00:00Z") == 1791799200000000000
    assert source_timestamp("2026-10-12T10:00:00") is None
    assert source_timestamp("missing") is None
    with pytest.raises(ValueError, match="stable"):
        hardware_resource({"Id": "1"})


def test_recipe_otel_exports_multiple_points_logs_and_actual_spans(monkeypatch, capsys):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    with RecipeTelemetry({"SerialNumber": "hardware-42"}) as telemetry:
        telemetry.gauge("redfish.hardware.temperature", 43, "Cel", {"sensor.id": "cpu"})
        telemetry.gauge("redfish.hardware.temperature", 28, "Cel", {"sensor.id": "intake"})
        telemetry.log("Fan failed", "Critical", "2026-10-12T10:00:00Z", {"sensor.id": "fan"})
        with telemetry.tracer.start_as_current_span("actual.poll"):
            pass
        with pytest.raises(ValueError, match="mix units"):
            telemetry.gauge("redfish.hardware.temperature", 88, "W")
        with pytest.raises(ValueError, match="finite"):
            telemetry.gauge("redfish.bad", float("nan"), "Cel")
    output = capsys.readouterr().out
    assert '"host.id": "hardware-42"' in output
    assert '"value": 43.0' in output and '"value": 28.0' in output
    assert '"name": "actual.poll"' in output
    assert '"body": "Fan failed"' in output
    assert '"timestamp": "2026-10-12T10:00:00.000000Z"' in output
