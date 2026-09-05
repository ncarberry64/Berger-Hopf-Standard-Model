"""Representation theorem for the still-unselected encapsulation response.

This module deliberately does not choose an encapsulation carrier or response
law.  It records the strongest representation-theoretic statement available
from the retained BHSM boundary, mode, scale, and canonical structures.  In
particular, a sector decomposition is not promoted to a physical irreducible
decomposition when the physical boundary operator and its domain are absent.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


ACTION_VERSION = "BHSM-AE-3.2.11-ENCAPSULATION-RESPONSE-REPRESENTATION"
STATUS = (
    "GENERAL_COVARIANT_RESPONSE_TYPED;_GLOBAL_IRREDUCIBLE_DECOMPOSITION_"
    "AND_FINITE_INTERTWINER_COUNT_BLOCKED_BY_THE_UNSELECTED_CARRIER_"
    "PHYSICAL_OPERATOR_DOMAIN_AND_EVENT_MODE_PROJECTORS"
)
RSP_CLASS = "RSP5"
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_ENCAPSULATION_CARRIER_WITH_PHYSICAL_EVENT_AND_CHILD_"
    "BOUNDARY_OPERATOR_DOMAINS_ACTUAL_STABILIZER_GROUP_AND_SPECTRAL_"
    "PROJECTORS"
)


@dataclass(frozen=True)
class Channel:
    """One owned isotypic sector or recovered finite diagnostic subspace."""

    key: str
    mathematical_space: str
    scalar_field: str
    dimension: str
    gauge_type: str
    diffeomorphism_type: str
    spin_type: str
    mode_labels: str
    amplitude_status: str
    parity_orientation: str
    incidence_constraints: str
    multiplicity: str
    physical_status: str
    phase_status: str
    canonical_partner: str


@dataclass(frozen=True)
class Coupling:
    """A block in the event-to-child response graph."""

    source: str
    target: str
    order: str
    status: str
    reason: str


def provenance_categories() -> dict[str, list[str]]:
    """Keep recovered, owner-supplied, and newly derived statements separate."""

    return {
        "RECOVERED_PRIOR_BHSM": [
            "sectorwise boundary Green and presymplectic forms",
            "conditional full-field naturality under an admissible F_B",
            "AE2 unitary fermion trace graph on its owned squared domain",
            "FB5 full-field attachment freedom and unselected nonfermion maximal-isotropic relations",
            "round ell=2 H2=(1,1) Spin(4) representation with a one-dimensional full-product commutant",
            "diagonal-SU2 restriction H2=1+3+5 with a three-dimensional commutant",
            "full irreducible Clifford spin-factor commutant of complex dimension one",
            "Hopf harmonic selection rules are kinematic and do not select coefficients",
            "N12 branch-24 event stop eigenline and the 31-by-98 fixed-event child Jacobian rank",
            "Lambda_s=(ell_kappa,R_reset/ell_kappa,x_s)",
        ],
        "OWNER_SUPPLIED_PHYSICS": [
            "encapsulation actively creates erases or redistributes boundary information",
            "for a given initiating mode the response is determined by that mode amplitude and geometry together with local energy-spacetime ratio and scale",
            "Xi_enc=(M_event,rho_E_over_ST,Lambda_s)",
        ],
        "NEWLY_DERIVED": [
            "the first derivative of any deterministic covariant response is an intertwiner for the actual event stabilizer",
            "isotypic blocks have identity-on-irrep tensor arbitrary multiplicity-space maps",
            "higher response jets lie in graded symmetric tensor-product intertwiner spaces",
            "canonical compatibility is a pullback-isotropy condition on response derivatives and does not generally impose b=a_inverse",
            "the absent carrier and operator domain leave infinitely many spectral and base-map response freedoms, hence RSP5",
            "form restrictions add zero N12 Jacobian rank",
        ],
    }


def input_space_contract() -> dict[str, Any]:
    """Type the control space without pretending that one global vector space exists."""

    return {
        "control": "Xi_enc=(M_event,rho_E/ST,Lambda_s)",
        "exact_current_mathematical_class": (
            "DISJOINT_UNION_OVER_ADMISSIBLE_EVENT_STRATA_CARRIERS_DOMAINS_"
            "AND_DISCRETE_SUPERSELECTION_DATA;_NOT_ONE_OWNED_VECTOR_SPACE"
        ),
        "fixed_regular_carrier_local_model": (
            "T_Xi=V_event_DIRECT_SUM_R_rho_DIRECT_SUM_R_ell_DIRECT_SUM_"
            "R_(R_reset/ell)_DIRECT_SUM_R_x"
        ),
        "V_event_fixed_carrier": (
            "DIRECT_SUM_s Gamma_red^(t_s)(Sigma_event,E_s)_event-mode;_"
            "Sobolev_orders_and_physical_projectors_require_the_operator_domain"
        ),
        "scalar_controls": {
            "rho_E/ST": "OWNER_SUPPLIED_INVARIANT_SCALAR_SLOT;_DEFINITION_SIGN_RANGE_AND_UNITS_NOT_RECOVERED",
            "Lambda_s": "(ell_kappa,R_reset/ell_kappa,x_s)",
            "ell_kappa": "POSITIVE_SCALAR_LENGTH;_ell_kappa=kappa1^(-1/6)",
            "R_reset_over_ell_kappa": "DIMENSIONLESS_SCALAR",
            "x_s": "DIMENSIONLESS_SCALAR_log(B/A)|_(sigma=0)",
        },
        "discrete_controls": (
            "alpha_s,tau_s,degree,orientation,FR_parity,incidence,"
            "Spin_x_GSM_bundle_class,family_projectors,route"
        ),
        "N12_owned_event_subspace": {
            "space": "E_24=span_R{v_24}",
            "dimension": 1,
            "meaning": "SIMPLE_ORDERED_EVENT_STOP_EIGENLINE_NOT_A_CHILD_BOUNDARY_HARMONIC",
            "amplitude": "REAL_TANGENT_AMPLITUDE_IN_THE_CERTIFIED_CHART",
            "orientation": "FORWARD_TEMPORAL_CHIRALITY_IS_PHYSICAL_ON_THE_SELECTED_EVENT_SIDE",
        },
        "global_event_irreducible_decomposition_owned": False,
        "reason_not_vector_space": (
            "different strata can lack ordinary geometry and different carriers have different section spaces"
        ),
    }


def output_space_contract() -> dict[str, Any]:
    """Return the fundamental trace and canonical-covector target types."""

    return {
        "target": "V_q DIRECT_SUM V_Pi",
        "V_q_fixed_carrier": (
            "DIRECT_SUM_s Gamma_red^(t_s)(Sigma_child,E_s);_configuration_"
            "traces_subject_to_gauge_constraint_incidence_FR_and_retarded_admissibility"
        ),
        "V_Pi_fixed_carrier": (
            "SECTORWISE_CONTINUOUS_DUAL_OF_V_q_FROM_LEGENDRE_OR_GREEN_"
            "FORMS;_NOT_ONE_CROSS_SECTOR_UNITED_DUAL"
        ),
        "bundle": "BRST_AND_CONSTRAINT_REDUCED_GRADED_BOUNDARY_PHASE_BUNDLE",
        "pairing": "sum_s <Pi_s,delta q_s>_Sigma_HAS_ACTION_UNITS",
        "symplectic_form": "Omega_Sigma=sum_s delta Pi_s WEDGE delta q_s_WITH_GRADED_SIGNS",
        "real_complex_structure": {
            "geometry_scalar_gauge_bosonic": "REAL_AFTER_REALITY_CONDITIONS",
            "fermion": "COMPLEX_SPINOR_WITH_CONJUGATE_GREEN_FORM_DATA",
            "ghost_antighost": "Z_GRADED_BRST_PAIR",
            "higher_spin": "REAL_OR_COMPLEX_AS_THE_REPRESENTED_FIELD_REQUIRES;_CURRENT_NORMAL_LEGENDRE_RANK_ZERO",
        },
        "sector_exceptions": {
            "fermion": "FIRST_ORDER_GREEN_DATA_NOT_AN_INDEPENDENT_ORDINARY_q_p_PAIR;_AE2_GRAPH_FIXES_THE_OWNED_COMPONENT_AFTER_F_B_AND_U_R",
            "higher_spin": "ALGEBRAIC_TRACE_EXISTS_BUT_RETAINED_NORMAL_MOMENTUM_IMAGE_HAS_RANK_ZERO",
            "complete_symplectic_form": "WITHHELD_BY_PRIOR_BHSM_OUTSIDE_THE_SECTORWISE_REGULAR_DOMAIN",
        },
        "Delta_enc": "Pi_child+C(F_B)^*Pi_event_IN_V_Pi",
        "finite_dimension": None,
        "dimension_class": "INFINITE_DIMENSIONAL_FOR_EACH_FIXED_SMOOTH_COMPACT_CARRIER_BEFORE_TRUNCATION",
    }


def event_channel_decomposition() -> tuple[Channel, ...]:
    """Return the minimal owned sector decomposition, not a fabricated irrep list."""

    common = "INFINITE_SECTION_SPACE;_SPECTRAL_MULTIPLICITIES_UNSET"
    return (
        Channel(
            "geometry",
            "Gamma(Sigma,Sym2 T*Sigma)_reduced",
            "R",
            common,
            "INTERNAL_GAUGE_SINGLET",
            "COVARIANT_SYMMETRIC_TWO_TENSOR_DENSITY_WEIGHTS_SECTOR_DEPENDENT",
            "SPIN_0_TENSOR_SECTOR",
            "PHYSICAL_OPERATOR_EIGENLABELS_UNSET;_ROUND_SHAPE_ell_IS_REFERENCE_ONLY",
            "REAL_TENSOR_AMPLITUDES_PHYSICAL_AFTER_DIFFEO_CONSTRAINT_REDUCTION",
            "ORIENTED_PULLBACK;_NORMAL_COVECTOR_ODD_UNDER_NORMAL_REVERSAL",
            "HAMILTONIAN_MOMENTUM_AND_ATTACHMENT_INCIDENCE",
            "OPERATOR_SPECTRUM_NOT_OWNED",
            "PHYSICAL_SECTOR;_NOT_IRREDUCIBLY_DECOMPOSED",
            "REAL_SIGN_ORIENTATION_CAN_BE_PHYSICAL;_NO_FREE_COMPLEX_PHASE",
            "BROWN_YORK_GHY_CORNER_MOMENTUM",
        ),
        Channel(
            "scalar_topographic",
            "Gamma(Sigma,E_scalar)_reduced",
            "R",
            common,
            "REPRESENTATION_DEPENDS_ON_SCALAR;_SUPPORT_SCALAR_IS_SINGLET",
            "SCALAR_OR_DENSITY_AS_DECLARED_BY_THE_ACTION",
            "SPIN_0",
            "SCALAR_SPECTRAL_LABELS_UNSET;_BERGER_HOPF_LABELS_NOT_INSTANTIATED_ON_CURRENT_CARRIER",
            "REAL_AMPLITUDE_PHYSICAL_MODULO_ANY_OWNED_SUPPORT_REDUNDANCY",
            "SCALAR_EVEN;_CONORMAL_MOMENTUM_ODD_UNDER_NORMAL_REVERSAL",
            "SUPPORT_TOPOGRAPHIC_AND_ATTACHMENT_INCIDENCE",
            "OPERATOR_SPECTRUM_NOT_OWNED",
            "PHYSICAL_SECTOR;_NOT_IRREDUCIBLY_DECOMPOSED",
            "REAL_AMPLITUDE_PHYSICAL;_SIGN_NOT_GENERICALLY_GAUGE",
            "NORMAL_LEGENDRE_MOMENTUM",
        ),
        Channel(
            "gauge",
            "Gamma(Sigma,T*Sigma tensor ad(P))_BRST-reduced",
            "R",
            common,
            "ADJOINT_G_SM_WITH_CONNECTION_AFFINE_ACTION_BEFORE_REDUCTION",
            "BOUNDARY_ONE_FORM_WITH_DENSITY_DUAL",
            "SPIN_1_GEOMETRIC_FORM",
            "ROOT_COLOR_WEAK_HYPERCHARGE_AND_BOUNDARY_HARMONIC_LABELS_AFTER_DOMAIN_SELECTION",
            "TRANSVERSE_AMPLITUDE_PHYSICAL;_LONGITUDINAL_AMPLITUDE_BRST_REDUNDANT",
            "ORIENTATION_PRESERVING_PULLBACK;_ELECTRIC_CONORMAL_ODD",
            "GAUSS_WARD_BRST_AND_BUNDLE_INCIDENCE",
            "ROOT_COLOR_WEAK_HYPERCHARGE_AND_HARMONIC_MULTIPLICITIES_UNSET_ON_PHYSICAL_DOMAIN",
            "PHYSICAL_TRANSVERSE_SECTOR;_LONGITUDINAL_PART_BRST_PAIRED",
            "INTERNAL_PHASE_OR_ORIENTATION_IS_GAUGE_ONLY_ALONG_THE_GAUGE_ORBIT;_HOLONOMY_CAN_BE_PHYSICAL",
            "WEIGHTED_ELECTRIC_CONORMAL",
        ),
        Channel(
            "fermion",
            "Gamma(Sigma,S_Sigma tensor R_SM)_AE2-domain",
            "C",
            common,
            "CHIRAL_STANDARD_MODEL_REPRESENTATION",
            "SPIN_LIFTED_PULLBACK",
            "SPINOR",
            "CHIRAL_GAUGE_FAMILY_HOPF_AND_BOUNDARY_SPECTRAL_LABELS_WHEN_PROJECTORS_EXIST",
            "SPINOR_AMPLITUDE_PHYSICAL_AFTER_GAUGE_AND_REALITY_CONDITIONS",
            "FR_PARITY_AND_SPIN_LIFT_REQUIRED",
            "AE2_DOMAIN_CHIRAL_BUNDLE_FAMILY_AND_ATTACHMENT_INCIDENCE",
            "FAMILY_INTERNAL_AND_BOUNDARY_SPECTRAL_MULTIPLICITIES_UNSET",
            "AE2_TRACE_GRAPH_OWNED_AFTER_F_B;_ACTIVE_RESPONSE_COEFFICIENTS_UNSET",
            "COMMON_INTERNAL_GAUGE_PHASE_REDUNDANT;_RELATIVE_PHYSICAL_PHASE_NOT_STRUCTURALLY_ELIMINATED",
            "CONJUGATE_FIRST_ORDER_GREEN_TRACE",
        ),
        Channel(
            "ghost_antighost",
            "Gamma(Sigma,ad(P))[ghost_number=+1,-1]",
            "C_OR_REAL_FORM",
            common,
            "ADJOINT_BRST_COMPLEX",
            "SCALAR_DENSITY_WITH_ASSOCIATED_BUNDLE_PULLBACK",
            "SPIN_0_GRASSMANN_ODD",
            "GHOST_NUMBER_ROOT_AND_BOUNDARY_OPERATOR_LABELS",
            "NOT_AN_INDEPENDENT_PHYSICAL_AMPLITUDE",
            "GHOST_NUMBER_AND_GRADED_PARITY_FIXED",
            "BRST_DIFFERENTIAL_MATCHES_THE_GAUGE_LONGITUDINAL_DOMAIN",
            "MATCHES_GAUGE_LONGITUDINAL_MULTIPLICITY_AFTER_DOMAIN_SELECTION",
            "AUXILIARY_BRST_SECTOR_NOT_AN_INDEPENDENT_PHYSICAL_MODE",
            "BRST_GAUGE_REDUNDANCY",
            "BRST_INDUCED_ADJOINT_PARTNER",
        ),
        Channel(
            "higher_spin",
            "Gamma(Sigma,E_HS)_incidence-restricted",
            "R_OR_C",
            common,
            "REPRESENTATION_LEDGER_OWNED_BUT_PHYSICAL_TRACE_INCIDENCE_INCOMPLETE",
            "TENSOR_SPIN_BUNDLE_PULLBACK",
            "DECLARED_HIGHER_SPIN_REPRESENTATIONS",
            "DECLARED_SPIN_FAMILY_AND_HARMONIC_LABELS;_PHYSICAL_BOUNDARY_PROJECTORS_UNSET",
            "ALGEBRAIC_TRACE_AMPLITUDE_NOT_YET_CLASSIFIED_AS_PHYSICAL_CANONICAL_DATA",
            "FR_AND_INCIDENCE_RESTRICTIONS_APPLY",
            "HIGHER_SPIN_ALGEBRAIC_AND_FAMILY_INCIDENCE_OPEN",
            "UNSET",
            "ALGEBRAIC_TRACE_ONLY;_NOT_A_COMPLETED_CANONICAL_CHANNEL",
            "UNSET",
            "ZERO_IMAGE_OF_THE_RETAINED_NORMAL_LEGENDRE_MAP",
        ),
    )


def recovered_finite_subspaces() -> dict[str, Any]:
    """Record exact finite representation results without global promotion."""

    from bhsm.interface.completion.round_hessian_centrality_no_go_v14_71 import (
        diagonal_commutant_dimension,
        product_commutant_dimension,
    )
    from bhsm.interface.completion.worldline_clifford_spin_lift_v14_44 import (
        commutant_complex_dimension,
        dirac_gamma_matrices,
        normal_symbol,
    )

    return {
        "N12_event_stop_line": {
            "representation": "REAL_ONE_DIMENSIONAL_EVENT_TANGENT_EIGENLINE",
            "dimension": 1,
            "commutant_dimension": 1,
            "child_boundary_identification": False,
        },
        "round_shape_H2_full_Spin4": {
            "representation": "H2=(1,1)_of_SU2_L_x_SU2_R",
            "real_dimension": 9,
            "multiplicity": 1,
            "commutant_real_dimension": product_commutant_dimension(),
            "response_form": "SCALAR_MULTIPLE_OF_IDENTITY_ON_THIS_REFERENCE_IRREP",
            "physical_current_carrier": False,
        },
        "round_shape_H2_diagonal_SU2": {
            "decomposition": "H2=V0_DIRECT_SUM_V1_DIRECT_SUM_V2",
            "dimensions": [1, 3, 5],
            "multiplicities": [1, 1, 1],
            "commutant_real_dimension": diagonal_commutant_dimension(),
            "physical_diagonal_polarization_selected": False,
        },
        "Clifford_spin_factor": {
            "full_irreducible_commutant_complex_dimension": commutant_complex_dimension(
                dirac_gamma_matrices()
            ),
            "normal_symbol_only_commutant_complex_dimension": commutant_complex_dimension(
                [normal_symbol()]
            ),
            "warning": "INTERNAL_GAUGE_FAMILY_AND_SPECTRAL_MULTIPLICITY_SPACES_REMAIN_AFTER_THE_SPIN_FACTOR",
        },
        "historical_three_noncentral_channels": {
            "basis_rank": 3,
            "amplitudes_phases_order_selected": False,
            "encapsulation_event_channels_identified": False,
        },
    }


def intertwiner_space_ledger() -> dict[str, Any]:
    """State exact Schur form and the dimensions that can actually be proved."""

    return {
        "actual_group": (
            "G_x=Stab(event_background)_IN_Diff_plus_spin(Sigma)_SEMI_DIRECT_"
            "Gauge(P)_WITH_BRST_AND_DISCRETE_INCIDENCE_FR_RESTRICTIONS"
        ),
        "actual_group_instantiated": False,
        "isotypic_theorem": (
            "IF_Vin=SUM_lambda(W_lambda tensor M_in_lambda)_AND_"
            "Vout=SUM_lambda(W_lambda tensor M_out_lambda),_THEN_"
            "Hom_G(Vin,Vout)=SUM_lambda(I_W_lambda tensor_"
            "Hom_Dlambda(M_in_lambda,M_out_lambda))"
        ),
        "finite_dimension_formula": (
            "dim_Hom_G=sum_lambda dim_Dlambda(M_in_lambda)*dim_Dlambda(M_out_lambda)"
        ),
        "zero_rule": (
            "Hom_G(V_r,V_s)=0_FOR_INEQUIVALENT_IRREPS_OR_INCOMPATIBLE_"
            "GAUGE_SPIN_GHOST_FR_ORIENTATION_TYPES_UNLESS_AN_OWNED_"
            "BACKGROUND_TENSOR_INCIDENCE_OR_ACTION_VERTEX_SUPPLIES_THE_MISSING_REPRESENTATION"
        ),
        "known_dimensions": recovered_finite_subspaces(),
        "sectorwise_current_result": {
            "geometry": "INFINITE_DIMENSIONAL_OPERATOR_FREEDOM",
            "scalar_topographic": "INFINITE_DIMENSIONAL_OPERATOR_FREEDOM",
            "gauge": "INFINITE_DIMENSIONAL_OPERATOR_FREEDOM_AFTER_TRANSVERSE_BRST_REDUCTION",
            "fermion": "SPIN_FACTOR_ONE_DIMENSIONAL_ONLY;_TOTAL_MULTIPLICITY_OPERATOR_FREEDOM_UNRESOLVED",
            "ghost_antighost": "BRST_LINKED_NOT_INDEPENDENT;_DOMAIN_MULTIPLICITY_UNRESOLVED",
            "higher_spin": "TRACE_INTERTWINER_UNRESOLVED;_NORMAL_MOMENTUM_IMAGE_ZERO",
        },
        "why_infinite": (
            "on_a_fixed_compact_carrier_covariance_allows_independent_maps_on_"
            "infinitely_many_isotypic_or_spectral_multiplicity_blocks;_before_"
            "fixing_F_B_the_base_map_itself_varies_in_an_infinite-dimensional_space"
        ),
        "unique_scalar_per_physical_channel_derived": False,
    }


def mode_coupling_graph() -> tuple[Coupling, ...]:
    """Classify diagonal and off-diagonal blocks at current authority."""

    return (
        Coupling("same_irrep", "same_irrep", "linear", "ALLOWED_UNRESOLVED", "Schur block on multiplicity spaces"),
        Coupling("inequivalent_irrep", "inequivalent_irrep", "linear", "REQUIRED_ZERO", "no owned compensating tensor or vertex"),
        Coupling("bosonic_even", "fermion_odd", "linear", "REQUIRED_ZERO", "spin and fermion-parity mismatch without an owned background spinor"),
        Coupling("physical_even", "ghost_odd_nonzero_number", "linear", "REQUIRED_ZERO", "ghost-number and BRST grading"),
        Coupling("gauge_longitudinal", "ghost_antighost", "linear", "ALLOWED_BRST_LINKED", "owned BRST complex; not independent physical response"),
        Coupling("geometry", "matter_or_gauge", "linear", "BACKGROUND_DEPENDENT_UNRESOLVED", "linearized action Hessian can mix sectors only through a selected background"),
        Coupling("Hopf_mode_r", "Hopf_mode_s", "linear", "REQUIRED_ZERO_IF_INEQUIVALENT", "mode fidelity follows only after the actual stabilizer projectors exist"),
        Coupling("Hopf_mode_r", "Hopf_mode_s", "nonlinear", "KINEMATICALLY_ALLOWED_ONLY_IF_SELECTION_RULES_MATCH", "v14.34 product rules do not establish a nonzero encapsulation vertex"),
        Coupling("sigma10", "sigma4_sigma4", "cubic", "FORBIDDEN_ON_SIGMA_ZERO_BACKGROUND", "historical sigma-parity exclusion"),
        Coupling("AE2_event_spinor", "AE2_child_spinor", "linear", "CONDITIONAL_NONZERO_TRACE_GRAPH", "unique spin trace graph after F_B and U_R; not an active source coefficient"),
        Coupling("N12_event_stop_line", "child_boundary_harmonic", "linear", "UNRESOLVED_NOT_IDENTIFIED", "the branch-24 stop direction is not a boundary harmonic"),
    )


def coupling_allowed(
    source: str,
    target: str,
    *,
    same_irrep: bool,
    owned_coupling_mechanism: bool = False,
    grading_compatible: bool = True,
) -> bool:
    """Conservative predicate for a potentially nonzero response block."""

    if not grading_compatible:
        return False
    if source == target and same_irrep:
        return True
    return bool(same_irrep or owned_coupling_mechanism)


def equivariance_residual(
    response: np.ndarray, input_action: np.ndarray, output_action: np.ndarray
) -> float:
    """Return ||T rho_in(g)-rho_out(g) T|| for a finite witness."""

    operator = np.asarray(response, dtype=float)
    in_rep = np.asarray(input_action, dtype=float)
    out_rep = np.asarray(output_action, dtype=float)
    if operator.ndim != 2 or in_rep.ndim != 2 or out_rep.ndim != 2:
        raise ValueError("matrix representations required")
    if in_rep.shape[0] != in_rep.shape[1] or out_rep.shape[0] != out_rep.shape[1]:
        raise ValueError("group actions must be square")
    if operator.shape != (out_rep.shape[0], in_rep.shape[0]):
        raise ValueError("response has incompatible representation dimensions")
    return float(np.linalg.norm(operator @ in_rep - out_rep @ operator))


def first_order_response_theorem() -> dict[str, Any]:
    """Return the strongest linear theorem at a fixed admissible background."""

    return {
        "hypotheses": [
            "a carrier Sigma_enc and physical event/child trace domains are fixed",
            "a deterministic response A_enc is differentiable at x in Xi_enc",
            "A_enc is equivariant under the actual stabilizer G_x",
            "constraint and BRST reductions defining tangent and target spaces have been made",
        ],
        "theorem": "D A_enc|_x belongs to Hom_(G_x)(T_x Xi_enc,V_q DIRECT_SUM V_Pi)",
        "block_form": (
            "D A_enc|_x=SUM_lambda I_(W_lambda) tensor A_lambda_ON_MATCHED_"
            "ISOTYPIC_BLOCKS;_ALL_UNMATCHED_BLOCKS_VANISH"
        ),
        "control_derivatives": (
            "derivatives_with_respect_to_invariant_scalar_controls_are_"
            "intertwiners_of_the_same_representation_type"
        ),
        "mode_fidelity": (
            "LINEAR_MODE_FIDELITY_HOLDS_BETWEEN_INEQUIVALENT_G_x_IRREPS;_"
            "MIXING_INSIDE_MULTIPLICITY_SPACES_REMAINS_ALLOWED"
        ),
        "current_scope": "CONDITIONAL_REPRESENTATION_THEOREM_ONLY",
        "does_not_supply_values": True,
    }


def nonlinear_response_theorem() -> dict[str, Any]:
    """Classify nonlinear jets without choosing a polynomial response."""

    return {
        "kth_jet": (
            "D^k A_enc|_x belongs to Hom_(G_x)(Sym_gr^k(T_x Xi_enc),"
            "V_q DIRECT_SUM V_Pi)"
        ),
        "linear": "MATCHED_ISOTYPIC_INTERTWINERS_ONLY",
        "quadratic": (
            "ONLY_TARGET_IRREPS_CONTAINED_IN_GRADED_SYMMETRIC_PRODUCTS_"
            "OF_TWO_INPUT_CHANNELS_AND_PERMITTED_BY_GAUGE_FR_ORIENTATION_GHOST_NUMBER"
        ),
        "cubic": (
            "SAME_TENSOR_PRODUCT_TEST;_HISTORICAL_10_4_4_sigma_CHANNEL_"
            "VANISHES_AT_sigma=0_BY_THE_RECOVERED_PARITY_RULE"
        ),
        "action_vertex_requirement": (
            "representation_allowance_is_not_a_nonzero_coupling;_incidence_"
            "action_interaction_constraint_or_reconstruction_BVP_must_supply_the_vertex"
        ),
        "full_nonlinear_map_determined": False,
        "high_order_campaign_launched": False,
    }


def scale_and_control_ledger() -> dict[str, Any]:
    """Give the maximal dimensional reduction justified by current scale data."""

    return {
        "rho_E/ST": {
            "type": "OWNER_SUPPLIED_SYMMETRY_SCALAR_CONTROL_SLOT",
            "recovered_unique_definition": False,
            "candidate_repository_container": "B_s_CONSTRAINT_CAUCHY_NOETHER_ENERGY_SUPPORT_DATA",
            "why_not_identified": "B_s_IS_TENSOR_AND_COVECTOR_VALUED_AND_NO_UNIQUE_ENERGY_TO_SPACETIME_SCALAR_CONTRACTION_IS_OWNED",
            "dimension": None,
            "sign_or_range": None,
        },
        "Lambda_s": {
            "definition": "(ell_kappa,r_reset,x_s)",
            "ell_kappa_units": "L",
            "r_reset": "R_reset/ell_kappa_DIMENSIONLESS",
            "x_s": "log(B/A)|_(sigma=0)_DIMENSIONLESS",
        },
        "coefficient_dimension_rule": (
            "for_input_component_u_with_[u]=L^d_in_and_output_y_with_"
            "[y]=L^d_out,_the_linear_coefficient_has_[a]=L^(d_out-d_in)"
        ),
        "scale_covariant_form": (
            "a_lambda_ij=ell_kappa^(d_out-d_in)*f_lambda_ij("
            "rho_hat,r_reset,x_s;discrete_stratum_data)"
        ),
        "rho_hat_condition": (
            "rho_hat=rho_E/ST*ell_kappa^(-d_rho)_ONLY_AFTER_[rho]=L^d_rho_IS_DEFINED"
        ),
        "minimal_continuous_invariant_arguments_currently_typed": [
            "rho_hat_if_defined",
            "R_reset/ell_kappa",
            "x_s",
            "event_mode_invariants_already_contained_in_M_event",
        ],
        "discrete_arguments": "alpha_s,tau_s,I_s_and_route_or_mapping_class_WHEN_SELECTED",
        "universal_dimensionless_function_count": "NOT_FINITE_OR_DETERMINED_BECAUSE_THE_ISOTYPIC_INDEX_AND_MULTIPLICITIES_ARE_UNSET",
        "no_function_selected": True,
    }


def coefficient_length_exponent(output_exponent: float, input_exponent: float) -> float:
    """Return the length exponent required of a linear response coefficient."""

    output = float(output_exponent)
    input_value = float(input_exponent)
    if not np.isfinite(output) or not np.isfinite(input_value):
        raise ValueError("finite length exponents required")
    return output - input_value


def canonical_pullback_residual(jacobian_q: np.ndarray, jacobian_pi: np.ndarray) -> float:
    """Measure the pullback of sum dPi wedge dq for a response immersion."""

    jq = np.asarray(jacobian_q, dtype=float)
    jp = np.asarray(jacobian_pi, dtype=float)
    if jq.ndim != 2 or jp.ndim != 2 or jq.shape != jp.shape:
        raise ValueError("q and Pi Jacobians must have the same matrix shape")
    pullback = jq.T @ jp - jp.T @ jq
    return float(np.linalg.norm(pullback))


def canonical_structure_ledger() -> dict[str, Any]:
    """State when a response image is isotropic, Lagrangian, or affine canonical."""

    return {
        "sectorwise_form": "Omega_Sigma=sum_s delta Pi_s WEDGE delta q_s_WITH_GRADED_SIGNS",
        "response_pullback": "A_enc^*Omega=0_IFF_(Dq)^*DPI-(DPI)^*Dq=0",
        "necessary_for_action_generated_isotropic_graph": True,
        "Lagrangian_condition": (
            "isotropic_plus_immersed_control_dimension_equal_to_half_the_"
            "reduced_target_symplectic_dimension"
        ),
        "affine_covector_graph": (
            "Pi=dS_boundary(q)+alpha(q)_IS_LAGRANGIAN_IFF_d_alpha=0;_"
            "a_nonclosed_active_source_is_not_a_Lagrangian_graph_without_extra_seam_variables"
        ),
        "canonical_relation_status": (
            "MAXIMAL_ISOTROPIC_OR_AFFINE_CANONICAL_RELATION_IS_THE_"
            "CONDITIONAL_ACTION_COMPATIBLE_CLASS;_NO_MEMBER_SELECTED"
        ),
        "one_control_direction": "PULLBACK_OF_A_TWO_FORM_TO_ONE_DIMENSION_IS_AUTOMATICALLY_ZERO",
        "multi_channel_consequence": "CROSS_DERIVATIVE_INTEGRABILITY_LINKS_TRACE_AND_COVECTOR_RESPONSE_JETS",
        "does_not_force": [
            "independent_scalar_coefficients_a_r_and_b_r_to_be_equal",
            "b_r=a_r^(-1)_unless_the_map_is_specifically_a_cotangent_lift",
            "the_response_image_to_be_Lagrangian_when_dimension_or_immersion_fails",
        ],
        "complete_global_reduced_symplectic_form_owned": False,
    }


def constraint_noether_ledger() -> dict[str, Any]:
    """Separate constraints already quotiented from restrictions on the response image."""

    return {
        "already_used_in_space_definition_do_not_recount": [
            "internal gauge quotient and BRST pairing",
            "Hamiltonian momentum and Gauss constraints defining reduced boundary data",
            "fixed degree orientation FR incidence and bundle class",
            "AE4 retarded-domain admissibility",
        ],
        "remaining_response_conditions": {
            "constraint_tangency": "D_constraint_at_output COMPOSE D_A_enc=0",
            "Noether_balance": "J_event+J_child+Pi_enc=0_WITH_Delta_enc=-Pi_enc_IN_THE_SELECTED_SIGN_CONVENTION",
            "incidence_intertwining": "C(F_B)P_child=P_event C(F_B)",
            "orientation": "det(D F_B)>0_ON_THE_RETAINED_BRANCH_AND_CONORMAL_SIGNS_OPPOSE",
            "FR_parity": "response_preserves_the_selected_spin_lift_and_FR_class",
            "topology": "degree_and_bundle_isomorphism_class_must_match_or_use_an_owned_transition_vertex",
        },
        "independent_equation_count": None,
        "reason_count_unavailable": "linearized_constraint_Noether_and_incidence_operators_on_the_physical_carrier_are_not_owned",
        "current_new_rank": 0,
    }


def calderon_structure_ledger() -> dict[str, Any]:
    """Give only the representation consequence of the conditional DtN equation."""

    return {
        "conditional_equation": "(N_c+C^*N_e C)q_c=J_enc",
        "required_type": "J_enc_IN_V_Pi_WITH_THE_SAME_G_x_ISOTYPIC_LABEL_AS_THE_IMAGE_OF_q_c",
        "equivariance_conditions": [
            "N_e and N_c commute with the actual stabilizer action on their domains",
            "C intertwines child and event trace representations",
            "all operators preserve BRST constraint incidence FR and retarded domains",
        ],
        "consequence": (
            "the_combined_operator_is_block_diagonal_by_G_x_isotypic_label_"
            "and_may_be_matrix_valued_on_multiplicity_spaces"
        ),
        "scalar_on_irrep_condition": "ONLY_FOR_A_MULTIPLICITY_ONE_IRREDUCIBLE_BLOCK",
        "mode_conversion": "FORBIDDEN_BETWEEN_INEQUIVALENT_IRREPS_IF_ALL_EQUIVARIANCE_HYPOTHESES_HOLD",
        "physical_full_field_DtN_owned": False,
        "additional_diagonalization_currently_earned": False,
    }


def response_freedom_classification() -> dict[str, Any]:
    """Quantify what can and cannot be counted after structural reduction."""

    return {
        "class": RSP_CLASS,
        "sector_isotypic_classes_owned": 6,
        "physical_irreducible_channel_count": None,
        "why_no_channel_integer": (
            "the_carrier_physical_operator_domain_stabilizer_and_spectral_"
            "projectors_that_define_irreducible_boundary_modes_are_absent"
        ),
        "independent_scalar_response_functions": (
            "ONE_PER_MULTIPLICITY_ONE_MATCHED_IRREP_CONDITIONALLY;_THE_"
            "GLOBAL_NUMBER_IS_NOT_FINITE_OR_CURRENTLY_DETERMINED"
        ),
        "matrix_valued_response_functions": (
            "ONE_PER_MATCHED_IRREP_WITH_NONTRIVIAL_MULTIPLICITY_CONDITIONALLY;_"
            "POTENTIALLY_COUNTABLY_INFINITE_ON_A_FIXED_COMPACT_CARRIER"
        ),
        "operator_valued_freedom": "INFINITE_DIMENSIONAL",
        "continuous_base_map_freedom": "F_B_IN_Diff_plus_spin_IS_INFINITE_DIMENSIONAL",
        "nonfermion_boundary_relation_freedom": "CONTINUOUS_INFINITE_DIMENSIONAL_MAXIMAL_ISOTROPIC_FAMILY",
        "discrete_branches": (
            "AT_LEAST_THREE_ENCLOSURE_ROUTE_CLASSES_PLUS_UNCLASSIFIED_"
            "MAPPING_SPIN_LIFT_HOLONOMY_AND_BOUNDARY_ENSEMBLE_SECTORS"
        ),
        "finite_discrete_branch_count": None,
        "RSP0_through_RSP4_excluded_at_current_authority": True,
        "response_functions_selected": 0,
    }


def n12_rank_forecast() -> dict[str, Any]:
    """Cap potential rank without turning a representation theorem into equations."""

    return {
        "child_state_dimension": 98,
        "current_certified_rank": 31,
        "current_residual": 67,
        "time_quotient_residual": 66,
        "structural_channel_direction_forecast": {
            "each_instantiated_channel": "rank_of_its_projected_response_Jacobian_ON_THE_67D_residual;_CURRENTLY_UNKNOWN",
            "all_channels_combined_before_time_quotient": "AT_MOST_67",
            "all_channels_combined_after_time_quotient": "AT_MOST_66",
            "N12_event_stop_line": "DOES_NOT_BY_ITSELF_CONTROL_A_CHILD_DIRECTION",
            "round_H2_reference": "AT_MOST_9_ONLY_IF_PHYSICALLY_IDENTIFIED_AND_TRANSVERSE;_NOT_CURRENTLY_IDENTIFIED",
            "historical_three_channel_basis": "AT_MOST_3_ONLY_IF_AN_INCIDENCE_MAP_IS_DERIVED;_CURRENTLY_ZERO",
        },
        "maximum_potential_additional_rank": 67,
        "maximum_potential_physical_rank_modulo_time": 66,
        "actual_new_equations_this_sprint": 0,
        "actual_additional_rank_this_sprint": 0,
        "closure_claimed": False,
        "parameter_counting_is_not_rank": True,
    }


def claim_ledger() -> dict[str, Any]:
    return {
        "VALIDATED": [
            "covariant_deterministic_response_derivatives_are_stabilizer_intertwiners",
            "inequivalent_irrep_blocks_vanish_without_an_owned_compensating_vertex",
            "multiplicity_spaces_retain_matrix_freedom",
            "canonical_compatibility_constrains_response_derivatives_by_pullback_isotropy",
            "Calderon_operators_would_be_isotypically_block_diagonal_if_the_physical_domains_and_equivariance_close",
            "the_current_global_response_class_is_RSP5",
        ],
        "INVALIDATED": [
            "the_six_sector_ledger_is_an_exact_physical_irreducible_decomposition",
            "the_N12_event_eigenline_is_a_child_boundary_mode",
            "covariance_alone_yields_one_universal_scalar_response",
            "canonicality_generically_forces_b_r_equal_a_r_inverse",
            "kinematically_allowed_Hopf_edges_are_derived_nonzero_encapsulation_couplings",
            "rho_E_over_ST_has_an_existing_unique_BHSM_formula_or_known_dimension",
        ],
        "REDUNDANT": [
            "recounting_gauge_constraints_already_used_to_define_reduced_spaces",
            "basis_multiplicity_inside_an_irrep_as_distinct_physical_channels",
            "reusing_round_Spin4_commutants_after_a_background_has_reduced_the_actual_stabilizer",
        ],
        "OPEN": [
            "action_owned_carrier_and_actual_stabilizer",
            "physical_event_and_child_boundary_operator_domains",
            "complete spectral_projectors_and_multiplicity_spaces",
            "definition_units_and_invariant_contraction_for_rho_E_over_ST",
            "event_mode_to_boundary_representation_incidence",
            "full_reduced_symplectic_form_and_active_source_extension",
            "physical_full_field_Calderon_DtN_operators",
        ],
        "DECISION_POWER": (
            "PROVES_RSP5_AND_PREVENTS_FALSE_FINITE_SCHUR_COUNTING;_ZERO_NEW_"
            "N12_RANK_AND_NO_RESPONSE_FUNCTION_OR_COEFFICIENT_SELECTED"
        ),
        "OWNER_RULE_CONSEQUENCE": (
            "DETERMINISM_MEANS_ONE_VALUE_AFTER_ALL_CONTROL_AND_DISCRETE_"
            "STRATUM_DATA_ARE_FIXED;_IT_DOES_NOT_REDUCE_THE_SPACE_OF_"
            "COVARIANT_FUNCTIONS_BEFORE_THE_ACTUAL_REPRESENTATIONS_EXIST"
        ),
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "ONE_OWNER_QUESTION": None,
    }


def representation_theorem_payload() -> dict[str, Any]:
    """Assemble the deterministic response-space authority."""

    claims = claim_ledger()
    return {
        "artifact": "BHSM_ENCAPSULATION_RESPONSE_REPRESENTATION_THEOREM",
        "action_version": ACTION_VERSION,
        "status": STATUS,
        "provenance": provenance_categories(),
        "input_space": input_space_contract(),
        "output_space": output_space_contract(),
        "event_sector_decomposition": [asdict(row) for row in event_channel_decomposition()],
        "recovered_finite_subspaces": recovered_finite_subspaces(),
        "intertwiner_space": intertwiner_space_ledger(),
        "mode_coupling_graph": [asdict(row) for row in mode_coupling_graph()],
        "first_order_response_theorem": first_order_response_theorem(),
        "nonlinear_response_theorem": nonlinear_response_theorem(),
        "scale_and_controls": scale_and_control_ledger(),
        "canonical_structure": canonical_structure_ledger(),
        "constraints_and_Noether": constraint_noether_ledger(),
        "Calderon_DtN": calderon_structure_ledger(),
        "response_freedom": response_freedom_classification(),
        "N12_rank_forecast": n12_rank_forecast(),
        **claims,
        "claim_boundary": {
            "full_active_encapsulation_law_selected": False,
            "response_function_selected": False,
            "carrier_selected": False,
            "physical_irreducible_decomposition_completed": False,
            "physical_DtN_claimed": False,
            "N12_closure_claimed": False,
            "particle_or_FTL_claim_made": False,
            "Gate7_promoted": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
    }
