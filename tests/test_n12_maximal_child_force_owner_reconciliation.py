import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/reconcile_n12_maximal_child_force_owner.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_MAXIMAL_CHILD_FORCE_OWNER_RECONCILIATION.json"
)


def test_n12_maximal_child_force_owner_reconciliation() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["closed_dependencies"][
        "gauge_ghost_rank16_HS_source_incidence"
    ] == "ASSEMBLED"
    assert payload["closed_dependencies"][
        "explicit_hybrid_time_generator_for_first_force_root"
    ] == "NOT_REQUIRED_BY_INTRINSIC_QUOTIENT_THEOREM"
    assert payload["single_open_input"]["available"] is False
    assert payload["single_open_input"]["action_owned"] is True
    assert payload["claim_boundary"][
        "maximal_history_coefficient_oracle_and_first_jet"
    ] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
