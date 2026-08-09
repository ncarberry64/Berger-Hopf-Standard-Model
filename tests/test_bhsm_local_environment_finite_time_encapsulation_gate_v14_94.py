import json

import numpy as np
import pytest

from bhsm.interface.completion.local_environment_finite_time_encapsulation_gate_v14_94 import (
    EXACT_NEXT_OBJECT,
    PATH_A_STATUS,
    completion_payload,
    environment_variable_ledger,
    event_gate_status,
    exact_incoming_state,
    homogeneous_shape_operator,
    instability_mechanism_ledger,
    integrate_linear_mode,
    local_flux_and_energy_ledger,
    materialize,
    resolution_convergence,
)


def test_environment_uses_only_retained_canonical_variables() -> None:
    names = {row["variable"] for row in environment_variable_ledger()}
    assert {"h_ij", "pi^ij", "eta", "p_eta", "chi,p_chi", "sigma,p_sigma"} <= names
    assert all("detector" not in name for name in names)


@pytest.mark.parametrize("branch", ["round", "jensen"])
def test_exact_incoming_branches_are_dynamic_and_constraint_satisfying(branch: str) -> None:
    state = exact_incoming_state(branch)
    assert state["physical_time_dependent"] is True
    assert state["canonical_momentum_nonzero"] is True
    assert abs(state["Hamiltonian_constraint_residual"]) < 1.0e-13
    assert state["momentum_constraint_residual"] == 0.0
    assert state["incoming_localized_flux_state"] is False


def test_round_is_stable_and_jensen_has_one_global_tachyon() -> None:
    round_modes = homogeneous_shape_operator("round", 1.0)["operators"]
    jensen_modes = homogeneous_shape_operator("jensen", 1.0)["operators"]
    assert all(row["mass_squared"] > 0.0 for row in round_modes)
    assert sum(row["mass_squared"] < 0.0 for row in jensen_modes) == 1
    assert sum(row["positive_growth_exponent"] for row in jensen_modes) == 1


def test_jensen_instability_has_no_threshold_crossing() -> None:
    stiffness = instability_mechanism_ledger()[0]
    assert stiffness["round"].startswith("NO_")
    assert stiffness["jensen"].startswith("NO_CROSSING")
    for time in (0.0, 0.5, 2.0, 10.0):
        assert homogeneous_shape_operator("jensen", time)["operators"][1]["mass_squared"] < 0.0


def test_homogeneous_dynamics_has_no_local_outgoing_flux() -> None:
    flux = local_flux_and_energy_ledger()
    assert flux["local_gravitational_energy_density"] is None
    assert flux["homogeneous_spatial_matter_flux"] == 0.0
    assert flux["homogeneous_spatial_gravitational_transport_flux"] == 0.0
    assert flux["homogeneous_cap_relative_flux"] == 0.0
    assert flux["event_energy_accounting"] is None


def test_finite_time_propagator_converges_and_obeys_wronskian_identity() -> None:
    convergence = resolution_convergence()
    assert convergence["observed_refinement"] > 12.0
    assert convergence["maximum_Wronskian_residual"] < 1.0e-9
    assert convergence["nonlinear_event_simulated"] is False


def test_propagator_validation_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        integrate_linear_mode("other", 0, 0.0, 1.0, 10)
    with pytest.raises(ValueError):
        integrate_linear_mode("round", 0, 1.0, 0.0, 10)
    with pytest.raises(ValueError):
        integrate_linear_mode("round", 0, 0.0, 1.0, 0)


def test_no_event_objects_are_fabricated() -> None:
    status = event_gate_status()
    assert status["threshold_location_time"] is None
    assert status["nonlinear_completion"] is None
    assert status["completion_criterion_C_enc"] is None
    assert status["post_event_state"] is None
    assert status["DeltaPi_t"] == 0.0
    assert status["B_dyn_L2"] is None


def test_outcome_d_and_next_object_are_exact() -> None:
    payload = completion_payload()
    assert PATH_A_STATUS == "NO_ENCAPSULATION_EVENT_IN_CONTROLLED_RETAINED_SECTORS_PATH_A_REMAINS_OPEN"
    assert payload["PATH_A_STATUS"] == PATH_A_STATUS
    assert payload["LOCAL_ENVIRONMENT_INSTABILITY_DERIVED"] is False
    assert payload["HOMOGENEOUS_GLOBAL_INSTABILITY_DERIVED"] is True
    assert payload["FINITE_TIME_ENCAPSULATION_EVENT_DERIVED"] is False
    assert payload["PATH_B_FALLBACK_ACTIVATED"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["validation_passed"] is True


def test_materializer_is_deterministic_and_strict_json(tmp_path) -> None:
    target = tmp_path / "v14_94.json"
    first = materialize(target).read_bytes()
    second = materialize(target).read_bytes()
    assert first == second
    assert json.loads(first) == completion_payload()
    assert np.isfinite(json.loads(first)["finite_time_evolution"]["observed_refinement"])
