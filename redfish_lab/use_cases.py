"""The searchable 100-case catalog, illustrated details and downloadable recipes."""

from __future__ import annotations

import json
import re
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from html import escape
from pathlib import Path


@dataclass(frozen=True)
class UseCase:
    id: int
    category: str
    title: str
    why: str
    outcome: str
    requires: str
    schema: str
    kind: str
    demo_path: str | None
    imports: str
    body: str
    source: str

    @property
    def label(self):
        return f"{self.id:03d} · {self.title}"

    @property
    def filename(self):
        slug = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")
        return f"{self.id:03d}_{slug}.py"

    @property
    def code(self):
        return (
            f'"""{self.label}\nRequires: {self.requires}\n"""\n'
            "# Install this project first: python -m pip install -e .\n"
            "# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.\n"
            "# Writes are previews unless ALLOW_REDFISH_WRITES=1.\n"
            "import json\nimport os\n"
            "from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show\n"
            + (self.imports + "\n" if self.imports else "")
            + "\nwith RecipeClient.from_env() as rf:\n"
            + textwrap.indent(self.body, "    ")
            + "\n"
        )


CATALOG = tuple(
    UseCase(**case)
    for case in json.loads((Path(__file__).parent / "assets/use_cases.json").read_text())
)
BY_ID = {case.id: case for case in CATALOG}
CATEGORIES = tuple(dict.fromkeys(case.category for case in CATALOG))
KINDS = ("Read", "Change", "OpenTelemetry")

SETUP = """## Run a downloaded sample

Install this repository first: `python -m pip install -e .`. Use Python 3.11 or 3.12.
These samples use the included `RecipeClient`, whose source is in `redfish_lab/recipe_client.py`.

Set `BMC_URL=https://your-bmc`, `BMC_USERNAME` and `BMC_PASSWORD`. The URL is the controller origin,
without a resource path. Keep credentials out of source files. An organization CA can be supplied with
`BMC_CA_BUNDLE=/path/to/ca.pem`. TLS verification stays enabled. The client uses HTTP Basic authentication;
controllers requiring session-only authentication need a different authentication adapter.

If several resources exist, set the relevant ID variable (`BMC_SYSTEM_ID`, `BMC_CHASSIS_ID`,
`BMC_MANAGER_ID`, `STORAGE_ID`, `DRIVE_ID`, etc.). The helper lists available IDs rather than choosing
an arbitrary device. Recipe-specific inputs appear as `required('VARIABLE_NAME')` in the code.

Run `python 095_export-temperature-into-an-otel-dashboard.py` (use your downloaded filename).
All POST/PATCH/DELETE operations print a redacted **dry-run preview** by default.
An operator can explicitly enable execution with `ALLOW_REDFISH_WRITES=1` after reviewing the selected
device, payload and maintenance impact. HTTP 202 means accepted; follow the returned task/monitor and
Retry-After. A preview does not validate hardware compatibility or server-side permissions.

The catalog displays code; it never executes it against a real BMC. **Inspect simulator resource**
performs only a local GET. A simulator example illustrates a related resource and can omit fields or
actions required by the real-hardware recipe. The lab implements a small teaching subset of Redfish.

OTel examples export through the real Python SDK: console by default, or OTLP HTTP/protobuf when
`OTEL_EXPORTER_OTLP_ENDPOINT` is set to a Collector origin, such as `http://127.0.0.1:4318`.
`redfish.*` metric names here are example names, not standardized semantic conventions. Observable gauges
represent current collection/export time; source timestamps are retained separately for inspection.
Continuous adapters need suitable polling intervals, retries, sample freshness checks and log deduplication.
Hardware and application signals correlate by verified server identity and time, not invented trace IDs.

Availability depends on the advertised schema, writable properties, actions, licenses and firmware.
The examples are learning starting points; validate them against the device's supported schema and
vendor documentation. Optional facility/fabric cases require a Redfish-capable PDU, cooling or fabric controller.
"""


def search_cases(query="", category="All areas", kind="All operations"):
    tokens = (query or "").casefold().split()
    return [
        case
        for case in CATALOG
        if (category in {None, "All areas"} or case.category == category)
        and (kind in {None, "All operations"} or case.kind == kind)
        and all(
            token
            in " ".join(
                (
                    f"{case.id:03d}",
                    case.category,
                    case.title,
                    case.why,
                    case.outcome,
                    case.requires,
                    case.schema,
                    case.body,
                    case.kind,
                )
            ).casefold()
            for token in tokens
        )
    ]


def table_rows(cases):
    return [[f"{case.id:03d}", case.title, case.category, case.kind, case.schema] for case in cases]


def row_case_id(row, visible_ids):
    try:
        case_id = int(row[0])
    except (ValueError, TypeError, IndexError):
        return None
    return case_id if case_id in visible_ids else None


def count_html(cases):
    reads = sum(case.kind == "Read" for case in cases)
    changes = sum(case.kind == "Change" for case in cases)
    otel = sum(case.kind == "OpenTelemetry" for case in cases)
    return (
        '<div class="rf-catalog-count">'
        f"<strong>{len(cases)} / 100</strong> use cases"
        f"<span>{reads} reads · {changes} changes · {otel} OpenTelemetry</span></div>"
    )


def detail_html(case_id, animate=True):
    case = BY_ID.get(case_id)
    if case is None:
        return (
            '<div class="rf-case-empty">No matches. Clear a filter or try a broader search.</div>'
        )
    e = escape
    color = {"Read": "#56e0df", "Change": "#ffd084", "OpenTelemetry": "#bb9cff"}[case.kind]
    paused = "" if animate else " rf-paused"
    is_otel = case.kind == "OpenTelemetry"
    nodes = (
        [
            (18, "BMC sensors / logs", "Redfish resources"),
            (207, "Python adapter", "OpenTelemetry SDK"),
            (396, "Collector / console", "Shared server identity"),
        ]
        if is_otel
        else [
            (18, "Python automation", "Discover then request"),
            (207, "Management controller", case.schema),
            (
                396,
                "Hardware / firmware",
                "Read state" if case.kind == "Read" else "Apply supported change",
            ),
        ]
    )
    boxes = "".join(
        f'<rect x="{x}" y="31" width="165" height="72" rx="12" fill="#142638" stroke="#36506b"/>'
        f'<text x="{x + 82}" y="61" text-anchor="middle" fill="#ecf3ff" font-size="11" font-weight="600">{e(title)}</text>'
        f'<text x="{x + 82}" y="83" text-anchor="middle" fill="#b2c7dc" font-size="9">{e(subtitle)}</text>'
        for x, title, subtitle in nodes
    )
    wires = "".join(
        f'<path d="M{x} 67h24" stroke="{color}" stroke-width="2" class="rf-wire"/>'
        f'<path d="M{x + 19} 63l5 4-5 4" fill="none" stroke="{color}" stroke-width="2"/>'
        for x in (183, 372)
    )
    demo = "Simulator resource available" if case.demo_path else "Requires compatible hardware"
    return f'''<article class="rf-case{paused}">
<div class="rf-eyebrow">USE CASE {case.id:03d} / 100 · {e(case.category)}</div>
<h2>{e(case.title)}</h2>
<div class="rf-badges"><span class="rf-pill" style="color:{color}">{e(case.kind)}</span>
<span class="rf-pill">{e(case.schema)}</span></div>
<p class="rf-case-why">{e(case.why)}</p>
<svg viewBox="0 0 580 124" role="img" aria-label="{e(case.title)} request flow"
     xmlns="http://www.w3.org/2000/svg" style="font-family:system-ui">{wires}{boxes}</svg>
<div class="rf-case-fact"><b>What you get</b><p>{e(case.outcome)}</p></div>
<div class="rf-case-fact"><b>What the device needs</b><p>{e(case.requires)}</p></div>
<div class="rf-case-source"><span>{demo}</span> ·
<a href="{e(case.source)}" target="_blank" rel="noopener noreferrer">DMTF {e(case.schema)} schema ↗</a></div>
</article>'''


@lru_cache(maxsize=1)
def sample_directory():
    directory = Path(tempfile.mkdtemp(prefix="redfish-recipes-"))
    for case in CATALOG:
        (directory / case.filename).write_text(case.code)
    (directory / "SETUP.md").write_text(SETUP)
    with zipfile.ZipFile(
        directory / "redfish-100-python-samples.zip", "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for path in sorted(directory.iterdir()):
            if path.suffix in {".py", ".md"}:
                archive.write(path, path.name)
    return directory


def sample_path(case_id):
    case = BY_ID.get(case_id)
    return str(sample_directory() / case.filename) if case else None


def render_markdown():
    parts = [
        "# 100 practical Redfish use cases\n\n"
        "Ten areas, with a plain-language explanation and a Python sample for every case. "
        "This curated catalog prioritizes useful hardware workflows; ordering is for navigation. "
        "Each case names its required capabilities.\n\n",
        SETUP,
        "\n\n## Browse the catalog\n\n| # | Use case | Area | Operation |\n| --- | --- | --- | --- |\n",
    ]
    for case in CATALOG:
        parts.append(
            f"| {case.id:03d} | [{case.title}](#case-{case.id:03d}) | {case.category} | {case.kind} |\n"
        )
    for category in CATEGORIES:
        parts.append(f"\n## {category}\n")
        for case in CATALOG:
            if case.category != category:
                continue
            parts.append(
                f'\n<a id="case-{case.id:03d}"></a>\n\n### {case.label}\n\n'
                f"**Why Redfish fits:** {case.why}\n\n"
                f"**What you get:** {case.outcome}\n\n"
                f"**Requires:** {case.requires}\n\n"
                f"**Operation:** {case.kind}. [DMTF {case.schema} schema]({case.source}).\n\n"
                f"```python\n{case.code}```\n"
            )
    return "".join(parts)
