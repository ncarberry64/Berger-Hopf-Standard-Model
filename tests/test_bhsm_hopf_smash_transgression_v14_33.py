from __future__ import annotations
from pathlib import Path
import numpy as np

from bhsm.interface.completion.hopf_smash_completion_gate_v14_33 import (
    all_payloads,
    completion_payload,
    materialization_hashes,
)
from bhsm.interface.completion.hopf_smash_topological_transgression_v14_33 import (
    EXACT_NEXT_OBJECT,
    degree_form_factorization_payload,
    fr_dirac_transgression_gate_payload,
    join_dimension,
    join_smash_architecture_payload,
    normalized_suspension_factor,
    path_b_reconciliation_payload,
    pushforward_degree,
    smash_dimension,
    sphere_volume,
    suspension_radial_integral,
    topological_current_transgression_payload,
    transgressed_current_conservation,
)


def test_01_sphere_volumes():
    assert np.isclose(sphere_volume(6), 16 * np.pi**3 / 15)
    assert np.isclose(sphere_volume(7), np.pi**4 / 3)


def test_02_join_and_smash_dimensions():
    assert smash_dimension(3, 3) == 6
    assert join_dimension(3, 3) == 7


def test_03_suspension_integral_and_normalization():
    assert abs(suspension_radial_integral() - 5 * np.pi / 16) < 1e-11
    assert abs(normalized_suspension_factor() - 1 / sphere_volume(6)) < 1e-11


def test_04_join_smash_architecture_passes():
    payload = join_smash_architecture_payload()
    assert payload["validation_passed"]
    assert "S3_base smash S3_fiber" in payload["smash_identity"]


def test_05_degree_form_factorization_passes():
    assert degree_form_factorization_payload()["validation_passed"]


def test_06_zero_boundary_flux_preserves_degree():
    result = pushforward_degree(1, 0.0)
    assert result["physical_charge"] == 1.0
    assert transgressed_current_conservation(0.0, 0.0) == 0.0


def test_07_boundary_flux_is_fail_closed():
    result = pushforward_degree(1, 0.25)
    assert result["physical_charge"] == 0.75
    assert transgressed_current_conservation(0.0, 0.25) != 0.0


def test_08_topological_current_payload_passes():
    payload = topological_current_transgression_payload()
    assert payload["validation_passed"]
    assert "Pi_!(nu7)" in payload["physical_current_three_form"]


def test_09_v14_32_no_go_is_preserved_for_M4_field_alone():
    payload = path_b_reconciliation_payload()
    assert payload["validation_passed"]
    assert "homotopically trivial" in payload["M4_statement"]


def test_10_FR_is_available_but_not_derived():
    payload = fr_dirac_transgression_gate_payload()
    assert payload["validation_passed"]
    assert payload["FR_status"].startswith("TOPOLOGICALLY_AVAILABLE")
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_11_completion_gate_stops_at_smooth_equivariant_map():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["full_preimage_smash_topology_gate"].startswith("PASSED")
    assert payload["smooth_equivariant_map_gate"] == "OPEN"
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_12_no_physical_outputs_emitted():
    payload = completion_payload()
    assert all(value is None for value in payload["forbidden_outputs"].values())


def test_13_materialization_is_deterministic(tmp_path: Path):
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert "BHSM_completion_gate_v14_33.json" in first


def test_14_required_artifacts_present():
    names = all_payloads()
    for name in (
        "BHSM_Hopf_base_fiber_join_smash_architecture_v14_33.json",
        "BHSM_eta_degree_form_suspension_factorization_v14_33.json",
        "BHSM_M8_to_M4_topological_current_transgression_v14_33.json",
        "BHSM_Path_B_and_M8_transgression_reconciliation_v14_33.json",
        "BHSM_FR_Dirac_transgression_gate_v14_33.json",
        "BHSM_completion_gate_v14_33.json",
    ):
        assert name in names
