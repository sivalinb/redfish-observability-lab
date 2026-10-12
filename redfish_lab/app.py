"""Gradio application. All controls target the embedded simulator."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import gradio as gr
import uvicorn

from . import visuals
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
