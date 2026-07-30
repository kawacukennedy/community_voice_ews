#!/usr/bin/env python3
"""Example: Submit reports via the API and view results."""

import requests
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


def report(message, lat=-1.315, lng=36.785, location="Nairobi"):
    resp = requests.post(f"{BASE}/api/reports", json={
        "message": message,
        "latitude": lat,
        "longitude": lng,
        "location_name": location,
        "source": "demo",
    })
    print(f"POST /api/reports -> {resp.status_code}")
    data = resp.json()
    print(f"  ID: {data['id']}")
    print(f"  Type: {data['report_type']} ({data['severity']})")
    print(f"  Confidence: {data['confidence']:.2f}")
    print()
    return data


def health():
    resp = requests.get(f"{BASE}/api/health")
    print(f"GET /api/health -> {resp.status_code}")
    print(f"  {resp.json()}")
    print()


def stats():
    resp = requests.get(f"{BASE}/api/stats")
    print(f"GET /api/stats -> {resp.status_code}")
    print(f"  {resp.json()}")
    print()


if __name__ == "__main__":
    health()

    report("Heavy flooding in the village near the river, water entering homes",
           lat=-1.315, lng=36.785, location="Nairobi River Basin")

    report("No rain for months, crops failing, livestock dying from thirst",
           lat=0.347, lng=32.582, location="Kampala Region")

    report("Desert locust swarm spotted moving east across farms",
           lat=2.046, lng=45.318, location="Mogadishu Area")

    stats()
