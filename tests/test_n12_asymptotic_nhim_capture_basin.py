from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_asymptotic_nhim_capture_basin.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_family_and_normal_spectrum_produce_existential_basin() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    nhim = payload["leading_weight_NHIM"]
    assert nhim["tangent_center_roots"] == 25
    assert nhim["stable_normal_roots"] == 25
    assert nhim["unstable_normal_roots"] == 0
    theorem = payload["capture_theorem"]
    assert theorem["forward_local_capture"] is True
    assert theorem["H4_limit"] == "H0>0"
    assert theorem["shape_limit_exists"] is True


def test_common_scale_is_not_double_counted_with_epsilon() -> None:
    payload = _payload()
    compactified = payload["compactified_full_flow"]
    assert compactified[
        "common_scale_center_replaced_by_epsilon_on_forward_scale_section"
    ] is True
    assert compactified["boundary_family_shape_dimension"] == 24
    assert compactified["stable_velocity_normal_dimension"] == 25
    assert compactified["stable_radial_dimension"] == 1
    assert compactified["total_stable_normal_dimension"] == 26


def test_basin_is_not_promoted_to_reset_connection_or_continuum() -> None:
    payload = _payload()
    scope = payload["scope"]
    assert scope["existential_not_quantitative"] is True
    assert scope["explicit_capture_surface_certified"] is False
    assert scope["AE2_reset_entry_certified"] is False
    assert scope["continuum_uniformity_certified"] is False
    boundary = payload["claim_boundary"]
    assert boundary["Gate7"].startswith("ACTIVE_")
    assert boundary["Gate8"] == "LOCKED"
    assert boundary["chord_03_authorized"] is False
