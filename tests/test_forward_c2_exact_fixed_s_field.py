from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import numpy as np

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (
    exact_fixed_s_field_action,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def test_exact_fixed_s_field_matches_certified_center_1214() -> None:
    with np.load(BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz") as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.npz") as data:
        expected = np.asarray(data["exact_center_field_action"], dtype=float)
    import json
    record = json.loads((BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json").read_text(encoding="utf-8"))
    result = exact_fixed_s_field_action(
        state=center,
        weights=weights,
        reference=reference,
        signed_descriptor=float(Decimal(record["center_field"]["signed_descriptor_decimal"])),
    )
    assert result["selected_branch"] == 24
    assert abs(float(result["Dlambda_field"]) - 1.0) < 1.0e-12
    assert abs(
        float(result["c_psi"])
        - float(record["center_field"]["moving_cubic_direct_fixed_line_D3"])
    ) / abs(float(result["c_psi"])) < 2.0e-11
    assert np.linalg.norm(np.asarray(result["field_action"]) - expected) / np.linalg.norm(expected) < 5.0e-10
    assert result["explicit_full_Euler_Dirac_inverse_formed"] is False
