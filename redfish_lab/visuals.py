"""Responsive SVG illustrations and CSS animations; no remote assets or browser scripts."""

import time
from html import escape

from .lessons import LESSONS, TOUR


def e(value):
    return escape(str(value), quote=True)


HEADER = """<div class="rf-hero"><div><div class="rf-eyebrow">AN INTERACTIVE HARDWARE + OBSERVABILITY LAB</div>
<h1>Redfish Observatory<span style="color:#56e0df">.</span></h1>
<p>Operate a server. Watch the hardware. Follow every signal from the management controller to OpenTelemetry.</p>
<div class="rf-badges"><span class="rf-pill"><span class="rf-dot"></span>Simulated hardware</span>
<span class="rf-pill">Real Redfish-shaped HTTP</span><span class="rf-pill">Real OpenTelemetry SDK</span>
<span class="rf-pill">10 management capabilities</span><span class="rf-pill">100 Python use cases</span></div></div>
<div class="rf-logo"><svg width="44" height="44" viewBox="0 0 44 44" aria-hidden="true">
<rect x="7" y="5" width="30" height="34" rx="5" fill="none" stroke="#56e0df" stroke-width="1.5"/>
<path d="M12 14h20M12 23h20M12 32h20" stroke="#56e0df" stroke-width="1.5"/>
<circle cx="15" cy="10" r="1.5" fill="#ffca80"/><circle cx="15" cy="19" r="1.5" fill="#56e0df"/>
<circle cx="15" cy="28" r="1.5" fill="#b99aff"/></svg></div></div>"""


def _fan(x, y, stopped=False):
    cls = "rf-fan rf-stopped" if stopped else "rf-fan"
    return f'''<g transform="translate({x} {y})"><circle r="21" fill="#0c1929" stroke="#34556a"/>
    <g class="{cls}"><path d="M0-3C-19-17-16-24-5-16L2-3C19-17 24-12 14-3L3 2C17 19 12 24 3 14L-2 3C-19 17-24 12-14 3Z" fill="{"#a15768" if stopped else "#56e0df"}" opacity=".75"/></g>
    <circle r="4" fill="#192f43" stroke="#5abebf"/></g>'''


def rack_svg(data):
    off = data["power_state"] == "Off"
    fan_stopped = off or data["fault"] == "Fan failure"
    color = "#ff8194" if data["health"] == "Critical" else "#56e0df"
    host = "HOST OFF" if off else "OS UNAVAILABLE" if not data["os_running"] else "HOST RUNNING"
    return f'''<svg class="rf-rack-svg" viewBox="0 0 650 310" role="img" aria-label="Illustration of a physical server with independent BMC, fans, CPU, memory and disks">
    <defs><linearGradient id="rf-case" x2="0" y2="1"><stop stop-color="#263950"/><stop offset="1" stop-color="#142235"/></linearGradient></defs>
    <path d="M40 282L342 282 452 234 151 234Z" fill="#06101a" opacity=".8"/>
    <rect x="35" y="41" width="385" height="230" rx="16" fill="url(#rf-case)" stroke="#3d546e"/>
    <rect x="49" y="55" width="357" height="29" rx="5" fill="#0b1828" stroke="#2b4057"/>
    <circle cx="66" cy="69" r="4" fill="{color}" class="rf-pulse"/>
    <text x="82" y="73" class="rf-svg-label" fill="#dceaff">ATLAS R42  /  UNIT 12  /  SIM-R42-0001</text>
    <rect x="50" y="95" width="80" height="130" rx="7" fill="#0e1b2a" stroke="#2e455d"/>
    {_fan(90, 127, fan_stopped)}{_fan(90, 183, off)}
    <text x="67" y="218" class="rf-svg-label">COOLING</text>
    <rect x="145" y="95" width="108" height="83" rx="8" fill="#1a2c42" stroke="{color}"/>
    <path d="M156 106H241M156 117H241M156 128H241M156 139H241" stroke="#38506c"/>
    <rect x="165" y="110" width="67" height="47" rx="5" fill="#102135" stroke="#4d6983"/>
    <text x="180" y="135" fill="{color}" font-family="system-ui" font-size="14" font-weight="600">CPU</text>
    <text x="163" y="169" class="rf-svg-label">{data["temperature"]:.1f} °C</text>
    <rect x="270" y="100" width="10" height="77" rx="2" fill="#357784"/>
    <rect x="286" y="100" width="10" height="77" rx="2" fill="#357784"/>
    <rect x="302" y="100" width="10" height="77" rx="2" fill="#357784"/>
    <text x="267" y="195" class="rf-svg-label">128 GiB RAM</text>
    <rect x="330" y="103" width="62" height="45" rx="5" fill="#182d44" stroke="#415975"/>
    <rect x="330" y="157" width="62" height="45" rx="5" fill="#182d44" stroke="#415975"/>
    <text x="344" y="129" class="rf-svg-label">SSD 1</text><text x="344" y="183" class="rf-svg-label">SSD 2</text>
    <circle cx="384" cy="140" r="3" fill="{"#ff8194" if data["fault"] == "Disk failure" else "#56e0df"}"/>
    <rect x="145" y="194" width="108" height="33" rx="5" fill="#0e1b2a" stroke="#425670"/>
    <text x="159" y="215" class="rf-svg-label">{data["power_watts"]:.0f} W · PSU</text>
    <rect x="51" y="237" width="195" height="21" rx="5" fill="#122c37"/>
    <text x="63" y="251" font-size="9" fill="{"#ff8194" if not data["os_running"] else "#8fc3d0"}" font-family="monospace">{host}</text>
    <rect x="320" y="225" width="80" height="32" rx="5" fill="#17413e" stroke="#56e0df"/>
    <text x="336" y="245" fill="#9cf6e9" font-size="12" font-family="monospace">BMC ●</text>
    <path d="M401 241H443V125H492" fill="none" stroke="#56e0df" stroke-width="2" class="rf-wire"/>
    <rect x="495" y="90" width="131" height="74" rx="11" fill="#152b3c" stroke="#367f88"/>
    <text x="517" y="116" fill="#bdfaf1" font-size="14" font-family="system-ui">Redfish API</text>
    <text x="513" y="137" class="rf-svg-label">BMC stays online</text>
    <text x="468" y="202" class="rf-svg-label">SEPARATE MANAGEMENT</text>
    <text x="482" y="218" class="rf-svg-label">PATH + STANDBY POWER</text></svg>'''


def chart(title, subtitle, points, color, low, high, unit, chart_id):
    width, height = 510, 135
    now = time.time()
    rows = [
        (max(0, min(1, (ts - (now - 85)) / 85)), max(low, min(high, value)))
        for ts, value in points
        if ts >= now - 85
    ]
    xy = [(34 + t * (width - 46), 12 + (high - value) / (high - low) * 92) for t, value in rows]
    path = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(xy))
    grid = "".join(
        f'<path d="M34 {y}H498" stroke="#23374e" stroke-dasharray="3 5"/>' for y in [12, 58, 104]
    )
    fill = (
        f'<path d="{path} L{xy[-1][0]:.1f},104 L{xy[0][0]:.1f},104Z" fill="url(#{chart_id})"/>'
        if len(xy) > 1
        else ""
    )
    end = f'<circle cx="{xy[-1][0]:.1f}" cy="{xy[-1][1]:.1f}" r="3" fill="{color}"/>' if xy else ""
    empty = (
        '<text x="150" y="62" class="rf-svg-label">Collecting the first samples…</text>'
        if not xy
        else ""
    )
    return f'''<div class="rf-chart"><h3>{e(title)}</h3><p>{e(subtitle)}</p>
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="{e(title)} history">
    <defs><linearGradient id="{chart_id}" x2="0" y2="1"><stop stop-color="{color}" stop-opacity=".24"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
    {grid}{fill}<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5"/>{end}{empty}
    <text x="0" y="16" class="rf-svg-label">{high:g}</text><text x="0" y="108" class="rf-svg-label">{low:g}</text>
    <text x="35" y="128" class="rf-svg-label">85 seconds ago</text><text x="443" y="128" class="rf-svg-label">now · {e(unit)}</text></svg></div>'''


def dashboard(session, motion=True):
    data = session.model.snapshot()
    tb = session.bridge.buffer.snapshot()
    temp = session.bridge.latest_hardware.get("temperature")
    duration = session.last_workload.get("duration_ms", 0)
    status = session.last_workload.get("status", "waiting")
    alert = temp is not None and temp >= 75 and duration > 200
    incident = (
        "Lab alert: collected temperature ≥ 75 °C AND checkout duration > 200 ms. Investigate the simulated cooling failure."
        if alert
        else "Watch the relationship: cooling → temperature → application duration. The demo rule triggers when collected temperature ≥ 75 °C and checkout duration > 200 ms."
    )
    cards = [
        (
            "CPU temperature",
            f"{data['temperature']:.1f}",
            "°C",
            "Live simulated sensor · 1 s refresh",
        ),
        ("Cooling fan 1", f"{data['fan_rpm']:,}", "RPM", "Zero RPM after Fan failure or power off"),
        ("Server power", f"{data['power_watts']:.0f}", "W", f"Power cap: {data['power_limit']} W"),
        (
            "Checkout duration",
            f"{duration:.0f}" if status == "ok" else "—",
            "ms",
            "Measured HTTP workload" if status == "ok" else f"Application: {status}",
        ),
    ]
    card_html = "".join(
        f'<div class="rf-card"><div class="rf-card-label">{a}</div><div class="rf-value">{b} <small>{c}</small></div><div class="rf-card-caption">{d}</div></div>'
        for a, b, c, d in cards
    )
    root_spans = [
        (row["time"], row["duration_ms"]) for row in tb["durations"] if row["status"] == 200
    ]
    charts = chart(
        "Collected hardware temperature",
        "Updates when a poll or pushed report reaches the adapter",
        [(row["time"], row["temperature"]) for row in tb["history"] if "temperature" in row],
        "#56e0df",
        20,
        110,
        "°C",
        "rf-temp",
    )
    charts += chart(
        "Application request duration",
        "Actual instrumented checkout endpoint · one request per cycle",
        root_spans,
        "#b99aff",
        0,
        550,
        "ms",
        "rf-latency",
    )
    return f'''<div class="{"rf-paused" if not motion else ""}"><div class="rf-cards">{card_html}</div>
    <div class="rf-stage"><div class="rf-stage-head"><h2>Your simulated rack</h2><span>RACK 07 / UNIT 12</span></div>
    <div class="rf-rack-grid">{rack_svg(data)}<div class="rf-facts"><div class="rf-eyebrow">ONE HOST. INDEPENDENT MANAGEMENT.</div>
    <h3>{e(data["host"])}</h3><p>The main computer runs the application. The BMC checks and controls its hardware using a separate management path.</p>
    <div class="rf-fact"><span>Hardware health</span><strong style="color:{"#ff8194" if data["health"] != "OK" else "#56e0df"}">{e(data["health"])}</strong></div>
    <div class="rf-fact"><span>Scenario</span><strong>{e(data["fault"])}</strong></div>
    <div class="rf-fact"><span>Host / BMC power</span><strong>{e(data["power_state"])} / On</strong></div>
    <div class="rf-fact"><span>Application</span><strong>{"Running" if data["os_running"] else "Unavailable"}</strong></div></div></div></div>
    <div class="rf-incident {"alert" if alert else ""}">{incident}</div><div class="rf-charts">{charts}</div></div>'''


def flow(session, motion=True):
    bridge = session.bridge
    data = bridge.buffer.snapshot()
    endpoint = (
        "External OTLP configured"
        if bridge.otlp_endpoint
        else "Optional external stack · not connected"
    )
    # The moving dashes illustrate direction, not delivery acknowledgements.
    nodes = [
        (18, 55, 145, "Server + BMC", "simulated sensors", "#56e0df"),
        (190, 55, 145, "Redfish HTTP", session.mode, "#56e0df"),
        (362, 55, 145, "Python adapter", "JSON → OTel signals", "#56e0df"),
        (534, 55, 145, "OTel SDK", "real SDK exporters", "#b99aff"),
        (733, 55, 200, "Local signal viewer", "bounded in-memory export", "#ffca80"),
        (534, 205, 145, "Collector", "optional OTLP routing", "#566b87"),
        (733, 205, 200, "Grafana + LGTM", "optional storage / dashboards", "#566b87"),
    ]
    node_html = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="65" rx="10" fill="#122237" stroke="{color}"/><text x="{x + 13}" y="{y + 27}" class="rf-flow-label">{e(label)}</text><text x="{x + 13}" y="{y + 46}" class="rf-flow-small">{e(sub)}</text>'
        for x, y, w, label, sub, color in nodes
    )
    age = f"{time.time() - bridge.acquired_at:.1f} s" if bridge.acquired_at else "waiting"
    counts = data["counts"]
    return f'''<div class="rf-flow {"rf-paused" if not motion else ""}"><div class="rf-stage-head" style="padding:0 0 14px"><h2>Follow the signal</h2><span>ANIMATION SHOWS DIRECTION</span></div>
    <svg viewBox="0 0 955 300" role="img" aria-label="Redfish readings flow through a Python adapter to the real OpenTelemetry SDK and local viewer, with an optional external Collector and backend">
    <path d="M163 88H190M335 88H362M507 88H534M679 88H733" stroke="#56e0df" fill="none" stroke-width="2" class="rf-wire"/>
    <path d="M292 172H466V132H591V120" stroke="#b99aff" fill="none" stroke-width="2" class="rf-wire"/>
    <text x="40" y="168" class="rf-flow-label">Application + host context</text><text x="40" y="186" class="rf-flow-small">synthetic workload · real traces + metrics</text>
    <path d="M607 120V205M679 237H733" stroke="{"#b99aff" if bridge.otlp_endpoint else "#465c75"}" fill="none" stroke-dasharray="4 8" stroke-width="1.6"/>
    {node_html}<text x="536" y="292" class="rf-flow-small">{e(endpoint)}</text></svg>
    <div class="rf-flow-legend"><b style="color:#56e0df">● Metrics {counts["metrics"]}</b><b style="color:#ffca80">● Logs {counts["logs"]}</b><b style="color:#b99aff">● Spans {counts["spans"]}</b>
    <span>Hardware polls {bridge.polls} · pushed payloads {bridge.pushes} · acquired {age} ago</span></div>
    <div class="rf-section-note">Last hardware path: {e(bridge.last_transport)} · Local export every 1 s · External export, when configured, uses batching.<br>
    Freshness includes sensor sampling, report/poll interval, transport and export. No hard real-time delivery guarantee.</div></div>'''


def signals(session):
    data = session.bridge.buffer.snapshot()
    metrics = [m for m in data["metrics"] if m["name"].startswith("lab.hardware")][-4:]
    m_html = "".join(
        f'<div class="rf-signal-entry"><strong>{e(m["name"])}</strong><br><span style="color:#56e0df">{e(m["value"])} {e(m["unit"])}</span><small>{e(m["timestamp"][11:23])} UTC · {e(m["attributes"].get("sensor", ""))}</small></div>'
        for m in reversed(metrics)
    )
    l_html = "".join(
        f'<div class="rf-signal-entry"><strong style="color:#ffca80">{e(log["severity"])}</strong> · {e(log["body"])}<small>{e(log["timestamp"][11:23])} UTC · {e(log["attributes"].get("redfish.transport", "application"))}</small></div>'
        for log in reversed(data["logs"][-5:])
    )
    s_html = "".join(
        f'<div class="rf-signal-entry"><strong>{e(s["name"])}</strong> · {s["duration_ms"]:.1f} ms<small>trace {s["trace_id"][:12]}… · {"child" if s["parent_id"] else "root"}</small><div class="rf-span-bar" style="width:{max(3, min(100, s["duration_ms"] / 5)):.1f}%"></div></div>'
        for s in reversed(data["spans"][-6:])
    )
    return f"""<div class="rf-signal-grid"><div class="rf-signal"><h3>Metrics / measurements</h3>{m_html or "Waiting for SDK export…"}</div>
    <div class="rf-signal"><h3>Logs / what happened</h3>{l_html or "Waiting for an event…"}</div>
    <div class="rf-signal"><h3>Traces / request journeys</h3>{s_html or "Waiting for a checkout request…"}</div></div>
    <div class="rf-incident">Correlation key: <strong>host.name = server-42</strong> + <strong>lab.physical_server.id = SIM-R42-0001</strong> + time.
    The application supplies trace context. Hardware events are linked by server and time, not an invented request trace ID.</div>"""


def lesson_html(choice, motion=True):
    lesson = LESSONS[choice]
    return f"""<div class="rf-lesson {"rf-paused" if not motion else ""}"><div class="rf-eyebrow">MANAGEMENT STUDIO / {e(choice[:2])}</div>
    <h2>{e(lesson.title)}</h2><p style="color:#e2edff">{e(lesson.meaning)}</p>
    <div class="rf-operation-flow"><span class="rf-mini-node">Python client</span><span class="rf-mini-arrow">→</span><span class="rf-mini-node">Redfish / BMC</span><span class="rf-mini-arrow">→</span><span class="rf-mini-node">Hardware / settings</span></div>
    <div class="rf-code"><span class="rf-verb">{lesson.verb}</span>{e(lesson.path)}</div><p>{e(lesson.explanation)}</p>
    <div class="rf-next">Try it: {e(lesson.next_step)}</div></div>"""


def management_state(session):
    data = session.model.snapshot()
    tasks = "".join(
        f'<div class="rf-task">{e(t["Name"])} · {e(t["TaskState"])} · {t["PercentComplete"]}%<div class="rf-task-bar"><span style="width:{t["PercentComplete"]}%"></span></div></div>'
        for t in data["tasks"][-3:]
    )
    return f"""<div class="rf-state"><h3>Resulting server state</h3>
    <div class="rf-fact"><span>Firmware</span><strong>{e(data["firmware"])}</strong></div>
    <div class="rf-fact"><span>Virtualization active / pending</span><strong>{e(data["bios"]["ProcVirtualization"])} / {e(data["pending_bios"].get("ProcVirtualization", "—"))}</strong></div>
    <div class="rf-fact"><span>Boot / attached image</span><strong>{e(data["boot_target"])} / {"Attached" if data["media"] else "None"}</strong></div>
    <div class="rf-fact"><span>Installed demo OS</span><strong>{e(data["installed_os"])}</strong></div>
    <div class="rf-fact"><span>Volumes / accounts / callbacks</span><strong>{len(data["volumes"])} / {len(data["accounts"])} / {data["subscriptions"]}</strong></div>
    {tasks}</div>"""


def tour_html():
    icons = ["◉", "✣", "⇢", "◷", "⌘", "◇"]
    return (
        '<div class="rf-guide-grid">'
        + "".join(
            f'<div class="rf-guide-card"><div class="rf-eyebrow">{e(title)}</div><div class="rf-guide-icon">{icon}</div><h3>{e(meaning)}</h3><p>{e(instruction)}</p></div>'
            for (title, meaning, instruction), icon in zip(TOUR, icons)
        )
        + "</div>"
    )
