import json
from decimal import Decimal
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_bordered_graph_uniform_nonlinear_defect.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_BORDERED_GRAPH_UNIFORM_NONLINEAR_DEFECT.json"
)


def test_n12_bordered_graph_uniform_nonlinear_defect() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    fourth = payload["exact_local_fourth_variation"]
    assert fourth["nonzero_symmetric_coefficients"] == 99
    assert fourth["nonzero_ordered_coefficients"] == 1416
    uniform = payload["uniform_relative_graph_bound"]
    radius = Decimal(uniform["certified_nonlinear_radius"])
    assert Decimal("1e-604") < radius < Decimal("1e-602")
    assert Decimal(uniform["total_theta_upper"]) <= Decimal("0.5")
    assert Decimal(uniform["strict_Neumann_margin_lower"]) >= Decimal("0.5")
    assert uniform["explicit_inverse_formed"] is False
    assert payload["claim_boundary"][
        "uniform_nonlinear_relative_graph_defect"
    ] == "CERTIFIED"
    assert payload["claim_boundary"][
        "lower_weight_inhomogeneous_remainder"
    ] == "ANALYTICALLY_ABSORBED_FOR_NONREALIZED_FORMATION_BRANCH"
    assert payload["claim_boundary"]["Gate7"] == (
        "ACTIVE_MAXIMAL_CHILD_CALDERON_WEYL_FORCE_ROOT"
    )
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
