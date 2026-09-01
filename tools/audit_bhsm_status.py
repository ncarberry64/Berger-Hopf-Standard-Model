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
        "candidate_architecture_complete": status["candidate_architecture_complete"] is True,
        "full_bhsm_not_proven": status["full_bhsm_proven"] is False,
        "standard_model_not_fully_derived": status["standard_model_fully_derived"] is False,
        "mass_numerical_closure_open": status["mass_numerical_closure"] is False,
        "dark_matter_not_solved": status["dark_matter_solved"] is False,
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
            "BHSM_REPO_STATUS_REFRESH_COMPLETE",
            "FULL_BHSM_STATUS_SYNCHRONIZED",
            "SM_DERIVATION_REMAINS_OPEN",
            "MASS_NUMERICAL_CLOSURE_REMAINS_OPEN",
        ],
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
