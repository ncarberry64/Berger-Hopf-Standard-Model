from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def audit() -> dict:
    status = _json("docs/current_bhsm_status.json")
    completion = _json("theory/full_bhsm_completion_results.json")
    checks = {
        "canonical_public_status": status["canonical_public_status"] is True,
        "gate_7_open": status["gate_7"]["status"] == "OPEN",
        "unchanged_ae2_localization_carrier_open": status[
            "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND"
        ]
        is False,
        "physical_encapsulation_open": status[
            "PHYSICAL_ENCAPSULATION_IDENTIFIED"
        ]
        is False,
        "full_bhsm_not_complete": status["FULL_BHSM_COMPLETE"] is False,
        "observable_machinery_promotion_gated": status[
            "observable_machinery_classification"
        ]
        == "IMPLEMENTED_BUT_PHYSICAL_PROMOTION_GATED",
        "frozen_predictions_unchanged": status["frozen_predictions_changed"] is False,
        "official_predictions_unchanged": status["official_predictions_changed"] is False,
        "completion_payload_candidate_only": completion["status"] == "candidate_only",
        "completion_payload_not_proven": completion["full_bhsm_proven"] is False,
    }
    return {
        "audit": "bhsm_status",
        "passed": all(checks.values()),
        "checks": checks,
        "verdict_labels": [
            "BHSM_CANONICAL_PUBLIC_STATUS_SYNCHRONIZED",
            "GATE7_REMAINS_OPEN",
            "PHYSICAL_ENCAPSULATION_REMAINS_OPEN",
            "FULL_BHSM_COMPLETE_FALSE",
        ],
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
