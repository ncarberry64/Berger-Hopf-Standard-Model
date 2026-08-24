from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_event_normal_two_sided_seam.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_physical_ae2_seam_retains_opposite_arm_response() -> None:
    payload = _payload()
    theorem = payload["corrected_seam_theorem"]
    assert payload["validation_passed"] is True
    assert theorem["physical_seam_operator"] == (
        "S_AE2(z)=M_event(z)+U_R_DAGGER*M_child(z)*U_R+W_phys"
    )
    assert theorem["event_arm_effective_load_after_child_elimination"] == (
        "B_event(z)=U_R_DAGGER*M_child(z)*U_R+W_phys"
    )
    assert payload["finite_encapsulation_consequence"][
        "two_sided_event_child_seam_removed"
    ] is False


def test_w_only_initialization_is_explicitly_superseded() -> None:
    payload = _payload()
    assert payload["supersession"]["superseded_claim"] == (
        "M(0,z)=W_phys_AS_THE_PHYSICAL_AE2_EVENT_INITIAL_VALUE"
    )
    assert payload["claim_boundary"]["physical_AE2_event_initial_value"] == "OPEN"
    assert payload["witness"]["one_sided_W_only_omission_residual"] > 1.0e-3


def test_full_seam_geometry_jet_is_verified() -> None:
    payload = _payload()
    assert payload["witness"]["geometry_jet_finite_difference_residual"] < 1.0e-8
    assert payload["claim_boundary"]["zero_source_force_value"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
