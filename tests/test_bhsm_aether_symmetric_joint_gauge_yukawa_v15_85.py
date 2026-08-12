import json

from bhsm.interface.aether_symmetric_joint_gauge_yukawa_v15_85 import (
    channel_ledger,
    completion_payload,
    deterministic_json,
    same_slice_joint_coefficients,
)


def test_same_slice_has_absolute_gauge_and_nonzero_yukawa():
    row = same_slice_joint_coefficients()
    assert row["absolute_transverse_DtN"] > 0.0
    assert row["absolute_electric_DtN"] > 0.0
    assert row["Z_H_at_H_zero"] > 0.0
    assert row["canonical_Yukawa_per_normalized_paired_mode"] > 0.0
    assert row["same_slice"] and row["same_parent_Gamma_boundary"]


def test_yukawa_vertex_is_not_confused_with_mass_or_condensate():
    row = same_slice_joint_coefficients()
    assert row["Yukawa_vertex_nonzero"]
    assert not row["condensate_nonzero"]
    assert row["composite_background_H_star"] == 0.0
    assert row["fermion_mass_m_star"] == 0.0
    assert channel_ledger()["all_channels_nonzero"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.85"
