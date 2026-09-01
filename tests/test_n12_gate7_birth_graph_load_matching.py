from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_birth_graph_load_matching.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_birth_graph_load_matching() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "AE2_BIRTH_GRAPH_TYPE_CLOSED_EVENT_SIDE_LOAD_AND_JET_OPEN"
    )
    assert payload["exact_birth_load"]["load"] == (
        "B_birth=U_R0*(M_E0+W_E0)*U_R0^dagger"
    )
    assert payload["matching_audit"]["M_E0_nonzero_event_side_Calderon_family"] == (
        "ACTUALLY_MISSING"
    )
    assert payload["adjudication"]["natural_B_birth_zero_specialization_authorized"] is False
    assert payload["adjudication"]["additional_external_source_or_seam_force_required"] is False
    assert payload["claim_boundary"]["B_birth_realized"] is False
    assert payload["claim_boundary"]["physical_M_f_realized"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_birth_graph_load_matching_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
