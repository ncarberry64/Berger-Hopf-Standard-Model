import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_intrinsic_time_quotient_force_root.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
)


def test_n12_intrinsic_time_quotient_force_root() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["dimensions"] == {
        "exact_time_orbit": 1,
        "physical_quotient_tangent": 66,
        "raw_regular_constraint_tangent": 67,
    }
    assert payload["scope"][
        "explicit_time_generator_needed_for_first_force_root"
    ] is False
    assert payload["scope"]["actual_q_rep_evaluated"] is False
    assert payload["scope"]["common_scale_quotiented"] is False
    assert payload["claim_boundary"][
        "force_root_time_quotient_equivalence"
    ] == "DERIVED"
    assert payload["claim_boundary"]["actual_maximal_child_oracle"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
