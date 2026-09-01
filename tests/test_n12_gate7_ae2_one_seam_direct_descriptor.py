from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_ae2_one_seam_descriptor import (  # noqa: E402
    assemble_ae2_one_seam_descriptor,
)


SCRIPT = ROOT / "scripts" / "derive_n12_gate7_ae2_one_seam_direct_descriptor.py"
ARTIFACT = (
    ROOT
    / "artifacts"
    / "flagship_integration"
    / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
)


def _base(**updates):
    arguments = {
        "formation_log_radii": np.asarray((0.1, 0.05, 0.0)),
        "formation_proper_durations": np.asarray((0.2, 0.3)),
        "child_log_radii": np.asarray((0.0, -0.02, 0.03)),
        "child_proper_durations": np.asarray((0.4, 0.5)),
        "channel": "scalar",
        "unit_channel_value": 3.0,
        "seam_contact": 0.7,
    }
    arguments.update(updates)
    return assemble_ae2_one_seam_descriptor(**arguments)


def test_single_seam_dimension_and_contact_count() -> None:
    result = _base()
    assert result["dimension"] == 3
    assert result["seam_reduced_index"] == 1
    assert result["internal_seam_trace_count"] == 1
    without_contact = _base(seam_contact=0.0)
    difference = result["K"] - without_contact["K"]
    assert np.count_nonzero(difference) == 1
    assert difference[1, 1] == pytest.approx(0.7)
    assert result["explicit_matrix_inverse_formed"] is False


def test_reset_radius_must_match() -> None:
    with pytest.raises(ValueError, match="match at the AE2 seam"):
        _base(child_log_radii=np.asarray((0.01, -0.02, 0.03)))


def test_product_dirac_descriptor_has_exact_element_jets() -> None:
    result = _base(
        channel="product_Dirac",
        unit_channel_value=1.5,
        chirality=-1,
        seam_contact=0.0,
    )
    assert result["chirality"] == -1
    assert result["D_x_mid_K_elements"].shape == (4, 2, 2)
    assert result["D_h_K_elements"].shape == (4, 2, 2)
    assert result["D_h_M_elements"].shape == (4, 2, 2)
    assert np.allclose(result["K"], result["K"].T)
    assert np.allclose(result["M"], result["M"].T)


def test_artifact_replays_and_closes_only_the_finite_core_type() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "ONE_SEAM_DIRECT_DESCRIPTOR_AND_SCHUR_EQUIVALENCE_DERIVED"
    )
    assert payload["matching_audit"]["M_E0"] == "NOT_A_CURRENT_GATE7_SLOT"
    assert payload["matching_audit"]["B_birth"] == "NOT_A_CURRENT_GATE7_SLOT"
    assert payload["matching_audit"]["actual_graded_cotangent_value"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
