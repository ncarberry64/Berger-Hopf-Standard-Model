from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_local_reset_terminal_transversality.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json"
)


def test_local_reset_terminal_transversality_audit() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["witness"]["raw_reset_tangent_dimension"] == 67
    assert payload["route_adjudication"][
        "local_reset_IFT_supplies_finite_stratum"
    ] is False
    assert payload["route_adjudication"][
        "global_reset_quotient_finite_stratum_disproved"
    ] is False
    assert payload["route_adjudication"]["favorable_reset_child_selected"] is False
    assert payload["route_adjudication"]["new_canonical_stop_declared"] is False
    assert payload["claim_boundary"][
        "local_reset_terminal_transversality_route"
    ] == "CLOSED_INSUFFICIENT"
    assert payload["claim_boundary"]["actual_finite_stratum"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
