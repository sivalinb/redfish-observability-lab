"""Opt-in, read-only real BMC access with TLS verification and resource discovery."""

from __future__ import annotations

from urllib.parse import urlparse

import httpx


class ReadOnlyRedfishClient:
    def __init__(self, endpoint, username, password, ca_bundle=None, transport=None):
        url = urlparse(endpoint)
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError(
                "BMC endpoint must be https://host with credentials supplied separately"
            )
        if url.path not in {"", "/"} or url.query or url.fragment:
            raise ValueError("Use the BMC origin URL, without a resource path, query or fragment")
        self.client = httpx.Client(
            base_url=endpoint.rstrip("/"),
            auth=httpx.BasicAuth(username, password),
            verify=ca_bundle or True,
            follow_redirects=False,
            timeout=10,
            transport=transport,
            trust_env=False,
        )

    def get(self, path):
        # Do not let a device-supplied link forward credentials to a different origin.
        if not isinstance(path, str) or not (
            path == "/redfish/v1" or path.startswith("/redfish/v1/")
        ):
            raise ValueError("Only local /redfish/v1 resource links are accepted")
        response = self.client.get(path)
        response.raise_for_status()
        return response.json()

    def optional(self, path):
        try:
            return self.get(path)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return {}
            raise

    def identity(self):
        root = self.get("/redfish/v1")
        systems = self.get(root["Systems"]["@odata.id"])
        if not systems.get("Members"):
            raise ValueError("No ComputerSystem resources advertised by the BMC")
        system = self.get(systems["Members"][0]["@odata.id"])
        return {
            "host.name": system.get("HostName") or system.get("Name") or system["Id"],
            "lab.physical_server.id": system.get("SerialNumber")
            or system.get("UUID")
            or system["Id"],
        }

    def readings(self):
        root = self.get("/redfish/v1")
        chassis = self.get(root["Chassis"]["@odata.id"])
        readings = []
        for member in chassis.get("Members", []):
            info = self.get(member["@odata.id"])
            cid = info.get("Id", "unknown")
            if info.get("Sensors"):
                sensors = self.get(info["Sensors"]["@odata.id"])
                for sensor_link in sensors.get("Members", []):
                    sensor = self.get(sensor_link["@odata.id"])
                    typ = sensor.get("ReadingType")
                    units = sensor.get("ReadingUnits", "")
                    mapping = {
                        "Temperature": ("lab.hardware.temperature", "Cel"),
                        "Power": ("lab.hardware.power", "W"),
                        "Rotational": ("lab.hardware.fan.speed", "{revolution}/min"),
                    }
                    if typ in mapping and isinstance(sensor.get("Reading"), (int, float)):
                        name, unit = mapping[typ]
                        supported_units = {
                            "Temperature": {"Cel"},
                            "Power": {"W"},
                            "Rotational": {"RPM", "{revolution}/min"},
                        }
                        if units not in supported_units[typ]:
                            continue
                        readings.append(
                            {
                                "name": name,
                                "unit": unit,
                                "value": sensor["Reading"],
                                "attributes": {
                                    "chassis.id": cid,
                                    "sensor.id": sensor.get("Id", "unknown"),
                                },
                            }
                        )
            else:
                thermal = self.optional(
                    info.get("Thermal", {}).get("@odata.id", member["@odata.id"] + "/Thermal")
                )
                power = self.optional(
                    info.get("Power", {}).get("@odata.id", member["@odata.id"] + "/Power")
                )
                for item in thermal.get("Temperatures", []):
                    if isinstance(item.get("ReadingCelsius"), (int, float)):
                        readings.append(
                            {
                                "name": "lab.hardware.temperature",
                                "unit": "Cel",
                                "value": item["ReadingCelsius"],
                                "attributes": {
                                    "chassis.id": cid,
                                    "sensor.id": str(item.get("MemberId", "temperature")),
                                },
                            }
                        )
                for item in thermal.get("Fans", []):
                    if item.get("ReadingUnits") == "RPM" and isinstance(
                        item.get("Reading"), (int, float)
                    ):
                        readings.append(
                            {
                                "name": "lab.hardware.fan.speed",
                                "unit": "{revolution}/min",
                                "value": item["Reading"],
                                "attributes": {
                                    "chassis.id": cid,
                                    "sensor.id": str(item.get("MemberId", "fan")),
                                },
                            }
                        )
                for item in power.get("PowerControl", []):
                    if isinstance(item.get("PowerConsumedWatts"), (int, float)):
                        readings.append(
                            {
                                "name": "lab.hardware.power",
                                "unit": "W",
                                "value": item["PowerConsumedWatts"],
                                "attributes": {
                                    "chassis.id": cid,
                                    "sensor.id": str(item.get("MemberId", "power")),
                                },
                            }
                        )
        return readings

    def close(self):
        self.client.close()
