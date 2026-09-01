from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_NHIM_RANK72_RELATIVE_TAIL_THEOREM.json"
)
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_nhim_rank72_relative_tail_theorem.py"


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_captured_nhim_rank72_relative_tail_is_cauchy() -> None:
    data = _load()
    assert data["validation_passed"] is True
    assert data["rank72_consequence"]["captured_family_rank72_relative_form_net"] == (
        "CAUCHY"
    )
    assert data["rank72_consequence"]["absolute_infinite_volume_heat_trace_required"] is False
    assert data["supersession"]["prior_absolute_NHIM_no_go"] == "PRESERVED"
    assert data["claim_boundary"]["AE2_reset_image_enters_capture_basin"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert data["source_ontology"]["external_Cauchy_birth_source"] == 0
    assert data["source_ontology"]["internal_responses_zeroed"] is False
    assert data["FULL_BHSM_COMPLETE"] is False


def test_captured_nhim_relative_tail_materialization_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert first == second
