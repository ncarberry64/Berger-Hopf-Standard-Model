from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_AE2_CHILD_BOUNDARY_HAMILTONIAN_NON_SUPERSESSION.json"
)
SCRIPT = ROOT / "scripts" / (
    "audit_n12_ae2_child_boundary_hamiltonian_non_supersession.py"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_ae2_does_not_supersede_child_boundary_hamiltonian_gate() -> None:
    data = _load()
    assert data["validation_passed"] is True
    assert data["action_version"] == "BHSM-AE-2.0.0"
    assert data["non_supersession_consequences"]["fermion_self_adjoint_domain"] == (
        "CLOSED_BY_AE2"
    )
    assert data["non_supersession_consequences"]["child_boundary_H_xi"] == (
        "NOT_ACTION_EXECUTABLE"
    )
    assert data["source_ontology"]["external_Cauchy_birth_source"] == 0
    assert data["source_ontology"]["internal_responses_zeroed"] is False
    assert data["claim_boundary"]["rank72_joint_heat_minus_zeta_tail"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert data["FULL_BHSM_COMPLETE"] is False


def test_non_supersession_materialization_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert first == second
