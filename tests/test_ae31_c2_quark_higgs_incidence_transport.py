import hashlib

from bhsm.interface.ae31_c2_quark_higgs_incidence_transport import (
    claim_boundary,
    current_c2_domain_tensor_theorem,
    exact_remaining_owner,
    finite_sector_projectors,
    quark_higgs_support_pencil,
    two_to_four_component_transport,
)
from scripts.materialize_ae31_c2_quark_higgs_incidence_transport import (
    TARGET,
    build_payload,
    main,
)


def test_two_component_boundary_classes_transport_to_current_quark_channels():
    theorem = two_to_four_component_transport()
    assert theorem["both_quark_classes_transport_uniquely"]
    rows = {row["sector"]: row for row in theorem["rows"]}
    assert rows["up"]["current_fields"] == ["bar(Q_L)", "H_tilde", "u_R"]
    assert rows["down"]["current_fields"] == ["bar(Q_L)", "H", "d_R"]
    assert all(row["current_charge_sum"] == "0" for row in rows.values())
    assert not theorem["standard_model_operator_table_used_as_premise"]


def test_existing_sector_projectors_select_support_not_residue():
    theorem = finite_sector_projectors()
    assert theorem["quark_projector_orthogonality_residual"] == 0.0
    assert theorem["all_sector_orthogonality_residual"] == 0.0
    assert theorem["sector_completeness_residual"] == 0.0
    assert theorem["up_down_support_selected"]
    assert not theorem["up_down_residue_selected"]


def test_binary_up_down_incidence_supports_are_distinct():
    theorem = quark_higgs_support_pencil()
    assert theorem["supports_linearly_independent"]
    assert theorem["support_inner_product"] == 0.0
    assert theorem["up_support_rank"] == 2
    assert theorem["down_support_rank"] == 2


def test_finite_internal_transport_preserves_current_c2_radial_domain():
    theorem = current_c2_domain_tensor_theorem()
    assert theorem["sample_commutator_residual"] == 0.0
    assert theorem["finite_internal_support_is_bounded"]
    assert theorem["reset_generated_C2_radial_operator_unchanged"]
    assert theorem["retained_birth_trace_unchanged"]
    assert not theorem["maximal_or_friedrichs_radial_domain_reselected"]


def test_remaining_owner_contains_coefficients_and_contact_jet_without_fit():
    owner = exact_remaining_owner()
    assert owner["transported_object"].startswith("rho_qH_support")
    assert owner["required_first_variations"] == ["V_u", "V_d"]
    assert len(owner["required_second_variations"]) == 4
    assert not owner["independent_yukawa_or_mass_fit_allowed"]


def test_claim_boundary_promotes_support_transport_only():
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORTED_CONDITIONAL"]
    assert boundary["CURRENT_C2_HISTORICAL_TO_CURRENT_FIELD_CONVENTION_BRIDGE_DERIVED"]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_COEFFICIENTS_ACTION_DERIVED"]
    assert not boundary["CURRENT_C2_QUARK_CONTACT_JET_ACTION_DERIVED"]
    assert not boundary["FULL_BHSM_COMPLETE"]


def test_materialized_incidence_transport_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
