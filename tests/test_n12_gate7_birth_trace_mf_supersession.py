from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_birth_trace_mf_supersession.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_BIRTH_TRACE_MF_SUPERSESSION_AUDIT.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_birth_trace_mf_supersession() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["zero_source_Dirichlet_equivalence"] == "CLOSED_INVALID"
    assert payload["adjudication"]["M_f_equals_M11_as_physical_zero_source_response"] == "SUPERSEDED"
    assert payload["exact_reduction"]["physical_incoming_response"] == (
        "M_f_phys=M11-M10*X_birth"
    )
    witness = payload["deterministic_counterexample"]
    assert witness["stationarity_residual"] == "0"
    assert witness["physical_M_f"] == "19/5"
    assert witness["Dirichlet_M11"] == "4"
    assert witness["responses_are_distinct"] is True
    assert payload["matching_audit"]["physical_zero_source_incoming_M_f"].startswith(
        "ACTUALLY_MISSING"
    )
    assert payload["claim_boundary"]["physical_incoming_M_f_claimed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_birth_trace_mf_supersession_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
