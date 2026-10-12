"""End-to-end Docker smoke check: actual SDK → Collector → all three backends.

Run after `docker compose up --build -d`. This script is separate from pytest.
"""

import time

import httpx


def main():
    deadline = time.monotonic() + 240
    last_error = "Stack has not started"
    observed = set()
    seeded = False
    with httpx.Client(timeout=5, trust_env=False) as client:
        while time.monotonic() < deadline:
            try:
                client.get("http://127.0.0.1:7860/healthz").raise_for_status()
                if not seeded:
                    client.get("http://127.0.0.1:7860/redfish/v1/Systems/1").raise_for_status()
                    client.post(
                        "http://127.0.0.1:7860/lab/scenario",
                        json={"fault": "Fan failure", "load": 40},
                    ).raise_for_status()
                    seeded = True
                metrics = client.get(
                    "http://127.0.0.1:9090/api/v1/query",
                    params={
                        "query": '{__name__=~"lab_hardware_temperature.*",job="redfish-observatory"}'
                    },
                )
                metrics.raise_for_status()
                if metrics.json()["data"]["result"]:
                    observed.add("metrics")
                logs = client.get(
                    "http://127.0.0.1:3000/api/datasources/proxy/uid/loki/loki/api/v1/query_range",
                    params={"query": '{service_name="redfish-observatory"}', "limit": 10},
                )
                logs.raise_for_status()
                if logs.json()["data"]["result"]:
                    observed.add("logs")
                traces = client.get(
                    "http://127.0.0.1:3000/api/datasources/proxy/uid/tempo/api/search",
                    params={"q": '{ resource.service.name = "redfish-observatory" }', "limit": 10},
                )
                traces.raise_for_status()
                if traces.json().get("traces"):
                    observed.add("traces")
                dashboard = client.get(
                    "http://127.0.0.1:3000/api/dashboards/uid/redfish-observatory"
                )
                dashboard.raise_for_status()
                if dashboard.json()["dashboard"]["uid"] == "redfish-observatory":
                    observed.add("dashboard")
                if observed == {"metrics", "logs", "traces", "dashboard"}:
                    print(
                        "PASS: OTLP metrics in Prometheus, logs in Loki, traces in Tempo, Grafana dashboard provisioned"
                    )
                    return
                last_error = f"Still waiting for {sorted({'metrics', 'logs', 'traces', 'dashboard'} - observed)}"
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                last_error = str(exc)
            time.sleep(3)
    raise SystemExit(f"Stack smoke check failed: {last_error}; observed={sorted(observed)}")


if __name__ == "__main__":
    main()
