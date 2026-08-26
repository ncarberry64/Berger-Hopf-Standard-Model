from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_external_birth_source_role_supersession.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_external_birth_source_role_supersession() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "EXTERNAL_BIRTH_TRACE_DIRICHLET_REFERENCE_REAFFIRMED_E0_ARM_REMOVED"
    )
    assert payload["adjudication"]["M_f_equals_M11_at_zero_external_birth_trace"] == (
        "REAFFIRMED"
    )
    assert payload["adjudication"]["M_E0_required"] is False
    assert payload["matching_audit"]["incoming_M_f"] == (
        "VALID_MATCH_NONZERO_INTERNAL_M11_RESPONSE"
    )
    assert payload["exact_witness"]["S_AE2"] == "11"
    assert payload["exact_witness"]["D_logdet_S_AE2"] == "7/11"
    assert payload["claim_boundary"]["M_E0_dependency_removed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_external_birth_source_role_supersession_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
