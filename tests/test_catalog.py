import ast
import json
import zipfile
from collections import Counter
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from redfish_lab.api import make_api
from redfish_lab.recipe_client import RecipeClient
from redfish_lab.runtime import LabRegistry
from redfish_lab.use_cases import (
    BY_ID,
    CATALOG,
    CATEGORIES,
    detail_html,
    render_markdown,
    row_case_id,
    sample_directory,
    search_cases,
)


def test_catalog_delivers_100_distinct_cases_in_ten_areas():
    assert [case.id for case in CATALOG] == list(range(1, 101))
    assert len({case.title for case in CATALOG}) == 100
    assert len({case.body for case in CATALOG}) == 100
    assert len(CATEGORIES) == 10
    assert set(Counter(case.category for case in CATALOG).values()) == {10}
    for case in CATALOG:
        assert all((case.why, case.outcome, case.requires, case.source, case.code))
        ast.parse(case.code, filename=case.filename)


def test_search_combines_text_area_and_operation_filters():
    assert len(search_cases()) == 100
    assert BY_ID[95] in search_cases("temperature", "Events & OpenTelemetry", "OpenTelemetry")
    assert search_cases("temperature", "Events & OpenTelemetry", "Change") == []
    assert search_cases("  095  ") == [BY_ID[95]]
    assert len(search_cases(category="Storage & data")) == 10
    assert len(search_cases(kind="OpenTelemetry")) == 8
    assert search_cases("nothing-matches-this-query") == []
    assert "No matches" in detail_html(None)
    assert "rf-paused" in detail_html(95, False)


def test_sorted_table_selection_uses_case_identity_not_row_position():
    assert row_case_id(["095", BY_ID[95].title], [12, 87, 89, 95, 100]) == 95
    assert row_case_id(["001"], [95, 100]) is None
    assert row_case_id(None, [95, 100]) is None


def test_download_archive_contains_all_runnable_samples_and_setup():
    with zipfile.ZipFile(sample_directory() / "redfish-100-python-samples.zip") as archive:
        assert len(archive.namelist()) == 101
        assert "SETUP.md" in archive.namelist()
        for case in CATALOG:
            assert archive.read(case.filename).decode() == case.code


def test_documentation_matches_the_ui_catalog():
    path = Path(__file__).parents[1] / "docs/USE_CASES.md"
    assert path.read_text() == render_markdown()


@pytest.mark.parametrize(
    "case_id",
    [
        1,
        2,
        7,
        8,
        9,
        11,
        12,
        13,
        16,
        19,
        27,
        36,
        46,
        47,
        51,
        52,
        53,
        71,
        75,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
        100,
    ],
)
def test_discovery_and_observability_samples_run_against_teaching_api(case_id, monkeypatch):
    """Execute source displayed in the UI across actual simulator HTTP routes."""
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    monkeypatch.setenv("SAMPLE_MAX_AGE_SECONDS", "30")
    monkeypatch.setenv(
        "METRIC_UNITS_JSON",
        json.dumps({"CPU1Temp": "Cel", "Fan1": "{revolution}/min", "SystemPower": "W"}),
    )
    registry = LabRegistry()
    app = make_api(registry, background=False)
    with TestClient(app) as api:

        def respond(request):
            assert request.method == "GET"
            result = api.get(request.url.raw_path.decode())
            return httpx.Response(result.status_code, json=result.json())

        def client_from_env():
            return RecipeClient(
                "https://bmc.example",
                "observer",
                "placeholder",
                transport=httpx.MockTransport(respond),
            )

        monkeypatch.setattr(RecipeClient, "from_env", client_from_env)
        exec(compile(BY_ID[case_id].code, BY_ID[case_id].filename, "exec"), {})


@pytest.mark.asyncio
async def test_every_advertised_simulator_example_path_exists(lab):
    registry, session = lab
    for path in {case.demo_path for case in CATALOG if case.demo_path}:
        response = await registry.request(session, "GET", path)
        assert response.status_code == 200, path
