import json

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import (
    completion_payload,
    deterministic_json,
    floquet_fermion_operator,
    one_cycle_residues,
)


def test_one_cycle_has_joint_positive_gauge_and_nonzero_yukawa():
    residues = one_cycle_residues()
    assert residues["PCHIP_cycle_transverse_DtN"] > 0.0
    assert residues["PCHIP_cycle_electric_DtN"] > 0.0
    assert residues["PCHIP_cycle_canonical_Yukawa"] > 0.0
    assert residues["same_Gamma_cycle"]
    assert residues["reset_probe_derivative"] == 0.0


def test_symmetric_floquet_mass_zero_does_not_erase_yukawa():
    floquet = floquet_fermion_operator()
    assert floquet["Floquet_mass_eigenvalues"] == [0.0, 0.0, 0.0]
    assert floquet["massless_does_not_imply_zero_Yukawa"]
    assert "not_zero" in floquet["Yukawa_vertex_matrix"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.86"
