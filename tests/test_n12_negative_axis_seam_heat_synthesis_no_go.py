from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from scripts.certify_n12_negative_axis_seam_heat_synthesis_no_go import (
    build_payload,
    scalar_family_membership_witness,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_negative_axis_seam_heat_synthesis_no_go.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json"
)


def test_whole_axis_scalar_ordering_contains_both_far_loads() -> None:
    witness = scalar_family_membership_witness()
    assert witness["all_kappa_positive"] is True
    assert witness["all_rows_ordered"] is True


def test_enclosed_force_families_have_opposite_signs() -> None:
    payload = build_payload()
    pair = payload["certified_force_counterpair"]
    assert pair["Neumann_far_load"]["strict_sign"] == "POSITIVE"
    assert pair["Dirichlet_far_load"]["strict_sign"] == "NEGATIVE"
    assert payload["claim_boundary"]["actual_projected_force"] == "OPEN"
    assert payload["validation_passed"] is True


def test_artifact_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
    assert json.loads(TARGET.read_text(encoding="utf-8"))["validation_passed"] is True
