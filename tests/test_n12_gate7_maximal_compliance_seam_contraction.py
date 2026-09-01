from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_maximal_compliance_seam_contraction.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_MAXIMAL_COMPLIANCE_SEAM_CONTRACTION.json"
)


def test_maximal_compliance_seam_contraction() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "MAXIMAL_CHILD_LOAD_CANNOT_AMPLIFY_FIXED_TERMINAL_INCOMING_COMPLIANCE_COTANGENT"
    )
    witness = payload["algebra_witness"]
    assert 0.0 < witness["contraction_factor"] <= 1.0
    assert witness["finite_difference_residual"] < 1.0e-9
    assert payload["theorem"]["maximal_child_jet_required_in_this_direction"] is False
    assert payload["adjudication"]["maximal_child_or_contact_response_zeroed"] is False
    assert payload["adjudication"][
        "finite_core_sign_transferred_to_maximal_heat_functional"
    ] is False
    assert payload["claim_boundary"]["maximal_full_graded_heat_cotangent"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
