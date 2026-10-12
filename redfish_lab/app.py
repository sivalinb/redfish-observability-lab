"""Gradio application. All controls target the embedded simulator."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import gradio as gr
import uvicorn

from . import use_cases, visuals
from .api import make_api
from .lessons import LESSONS, payload_for
from .runtime import LabRegistry

ASSETS = Path(__file__).parent / "assets"
API_PATHS = [
    "/redfish/v1",
    "/redfish/v1/Systems/1",
    "/redfish/v1/Chassis/1",
    "/redfish/v1/Chassis/1/Sensors",
    "/redfish/v1/Chassis/1/Sensors/CPU1Temp",
    "/redfish/v1/Chassis/1/Thermal",
    "/redfish/v1/Chassis/1/Power",
    "/redfish/v1/Managers/1",
    "/redfish/v1/Systems/1/Bios",
    "/redfish/v1/Systems/1/Bios/Settings",
    "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "/redfish/v1/TaskService/Tasks",
    "/redfish/v1/Managers/1/VirtualMedia/CD",
    "/redfish/v1/Systems/1/Storage/1",
    "/redfish/v1/Systems/1/Storage/1/Drives/1",
    "/redfish/v1/Systems/1/Storage/1/Volumes",
    "/redfish/v1/AccountService/Accounts",
    "/redfish/v1/AccountService/Roles/ReadOnly",
    "/redfish/v1/EventService/Subscriptions",
    "/redfish/v1/Managers/1/LogServices/Hardware/Entries",
    "/redfish/v1/TelemetryService/MetricReports/LiveHardware",
    "/redfish/v1/TelemetryService/MetricReportDefinitions/LiveHardware",
]


def create_app(background=True):
    registry = LabRegistry()
    app = make_api(registry, background=background)
    css = (ASSETS / "style.css").read_text()
    theme = gr.themes.Base(primary_hue="cyan", secondary_hue="slate", neutral_hue="slate")

    with gr.Blocks(
        title="Redfish Observatory", theme=theme, css=css, analytics_enabled=False, fill_width=True
    ) as demo:
        session_id = gr.State()
        gr.HTML(visuals.HEADER)
        with gr.Tabs():
            with gr.Tab("Live rack", id="live"):
                live = gr.HTML()
                with gr.Row():
                    with gr.Column(scale=2):
                        fault = gr.Dropdown(
                            [
                                "Healthy",
                                "Fan failure",
                                "Power supply failure",
                                "Disk failure",
                                "OS crash",
                            ],
                            value="Fan failure",
                            label="Choose a scenario",
                            interactive=True,
                        )
                        with gr.Row():
                            inject = gr.Button("Inject scenario", variant="primary")
                            recover = gr.Button("Restore healthy")
                    with gr.Column(scale=2):
                        load = gr.Slider(
                            0, 100, value=40, step=5, label="Simulated CPU workload (%)"
                        )
                        apply_load = gr.Button("Apply workload")
                    with gr.Column(scale=1):
                        motion = gr.Checkbox(value=True, label="Animate diagrams")
                        gr.Markdown(
                            "**Measurements continue** when animation is disabled. Reduced motion preferences are respected."
                        )
                live_note = gr.Markdown("Starting your simulated rack…")
            with gr.Tab("100 use cases", id="catalog"):
                gr.HTML("""<div class="rf-catalog-heading"><div>
<div class="rf-eyebrow">THE PRACTICAL REDFISH LIBRARY</div>
<h2>100 ways to use Redfish.</h2>
<p>Find a real problem, understand the flow, and take a Python example with you.</p>
</div><div class="rf-catalog-total">100<small>examples · 10 areas</small></div></div>""")
                with gr.Row():
                    catalog_search = gr.Textbox(
                        label="Search use cases",
                        placeholder="Try temperature, PXE, RAID, certificate or OpenTelemetry…",
                        scale=3,
                    )
                    catalog_area = gr.Dropdown(
                        ["All areas", *use_cases.CATEGORIES],
                        value="All areas",
                        label="Area",
                        scale=2,
                    )
                    catalog_kind = gr.Dropdown(
                        ["All operations", *use_cases.KINDS],
                        value="All operations",
                        label="Operation",
                        scale=1,
                    )
                    catalog_clear = gr.Button("Clear filters", scale=0)
                catalog_count = gr.HTML(use_cases.count_html(use_cases.CATALOG))
                catalog_matches = gr.State([case.id for case in use_cases.CATALOG])
                catalog_selection = gr.State(1)
                catalog_choice = gr.Dropdown(
                    [(case.label, case.id) for case in use_cases.CATALOG],
                    value=1,
                    label="Choose a use case — or select a row in the full list below",
                    interactive=True,
                )
                with gr.Row():
                    with gr.Column(scale=2):
                        catalog_detail = gr.HTML(use_cases.detail_html(1))
                        catalog_inspect = gr.Button("Inspect simulator resource", interactive=True)
                        with gr.Accordion("Local simulator response", open=False):
                            catalog_response = gr.JSON(label="Teaching resource · GET only")
                    with gr.Column(scale=3):
                        catalog_code = gr.Code(
                            value=use_cases.BY_ID[1].code,
                            language="python",
                            interactive=False,
                            label="Python sample · install this project first",
                            lines=23,
                            max_lines=32,
                            wrap_lines=True,
                            elem_classes=["rf-python-sample"],
                        )
                        with gr.Row():
                            catalog_download = gr.DownloadButton(
                                "Download this Python sample",
                                value=use_cases.sample_path(1),
                            )
                            gr.DownloadButton(
                                "Download all 100 samples (.zip)",
                                value=str(
                                    use_cases.sample_directory() / "redfish-100-python-samples.zip"
                                ),
                            )
                        gr.Markdown(
                            "**Reads use verified HTTPS. Changes preview the request by default.** "
                            "The catalog displays code for you to review and run separately. "
                            "Each example names its device requirements."
                        )
                with gr.Accordion("Setup, credentials and example scope", open=False):
                    gr.Markdown(use_cases.SETUP)
                gr.Markdown(
                    "### All matching use cases\nSelect any row to open its explanation and code. The numbered library is curated for learning; device support varies."
                )
                catalog_table = gr.Dataframe(
                    value=use_cases.table_rows(use_cases.CATALOG),
                    headers=["#", "Use case", "Area", "Operation", "Schema"],
                    datatype="str",
                    type="array",
                    interactive=False,
                    max_height=520,
                    wrap=True,
                    column_widths=[55, 350, 210, 120, 180],
                    label="100 Redfish use cases",
                    show_row_numbers=False,
                )
            with gr.Tab("Management studio", id="manage"):
                with gr.Row():
                    with gr.Column(scale=2):
                        choice = gr.Dropdown(
                            list(LESSONS),
                            value=list(LESSONS)[0],
                            label="Explore a capability",
                            interactive=True,
                        )
                        lesson = gr.HTML(visuals.lesson_html(list(LESSONS)[0]))
                        state_view = gr.HTML()
                    with gr.Column(scale=2):
                        request_role = gr.Dropdown(
                            ["Administrator", "Operator", "ReadOnly"],
                            value="Administrator",
                            label="Teaching request role",
                        )
                        with gr.Group(visible=False) as power_group:
                            power_action = gr.Dropdown(
                                [
                                    "On",
                                    "GracefulShutdown",
                                    "GracefulRestart",
                                    "ForceRestart",
                                    "ForceOff",
                                ],
                                value="GracefulRestart",
                                label="Power action",
                            )
                        with gr.Group(visible=False) as cap_group:
                            cap = gr.Slider(
                                150, 600, value=450, step=10, label="Power budget (watts)"
                            )
                        with gr.Group(visible=False) as bios_group:
                            virtualization = gr.Radio(
                                ["Enabled", "Disabled"],
                                value="Disabled",
                                label="Pending CPU virtualization setting",
                            )
                        with gr.Group(visible=False) as firmware_group:
                            version = gr.Textbox(
                                value="2.1.0", label="Demo target firmware version"
                            )
                        with gr.Group(visible=False) as boot_group:
                            boot = gr.Dropdown(
                                ["Hdd", "Pxe", "Cd", "Usb"], value="Cd", label="Next boot source"
                            )
                        with gr.Group(visible=False) as media_group:
                            image = gr.Textbox(
                                value="https://example.com/demo-linux.iso",
                                label="Simulated installer URL",
                            )
                        with gr.Group(visible=False) as name_group:
                            name = gr.Textbox(
                                value="learning-volume", label="Volume or demo account name"
                            )
                        with gr.Group(visible=False) as raid_group:
                            raid = gr.Dropdown(
                                ["RAID1", "RAID0"], value="RAID1", label="Volume RAID type"
                            )
                        with gr.Group(visible=False) as account_group:
                            account_role = gr.Dropdown(
                                ["ReadOnly", "Operator", "Administrator"],
                                value="ReadOnly",
                                label="New account role",
                            )
                        run = gr.Button("Run selected operation", variant="primary")
                        operation_note = gr.Markdown(
                            "Read an inventory first, then explore the write operations."
                        )
                        request_preview = gr.JSON(
                            label="Request preview",
                            value={"method": "GET", "path": "/redfish/v1/Systems/1", "body": None},
                        )
                        response_view = gr.JSON(label="Actual HTTP request and response")
            with gr.Tab("Signal pipeline", id="signals"):
                flow_view = gr.HTML()
                with gr.Row():
                    transport = gr.Radio(
                        ["Polling + push", "Polling only", "Push reports + events"],
                        value="Polling + push",
                        label="Hardware collection method",
                    )
                    interval = gr.Slider(
                        1, 15, value=3, step=1, label="Poll / metric report interval (seconds)"
                    )
                    apply_transport = gr.Button("Apply collection settings", variant="primary")
                transport_note = gr.Markdown(
                    "Polling + push: readings are polled; fault events arrive by HTTP callback."
                )
                signal_view = gr.HTML()
                with gr.Accordion("Inspect the actual exported OpenTelemetry records", open=False):
                    inspect_signals = gr.Button("Refresh exported records")
                    exported_records = gr.JSON(label="Resource attributes, metrics, logs and spans")
                gr.Markdown("""The animated arrows illustrate direction. Counts come from the **real SDK exporters**.
The local viewer keeps bounded recent records. To route all three signals through a separate Collector
into Grafana, use the optional `docker compose up --build` stack documented in the README.
Hardware metrics use the `lab.*` namespace because this is a simulated learning model.""")
            with gr.Tab("API explorer", id="api"):
                gr.Markdown(
                    "Start at `/redfish/v1` and follow `@odata.id` links. Resources and IDs vary on real hardware; these are this simulator's teaching endpoints."
                )
                api_path = gr.Dropdown(
                    API_PATHS, value="/redfish/v1", label="Resource path", allow_custom_value=True
                )
                read_api = gr.Button("GET resource", variant="primary")
                api_result = gr.JSON(label="HTTP response")
                gr.Markdown(
                    "**Logs and events:** read LogServices/Hardware/Entries for history. EventService subscriptions deliver new events. A metric report contains readings with their own sample timestamps."
                )
            with gr.Tab("Guided experiments", id="tour"):
                gr.HTML(visuals.tour_html())
                gr.Markdown("""**What is real here?** Python, Gradio, FastAPI HTTP operations, the OpenTelemetry SDK,
metrics/log/span exporters, request durations, trace parents and optional OTLP delivery.

**What is simulated?** Hardware, sensors, faults, CPU load, firmware flashing, OS installation,
volume allocation, and account identities. The simulator is a teaching subset, not a conformant
Redfish service or an authenticated management controller. Every control targets the simulator.""")
        gr.HTML(
            '<div class="rf-footer">REDFISH OBSERVATORY · Python + Gradio · No server hardware required<br>Independent BMC management · Hardware-to-application correlation · Near real-time collection</div>'
        )

        views = [live, flow_view, signal_view, state_view]

        def refresh(sid, animate):
            s = registry.get(sid)
            return [
                visuals.dashboard(s, animate),
                visuals.flow(s, animate),
                visuals.signals(s),
                visuals.management_state(s),
            ]

        async def initialize():
            s = registry.new()
            await registry.step(s)
            s.bridge.flush()
            return [s.id, *refresh(s.id, True), s.note]

        demo.load(initialize, outputs=[session_id, *views, live_note])
        timer = gr.Timer(1)
        timer.tick(
            refresh, inputs=[session_id, motion], outputs=views, queue=False, show_progress="hidden"
        )
        motion.change(
            lambda sid, animate, selected: [
                *refresh(sid, animate),
                visuals.lesson_html(selected, animate),
            ],
            inputs=[session_id, motion, choice],
            outputs=[*views, lesson],
            queue=False,
        )

        def filter_catalog(query, category, kind, selected):
            cases = use_cases.search_cases(query, category, kind)
            ids = [case.id for case in cases]
            selection = selected if selected in ids else (ids[0] if ids else None)
            return [
                use_cases.table_rows(cases),
                use_cases.count_html(cases),
                ids,
                gr.update(choices=[(case.label, case.id) for case in cases], value=selection),
            ]

        for control in (catalog_search, catalog_area, catalog_kind):
            control.change(
                filter_catalog,
                inputs=[catalog_search, catalog_area, catalog_kind, catalog_selection],
                outputs=[catalog_table, catalog_count, catalog_matches, catalog_choice],
                queue=False,
            )
        catalog_clear.click(
            lambda: ["", "All areas", "All operations"],
            outputs=[catalog_search, catalog_area, catalog_kind],
            queue=False,
        )

        def open_case(selected, animate):
            case = use_cases.BY_ID.get(selected)
            return [
                use_cases.detail_html(selected, animate),
                case.code if case else "",
                gr.update(value=use_cases.sample_path(selected), interactive=case is not None),
                gr.update(interactive=bool(case and case.demo_path)),
                None,
                selected,
            ]

        catalog_choice.change(
            open_case,
            inputs=[catalog_choice, motion],
            outputs=[
                catalog_detail,
                catalog_code,
                catalog_download,
                catalog_inspect,
                catalog_response,
                catalog_selection,
            ],
            queue=False,
        )
        motion.change(
            use_cases.detail_html,
            inputs=[catalog_choice, motion],
            outputs=catalog_detail,
            queue=False,
        )

        def select_case(ids, event: gr.SelectData):
            # Use the displayed row's identity so sorting cannot select another case.
            selected = use_cases.row_case_id(event.row_value, ids)
            return gr.update(value=selected) if selected is not None else gr.skip()

        catalog_table.select(
            select_case, inputs=catalog_matches, outputs=catalog_choice, queue=False
        )

        async def inspect_catalog_resource(sid, selected):
            case = use_cases.BY_ID.get(selected)
            if not case or not case.demo_path:
                return {"message": "This case requires compatible real hardware."}
            s = registry.get(sid)
            await registry.request(s, "GET", case.demo_path)
            return s.model.last_request

        catalog_inspect.click(
            inspect_catalog_resource,
            inputs=[session_id, catalog_choice],
            outputs=catalog_response,
        )

        async def scenario(sid, selected, percent, animate):
            s = registry.get(sid)
            response = await registry.request(
                s, "POST", "/lab/scenario", {"fault": selected, "load": int(percent)}
            )
            if response.status_code >= 400:
                return [*refresh(sid, animate), f"Request failed: {response.json()}"]
            s.note = f"Scenario: **{selected}** · workload **{int(percent)}%**. Hardware refreshes every second; collection follows your selected interval."
            return [*refresh(sid, animate), s.note]

        inject.click(
            scenario, inputs=[session_id, fault, load, motion], outputs=[*views, live_note]
        )

        async def restore(sid, percent, animate):
            return await scenario(sid, "Healthy", percent, animate)

        recover.click(restore, inputs=[session_id, load, motion], outputs=[*views, live_note])

        async def set_load(sid, percent, animate):
            s = registry.get(sid)
            return await scenario(sid, s.model.fault, percent, animate)

        apply_load.click(set_load, inputs=[session_id, load, motion], outputs=[*views, live_note])

        parameters = [
            choice,
            power_action,
            cap,
            virtualization,
            version,
            boot,
            image,
            name,
            raid,
            account_role,
        ]
        groups = [
            power_group,
            cap_group,
            bios_group,
            firmware_group,
            boot_group,
            media_group,
            name_group,
            raid_group,
            account_group,
        ]
        visible_indices = [{2}, {3}, {4}, {5}, {6}, {7}, {8, 9}, {8}, {9}]

        def preview(*args):
            selected = args[0]
            selected_lesson = LESSONS[selected]
            return {
                "method": selected_lesson.verb,
                "path": selected_lesson.path,
                "body": payload_for(*args),
            }

        def choose(*args):
            params, animate = args[:-1], args[-1]
            index = list(LESSONS).index(params[0])
            return [
                visuals.lesson_html(params[0], animate),
                preview(*params),
                *[gr.update(visible=index in indices) for indices in visible_indices],
            ]

        choice.change(
            choose, inputs=[*parameters, motion], outputs=[lesson, request_preview, *groups]
        )
        for param in parameters[1:]:
            param.change(preview, inputs=parameters, outputs=request_preview, queue=False)

        async def execute(sid, animate, teaching_role, *args):
            s = registry.get(sid)
            planned = preview(*args)
            response = await registry.request(
                s, planned["method"], planned["path"], planned["body"], role=teaching_role
            )
            status = response.status_code
            meaning = {
                200: "Read completed",
                201: "Resource created",
                202: "Accepted; task is still running",
                204: "Change accepted",
                403: "Role denied this operation",
            }.get(status, "Request rejected")
            note = f"**HTTP {status} · {meaning}.** {LESSONS[args[0]].next_step}"
            return [s.model.last_request, note, *refresh(sid, animate)]

        run.click(
            execute,
            inputs=[session_id, motion, request_role, *parameters],
            outputs=[response_view, operation_note, *views],
        )

        async def change_transport(sid, mode, seconds, animate):
            s = registry.get(sid)
            await registry.set_transport(s, mode, seconds)
            explanation = {
                "Polling + push": "Readings arrive by REST polling; fault events arrive by HTTP callback.",
                "Polling only": "Readings and stored fault logs are discovered at the next poll.",
                "Push reports + events": "Readings arrive in periodic MetricReports; fault events arrive by HTTP callback.",
            }[mode]
            return [*refresh(sid, animate), f"**{mode} · {int(seconds)} seconds.** {explanation}"]

        apply_transport.click(
            change_transport,
            inputs=[session_id, transport, interval, motion],
            outputs=[*views, transport_note],
        )

        async def explore(sid, path):
            if not path.startswith("/redfish/v1"):
                return {"error": "Choose a /redfish/v1 resource in this simulator."}
            s = registry.get(sid)
            await registry.request(s, "GET", path)
            return s.model.last_request

        read_api.click(explore, inputs=[session_id, api_path], outputs=api_result)
        inspect_signals.click(
            lambda sid: registry.get(sid).bridge.buffer.snapshot(),
            inputs=session_id,
            outputs=exported_records,
        )

    app = gr.mount_gradio_app(app, demo, path="/", show_api=False)
    registry.app = app
    return app


def main():
    parser = argparse.ArgumentParser(description="Run the Redfish Observatory learning lab")
    parser.add_argument("--host", default=os.getenv("LAB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "7860")))
    args = parser.parse_args()
    uvicorn.run(create_app(), host=args.host, port=args.port, access_log=False)


if __name__ == "__main__":
    main()
