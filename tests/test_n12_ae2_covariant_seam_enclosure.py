from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_ae2_covariant_seam_enclosure.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_covariant_reset_frame_adds_no_independent_force_source() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["covariant_seam_reduction"]["global_connection_compatibility"] == (
        "NABLA_Phi_U_R=0"
    )
    assert payload["claim_boundary"]["reset_lift_independent_frame_source"] == (
        "ABSENT_COVARIANTLY"
    )
    assert payload["covariant_seam_reduction"][
        "relative_event_child_orientation_erased"
    ] is False


def test_existing_child_bounds_pull_back_to_fermion_event_load() -> None:
    payload = _payload()
    rows = payload["fermion_AE2_W_zero_load_enclosures"]
    assert len(rows) == 4
    for row in rows:
        assert row["event_effective_load_interval_AE2_W_zero"] == row[
            "child_Calderon_interval"
        ]
        assert row["covariant_first_load_jet_norm_upper"] >= 0.0
        assert row["covariant_mixed_load_jet_norm_upper"] >= 0.0
        assert row["reset_frame_derivative_separate_physical_source"] is False


def test_single_probe_is_not_promoted_to_complete_force_oracle() -> None:
    payload = _payload()
    assert payload["native_resolvent_probe"]["z"] == -1.0
    assert payload["native_resolvent_probe"]["role"] == (
        "RESOLVENT_PROBE_NOT_MOMENTUM_SQUARED"
    )
    assert payload["claim_boundary"]["complete_heat_spectral_family"] == "OPEN"
    assert payload["claim_boundary"]["zero_source_force_value"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
