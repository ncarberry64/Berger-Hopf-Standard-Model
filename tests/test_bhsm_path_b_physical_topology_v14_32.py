from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.completion.path_b_completion_gate_v14_32 import (
    all_payloads,
    completion_payload,
    materialization_hashes,
)
from bhsm.interface.completion.path_b_physical_topology_v14_32 import (
    CONFINEMENT_NEXT_OBJECT,
    MATTER_NEXT_OBJECT,
    bvp_interpretation_payload,
    derrick_scaled_energies,
    derrick_stationarity_residual,
    fr_obstruction_payload,
    global_s6_constraint,
    global_s6_kinetic,
    global_target_payload,
    matter_completion_fork_payload,
    normalize_global_s6,
    physical_topology_payload,
    source_bound_saddle_classification,
    sphere_homotopy_vanishes_below_dimension,
)


def test_01_global_s6_normalization():
    s, z = normalize_global_s6(0.4, np.asarray([0.2 + 0.3j, -0.1j, 0.5]))
    assert np.isclose(global_s6_constraint(s, z), 1.0)


def test_02_global_s6_kinetic_matches_local_complex_metric():
    ds = np.asarray([0.0, 0.0])
    dz = np.asarray([[1.0, 0.0, 0.0], [0.0, 1j, 0.0]], complex)
    assert global_s6_kinetic(ds, dz) == 4.0


def test_03_sphere_connectivity_gives_pi3_and_pi4_zero():
    assert sphere_homotopy_vanishes_below_dimension(3, 6)
    assert sphere_homotopy_vanishes_below_dimension(4, 6)
    assert not sphere_homotopy_vanishes_below_dimension(6, 6)


def test_04_physical_static_eta_has_no_degree_one_sector():
    payload = physical_topology_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == "pi_3(S6)=0"
    assert "no degree-one" in payload["consequence"]


def test_05_FR_loop_group_is_trivial_for_M4_S6_eta():
    payload = fr_obstruction_payload()
    assert payload["validation_passed"]
    assert payload["FR_result"].startswith("TRIVIAL")
    assert "pi_4(S6)=0" in payload["adjunction"]


def test_06_M8_historical_FR_result_is_not_erased():
    payload = fr_obstruction_payload()
    assert "not invalidated" not in payload["invalidated_identification"].lower()
    assert "historical FR result" in payload["not_invalidated"]


def test_07_derrick_scaling_exponents_are_exact():
    values = derrick_scaled_energies(2.0, 3.0, 5.0, 7.0)
    assert values["E2"] == 6.0
    assert np.isclose(values["E8"], 5.0 / 32.0)
    assert values["EYM"] == 3.5


def test_08_reference_virial_identity_closes():
    assert derrick_stationarity_residual(7.0, 1.0, 2.0) == 0.0
    assert bvp_interpretation_payload()["validation_passed"]


def test_09_source_bound_response_is_not_topological_particle():
    assert source_bound_saddle_classification(
        stationary=True,
        hessian_nonnegative=True,
        source_removed_limit_vacuum=True,
    ) == "STABLE_SOURCE_BOUND_RESPONSE_NOT_A_TOPOLOGICAL_PARTICLE"


def test_10_external_Wilson_BVP_remains_parallel_open_object():
    payload = bvp_interpretation_payload()
    assert payload["exact_confinement_object"] == CONFINEMENT_NEXT_OBJECT
    assert payload["BVP_status"].startswith("ELIGIBLE")


def test_11_matter_completion_fork_is_explicit():
    payload = matter_completion_fork_payload()
    assert payload["validation_passed"]
    assert payload["exact_next_object"] == MATTER_NEXT_OBJECT
    assert len(payload["routes"]) == 4


def test_12_global_target_payload_passes():
    assert global_target_payload()["validation_passed"]


def test_13_completion_gate_preserves_v14_31_but_stops_FR_claim():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["v14_31_action_ownership_gate"].startswith("PRESERVED")
    assert payload["physical_eta_FR_gate"].startswith("FAILED")
    assert payload["exact_next_object"] == MATTER_NEXT_OBJECT


def test_14_no_physical_outputs_emitted():
    payload = completion_payload()
    assert not payload["physical_outputs_emitted"]
    assert all(value is None for value in payload["forbidden_outputs"].values())


def test_15_materialization_is_deterministic(tmp_path: Path):
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert "BHSM_completion_gate_v14_32.json" in first


def test_16_required_artifacts_are_present():
    names = all_payloads()
    for required in (
        "BHSM_Path_B_global_S6_target_v14_32.json",
        "BHSM_Path_B_physical_eta_topology_gate_v14_32.json",
        "BHSM_Path_B_FR_topology_obstruction_v14_32.json",
        "BHSM_Path_B_BVP_topology_interpretation_v14_32.json",
        "BHSM_Path_B_matter_completion_fork_v14_32.json",
        "BHSM_completion_gate_v14_32.json",
    ):
        assert required in names
