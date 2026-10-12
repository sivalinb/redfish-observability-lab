import httpx
import pytest

from redfish_lab.readonly import ReadOnlyRedfishClient


def fixture_transport():
    resources = {
        "/redfish/v1": {
            "Systems": {"@odata.id": "/redfish/v1/Systems"},
            "Chassis": {"@odata.id": "/redfish/v1/Chassis"},
        },
        "/redfish/v1/Systems": {"Members": [{"@odata.id": "/redfish/v1/Systems/vendor-id"}]},
        "/redfish/v1/Systems/vendor-id": {
            "Id": "vendor-id",
            "HostName": "physical-7",
            "SerialNumber": "actual-fixture",
        },
        "/redfish/v1/Chassis": {"Members": [{"@odata.id": "/redfish/v1/Chassis/enclosure"}]},
        "/redfish/v1/Chassis/enclosure": {
            "Id": "enclosure",
            "Sensors": {"@odata.id": "/redfish/v1/Chassis/enclosure/Sensors"},
        },
        "/redfish/v1/Chassis/enclosure/Sensors": {
            "Members": [{"@odata.id": "/redfish/v1/Chassis/enclosure/Sensors/temp"}]
        },
        "/redfish/v1/Chassis/enclosure/Sensors/temp": {
            "Id": "temp",
            "ReadingType": "Temperature",
            "ReadingUnits": "Cel",
            "Reading": 43.2,
        },
    }

    def respond(request):
        assert request.method == "GET"
        return httpx.Response(200, json=resources[request.url.path])

    return httpx.MockTransport(respond)


def test_real_client_discovers_vendor_ids_and_sensor_links():
    client = ReadOnlyRedfishClient(
        "https://bmc.example", "observer", "placeholder", transport=fixture_transport()
    )
    try:
        assert client.identity()["host.name"] == "physical-7"
        readings = client.readings()
        assert readings[0]["value"] == 43.2
        assert readings[0]["attributes"]["chassis.id"] == "enclosure"
    finally:
        client.close()


@pytest.mark.parametrize(
    "endpoint",
    ["http://bmc.example", "https://user:pass@bmc.example", "https://bmc.example/redfish/v1"],
)
def test_real_client_requires_a_verified_https_origin(endpoint):
    with pytest.raises(ValueError):
        ReadOnlyRedfishClient(endpoint, "observer", "placeholder")


def test_external_resource_links_cannot_forward_credentials():
    client = ReadOnlyRedfishClient(
        "https://bmc.example", "observer", "placeholder", transport=fixture_transport()
    )
    try:
        with pytest.raises(ValueError):
            client.get("https://another.example/redfish/v1")
    finally:
        client.close()


def test_unsupported_sensor_units_are_skipped():
    base = fixture_transport()

    def respond(request):
        response = base.handle_request(request)
        payload = response.json()
        if payload.get("ReadingType") == "Temperature":
            payload["ReadingUnits"] = "degF"
        return httpx.Response(200, json=payload)

    client = ReadOnlyRedfishClient(
        "https://bmc.example", "observer", "placeholder", transport=httpx.MockTransport(respond)
    )
    try:
        assert client.readings() == []
    finally:
        client.close()
