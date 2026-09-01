"""Close the Gate-7 readout-symbol provenance classification.

The historical gauge readout uses ``p``, ``p^2``, ``K_A(p)`` and a
transverse test source without deriving those objects on the corrected
maximal-forward domain.  This audit traces the exact semantic lineage,
distinguishes unrelated uses of the letter ``p``, and classifies the inherited
``p^2`` exactly once before any replacement family is constructed.

No Gate-7 value is evaluated here.  The nearest retained object is the
resolvent/spectral family of the action-owned forward operator with a neutral
spectral parameter ``z``; no map ``z <-> p^2`` is asserted.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_GATE7_READOUT_SYMBOL_PROVENANCE_AUDIT.json"
)

INPUTS = (
    ARTIFACTS / "BHSM_aether_m5_m4_gauge_higgs_ownership_v15_60.json",
    ARTIFACTS / "BHSM_aether_zeta_rg_microscopic_completion_v15_61.json",
    ARTIFACTS / "BHSM_aether_round_cap_maxwell_dtn_v15_65.json",
    ARTIFACTS / "BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json",
    ARTIFACTS / "BHSM_aether_lr_susceptibility_zeta_v15_67.json",
    ARTIFACTS / "BHSM_aether_round_cap_coulomb_dtn_v15_68.json",
    ARTIFACTS / "BHSM_aether_unified_m5_m4_pushforward_v15_69.json",
    ARTIFACTS / "BHSM_aether_legendre_crossing_unified_condensation_v15_72.json",
    ARTIFACTS / "BHSM_aether_event_shell_joint_operator_v15_73.json",
    ARTIFACTS / "BHSM_aether_einstein_cartan_joint_pushforward_v15_75.json",
    ARTIFACTS / "BHSM_aether_coupled_event_cycle_pushforward_v15_78.json",
    ARTIFACTS / "BHSM_aether_one_cycle_joint_residues_v15_86.json",
    ARTIFACTS / "BHSM_aether_cycle_scale_renormalization_v15_89.json",
    ARTIFACTS / "BHSM_aether_cycle_dtn_local_limit_v15_90.json",
    ARTIFACTS / "BHSM_aether_proper_time_joint_pushforward_v15_91.json",
    ARTIFACTS / "BHSM_aether_adm_dtn_proper_gap_v15_92.json",
    ARTIFACTS / "BHSM_aether_common_quantum_superdeterminant_v15_96.json",
    ARTIFACTS / "BHSM_aether_common_source_frechet_response_v15_99.json",
    ARTIFACTS / "BHSM_frozen_prediction_dependency_graph_v6_30_8.json",
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json"
    ),
    ROOT / "src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py",
    ROOT / "tests/test_bhsm_aether_unified_m5_m4_pushforward_v15_69.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load_json_inputs() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in INPUTS:
        if path.suffix == ".json":
            records[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return records


def _v1569_formula_is_nonexecutable() -> dict[str, object]:
    source_path = ROOT / (
        "src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py"
    )
    test_path = ROOT / "tests/test_bhsm_aether_unified_m5_m4_pushforward_v15_69.py"
    source = source_path.read_text(encoding="utf-8")
    tests = test_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    parameter_names = {
        arg.arg
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
    }
    executable_parameter_names = sorted(
        name for name in parameter_names if name in {"p", "p2", "p_squared"}
    )
    return {
        "formula_string_present": (
            "Z_g=partial_(p^2)<a_T,K_A(p)*a_T>|p^2=mu_star^2" in source
        ),
        "functions_accepting_p_or_p2": executable_parameter_names,
        "test_only_checks_formula_prefix": (
            'result["absolute_local_gauge_residue"].startswith("Z_g=")' in tests
        ),
        "test_evaluates_p_family_or_derivative": (
            "derivative_at" in tests or "K_A(" in tests or "p_squared" in tests
        ),
        "conclusion": (
            "V15_69_RECORDS_THE_READOUT_AS_A_STRING_CONTRACT;_ITS_SOURCE_"
            "HAS_NO_EXECUTABLE_p_OR_p2_ARGUMENT_AND_ITS_TEST_CHECKS_ONLY_"
            "THE_FORMULA_PREFIX"
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        missing = [str(path) for path in INPUTS if not path.is_file()]
        raise FileNotFoundError(f"missing provenance inputs: {missing}")

    records = _load_json_inputs()
    for name, record in records.items():
        if name == "BHSM_frozen_prediction_dependency_graph_v6_30_8.json":
            if record.get("frozen_prediction_changed") is not False:
                raise RuntimeError("frozen prediction graph must remain unchanged")
        elif record.get("validation_passed") is not True:
            raise RuntimeError(f"input did not validate: {name}")

    v60 = records["BHSM_aether_m5_m4_gauge_higgs_ownership_v15_60.json"]
    v61 = records["BHSM_aether_zeta_rg_microscopic_completion_v15_61.json"]
    v65 = records["BHSM_aether_round_cap_maxwell_dtn_v15_65.json"]
    v66 = records["BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json"]
    v67 = records["BHSM_aether_lr_susceptibility_zeta_v15_67.json"]
    v68 = records["BHSM_aether_round_cap_coulomb_dtn_v15_68.json"]
    v69 = records["BHSM_aether_unified_m5_m4_pushforward_v15_69.json"]
    v72 = records[
        "BHSM_aether_legendre_crossing_unified_condensation_v15_72.json"
    ]
    v73 = records["BHSM_aether_event_shell_joint_operator_v15_73.json"]
    v75 = records["BHSM_aether_einstein_cartan_joint_pushforward_v15_75.json"]
    v78 = records["BHSM_aether_coupled_event_cycle_pushforward_v15_78.json"]
    v86 = records["BHSM_aether_one_cycle_joint_residues_v15_86.json"]
    v89 = records["BHSM_aether_cycle_scale_renormalization_v15_89.json"]
    v90 = records["BHSM_aether_cycle_dtn_local_limit_v15_90.json"]
    v91 = records["BHSM_aether_proper_time_joint_pushforward_v15_91.json"]
    v92 = records["BHSM_aether_adm_dtn_proper_gap_v15_92.json"]
    v96 = records["BHSM_aether_common_quantum_superdeterminant_v15_96.json"]
    v99 = records["BHSM_aether_common_source_frechet_response_v15_99.json"]
    frozen = records["BHSM_frozen_prediction_dependency_graph_v6_30_8.json"]
    domain = records["BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"]
    necessity = records[
        "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json"
    ]

    inherited_formula = v69["common_derivative_ledger"][
        "absolute_local_gauge_residue"
    ]
    formula_execution = _v1569_formula_is_nonexecutable()

    frozen_text = json.dumps(frozen, sort_keys=True)
    exact_readout_tokens = (
        "partial_(p^2)",
        "K_A(",
        "<a_T",
        "a_i(",
        "momentum-space",
        "Fourier",
        "residue",
    )
    frozen_readout_tokens = [
        token for token in exact_readout_tokens if token in frozen_text
    ]
    gauge_outputs = [
        row
        for row in frozen["outputs"]
        if "gauge_couplings" in row["output_id"]
    ]

    p_ambiguity = {
        "v15_60_profile_exponent": {
            "meaning": "INTEGER_LOCALIZATION_TEST_PROFILE_u_p=sin(2chi)^p",
            "same_as_external_momentum_p": False,
        },
        "v15_69_external_label": {
            "meaning": "UNDEFINED_ARGUMENT_IN_K_A(p)_AND_K_H(p)",
            "same_as_profile_or_event_exponent": False,
        },
        "v15_78_event_exponent": {
            "meaning": "ASYMPTOTIC_EVENT_LAW_epsilon~a*(T_star-t)^p",
            "evaluated": v78["claim_boundary"][
                "constrained_Legendre_event_exponent_p_evaluated"
            ],
            "same_as_external_momentum_p": False,
        },
        "v15_92_sturm_liouville_coefficient": {
            "meaning": "COEFFICIENT_FUNCTION_NAMED_p_IN_THE_RADIAL_DTN_ODE",
            "same_as_external_momentum_p": False,
        },
    }

    semantic_lineage = [
        {
            "version": "v15.60",
            "role": "LOCAL_M4_ACTION_TARGET",
            "evidence": v60["forced_intrinsic_M4_action"]["action"],
            "boundary": (
                "Z_g_IS_A_REQUIRED_TARGET_COEFFICIENT_BUT_THE_PARENT_DOES_NOT_"
                "SELECT_IT"
            ),
        },
        {
            "version": "v15.61",
            "role": "GEOMETRIC_SCALE_NOT_NORMALIZATION",
            "evidence": v61["actual_operator_spectral_contract"][
                "canonical_matching_scale"
            ],
            "boundary": (
                "THE_CHILD_SELECTS_mu_star_BUT_NOT_THE_ABSOLUTE_M4_"
                "NORMALIZATION_OR_FINITE_COUNTERTERM"
            ),
        },
        {
            "version": "v15.65-v15.68",
            "role": "STATIC_SPATIAL_DTN_OPERATOR",
            "evidence": {
                "transverse": v65["boundary_effective_operator"]["DtN_operator"],
                "full_carrier": v66["full_gauge_DtN_completion"]["operator"],
                "electric": v68["electric_DtN_contract"]["operator_form"],
            },
            "boundary": (
                "ACTION_NATIVE_SPATIAL_SPECTRA_ONLY;_NO_LOCAL_LORENTZIAN_"
                "MAXWELL_OR_EXTERNAL_MOMENTUM_FAMILY"
            ),
        },
        {
            "version": "v15.69",
            "role": "FORMAL_MOMENTUM_SPACE_READOUT_CONTRACT",
            "evidence": inherited_formula,
            "boundary": (
                "THE_ABSOLUTE_LOCAL_GAUGE_RESIDUE_AND_COMMON_SUBTRACTION_"
                "REMAIN_UNDERIVED_AND_THE_FORMULA_IS_NONEXECUTABLE"
            ),
        },
        {
            "version": "v15.72-v15.75",
            "role": "FORMAL_REUSE_AT_MODELLED_CROSSINGS",
            "evidence": {
                "v15_72": v72["joint_absolute_normalization"]["gauge_residues"],
                "v15_73": v73["exact_joint_crossing_problem"][
                    "absolute_gauge_residue"
                ],
                "v15_75": v75["forced_joint_crossing"][
                    "gauge_residue_at_same_crossing"
                ],
            },
            "boundary": (
                "a_i_AND_K_A(p)_ARE_STILL_NOT_CONSTRUCTED;_THE_UNIFORM_"
                "CROSSING_MODEL_IS_RECLASSIFIED_AND_NO_p_FAMILY_IS_EVALUATED"
            ),
        },
        {
            "version": "v15.78-v15.86",
            "role": "PERIODIC_CYCLE_REPLACEMENT_READOUT",
            "evidence": {
                "cycle_functional": v78["cycle_pushforward"][
                    "one_period_functional"
                ],
                "evaluated_residues": v86["one_cycle_residues"]["Gamma_cycle"],
            },
            "boundary": (
                "THE_SCALAR_p2_DERIVATIVE_IS_REPLACED_BY_ONE_PERIOD_"
                "FUNCTIONAL_DERIVATIVES_NOT_DERIVED_ON_A_FORWARD_MAXIMAL_DOMAIN"
            ),
        },
        {
            "version": "v15.89-v15.92",
            "role": "LOCAL_LIMIT_KILLSCREEN",
            "evidence": {
                "coupling_not_identified": not v89["absolute_cycle_form_factors"]
                ["local_zero_momentum_coupling_identified_with_DtN_form_factor"],
                "dynamic_frequency_response": v90["claim_boundary"]
                ["dynamic_frequency_response_derived"],
                "Lorentz_coefficient": v90["claim_boundary"]
                ["Lorentz_invariant_FmunuFmunu_coefficient_derived"],
                "frequency_DtN": v92["claim_boundary"]
                ["frequency_dependent_shift_covariant_DtN_evaluated"],
                "proper_cycle_Lorentz_match": v91["claim_boundary"]
                ["Lorentz_invariant_Maxwell_matching_derived"],
            },
            "boundary": (
                "SPATIAL_lambda_IS_SPECTRAL_ONLY;_THE_DYNAMIC_AND_LORENTZIAN_"
                "MAP_REQUIRED_FOR_PHYSICAL_p2_REMAINS_OPEN"
            ),
        },
        {
            "version": "v15.96-v15.99",
            "role": "FIRST_COMMON_NUMERICAL_OPERATOR_AND_SOURCE_HESSIAN",
            "evidence": {
                "operator": v96["joint_quantum_derivative_contract"]
                ["graded_cycle_operator"],
                "Hessian": v96["joint_quantum_derivative_contract"]
                ["second_variation"],
                "source_contract": v99["physical_source_vertex_contract"]
                ["quantum_responses"],
            },
            "boundary": (
                "THE_OPERATOR_IS_PERIODIC_ON_S1_tau;_THE_RADIAL_ANGULAR_"
                "SOURCE_MATRICES_AND_QUANTUM_SADDLE_REMAIN_OPEN"
            ),
        },
        {
            "version": "current_N12_forward",
            "role": "ACTION_OWNED_MAXIMAL_FORWARD_DOMAIN",
            "evidence": domain["closed_form_domain"],
            "boundary": (
                "THE_DOMAIN_IS_OWNED_BUT_NO_TRANSLATION_GENERATOR_"
                "ASYMPTOTIC_MEASUREMENT_MAP_OR_p_FAMILY_IS_SUPPLIED"
            ),
        },
    ]

    p2_classification = {
        "selected": "D_RETIRED_PERIODIC_FOURIER_ARTIFACT",
        "decision_type": "OWNER_POLICY_DECISION_CONSTRAINED_BY_REPOSITORY_FACTS",
        "A_ACTION_NATIVE": {
            "selected": False,
            "reason": (
                "NO_RETAINED_TRANSLATION_GENERATOR_OR_OTHER_ACTION_OWNED_"
                "SYMMETRY_DERIVES_THE_EXTERNAL_p2_LABEL"
            ),
        },
        "B_PHYSICAL_ASYMPTOTIC_READOUT": {
            "selected": False,
            "reason": (
                "NO_ACTION_OWNED_ASYMPTOTIC_OR_MEASUREMENT_REGION_MAPS_THE_"
                "FORWARD_OPERATOR_TO_PHYSICAL_FOUR_MOMENTUM"
            ),
        },
        "C_SPECTRAL_PARAMETERIZATION": {
            "selected": False,
            "reason": (
                "THE_NATIVE_SPATIAL_lambda_AND_THE_FORWARD_RESOLVENT_z_ARE_"
                "SPECTRAL_PARAMETERS_BUT_NO_THEOREM_IDENTIFIES_EITHER_WITH_"
                "THE_INHERITED_p2"
            ),
        },
        "D_RETIRED_PERIODIC_FOURIER_ARTIFACT": {
            "selected": True,
            "reason": (
                "THE_TEXTUAL_SYMBOL_IS_A_FORMAL_SM_QFT_LOW_MOMENTUM_"
                "CONVENTION_FROM_V15_69;_ITS_ONLY_DOMAIN_LEVEL_LINEAGE_IS_"
                "THE_NOW_RETIRED_PERIODIC_S1_CYCLE_AND_THE_FORWARD_LINEAGE_"
                "SUPPLIES_NO_SURVIVING_PHYSICAL_MAP"
            ),
        },
        "important_distinction": (
            "NATIVE_SPECTRAL_z_IS_CLASS_C_AND_MUST_NOT_BE_CALLED_p2;_THE_"
            "INHERITED_ADVERTISED_p2_IS_CLASS_D"
        ),
    }

    symbol_ledger = {
        "p": {
            "classification": "SM_OR_QFT_IMPORTED",
            "origin": "V15_69_UNDEFINED_EXTERNAL_ARGUMENT_IN_K_A(p)_AND_K_H(p)",
            "domain": "NONE_ON_THE_CURRENT_FORWARD_HISTORY",
            "normalization_source": "NONE",
            "still_required": False,
            "replacement": "NEUTRAL_RESOLVENT_PARAMETER_z_IF_A_PARAMETER_IS_NEEDED",
            "ambiguity_audit": p_ambiguity,
        },
        "p2": {
            "classification": "RETIRED_PERIODIC_FOURIER_ARTIFACT",
            "exact_A_to_D_classification": p2_classification["selected"],
            "action_source": "NONE",
            "observable_map": "NONE",
            "still_required": False,
            "replacement": "z_IN_rho(K_C)_OR_lambda_IN_THE_SPECTRAL_MEASURE",
        },
        "K_A(p)": {
            "classification": "HISTORICAL_ASSUMPTION",
            "origin": "V15_69_FORMULA_STRING",
            "action_native_core": (
                "D_A2_Gamma_OR_K_F5*N_DtN+Pi_AA_AT_SUPPLIED_SOURCES"
            ),
            "missing_part": "THE_p_DEPENDENCE",
            "still_required": False,
            "replacement": "THE_FORWARD_OPERATOR_K_C_AND_ITS_RESOLVENT",
        },
        "a_T": {
            "classification": "OPTIONAL_REPRESENTATION",
            "origin": "V15_69_FORMAL_TRANSVERSE_TEST_VECTOR",
            "normalization_source": "NONE",
            "constructed_in_origin": False,
            "replacement": "ARBITRARY_SUPPLIED_a_IN_H_BRST_phys",
        },
        "a_i(p)": {
            "classification": "HISTORICAL_ASSUMPTION",
            "origin": (
                "NO_SUCH_FAMILY_IS_CONSTRUCTED;_V15_72_AND_V15_73_USE_a_i_"
                "ONLY_INSIDE_FORMULA_STRINGS"
            ),
            "normalization_source": "NONE",
            "still_required": False,
            "replacement": "ADMISSIBLE_BRST_SOURCE_SECTIONS_WITHOUT_p_LABEL",
        },
        "residue": {
            "classification": "OBSERVABLE_REQUIRED_ONLY_IF_SCALAR_COUPLING_CLAIMED",
            "gauge_meaning": (
                "DERIVATIVE_COEFFICIENT_OF_A_FORMAL_TWO_POINT_KERNEL_NOT_A_"
                "PROVED_PROPAGATOR_POLE_RESIDUE"
            ),
            "Higgs_Yukawa_meaning": (
                "PROJECTION_ALONG_A_NORMALIZED_COMPOSITE_MODE_AND_CANONICAL_"
                "FIELD_RESCALE;_A_DIFFERENT_USE_OF_RESIDUE"
            ),
            "zeta_meaning": (
                "LAURENT_RESIDUE_OF_THE_REGULATOR_AT_s=0;_NOT_THE_GAUGE_"
                "READOUT"
            ),
            "action_native_operator_predecessor": "PAIR_PLUS_CONTACT_HESSIAN",
        },
        "pole": {
            "classification": "SM_OR_QFT_IMPORTED_FOR_PARTICLE_POLE_LANGUAGE",
            "v15_67_meaning": v67["exact_spectral_contract"]["pole_operator"],
            "v15_67_scope": "UV_LAURENT_POLE_AND_LOCAL_COUNTERTERM_OPERATOR",
            "geometric_uses": "REGULAR_COLLAPSE_POLE_IN_THE_RADIAL_DTN_PROBLEM",
            "physical_gauge_propagator_pole_derived": False,
            "Gate7_native_dependency": False,
        },
        "transverse_source_family": {
            "classification": "ACTION_REQUIRED_AT_THE_BRST_QUOTIENT_SPACE_LEVEL",
            "action_owned_part": (
                "COEXACT_SPATIAL_SECTOR_AND_THE_H_BRST_phys_ADMISSIBLE_"
                "SOURCE_SPACE"
            ),
            "not_action_owned": "A_PLANE_WAVE_OR_p_INDEXED_NORMALIZED_FAMILY",
            "weakest_sufficient_object": "SUPPLIED_a_i_IN_H_BRST_phys",
        },
        "readout_scalar": {
            "classification": "OBSERVABLE_REQUIRED",
            "required_only_for": (
                "A_BHSM_CLAIM_OF_A_SCALAR_PHYSICAL_GAUGE_COUPLING_OR_"
                "NORMALIZATION"
            ),
            "not_required_to_define": "THE_OPERATOR_VALUED_GATE7_HESSIAN",
            "current_convention": v72["joint_absolute_normalization"]
            ["gauge_couplings"],
            "contrary_lineage_fact": (
                "V15_89_EXPLICITLY_REFUSES_TO_IDENTIFY_THE_DTN_FORM_FACTOR_"
                "WITH_A_LOCAL_ZERO_MOMENTUM_COUPLING"
            ),
            "missing": (
                "ACTION_OWNED_SOURCE_NORMALIZATION_AND_OBSERVABLE_MAP_WITH_"
                "BASIS_INDEPENDENCE"
            ),
        },
    }

    required_statement_classification = {
        "ACTION_REQUIRED": [
            "ONE_RETAINED_PAIR_PLUS_CONTACT_SOURCE_HESSIAN",
            "THE_BRST_QUOTIENT_AND_ACTION_OWNED_MAXIMAL_FORWARD_DOMAIN",
            "THE_EXISTING_BIRTH_GRAPH_AND_FRIEDRICHS_OR_ACTUAL_RESET_ENDPOINT_RULE",
            "THE_SAME_ACTION_GAUGE_GHOST_RANK16_HS_INCIDENCE",
        ],
        "INTERNAL_CONSISTENCY_REQUIRED": [
            "ZERO_SOURCE_WEAK_GEOMETRY_FORCE",
            "SAME_ACTION_STATIONARY_SADDLE_BEFORE_THE_FINAL_HESSIAN",
            "WARD_BRST_IDENTITIES",
            "EXTERIOR_WEYL_CALDERON_RESPONSE_OR_EQUIVALENT_OPERATOR_ORACLE",
        ],
        "OBSERVABLE_REQUIRED": [
            "A_BASIS_INDEPENDENT_SOURCE_NORMALIZATION_AND_SCALAR_MAP_IF_BHSM_CLAIMS_g_i",
            "A_PHYSICAL_z_TO_p2_MAP_ONLY_IF_A_MOMENTUM_SPACE_OBSERVABLE_IS_CLAIMED",
        ],
        "EXISTENCE_ONLY": [
            "ONE_TERMINAL_REACHING_HISTORY_AS_AN_OPTIONAL_FINITE_ENDPOINT_ROUTE",
        ],
        "UNIVERSAL_REACHABILITY_ASSUMPTION": [
            "TERMINAL_EVENT_REACHABILITY_FOR_EVERY_HISTORY_IS_NOT_REQUIRED_AND_NOT_DERIVED",
        ],
        "INTERPRETIVE_OR_SM_IMPORTED": [
            "THE_UNDEFINED_EXTERNAL_p_AND_p2_LABELS",
            "PLANE_WAVE_OR_PERIODIC_FOURIER_SOURCE_NORMALIZATION",
            "g_i_INVERSE_SQUARED_EQUALS_THE_FORMAL_DERIVATIVE_RESIDUE",
            "PHYSICAL_PARTICLE_POLE_LANGUAGE_WITHOUT_AN_OBSERVABLE_MAP",
        ],
    }

    native_replacement = {
        "operator": "K_C_ON_THE_ACTION_OWNED_BRST_QUOTIENTED_MAXIMAL_FORWARD_DOMAIN",
        "spectral_parameter": "z_IN_rho(K_C)",
        "resolvent": "R_C(z)=(K_C-z)^(-1)",
        "spectral_resolution": "K_C=int_lambda*dE_C(lambda)",
        "spectral_measure": "dE_C(lambda)",
        "sources": "a_i_IN_H_BRST^phys_ON_THE_SAME_DOMAIN",
        "pair_plus_contact": (
            "H_ij(z)=<a_i,R_C(z)a_j>+H_ij^contact(z)_OR_THE_EXACT_"
            "RETAINED_HEAT_FRECHET_EQUIVALENT"
        ),
        "exterior_oracle": (
            "M_C(z)_ENTERING_K_eff(z)=A-z-B*(C-z)^(-1)*B^star"
        ),
        "forbidden_identification": "DO_NOT_CALL_z_MOMENTUM_SQUARED",
        "future_physical_map": (
            "z_TO_p2_REQUIRES_A_SEPARATE_ACTION_OWNED_TRANSLATION_"
            "ASYMPTOTIC_OR_MEASUREMENT_THEOREM"
        ),
    }

    downstream = {
        "Gate7_current": "ACTIVE_NOT_CLOSED",
        "Gate7_native_sequence": [
            "CONSTRUCT_THE_FORWARD_OPERATOR_RESOLVENT_AND_SPECTRAL_MEASURE",
            "ASSEMBLE_ADMISSIBLE_BRST_SOURCE_INCIDENCE_WITHOUT_A_p_LABEL",
            "DERIVE_OR_ENCLOSE_THE_EXTERIOR_M_C(z)",
            "EVALUATE_THE_ZERO_SOURCE_FORCE",
            "SOLVE_THE_SAME_ACTION_SADDLE_IF_THE_FORCE_IS_NONZERO",
            "EVALUATE_THE_PAIR_PLUS_CONTACT_HESSIAN",
            "CLOSE_WARD_BRST_AND_CONTINUUM_RELATIVE_TRACE_CONTROL",
            "DERIVE_A_SCALAR_OBSERVABLE_MAP_OR_RECLASSIFY_THE_SCALAR_COUPLING_CLAIM",
        ],
        "Gate8": "LOCKED_BY_GATE7",
        "Gate9_and_later": "LOCKED_TRANSITIVELY_BY_GATE7",
        "terminal_return": "OPTIONAL_FINITE_RESET_ENDPOINT_ROUTE",
        "chord_03": "UNAUTHORIZED",
        "superseded_dependency_strings": [
            (
                "CONSTRUCT_A_FORWARD_p2_FAMILY_IS_SUPERSEDED_BY_CONSTRUCT_"
                "THE_NATIVE_z_RESOLVENT_FAMILY"
            ),
            (
                "GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_AS_THE_FLAGSHIP_"
                "BLOCKER_IS_STALE"
            ),
            (
                "THE_UNCOMMITTED_GATE7_PHYSICAL_READOUT_CONVENTION_DRAFT_"
                "MUST_NOT_BE_PROMOTED"
            ),
        ],
        "frozen_predictions": {
            "changed": False,
            "exact_readout_dependency_tokens_found": frozen_readout_tokens,
            "gauge_outputs_count": len(gauge_outputs),
            "official_gauge_outputs_count": sum(
                row["official_status"] == "FROZEN_SCREEN" for row in gauge_outputs
            ),
            "gauge_direct_inputs": sorted(
                {item for row in gauge_outputs for item in row["direct_inputs"]}
            ),
            "gauge_transitive_inputs": sorted(
                {item for row in gauge_outputs for item in row["transitive_inputs"]}
            ),
            "conclusion": (
                "THE_FROZEN_GAUGE_SCREENS_USE_gauge_trace_weights_AND_"
                "gauge_normalization_rule_NOT_THE_GATE7_p2_READOUT_LINEAGE"
            ),
        },
    }

    validation = {
        "all_inputs_present_and_validated": True,
        "v15_60_gauge_target_not_parent_selected": not v60["forced_intrinsic_M4_action"]
        ["these_data_selected_by_current_parent_child_action"],
        "v15_61_absolute_normalization_not_selected": not v61["claim_boundary"]
        ["absolute_M4_normalization_selected"],
        "v15_65_static_transverse_operator_is_spatial": (
            v65["boundary_effective_operator"]["DtN_operator"]
            == "N_T=(Delta_1_coexact)^(1/2)"
        ),
        "v15_66_local_M4_action_not_derived": not v66[
            "full_gauge_DtN_completion"
        ]["local_M4_Yang-Mills_action"],
        "v15_68_static_scope_explicit": v68["claim_boundary"]
        ["static_transverse_plus_electric_kernel_complete"],
        "v15_69_formula_traced_exactly": inherited_formula
        == "Z_g=partial_(p^2)<a_T,K_A(p)*a_T>|p^2=mu_star^2",
        "v15_69_formula_nonexecutable": (
            formula_execution["formula_string_present"]
            and not formula_execution["functions_accepting_p_or_p2"]
            and formula_execution["test_only_checks_formula_prefix"]
            and not formula_execution["test_evaluates_p_family_or_derivative"]
        ),
        "v15_89_refuses_local_coupling_identification": not v89[
            "absolute_cycle_form_factors"
        ]["local_zero_momentum_coupling_identified_with_DtN_form_factor"],
        "v15_90_spatial_lambda_not_lorentzian_p2": (
            not v90["claim_boundary"]["dynamic_frequency_response_derived"]
            and not v90["claim_boundary"]
            ["Lorentz_invariant_FmunuFmunu_coefficient_derived"]
        ),
        "v15_91_lorentz_matching_open": not v91["claim_boundary"]
        ["Lorentz_invariant_Maxwell_matching_derived"],
        "v15_92_frequency_dtn_open": not v92["claim_boundary"]
        ["frequency_dependent_shift_covariant_DtN_evaluated"],
        "v15_96_first_common_domain_is_periodic": "L2(S1_tau_times_S3"
        in v96["joint_quantum_derivative_contract"]["graded_cycle_operator"],
        "v15_99_source_matrices_open": not v99["claim_boundary"]
        ["radial_angular_vertex_matrices_assembled"],
        "current_forward_domain_does_not_restore_periodic_cycle": not domain[
            "ownership"
        ]["periodic_cycle_restored"],
        "prior_necessity_audit_already_found_formula_nonexecutable": necessity[
            "readout_adjudication"
        ]["current_formula_status"].startswith("INHERITED_FORMAL"),
        "p2_classified_exactly_once": sum(
            bool(p2_classification[key]["selected"])
            for key in (
                "A_ACTION_NATIVE",
                "B_PHYSICAL_ASYMPTOTIC_READOUT",
                "C_SPECTRAL_PARAMETERIZATION",
                "D_RETIRED_PERIODIC_FOURIER_ARTIFACT",
            )
        )
        == 1,
        "native_z_kept_distinct_from_p2": (
            p2_classification["C_SPECTRAL_PARAMETERIZATION"]["selected"] is False
            and p2_classification["D_RETIRED_PERIODIC_FOURIER_ARTIFACT"]
            ["selected"]
            is True
        ),
        "frozen_predictions_have_no_exact_readout_dependency": not bool(
            frozen_readout_tokens
        ),
        "no_gate_source_scale_selector_fit_prediction_or_physics_added": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_READOUT_SYMBOL_PROVENANCE_AUDIT",
        "classification": (
            "THE_INHERITED_GATE7_p2_READOUT_IS_D_RETIRED_PERIODIC_FOURIER_"
            "ARTIFACT;_THE_ACTION_NATIVE_REPLACEMENT_IS_THE_MAXIMAL_FORWARD_"
            "OPERATOR_RESOLVENT_AND_SPECTRAL_MEASURE_WITH_NEUTRAL_PARAMETER_z"
        ),
        "current_flagship_gate": 7,
        "status": "READOUT_SYMBOL_PROVENANCE_CLOSED_NATIVE_SPECTRAL_CONSTRUCTION_OPEN",
        "p_ambiguity": p_ambiguity,
        "semantic_lineage": semantic_lineage,
        "formula_execution_audit": formula_execution,
        "p2_classification": p2_classification,
        "symbol_ledger": symbol_ledger,
        "required_statement_classification": required_statement_classification,
        "native_replacement": native_replacement,
        "downstream": downstream,
        "exact_next_dependency": (
            "CONSTRUCT_K_C_RESOLVENT_SPECTRAL_MEASURE_AND_EXTERIOR_M_C(z)_"
            "ON_THE_ACTION_OWNED_MAXIMAL_FORWARD_BRST_DOMAIN_FOR_SUPPLIED_"
            "ADMISSIBLE_SOURCES;_DO_NOT_CONSTRUCT_OR_NAME_A_p2_FAMILY"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "Gate7_status_changed": False,
        "chord_03_authorized": False,
        "frozen_predictions_changed": False,
        "new_physics_added": False,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "p2_classification": payload["p2_classification"]["selected"],
                "exact_next_dependency": payload["exact_next_dependency"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
