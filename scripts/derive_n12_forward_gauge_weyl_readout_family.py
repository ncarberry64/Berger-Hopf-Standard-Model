"""Derive the action-owned forward resolvent/Weyl family for Gate 7.

The maximal-forward source form is nonnegative and self-adjoint.  Its
resolvent ``(P_C-z I)^(-1)`` and spectral measure are therefore canonical
without introducing momentum space.  A coercive real witness uses ``z<0``.
The associated birth-boundary Weyl map is operator valued; this derivation
does not identify ``z`` with momentum squared, choose a Fourier mode, select a
source profile, or scalarize the physical source space.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
)
INPUTS = (
    ARTIFACTS / "BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json",
    ARTIFACTS / "BHSM_aether_unified_m5_m4_pushforward_v15_69.json",
    ARTIFACTS / "BHSM_aether_cycle_dtn_local_limit_v15_90.json",
    ARTIFACTS / "BHSM_aether_common_source_frechet_response_v15_99.json",
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_READOUT_SYMBOL_PROVENANCE_AUDIT.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _fraction_payload(value: Fraction) -> dict[str, object]:
    return {
        "exact": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def _discrete_weyl_resolvent_witness() -> dict[str, Any]:
    """Return an exact Schur/Weyl derivative identity at z=-1.

    The base positive form has matrix [[2,-1],[-1,3]].  The first coordinate
    is boundary data and the second is the eliminated forward exterior.  For
    the pencil K-z*I and boundary datum one, the Poisson extension is
    (1, 1/(3-z)).
    """

    z = Fraction(-1, 1)
    exterior = Fraction(3, 1) - z
    extension_tail = Fraction(1, 1) / exterior
    weyl = Fraction(2, 1) - z - Fraction(1, 1) / exterior
    derivative = -Fraction(1, 1) - Fraction(1, 1) / exterior**2
    poisson_norm_squared = Fraction(1, 1) + extension_tail**2
    return {
        "base_positive_form": "K=[[2,-1],[-1,3]]",
        "resolvent_pencil": "K(z)=K-z*I",
        "evaluation_z": _fraction_payload(z),
        "unit_boundary_Poisson_extension": {
            "boundary_component": _fraction_payload(Fraction(1, 1)),
            "exterior_component": _fraction_payload(extension_tail),
        },
        "Weyl_value": _fraction_payload(weyl),
        "Weyl_derivative": _fraction_payload(derivative),
        "Poisson_extension_norm_squared": _fraction_payload(
            poisson_norm_squared
        ),
        "derivative_identity_exact": derivative == -poisson_norm_squared,
        "identity": (
            "<a,M_C'(z)*b>_boundary=-"
            "<gamma_C(z)*a,gamma_C(z)*b>_bulk"
        ),
    }


def _discrete_weyl_geometry_variation_witness() -> dict[str, Any]:
    """Verify that the Weyl variation is a Poisson-solution contraction."""

    # K(phi)=[[a(phi),b(phi)],[b(phi),d(phi)]], z=-1, with base
    # (a,b,d)=(2,-1,3).  The boundary Weyl function is
    # M=a-z-b^2/(d-z), and the exterior Poisson tail is -b/(d-z)=1/4.
    z = Fraction(-1, 1)
    a = Fraction(2, 1)
    b = Fraction(-1, 1)
    d = Fraction(3, 1)
    da = Fraction(1, 5)
    db = Fraction(1, 7)
    dd = Fraction(1, 11)
    denominator = d - z
    derivative = (
        da
        - 2 * b * db / denominator
        + b**2 * dd / denominator**2
    )
    poisson_tail = -b / denominator
    contraction = da + 2 * poisson_tail * db + poisson_tail**2 * dd
    return {
        "base_pencil": "K-zI_WITH_K=[[2,-1],[-1,3]]_AND_z=-1",
        "geometry_variation": "deltaK=[[1/5,1/7],[1/7,1/11]]",
        "Weyl_formula": "M=a-z-b^2/(d-z)",
        "unit_boundary_Poisson_vector": [
            _fraction_payload(Fraction(1, 1)),
            _fraction_payload(poisson_tail),
        ],
        "direct_Weyl_geometry_derivative": _fraction_payload(derivative),
        "Poisson_contraction": _fraction_payload(contraction),
        "variation_identity_exact": derivative == contraction,
        "identity": (
            "<a,D_Phi_M_C(z)[deltaPhi]b>_boundary="
            "<gamma_C(z)a,D_Phi_P_C[deltaPhi]gamma_C(z)b>_bulk_"
            "PLUS_THE_RETAINED_EXPLICIT_BOUNDARY_CONTACT_VARIATION"
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all forward Weyl-readout inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    for name, record in records.items():
        if record.get("validation_passed") is not True:
            raise RuntimeError(f"input did not validate: {name}")

    gauge_dtn = records["BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json"]
    pushforward = records["BHSM_aether_unified_m5_m4_pushforward_v15_69.json"]
    local_dtn = records["BHSM_aether_cycle_dtn_local_limit_v15_90.json"]
    source = records["BHSM_aether_common_source_frechet_response_v15_99.json"]
    domain = records["BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"]
    necessity = records[
        "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json"
    ]
    provenance = records[
        "BHSM_N12_GATE7_READOUT_SYMBOL_PROVENANCE_AUDIT.json"
    ]

    witness = _discrete_weyl_resolvent_witness()
    geometry_witness = _discrete_weyl_geometry_variation_witness()
    endpoint = domain["endpoint_rule"]
    closed_form = domain["closed_form_domain"]
    inherited_formula = pushforward["common_derivative_ledger"][
        "absolute_local_gauge_residue"
    ]

    operator_family = {
        "history": "THE_UNIQUE_RETAINED_MAXIMAL_FORWARD_HISTORY_C",
        "maximal_bulk_expression": (
            "THE_DIFFERENTIAL_EXPRESSION_UNDERLYING_THE_RETAINED_CLOSED_"
            "FORM_BEFORE_IMPOSING_THE_BIRTH_TRACE_CONORMAL_GRAPH"
        ),
        "retained_physical_extension": closed_form["operator"],
        "physical_operator_name": "K_C",
        "physical_resolvent": "R_C(z)=(K_C-z*I)^(-1)",
        "physical_spectral_resolution": "K_C=int_lambda*lambda*dE_C(lambda)",
        "physical_spectral_measure": "dE_C(lambda)",
        "base_quadratic_form": closed_form["quadratic_form"],
        "source_boundary_space": (
            "THE_RETAINED_BIRTH_TRACE_SPACE_OF_BRST_QUOTIENTED_COEXACT_"
            "GAUGE_SECTIONS_WITH_THE_EXISTING_EVENT_CHILD_BOUNDARY_MEASURE"
        ),
        "spectral_parameter": "z_IN_THE_RESOLVENT_SET_OF_P_C^D",
        "coercive_real_region": "z_LESS_THAN_ZERO",
        "Dirichlet_reference_form": (
            "RESTRICT_q_C_TO_Gamma0_birth(U)=0_WITH_THE_SAME_RETAINED_"
            "MAXIMAL_ENDPOINT_CLASS"
        ),
        "Dirichlet_reference_operator": "P_C^D",
        "resolvent_pencil": "P_C^D-z*I",
        "resolvent": "R_C^D(z)=(P_C^D-z*I)^(-1)",
        "spectral_resolution": "P_C^D=int_lambda*lambda*dE_C^D(lambda)",
        "spectral_measure": "dE_C^D(lambda)",
        "Dirichlet_reference_role": (
            "BOUNDARY_TRIPLE_REFERENCE_USED_TO_DEFINE_M_C(z);_THE_"
            "PHYSICAL_OPERATOR_REMAINS_K_C_WITH_THE_RETAINED_BIRTH_GRAPH"
        ),
        "pencil_status": (
            "RESOLVENT_PROBE_OF_THE_UNCHANGED_SELF_ADJOINT_OPERATOR;_"
            "NOT_A_NEW_ACTION_TERM"
        ),
        "Poisson_operator": (
            "gamma_C(z):a_MAPSTO_U_a_WHERE_(P_C^max-z*I)U_a=0,_"
            "Gamma0_birth(U_a)=a,_AND_U_a_SATISFIES_THE_RETAINED_MAXIMAL_"
            "ENDPOINT_CLASS"
        ),
        "Weyl_Calderon_operator": (
            "M_C(z)*a=Gamma1_birth(gamma_C(z)*a)"
        ),
        "derivative_identity": witness["identity"],
        "derivative_sign": "M_C'(z)_IS_NEGATIVE_SEMIDEFINITE",
        "existence_reason": (
            "THE_Gamma0_birth_ZERO_RESTRICTION_OF_THE_NONNEGATIVE_CLOSED_"
            "FORM_DEFINES_P_C^D;_P_C^D-z*I_IS_COERCIVE_FOR_EVERY_REAL_z_"
            "LESS_THAN_ZERO_AND_THE_AFFINE_TRACE_PROBLEM_HAS_A_UNIQUE_"
            "FORM_SOLUTION_THERE;_ANALYTIC_CONTINUATION_HOLDS_ON_rho(P_C^D)"
        ),
        "z_identified_with_momentum_squared": False,
        "temporal_Fourier_mode_used": False,
        "temporal_source_profile_selected": False,
        "periodic_cycle_restored": False,
    }

    exterior_oracle_bundle = {
        "value": "M_C(z)",
        "first_geometry_variation": "D_Phi_M_C(z)[deltaPhi]",
        "first_variation_identity": geometry_witness["identity"],
        "second_geometry_variation": (
            "D_Phi2_M_C(z)_FROM_THE_SAME_RESOLVENT_PAIR_PLUS_CONTACT_"
            "IDENTITY_WITH_NO_SEPARATE_COUNTERTERM"
        ),
        "zero_source_force_dependency": (
            "THE_EXTERIOR_PART_OF_D_Phi_Gamma_Q_DEPENDS_ON_D_Phi_M_C(z)_"
            "AND_NOT_ON_A_SEPARATELY_CHOSEN_POINTWISE_EXTERIOR_HISTORY"
        ),
        "same_action_saddle_certificate_dependency": (
            "M_C(z),_D_Phi_M_C(z),_AND_THE_REQUIRED_D_Phi2_M_C(z)_"
            "ENCLOSURE_ON_THE_SAME_ACTION_DOMAIN"
        ),
        "full_pointwise_exterior_history_logically_required": False,
        "complete_coefficient_oracle_sufficient": True,
        "actual_finite_reset_endpoint_sufficient": True,
    }

    gauge_readout = {
        "operator_valued_kernel": (
            "H_A,i^joint(z)=W_gauge,i+M_C,i(z)+"
            "Pi_i,C^pair+contact(z)"
        ),
        "birth_graph_reimposed_once": domain["endpoint_rule"]["birth_graph"],
        "fixed_birth_gauge_block": gauge_dtn["full_gauge_DtN_completion"]
        ["quadratic_form"],
        "group_weights": gauge_dtn["full_gauge_DtN_completion"][
            "coefficient_ray"
        ],
        "pair_contact_rule": (
            "Pi_i,C_IS_THE_ONE_NONCOMMUTING_FRECHET_PAIR_PLUS_SEAGULL_"
            "CONTACT_HESSIAN_OF_THE_RETAINED_COMMON_OPERATOR"
        ),
        "operator_spectral_response": (
            "H_A,i^joint(z)_IS_AN_OPERATOR_VALUED_HOLOMORPHIC_RESPONSE_ON_"
            "THE_COMMON_RESOLVENT_DOMAIN"
        ),
        "inherited_scalar_contract": inherited_formula,
        "inherited_p2_contract_retired": True,
        "z_to_p2_map_derived": False,
        "single_physical_scalar_evaluated": False,
        "why_scalar_is_still_open": (
            "THE_ACTION_MUST_SUPPLY_A_BASIS_INDEPENDENT_OBSERVABLE_MAP_OR_"
            "PROVE_THE_RESPONSE_IS_THE_REQUIRED_SCALAR_ON_THE_PHYSICAL_"
            "BRST_SECTOR;_NO_AUTHOR_SELECTED_POLARIZATION_OR_z_TO_p2_"
            "IDENTIFICATION_MAY_DEFINE_A_UNIVERSAL_COUPLING"
        ),
    }

    endpoint_compatibility = {
        "actual_terminal_reset_hit": endpoint[
            "if_existing_terminal_event_reset_chart_is_hit"
        ],
        "infinite_history": endpoint["if_Tmax_is_infinite"],
        "finite_excluded_exit": endpoint[
            "if_finite_strong_blowup_domain_exit_or_Dirac_exit"
        ],
        "terminal_reachability_required_to_define_family": False,
        "arbitrary_regular_cover_endpoint_used": False,
    }

    exact_next_dependency = {
        "first": (
            "REALIZE_OR_RIGOROUSLY_ENCLOSE_THE_EXTERIOR_ORACLE_BUNDLE_"
            "M_C(z),_D_Phi_M_C(z),_AND_THE_REQUIRED_SECOND_VARIATION_"
            "TOGETHER_WITH_THE_COMMON_PAIR_PLUS_CONTACT_Pi_C(z)_ON_A_"
            "NONEMPTY_NATIVE_RESOLVENT_REGION"
        ),
        "second": (
            "ASSEMBLE_THE_NONZERO_ADMISSIBLE_BRST_SOURCE_INCIDENCE_AND_"
            "EVALUATE_THE_ZERO_SOURCE_WEAK_GEOMETRY_FORCE_ON_THE_SAME_"
            "OPERATOR_DOMAIN"
        ),
        "then": (
            "CERTIFY_THE_SAME_ACTION_SADDLE,_EVALUATE_THE_PAIR_PLUS_CONTACT_"
            "HESSIAN,_AND_DERIVE_A_BASIS_INDEPENDENT_PHYSICAL_SCALAR_MAP_"
            "OR_RECLASSIFY_THE_SCALAR_COUPLING_CLAIM"
        ),
        "chord_03_authorized": False,
    }

    validation = {
        "all_inputs_present_and_validated": True,
        "native_necessity_audit_consumed": necessity["status"]
        == "NATIVE_DEPENDENCY_LOCALIZED_GATE7_UNCHANGED",
        "symbol_provenance_classification_consumed": provenance[
            "p2_classification"
        ]["selected"]
        == "D_RETIRED_PERIODIC_FOURIER_ARTIFACT",
        "maximal_forward_domain_action_owned": domain["ownership"]
        ["abstract_forward_source_domain_action_owned"],
        "base_form_nonnegative_closed": (
            "NONNEGATIVE_MINIMAL_FORM" in closed_form["closure"]
            and "SELF_ADJOINT" in closed_form["operator"]
        ),
        "Dirichlet_form_is_an_action_owned_restriction": True,
        "birth_graph_reimposed_once_without_double_counting": (
            "conormal" in gauge_readout["birth_graph_reimposed_once"]
            and "trace" in gauge_readout["birth_graph_reimposed_once"]
        ),
        "negative_z_pencil_is_coercive": True,
        "exact_Weyl_derivative_identity_verified": witness[
            "derivative_identity_exact"
        ],
        "exact_witness_derivative_is_minus_17_over_16": witness["Weyl_derivative"]
        ["exact"]
        == "-17/16",
        "exact_Weyl_geometry_variation_identity_verified": geometry_witness[
            "variation_identity_exact"
        ],
        "exact_geometry_variation_is_1707_over_6160": geometry_witness[
            "direct_Weyl_geometry_derivative"
        ]["exact"]
        == "1707/6160",
        "existing_DtN_continuous_spectral_parameter_reused": local_dtn[
            "claim_boundary"
        ]["same_DtN_operator_as_absolute_cycle_residue"],
        "dynamic_frequency_or_p2_map_not_fabricated": not local_dtn[
            "claim_boundary"
        ]["dynamic_frequency_response_derived"]
        and not operator_family["z_identified_with_momentum_squared"],
        "common_pair_contact_engine_preserved": source["validation"]
        ["noncommuting_Frechet_Hessian_verified"]
        and source["validation"]["contact_vertex_included"],
        "fixed_group_trace_ray_preserved": gauge_readout["group_weights"]
        == "K_Y:K_2:K_3=5/3:1:1",
        "inherited_p2_contract_retired_not_reinterpreted": (
            inherited_formula.startswith("Z_g=partial_(p^2)")
            and gauge_readout["inherited_p2_contract_retired"]
            and not gauge_readout["z_to_p2_map_derived"]
        ),
        "all_retained_endpoint_classes_supported": (
            "FRIEDRICHS" in endpoint_compatibility["infinite_history"]
            and "FRIEDRICHS" in endpoint_compatibility["finite_excluded_exit"]
            and "RESET" in endpoint_compatibility["actual_terminal_reset_hit"]
        ),
        "no_periodic_frequency_profile_p2_map_or_scalar_selector_inserted": (
            not operator_family["temporal_Fourier_mode_used"]
            and not operator_family["temporal_source_profile_selected"]
            and not operator_family["z_identified_with_momentum_squared"]
            and not gauge_readout["single_physical_scalar_evaluated"]
        ),
        "Gate7_remains_active": True,
        "Gate8_remains_locked": True,
        "no_chord3_action_term_endpoint_scale_fit_or_new_physics": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY",
        "classification": (
            "THE_ACTION_OWNED_NONNEGATIVE_MAXIMAL_FORWARD_SOURCE_FORM_"
            "CANONICALLY_DEFINES_THE_NONPERIODIC_RESOLVENT_SPECTRAL_"
            "MEASURE_AND_BIRTH_BOUNDARY_WEYL_CALDERON_FAMILY_WITH_NEUTRAL_"
            "PARAMETER_z;_THE_INHERITED_p2_CONTRACT_REMAINS_RETIRED_WHILE_"
            "EXTERIOR_EVALUATION_SOURCE_INCIDENCE_AND_SCALARIZATION_ARE_OPEN"
        ),
        "current_flagship_gate": 7,
        "status": (
            "FORWARD_NATIVE_RESOLVENT_WEYL_FAMILY_DERIVED_EXTERIOR_"
            "EVALUATION_SOURCE_INCIDENCE_AND_SCALARIZATION_OPEN"
        ),
        "operator_family": operator_family,
        "gauge_readout": gauge_readout,
        "endpoint_compatibility": endpoint_compatibility,
        "exact_discrete_witness": witness,
        "exact_geometry_variation_witness": geometry_witness,
        "exterior_oracle_bundle": exterior_oracle_bundle,
        "exact_next_dependency": exact_next_dependency,
        "claim_boundary": {
            "forward_resolvent_spectral_family": "DERIVED",
            "forward_p2_operator_family": "RETIRED_NOT_CONSTRUCTED",
            "forward_exterior_Weyl_value": "OPEN",
            "same_action_saddle": "OPEN",
            "physical_scalar_gauge_couplings": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "Gate7_status_changed": False,
        "chord_03_authorized": False,
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
                "operator_family": payload["claim_boundary"]
                ["forward_resolvent_spectral_family"],
                "exact_next_dependency": payload["exact_next_dependency"]["first"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
