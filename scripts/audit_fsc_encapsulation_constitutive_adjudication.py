"""Audit the checked-in FSC adjudication against its deterministic source."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.materialize_fsc_encapsulation_constitutive_adjudication import (  # noqa: E402
    TARGET,
    build_payload,
    deterministic_json,
)


def audit() -> dict[str, Any]:
    expected_payload = build_payload()
    expected_bytes = deterministic_json(expected_payload).encode("utf-8")
    actual_bytes = TARGET.read_bytes() if TARGET.is_file() else b""
    checks = {
        "artifact_exists": TARGET.is_file(),
        "artifact_matches_deterministic_materializer": actual_bytes == expected_bytes,
        "materializer_validation_passed": expected_payload["validation_passed"] is True,
        "classification_is_fail_closed": (
            expected_payload["classification"]["interface"] == "FSC-IF5"
            and expected_payload["classification"]["effective_map"] == "GEFF5"
            and expected_payload["classification"]["scale"] == "SCALE4"
        ),
        "no_rank_or_cycle_promotion": (
            expected_payload["adjudication"]["variation_rank_cycle"]["N12_rank_added"] == 0
            and expected_payload["adjudication"]["variation_rank_cycle"]["loop"] == "LOOP3"
            and expected_payload["adjudication"]["variation_rank_cycle"]["RSP"] == "RSP5"
        ),
        "no_frozen_prediction_change": not any(
            expected_payload["adjudication"]["frozen_cross_check"].values()
        ),
        "claim_firewall_clean": not any(
            expected_payload["adjudication"]["claim_firewall"].values()
        ),
    }
    return {
        "audit": "BHSM_FSC_ENCAPSULATION_CONSTITUTIVE_ADJUDICATION_AUDIT",
        "checks": checks,
        "passed": all(checks.values()),
        "artifact_sha256": hashlib.sha256(actual_bytes).hexdigest().upper() if actual_bytes else None,
    }


def main() -> None:
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit("FSC adjudication audit failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
