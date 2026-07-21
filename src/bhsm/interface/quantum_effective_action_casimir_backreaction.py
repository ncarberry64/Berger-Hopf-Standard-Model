"""BHSM v5.10 quantum-effective-action and Casimir-backreaction audit.

The full one-loop determinant is blocked by unresolved gauge fixing, ghosts,
fermion provenance, and geometric fluctuation domains.  This module therefore
computes only the exact finite determinant of the action-supported homogeneous
scalar/topographic fluctuation orthogonal to the retained scale coordinate.
The reduced diagnostic keeps the renormalization scale explicit and is never
promoted to a field-theoretic Casimir energy or an absolute unit anchor.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, log, sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.10"
SPRINT = "bhsm-quantum-effective-action-casimir-backreaction-v5-10"
PRIMARY_RESULT = "BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL"
SIGMA_0 = 0.5
REFERENCE_L = 1.0
REFERENCE_MU = 1.0

ARTIFACT_FILES = {
    "mode_ownership": "BHSM_quantum_mode_ownership_v5_10.json",
    "euclidean_operators": "BHSM_quantum_euclidean_operator_domain_ledger_v5_10.json",
    "gauge_ghost": "BHSM_quantum_gauge_fixing_ghost_audit_v5_10.json",
    "spectral_ledger": "BHSM_quantum_berger_hopf_spectral_ledger_v5_10.json",
    "heat_kernel": "BHSM_quantum_heat_kernel_divergence_v5_10.json",
    "renormalization": "BHSM_quantum_renormalization_counterterm_v5_10.json",
    "zeta_determinant": "BHSM_quantum_zeta_determinant_v5_10.json",
    "casimir_anomaly": "BHSM_quantum_casimir_trace_anomaly_v5_10.json",
    "backreaction": "BHSM_quantum_backreaction_equations_v5_10.json",
    "effective_solution": "BHSM_quantum_effective_modulus_solution_v5_10.json",
    "pilot_wave_update": "BHSM_quantum_pilot_wave_no_double_counting_update_v5_10.json",
    "uploaded_source_audit": "BHSM_quantum_uploaded_source_audit_v5_10.json",
    "construction_report": "BHSM_quantum_effective_action_casimir_backreaction_report_v5_10.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "observed_mass_or_vev_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "ckm_fitting_used": False,
    "neutrino_limits_used": False,
    "cosmological_parameter_used": False,
    "hubble_or_cmb_calibration_used": False,
    "planck_length_inserted": False,
    "cutoff_promoted_to_physical_scale": False,
    "box_size_promoted_to_physical_scale": False,
    "subtraction_point_promoted_to_physical_scale": False,
    "casimir_coefficient_assumed": False,
    "legacy_mass_ansatz_used_as_action_result": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "physics_model_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "numerical_particle_masses_emitted": False,
    "physical_couplings_promoted": False,
    "rare_b_phenomenology_pursued": False,
}

OPEN_GATES = (
    "OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN",
    "OPEN_MISSING_FADDEEV_POPOV_GHOST_OPERATOR",
    "OPEN_MISSING_FULL_LOWER_ORDER_OPERATOR_TERMS",
    "OPEN_MISSING_FERMION_DIRAC_OPERATOR_ACTION_SOURCE",
    "OPEN_MISSING_FERMION_DETERMINANT_PHASE_ETA_INVARIANT",
    "OPEN_MISSING_GEOMETRIC_FLUCTUATION_GAUGE_AND_DOMAIN",
    "OPEN_MISSING_CHARGED_CURRENT_QUADRATIC_OPERATOR",
    "OPEN_MISSING_NEUTRAL_RESPONSE_NORMALIZATION",
    "OPEN_MISSING_COMPLETE_BERGER_HOPF_SPECTRAL_LEDGER",
    "OPEN_MISSING_FIELD_THEORETIC_HEAT_KERNEL_COEFFICIENTS",
    "OPEN_MISSING_RENORMALIZED_ACTION_COEFFICIENT_RUNNING",
    "OPEN_MISSING_FINITE_CASIMIR_SPECTRAL_REMAINDER",
    "OPEN_MISSING_TOTAL_TRACE_ANOMALY",
    "OPEN_MISSING_NONLINEAR_GEOMETRIC_BACKREACTION",
    "OPEN_MISSING_NONLINEAR_FULL_GEOMETRIC_BACKREACTION",
    "OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE",
    "OPEN_MISSING_PRIMORDIAL_QUANTUM_BOUNDARY_STATE_CLOSURE",
    "OPEN_MISSING_ABSOLUTE_ACTION_QUANTUM_OR_BOUNDARY_TENSION",
    "OPEN_MISSING_ABSOLUTE_SPECTRAL_EIGENVALUE_SOURCE",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "FULL_BHSM_NOT_COMPLETE",
)


@dataclass(frozen=True)
class ModeOwnershipRow:
    name: str
    background_value: str
    fluctuation: str
    statistics: str
    multiplicity: str
    sector_projector: str
    domain: str
    boundary_condition: str
    integrated_out: bool
    retained_collective: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OperatorRow:
    sector: str
    formula: str
    leading_symbol: str
    lower_order_terms: str
    field_space: str
    domain: str
    boundary_condition: str
    adjoint: str
    ellipticity: str
    zero_modes: str
    negative_modes: str
    multiplicity: str
    dimension: str
    determinant_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "BHSM v5.10 audits the one-loop construction and computes one exact "
            "finite homogeneous scalar/topographic determinant diagnostic. The "
            "full gauge, ghost, fermion, geometry, charged, neutral, heat-kernel, "
            "Casimir, anomaly, and renormalized backreaction system is not "
            "closed; no absolute unit, mass, coupling, CKM value, rare-B "
            "observable, physical validation, or full BHSM completion is derived."
        ),
        **GUARDS,
    }


def scalar_background(sigma: float = SIGMA_0) -> dict[str, float]:
    value = sigma / sqrt(2.0)
    return {"T": value, "Phi": value}


def classical_scale_potential(sigma: float) -> float:
    return -(sigma**2) + 2.0 * sigma**4


def radial_eigenvalue_hat(sigma: float) -> float:
    """Retained symmetric v5.7 Hessian eigenvalue."""

    return -2.0 + 24.0 * sigma**2


def orthogonal_eigenvalue_hat(sigma: float) -> float:
    """Integrated antisymmetric v5.7 Hessian eigenvalue."""

    return 4.0 + 8.0 * sigma**2


def orthogonal_eigenvalue(L: float, sigma: float = SIGMA_0) -> float:
    if L <= 0.0:
        raise ValueError("L must be positive")
    return orthogonal_eigenvalue_hat(sigma) / (L * L)


def reduced_zeta(s: float, L: float = REFERENCE_L, sigma: float = SIGMA_0) -> float:
    return orthogonal_eigenvalue(L, sigma) ** (-s)


def reduced_heat_trace(t: float, L: float = REFERENCE_L, sigma: float = SIGMA_0) -> float:
    if t < 0.0:
        raise ValueError("heat-trace time must be nonnegative")
    return exp(-t * orthogonal_eigenvalue(L, sigma))


def reduced_zeta_zero_data(sigma: float = SIGMA_0) -> dict[str, float]:
    eigen_hat = orthogonal_eigenvalue_hat(sigma)
    return {"zeta_hat_0": 1.0, "zeta_hat_prime_0": -log(eigen_hat)}


def reduced_log_determinant(
    L: float = REFERENCE_L,
    sigma: float = SIGMA_0,
    mu: float = REFERENCE_MU,
) -> float:
    if mu <= 0.0:
        raise ValueError("mu must be positive")
    return log(orthogonal_eigenvalue(L, sigma) / (mu * mu))


def reduced_log_determinant_zeta(
    L: float = REFERENCE_L,
    sigma: float = SIGMA_0,
    mu: float = REFERENCE_MU,
) -> float:
    if L <= 0.0 or mu <= 0.0:
        raise ValueError("L and mu must be positive")
    zero = reduced_zeta_zero_data(sigma)
    zeta_prime_L_0 = 2.0 * log(L) * zero["zeta_hat_0"] + zero["zeta_hat_prime_0"]
    return -zeta_prime_L_0 - 2.0 * zero["zeta_hat_0"] * log(mu)


def reduced_one_loop_action(
    L: float = REFERENCE_L,
    sigma: float = SIGMA_0,
    mu: float = REFERENCE_MU,
) -> float:
    return 0.5 * reduced_log_determinant(L, sigma, mu)


def reduced_effective_action(
    L: float = REFERENCE_L,
    sigma: float = SIGMA_0,
    mu: float = REFERENCE_MU,
) -> float:
    return classical_scale_potential(sigma) + reduced_one_loop_action(L, sigma, mu)


def effective_gradients(L: float, sigma: float) -> dict[str, float]:
    if L <= 0.0:
        raise ValueError("L must be positive")
    eigen_hat = orthogonal_eigenvalue_hat(sigma)
    return {
        "dGamma_dL": -1.0 / L,
        "dGamma_da_Berger": 0.0,
        "dGamma_dsigma": -2.0 * sigma + 8.0 * sigma**3 + 8.0 * sigma / eigen_hat,
        "dGamma_drho_star": 0.0,
    }


def effective_hessian(L: float, sigma: float) -> list[list[float]]:
    if L <= 0.0:
        raise ValueError("L must be positive")
    eigen_hat = orthogonal_eigenvalue_hat(sigma)
    sigma_sigma = (
        -2.0
        + 24.0 * sigma**2
        + 8.0 / eigen_hat
        - 128.0 * sigma**2 / (eigen_hat * eigen_hat)
    )
    return [
        [1.0 / (L * L), 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, sigma_sigma, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ]


def mode_rows() -> tuple[ModeOwnershipRow, ...]:
    background = "T=Phi=sigma_scale/sqrt(2)"
    return (
        ModeOwnershipRow("global size", "L>0", "delta L", "collective bosonic", "1", "none", "positive half-line", "primordial collective boundary-state condition open", False, True, "RETAINED_FOR_COLLECTIVE_QUANTIZATION"),
        ModeOwnershipRow("Berger squashing", "a_Berger", "delta a_Berger", "collective bosonic", "1", "none", "admissible positive Berger metrics", "geometric boundary condition unresolved", False, True, "RETAINED_BACKGROUND_DOMAIN_OPEN"),
        ModeOwnershipRow("scalar/topographic scale", "sigma_scale=1/2", "delta_parallel=(delta T+delta Phi)/sqrt(2)", "collective bosonic", "1", "scalar/topographic", "normalized homogeneous symmetric mode", "Robin zero-flux", False, True, "RETAINED_FOR_COLLECTIVE_QUANTIZATION"),
        ModeOwnershipRow("collar modulus", "rho_star=1 normalized", "delta rho_star", "collective bosonic", "1", "none", "positive collar endpoint", "fixed or natural collar condition unresolved", False, True, "RETAINED_BACKGROUND_CONVENTIONAL_OR_DYNAMICAL_OPEN"),
        ModeOwnershipRow("homogeneous scalar/topographic orthogonal mode", background, "delta_perp=(delta T-delta Phi)/sqrt(2)", "bosonic", "1", "scalar/topographic", "two-component homogeneous v5.7 reduced subspace", "Robin zero-flux", True, False, "EXACT_FINITE_REDUCED_DETERMINANT"),
        ModeOwnershipRow("nonhomogeneous scalar/topographic modes", background, "delta T_nonzero, delta Phi_nonzero", "bosonic", "unresolved", "scalar/topographic", "nonhomogeneous Berger/collar domain unresolved", "self-adjoint family unresolved", False, False, "EXCLUDED_OPEN_NONHOMOGENEOUS_SPECTRUM"),
        ModeOwnershipRow("geometric fluctuations", "h(L,a_Berger)", "delta g", "bosonic", "tensor multiplicity unresolved", "none", "metric perturbations modulo diffeomorphisms", "geometric gauge/domain unresolved", False, False, "EXCLUDED_OPEN_GEOMETRIC_HESSIAN"),
        ModeOwnershipRow("gauge fluctuations", "background connection unresolved", "delta A_i", "bosonic", "adjoint ranks 1,3,8 before physical projection", "P_i", "gauge-fixed/coexact domain not derived", "gauge boundary flux unresolved", False, False, "EXCLUDED_OPEN_GAUGE_FIXING"),
        ModeOwnershipRow("Faddeev-Popov ghosts", "none before gauge fixing", "c_i, cbar_i", "Grassmann", "unresolved", "P_i", "not defined without actual gauge-fixing functional", "ghost boundary condition unresolved", False, False, "EXCLUDED_GHOST_OPERATOR_NOT_DERIVED"),
        ModeOwnershipRow("fermion fluctuations", "fermion background not fixed by v5.4", "delta psi", "fermionic", "generation/chiral multiplicity conditional", "P_i and P_gen", "Hermitian spinor domain unresolved", "spinor boundary pairing conditional", False, False, "EXCLUDED_OPEN_DIRAC_ACTION_AND_DOMAIN"),
        ModeOwnershipRow("charged-current modes", "J_ch background unresolved", "delta J_ch or mediator", "bosonic/composite unresolved", "unresolved", "P_ch and P_gen", "quadratic field space not derived", "boundary condition not derived", False, False, "EXCLUDED_OPEN_CHARGED_QUADRATIC_OPERATOR"),
        ModeOwnershipRow("neutral-response modes", "N background unresolved", "delta N", "bosonic", "unresolved", "neutral projector", "neutral cone/domain conditional", "neutral flux conditional", False, False, "EXCLUDED_OPEN_NEUTRAL_NORMALIZATION"),
    )


def mode_ownership_payload() -> dict[str, Any]:
    rows = mode_rows()
    integrated = [row.name for row in rows if row.integrated_out]
    retained = [row.name for row in rows if row.retained_collective]
    return {
        **_common_payload("BHSM_quantum_mode_ownership_v5_10"),
        "status": "QUANTUM_MODE_OWNERSHIP_LEDGER_PARTIAL_EXPLICIT",
        "hierarchy": [
            "supported noncollective fluctuations -> Gamma_1loop",
            "retained collective variables -> Gamma_eff",
            "pilot-wave quantization only for retained collective variables",
        ],
        "rows": [row.to_dict() for row in rows],
        "integrated_modes": integrated,
        "retained_collective_modes": retained,
        "overlap": sorted(set(integrated).intersection(retained)),
        "double_counting_avoided": not set(integrated).intersection(retained),
    }


def operator_rows() -> tuple[OperatorRow, ...]:
    return (
        OperatorRow("scalar/topographic orthogonal homogeneous", "H_perp(L,sigma)=L^-2(4+8 sigma^2)", "finite 1x1 positive matrix; differential principal symbol not applicable", "v5.7 reduced potential Hessian", "span{(1,-1)/sqrt(2)}", "homogeneous v5.7 reduced subspace", "Robin zero-flux inherited from v5.7", "real symmetric", "not a differential ellipticity claim; strictly positive for L>0", "none", "none", "1", "length^-2 in symbolic scale family", "INCLUDED_EXACT_FINITE_REDUCED"),
        OperatorRow("scalar/topographic full", "diag(-partial_rho^2,-Delta_B)+Hess(V_ST) schematically", "scalar Laplace type where separately defined", "mixed collar/Berger lower-order realization incomplete", "delta T plus delta Phi", "full mixed collar/Berger domain unresolved", "nonhomogeneous self-adjoint family unresolved", "formal only", "NOT_ESTABLISHED_FOR_COUPLED_FULL_DOMAIN", "possible collective mode", "background dependent", "unresolved", "length^-2 candidate", "EXCLUDED"),
        OperatorRow("gauge", "(1/lambda_i)L_i(rho)", "Laplace-type candidate", "OPEN_MISSING_FULL_LOWER_ORDER_OPERATOR_TERMS", "adjoint-valued one-forms", "OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN", "admissible gauge flux unresolved", "formal Hermitian on controlled domain", "NOT_ESTABLISHED", "exact gauge modes unprojected", "unresolved", "1,3,8 raw adjoint ranks", "length^-2 candidate", "EXCLUDED"),
        OperatorRow("ghost", "not derived", "not derived", "not derived", "Grassmann gauge parameters", "not derived", "not derived", "not derived", "NOT_ESTABLISHED", "not classified", "not classified", "unresolved", "length^-2 expected but not promoted", "EXCLUDED"),
        OperatorRow("fermion positive determinant", "D_f^dagger D_f not derived from completed D_f domain", "Dirac-square candidate", "action coefficient, connection, and boundary terms open", "spinor/generation module", "Hermitian spinor domain unresolved", "eta/boundary condition unresolved", "conditional", "NOT_ESTABLISHED", "Dirac zero modes possible", "not classified", "conditional", "length^-2 candidate", "EXCLUDED"),
        OperatorRow("charged", "H_ch not derived", "not derived", "interaction second variation open", "charged current/mediator space", "not derived", "not derived", "not derived", "NOT_ESTABLISHED", "not classified", "not classified", "unresolved", "unresolved", "EXCLUDED"),
        OperatorRow("neutral", "K_neu symbolic", "conditional", "normalization and scale open", "neutral response cone", "conditional cone/domain", "neutral flux conditional", "formal self-adjoint", "NOT_ESTABLISHED", "neutral kernel modes possible", "not classified", "unresolved", "unresolved", "EXCLUDED"),
        OperatorRow("geometry", "kappa_geom L_geom symbolic", "not fully derived after geometric gauge fixing", "curvature and boundary terms incomplete", "metric perturbations", "diffeomorphism/shape quotient unresolved", "geometric boundary flux unresolved", "formal", "NOT_ESTABLISHED", "diffeomorphism/shape modes unresolved", "conformal/negative modes unresolved", "unresolved", "length^-2 candidate", "EXCLUDED"),
    )


def euclidean_operator_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_euclidean_operator_domain_ledger_v5_10"),
        "status": "EUCLIDEAN_OPERATOR_LEDGER_PARTIAL_FULL_DETERMINANT_BLOCKED",
        "continuation": {
            "full_Lorentzian_to_Euclidean_map": None,
            "reason": "v5.4 supplies a symbolic boundary action, not a closed Lorentzian action with all signs and domains",
            "reduced_scalar_convention": "exp(i S_L) -> exp(-S_E); use the real v5.7 reduced Hessian on its declared Robin domain",
            "continued_metric": "positive normalized Berger boundary metric for the reduced scalar block only",
            "fermion_continuation": None,
            "gauge_fixing_term": None,
            "reality_conditions": "delta_perp real in the included reduced block",
            "boundary_orientation": "v5.7 outward orientation and Robin zero-flux retained",
        },
        "operators": [row.to_dict() for row in operator_rows()],
        "included_bosonic_operator_positive": orthogonal_eigenvalue_hat(SIGMA_0) > 0.0,
        "included_bosonic_differential_ellipticity_claimed": False,
        "full_bosonic_ellipticity_established": False,
        "conformal_or_negative_mode_status": "unresolved outside included scalar block",
    }


def gauge_ghost_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_gauge_fixing_ghost_audit_v5_10"),
        "status": "GAUGE_AND_GHOST_DETERMINANT_BLOCKED",
        "action_source": "v5.4 conditional gauge quadratic slot and v4.6 operator candidate",
        "gauge_fixing_functional": None,
        "gauge_fixing_action": None,
        "gauge_parameter": None,
        "faddeev_popov_operator": None,
        "ghost_boundary_conditions": None,
        "residual_gauge_transformations": "unresolved",
        "zero_mode_projection": "required but not constructed",
        "candidate_d_dagger_d_promoted_to_final_operator": False,
        "gauge_determinant_included": False,
        "ghost_determinant_included": False,
        "gauge_parameter_variation_performed": False,
        "gauge_parameter_independence_established": False,
        "reason": "No actual BHSM gauge-fixing functional and compatible ghost domain are derived.",
    }


def spectral_ledger_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_berger_hopf_spectral_ledger_v5_10"),
        "status": "BERGER_HOPF_SPECTRAL_LEDGER_CONTROLLED_REDUCED_SUBSET",
        "background": {"L": "positive symbolic modulus", "a_Berger": "retained", "sigma_scale": SIGMA_0, "rho_star": "retained normalized collar modulus"},
        "modes": [
            {
                "name": "delta_perp",
                "eigenvalue": "(4+8 sigma_scale^2)/L^2",
                "eigenvalue_at_sigma_half": "6/L^2",
                "degeneracy": 1,
                "mode_labels": {"homogeneous": True, "internal_vector": "(1,-1)/sqrt(2)"},
                "sector": "scalar/topographic",
                "statistics": "bosonic",
                "integrated_out": True,
                "zero_mode": False,
                "negative_mode": False,
                "L_scaling": "L^-2 symbolic operator-dimension family",
                "a_Berger_dependence": "none in homogeneous v5.7 reduction; full dependence open",
                "sigma_scale_dependence": "4+8 sigma_scale^2",
                "rho_star_dependence": "none in normalized v5.7 reduction; physical collar dependence open",
            },
            {
                "name": "delta_parallel",
                "eigenvalue": "(-2+24 sigma_scale^2)/L^2",
                "eigenvalue_at_sigma_half": "4/L^2",
                "degeneracy": 1,
                "mode_labels": {"homogeneous": True, "internal_vector": "(1,1)/sqrt(2)"},
                "sector": "retained sigma_scale collective coordinate",
                "statistics": "collective bosonic",
                "integrated_out": False,
                "zero_mode": False,
                "negative_mode": False,
                "L_scaling": "L^-2 diagnostic only",
                "a_Berger_dependence": "none in homogeneous reduction",
                "sigma_scale_dependence": "-2+24 sigma_scale^2",
                "rho_star_dependence": "none in normalized reduction",
            },
        ],
        "exact_sectors": ["finite homogeneous scalar/topographic orthogonal mode"],
        "truncated_infinite_sectors": [],
        "mode_cutoff_used": False,
        "flat_space_momentum_integral_used": False,
        "complete_BHSM_spectrum": False,
        "missing_sectors": ["nonhomogeneous scalar/topographic", "geometry", "gauge", "ghost", "fermion", "charged", "neutral"],
    }


def heat_kernel_payload() -> dict[str, Any]:
    eigen = orthogonal_eigenvalue(REFERENCE_L, SIGMA_0)
    return {
        **_common_payload("BHSM_quantum_heat_kernel_divergence_v5_10"),
        "status": "FINITE_REDUCED_HEAT_TRACE_EXACT_FIELD_THEORY_DIVERGENCES_OPEN",
        "included_trace": "K_perp(t)=exp[-t(4+8 sigma_scale^2)/L^2]",
        "heat_trace_and_zeta_use_same_single_eigenvalue": True,
        "sample_coefficients": {"t^0": 1.0, "t^1": -eigen, "t^2": 0.5 * eigen * eigen},
        "coefficients_are_field_theory_Seeley_DeWitt": False,
        "reason": "The included determinant is one finite-dimensional homogeneous mode, not a complete differential spectrum.",
        "full_coefficients": {"a_0": None, "a_1_over_2": None, "a_1": None, "a_3_over_2": None, "a_2": None},
        "ultraviolet_divergence_in_included_finite_mode": False,
        "full_ultraviolet_divergence_structure_derived": False,
        "required_local_counterterm_classes_to_audit_later": ["volume", "scalar curvature", "curvature squared", "gauge kinetic", "scalar potential", "boundary tension", "K", "K^2", "Tr(S^2)", "collar"],
        "new_action_term_added": False,
    }


def renormalization_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_renormalization_counterterm_v5_10"),
        "status": "RENORMALIZATION_NOT_CLOSED_MU_EXPLICIT",
        "bare_coefficients": "v5.4 symbolic coefficients",
        "divergent_counterterms": None,
        "renormalized_coefficients": None,
        "finite_scheme_dependent_local_terms": None,
        "finite_scheme_independent_spectral_remainder": None,
        "included_finite_mode_scheme": "exact zeta determinant equals direct finite determinant",
        "second_field_theory_scheme_compared": False,
        "reason_second_scheme_unavailable": "no complete differential operator or heat-kernel subtraction ledger",
        "renormalization_scale": "mu retained explicitly",
        "mu_derivative_of_reduced_Gamma_1loop": -1.0,
        "coefficient_running_available_to_cancel_mu": False,
        "renormalization_group_invariance_established": False,
        "Lambda_BH": None,
        "subtraction_point_selected": None,
        "absolute_unit_from_mu_claimed": False,
    }


def zeta_determinant_payload() -> dict[str, Any]:
    direct = reduced_log_determinant()
    zeta = reduced_log_determinant_zeta()
    zero = reduced_zeta_zero_data()
    return {
        **_common_payload("BHSM_quantum_zeta_determinant_v5_10"),
        "status": "EXACT_FINITE_REDUCED_ZETA_DETERMINANT_COMPUTED",
        "determinant_scope": "one integrated homogeneous scalar/topographic orthogonal mode",
        "operator": "H_perp=L^-2(4+8 sigma_scale^2)",
        "zeta": "zeta_perp(s)=[L^-2(4+8 sigma_scale^2)]^-s",
        "zeta_hat_0": zero["zeta_hat_0"],
        "zeta_hat_prime_0_at_sigma_half": zero["zeta_hat_prime_0"],
        "log_determinant_formula": "log det(H_perp/mu^2)=log(4+8 sigma_scale^2)-2 log(mu L)",
        "direct_sample": direct,
        "zeta_sample": zeta,
        "direct_zeta_residual": abs(direct - zeta),
        "bosonic_contribution": "Gamma_1loop,perp=1/2 log det(H_perp/mu^2)",
        "fermionic_contribution": None,
        "ghost_contribution": None,
        "eta_phase_contribution": None,
        "zero_modes_removed": [],
        "negative_modes": [],
        "cutoff_used": False,
        "full_one_loop_action_derived": False,
    }


def casimir_anomaly_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_casimir_trace_anomaly_v5_10"),
        "status": "CASIMIR_AND_TOTAL_ANOMALY_NOT_DERIVED_REDUCED_SCALE_RESPONSE_ONLY",
        "total_zero_point_sum": None,
        "renormalized_vacuum_energy": None,
        "finite_Casimir_remainder": None,
        "local_counterterm_contribution": None,
        "sector_contributions": {"scalar_topographic_orthogonal_mode": "finite determinant diagnostic only", "all_other_sectors": None},
        "Casimir_sign": None,
        "Casimir_L_dependence": None,
        "Casimir_Berger_squashing_dependence": None,
        "regulator_dependence": "no cutoff in finite mode; full regulator comparison unavailable",
        "truncated_zeta_total_0": 1.0,
        "scale_variation_delta_Gamma_per_delta_omega": -1.0,
        "integrated_trace_interpretation": "reduced one-mode scale response only",
        "beta_function_contribution": None,
        "boundary_anomaly": None,
        "genuine_BHSM_scale_anomaly_derived": False,
        "dimensional_transmutation_derived": False,
    }


def backreaction_payload() -> dict[str, Any]:
    gradients = effective_gradients(REFERENCE_L, SIGMA_0)
    return {
        **_common_payload("BHSM_quantum_backreaction_equations_v5_10"),
        "status": "REDUCED_PARTIAL_BACKREACTION_EQUATIONS_DERIVED",
        "Gamma_eff_reduced": "-sigma^2+2 sigma^4+1/2 log[(4+8 sigma^2)/(mu^2 L^2)]",
        "classical_terms": "-sigma^2+2 sigma^4; no L,a_Berger,rho_star potential in current normalized reduction",
        "quantum_terms": "1/2 log[(4+8 sigma^2)/(mu^2 L^2)] from delta_perp only",
        "equations": {
            "dGamma_dL": "-1/L",
            "dGamma_da_Berger": "0 in homogeneous reduced determinant; full dependence open",
            "dGamma_dsigma": "-2 sigma+8 sigma^3+8 sigma/(4+8 sigma^2)",
            "dGamma_drho_star": "0 in normalized reduced determinant; full dependence open",
        },
        "sample_at_L1_sigma_half": gradients,
        "reduced_scale_stress": "-dGamma_1loop/d(ln L)=1",
        "full_quantum_stress_tensor": None,
        "Berger_metric_backreaction": None,
        "squashing_backreaction": None,
        "extrinsic_curvature_backreaction": None,
        "shape_operator_backreaction": None,
        "collar_Jacobian_backreaction": None,
        "first_nonhomogeneous_perturbations": None,
    }


def effective_solution_payload() -> dict[str, Any]:
    hessian_sigma_zero = effective_hessian(REFERENCE_L, 0.0)
    return {
        **_common_payload("BHSM_quantum_effective_modulus_solution_v5_10"),
        "status": "NO_FINITE_STABLE_EFFECTIVE_MODULUS_SOLUTION_IN_PARTIAL_SYSTEM",
        "scale_classification": "ANOMALOUS_BUT_REFERENCE_SCALE_DEPENDENT_PARTIAL",
        "stationary_analysis": {
            "L_equation": "-1/L=0 has no finite positive solution",
            "finite_L0": None,
            "sigma_equation_real_roots": [0.0],
            "sigma_half_stationary_after_partial_loop": False,
            "sigma_half_force": effective_gradients(REFERENCE_L, SIGMA_0)["dGamma_dsigma"],
            "sigma_zero_hessian": hessian_sigma_zero[2][2],
            "sigma_zero_classification": "degenerate quartic point in reduced diagnostic; not a positive-Hessian physical vacuum",
            "a_Berger": None,
            "rho_star": None,
            "unique": False,
            "stable": False,
            "global_or_local": None,
        },
        "coupled_hessian_order": ["L", "a_Berger", "sigma_scale", "rho_star"],
        "coupled_hessian_at_formal_sigma_zero_L1": hessian_sigma_zero,
        "positive_physical_hessian": False,
        "unprojected_negative_mode_status": "unresolved in excluded sectors",
        "regulator_independence": "finite one-mode determinant only; full result unavailable",
        "renormalization_group_consistency": False,
        "gauge_parameter_independence": False,
        "absolute_ell_star": None,
        "M_star": None,
        "M_BH": None,
        "R_BH": None,
        "hidden_reference_scale": "mu remains explicit and is not promoted",
        "v5_7_sigma_half_preserved_as_official_input": True,
        "partial_diagnostic_not_promoted_to_v5_7_correction": True,
    }


def pilot_wave_update_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_pilot_wave_no_double_counting_update_v5_10"),
        "status": "PILOT_WAVE_UPDATE_DEFERRED_PARTIAL_EFFECTIVE_ACTION_NO_DOUBLE_COUNTING_EXPLICIT",
        "collective_variables": ["L", "a_Berger", "sigma_scale", "rho_star"],
        "integrated_one_loop_modes": ["delta_perp=(delta T-delta Phi)/sqrt(2)"],
        "collective_Hamiltonian_candidate": "H_eff may use Gamma_eff,red only after full renormalized action closure",
        "official_v5_9_Hamiltonian_changed": False,
        "one_loop_mode_included_in_Bohmian_quantum_potential": False,
        "double_counting_avoided": True,
        "guidance_recomputed": False,
        "reason": "the partial mu-dependent determinant is not a closed collective potential",
        "v5_9_expanding_trajectory_status": "preserved as prior scale-covariant conditional result; survival under full backreaction open",
        "finite_attractor_generated": False,
        "primordial_interpretation": "scale-free compact-to-expanding interpretation retained; no white-hole observation claim",
        "redshift_generates_unit": False,
        "redshifted_relics": "physical on-shell relics, not virtual",
        "effective_or_virtual_memory": "boundary/topographic or pilot-wave response memory only",
    }


def uploaded_source_audit_payload() -> dict[str, Any]:
    return {
        **_common_payload("BHSM_quantum_uploaded_source_audit_v5_10"),
        "status": "UPLOADED_SOURCE_CANDIDATES_AUDITED_NOT_USED_AS_SCALE_INPUTS",
        "available_uploads": ["pasted sprint instruction"],
        "manuscript_files_present_in_attachment": [],
        "rows": [
            {"source": "Casimir notation description", "allowed": "motivation for an actual spectral calculation", "used": "terminology only", "imported_numeric_coefficient": False},
            {"source": "fine-structure curvature-projection description", "allowed": "later gauge-normalization candidate only", "used": "not used in determinant", "alpha_promoted": False},
            {"source": "local-curvature mass description", "allowed": "audit K[rho]=-Delta log rho for later action work", "used": "legacy candidate only; absent from included reduced Hessian", "mass_ansatz_used": False},
            {"source": "mass-gap description", "allowed": "superseded historical source", "used": "kept invalidated", "mass_gap_restored": False},
            {"source": "cosmology descriptions", "allowed": "ontology distinctions only", "used": "relic/memory language only", "phenomenological_coefficients_used": []},
        ],
        "K_rho_natural_appearance_in_included_hessian": False,
        "K_rho_action_derivation_claimed": False,
        "old_curvature_threshold_mass_gap_remains_invalidated": True,
        "forbidden_values_used": [],
    }


def construction_report_payload() -> dict[str, Any]:
    solution = effective_solution_payload()
    return {
        **_common_payload("BHSM_quantum_effective_action_casimir_backreaction_report_v5_10"),
        "status": PRIMARY_RESULT,
        "background_variables": {
            "L": "retained positive global size modulus",
            "a_Berger": "retained squashing coordinate; determinant dependence open",
            "sigma_scale": "retained collective coordinate with official v5.7 input 1/2",
            "rho_star": "retained; normalized value 1 is conventional until dynamics closes",
        },
        "mode_ownership": mode_ownership_payload(),
        "euclidean_operators": euclidean_operator_payload(),
        "gauge_and_ghosts": gauge_ghost_payload(),
        "spectrum": spectral_ledger_payload(),
        "heat_kernel": heat_kernel_payload(),
        "renormalization": renormalization_payload(),
        "zeta_determinant": zeta_determinant_payload(),
        "casimir_and_anomaly": casimir_anomaly_payload(),
        "backreaction": backreaction_payload(),
        "effective_solution": solution,
        "pilot_wave_update": pilot_wave_update_payload(),
        "uploaded_source_audit": uploaded_source_audit_payload(),
        "derived": [
            "explicit disjoint ownership of retained collective modes and the one integrated reduced fluctuation",
            "exact positive finite determinant for the homogeneous scalar/topographic orthogonal mode",
            "direct and zeta determinant equality without a cutoff",
            "explicit mu and L dependence of the controlled reduced determinant",
            "reduced backreaction equations and proof that dGamma/dL=-1/L has no finite positive root",
        ],
        "conditionally_established": [
            "the reduced determinant uses the v5.7 homogeneous Robin Hessian and symbolic L^-2 scale family only",
            "the one-mode scale response is a diagnostic, not a complete Casimir energy or trace anomaly",
            "the v5.9 pilot-wave layer can accept a future closed Gamma_eff without double counting integrated modes",
        ],
        "invalidated_or_ruled_out": [
            "a complete BHSM one-loop action cannot be claimed from the current operator ledger",
            "the candidate gauge Laplacian cannot be used without gauge fixing and ghosts",
            "log(mu L) alone is not an absolute scale or dimensional-transmutation prediction",
            "the finite homogeneous determinant is not the full Casimir spectral remainder",
            "the legacy curvature-threshold mass ansatz and mass-gap shortcut are not action results",
        ],
        "still_requiring_new_mathematics": list(OPEN_GATES),
        "scale_result": {
            "scale_covariance_preserved": "not decidable for full theory",
            "dimensional_transmutation": False,
            "RG_invariant_scale": None,
            "absolute_ell_star": solution["absolute_ell_star"],
            "hidden_reference_scale": solution["hidden_reference_scale"],
        },
        "claim_safe_conclusion": (
            "BHSM v5.10 produces a controlled partial effective-action audit and "
            "one exact finite reduced scalar/topographic determinant. Missing "
            "gauge/ghost, fermion, geometry, charged, neutral, heat-kernel, and "
            "renormalization data block a physical Casimir or total anomaly. The "
            "partial log(mu L) force has no finite L stationary point and does "
            "not generate an absolute unit."
        ),
        "recommended_next_construction_sprint": "bhsm-full-geometric-gauge-fixed-hessian-v5-11",
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "mode_ownership": mode_ownership_payload(),
        "euclidean_operators": euclidean_operator_payload(),
        "gauge_ghost": gauge_ghost_payload(),
        "spectral_ledger": spectral_ledger_payload(),
        "heat_kernel": heat_kernel_payload(),
        "renormalization": renormalization_payload(),
        "zeta_determinant": zeta_determinant_payload(),
        "casimir_anomaly": casimir_anomaly_payload(),
        "backreaction": backreaction_payload(),
        "effective_solution": effective_solution_payload(),
        "pilot_wave_update": pilot_wave_update_payload(),
        "uploaded_source_audit": uploaded_source_audit_payload(),
        "construction_report": construction_report_payload(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = artifact_dir / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def quantum_effective_action_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _ = repo_root
    report = construction_report_payload()
    report["artifacts"] = {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()}
    return report


def quantum_effective_action_status_to_markdown(report: dict[str, Any]) -> str:
    solution = report["effective_solution"]
    return "\n".join(
        [
            "# BHSM v5.10 Quantum Effective Action and Casimir Backreaction",
            "",
            f"Primary result: `{report['primary_result']}`.",
            "",
            "The only included determinant is the exact finite homogeneous scalar/topographic mode orthogonal to the retained `sigma_scale` coordinate.",
            "",
            "`Gamma_1loop,perp = 1/2 log[(4+8 sigma_scale^2)/(mu^2 L^2)]`",
            "",
            f"Finite L0: `{solution['stationary_analysis']['finite_L0']}`.",
            "",
            f"Absolute ell_star: `{solution['absolute_ell_star']}`.",
            "",
            "Gauge fixing, ghosts, fermions, geometry, full spectra, heat-kernel subtraction, and renormalization remain open; no Casimir energy or physical anomaly is claimed.",
            "",
            "## Open gates",
            "",
            *[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]],
        ]
    ) + "\n"
