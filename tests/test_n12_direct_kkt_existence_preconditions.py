from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_direct_kkt_existence_preconditions.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_heat_regulator_is_not_a_coercive_exhaustion() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    theorem = payload["exact_heat_regulator_theorem"]
    assert theorem["ultraviolet_limit"] == "lim_lambda_to_infinity_f(lambda)=0_from_below"
    assert payload["adjudication"]["heat_regulator_alone_closes_direct_method"] is False


def test_local_principal_inf_sup_is_not_global_kkt_compactness() -> None:
    payload = _payload()
    assert payload["validation"][
        "principal_certificate_is_not_continuum_KKT_compactness"
    ] is True
    assert payload["adjudication"][
        "local_principal_coercivity_closes_global_KKT_existence"
    ] is False


def test_direct_route_remains_open_without_action_incompatibility() -> None:
    payload = _payload()
    adjudication = payload["adjudication"]
    assert adjudication["direct_existence_route_invalid_in_principle"] is False
    assert adjudication["validated_finite_endpoint_BVP_route_remains_distinct"] is True
    assert adjudication["retained_action_incompatibility_proved"] is False
    assert adjudication["new_action_term_justified"] is False
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE_KKT_ROOT_EXISTENCE_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False
