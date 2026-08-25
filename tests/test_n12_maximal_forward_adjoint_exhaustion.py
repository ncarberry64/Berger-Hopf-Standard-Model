from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_maximal_forward_adjoint_exhaustion.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json"
)


def test_maximal_forward_adjoint_exhaustion() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    criterion = payload["criterion"]
    assert criterion["all_forward_Jacobi_columns_required"] is False
    assert criterion["explicit_noncompact_D_xi_M_required"] is False
    assert criterion["finite_endpoint_route_requires_infinite_bound"] is False
    assert payload["open_after_theorem"]["actual_N12_state_propagator_weight"] is True
    assert payload["claim_boundary"]["actual_weighted_load"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
