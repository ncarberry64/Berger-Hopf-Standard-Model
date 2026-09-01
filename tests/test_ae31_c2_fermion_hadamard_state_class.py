import hashlib

from bhsm.interface.ae31_c2_fermion_hadamard_state_class import (
    ACTION_VERSION,
    EXTERNAL_THEOREM_REFERENCES,
    cauchy_covariance_selection_contract,
    claim_boundary,
    hadamard_class_existence_theorem,
    retained_state_selector_audit,
)
from scripts.materialize_ae31_c2_fermion_hadamard_state_class import (
    TARGET,
    build_payload,
    main,
)


def test_hadamard_class_exists_familywise_without_selecting_one_state():
    result = hadamard_class_existence_theorem()
    assert ACTION_VERSION == "BHSM-AE-3.1.0"
    assert result["globally_hyperbolic_member_by_member"]
    assert result["advanced_retarded_Green_existence_inherited"]
    assert result["external_existence_theorems"] == EXTERNAL_THEOREM_REFERENCES
    assert len(EXTERNAL_THEOREM_REFERENCES) == 2
    assert result["quasifree_Hadamard_state_class_nonempty_member_by_member"]
    assert result["state_dependent_Feynman_two_point_distribution_exists"]
    assert result["local_Hadamard_singularity_class_is_state_independent"]
    assert not result["smooth_state_dependent_part_is_fixed_by_action"]
    assert not result["one_Hadamard_state_selected"]
    assert not result["global_frequency_poles_defined"]


def test_exact_missing_datum_is_a_reset_compatible_cauchy_covariance():
    result = cauchy_covariance_selection_contract()
    assert result["causal_evolution_owned_by_action"]
    assert result["CAR_pairing_owned_by_action"]
    assert result["quasifree_state_datum"] == (
        "A_SELF_DUAL_CAR_CAUCHY_COVARIANCE_C_WITH_0_LE_C_LE_I_"
        "AND_C_PLUS_GAMMA_C_GAMMA=I"
    )
    assert result["self_dual_CAR_reality_constraint"] == (
        "C+Gamma*C*Gamma=I"
    )
    assert result["reset_compatibility_required"] == (
        "C_child=U_R*C_event*U_R_dagger"
    )
    assert not result["state_covariance_present_in_current_action"]
    assert not result[
        "new_continuous_temperature_or_Bogoliubov_coefficient_inserted"
    ]


def test_no_retained_candidate_silently_selects_a_feynman_state():
    result = retained_state_selector_audit()
    assert result["candidate_count"] == 9
    assert result["selected_candidate_count"] == 0
    assert not result["retained_action_selects_unique_Feynman_state"]
    assert result["arbitrary_vacuum_choice_forbidden"]
    assert all(not row["selects_state"] for row in result["rows"])


def test_claim_boundary_promotes_existence_class_not_physical_poles():
    result = claim_boundary()
    assert result["FINITE_CORE_CURRENT_C2_HADAMARD_STATE_CLASS_NONEMPTY_FAMILYWISE"]
    assert result[
        "STATE_DEPENDENT_FEYNMAN_TWO_POINT_DISTRIBUTION_EXISTS_FAMILYWISE"
    ]
    assert result["LOCAL_HADAMARD_SINGULARITY_CLASS_DERIVED"]
    assert not result["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"]
    assert not result["CURRENT_C2_ACTION_OWNED_FEYNMAN_TWO_POINT_FUNCTION_DERIVED"]
    assert not result["CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"]
    assert not result["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
    assert not result["MUON_MAGNETIC_MOMENT_DERIVED"]
    assert not result["particle_spectrum_rebuilt"]


def test_materialized_hadamard_state_class_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
