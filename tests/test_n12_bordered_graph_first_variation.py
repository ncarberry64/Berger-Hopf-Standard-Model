import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_bordered_graph_first_variation.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_BORDERED_GRAPH_FIRST_VARIATION.json"
)


def _arb_leading_float(value: str) -> float:
    return float(value.lstrip("[").split()[0])


def test_n12_bordered_graph_first_variation() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["descriptor_dimension"] == 74
    assert payload["local_action_third_variation"][
        "nonzero_symmetric_terms"
    ] == 60
    bound = payload["structured_repeated_solve_bound"]
    assert bound["explicit_inverse_formed"] is False
    assert bound["dominant_direction"]["label"] == "dot_q0"
    assert 2.36e17 < _arb_leading_float(
        bound["stack_frobenius_upper"]
    ) < 2.38e17
    radius = _arb_leading_float(
        payload["linear_relative_defect"][
            "half_contraction_radius_lower"
        ]
    )
    assert 2.10e-18 < radius < 2.12e-18
    assert payload["linear_relative_defect"][
        "full_nonlinear_theta_below_one_certified"
    ] is False
    assert payload["claim_boundary"]["uniform_D4_graph_remainder"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
