from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_same_action_continuation_preconditions.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_continuation_cannot_start_from_synthetic_hessian() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["synthetic_Hessian_promoted"] is False
    assert payload["adjudication"]["local_implicit_function_theorem_applicable_now"] is False
    assert "NOT_D2_Gamma_TOTAL" in payload["nonpromotable_objects"][
        "synthetic_positive_tangent_Hessian"
    ]


def test_historical_constant_reset_hessian_is_not_current_curvature() -> None:
    payload = _payload()
    assert payload["claim_boundary"]["historical_constant_reset_Hessian_promoted"] is False
    assert "CONSTANT_RECONSTRUCTION_MAP" in payload["nonpromotable_objects"][
        "historical_v15_93_zero_reset_Hessian"
    ]


def test_route_is_open_not_disproved_and_direct_bvp_remains() -> None:
    payload = _payload()
    adjudication = payload["adjudication"]
    assert adjudication["continuation_route_invalid_in_principle"] is False
    assert adjudication["continuation_route_currently_blocked_by_same_oracle"] is True
    assert adjudication["validated_direct_BVP_route_remains_distinct"] is True
    assert adjudication["retained_action_incompatibility_proved"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
