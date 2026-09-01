import hashlib

import numpy as np

from bhsm.interface.ae31_c2_fixed_history_state_nonuniqueness import (
    ACTION_VERSION,
    claim_boundary,
    finite_rank_hadamard_nonuniqueness_theorem,
    pure_self_dual_covariance,
    retained_selector_status,
)
from scripts.materialize_ae31_c2_fixed_history_state_nonuniqueness import (
    TARGET,
    build_payload,
    main,
)


def test_finite_rank_witness_is_a_distinct_pure_self_dual_covariance():
    witness = pure_self_dual_covariance(0.37)
    assert ACTION_VERSION == "BHSM-AE-3.1.0"
    assert witness["frame_orthonormality_residual"] < 1.0e-12
    assert witness["Hermitian_residual"] < 1.0e-12
    assert witness["purity_residual"] < 1.0e-12
    assert witness["self_dual_CAR_residual"] < 1.0e-12
    assert witness["charge_commutator_residual"] < 1.0e-12
    assert witness["minimum_eigenvalue"] > -1.0e-12
    assert witness["maximum_eigenvalue"] < 1.0 + 1.0e-12
    assert witness["distance_from_zero_covariance"] > 0.1


def test_theta_zero_recovers_reference_projection():
    witness = pure_self_dual_covariance(0.0)
    assert np.allclose(
        witness["covariance_theta"], witness["covariance_zero"], atol=1.0e-12
    )
    assert witness["distance_from_zero_covariance"] < 1.0e-12


def test_nonuniqueness_survives_family_and_reset_requirements():
    theorem = finite_rank_hadamard_nonuniqueness_theorem()
    assert theorem["P_theta_minus_P_is_finite_rank_smoothing"]
    assert theorem["Hadamard_wavefront_and_polarization_unchanged"]
    assert theorem["gauge_charge_grading_unchanged"]
    assert theorem["family_projectors_unchanged"]
    assert theorem["reset_transport_preserves_the_continuum"]
    assert theorem["continuum_of_distinct_pure_Hadamard_covariances"]
    assert not theorem["history_selection_alone_selects_a_state"]


def test_current_retained_structures_do_not_supply_missing_selector():
    selector = retained_selector_status()
    assert selector["current_Gate7_continuous_action_constrained_history"] == "OPEN"
    assert not selector["stored_quarter_DOP853_center_is_physical_history"]
    assert not selector["mathematical_asymptotic_branch_is_owner_realized"]
    assert not selector["asymptotic_stationary_vacuum_condition_derived"]
    assert not selector["complete_child_boundary_H_xi_executable"]
    assert selector["classical_constraint_reduced_Legendre_energy"] == 0.0
    assert not selector["even_a_future_unique_history_would_remove_covariance_freedom"]


def test_claim_boundary_promotes_no_selector_theorem_not_physical_poles():
    boundary = claim_boundary()
    assert boundary[
        "CURRENT_C2_FIXED_HISTORY_PURE_HADAMARD_STATE_NONUNIQUENESS_DERIVED"
    ]
    assert not boundary[
        "CURRENT_C2_HISTORY_SELECTION_ALONE_SUFFICIENT_FOR_STATE_SELECTION"
    ]
    assert not boundary["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"]
    assert not boundary["CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
    assert not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
    assert not boundary["new_state_parameter_inserted"]
    assert not boundary["particle_spectrum_rebuilt"]


def test_materialized_fixed_history_theorem_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
