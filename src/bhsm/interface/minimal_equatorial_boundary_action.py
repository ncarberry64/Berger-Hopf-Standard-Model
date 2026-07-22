"""BHSM v6.1.3 minimal intrinsic equatorial boundary-action freeze."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


VERSION = "v6.1.3"
SPRINT = "bhsm-minimal-equatorial-boundary-action-freeze-v6-1-3"
PRIMARY_RESULT = "BHSM_MINIMAL_EQUATORIAL_BOUNDARY_ACTION_REQUIRES_MULTIPLE_PRIMITIVES"
COMPLETION_GATE = "V6_1_3_INTRINSIC_ACTION_FROZEN_COEFFICIENT_LOCK_UNDERDETERMINED_SHIFTED_BACKGROUND_OPEN"

ARTIFACT_FILES = {
    "axiom": "BHSM_boundary_axiom_B1_freeze_v6_1_3.json",
    "trace": "BHSM_trace_field_vs_intrinsic_field_theorem_v6_1_3.json",
    "freeze": "BHSM_minimal_equatorial_boundary_action_freeze_v6_1_3.json",
    "matching": "BHSM_exact_boundary_matching_action_ledger_v6_1_3.json",
    "lock": "BHSM_boundary_one_normalization_coefficient_lock_test_v6_1_3.json",
    "primitives": "BHSM_boundary_independent_primitive_count_v6_1_3.json",
    "gravity": "BHSM_intrinsic_M4_gravity_action_v6_1_3.json",
    "connection": "BHSM_intrinsic_M4_connection_action_v6_1_3.json",
    "u1": "BHSM_nested_U1_intrinsic_boundary_classification_v6_1_3.json",
    "sigma": "BHSM_intrinsic_M4_sigma_kinetic_action_v6_1_3.json",
    "potential": "BHSM_boundary_scalar_potential_source_audit_v6_1_3.json",
    "variation": "BHSM_combined_bulk_boundary_variation_v6_1_3.json",
    "backreaction": "BHSM_round_background_boundary_backreaction_v6_1_3.json",
    "lorentz": "BHSM_intrinsic_M4_Lorentz_hyperbolicity_test_v6_1_3.json",
    "stability": "BHSM_intrinsic_boundary_constraint_reduced_stability_v6_1_3.json",
    "boundary": "BHSM_equatorial_intrinsic_physical_boundary_status_v6_1_3.json",
    "current": "BHSM_intrinsic_boundary_current_normalization_v6_1_3.json",
    "aperture": "BHSM_intrinsic_M4_aperture_readiness_v6_1_3.json",
    "parent_map": "BHSM_intrinsic_boundary_parent_to_v5_v4_map_v6_1_3.json",
    "fermionic": "BHSM_M4_first_order_fermionic_action_readiness_v6_1_3.json",
    "scale": "BHSM_intrinsic_boundary_scale_primitive_audit_v6_1_3.json",
    "hidden": "BHSM_intrinsic_boundary_hidden_input_claim_audit_v6_1_3.json",
    "report": "BHSM_minimal_equatorial_boundary_action_report_v6_1_3.json",
}

GUARDS = {
    "boundary_axiom_parent_derived": False,
    "preferred_equator_invented": False,
    "bulk_and_boundary_fields_conflated": False,
    "term_added_after_freeze": False,
    "finite_matching_penalty_used": False,
    "v5_scalar_coefficients_imported": False,
    "measured_mass_or_coupling_used": False,
    "alpha_evaluated": False,
    "standard_model_group_or_charge_assigned": False,
    "physical_Dirac_equation_assumed": False,
    "magnetic_monopole_sector_used": False,
    "magnetic_charge_operator_exists": False,
    "absolute_unit_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all kinetic coefficients and geometric scales must be positive")


def trace_field_mismatch(temporal: float, spatial: float, boundary_term: float) -> dict[str, float]:
    """Compare a smooth bulk trace before and after a common intrinsic term."""
    if temporal <= 0 or spatial < temporal or boundary_term < 0:
        raise ValueError("require 0<N_t<=N_s and a nonnegative boundary term")
    return {
        "bulk_difference": spatial - temporal,
        "augmented_difference": (spatial + boundary_term) - (temporal + boundary_term),
        "augmented_ratio_minus_one": (spatial + boundary_term) / (temporal + boundary_term) - 1,
    }


def coefficient_lock_candidate(
    beta_partial: float,
    c_g: float,
    c_A: float,
    c_sigma: float,
    a_min: float,
) -> dict[str, float]:
    _positive(beta_partial, c_g, c_A, c_sigma, a_min)
    return {
        "C_partial": beta_partial * c_g / a_min**2,
        "tau_A": beta_partial * c_A,
        "Z_partial": beta_partial * c_sigma / a_min**2,
    }


def canonical_connection_coefficients(tau_A: float, trace_index: float) -> dict[str, float]:
    _positive(tau_A, trace_index)
    normalization = math.sqrt(tau_A * trace_index)
    coupling = 1 / normalization
    return {
        "canonical_factor": normalization,
        "geometric_interaction": coupling,
        "cubic_coefficient": coupling,
        "quartic_coefficient": coupling**2,
    }


def scalar_mode_mass_squared(level: int, radius: float, mass_squared: float = 0.0) -> float:
    if not isinstance(level, int) or isinstance(level, bool) or level < 0:
        raise ValueError("level must be a nonnegative integer")
    _positive(radius)
    return level * (level + 2) / radius**2 + mass_squared


def independent_primitive_count(*, scalar_potential: bool = False, scalar_matching: bool = False) -> dict[str, Any]:
    scalar_normalization_physical = scalar_potential or scalar_matching
    return {
        "raw_coefficients": 3,
        "physical_invariants_before_potential": 2,
        "scalar_normalization_physical": scalar_normalization_physical,
        "physical_invariants_with_scalar_source": 3 if scalar_normalization_physical else 2,
    }


def intrinsic_einstein_tensor(radius: float, H: float, acceleration_over_radius: float) -> dict[str, float]:
    _positive(radius)
    return {
        "G00": 3 * (H**2 + 1 / radius**2),
        "Gij_over_hij": -(2 * acceleration_over_radius + H**2 + 1 / radius**2),
    }


def round_equator_junction_residual(
    C_partial: float,
    radius: float,
    H: float,
    acceleration_over_radius: float,
) -> dict[str, float]:
    _positive(C_partial, radius)
    einstein = intrinsic_einstein_tensor(radius, H, acceleration_over_radius)
    return {
        "residual_00": 2 * C_partial * einstein["G00"],
        "residual_ij_over_hij": 2 * C_partial * einstein["Gij_over_hij"],
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "Boundary Axiom B1 and its intrinsic action are a provisional freeze, not a P1 derivation. Exact intrinsic M4 Lorentz structure is obtained, while one-normalization coefficient locking, the shifted junction background, scalar potential, full spectrum, physical gauge interpretation, absolute units, fermions, and Standard Model closure remain open.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    return {
        "axiom": {**c("BHSM_boundary_axiom_B1_freeze_v6_1_3"), "status": "BHSM_BOUNDARY_AXIOM_B1_PROVISIONAL_FROZEN", "classification": "PROVISIONAL BOUNDARY AXIOM — NOT PARENT-DERIVED", "domain": "M4=I_t x S3 on one representative of the SO(5)-equivalent Lorentz-selected great-S3 orbit", "fields": {"h_mu_nu": "independent intrinsic boundary metric constrained to the induced metric", "A_mu": "independent intrinsic connection with inherited parent representation and transition data", "sigma_partial": "independent intrinsic neutral real Z2 scalar"}, "bulk_relation": "parent and boundary variables are distinct unless an explicit matching constraint identifies them", "physical_kinetics": "intrinsic action only; smooth bulk zero-mode kinetics excluded", "preferred_representative": None, "frozen_before_kill_tests": True},
        "trace": {**c("BHSM_trace_field_vs_intrinsic_field_theorem_v6_1_3"), "status": "BHSM_SMOOTH_TRACE_FIELD_FINITE_BOUNDARY_TERM_CANNOT_CLOSE_EXACT_LORENTZ", "scalar": "(N_s+Z_partial)-(N_t+Z_partial)=N_s-N_t", "connection": "(N_B+tau_A)-(N_E+tau_A)=N_B-N_E", "tensor": "(N_s,T+C_partial)-(N_t,T+C_partial)=N_s,T-N_t,T at principal kinetic order", "finite_common_term": "dilutes the ratio but leaves the difference unchanged", "exact_result": "a nonzero smooth bulk mismatch cannot be cancelled by a finite common Lorentz-invariant boundary coefficient", "intrinsic_requirement": "BHSM_INTRINSIC_BOUNDARY_FIELD_FORMULATION_REQUIRED_FOR_EXACT_M4_LORENTZ", "scope": "declared additive trace-plus-intrinsic action structure"},
        "freeze": {**c("BHSM_minimal_equatorial_boundary_action_freeze_v6_1_3"), "status": "BHSM_MINIMAL_INTRINSIC_BOUNDARY_ACTION_FROZEN", "action": "integral_M4 sqrt(-h)[C_partial R4-tau_A Tr(F^2)/4-Z_partial(D sigma_partial)^2/2-U_partial]+S_match", "sign_domain": "C_partial>0, tau_A>0, Z_partial>0", "potential_primary_kill_test": "U_partial=0", "fields_added": [], "prohibited": ["higher derivatives", "sigma F^2", "sigma R", "connection mass", "symmetry-breaking term", "boundary fluid", "monopoles", "physical fermion action"], "freeze_hash_basis": ["B1 fields", "four displayed action terms", "metric matching only", "no post-freeze additions"]},
        "matching": {**c("BHSM_exact_boundary_matching_action_ledger_v6_1_3"), "status": "BHSM_EXACT_METRIC_MATCHING_WELL_POSED_CONDITIONALLY", "metric": "S_match=integral sqrt(-h) Lambda^{mu nu}(h_mu nu-iota^*g_mu nu)", "multiplier": {"domain": "M4", "type": "symmetric contravariant boundary tensor", "dimension": "L^-4", "equation": "h_mu nu=iota^*g_mu nu", "physical_primitive": False}, "connection": "A_mu remains intrinsic; only parent bundle representation and transition law are restricted", "scalar": "sigma_partial remains independent and is not set equal to the bulk singlet", "penalty_coefficient": None, "overconstraint": "no formal overconstraint: Lambda is eliminated between the intrinsic metric equation and bulk junction equation; compatible boundary data and the shifted background still must be solved", "conservation": "boundary diffeomorphism and gauge identities hold when the matching and bulk equations are imposed"},
        "lock": {**c("BHSM_boundary_one_normalization_coefficient_lock_test_v6_1_3"), "status": "BHSM_BOUNDARY_ONE_NORMALIZATION_HYPOTHESIS_UNDERDETERMINED", "ansatz": {"C_partial": "beta_partial c_g/a_min^2", "tau_A": "beta_partial c_A", "Z_partial": "beta_partial c_sigma/a_min^2"}, "a_min_squared": "21 kappa_1/(2 kappa_0)", "dimensions": "fix the powers of a_min but not c_g:c_A:c_sigma", "covariance": "fixes operator form, not relative normalization", "representation_traces": "fix c_A only after a generator convention and cannot relate it to gravity or a neutral scalar", "universal_measure": "common integration measure does not equate distinct operator coefficients", "spectral_or_Dirac_lock_used": False, "measured_coupling_used": False, "lock_result": "no parent-derived relation among c_g, c_A, and c_sigma"},
        "primitives": {**c("BHSM_boundary_independent_primitive_count_v6_1_3"), "status": "BHSM_BOUNDARY_MULTIPLE_INVARIANT_COMBINATIONS_REMAIN", "raw": ["C_partial", "tau_A", "Z_partial"], "metric": "h is fixed to the induced metric, so C_partial a_min^2 cannot be removed by a metric convention", "connection": "tau_A times the fixed trace index becomes the inverse squared canonical self-interaction", "scalar": "with U_partial=0 and no scalar matching/source, Z_partial is removed by s=sqrt(Z_partial)sigma_partial", "before_potential": ["C_partial a_min^2", "tau_A I_R"], "count_before_potential": 2, "with_scalar_potential_or_matching": "Z_partial re-enters through canonical masses/couplings, restoring a third independently sourced combination", "field_convention_called_prediction": False},
        "gravity": {**c("BHSM_intrinsic_M4_gravity_action_v6_1_3"), "status": "BHSM_M4_INTRINSIC_GRAVITY_ACTION_DERIVED_CONDITIONALLY", "action": "C_partial integral sqrt(-h) R4", "ADM": "C_partial integral N sqrt(q)[R3+K_ij K^ij-K^2] plus the standard temporal endpoint term", "constraints": ["lapse Hamiltonian constraint", "shift momentum constraint"], "tensor_quadratic_principal": "(C_partial/4) integral a^3[dot gamma_TT^2-a^-2(nabla gamma_TT)^2]", "physical_polarizations": 2, "kinetic_positive_if": "C_partial>0", "tensor_speed_squared": 1, "Lorentz_mismatch": 0, "observed_Planck_identification": None},
        "connection": {**c("BHSM_intrinsic_M4_connection_action_v6_1_3"), "status": "BHSM_M4_INTRINSIC_CONNECTION_ACTION_DERIVED_CONDITIONALLY", "action": "-tau_A/4 integral sqrt(-h) Tr(F_mu nu F^mu nu)", "trace": "Tr(T_a T_b)=I_R delta_ab", "canonical_field": "A_can^a=sqrt(tau_A I_R) A^a", "geometric_interaction": "g_partial=(tau_A I_R)^(-1/2)", "cubic": "g_partial f_abc with the canonical derivative structure", "quartic": "g_partial^2 f_abe f_cde with the canonical gauge identity", "constraint": "Gauss law D_i E^i=J^0", "kinetic_positive_if": "tau_A I_R>0", "Lorentz_mismatch": 0, "physical_group": None, "observed_coupling": None},
        "u1": {**c("BHSM_nested_U1_intrinsic_boundary_classification_v6_1_3"), "status": "BHSM_NESTED_U1_REMAINS_CONSTRAINED_CONNECTION_DATA", "classification": ["component/weight data inside the retained parent-derived connection representation", "not a fourth independent boundary field"], "independent_boundary_connection": False, "double_counted": False, "physical_hypercharge": None, "magnetic_interpretation": None, "stop_condition": "if an independent U1 kinetic field is required, the frozen minimal field content fails and must not be amended in this sprint"},
        "sigma": {**c("BHSM_intrinsic_M4_sigma_kinetic_action_v6_1_3"), "status": "BHSM_M4_INTRINSIC_SIGMA_KINETIC_ACTION_DERIVED_CONDITIONALLY", "action": "-Z_partial/2 integral sqrt(-h)(partial sigma_partial)^2", "canonical_field": "s_partial=sqrt(Z_partial) sigma_partial", "canonical_dimension": "L^-1", "parity": "Z2 even action under sigma_partial->-sigma_partial", "charge": "neutral", "equation": "box_h s_partial=0 for the frozen U_partial=0 test", "homogeneous_equation": "ddot s_partial+3H dot s_partial=0", "conformal_pump": "v=a s_partial gives v''-(Delta_S3+a''/a)v=0", "S3_spectrum": "l(l+2)/a^2, l=0,1,...", "kinetic_positive_if": "Z_partial>0", "Higgs_identification": None},
        "potential": {**c("BHSM_boundary_scalar_potential_source_audit_v6_1_3"), "status": "BHSM_BOUNDARY_SIGMA_KINETIC_ACTION_DERIVED_POTENTIAL_OPEN", "primary_freeze": "U_partial=0", "bulk_A0_G0": "a pullback potential acts on the bulk trace; it is not automatically a potential for independent sigma_partial", "exact_matching": "sigma_partial=sigma_bulk| would undo the intrinsic-field ontology and reintroduce trace-field kinetics", "curvature": "no sigma R term exists in the freeze", "bulk_elimination": "may generate controlled nonlocal terms only after a boundary source is specified", "inherited_coefficients": None, "A_ST": "not derived", "G_ST": "not derived", "sigma_vacuum": "not derived"},
        "variation": {**c("BHSM_combined_bulk_boundary_variation_v6_1_3"), "status": "BHSM_BULK_BOUNDARY_VARIATION_DERIVED_CONDITIONALLY", "total_action": "S_M5,bulk+S_GHY+S_partial+S_match", "bulk": "P1 bulk equations away from M4", "metric_constraint": "h=iota^*g", "boundary_metric": "C_partial G_mu nu-(T_A+T_sigma)_mu nu/2 plus the metric multiplier equals zero", "junction": "2C5(K_mu nu-K h_mu nu)+2C_partial G_mu nu=T_A,mu nu+T_sigma,mu nu in the declared one-side orientation convention", "connection": "tau_A D_nu F^{nu mu}=J_match^mu; J_match=0 in the minimal freeze", "scalar": "Z_partial box_h sigma_partial-U_partial'=J_sigma,match; both sources vanish in the primary freeze", "conservation": "Codazzi plus boundary diffeomorphism identity gives covariant conservation when all equations hold", "energy_conservation": "conditional on compatible bulk flux and matching data"},
        "backreaction": {**c("BHSM_round_background_boundary_backreaction_v6_1_3"), "status": "BHSM_INTRINSIC_GRAVITY_SHIFTS_ROUND_EQUATOR_JUNCTION", "vacuum": {"A_mu": 0, "sigma_partial": "constant", "U_partial": 0, "matter_stress": 0}, "intrinsic_Einstein": {"G00": "3(H^2+a^-2)", "Gij": "-[2 ddot(a)/a+H^2+a^-2]hij"}, "old_equator": "K_mu nu=0", "junction_residual": "2C_partial G_mu nu", "round_status": "the old smooth K=0 round trajectory is not an exact solution for C_partial>0 because G00>0 at finite a", "required_response": ["shifted embedding/nonzero K", "compensating action-derived surface stress", "modified parent solution"], "ignored_to_preserve_background": False},
        "lorentz": {**c("BHSM_intrinsic_M4_Lorentz_hyperbolicity_test_v6_1_3"), "status": "BHSM_INTRINSIC_M4_EXACT_LORENTZ_PRINCIPAL_STRUCTURE_DERIVED", "gravity": "ADM hyperbolic tensor principal symbol after lapse/shift constraint reduction", "connection": "normally hyperbolic Yang-Mills operator after a declared covariant gauge; Gauss constraint propagates", "scalar": "normally hyperbolic box_h", "temporal_spatial_coefficient": "one common intrinsic coefficient in every sector", "speeds_squared": {"tensor": 1, "connection": 1, "scalar": 1}, "sign_domain": "C_partial>0, tau_A I_R>0, Z_partial>0", "observational_bound_used": False},
        "stability": {**c("BHSM_intrinsic_boundary_constraint_reduced_stability_v6_1_3"), "status": "BHSM_INTRINSIC_M4_PRINCIPAL_KINETICS_HEALTHY_FULL_SPECTRUM_OPEN", "removed": ["lapse", "shift", "temporal gauge multiplier", "metric matching multiplier", "gauge directions"], "tensor": "two TT modes have positive principal kinetic and gradient terms for C_partial>0", "connection": "transverse modes have positive principal kinetic and gradient terms for tau_A I_R>0", "scalar": "one massless neutral scalar has positive kinetic/gradient terms for Z_partial>0; homogeneous l=0 is flat, not tachyonic", "matching": "Lambda has no derivatives and no propagating mode", "open": ["quadratic expansion about the shifted junction solution", "bulk-boundary mixed spectrum", "junction stability", "potential-induced scalar mass"], "physical_negative_mode_claim": None},
        "boundary": {**c("BHSM_equatorial_intrinsic_physical_boundary_status_v6_1_3"), "status": "BHSM_EQUATORIAL_M4_INTRINSIC_BOUNDARY_DOMAIN_DERIVED_CONDITIONALLY", "support": "Lorentz-selected SO(5) orbit of equatorial great S3 hypersurfaces", "action": "frozen intrinsic EH+Yang-Mills+free-neutral-scalar action", "ontology": "provisional independent-field domain", "classification": "interface/boundary carrying an independent intrinsic action, conditional on Boundary Axiom B1", "parent_derivation": False, "unique_axis": False, "background_solution": "shifted junction solution required"},
        "current": {**c("BHSM_intrinsic_boundary_current_normalization_v6_1_3"), "status": "BHSM_INTRINSIC_BOUNDARY_CURRENT_STRUCTURE_PARTIAL", "equation": "D_nu F^{nu mu,a}=g_partial J_can^{mu,a}", "canonical_coupling": "g_partial=(tau_A I_R)^(-1/2)", "sigma_current": 0, "pure_connection": "non-Abelian self-current is fixed by cubic and quartic gauge identities", "representation_weights": "geometric labels inherited from the parent associated bundle", "continuity": "D_mu J^mu=0 when matter and matching equations hold", "bulk_flux": "zero in the minimal independent-connection freeze", "observed_charge": None, "magnetic_current": None},
        "aperture": {**c("BHSM_intrinsic_M4_aperture_readiness_v6_1_3"), "status": "BHSM_INTRINSIC_M4_APERTURE_REMAINS_INCOMPLETE", "connection_normalization": "tau_A I_R", "intrinsic_support": "no normal profile integral", "matter_normalization": None, "representation_projector": None, "geometric_overlap": None, "candidate": "e_eff^2=g_partial^2 |I_R,overlap|^2/N_A when the missing matter/projector data close", "amplitude_square_distinguished": True, "e_eff": None, "alpha": None},
        "parent_map": {**c("BHSM_intrinsic_boundary_parent_to_v5_v4_map_v6_1_3"), "status": "BHSM_INTRINSIC_BOUNDARY_PARENT_MAP_ADVANCED_CONDITIONALLY", "map": {"gravity": "boundary-axiom-derived intrinsic C_partial action; source open", "Sp1_connection": "boundary-axiom-derived intrinsic tau_A action with parent representation data", "nested_U1": "constrained component/weight, not independently counted", "scalar_kinetic": "boundary-axiom-derived; Z_partial convention-removable while free", "scalar_quadratic": "unresolved", "scalar_quartic": "unresolved", "sigma_normalization": "canonical only, no v5 value", "charged": "current architecture partial; physical map open", "neutral": "free boundary scalar only; response map open", "boundary": "B1 provisional plus exact metric matching", "scale_RG": "a_min symbolic; no RG or unit claim", "recycling": "unchanged"}, "A_ST": "not derived", "G_ST": "not derived", "frozen_values_changed": False},
        "fermionic": {**c("BHSM_M4_first_order_fermionic_action_readiness_v6_1_3"), "status": "BHSM_M4_FIRST_ORDER_FERMIONIC_ACTION_READINESS_DERIVED", "spin_structure": "I_t x S3 is spin", "Clifford_bundle": "defined from the intrinsic Lorentzian metric and orthonormal frame", "spin_connection": "intrinsic Levi-Civita spin connection", "gauge_representation": "parent associated-bundle representation data available", "scalar_coupling_candidate": "possible only after a BHSM-native fermionic action and sigma role are derived", "self_adjoint_domain": "architecture available but not selected", "conserved_inner_product": "candidate follows from a future action and globally hyperbolic domain", "physical_first_order_action": None, "physical_Dirac_equation": None, "monopole_dependency": None},
        "scale": {**c("BHSM_intrinsic_boundary_scale_primitive_audit_v6_1_3"), "status": "BHSM_INTRINSIC_BOUNDARY_SCALE_REMAINS_PRIMITIVE", "kappa_0": "parent primitive", "kappa_1": "parent primitive", "a_min_squared": "21 kappa_1/(2 kappa_0)", "beta_partial": "provisional and not derived", "boundary_coefficients": {"C_partial": "independent source; physical combination C_partial a_min^2", "tau_A": "independent source up to fixed trace convention", "Z_partial": "canonical convention while scalar is free; physical once a scalar source is added"}, "potential_primitives": [], "absolute_unit": None, "a_min_called_absolute": False},
        "hidden": {**c("BHSM_intrinsic_boundary_hidden_input_claim_audit_v6_1_3"), "status": "BHSM_INTRINSIC_BOUNDARY_HIDDEN_INPUTS_EXPOSED", "provisional": ["Boundary Axiom B1", "existence of intrinsic boundary fields", "positive C_partial, tau_A, Z_partial", "exact metric matching"], "derived": ["trace-field no-cancellation theorem", "intrinsic Lorentz principal symbols", "canonical normalization formulas", "two-invariant pre-potential count", "old round-junction residual"], "not_derived": ["one-normalization coefficient lock", "boundary coefficient values", "shifted background", "scalar potential", "full mixed spectrum", "physical gauge interpretation", "fermionic action", "absolute unit"], "not_imported": ["A_ST=-2", "G_ST=8", "sigma=1/2", "Planck mass", "gauge couplings", "alpha", "masses", "CKM", "PMNS", "cosmological parameters", "magnetic charge"]},
        "report": {**c("BHSM_minimal_equatorial_boundary_action_report_v6_1_3"), "status": PRIMARY_RESULT, "subsidiary_results": ["BHSM_SMOOTH_TRACE_FIELD_FINITE_BOUNDARY_TERM_CANNOT_CLOSE_EXACT_LORENTZ", "BHSM_INTRINSIC_BOUNDARY_FIELD_FORMULATION_REQUIRED_FOR_EXACT_M4_LORENTZ", "BHSM_BOUNDARY_ONE_NORMALIZATION_HYPOTHESIS_UNDERDETERMINED", "BHSM_M4_INTRINSIC_GRAVITY_ACTION_DERIVED_CONDITIONALLY", "BHSM_M4_INTRINSIC_CONNECTION_ACTION_DERIVED_CONDITIONALLY", "BHSM_M4_INTRINSIC_SIGMA_KINETIC_ACTION_DERIVED_CONDITIONALLY", "BHSM_BOUNDARY_SIGMA_KINETIC_ACTION_DERIVED_POTENTIAL_OPEN", "BHSM_EQUATORIAL_M4_INTRINSIC_BOUNDARY_DOMAIN_DERIVED_CONDITIONALLY", "BHSM_M4_FIRST_ORDER_FERMIONIC_ACTION_READINESS_DERIVED"], "central_answer": "Boundary Axiom B1 consistently freezes independent intrinsic h_mu_nu, A_mu, and sigma_partial fields on Lorentz-selected equatorial support. Their Einstein-Hilbert, Yang-Mills, and free-scalar action has exact M4 Lorentz principal symbols and healthy principal kinetics for positive coefficients. A finite intrinsic term cannot repair the mismatch of a smooth bulk trace, so the independent-field distinction is essential. The proposed one-normalization lock is underdetermined: dimensions fix powers of a_min and representation traces fix only the connection convention, leaving two physical invariant combinations before a scalar potential or scalar matching is introduced and three independently sourced raw coefficients. The old K_mu_nu=0 round equator is not an exact solution after adding C_partial R4 because its nonzero intrinsic Einstein tensor leaves a junction residual. Thus the action is a conditional boundary-axiom construction requiring multiple coefficient sources and a shifted bulk-boundary background; it is not parent-derived closure.", "derived": ["trace-versus-intrinsic theorem", "frozen minimal action and prohibited-term ledger", "exact metric-multiplier matching architecture", "coefficient-lock underdetermination", "pre-potential invariant count", "intrinsic Lorentz principal structure", "canonical gravity/connection/scalar formulas", "round-junction backreaction obstruction"], "conditional": ["well-posed induced-metric matching", "healthy principal kinetic sectors", "intrinsic physical-boundary interpretation", "first-order fermionic readiness"], "open": ["boundary coefficient sources", "shifted background", "full mixed stability spectrum", "scalar potential", "aperture", "physical gauge and fermion interpretations", "absolute unit", "Standard Model limit"], "completion_gate": COMPLETION_GATE, "recommended_next_branch": "bhsm-boundary-coefficient-source-theorem-v6-1-4", "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE"},
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    paths: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def boundary_action_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def boundary_action_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.1.3 Minimal Equatorial Boundary Action Freeze",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"
