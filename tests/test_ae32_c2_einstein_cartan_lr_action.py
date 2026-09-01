import hashlib

import numpy as np
import pytest

from bhsm.interface.ae32_c2_einstein_cartan_lr_action import (
    ACTION_VERSION,
    action_completion_contract,
    algebraic_hubbard_stratonovich_block,
    charged_bridge_separation_theorem,
    claim_boundary,
    contorsion_schur_complement,
    local_current_c2_lr_kernel,
    retained_zero_mode_endpoint_domain_test,
    scalar_lr_channel_ledger,
)
from scripts.materialize_ae32_c2_einstein_cartan_lr_action import (
    TARGET,
    build_payload,
    main,
)


def test_first_order_completion_is_versioned_and_not_double_counted():
    result = action_completion_contract()
    assert ACTION_VERSION == "BHSM-AE-3.2.0-CANDIDATE"
    assert result["predecessor_action_version"] == "BHSM-AE-3.1.0"
    assert result["replacement_not_addition"]
    assert result["contorsion_is_algebraic"]
    assert not result["new_continuous_coefficient"]
    assert result["Gamma_EC_on_symmetric_zero_fermion_background"] == 0.0
    assert not result["background_geometry_first_variation_changed_at_zero_fermion"]
    assert not result["intrinsic_M4_Higgs_term_removed"]
    assert not result["intrinsic_Higgs_identified_with_HS_auxiliary"]
    assert not result["global_action_promotion_before_domain_test"]


def test_exact_clifford_fierz_coefficient_is_inherited_without_fit():
    result = contorsion_schur_complement()
    assert result["c_EC"] == 0.75
    assert result["scalar_LR_sign"] == "ATTRACTIVE"
    assert result["same_parent_Einstein_Dirac_Hessian"]
    assert not result["coefficient_inserted_by_hand"]


def test_local_current_c2_kernel_is_positive_even_and_divergent_at_support_edge():
    sigma = np.asarray((-0.49, -0.25, 0.0, 0.25, 0.49))
    result = local_current_c2_lr_kernel(sigma)
    values = result["K_G5_times_G_EC"]
    assert result["positive"]
    assert result["reflection_even"]
    assert np.isclose(values[2], 0.75)
    assert values[0] == values[-1] > values[2]
    assert not result["global_zero_mode_weighted_integrability_derived"]
    assert not result["global_reduced_EC_action_domain_derived"]


def test_kernel_rejects_noninterior_or_nonfinite_material_values():
    with pytest.raises(ValueError):
        local_current_c2_lr_kernel(np.asarray((0.5,)))
    with pytest.raises(ValueError):
        local_current_c2_lr_kernel(np.asarray((np.nan,)))


def test_all_lr_channels_are_attached_but_family_action_is_central():
    result = scalar_lr_channel_ledger()
    assert result["total_pairing_multiplicity"] == 24
    assert result["family_action"] == "I3"
    assert result["all_channels_gauge_singlets_after_LR_product"]
    assert not result["family_noncentral_direction_selected"]
    assert result["neutrino_is_effective_extension_not_minimal_SM"]


def test_retained_zero_mode_is_l2_but_not_in_ec_quartic_form_domain():
    result = retained_zero_mode_endpoint_domain_test()
    expected = 3.0 * np.pi / 512.0
    assert result["zero_mode_L2_normalizable"]
    assert not result["EC_quartic_form_finite"]
    assert not result["retained_zero_mode_in_reduced_EC_form_domain"]
    assert not result["first_order_contorsion_infimum_bounded_below_on_zero_mode"]
    assert abs(result["cutoff_rows"][-1]["epsilon_times_integral"] - expected) < 5.0e-5


def test_endpoint_domain_test_rejects_invalid_cutoff_order():
    with pytest.raises(ValueError):
        retained_zero_mode_endpoint_domain_test((0.01, 0.02))


def test_hs_transform_is_algebraic_not_a_physical_yukawa_residue():
    result = algebraic_hubbard_stratonovich_block()
    assert result["unnormalized_LR_HS_vertex"] == 1.0
    assert result["HS_quadratic_coefficient_positive_in_C2_interior"]
    assert not result["HS_derivative_kinetic_term_present"]
    assert not result["auxiliary_field_is_propagating"]
    assert not result["canonical_Yukawa_residue_derived"]


def test_charged_bridge_values_cannot_be_relabelled_as_quark_yukawas():
    result = charged_bridge_separation_theorem()
    assert not result["objects_are_the_same_variation"]
    assert not result["beta_u_or_beta_d_promoted_to_Yukawa_prefactor"]
    assert not result["kappa_u_or_kappa_d_promoted_to_Yukawa_prefactor"]
    assert not result["independent_c_u_or_c_d_inserted"]


def test_claim_boundary_promotes_only_the_local_algebraic_lr_kernel():
    result = claim_boundary()
    assert result["BHSM_AE32_FIRST_ORDER_EINSTEIN_CARTAN_COMPLETION_FORMULATED"]
    assert not result["BHSM_AE32_FIRST_ORDER_EINSTEIN_CARTAN_COMPLETION_GLOBALLY_PROMOTED"]
    assert result["CURRENT_C2_LOCAL_ALGEBRAIC_LR_KERNEL_DERIVED"]
    assert result["CURRENT_C2_EXACT_CLIFFORD_FIERZ_COEFFICIENT_DERIVED"]
    assert not result["CURRENT_C2_GLOBAL_REDUCED_EC_ACTION_DOMAIN_DERIVED"]
    assert result["RETAINED_ZERO_MODE_EC_ENDPOINT_DIVERGENCE_DERIVED"]
    assert not result["CURRENT_C2_PROPAGATING_HS_KINETIC_KERNEL_DERIVED"]
    assert not result["UP_DOWN_ACTION_YUKAWA_PREFACTORS_DERIVED"]
    assert not result["QUARK_MASS_OPERATORS_DERIVED"]


def test_materialized_ae32_action_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
