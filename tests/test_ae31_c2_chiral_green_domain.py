import hashlib

from bhsm.interface.ae31_c2_chiral_green_domain import (
    chiral_operator_assembly,
    claim_boundary,
    domain_provenance_reconciliation,
    family_reset_intertwiner_certificate,
    green_operator_feasibility,
)
from scripts.materialize_ae31_c2_chiral_green_domain import TARGET, build_payload, main


def test_ae2_supersedes_only_the_old_birth_phase_family():
    result = domain_provenance_reconciliation()
    assert not result["old_phase_family_live_in_AE31"]
    assert not result["AE3_enclosure_is_terminal_boundary"]
    assert not result["independent_enclosure_fermion_boundary_parameter_required"]
    assert "PHYSICAL_MEMBER" in result["remaining_domain_question"]


def test_first_order_family_noncentral_lr_operator_is_assembled():
    result = chiral_operator_assembly()
    assert result["same_current_C2_first_order_LR_block_assembled"]
    assert result["Hermitian_zero_order_perturbation"]
    assert result["domain_preserved_by_zero_order_mass_term"]
    assert result["first_order_principal_symbol_unchanged"]
    assert not result["measured_mass_used"]


def test_mass_block_intertwines_the_reset_without_new_phase():
    result = family_reset_intertwiner_certificate()
    assert result["commutator_residual"] == 0.0
    assert result["mass_block_intertwines_AE2_reset"]
    assert not result["new_Cayley_phase_introduced"]
    assert not result["new_surface_mass_density_introduced"]


def test_green_result_distinguishes_causal_from_stationary_propagators():
    result = green_operator_feasibility()
    assert result["same_domain_chiral_operator_available"]
    assert result["finite_core_global_hyperbolicity_derived_familywise"]
    assert result["advanced_retarded_Green_operator_existence_derived"]
    assert not result["physical_C2_history_member_selected"]
    assert not result["maximal_C2_Lorentzian_continuation_certified"]
    assert not result["retarded_Green_operator_constructed"]
    assert not result["Feynman_two_point_function_constructed"]
    assert not result["continuous_global_frequency_diagonalization_available"]
    assert not result["proper_history_z_identified_with_p_squared"]
    assert not result["mass_operator_is_first_obstruction"]
    assert not result["AE2_reset_domain_is_first_obstruction"]


def test_claim_boundary_promotes_the_operator_but_not_a_global_pole():
    boundary = claim_boundary()
    assert boundary["current_C2_first_order_charged_lepton_LR_operator_assembled"]
    assert boundary["current_C2_chiral_operator_domain_preserved_by_mass_block"]
    assert boundary["finite_core_current_C2_global_hyperbolicity_derived_familywise"]
    assert boundary["finite_core_advanced_retarded_Green_existence_derived"]
    assert not boundary["global_current_C2_charged_lepton_Green_operator_derived"]
    assert not boundary["global_or_dressed_current_C2_charged_lepton_poles_derived"]
    assert not boundary["proper_history_z_promoted_to_p_squared"]


def test_materialized_green_domain_theorem_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
