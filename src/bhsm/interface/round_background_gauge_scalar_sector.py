"""BHSM v6.1 round-background gauge/scalar normalization."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

VERSION = "v6.1"
SPRINT = "bhsm-round-background-gauge-scalar-sector-v6-1"
PRIMARY_RESULT = "BHSM_ROUND_BACKGROUND_GAUGE_SCALAR_ACTION_DERIVED_CONDITIONALLY"

ARTIFACT_FILES = {
    "control": "BHSM_round_background_control_window_v6_1.json",
    "dimension": "BHSM_round_background_effective_dimension_firewall_v6_1.json",
    "sp1": "BHSM_round_Sp1_connection_normalization_v6_1.json",
    "u1": "BHSM_complex_Hopf_U1_normalization_v6_1.json",
    "ratio": "BHSM_round_connection_normalization_ratio_v6_1.json",
    "charges": "BHSM_round_canonical_multiplet_charge_operators_v6_1.json",
    "gauge": "BHSM_round_gauge_self_interaction_ledger_v6_1.json",
    "candidates": "BHSM_round_scalar_candidate_comparison_v6_1.json",
    "sigma": "BHSM_sigma_parent_identification_theorem_v6_1.json",
    "scalar_kinetic": "BHSM_round_scalar_kinetic_normalization_v6_1.json",
    "potential": "BHSM_parent_scalar_potential_source_map_v6_1.json",
    "tower": "BHSM_round_tower_induced_scalar_operators_v6_1.json",
    "hessian": "BHSM_round_constraint_reduced_scalar_modulus_hessian_v6_1.json",
    "gauge_scalar": "BHSM_round_gauge_scalar_interaction_map_v6_1.json",
    "aperture": "BHSM_geometric_aperture_readiness_v6_1.json",
    "coupling_dimension": "BHSM_M5_M4_coupling_dimension_ledger_v6_1.json",
    "parent_v5": "BHSM_parent_to_v5_bosonic_coefficient_map_v6_1.json",
    "spectrum": "BHSM_round_background_mode_spectrum_v6_1.json",
    "dirac": "BHSM_round_background_Dirac_forward_link_v6_1.json",
    "scale": "BHSM_round_background_scale_primitive_audit_v6_1.json",
    "hidden": "BHSM_round_background_hidden_input_claim_audit_v6_1.json",
    "report": "BHSM_round_background_gauge_scalar_report_v6_1.json",
}

GUARDS = {
    "v6_0_10_round_background_preserved": True,
    "jensen_selected_as_primary": False,
    "t0_called_static_universe": False,
    "effective_base_dimension": 5,
    "s4_identified_as_observed_spacetime": False,
    "sp1_identified_as_standard_model_group": False,
    "u1_identified_as_hypercharge": False,
    "geometric_weights_called_observed_charges": False,
    "time_normalization_called_rg_running": False,
    "compactification_length_invented": False,
    "measured_input_used": False,
    "v5_numbers_used_as_parent_inputs": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
    "physical_fermion_equation_assumed": False,
    "magnetic_monopole_sector_used": False,
    "monopole_harmonics_used": False,
    "chern_data_called_magnetic_charge": False,
    "magnetic_charge_quantization_imported": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all scales and positive kinetic coefficients must be positive")


def round_minimum(kappa0: float, kappa1: float) -> dict[str, float]:
    _positive(kappa0, kappa1)
    lam = kappa0 / kappa1
    a_min = math.sqrt(21 / (2 * lam))
    return {
        "lambda": lam,
        "a_min": a_min,
        "a_min_squared": a_min**2,
        "expansion_scale_squared": lam / 42,
        "gap_at_minimum_radius": lam / 14,
        "acceleration_to_gap": 1 / 3,
    }


def control_ratios(
    time_offset: float,
    kappa0: float,
    kappa1: float,
    energy_ratio_at_t0: float = 0.0,
    source_ratio: float = 0.0,
    amplitude_ratio: float = 0.0,
) -> dict[str, Any]:
    if min(energy_ratio_at_t0, source_ratio, amplitude_ratio) < 0:
        raise ValueError("control ratios must be nonnegative")
    minimum = round_minimum(kappa0, kappa1)
    x = math.sqrt(minimum["expansion_scale_squared"]) * time_offset
    sinh = math.sinh(x)
    sech2 = 1 / math.cosh(x) ** 2
    gap = minimum["gap_at_minimum_radius"] * sech2
    ratios = {
        "H_squared_over_gap": sinh**2 / 3,
        "gap_adiabaticity": 2 * abs(sinh) / math.sqrt(3),
        "Hdot_over_gap": 1 / 3,
        "energy_over_gap": energy_ratio_at_t0 / sech2,
        "source": source_ratio,
        "interaction_amplitude": amplitude_ratio,
    }
    return {"x": x, "gap": gap, "ratios": ratios, "epsilon_control": max(ratios.values())}


def control_window(epsilon_star: float, kappa0: float, kappa1: float) -> dict[str, Any]:
    _positive(epsilon_star, kappa0, kappa1)
    floor = 1 / 3
    if epsilon_star < floor:
        return {"exists": False, "epsilon_floor": floor, "reason": "Hdot/Delta=1/3 everywhere on the exact round branch"}
    h = math.sqrt((kappa0 / kappa1) / 42)
    sinh_bound = min(math.sqrt(3 * epsilon_star), math.sqrt(3) * epsilon_star / 2)
    half_width = math.asinh(sinh_bound) / h
    return {"exists": True, "epsilon_floor": floor, "half_width": half_width, "symbolic_condition": "|t-t0|<=asinh[min(sqrt(3 epsilon_star),sqrt(3)epsilon_star/2)]/sqrt(lambda/42)"}


def round_connection_coefficient(kappa1: float, a: float) -> float:
    _positive(kappa1, a)
    return 8 * math.pi**2 * kappa1 * a**5


def round_geometric_coupling(kappa1: float, a: float) -> float:
    return 1 / math.sqrt(round_connection_coefficient(kappa1, a))


def u1_normalization(kappa1: float, a: float, convention: str = "inherited_4pi") -> dict[str, float | str]:
    """Normalize the nested circle without promoting an independent M5 field."""
    kr = round_connection_coefficient(kappa1, a)
    if convention == "inherited_4pi":
        factor = 1.0
    elif convention == "unit_charge_2pi":
        factor = 4.0
    else:
        raise ValueError("unknown U(1) convention")
    return {
        "convention": convention,
        "M7_circle_coefficient": 2 * math.pi * kappa1 * a**3,
        "M5_pushforward_coefficient": factor * kr,
        "ratio_to_inherited_Sp1": factor,
        "canonical_interaction_ratio": 1 / math.sqrt(factor),
    }


def canonical_charge_operator(two_j: int, weight: int, kappa1: float, a: float) -> dict[str, Any]:
    if not isinstance(two_j, int) or isinstance(two_j, bool) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    if not isinstance(weight, int) or isinstance(weight, bool) or abs(weight) > two_j or (two_j - weight) % 2:
        raise ValueError("weight must be -two_j,-two_j+2,...,two_j")
    j = two_j / 2
    g5 = round_geometric_coupling(kappa1, a)
    return {
        "two_j": two_j,
        "J": j,
        "rank": two_j + 1,
        "casimir": j * (j + 1),
        "integral_u1_weight_q": weight,
        "magnetic_weight_m": weight / 2,
        "Sp1_generator_scale": g5,
        "unit_charge_U1_scale": g5 / 2,
        "U1_eigenvalue_coefficient": weight * g5 / 2,
        "physical_charge": None,
    }


def gauge_vertex_coefficients(kappa1: float, a: float, hubble: float = 0.0) -> dict[str, float]:
    g5 = round_geometric_coupling(kappa1, a)
    return {
        "quadratic": 1.0,
        "cubic": g5,
        "quartic": g5**2,
        "canonical_pump_rate": -5 * hubble / 2,
        "log_K_rate": 5 * hubble,
    }


def scalar_normalization(Zsigma: float, a: float) -> dict[str, float]:
    _positive(Zsigma, a)
    fiber_volume = 16 * math.pi**2 * a**3
    z5 = Zsigma * fiber_volume
    return {"fiber_volume": fiber_volume, "Z5": z5, "canonical_factor": math.sqrt(z5)}


def scalar_canonical_coefficients(
    Zsigma: float,
    A0: float,
    G0: float,
    a: float,
    background_lambda: float,
    chi_kinetic_invariant: float = 0.0,
    Zchi: float = 0.0,
    g: float = 0.0,
) -> dict[str, float]:
    _positive(Zsigma, a, background_lambda)
    norm = scalar_normalization(Zsigma, a)
    a_eff = A0 + Zchi * g * chi_kinetic_invariant
    return {
        "raw_A_eff": a_eff,
        "potential_mass_squared": a_eff / Zsigma,
        "t0_canonical_pump_mass_squared": -background_lambda / 28,
        "t0_operator_mass_squared": a_eff / Zsigma - background_lambda / 28,
        "canonical_quartic_5D": G0 / (Zsigma**2 * norm["fiber_volume"]),
        "canonical_cubic_at_sigma_zero": 0.0,
    }


def scalar_stationary_points(Aeff: float, G0: float) -> dict[str, Any]:
    points = [0.0]
    if G0 > 0 and Aeff < 0:
        value = math.sqrt(-Aeff / G0)
        points.extend([-value, value])
    return {"points": points, "nonzero_branch_condition": "A_eff<0 and G0>0", "coefficient_signs_selected": False}


def round_mode_row(two_j: int, kappa0: float, kappa1: float) -> dict[str, Any]:
    if not isinstance(two_j, int) or isinstance(two_j, bool) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    minimum = round_minimum(kappa0, kappa1)
    j = two_j / 2
    eigenvalue = j * (j + 1) / minimum["a_min_squared"]
    return {
        "two_j": two_j,
        "J": j,
        "eigenvalue_t0": eigenvalue,
        "associated_rank_per_weight": two_j + 1,
        "u1_weights": list(range(-two_j, two_j + 1, 2)),
        "total_round_S3_degeneracy": (two_j + 1) ** 2,
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "This is a parent M8-to-effective-M5 geometric bosonic normalization. It does not derive a physical M4 action, Standard Model groups or charges, measured couplings, particles, masses, or full BHSM.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    spectrum_rows = [round_mode_row(two_j, 1.0, 1.0) for two_j in range(5)]
    payloads = {
        "control": {**c("BHSM_round_background_control_window_v6_1"), "status": "BHSM_ROUND_T0_INSTANTANEOUS_NORMALIZATION_DERIVED_STRICT_WINDOW_OPEN", "trajectory": "a=a_min cosh[sqrt(lambda/42)(t-t0)]", "minimum_slice": "a_min^2=21/(2lambda), H(t0)=0", "gap": "Delta(t)=lambda sech^2(x)/14; Delta(t0)=lambda/14", "ratios": {"H2_over_Delta": "sinh^2(x)/3", "gap_adiabaticity": "2|sinh(x)|/sqrt(3)", "Hdot_over_Delta": "1/3"}, "epsilon": "max of the displayed background ratios, E^2/Delta, source ratio, and interaction-amplitude ratio", "strict_result": "epsilon_control has an exact 1/3 floor, so no epsilon_star<<1 window exists under the full requested criterion", "interpretation": "t0 is an exact instantaneous normalization surface, not a static universe or a parametrically adiabatic slice"},
        "dimension": {**c("BHSM_round_background_effective_dimension_firewall_v6_1"), "status": "BHSM_EFFECTIVE_BASE_DIMENSION_5D_CONFIRMED", "M8": "I_t x S7", "M7_intermediate": "I_t x CP3 after S1 pushforward", "M5": "I_t x S4 after full S3 pushforward", "fiber": "Berger S3, round on the selected branch", "unresolved_M4": "physical boundary, collar, quotient, localization, hypersurface action, or further reduction not selected", "coefficient_layers": {"parent": ["kappa0", "kappa1", "Zchi", "Zsigma", "A0", "G0", "g"], "M5": ["K_R", "Z5", "A5", "G5", "g5_geom"], "M4": "requires an explicit additional measure/reduction map"}},
        "sp1": {**c("BHSM_round_Sp1_connection_normalization_v6_1"), "status": "BHSM_ROUND_SP1_CONNECTION_NORMALIZATION_DERIVED", "action": "S_A=-1/4 integral_M5 sqrt(-g5) K_R(a) F^a_mn F^(a,mn)", "K_R": "8 pi^2 kappa1 a^5", "matrix": "K_ab=K_R delta_ab", "canonical_field": "A_can^a=sqrt(K_R) A^a", "g5_geom": "1/sqrt(K_R)", "dimensions": {"kappa1": "L^-6", "K_R": "L^-1", "A_geometric": "L^-1", "A_can": "L^-3/2", "g5_geom": "L^1/2"}, "isotropy": "round metric restores one Sp(1) normalization", "algebra": "Sp(1) isomorphic to SU(2) algebraically; no physical group map"},
        "u1": {**c("BHSM_complex_Hopf_U1_normalization_v6_1"), "status": "BHSM_COMPLEX_HOPF_U1_NORMALIZATION_DERIVED_CONDITIONALLY", "bundle": "S1->S7->CP3 with 4pi subgroup orbit in the repository coordinate convention", "M7_coefficient": "2 pi kappa1 a^3", "M5_inherited_pushforward": "multiplication by Vol(S2)=4 pi a^2 gives 8 pi^2 kappa1 a^5", "standard_2pi_unit_charge": "B=A_inherited/2 gives K_U1=4K_R and q=2m integral", "role": "nested/right-weight connection constrained by the geometry, not an additional independent M5 field alongside the same inherited direction", "double_counted": False, "hypercharge_identification": None},
        "ratio": {**c("BHSM_round_connection_normalization_ratio_v6_1"), "status": "BHSM_GEOMETRIC_CONNECTION_RATIO_CONVENTION_CLASSIFIED", "inherited_4pi": {"K_U1_over_K_Sp1": 1, "g_U1_over_g_Sp1": 1}, "standard_2pi_unit_charge": {"K_U1_over_K_Sp1": 4, "g_U1_over_g_Sp1": "1/2"}, "scale_dependence": "none", "representation_dependence": "canonical eigenvalues still multiply m or q", "convention_dependence": "yes: the generator period and trace must be declared", "physical_mixing_candidate_frozen": False},
        "charges": {**c("BHSM_round_canonical_multiplet_charge_operators_v6_1"), "status": "BHSM_ASSOCIATED_MULTIPLET_CHARGE_OPERATORS_DERIVED", "space": "H_(J,m), rank 2J+1 for every fixed right weight m", "covariant_derivative": "D_mu=partial_mu+g5_geom rho_J(T_a) A_can^a_mu+i(q g5_geom/2) B_can_mu in the standard 2pi convention", "Sp1": "[T_a,T_b]=epsilon_abc T_c; tr_fund(T_aT_b)=-delta_ab/2; C2=J(J+1)", "U1": "q=2m integral; weights -2J,-2J+2,...,2J", "reality": "real parent fields pair (J,m) with (J,-m) by Wigner conjugation", "physical_charge_map": None},
        "gauge": {**c("BHSM_round_gauge_self_interaction_ledger_v6_1"), "status": "BHSM_ROUND_GEOMETRIC_GAUGE_SELF_INTERACTIONS_DERIVED", "field_strength": "F^a=dA^a+(1/2)epsilon^a_bc A^b wedge A^c", "canonical_vertices": {"quadratic": 1, "cubic": "g5_geom", "quartic": "g5_geom^2"}, "time_dependence": "D_t ln K_R=5H; A_can redefinition supplies pump term -(5/2)H A_can", "identity": "the same g5_geom appears in the canonical gauge transformation, cubic vertex, and square root of the quartic vertex", "Bianchi": "D_[mu F_nu rho]=0", "kinetic_positive": "kappa1,a>0", "longitudinal_modes": "gauge constraints/zero modes removed before physical counting", "RG_running": False},
        "candidates": {**c("BHSM_round_scalar_candidate_comparison_v6_1"), "status": "BHSM_ROUND_SCALAR_CANDIDATES_CLASSIFIED", "rows": [{"candidate": "declared (J,m)=(0,0) sigma", "domain": "bulk M8 -> neutral M5 scalar", "kinetic": "Zsigma Vol(S3)", "parity": "Z2 odd field/even action", "potential": "existing primitive A0,G0 and chi coupling", "result": "selected parent field; v5 potential/boundary role open"}, {"candidate": "common rho=ln a", "domain": "metric volume", "result": "Hamiltonian-constrained homogeneous background direction"}, {"candidate": "two shape modes", "domain": "metric", "result": "positive 4/a^2 round modes, not selected as v5 sigma"}, {"candidate": "fiber volume", "domain": "combination of rho and shapes", "result": "not independent"}, {"candidate": "boundary/collar response", "domain": "unselected physical M4 boundary", "result": "not yet defined"}, {"candidate": "linear combination", "result": "no action-selected mixing at sigma=0"}]},
        "sigma": {**c("BHSM_sigma_parent_identification_theorem_v6_1"), "status": "BHSM_SIGMA_PARENT_FIELD_SELECTED_POTENTIAL_OPEN", "selected": "the already declared real Z2 bulk (J,m)=(0,0) scalar", "selection_basis": ["correct bulk scalar domain", "neutral associated singlet", "independent of constrained metric volume", "explicit Z2-even action", "existing parent kinetic and polynomial source"], "not_selection_basis": ["sigma=1/2", "A_ST=-2", "G_ST=8"], "identification_scope": "parent field representative selected", "still_open": ["v5 topographic/boundary response map", "geometric origin of A0,G0,g", "coefficient signs", "vacuum value", "physical M4 normalization"], "higgs_identification": False},
        "scalar_kinetic": {**c("BHSM_round_scalar_kinetic_normalization_v6_1"), "status": "BHSM_ROUND_SCALAR_KINETIC_NORMALIZATION_DERIVED", "raw_M5": "Z5(a)=Zsigma Vol(S3)=16 pi^2 Zsigma a^3", "canonical": "s5=sqrt(Z5) sigma on an instantaneous slice", "dimensions": {"sigma_parent": "dimensionless", "Zsigma": "L^-6", "Z5": "L^-3", "s5": "L^-3/2"}, "friction": "raw sigma has 7H friction; s5 has 4H friction and pump mass -(3/2)Hdot-(33/4)H^2", "t0_pump": "-lambda/28", "neutral": True},
        "potential": {**c("BHSM_parent_scalar_potential_source_map_v6_1"), "status": "BHSM_SCALAR_POTENTIAL_PARENT_SOURCE_DERIVED_CONDITIONALLY", "sources": {"declared_parent": "A0 sigma^2/2+G0 sigma^4/4", "chi": "Zchi g sigma^2 (nabla chi)^2/2; zero on the selected vacuum chi branch", "P1_curvature": "modulus potential only; no direct sigma term", "connection": "no sigma dependence in K_R in the frozen P1 action", "singlet_spectrum": "lambda_(0,0)=0", "boundary": "no selected spatial/collar boundary term", "tower": "no pure-singlet heavy source from a local singlet polynomial"}, "canonical_t0": {"quadratic": "A0/Zsigma-lambda/28 including the time-normalization pump", "cubic": 0, "quartic_5D": "G0/[Zsigma^2 Vol(S3,t0)]"}, "stationary": "sigma=0 always; sigma=+/-sqrt(-A_eff/G0) only if A_eff<0,G0>0", "signs_selected": False, "v5_coefficients_reproduced": False},
        "tower": {**c("BHSM_round_tower_induced_scalar_operators_v6_1"), "status": "BHSM_ROUND_TOWER_SCALAR_CORRECTIONS_CONDITIONAL_NO_STRICT_WINDOW", "pure_sigma": "products of the fiber singlet remain singlets, so the declared local sigma polynomial has J_H=0 and no tree-level heavy-tower correction", "general_retained_modes": "Delta S=-1/2<J_H,O_H^-1 J_H> generates overlap-weighted quadratic/quartic/derivative/nonlocal terms", "denominator": "instantaneous eigenvalues at least Delta(t) only inside the v6.0.10 low-energy hypothesis", "sign": "not universally fixed in Lorentzian signature or across interaction channels", "error": "controlled by epsilon_control, whose full round-background floor is 1/3", "extension_outside_interval": False},
        "hessian": {**c("BHSM_round_constraint_reduced_scalar_modulus_hessian_v6_1"), "status": "BHSM_ROUND_SCALAR_MODULUS_HESSIAN_DERIVED_CONDITIONALLY", "removed": ["lapse", "time-reparameterization gauge", "Hamiltonian-constrained homogeneous volume direction", "connection gauge zero modes"], "physical_block_at_sigma_zero_t0": ["m_sigma,op^2=A0/Zsigma-lambda/28", "m_shape1^2=4/a_min^2=8lambda/21", "m_shape2^2=4/a_min^2=8lambda/21"], "mixing": "Z2 symmetry makes sigma-shape and sigma-volume Hessian cross terms vanish at sigma=0; coefficient dependence produces higher interactions", "stability": "shape block positive; sigma sign remains conditional on A0/Zsigma", "phase_transition_claim": False},
        "gauge_scalar": {**c("BHSM_round_gauge_scalar_interaction_map_v6_1"), "status": "BHSM_GAUGE_SCALAR_COUPLING_DERIVED_CONDITIONALLY", "modulus": "K_R proportional to a^5 gives K_R=K_R0[1+5 delta rho+(25/2)delta rho^2+...] and hence modulus F^2 vertices", "sigma_F2": "absent in the frozen P1 action", "multiplets": "nontrivial associated scalars couple through |D_A Phi|^2", "selected_sigma": "neutral singlet; no connection mass or Sp1->U1 reduction", "shape": "off-round shape perturbations split K_ab but do not establish physical symmetry breaking", "electroweak_claim": False},
        "aperture": {**c("BHSM_geometric_aperture_readiness_v6_1"), "status": "BHSM_GEOMETRIC_APERTURE_NORMALIZATIONS_READY_DOMAIN_OPEN", "available": ["physical S3/S7 measure", "canonical M5 connection", "normalized associated modes", "representation trace", "amplitude-versus-square rule"], "definitions": {"N_A": "integral_C dmu w_A |u_A|^2", "I_R": "integral_C dmu chi_R^dagger Pi_A u_A chi_R", "candidate": "e_eff^2=g_geom^2 |I_R|^2/N_A"}, "missing": ["physical collar/boundary domain C", "projection Pi_A", "M5-to-M4 measure", "dimension-closing localization length"], "inputs_complete": False, "alpha": None},
        "coupling_dimension": {**c("BHSM_M5_M4_coupling_dimension_ledger_v6_1"), "status": "BHSM_PHYSICAL_3P1_REDUCTION_REMAINS_REQUIRED", "M5": "[g5_geom]=L^1/2 and [g5_geom^2]=L", "M4": "a dimensionless g4 would require a declared normalized M5-to-M4 zero-mode/restriction map", "conditional_formula": "g4^2=g5^2/L_eff only for a defined interval/normal profile with physical length L_eff", "L_eff": None, "allowed_routes": ["physical boundary restriction", "collar zero mode", "radial localization", "hypersurface action", "repository-defined further quotient"], "observed_coupling": None},
        "parent_v5": {**c("BHSM_parent_to_v5_bosonic_coefficient_map_v6_1"), "status": "BHSM_PARENT_TO_V5_BOSONIC_MAP_ADVANCED_CONDITIONALLY", "map": {"Berger_geometry": "exact instantaneous round parent geometry", "physical_measure": "exact M8/M5", "gauge_kinetic": "exact geometric M5 K_R; M4 physical map required", "scalar_kinetic": "exact Zsigma Vol(S3); v5 normalization open", "A_ST": "structural A0/Zsigma plus background pump, value not derived", "G_ST": "structural G0/[Zsigma^2 Vol(S3)], value not derived", "sigma_scale": "conditional stationary formula; no selected signs or vacuum", "charged_current": "requires fermions and aperture", "neutral_response": "requires physical current/response map", "boundary_collar": "unresolved M4 domain", "scale_RG": "time normalization is not RG running"}, "frozen_values_changed": False},
        "spectrum": {**c("BHSM_round_background_mode_spectrum_v6_1"), "status": "BHSM_ROUND_BACKGROUND_SPECTRAL_INPUT_DERIVED", "formula": "lambda_J=J(J+1)/a_min^2=2lambda J(J+1)/21", "gap": "J=1/2 gives Delta=lambda/14", "rows_lambda_equals_one": spectrum_rows, "canonical_strength": "g5_geom(t0)=[8 pi^2 kappa1 a_min^5]^-1/2", "modulus_derivative": "D_t lambda_J=-2H lambda_J", "particle_map": None},
        "dirac": {**c("BHSM_round_background_Dirac_forward_link_v6_1"), "status": "BHSM_ROUND_BACKGROUND_SPINORIAL_BOUNDARY_OPERATOR_INPUTS_CONDITIONAL", "historical_filename_retained": True, "available": ["round orthonormal 4+2+1 frame", "Levi-Civita/spin-connection geometry", "physical S3/S7 measures", "Sp1 associated representations", "complex-Hopf integral weights", "canonical M5 connection", "neutral sigma parent field", "t0 normalization surface", "effective dimension M5"], "mathematical_scope": "Clifford bundles, spin structures, spin connections, and first-order geometric operator candidates only after their domains are specified", "missing": ["BHSM-native fermionic action source", "parent spinor representation", "chirality mechanism", "physical M4 boundary/domain reduction", "fermion action normalization", "Yukawa/geometric mass operator", "particle map", "strict adiabatic window"], "physical_fermion_equation": None, "next_fermionic_action_sprint_ready": False, "next_Dirac_sprint_ready": False, "monopole_dependency": None},
        "scale": {**c("BHSM_round_background_scale_primitive_audit_v6_1"), "status": "BHSM_ROUND_LOCAL_COEFFICIENTS_DERIVED_PRIMITIVES_OPEN", "relations": {"lambda": "kappa0/kappa1", "a_min_squared": "21kappa1/(2kappa0)", "Delta_t0": "kappa0/(14kappa1)", "K_R_t0": "8 pi^2 kappa1[21kappa1/(2kappa0)]^(5/2)", "g5_t0": "K_R_t0^-1/2", "Z5_t0": "16 pi^2 Zsigma[21kappa1/(2kappa0)]^(3/2)"}, "raw_primitives": 7, "field_normalized_invariants": 5, "primitive_reduction": "no primitive value is selected by normalization", "absolute_unit": None},
        "hidden": {**c("BHSM_round_background_hidden_input_claim_audit_v6_1"), "status": "BHSM_ROUND_GAUGE_SCALAR_HIDDEN_INPUTS_EXPOSED", "primitive_inputs": ["kappa0", "kappa1", "Zchi", "Zsigma", "A0", "G0", "g"], "declared_conventions": ["Sp1 trace", "4pi inherited circle", "2pi unit-charge conversion", "instantaneous t0 canonicalization"], "unresolved_inputs": ["epsilon_star with epsilon_star>=1/3 if used diagnostically", "physical M4 domain", "L_eff", "aperture domain/projector", "spinor/chirality data"], "not_imported": ["alpha", "1/137", "1/(12pi^2)", "measured gauge couplings", "masses", "CKM", "PMNS", "cosmological calibration"], "strict_control_window_claimed": False},
        "report": {**c("BHSM_round_background_gauge_scalar_report_v6_1"), "status": PRIMARY_RESULT, "central_answer": "On the exact round P1 trajectory, the S3 pushforward gives an isotropic canonical M5 Sp(1) connection with K_R=8 pi^2 kappa1 a^5, algebra-consistent cubic/quartic vertices, and normalized associated-multiplet generators. The complex-Hopf U(1) normalization is derived only as a nested, convention-declared component and is not an independent additional M5 gauge factor. The declared neutral bulk singlet is selected as the parent sigma field, but its potential coefficients, v5 boundary/topographic map, and vacuum remain open. The t0 slice is an exact normalization surface, yet the full adiabatic control parameter has the irreducible value |Hdot|/Delta=1/3, so no parametrically small tower-control window is proved. A physical dimensionless coupling and chirality still require an explicit M5-to-M4 reduction.", "derived": ["M8/M5 dimensional firewall", "round Sp1 K_R and canonical fields", "gauge self-interaction identities", "multiplet geometric charge operators", "scalar M5 normalization", "parent potential source map", "constraint-reduced t0 scalar/shape block", "round spectrum", "permanent fermionic/Clifford and no-monopole firewall"], "conditional": ["nested U1 normalization", "sigma parent role", "tower-induced operators", "gauge-scalar modulus vertices", "spinorial boundary-operator input package"], "constructive_constraints": ["no strict epsilon<<1 control window", "U1 cannot be double counted", "sigma potential is primitive rather than geometrically derived", "aperture domain is missing", "M5 coupling is dimensionful", "physical M4 reduction is required", "a physical fermion equation requires a BHSM-native action source", "bundle curvature and Chern data have no magnetic interpretation by default"], "completion_gate": "V6_1_M5_BOSONIC_NORMALIZATION_DERIVED_M4_REDUCTION_REQUIRED", "recommended_next_branch": "bhsm-parent-m5-to-physical-boundary-m4-reduction-v6-1-1", "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE"},
    }
    return payloads


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    built = build_artifact_payloads(root)
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(built[key]), encoding="utf-8")
        paths.append(path)
    return paths


def round_bosonic_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def round_bosonic_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.1 Round-Background Gauge and Scalar Sector",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Next gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"
