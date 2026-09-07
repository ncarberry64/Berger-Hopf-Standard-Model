import hashlib

from bhsm.interface.ae31_c2_quark_scalar_attachment_variation import (
    chirality_parity_theorem,
    claim_boundary,
    current_action_internal_scalar_incidence,
    exact_remaining_owner,
    historical_parent_term_adjudication,
    required_odd_endomorphism_contract,
    scalar_only_variation_theorem,
)
from scripts.materialize_ae31_c2_quark_scalar_attachment_variation import (
    TARGET,
    build_payload,
    main,
)


def test_internal_profile_is_not_active_AE31_coordinate():
    theorem = current_action_internal_scalar_incidence()
    assert not theorem["active_internal_Phi_field"]
    assert not theorem["delta_S_AE31_over_delta_Phi_defined"]
    assert not theorem["H_times_Phi_kinematic_factorization_is_action_attachment"]


def test_u1_connection_cannot_equal_chirality_odd_scalar_incidence():
    theorem = chirality_parity_theorem()
    assert theorem["u1_chirality_commutator_norm"] == 0.0
    assert theorem["u1_left_right_block_norm"] == 0.0
    assert theorem["up_scalar_chirality_anticommutator_norm"] == 0.0
    assert theorem["down_scalar_chirality_anticommutator_norm"] == 0.0
    assert not theorem["even_U1_connection_variation_can_equal_odd_LR_scalar_vertex"]


def test_scalar_profile_normalization_does_not_create_fermion_vertex():
    theorem = scalar_only_variation_theorem()
    assert theorem["kinetic_residue_conditionally_fixed"]
    assert set(theorem["mixed_third_variations"].values()) == {"0"}
    assert not theorem["profile_normalization_generates_Yukawa_vertex"]


def test_historical_phi_terms_preserve_their_actual_roles():
    theorem = historical_parent_term_adjudication()
    assert not theorem["boundary_functional_full_action_variation_completed"]
    assert not theorem["target_values_6_and_12_relabelled_as_Yukawa_residues"]
    assert all(not row["can_own_c_u_c_d"] for row in theorem["rows"])


def test_required_parent_object_is_odd_without_being_inserted():
    contract = required_odd_endomorphism_contract()
    assert contract["sample_grading_residual"] == 0.0
    assert contract["existing_binary_supports_reused"]
    assert not contract["new_representation_channel_required"]
    assert not contract["new_independent_contact_term_required"]
    assert not contract["coefficient_or_residue_inserted"]
    assert not contract["object_promoted_into_AE31_action"]


def test_remaining_owner_is_one_parent_action_not_a_fit():
    owner = exact_remaining_owner()
    assert not owner["U1_connection_or_scalar_kinetic_term_can_substitute"]
    assert not owner["historical_target_or_beta_kappa_relabelling_allowed"]
    assert not owner["independent_yukawa_or_mass_fit_allowed"]
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_REQUIRED_ODD_DIRAC_ENDOMORPHISM_CLASS_DERIVED"]
    assert not boundary["CURRENT_C2_ODD_DIRAC_ENDOMORPHISM_ACTION_OWNED"]


def test_materialized_scalar_attachment_variation_is_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
