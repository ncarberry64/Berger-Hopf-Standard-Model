from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import full_architecture_freeze_status as freeze


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)

    write_json(artifacts / "full_BHSM_architecture_freeze_v1.json", freeze.architecture_freeze_artifact())

    open_gate_path = artifacts / "full_BHSM_open_gate_ledger_v2.json"
    open_gate = json.loads(open_gate_path.read_text(encoding="utf-8"))
    open_gate["statuses"].update(freeze.open_gate_ledger_updates())
    open_gate["remaining_open_blockers"] = list(freeze.REMAINING_OPEN_BLOCKERS)
    write_json(open_gate_path, open_gate)

    claim_path = artifacts / "full_BHSM_claim_status_table_v2.json"
    claims = json.loads(claim_path.read_text(encoding="utf-8"))
    existing = {row["claim"] for row in claims["claim_statuses"]}
    for row in freeze.claim_status_rows():
        if row["claim"] not in existing:
            claims["claim_statuses"].append(row)
    write_json(claim_path, claims)

    forbidden_path = artifacts / "forbidden_claim_audit_v2.json"
    forbidden = json.loads(forbidden_path.read_text(encoding="utf-8"))
    forbidden["forbidden_claims"] = list(freeze.FORBIDDEN_CLAIMS)
    forbidden["allowed_strongest_claim"] = freeze.ALLOWED_STRONGEST_CLAIM
    write_json(forbidden_path, forbidden)


if __name__ == "__main__":
    main()
