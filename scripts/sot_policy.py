#!/usr/bin/env python3

import json
from pathlib import Path

POLICY_PATH = Path("/Users/hafsahnuzhat/Desktop/🦀/config/bella-sot-policy.json")


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def save_policy(policy: dict) -> None:
    POLICY_PATH.write_text(json.dumps(policy, indent=2) + "\n")


def get_sheet_id(policy: dict, role: str) -> str:
    return policy.get("source_of_truth", {}).get(role, "")

