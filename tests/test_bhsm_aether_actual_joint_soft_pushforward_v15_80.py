import json

from bhsm.interface.aether_actual_joint_soft_pushforward_v15_80 import (
    completion_payload,
    deterministic_json,
    first_actual_joint_crossing,
    same_slice_residues,
    soft_wall_source_projection,
)


def test_soft_source_and_actual_crossing_are_nonzero():
    source = soft_wall_source_projection()
    crossing = first_actual_joint_crossing()
    assert source["nonzero"]
    assert abs(source["g_s0"]) > 0.05
    assert 0.0 < crossing["delta_star"] < 1.0e-3
    assert crossing["minimum_eta_Legendre_at_crossing"] > 0.5


def test_gauge_and_lr_residues_come_from_the_same_slice():
    residues = same_slice_residues()
    assert residues["absolute_transverse_DtN_residue"] > 0.0
    assert residues["absolute_electric_DtN_residue"] > 0.0
    assert residues["nonzero_LR_soft_residue"] > 0.0
    assert residues["common_slice"] and residues["common_Gamma_boundary"]
    assert not residues["independent_Yukawa_normalization"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.80"
