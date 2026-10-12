"""Discovery-based HTTPS client for the catalog's opt-in hardware recipes.

This client is separate from the simulator and the GET-only observer. Writes
are previews unless ALLOW_REDFISH_WRITES=1 is explicitly set by the operator.
"""

from __future__ import annotations

import json
import os
from functools import cached_property
from urllib.parse import unquote, urlsplit

import httpx


class CapabilityError(RuntimeError):
    """The selected service does not advertise a required capability."""


def required(name):
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Set {name} for this recipe; see the setup notes")
    return value


def redact(value):
    if isinstance(value, dict):
        return {
            key: "<redacted>"
            if any(
                s in key.lower()
                for s in ("password", "token", "secret", "privatekey", "authorization")
            )
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def show(value):
    print(json.dumps(redact(value), indent=2, default=str))


def fields(resource, *names):
    """Retain null/missing fields so an unsupported reading is never a false zero."""
    return {name: resource.get(name) for name in names}


class RecipeClient:
    def __init__(
        self, endpoint, username, password, ca_bundle=None, *, allow_writes=False, transport=None
    ):
        url = httpx.URL(endpoint)
        if (
            url.scheme != "https"
            or not url.host
            or url.userinfo
            or url.path not in {"", "/"}
            or url.query
            or url.fragment
        ):
            raise ValueError("Use an HTTPS BMC origin with credentials supplied separately")
        self.origin = url.copy_with(path="/")
        self.allow_writes = allow_writes
        self.client = httpx.Client(
            base_url=endpoint.rstrip("/"),
            auth=httpx.BasicAuth(username, password),
            verify=ca_bundle or True,
            timeout=30,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        )

    @classmethod
    def from_env(cls):
        return cls(
            required("BMC_URL"),
            required("BMC_USERNAME"),
            required("BMC_PASSWORD"),
            os.getenv("BMC_CA_BUNDLE"),
            allow_writes=os.getenv("ALLOW_REDFISH_WRITES") == "1",
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.client.close()

    def path(self, link):
        if isinstance(link, dict):
            link = link.get("@odata.id")
        if not isinstance(link, str) or not link:
            raise CapabilityError("No @odata.id link is advertised for this resource")
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            url = httpx.URL(link)
            if (url.scheme, url.host, url.port) != (
                self.origin.scheme,
                self.origin.host,
                self.origin.port,
            ) or url.userinfo:
                raise ValueError("Cross-origin Redfish links are refused")
        decoded = unquote(parsed.path)
        if (
            parsed.fragment
            or not (decoded == "/redfish/v1" or decoded.startswith("/redfish/v1/"))
            or any(part in {".", ".."} for part in decoded.split("/"))
            or "\\" in decoded
            or "%" in decoded
        ):
            raise ValueError("Only local /redfish/v1 resource links are accepted")
        return parsed.path + ("?" + parsed.query if parsed.query else "")

    def get(self, link):
        response = self.client.get(self.path(link))
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Expected a Redfish resource object")
        if response.headers.get("etag"):
            data.setdefault("@odata.etag", response.headers["etag"])
        return data

    @cached_property
    def root(self):
        return self.get("/redfish/v1")

    def follow(self, resource, name):
        if not resource.get(name):
            raise CapabilityError(f"{resource.get('Name', 'Resource')} does not advertise {name}")
        return self.get(resource[name])

    def members(self, collection):
        """Follow collection pagination, with a bounded cycle-safe walk."""
        page = (
            collection
            if isinstance(collection, dict) and "Members" in collection
            else self.get(collection)
        )
        result, seen = [], set()
        for _ in range(100):
            for member in page.get("Members", []):
                # Expanded collections can contain the complete member resource.
                result.append(
                    member if member.get("@odata.type") and "Id" in member else self.get(member)
                )
            next_link = page.get("Members@odata.nextLink")
            if not next_link:
                return result
            path = self.path(next_link)
            if path in seen:
                raise ValueError("Repeated collection nextLink")
            seen.add(path)
            page = self.get(path)
        raise ValueError("Collection exceeded 100 pages")

    def choose(self, resources, id_variable):
        wanted = os.getenv(id_variable)
        if wanted:
            for resource in resources:
                if resource.get("Id") == wanted:
                    return resource
            raise CapabilityError(f"No resource with {id_variable}={wanted}")
        if len(resources) == 1:
            return resources[0]
        raise CapabilityError(
            f"Set {id_variable}; available IDs: {[r.get('Id') for r in resources]}"
        )

    def system(self):
        return self.choose(self.members(self.follow(self.root, "Systems")), "BMC_SYSTEM_ID")

    def chassis(self):
        return self.choose(self.members(self.follow(self.root, "Chassis")), "BMC_CHASSIS_ID")

    def manager(self):
        return self.choose(self.members(self.follow(self.root, "Managers")), "BMC_MANAGER_ID")

    def storage(self):
        return self.choose(self.members(self.follow(self.system(), "Storage")), "STORAGE_ID")

    def drive(self):
        return self.choose([self.get(d) for d in self.storage().get("Drives", [])], "DRIVE_ID")

    def volume(self):
        return self.choose(self.members(self.follow(self.storage(), "Volumes")), "VOLUME_ID")

    def sensors(self, reading_type=None):
        sensors = self.members(self.follow(self.chassis(), "Sensors"))
        return [s for s in sensors if reading_type is None or s.get("ReadingType") == reading_type]

    def settings(self, resource):
        link = resource.get("@Redfish.Settings", {}).get("SettingsObject")
        if not link:
            raise CapabilityError("No pending SettingsObject is advertised")
        return self.get(link)

    def write(self, method, link, body=None, *, etag=None):
        path = self.path(link)
        if method not in {"POST", "PATCH", "DELETE"}:
            raise ValueError("Recipe writes support POST, PATCH and DELETE")
        if not self.allow_writes:
            return {"dry_run": True, "method": method, "path": path, "body": redact(body)}
        headers = {"If-Match": etag} if etag else {}
        response = self.client.request(method, path, json=body, headers=headers)
        response.raise_for_status()
        return {
            "status": response.status_code,
            "location": response.headers.get("Location"),
            "retry_after": response.headers.get("Retry-After"),
            "body": redact(response.json()) if response.content else None,
        }

    def patch(self, resource, body):
        return self.write("PATCH", resource, body, etag=resource.get("@odata.etag"))

    def action(self, resource, name, body):
        action = resource.get("Actions", {}).get("#" + name)
        if not action or not action.get("target"):
            raise CapabilityError(f"Action {name} is not advertised")
        for parameter, value in body.items():
            allowed = action.get(parameter + "@Redfish.AllowableValues")
            if allowed is not None and value not in allowed:
                raise CapabilityError(f"{parameter} must be one of {allowed}")
        if action.get("@Redfish.ActionInfo"):
            info = self.get(action["@Redfish.ActionInfo"])
            for parameter in info.get("Parameters", []):
                key = parameter["Name"]
                if parameter.get("Required") and key not in body:
                    raise CapabilityError(f"Action requires {key}; inspect its ActionInfo")
                if (
                    key in body
                    and parameter.get("AllowableValues")
                    and body[key] not in parameter["AllowableValues"]
                ):
                    raise CapabilityError(f"Unsupported {key} value")
        return self.write("POST", action["target"], body)

    def boot(self, target, **extra):
        system = self.system()
        boot = system.get("Boot", {})
        if not boot:
            raise CapabilityError("This system does not advertise Boot controls")
        allowed = boot.get("BootSourceOverrideTarget@Redfish.AllowableValues")
        if allowed is not None and target not in allowed:
            raise CapabilityError(f"Boot targets supported: {allowed}")
        return self.patch(
            system,
            {
                "Boot": {
                    "BootSourceOverrideEnabled": "Once",
                    "BootSourceOverrideTarget": target,
                    **extra,
                }
            },
        )
