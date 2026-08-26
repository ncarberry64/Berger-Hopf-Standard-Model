from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_two_seam_closed_operator_assembly.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_two_seam_closed_operator_assembly() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "TWO_SEAM_CLOSED_OPERATOR_TOPOLOGY_AND_SCHUR_EQUIVALENCE_DERIVED"
    )
    witness = payload["exact_witness"]
    assert witness["direct_determinant"] == "44"
    assert witness["Schur_determinant"] == "44"
    assert witness["determinant_residual"] == "0"
    assert witness["first_variation_residual"] == "0"
    assert payload["closed_operator"]["zero_source_effect"].endswith(
        "RETAIN_BOTH_ROWS_AND_COLUMNS"
    )
    assert payload["adjudication"]["complete_internal_operator_topology"] == "CLOSED"
    assert payload["matching_audit"]["E0_event_side_M_E0_and_first_jet"] == (
        "ACTUALLY_MISSING"
    )
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_two_seam_closed_operator_assembly_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
