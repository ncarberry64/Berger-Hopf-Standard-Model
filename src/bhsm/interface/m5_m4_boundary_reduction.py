"""BHSM v6.1.1 parent-M5 to equatorial-M4 boundary reduction."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


VERSION = "v6.1.1"
SPRINT = "bhsm-parent-m5-to-physical-boundary-m4-reduction-v6-1-1"
PRIMARY_RESULT = "BHSM_ROUND_EQUATORIAL_M4_ZERO_MODE_ARCHITECTURE_DERIVED"
COMPLETION_GATE = "V6_1_1_EQUATORIAL_GEOMETRY_AND_ZERO_MODE_ARCHITECTURE_DERIVED_LOCALIZATION_ACTION_REQUIRED"

ARTIFACT_FILES = {
    "firewall": "BHSM_fermionic_clifford_no_monopole_firewall_v6_1_1.json",
    "m5_geometry": "BHSM_M5_hyperspherical_convention_ledger_v6_1_1.json",
    "roles": "BHSM_M4_candidate_role_matrix_v6_1_1.json",
    "equator": "BHSM_round_equatorial_M4_geometry_v6_1_1.json",
    "selection": "BHSM_equator_selection_status_v6_1_1.json",
    "boundary_firewall": "BHSM_boundary_control_surface_firewall_v6_1_1.json",
    "gauss_codazzi": "BHSM_M4_Gauss_Codazzi_reduction_v6_1_1.json",
    "ghy": "BHSM_M4_GHY_boundary_variation_v6_1_1.json",
    "sturm": "BHSM_M4_normal_Sturm_Liouville_operator_v6_1_1.json",
    "zero_modes": "BHSM_M4_exact_zero_mode_audit_v6_1_1.json",
    "gravity": "BHSM_M4_gravitational_normalization_v6_1_1.json",
    "sp1": "BHSM_M4_Sp1_connection_normalization_v6_1_1.json",
    "u1": "BHSM_M4_nested_U1_classification_v6_1_1.json",
    "no_monopole": "BHSM_M4_no_monopole_connection_ledger_v6_1_1.json",
    "scalar": "BHSM_M4_scalar_normalization_v6_1_1.json",
    "sigma": "BHSM_sigma_M4_role_theorem_v6_1_1.json",
    "localization": "BHSM_M4_localization_action_source_audit_v6_1_1.json",
    "boundary_conditions": "BHSM_M4_boundary_condition_self_adjointness_v6_1_1.json",
    "currents": "BHSM_M4_charge_current_normalization_v6_1_1.json",
    "aperture": "BHSM_M4_geometric_aperture_readiness_v6_1_1.json",
    "potential": "BHSM_M4_scalar_potential_map_v6_1_1.json",
    "parent_v5": "BHSM_parent_to_v5_v4_coefficient_map_v6_1_1.json",
    "fermionic": "BHSM_fermionic_Clifford_boundary_readiness_v6_1_1.json",
    "scale": "BHSM_M4_scale_primitive_audit_v6_1_1.json",
    "hidden": "BHSM_M4_hidden_input_claim_audit_v6_1_1.json",
    "report": "BHSM_parent_M5_to_M4_boundary_report_v6_1_1.json",
}

GUARDS = {
    "v6_1_bosonic_results_preserved": True,
    "physical_fermion_equation_assumed": False,
    "magnetic_monopole_sector_used": False,
    "monopole_harmonics_used": False,
    "chern_data_called_magnetic_charge": False,
    "magnetic_charge_quantization_imported": False,
    "equator_called_uniquely_selected": False,
    "control_surface_called_physical_boundary": False,
    "m4_identified_as_observed_spacetime": False,
    "measured_input_used": False,
    "compactification_length_invented": False,
    "alpha_evaluated": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all radii and positive kinetic coefficients must be positive")


def hyperspherical_geometry(a: float, chi: float) -> dict[str, float]:
    _positive(a)
    if not 0 <= chi <= math.pi:
        raise ValueError("chi must lie in [0,pi]")
    sine = math.sin(chi)
    cosine = math.cos(chi)
    return {
        "warp": sine,
        "level_radius": a * sine,
        "spatial_measure_coefficient": a**4 * sine**3,
        "normal_contravariant_chi": 1 / a,
        "K_spatial_principal": cosine / (a * sine) if sine else math.inf,
        "K_trace": 3 * cosine / (a * sine) if sine else math.inf,
    }


def equatorial_geometry(a: float, hubble: float, acceleration_over_a: float) -> dict[str, float]:
    _positive(a)
    return {
        "spatial_radius": a,
        "spatial_volume": 2 * math.pi**2 * a**3,
        "K_trace": 0.0,
        "K_mn_K_mn": 0.0,
        "R4": 6 * (acceleration_over_a + hubble**2 + 1 / a**2),
        "G00": 3 * (hubble**2 + 1 / a**2),
        "Gspatial_coefficient": -(2 * acceleration_over_a + hubble**2 + 1 / a**2),
    }


def gauss_codazzi_background(a: float, chi: float, hubble: float, acceleration_over_a: float) -> dict[str, float]:
    _positive(a)
    if not 0 < chi < math.pi:
        raise ValueError("the polar coordinate formula requires 0<chi<pi")
    sine = math.sin(chi)
    cotangent = math.cos(chi) / sine
    r4 = 6 * (acceleration_over_a + hubble**2 + 1 / (a**2 * sine**2))
    k_squared = 9 * cotangent**2 / a**2
    kmn_squared = 3 * cotangent**2 / a**2
    divergence = 3 * (2 * cotangent**2 - 1) / a**2 - (acceleration_over_a + 3 * hubble**2)
    rhs = r4 + k_squared - kmn_squared - 2 * divergence
    r5 = 8 * acceleration_over_a + 12 * (hubble**2 + 1 / a**2)
    return {"R4": r4, "K_squared": k_squared, "Kmn_squared": kmn_squared, "normal_divergence": divergence, "R5_from_decomposition": rhs, "R5_direct": r5, "residual": rhs - r5}


def normal_integrals(domain: str = "full") -> dict[str, float]:
    if domain == "full":
        return {"chi_min": 0.0, "chi_max": math.pi, "sin3": 4 / 3, "sin1": 2.0}
    if domain == "hemisphere":
        return {"chi_min": 0.0, "chi_max": math.pi / 2, "sin3": 2 / 3, "sin1": 1.0}
    raise ValueError("domain must be 'full' or 'hemisphere'")


def scalar_profile_factors(a: float, domain: str = "full") -> dict[str, float]:
    _positive(a)
    integrals = normal_integrals(domain)
    temporal = a * integrals["sin3"]
    spatial = a * integrals["sin1"]
    return {
        "L_time": temporal,
        "L_spatial": spatial,
        "spatial_to_time": spatial / temporal,
        "constant_weight_normalization": 1 / math.sqrt(integrals["sin3"]),
    }


def normal_eigenvalue(level: int, a: float) -> float:
    if not isinstance(level, int) or isinstance(level, bool) or level < 0:
        raise ValueError("level must be a nonnegative integer")
    _positive(a)
    return level * (level + 3) / a**2


def scalar_m4_coefficients(Zsigma: float, A0: float, G0: float, a: float, domain: str = "full") -> dict[str, float]:
    _positive(Zsigma, a)
    factor = scalar_profile_factors(a, domain)["L_time"]
    fiber_volume = 16 * math.pi**2 * a**3
    z4_time = Zsigma * fiber_volume * factor
    return {
        "Z4_time": z4_time,
        "Z4_spatial": Zsigma * fiber_volume * scalar_profile_factors(a, domain)["L_spatial"],
        "canonical_factor_time": math.sqrt(z4_time),
        "potential_mass_squared": A0 / Zsigma,
        "canonical_quartic_time": G0 / (Zsigma**2 * fiber_volume * factor),
    }


def m5_gravity_coefficient(kappa1: float, a: float) -> float:
    _positive(kappa1, a)
    return 8 * math.pi**2 * kappa1 * a**3


def formal_m4_gravity_coefficient(kappa1: float, a: float, domain: str = "full") -> float:
    return m5_gravity_coefficient(kappa1, a) * scalar_profile_factors(a, domain)["L_time"]


def green_boundary_form(u: float, du: float, v: float, dv: float, chi: float) -> float:
    return math.sin(chi) ** 3 * (u * dv - du * v)


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "This is an exact equatorial geometry and conditional boundary/localization reduction. It does not identify observed spacetime, physical gauge groups or charges, a physical fermion equation, magnetic monopoles, measured couplings, an absolute unit, or full BHSM.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    return {
        "firewall": {**c("BHSM_fermionic_clifford_no_monopole_firewall_v6_1_1"), "status": "BHSM_NO_MONOPOLE_FIREWALL_DERIVED", "doctrine": "Clifford/spin geometry is mathematical until a BHSM-native fermionic action and domain derive a physical equation", "bundle_data": ["Hopf winding", "principal U1 bundle", "first Chern class", "connection curvature", "transition functions"], "physical_magnetic_interpretation": None, "excluded": ["Dirac string", "monopole harmonic basis", "magnetic-charge sector", "magnetic-charge quantization", "monopole-induced chirality", "monopole-generated generations"]},
        "m5_geometry": {**c("BHSM_M5_hyperspherical_convention_ledger_v6_1_1"), "status": "BHSM_M5_HYPERSPHERICAL_GEOMETRY_DERIVED", "metric": "ds5^2=-dt^2+a(t)^2[dchi^2+sin^2(chi) ds^2_S3]", "range": "0<=chi<=pi", "poles": [0, "pi"], "equator": "chi=pi/2", "level_radius": "a sin chi", "measure": "sqrt(-g5)=a^4 sin^3(chi) sqrt(gamma3)", "normal": "n=a^-1 partial_chi", "volumes": {"S4": "8 pi^2 a^4/3", "hemisphere": "4 pi^2 a^4/3", "equatorial_S3": "2 pi^2 a^3"}, "not_product": True},
        "roles": {**c("BHSM_M4_candidate_role_matrix_v6_1_1"), "status": "BHSM_M4_RELATED_ROLES_CLASSIFIED", "rows": [{"role": "equatorial control hypersurface", "global": True, "actual_boundary": False, "localization_action": False}, {"role": "selected hemisphere boundary", "global": "after an orientation/hemisphere datum", "actual_boundary": True, "localization_action": "independent boundary dynamics still absent"}, {"role": "Z2 fixed surface", "global": "requires reflection quotient/interface interpretation", "actual_boundary": "conditional", "localization_action": "required for independent fields"}, {"role": "smooth collar", "global": True, "actual_boundary": False, "localization_action": True}, {"role": "bulk normal zero mode", "global": True, "actual_boundary": False, "localization_action": "not for the scalar singlet; required for a Lorentzian M4 field sector"}], "selected_role": "equatorial geometry plus a symmetry-equivalent hemisphere/Z2 representative, conditionally physical only with an action-supported boundary/localization term"},
        "equator": {**c("BHSM_round_equatorial_M4_geometry_v6_1_1"), "status": "BHSM_ROUND_EQUATORIAL_M4_GEOMETRY_DERIVED", "metric": "ds4^2=-dt^2+a(t)^2 ds^2_S3", "normal": "n=+/-a^-1 partial_chi", "K_components": "K_tt=0; K_ij=(cot chi/a)h_ij, hence K_mn=0 at chi=pi/2", "K": 0, "intrinsic_R4": "6[addot/a+H^2+1/a^2]", "volume": "2 pi^2 a^3", "properties": ["totally geodesic", "minimal", "fixed by chi->pi-chi", "dynamically preserved for every a(t)"]},
        "selection": {**c("BHSM_equator_selection_status_v6_1_1"), "status": "BHSM_EQUATOR_GEOMETRIC_EXISTENCE_DERIVED_PHYSICAL_SELECTION_OPEN", "family": "all great S3 equators form one SO(5)-equivalent orbit", "preferred_axis": None, "representative_choice": "coordinate choice only after the boundary orbit is selected", "orientation": "choosing a hemisphere/outward normal is additional boundary data", "monopole_selection": False},
        "boundary_firewall": {**c("BHSM_boundary_control_surface_firewall_v6_1_1"), "status": "BHSM_EQUATOR_CONTROL_SURFACE_DERIVED_PHYSICAL_BOUNDARY_CONDITIONAL", "restriction": "a bulk solution may be evaluated at the equator", "hemisphere": "cutting S4 produces a mathematical boundary and requires GHY", "independent_fields": "not supplied by restriction or GHY", "physical_boundary": "requires a selected hemisphere/Z2 interpretation plus an action-supported boundary or localization sector"},
        "gauss_codazzi": {**c("BHSM_M4_Gauss_Codazzi_reduction_v6_1_1"), "status": "BHSM_M4_GAUSS_CODAZZI_REDUCTION_DERIVED", "identity": "R5=R4+K^2-K_mn K^mn-2 nabla_A(K n^A-a_n^A) for K_mn=(1/2)L_n h_mn and spacelike normal", "normal_acceleration": "a_n^A=n^B nabla_B n^A; here a_n^t=H", "bulk_coefficient": "C5=kappa1 Vol(S3_fiber)/2=8 pi^2 kappa1 a^3", "equator": "K_mn=K=0 but the normal-divergence/normal-curvature contribution does not vanish", "background_check": {"R5": "8 addot/a+12(H^2+1/a^2)", "R4_equator": "6(addot/a+H^2+1/a^2)"}, "independent_EH_term": "not generated by mere restriction"},
        "ghy": {**c("BHSM_M4_GHY_boundary_variation_v6_1_1"), "status": "BHSM_M4_GHY_VARIATION_DERIVED_BOUNDARY_DYNAMICS_OPEN", "action": "S_GHY=2 C5 integral_M4 sqrt(-h) K for each actual boundary with its outward normal", "hemispheres": "opposite outward normals; cutting and summing requires both sides/interface matching", "canonical_momentum": "pi_mn=C5 sqrt(-h)(K_mn-Kh_mn)", "Brown_York": "T_mn=2 C5(K_mn-Kh_mn) in the declared sign convention", "equator_background": "K_mn=0 makes the value, momentum, and background Brown-York stress zero", "variation": "retained to cancel normal metric-derivative variations", "intrinsic_boundary_action": None},
        "sturm": {**c("BHSM_M4_normal_Sturm_Liouville_operator_v6_1_1"), "status": "BHSM_M4_NORMAL_STURM_LIOUVILLE_PROBLEM_DERIVED", "operator": "L_chi u=-sin^-3(chi) d_chi[sin^3(chi) d_chi u]", "weight": "sin^3 chi", "physical_normal_mass": "mu/a^2", "full_domain": "[0,pi], regular at both poles", "hemisphere": "[0,pi/2], regular at chi=0 and Dirichlet/Neumann/Robin at the equator", "spectrum": "mu_l=l(l+3), l=0,1,... for full regular zonal profiles", "even": "Neumann at equator; includes u0=constant", "odd": "Dirichlet at equator; lowest zonal profile cos chi has mu=4", "green_form": "[sin^3 chi(u* v'-u'* v)] at endpoints"},
        "zero_modes": {**c("BHSM_M4_exact_zero_mode_audit_v6_1_1"), "status": "BHSM_ROUND_EQUATORIAL_M4_ZERO_MODE_ARCHITECTURE_DERIVED", "scalar_singlet": "exact even constant normal profile, mu0=0", "associated_nonconstant_S3_modes": "no zero eigenvalue on connected compact S4", "connection": "no smooth global tangential vector zero mode; H1(S4)=0 and constant S3 components fail pole regularity", "metric": "no product-factor M4 graviton zero mode because S3 collapses at the S4 poles", "hemisphere": "constant scalar Neumann zero mode survives; Dirichlet/odd sector has no zero mode", "boundary_localized": "requires an additional action source"},
        "gravity": {**c("BHSM_M4_gravitational_normalization_v6_1_1"), "status": "BHSM_M4_GRAVITATIONAL_NORMALIZATION_DERIVED_CONDITIONALLY", "C5": "8 pi^2 kappa1 a^3", "formal_constant_profile_C4_time": {"full_S4": "(32 pi^2/3)kappa1 a^4", "hemisphere": "(16 pi^2/3)kappa1 a^4"}, "profile_integral": "L_t=a integral sin^3 chi |u|^2 dchi", "obstruction": "the warped S4 is not M4 times an interval; spatial-curvature and kinetic weights do not share one smooth zero-mode coefficient", "time_dependence": "proportional to a^4 for u=1", "Weyl_frame": "would be a further field redefinition, not stabilization", "observed_Planck_identification": None},
        "sp1": {**c("BHSM_M4_Sp1_connection_normalization_v6_1_1"), "status": "BHSM_M4_SP1_CONNECTION_NORMALIZATION_REQUIRES_LOCALIZATION", "M5": "K5=8 pi^2 kappa1 a^5", "smooth_bulk_problem": "tangential S3 vector components have distinct electric/magnetic warp weights and no regular massless full-S4 vector profile", "electric_weight": "a integral sin chi |u_A|^2 dchi", "magnetic_weight": "a integral csc(chi) |u_A|^2 dchi, subject to pole regularity", "boundary_profile": "if an action derives common L_eff,A at the equator, K4=K5 L_eff,A and g4_geom^2=g5_geom^2/L_eff,A", "canonical_vertices": "cubic g4_geom and quartic g4_geom^2 only after the common K4 exists", "physical_group": None},
        "u1": {**c("BHSM_M4_nested_U1_classification_v6_1_1"), "status": "BHSM_M4_U1_COMPONENT_CLASSIFIED", "surviving_data": ["tangential restriction where regular", "associated integral weights q=2m", "boundary holonomy where a loop and domain are specified"], "normal_component": "an adjoint scalar candidate subject to gauge constraints and parity", "independent_field": False, "zero_mode": "no additional independent smooth M4 vector zero mode", "normalization": "inherits the declared Sp1 subgroup convention only after the same boundary profile is sourced", "hypercharge": None},
        "no_monopole": {**c("BHSM_M4_no_monopole_connection_ledger_v6_1_1"), "status": "BHSM_NO_MONOPOLE_FIREWALL_DERIVED", "allowed": ["connection restriction", "holonomy", "associated weight", "tangential curvature", "Wilson loop", "characteristic class with its exact cycle"], "flux_rule": "state cycle, bundle, curvature, and characteristic normalization; default physical magnetic interpretation is none", "magnetic_charge_operator": None},
        "scalar": {**c("BHSM_M4_scalar_normalization_v6_1_1"), "status": "BHSM_M4_SIGMA_NORMALIZATION_DERIVED", "profile": "u0=constant, even, mu0=0", "full_S4": {"Z4_time": "(64 pi^2/3)Zsigma a^4", "Z4_spatial": "32 pi^2 Zsigma a^4", "ratio": "Z4_spatial/Z4_time=3/2"}, "hemisphere": {"Z4_time": "(32 pi^2/3)Zsigma a^4", "Z4_spatial": "16 pi^2 Zsigma a^4", "ratio": "3/2"}, "canonical_homogeneous_field": "s4=sqrt(Z4_time) sigma", "canonical_pump_t0": "-lambda/21", "normal_mass": 0, "Lorentzian_M4_status": "homogeneous normalization exact; inhomogeneous standard M4 scalar requires boundary localization because the smooth bulk weights differ"},
        "sigma": {**c("BHSM_sigma_M4_role_theorem_v6_1_1"), "status": "BHSM_SIGMA_BULK_ZERO_MODE_SELECTED", "selected_role": "even bulk singlet normal zero mode restricted to the equator", "not_derived": ["independent boundary scalar", "collar localization field", "boundary displacement mode", "interface order parameter"], "boundary_value": "nonzero for the even constant profile", "extrinsic_coupling": "none in the frozen parent action", "v5_role": "boundary/topographic interpretation remains conditional", "desired_vacuum_used": False},
        "localization": {**c("BHSM_M4_localization_action_source_audit_v6_1_1"), "status": "BHSM_M4_LOCALIZATION_SOURCE_REQUIRED", "present": {"GHY": "variational completion only", "Z2_parity": "available as a geometric condition, not a kinetic action", "bulk_sigma": "constant normal zero mode"}, "missing_terms": [{"term": "C_boundary integral sqrt(-h) R4", "dimension": "[C_boundary]=L^-2", "effect": "independent M4 gravitational kinetic term"}, {"term": "-(tau_A/4) integral sqrt(-h) F^2", "dimension": "[tau_A]=L^0", "effect": "common finite M4 connection normalization"}, {"term": "-(Z_boundary/2) integral sqrt(-h)(D sigma)^2", "dimension": "[Z_boundary]=L^-2 for dimensionless sigma", "effect": "Lorentzian boundary scalar kinetic term"}, {"term": "collar V_loc(chi) Phi^2 or Robin r Phi^2", "dimension": "[V_loc]=L^-2; [r]=L^-1", "effect": "normal localization/profile selection"}], "delta_brane_added": False, "coefficient_values": None},
        "boundary_conditions": {**c("BHSM_M4_boundary_condition_self_adjointness_v6_1_1"), "status": "BHSM_M4_BOUNDARY_SELF_ADJOINTNESS_LEDGER_DERIVED", "scalar": {"even": "u'=0", "odd": "u=0", "Robin": "u'+a r u=0 with real r"}, "metric": "Dirichlet induced metric with GHY, or a separately derived mixed boundary action", "Sp1": "absolute/relative gauge-compatible conditions paired with allowed gauge transformations", "U1": "same constrained subgroup boundary condition; no magnetic sector", "interface": "continuity plus action-derived jump of weighted normal derivative", "green_form": "vanishes for matched real Dirichlet, Neumann, or Robin domains", "spinorial_future": "self-adjoint Clifford boundary projectors remain action/domain candidates"},
        "currents": {**c("BHSM_M4_charge_current_normalization_v6_1_1"), "status": "BHSM_M4_CURRENT_OPERATORS_PROFILE_CONDITIONAL", "Sp1": "J_mu^a=i Phi^dagger T^a <->D_mu Phi times the derived profile overlap", "U1": "J_mu^(q)=q Phi^dagger <->D_mu Phi with q=2m when the nested component is independently retained", "conservation": "covariant after a common self-adjoint gauge/matter boundary domain closes", "conjugation": "q pairs with -q", "canonical_coefficient": "requires g4_geom from an action-supported common profile", "geometric_charge": "representation generator/weight only", "magnetic_charge": None, "observed_charge": None},
        "aperture": {**c("BHSM_M4_geometric_aperture_readiness_v6_1_1"), "status": "BHSM_M4_GEOMETRIC_APERTURE_PROFILE_ARCHITECTURE_DERIVED_INPUTS_OPEN", "definitions": {"N_A": "integral_normal dmu w_A |u_A|^2", "N_chi": "integral_normal dmu w_chi |u_chi|^2", "I_R": "integral_normal dmu u_chi^* Pi_A u_A u_chi", "candidate": "e_eff^2=g4_geom^2 |I_R|^2/(N_A N_chi) in the final declared convention"}, "available": ["equatorial measure", "scalar zero profile", "geometric representation operators"], "missing": ["localized regular vector profile", "action-derived common K4", "projector Pi_A", "physical matter profile"], "e_eff": None, "alpha": None},
        "potential": {**c("BHSM_M4_scalar_potential_map_v6_1_1"), "status": "BHSM_M4_SCALAR_POTENTIAL_PROFILE_MAP_DERIVED_CONDITIONALLY", "full_constant_profile": {"A4_raw": "(64 pi^2/3)A0 a^4", "G4_raw": "(64 pi^2/3)G0 a^4", "canonical_mass_parent": "A0/Zsigma", "canonical_quartic_time": "3G0/(64 pi^2 Zsigma^2 a^4)", "canonical_pump_t0": "-lambda/21"}, "normal": "mu0/a^2=0", "curvature": "no sigma-curvature term in the frozen parent action", "boundary": "none beyond a missing localization/potential coefficient", "tower": "no pure-singlet nontrivial heavy source", "v5": {"A_ST": "not derived", "G_ST": "not derived", "sigma_half": "not derived"}},
        "parent_v5": {**c("BHSM_parent_to_v5_v4_coefficient_map_v6_1_1"), "status": "BHSM_PARENT_TO_V5_V4_MAP_ADVANCED_CONDITIONALLY", "map": {"gravity": "formal bulk profile coefficient; independent M4 EH source required", "boundary_geometry": "exact equator/GHY", "gauge": "M5 exact; M4 localization coefficient required", "scalar_kinetic": "homogeneous bulk zero-mode exact; inhomogeneous M4 localization required", "scalar_quadratic": "A0/Zsigma plus canonical pump", "scalar_quartic": "profile-derived in the temporal/homogeneous normalization", "sigma": "bulk even zero mode; v5 boundary role conditional", "charged": "profile/current and physical group open", "neutral": "profile/current and physical group open", "boundary_collar": "coefficient source open", "scale_RG": "a-dependent normalization is not RG running", "recycling": "no new source"}, "frozen_values_changed": False},
        "fermionic": {**c("BHSM_fermionic_Clifford_boundary_readiness_v6_1_1"), "status": "BHSM_FERMIONIC_CLIFFORD_BOUNDARY_READINESS_DERIVED", "spin_structure": "I_t x S3 is spin for either orientation", "Clifford_bundle": "mathematically defined on the induced Lorentzian M4 geometry", "spin_connection": "induced Levi-Civita spin connection; equatorial extrinsic contribution vanishes on the background because K_mn=0", "candidate": "first-order spinorial/Clifford boundary operator with a specified self-adjoint domain", "associated_data": ["Sp1 representations", "nested U1 geometric weights", "even sigma bulk zero profile"], "physical_equation": None, "fermionic_action_source": None, "monopole_dependency": None},
        "scale": {**c("BHSM_M4_scale_primitive_audit_v6_1_1"), "status": "BHSM_M4_GEOMETRIC_PROFILE_SCALE_DERIVED_LOCALIZATION_PRIMITIVES_OPEN", "a_min_squared": "21 kappa1/(2 kappa0)", "geometric_normal_lengths": {"full_meridian": "pi a", "hemisphere": "pi a/2", "scalar_L_time_full": "4a/3", "scalar_L_time_hemisphere": "2a/3"}, "L_eff_connection": None, "new_geometric_primitive": False, "missing_boundary_coefficients": ["C_boundary", "tau_A", "Z_boundary or V_loc/r if localization is selected"], "absolute_unit": None},
        "hidden": {**c("BHSM_M4_hidden_input_claim_audit_v6_1_1"), "status": "BHSM_M4_HIDDEN_INPUTS_EXPOSED", "derived_inputs": ["round trajectory", "S4 warp and measures", "equatorial geometry", "normal spectrum", "constant scalar profile"], "conditional_inputs": ["hemisphere/orientation choice", "Z2 boundary interpretation"], "missing_inputs": ["boundary/localization action", "localized vector and metric profiles", "boundary coefficient values", "physical group/current map", "aperture projector", "fermionic action source"], "not_imported": ["Planck mass", "measured gauge couplings", "alpha", "1/137", "particle masses", "CKM", "PMNS", "cosmological parameters", "magnetic charge quantization"]},
        "report": {**c("BHSM_parent_M5_to_M4_boundary_report_v6_1_1"), "status": PRIMARY_RESULT, "boundary_action_status": "BHSM_M5_TO_M4_BOUNDARY_ACTION_PARTIAL", "central_answer": "The round M5 geometry contains an exact totally geodesic Lorentzian equator and an exact even scalar normal zero mode. Gauss-Codazzi, GHY variation, the warped Sturm-Liouville problem, boundary domains, and formal M4 profile coefficients are derived. However, the polar S4 is not a product M4 times an interval: smooth bulk temporal and S3-gradient weights differ, no regular massless tangential vector or product-graviton zero mode exists, and GHY supplies variational completion rather than independent boundary dynamics. The zero-mode architecture is exact, while a physical Lorentzian M4 action still requires explicit boundary/localization action sources with unsourced coefficients; no length, monopole sector, or physical fermion equation is invented.", "derived": ["permanent Clifford/no-monopole firewall", "exact S4 polar geometry", "totally geodesic equatorial M4", "Gauss-Codazzi and GHY ledgers", "self-adjoint scalar normal operator", "even scalar zero mode", "formal profile coefficients", "M4 kinematic Einstein tensor", "Clifford boundary geometry"], "conditional": ["hemisphere/Z2 physical-boundary role", "M4 gravity", "M4 gauge field", "inhomogeneous M4 sigma", "currents and aperture"], "constructive_requirements": ["action-derived intrinsic boundary or collar localization terms", "regular vector/metric profiles", "common Lorentzian kinetic normalization", "physical group and current map", "fermionic action source"], "completion_gate": COMPLETION_GATE, "recommended_next_branch": "bhsm-m4-boundary-localization-action-source-v6-1-2", "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE"},
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


def m5_m4_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def m5_m4_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.1.1 Parent M5 to Physical-Boundary M4 Reduction",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"
