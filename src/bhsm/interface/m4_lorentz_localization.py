"""BHSM v6.1.2 Lorentz-selected equatorial localization audit."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


VERSION = "v6.1.2"
SPRINT = "bhsm-m4-boundary-localization-action-source-v6-1-2"
PRIMARY_RESULT = "BHSM_M4_LORENTZ_SELECTED_LOCALIZATION_DERIVED"
COMPLETION_GATE = "V6_1_2_LORENTZ_SELECTS_GREAT_S3_SUPPORT_MINIMAL_BOUNDARY_ACTION_UNSOURCED"

ARTIFACT_FILES = {
    "scalar_theorem": "BHSM_M4_scalar_Lorentz_localization_theorem_v6_1_2.json",
    "connection_theorem": "BHSM_M4_connection_Lorentz_localization_theorem_v6_1_2.json",
    "gravity": "BHSM_M4_gravitational_Lorentz_normalization_audit_v6_1_2.json",
    "mismatch": "BHSM_M4_Lorentz_mismatch_functionals_v6_1_2.json",
    "orbit": "BHSM_M4_great_S3_orbit_selection_theorem_v6_1_2.json",
    "p1_source": "BHSM_P1_equatorial_boundary_source_audit_v6_1_2.json",
    "z2": "BHSM_M4_Z2_hemisphere_junction_ledger_v6_1_2.json",
    "collar": "BHSM_M4_exact_collar_geometry_v6_1_2.json",
    "sigma_test": "BHSM_existing_sigma_localization_test_v6_1_2.json",
    "sigma_coupling": "BHSM_sigma_supported_localization_coupling_audit_v6_1_2.json",
    "boundary_source": "BHSM_M4_intrinsic_boundary_action_source_map_v6_1_2.json",
    "lovelock": "BHSM_M4_P2_P3_boundary_completion_audit_v6_1_2.json",
    "bulk_induction": "BHSM_M4_controlled_bulk_mode_induction_audit_v6_1_2.json",
    "sturm": "BHSM_M4_localized_Sturm_Liouville_operators_v6_1_2.json",
    "scalar_profile": "BHSM_M4_localized_scalar_profile_v6_1_2.json",
    "connection_profile": "BHSM_M4_localized_connection_profile_v6_1_2.json",
    "tensor": "BHSM_M4_tensor_localization_audit_v6_1_2.json",
    "common_action": "BHSM_M4_common_localized_action_v6_1_2.json",
    "currents": "BHSM_M4_localized_current_charge_normalization_v6_1_2.json",
    "aperture": "BHSM_M4_localized_aperture_gate_v6_1_2.json",
    "fermionic": "BHSM_fermionic_localization_readiness_v6_1_2.json",
    "scale": "BHSM_M4_localization_scale_primitive_audit_v6_1_2.json",
    "parent_v5": "BHSM_localization_parent_to_v5_v4_map_v6_1_2.json",
    "hidden": "BHSM_M4_localization_hidden_input_claim_audit_v6_1_2.json",
    "report": "BHSM_M4_Lorentz_selected_localization_report_v6_1_2.json",
}

GUARDS = {
    "v6_1_1_geometry_preserved": True,
    "physical_fermion_equation_assumed": False,
    "magnetic_monopole_sector_used": False,
    "monopole_harmonics_used": False,
    "chern_data_called_magnetic_charge": False,
    "magnetic_charge_operator_exists": False,
    "preferred_equator_invented": False,
    "z2_fixed_set_called_brane": False,
    "smooth_profile_called_exactly_Lorentz_normalized": False,
    "delta_boundary_term_added": False,
    "boundary_kinetic_term_added": False,
    "compactification_length_invented": False,
    "L_eff_invented": False,
    "standard_model_group_or_charge_assigned": False,
    "measured_Lorentz_bound_used": False,
    "measured_input_used": False,
    "alpha_evaluated": False,
    "v5_potential_imported": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all radii and profile powers must be positive")


def cosine_power_integral(power: float) -> float:
    if power <= -1:
        raise ValueError("the full-collar cosine-power integral requires power>-1")
    return math.sqrt(math.pi) * math.exp(
        math.lgamma((power + 1) / 2) - math.lgamma((power + 2) / 2)
    )


def power_collar_normalizations(power: float, a: float) -> dict[str, float]:
    """Exact weights for |u|^2=sin(chi)^power=cos(y)^power."""
    _positive(power, a)
    nt = a * cosine_power_integral(power + 3)
    ns = a * cosine_power_integral(power + 1)
    ne = ns
    nb = a * cosine_power_integral(power - 1)
    return {
        "N_t": nt,
        "N_s": ns,
        "N_E": ne,
        "N_B": nb,
        "delta_scalar": ns / nt - 1,
        "delta_connection": nb / ne - 1,
        "concentration_width_over_a": 1 / math.sqrt(power),
    }


def power_collar_closed_form(power: float) -> dict[str, float]:
    _positive(power)
    epsilon_squared = 1 / power
    return {
        "delta_scalar": 1 / (power + 2),
        "delta_connection": 1 / power,
        "epsilon_squared": epsilon_squared,
        "scalar_c2": 1.0,
        "scalar_c4": -2.0,
        "connection_c2": 1.0,
        "connection_c4": 0.0,
    }


def boundary_augmented_mismatch(temporal: float, spatial: float, boundary_coefficient: float) -> float:
    if temporal <= 0 or spatial < temporal or boundary_coefficient < 0:
        raise ValueError("require 0<N_t<=N_s and a nonnegative boundary coefficient")
    return (spatial + boundary_coefficient) / (temporal + boundary_coefficient) - 1


def inverse_scalar_trap(power: float, y: float, a: float) -> float:
    """V for which u=cos(y)^(power/2) solves (L/a^2+V)u=0."""
    _positive(power, a)
    if not -math.pi / 2 < y < math.pi / 2:
        raise ValueError("y must lie inside the open collar chart")
    alpha = power / 2
    return (-alpha + alpha * (alpha + 2) * math.tan(y) ** 2) / a**2


def sigma_stationary_points(A0: float, G0: float) -> list[float]:
    points = [0.0]
    if A0 < 0 and G0 > 0:
        value = math.sqrt(-A0 / G0)
        points.extend([-value, value])
    return points


def sigma_kink_conditions(Zsigma: float, A0: float, G0: float) -> dict[str, Any]:
    _positive(Zsigma)
    exists_algebraically = A0 < 0 and G0 > 0
    return {
        "exists_algebraically": exists_algebraically,
        "vacuum_magnitude": math.sqrt(-A0 / G0) if exists_algebraically else None,
        "flat_wall_width": math.sqrt(2 * Zsigma / (-A0)) if exists_algebraically else None,
        "round_S4_profile_stability_derived": False,
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "Exact Lorentz normalization selects the SO(5) orbit of equatorial support. The existing action does not generate the required independent boundary dynamics. No preferred axis, observed spacetime, Standard Model map, physical fermion equation, monopole sector, measured input, absolute unit, or full-BHSM claim follows.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    return {
        "scalar_theorem": {**c("BHSM_M4_scalar_Lorentz_localization_theorem_v6_1_2"), "status": "BHSM_M4_SCALAR_LORENTZ_LOCALIZATION_THEOREM_DERIVED", "functionals": {"N_t": "a integral_I sin^3(chi) w(chi)dchi", "N_s": "a integral_I sin(chi) w(chi)dchi", "difference": "N_s-N_t=a integral_I sin(chi)cos^2(chi)w(chi)dchi"}, "inequality": "N_t<=N_s for every nonnegative integrable profile density", "equality_measure_support": "sin chi cos^2 chi=0 almost everywhere on the support", "pole": "sin chi=0 collapses S3 and gives no finite nonzero M4 kinetic normalization", "physical_equality_support": "chi=pi/2", "smooth_nonzero_bulk_profile": "strict inequality", "finite_width_collar": "positive mismatch", "exact_boundary_distribution": "can satisfy equality if an independent boundary action/domain defines it"},
        "connection_theorem": {**c("BHSM_M4_connection_Lorentz_localization_theorem_v6_1_2"), "status": "BHSM_M4_CONNECTION_LORENTZ_LOCALIZATION_THEOREM_DERIVED", "functionals": {"N_E": "a integral_I sin(chi)|u_A|^2dchi", "N_B": "a integral_I |u_A|^2/sin(chi)dchi", "difference": "N_B-N_E=a integral_I cos^2(chi)|u_A|^2/sin(chi)dchi"}, "inequality": "N_E<=N_B whenever both integrals are finite", "equality_support": "chi=pi/2", "pole": "N_B diverges unless the tangential profile vanishes sufficiently; pole support is not M4", "smooth_nonzero_bulk_profile": "strict inequality", "action_source": "separate gate"},
        "gravity": {**c("BHSM_M4_gravitational_Lorentz_normalization_audit_v6_1_2"), "status": "BHSM_M4_GRAVITATIONAL_LORENTZ_NORMALIZATION_AUDITED", "principal_tensor_weights": {"temporal": "a integral sin^3 chi |u_T|^2", "S3_gradient": "a integral sin chi |u_T|^2"}, "mismatch": "same nonnegative principal-symbol difference as the scalar theorem", "constraints": ["lapse and normal components are constrained", "tangential TT domain must be regular at collapsed S3 orbits", "full gauge-fixed tensor Hessian remains required"], "smooth_common_EH_coefficient": False, "localization_requirement": "equatorial boundary-supported tensor action or an independently derived distributional profile", "observed_Planck_scale": None},
        "mismatch": {**c("BHSM_M4_Lorentz_mismatch_functionals_v6_1_2"), "status": "BHSM_M4_LORENTZ_MISMATCH_FUNCTIONALS_DERIVED", "definitions": {"scalar": "delta_L,sigma=N_s/N_t-1", "connection": "delta_L,A=N_B/N_E-1", "tensor_principal": "delta_L,T=N_s,T/N_t,T-1"}, "positivity": "all are nonnegative on their finite admissible domains", "declared_family": "w_p=sin^p chi=cos^p y, p>0; epsilon=width/a:=p^-1/2", "exact_family": {"scalar": "1/(p+2)", "connection": "1/p", "tensor_principal": "1/(p+2)"}, "small_width": {"scalar": "epsilon^2-2epsilon^4+O(epsilon^6)", "connection": "epsilon^2", "tensor_principal": "epsilon^2-2epsilon^4+O(epsilon^6)"}, "measured_bound_comparison": None},
        "orbit": {**c("BHSM_M4_great_S3_orbit_selection_theorem_v6_1_2"), "status": "BHSM_M4_LORENTZ_SYMMETRY_SELECTS_GREAT_S3_ORBIT", "selection": "finite nonzero exact Lorentz kinetic equality selects support on a totally geodesic reflection-fixed great S3", "orbit": "all representatives form one SO(5)-equivalent orbit", "unique_representative": False, "orientation": "hemisphere/outward-normal choice remains boundary data", "interpretation": "support class selected; action source and representative selection remain separate"},
        "p1_source": {**c("BHSM_P1_equatorial_boundary_source_audit_v6_1_2"), "status": "BHSM_P1_INTRINSIC_BOUNDARY_KINETIC_SOURCE_ABSENT", "bulk_EH": "produces bulk equations and Gauss-Codazzi terms, not independent equatorial fields", "GHY": "coefficient-locked variational completion; K=0 on the background; no intrinsic kinetic dynamics", "cutting": "does not create physical degrees of freedom", "distributional_curvature": "requires a nonzero junction/source rather than following from the smooth round metric", "automatic_terms": {"C_partial_R4": False, "tau_A_F2": False, "Z_partial_Dsigma2": False}, "Brown_York_background": 0},
        "z2": {**c("BHSM_M4_Z2_hemisphere_junction_ledger_v6_1_2"), "status": "BHSM_M4_Z2_BOUNDARY_CONDITIONS_DERIVED_DYNAMICS_ABSENT", "construction": "two smooth hemispheres joined at chi=pi/2 or one hemisphere quotiented by chi<->pi-chi", "metric": "continuous", "K_jump": 0, "Israel_architecture": "2C5([K_mn]-[K]h_mn)=-S_mn in the declared orientation convention", "surface_stress_background": 0, "factor_two": "two outward-normal GHY terms when both cut sides are retained", "parity": {"even": "Neumann", "odd": "Dirichlet"}, "independent_boundary_dynamics": False, "brane_claim": False},
        "collar": {**c("BHSM_M4_exact_collar_geometry_v6_1_2"), "status": "BHSM_M4_EXACT_EQUATORIAL_COLLAR_GEOMETRY_DERIVED", "coordinate": "y=chi-pi/2", "metric": "ds5^2=-dt^2+a(t)^2[dy^2+cos^2(y)dOmega3^2]", "measure": "sqrt(-g5)=a^4 cos^3(y)sqrt(gamma3)", "proper_t0": "rho=a(t0)y", "time_warning": "rho=a(t)y over an interval generates time-normal cross terms", "series": "cos y=1-y^2/2+y^4/24+O(y^6)", "geometry": "measure is concentrated toward the equator but the scalar constant mode remains extended", "bound_state_from_round_geometry": False, "action_trapping": "requires V_loc, a boundary field, or another derived source"},
        "sigma_test": {**c("BHSM_existing_sigma_localization_test_v6_1_2"), "status": "BHSM_SIGMA_COLLAR_PROFILE_CONDITIONS_DERIVED_SOURCE_OPEN", "equation": "-(Zsigma/sin^3 chi)partial_chi(sin^3 chi partial_chi sigma_bar)+a^2 U_parent'(sigma_bar)=0", "constant": "U_parent'(sigma_bar)=0", "current_background": "constant sigma branch only; no nonconstant profile selected", "kink": "odd, crosses zero at the equator, and requires degenerate opposite vacua; algebraically A0<0,G0>0 for the declared quartic", "lump": "even positive maximum; not the same as a kink and not stabilized by the current source ledger", "domain_wall": "conditional on coefficient signs, boundary/parity data, and a full stability solution", "coefficients_selected": False, "v5_values_used": False},
        "sigma_coupling": {**c("BHSM_sigma_supported_localization_coupling_audit_v6_1_2"), "status": "BHSM_SIGMA_DOES_NOT_LOCALIZE_OTHER_SECTORS_IN_FROZEN_P1", "present": "neutral sigma kinetic, primitive polynomial, and declared chi coupling", "absent": ["f_A(sigma)F^2", "f_g(sigma)R", "sigma-dependent connection mass", "sigma-dependent tensor kinetic coefficient", "boundary Robin source for other fields"], "minimal_new_functions": {"connection": "positive even f_A(sigma) of dimension L^-1 in M5, concentrated on the wall", "gravity": "positive even f_g(sigma) of dimension L^-3 in M5", "other_scalar": "positive kinetic or mass profile with representation-compatible symmetry"}, "inserted": False},
        "boundary_source": {**c("BHSM_M4_intrinsic_boundary_action_source_map_v6_1_2"), "status": "BHSM_M4_MINIMAL_INTRINSIC_BOUNDARY_ACTION_FAMILY_IDENTIFIED_UNSOURCED", "terms": [{"coefficient": "C_partial", "term": "integral sqrt(-h) R4", "dimension": "L^-2", "source": None}, {"coefficient": "tau_A", "term": "-1/4 integral sqrt(-h) F^2", "dimension": "L^0", "source": None}, {"coefficient": "Z_partial", "term": "-1/2 integral sqrt(-h)(D sigma)^2", "dimension": "L^-2", "source": None}], "variation": "intrinsic Einstein tensor, boundary Yang-Mills equation/current, and boundary scalar wave operator enter their junction conditions", "finite_coefficient_effect": "adds the same Lorentz coefficient B to temporal and spatial terms but leaves N_s-N_t unchanged", "exact_closure": "requires a boundary-only field sector, vanishing bulk contribution, a distributional support theorem, or an independently derived compensating action", "independent_primitives_minimum": 3, "coefficient_lock_theorem": None},
        "lovelock": {**c("BHSM_M4_P2_P3_boundary_completion_audit_v6_1_2"), "status": "BHSM_P2_P3_BOUNDARY_COMPLETION_INSUFFICIENT_AT_EQUATOR", "P2": "Gauss-Bonnet with independent kappa2 and Myers B2", "P3": "cubic Lovelock with independent kappa3 and Myers B3", "dimensions_D8": {"kappa2": "L^-4", "kappa3": "L^-2"}, "equator": "standard Dirichlet boundary polynomials contain extrinsic-curvature factors and have zero background value at K_mn=0", "variation": "cancels higher-curvature normal variations; it is not an independent boundary-field kinetic action", "near_collar": "K is odd under y->-y, so a symmetric two-side construction supplies no positive even trap automatically", "selected": False},
        "bulk_induction": {**c("BHSM_M4_controlled_bulk_mode_induction_audit_v6_1_2"), "status": "BHSM_TREE_BULK_MODE_INDUCTION_DOES_NOT_CLOSE_LOCALIZATION", "split": "Phi=phi0 u0+sum_n>0 phi_n u_n", "equation": "O_H phi_H=J_H", "solution": "phi_H=O_H^-1 J_H+...", "pure_constant_sigma": "orthogonality makes J_H=0 for a local polynomial of the constant normal mode", "boundary_data": "can source heavy modes only after a boundary source/domain is supplied", "induced": "spectral-denominator nonlocal kernels and controlled derivative corrections", "local_boundary_primitive": False, "quantum_loop_included": False, "time_control": "v6.1 epsilon floor 1/3 prevents a parametrically small global time-EFT claim"},
        "sturm": {**c("BHSM_M4_localized_Sturm_Liouville_operators_v6_1_2"), "status": "BHSM_M4_LOCALIZED_PROFILE_OPERATOR_FAMILY_DERIVED_SOURCE_OPEN", "scalar": "L_chi u+a^2 V_loc u=mu u", "weight": "sin^3 chi", "power_profile": "u_p=sin^(p/2)chi is a zero mode only for V_p=a^-2[-p/2+(p/2)(p/2+2)cot^2 chi]", "width": "ell_p=a/sqrt(p)", "delta_matching": "continuity of u and [sin^3 chi u']=eta u at an explicitly declared interface sign convention", "Robin": "u'+a r u=0 with real r", "boundary_kinetic": "produces an eigenvalue-dependent matching term and does not by itself remove bulk mismatch", "self_adjoint": "real V, eta, r with the declared Green-form domain", "source": None},
        "scalar_profile": {**c("BHSM_M4_localized_scalar_profile_v6_1_2"), "status": "BHSM_M4_SCALAR_COLLAR_PROFILE_DIAGNOSTIC_NOT_ACTION_DERIVED", "family": "|u_p|^2=sin^p chi, p>0", "classification": "smooth finite-width collar profile", "width": "a/sqrt(p)", "normal_gap": None, "leakage": "nonzero for every finite p", "Lorentz_mismatch": "1/(p+2)>0", "exact_limit": "p->infinity is distributional equatorial support", "stability": None},
        "connection_profile": {**c("BHSM_M4_localized_connection_profile_v6_1_2"), "status": "BHSM_M4_CONNECTION_LOCALIZATION_PROFILE_SOURCE_OPEN", "family_diagnostic": "|u_A|^2=sin^p chi, p>0 gives finite weights", "Lorentz_mismatch": "1/p>0", "exact_limit": "distributional equatorial support", "gauge_covariance": "requires a boundary gauge field or gauge-compatible bulk/interface domain", "K4": None, "g4_geom": None, "cubic": None, "quartic": None, "normal_gap": None, "nested_U1": "remains a constrained component"},
        "tensor": {**c("BHSM_M4_tensor_localization_audit_v6_1_2"), "status": "BHSM_M4_TENSOR_LOCALIZATION_SOURCE_OPEN", "candidate": "tangential transverse-traceless M4 tensor candidate", "principal_profile": "same collar mismatch 1/(p+2) for the diagnostic power family", "exact_mode": None, "boundary_kinetic_support": "unsourced intrinsic C_partial term", "mixing": "bulk tensor and constrained scalar/normal components remain", "polarizations": "not physically counted before the boundary gauge/domain Hessian closes", "observed_graviton": False},
        "common_action": {**c("BHSM_M4_common_localized_action_v6_1_2"), "status": "BHSM_M4_COMMON_LOCALIZED_ACTION_PARTIAL", "exact": ["equatorial induced geometry", "support-selection inequalities", "P1/GHY source absence", "Z2 boundary conditions"], "profile_derived": ["finite-width mismatch functionals", "conditional scalar parent coefficients"], "open_boundary_terms": ["C_partial R4", "tau_A F2", "Z_partial(D sigma)^2"], "controlled": ["nonlocal O_H^-1 bulk-mode corrections where the spectral regime holds"], "unresolved": ["boundary-field ontology/action source", "coefficient lock", "regular localized gauge/tensor modes", "currents", "aperture", "fermionic action"]},
        "currents": {**c("BHSM_M4_localized_current_charge_normalization_v6_1_2"), "status": "BHSM_M4_LOCALIZED_CURRENTS_REMAIN_PROFILE_CONDITIONAL", "Sp1": "J_mu^a requires localized matter and connection profiles plus the generator trace", "U1": "q=2m remains a nested geometric weight if independently retained", "conservation": "requires a common gauge-compatible self-adjoint boundary action/domain", "boundary_flux": "fixed by the eventual junction condition", "canonical_coupling": None, "observed_charge": None, "magnetic_charge": None},
        "aperture": {**c("BHSM_M4_localized_aperture_gate_v6_1_2"), "status": "BHSM_M4_APERTURE_INPUTS_NOT_COMPLETE", "profiles": "diagnostic scalar collar only; no action-derived connection/matter profiles", "normalizations": "finite-width N values derived but not exact Lorentz coefficients", "overlap": None, "projector": None, "e_eff": None, "alpha": None, "freeze_candidate": None},
        "fermionic": {**c("BHSM_fermionic_localization_readiness_v6_1_2"), "status": "BHSM_FERMIONIC_LOCALIZATION_READINESS_DERIVED", "available": ["great-S3 support orbit", "induced spin and Clifford bundles", "spin connection", "Z2 parity choices", "self-adjoint boundary-domain architecture", "geometric Sp1 representations and nested weights"], "normal_spinorial_profile": None, "localized_action_source": None, "physical_equation": None, "monopole_dependency": None, "future_status": "a first-order candidate action can be posed only after the boundary field/action source is frozen"},
        "scale": {**c("BHSM_M4_localization_scale_primitive_audit_v6_1_2"), "status": "BHSM_M4_LOCALIZATION_PRIMITIVES_EXPOSED", "a_min_squared": "21 kappa1/(2 kappa0)", "diagnostic_width": "ell_p=a/sqrt(p)", "width_status": "p is not selected by round geometry or the frozen action", "normal_gap": None, "added_primitives_this_sprint": 0, "minimum_new_boundary_coefficients": ["C_partial", "tau_A", "Z_partial"], "additional_profile_source": "V_loc/Robin or a boundary-only field statement unless bulk contributions are removed", "single_primitive_suffices": False, "absolute_unit": None},
        "parent_v5": {**c("BHSM_localization_parent_to_v5_v4_map_v6_1_2"), "status": "BHSM_LOCALIZATION_PARENT_TO_V5_V4_MAP_ADVANCED", "map": {"gravity": "equatorial support selected; C_partial unsourced", "boundary_geometry": "exact P1/GHY/Z2 ledger", "Sp1": "support selected; tau_A/profile unsourced", "nested_U1": "constrained; no independent localization", "scalar_kinetic": "support selected; Z_partial/profile unsourced", "A_ST": "not derived", "G_ST": "not derived", "sigma_scale": "conditional parent stationary points only", "charged": "localized current and physical map open", "neutral": "localized response and physical map open", "boundary_collar": "minimal action family identified, not sourced", "scale_RG": "width/time dependence is not RG running", "recycling": "unchanged"}, "historical_values_changed": False},
        "hidden": {**c("BHSM_M4_localization_hidden_input_claim_audit_v6_1_2"), "status": "BHSM_M4_LOCALIZATION_HIDDEN_INPUTS_EXPOSED", "derived": ["Lorentz inequalities", "equality support", "great-S3 orbit", "P1/GHY absence", "collar geometry", "power-profile mismatch"], "diagnostic_not_input": ["p", "ell_p", "inverse trap V_p"], "missing": ["boundary field/action source", "C_partial", "tau_A", "Z_partial", "coefficient lock", "localized gauge/tensor profiles", "aperture projector", "fermionic action"], "not_imported": ["measured Lorentz bounds", "Planck scale", "gauge couplings", "alpha", "1/137", "masses", "CKM", "PMNS", "cosmological parameters", "magnetic charge quantization"]},
        "report": {**c("BHSM_M4_Lorentz_selected_localization_report_v6_1_2"), "status": PRIMARY_RESULT, "action_status": "BHSM_M4_EQUATORIAL_LOCALIZATION_SOURCE_SELECTED_ACTION_OPEN", "central_answer": "For every admissible nonnegative scalar, connection, or principal tensor profile, the spatial/magnetic normalization is at least the temporal/electric normalization. Finite nonzero exact equality excludes the collapsed poles and selects support on the SO(5) orbit of totally geodesic equatorial great S3 hypersurfaces. Every ordinary smooth bulk or finite-width collar profile has positive mismatch; the exact cosine-power family gives delta_sigma=delta_tensor=1/(p+2) and delta_A=1/p. P1 plus GHY, a smooth Z2 cut, round collar geometry, the unspecialized sigma sector, P2/P3 completion, and tree-level bulk-mode integration do not generate independent exact boundary kinetics. A finite boundary kinetic coefficient dilutes but does not cancel the bulk mismatch. Exact physical M4 closure therefore requires a separately sourced boundary-only/distributional field action or a new coefficient-locked decoupling theorem; at least C_partial, tau_A, and Z_partial are presently independent, so no single hidden primitive is claimed.", "derived": ["scalar and connection Lorentz-localization theorems", "principal tensor normalization audit", "great-S3 support-orbit selection", "finite-width mismatch expansion", "P1/GHY source-absence theorem", "Z2/collar ledgers", "minimal boundary-action family", "modified profile operator family", "fermionic localization readiness"], "conditional": ["sigma kink/domain wall", "inverse-designed collar profile", "boundary-only M4 gravity/gauge/scalar action", "currents and aperture"], "constructive_requirements": ["derive or freeze a minimal equatorial boundary-field action", "test coefficient locking versus at least three primitives", "derive regular localized gauge and tensor domains", "derive fermionic action without monopoles"], "completion_gate": COMPLETION_GATE, "recommended_next_branch": "bhsm-minimal-equatorial-boundary-action-freeze-v6-1-3", "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE"},
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def localization_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def localization_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.1.2 M4 Lorentz-Selected Boundary Localization",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"
