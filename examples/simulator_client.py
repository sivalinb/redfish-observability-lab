"""Discover the local simulator and print a real HTTP resource response."""

import httpx

with httpx.Client(base_url="http://127.0.0.1:7860", timeout=10) as client:
    root = client.get("/redfish/v1").raise_for_status().json()
    systems = client.get(root["Systems"]["@odata.id"]).raise_for_status().json()
    for link in systems["Members"]:
        system = client.get(link["@odata.id"]).raise_for_status().json()
        print(system["HostName"], system["PowerState"], system["MemorySummary"])
