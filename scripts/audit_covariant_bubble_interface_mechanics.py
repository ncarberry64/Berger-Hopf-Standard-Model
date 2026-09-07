"""Audit the covariant bubble/interface mechanics artifact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/action_extension/BHSM_COVARIANT_BUBBLE_INTERFACE_MECHANICS.json"


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def audit() -> dict[str, object]:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    checks = {
        "materializer_validation_passed": payload["validation_passed"] is True,
        "all_provenance_hashes_match": all(
            _sha(ROOT / relative) == expected
            for relative, expected in payload["inputs"].items()
        ),
        "single_open_object": len(payload["OPEN"]) == 1,
        "no_observed_alpha_input": payload["FSC"]["observed_alpha_EM_used"] is False,
        "no_fitted_interface_coefficient": payload["interface_stiffness"]["fitted_coefficient"] is None,
        "no_C_A_fluid_mechanics": "no pressure" in payload["domain"]["pregeometry"],
        "no_track1_interference": payload["N12"]["Gate7_result_imported"] is False,
        "no_completion_promotion": payload["FULL_BHSM_COMPLETE"] is False,
    }
    return {
        "audit": "covariant_bubble_interface_mechanics",
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> None:
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
