import httpx
import pytest

from redfish_lab.recipe_client import CapabilityError, RecipeClient, redact


@pytest.mark.parametrize(
    "link",
    [
        "https://other.example/redfish/v1",
        "//other.example/redfish/v1",
        "/redfish/v10/Systems",
        "/redfish/v1/../private",
        "/redfish/v1/%2e%2e/private",
        "/redfish/v1/%252e%252e/private",
        "/private",
        "/redfish/v1#secret",
    ],
)
def test_recipe_client_rejects_credential_forwarding_and_path_escape(link):
    def respond(_):
        pytest.fail("Invalid links must not issue HTTP requests")

    with RecipeClient(
        "https://bmc.example", "operator", "placeholder", transport=httpx.MockTransport(respond)
    ) as rf:
        with pytest.raises(ValueError):
            rf.get(link)


def test_recipe_client_follows_same_origin_collection_pagination(monkeypatch):
    monkeypatch.delenv("BMC_SYSTEM_ID", raising=False)
    resources = {
        "/redfish/v1": {"Systems": {"@odata.id": "/redfish/v1/Systems"}},
        "/redfish/v1/Systems": {
            "Members": [{"@odata.id": "/redfish/v1/Systems/A"}],
            "Members@odata.nextLink": "/redfish/v1/Systems?$skip=1",
        },
        "/redfish/v1/Systems?$skip=1": {
            "Members": [{"@odata.id": "https://bmc.example/redfish/v1/Systems/B"}]
        },
        "/redfish/v1/Systems/A": {"Id": "A"},
        "/redfish/v1/Systems/B": {"Id": "B"},
    }
    transport = httpx.MockTransport(
        lambda r: httpx.Response(200, json=resources[r.url.raw_path.decode()])
    )
    with RecipeClient("https://bmc.example", "observer", "placeholder", transport=transport) as rf:
        with pytest.raises(CapabilityError, match="available IDs"):
            rf.system()
        monkeypatch.setenv("BMC_SYSTEM_ID", "B")
        assert rf.system()["Id"] == "B"


def test_default_write_preview_never_sends_a_write_or_exposes_password():
    def respond(_):
        pytest.fail("A preview must not send HTTP")

    with RecipeClient(
        "https://bmc.example", "operator", "placeholder", transport=httpx.MockTransport(respond)
    ) as rf:
        preview = rf.write(
            "POST", "/redfish/v1/AccountService/Accounts", {"Password": "example-secret"}
        )
        assert preview["dry_run"] is True
        assert preview["body"]["Password"] == "<redacted>"


def test_opt_in_patch_uses_etag_and_returns_asynchronous_task_metadata():
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(
            202,
            json={"TaskState": "Running"},
            headers={"Location": "/redfish/v1/TaskService/Tasks/4", "Retry-After": "5"},
        )

    with RecipeClient(
        "https://bmc.example",
        "operator",
        "placeholder",
        allow_writes=True,
        transport=httpx.MockTransport(respond),
    ) as rf:
        result = rf.patch(
            {"@odata.id": "/redfish/v1/Systems/A", "@odata.etag": '"version-7"'},
            {"AssetTag": "rack-42"},
        )
        assert requests[0].method == "PATCH"
        assert requests[0].headers["If-Match"] == '"version-7"'
        assert result["status"] == 202 and result["retry_after"] == "5"
        assert result["location"].endswith("/4")


def test_actions_require_discovery_and_reject_unadvertised_enum_values():
    with RecipeClient("https://bmc.example", "operator", "placeholder") as rf:
        with pytest.raises(CapabilityError, match="not advertised"):
            rf.action({}, "ComputerSystem.Reset", {"ResetType": "On"})
        system = {
            "Actions": {
                "#ComputerSystem.Reset": {
                    "target": "/redfish/v1/Systems/A/Actions/ComputerSystem.Reset",
                    "ResetType@Redfish.AllowableValues": ["On"],
                }
            }
        }
        with pytest.raises(CapabilityError, match="must be one of"):
            rf.action(system, "ComputerSystem.Reset", {"ResetType": "ForceOff"})
        assert rf.action(system, "ComputerSystem.Reset", {"ResetType": "On"})["dry_run"]


def test_network_and_authentication_secrets_are_redacted_in_nested_records():
    result = redact(
        {
            "iSCSIBoot": {"CHAPSecret": "fixture-secret"},
            "HTTPHeaders": [{"Authorization": "fixture-secret"}],
        }
    )
    assert result["iSCSIBoot"]["CHAPSecret"] == "<redacted>"
    assert result["HTTPHeaders"][0]["Authorization"] == "<redacted>"


def test_missing_capabilities_and_pending_settings_are_explicit():
    with RecipeClient("https://bmc.example", "observer", "placeholder") as rf:
        with pytest.raises(CapabilityError, match="Sensors"):
            rf.follow({"Name": "Legacy enclosure"}, "Sensors")
        with pytest.raises(CapabilityError, match="SettingsObject"):
            rf.settings({})
