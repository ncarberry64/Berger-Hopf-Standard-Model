from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
ARTIFACT = BASE / "BHSM_N12_GATE7_COMMON_FRAME_ANISOTROPIC_Z2_RECONNAISSANCE.json"


def test_anisotropic_z2_reconnaissance_is_not_promoted() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert len(payload["rows"]) == 48
    assert payload["validation"]["all_48_retained_macro_seams_evaluated"] is True
    assert payload["validation"]["common_scale_direction_not_deleted"] is True
    assert payload["validation"]["no_multiplier_or_hybrid_time_generator_projected_out_by_hand"] is True
    assert payload["validation_passed"] is False
    assert payload["claim_boundary"]["literal_Z2"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_anisotropic_arrays_are_finite_and_hashed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as data:
        assert data["correction_time_transverse_unit"].shape == (48, 72)
        assert data["mixed_D2f_dot_correction_unit"].shape == (48, 72, 72)
        assert data["directional_D2f_correction_unit_squared"].shape == (48, 72)
        assert all(np.all(np.isfinite(data[name])) for name in data.files)
