import hashlib
import math

import numpy as np
import pytest

from bhsm.interface.ae31_c2_quark_channel_selector_domain import (
    claim_boundary,
    classical_selector_domain,
    exact_dependency_order,
    hadamard_susceptibility_witness,
    quantum_selector_contract,
    selector_state_dependence_theorem,
)
from scripts.materialize_ae31_c2_quark_channel_selector_domain import (
    TARGET,
    build_payload,
    main,
)


def test_intrinsic_undefined_is_not_relabelled_auxiliary_zero():
    domain = classical_selector_domain()
    assert domain["intrinsic_quark_channel_Hessian_status"] == "UNDEFINED_ON_ACTIVE_FIELD_SPACE"
    assert not domain["intrinsic_undefined_may_be_relabelled_zero"]
    assert domain["reduced_probe_rank"] == 0
    assert not domain["reduced_probe_is_complete_dynamical_HS_Hessian"]
    assert not domain["reduced_zero_block_selects_physical_direction"]


def test_hadamard_susceptibility_witness_is_charge_compatible():
    witness = hadamard_susceptibility_witness(math.pi / 6.0)
    assert max(witness["vertex_charge_commutator_norms"]) == 0.0
    assert witness["susceptibility_rank"] == 1
    assert witness["susceptibility_trace"] > 0.0
    assert not witness["proxy_is_physical_BHSM_quark_Hessian"]


def test_nonfinite_covariance_angle_fails_closed():
    with pytest.raises(ValueError):
        hadamard_susceptibility_witness(float("nan"))


def test_smooth_state_rotation_changes_finite_channel_response():
    theorem = selector_state_dependence_theorem()
    assert theorem["response_difference_frobenius_norm"] > 1.0e-12
    assert theorem["response_changes_within_same_Hadamard_class"]
    assert not theorem["action_and_domain_alone_fix_finite_channel_response"]
    assert not theorem["Hadamard_singularity_condition_alone_fixes_finite_channel_response"]
    assert np.asarray(theorem["reference"]["susceptibility_matrix"]).shape == (2, 2)


def test_quantum_formula_names_every_missing_input():
    contract = quantum_selector_contract()
    assert "G_C" in contract["second_variation_identity"]
    assert not contract["current_AE31_V_up_V_down_intrinsic_vertices_present"]
    assert not contract["current_C2_complete_dynamical_HS_kernel_present"]
    assert not contract["current_C2_action_selected_Feynman_inverse_present"]
    assert not contract["formula_currently_evaluable_as_physical_selector"]


def test_dependency_order_starts_before_diagonalization():
    order = exact_dependency_order()
    assert order["first_missing_object"].endswith("V_u_V_d_Q_fg")
    assert [row["order"] for row in order["steps"]] == [1, 2, 3, 4]
    assert not order["physical_channel_diagonalization_ready"]
    assert not order["quark_mass_fit_allowed"]


def test_claim_boundary_keeps_selector_and_poles_open():
    boundary = claim_boundary()
    assert boundary["CURRENT_AE31_INTRINSIC_QUARK_CHANNEL_HESSIAN_DOMAIN_CLASSIFIED"]
    assert not boundary["CURRENT_AE31_INTRINSIC_QUARK_CHANNEL_HESSIAN_DEFINED"]
    assert boundary["CURRENT_C2_QUANTUM_SELECTOR_STATE_DEPENDENCE_COUNTEREXAMPLE_DERIVED"]
    assert not boundary["CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]


def test_materialized_selector_domain_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
