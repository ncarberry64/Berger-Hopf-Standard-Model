import hashlib

from bhsm.interface.ae31_c2_quark_parent_third_variation import (
    claim_boundary,
    current_action_incidence_theorem,
    current_hs_vertex_separation,
    exact_next_owner,
    historical_residue_adjudication,
    maximal_eft_variation_theorem,
)
from scripts.materialize_ae31_c2_quark_parent_third_variation import (
    TARGET,
    build_payload,
    main,
)


def test_active_ae31_intrinsic_quark_variations_are_exactly_absent():
    theorem = current_action_incidence_theorem()
    assert theorem["up_zero_by_field_incidence"]
    assert theorem["down_zero_by_field_incidence"]
    assert not theorem["up_down_Yukawa_terms_added"]
    assert theorem["zero_is_a_derived_absence_not_a_zero_physical_quark_mass_claim"]
    assert not theorem["physical_quark_mass_zero_promoted"]


def test_maximal_eft_variation_returns_inputs_instead_of_deriving_them():
    theorem = maximal_eft_variation_theorem()
    assert theorem["only_T4_Yukawa_contributes"]
    assert theorem["coefficient_classification"] == "INDEPENDENT_THEORY_INPUT"
    assert theorem["variation_recovers_input_matrix"]
    assert not theorem["variation_derives_input_matrix"]
    assert not theorem["representation_trace_or_projector_removes_sector_scalar"]


def test_current_hs_vertex_is_not_intrinsic_quark_higgs_normalization():
    separation = current_hs_vertex_separation()
    assert separation["current_C2_reduced_third_vertex_nonzero"]
    assert separation["family_factor"] == "I3"
    assert not separation["intrinsic_H_or_H_tilde_derivative"]
    assert not separation["current_C2_dynamical_HS_kernel_derived"]
    assert not separation["physical_broken_LR_direction_selected"]
    assert not separation["can_canonically_normalize_Y_u_or_Y_d"]


def test_no_historical_residue_is_silently_promoted():
    history = historical_residue_adjudication()
    assert history["attachable_current_AE31_intrinsic_quark_residue_count"] == 0
    assert not history["historical_result_discarded"]
    assert not history["historical_result_silently_promoted"]
    assert all(not row["current_AE31_intrinsic_quark_owner"] for row in history["rows"])


def test_next_owner_requires_both_unfitted_sector_derivatives():
    owner = exact_next_owner()
    assert len(owner["required_derivatives"]) == 2
    assert not owner["quark_mass_fit_allowed"]
    assert not owner["independent_c_u_or_c_d_allowed"]
    assert any("T_u" in entry for entry in owner["must_include"])


def test_claim_boundary_does_not_promote_quark_poles_or_ckm():
    boundary = claim_boundary()
    assert boundary["CURRENT_AE31_UP_DOWN_INTRINSIC_HIGGS_THIRD_VARIATIONS_EVALUATED"]
    assert not boundary["CURRENT_AE31_UP_INTRINSIC_HIGGS_THIRD_VARIATION_NONZERO"]
    assert not boundary["CURRENT_AE31_DOWN_INTRINSIC_HIGGS_THIRD_VARIATION_NONZERO"]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
    assert not boundary["CKM_MATRIX_DERIVED"]


def test_materialized_third_variation_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
