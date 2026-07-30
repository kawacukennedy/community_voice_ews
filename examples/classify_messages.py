#!/usr/bin/env python3
"""Example: Classify messages and see NLP results."""

import requests
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

messages = [
    # English
    "flood",
    "heavy rain water entering my house",
    "drought crops are dying no rain",
    "locust swarm in the farm",
    "people sick with cholera outbreak",
    "fire burning the forest",
    "conflict violence in the village",
    # Swahili
    "mafuriko maji nyumbani",
    "ukame mifugo kufa hakuna mvua",
    "nzige wadudu shambani",
    "homa malaria ugonjwa",
]

for msg in messages:
    resp = requests.post(f"{BASE}/api/classify", params={"text": msg})
    data = resp.json()
    print(f"  {msg:45s} -> {data['report_type']:10s} ({data['severity']:8s}) confidence={data['confidence']:.2f}")
