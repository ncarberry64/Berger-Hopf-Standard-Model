"""BHSM v14.60 global-envelopment cap-selection theorem harness.

This module tests the paradigm shift motivated by the v14.59 cap obstruction:
do not infer a child cap from seam data alone.  Instead vary a complete reduced
parent-child envelopment functional in which the child interior profile, seam
value, seam traction, and relational nesting coordinate are solved together.

The implemented functional is deliberately a reduced convex theorem witness,
not the full BHSM gravity/gauge/fermion action.  Its purpose is to prove that a
global variational architecture *can* lift a local seam degeneracy without any
retuning: two profiles with exactly the same regular-center and seam Cauchy data
are distinguished by the globally integrated action, and strict convexity gives
one isolated stationary profile in the reduced model.

The result does NOT prove that the physical BHSM action has a unique cap.  That
requires deriving the actual gauge-fixed global Hessian from the unified action
and solving the full parent-child fields.  No physical mass, coupling, CKM/PMNS
matrix, scale, lifetime, cross section, or completed BHSM prediction is emitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.polynomial import Polynomial

VERSION = "v14.60"

PRIMARY_VERDICT = (
    "BHSM_V14_60_GLOBAL_ENVELOPMENT_VARIATION_LIFTS_THE_V14_59_LOCAL_SEAM_"
    "DEGENERACY_IN_A_STRICTLY_CONVEX_REDUCED_PARENT_CHILD_FUNCTIONAL_BY_"
    "SELECTING_THE_INTERIOR_SEAM_AND_RELATIONAL_NESTING_SIMULTANEOUSLY_"
    "BUT_PHYSICAL_CAP_UNIQUENESS_REMAINS_CONDITIONAL_ON_THE_FULL_BHSM_"
    "GAUGE_REDUCED_GLOBAL_HESSIAN"
)
DEGENERACY_VERDICT = (
    "BHSM_TWO_CAP_PROFILES_CAN_HAVE_IDENTICAL_REGULAR_CENTER_AND_SEAM_"
    "CAUCHY_DATA_WHILE_THE_GLOBAL_ENVELOPMENT_ACTION_STRICTLY_DISTINGUISHES_"
    "THEM_SO_LOCAL_BOUNDARY_EQUIVALENCE_IS_NOT_GLOBAL_VARIATIONAL_EQUIVALENCE"
)
UNIQUENESS_VERDICT = (
    "BHSM_THE_REDUCED_GLOBAL_ENVELOPMENT_FUNCTIONAL_IS_STRICTLY_CONVEX_FOR_"
    "POSITIVE_LOCAL_ENERGY_AND_PARENT_BUDGET_WEIGHTS_SO_ITS_STATIONARY_"
    "PARENT_CHILD_CAP_AND_NESTING_SOLUTION_IS_UNIQUE_IN_THE_REDUCED_CLASS"
)
SEAM_OUTPUT_VERDICT = (
    "BHSM_IN_THE_GLOBAL_FORMULATION_THE_SEAM_VALUE_AND_NORMAL_TRACTION_ARE_"
    "VARIATIONAL_OUTPUTS_COSELECTED_WITH_THE_CHILD_INTERIOR_AND_LOG_NESTING_"
    "COORDINATE_RATHER_THAN_INPUT_DATA_USED_TO_MANUFACTURE_THE_CAP"
)
EXACT_NEXT_OBJECT = (
    "FULL_UNIFIED_BHSM_GLOBAL_ENVELOPMENT_EULER_LAGRANGE_SYSTEM_ON_THE_"
    "COSMOLOGICAL_PARENT_AND_REGULAR_CHILD_CAP_WITH_ACTION_DERIVED_"
    "COEFFICIENTS_COMPLETE_GAUGE_METRIC_GHOST_FIXING_AND_THREE_TRANSVERSE_"
    "MOVING_SEAM_CHANNELS_FOLLOWED_BY_A_GLOBAL_HESSIAN_UNIQUENESS_SEARCH_"
    "AND_ZERO_RETUNING_NEUTRINO_DTN_HEAT_KERNEL_EXECUTION"
)


@dataclass(frozen=True)
class EnvelopmentParameters:
    """Dimensionless diagnostic coefficients for the reduced theorem witness.

    x = log(R_child/R_parent) is a relational coordinate.  All defaults are
    synthetic, frozen test coefficients; they are not BHSM physical inputs.
    """

    mu2: float = 1.8
    global_budget_weight: float = 2.2
    budget_nesting_coupling: float = 0.75
    seam_value_weight: float = 1.4
    seam_value_nesting_coupling: float = 0.60
    seam_slope_weight: float = 0.90
    seam_slope_nesting_coupling: float = -0.35
    nesting_weight: float = 1.10
    nesting_reference: float = -1.00
    source_amplitude: float = 0.65
    interior_modes: int = 6
    degeneracy_probe_amplitude: float = 0.40


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def validate_parameters(parameters: EnvelopmentParameters) -> None:
    positive = {
        "mu2": parameters.mu2,
        "global_budget_weight": parameters.global_budget_weight,
        "seam_value_weight": parameters.seam_value_weight,
        "seam_slope_weight": parameters.seam_slope_weight,
        "nesting_weight": parameters.nesting_weight,
    }
    for name, value in positive.items():
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be positive and finite")
    finite = {
        "budget_nesting_coupling": parameters.budget_nesting_coupling,
        "seam_value_nesting_coupling": parameters.seam_value_nesting_coupling,
        "seam_slope_nesting_coupling": parameters.seam_slope_nesting_coupling,
        "nesting_reference": parameters.nesting_reference,
        "source_amplitude": parameters.source_amplitude,
        "degeneracy_probe_amplitude": parameters.degeneracy_probe_amplitude,
    }
    for name, value in finite.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if not isinstance(parameters.interior_modes, int) or parameters.interior_modes < 1:
        raise ValueError("interior_modes must be a positive integer")


def _integral_01(poly: Polynomial) -> float:
    antiderivative = poly.integ()
    return float(antiderivative(1.0) - antiderivative(0.0))


def seam_value_mode() -> Polynomial:
    """Regular center; unit value and zero normal derivative at the seam."""

    r = Polynomial([0.0, 1.0])
    return 3.0 * r**2 - 2.0 * r**3


def seam_slope_mode() -> Polynomial:
    """Regular center; zero seam value and unit seam normal derivative."""

    r = Polynomial([0.0, 1.0])
    return r**2 * (r - 1.0)


def interior_mode(index: int) -> Polynomial:
    """Interior deformation invisible to both center and seam Cauchy data."""

    if not isinstance(index, int) or index < 0:
        raise ValueError("nonnegative integer index required")
    r = Polynomial([0.0, 1.0])
    return r ** (index + 2) * (1.0 - r) ** 2


def profile_basis(interior_modes: int, mu2: float = 1.8) -> list[Polynomial]:
    if not isinstance(interior_modes, int) or interior_modes < 1:
        raise ValueError("positive integer interior_modes required")
    if not math.isfinite(mu2) or mu2 <= 0.0:
        raise ValueError("positive finite mu2 required")
    normalized: list[Polynomial] = []
    for index in range(interior_modes):
        mode = interior_mode(index)
        norm2 = _integral_01(mode.deriv() * mode.deriv() + mu2 * mode * mode)
        normalized.append(mode / math.sqrt(norm2))
    return [seam_value_mode(), seam_slope_mode()] + normalized


def rho_profile() -> Polynomial:
    return Polynomial([1.0, 1.0])


def source_profile() -> Polynomial:
    return Polynomial([0.0, 1.0, -1.0])


def local_gram_matrix(basis: Sequence[Polynomial], mu2: float) -> np.ndarray:
    if not math.isfinite(mu2) or mu2 <= 0.0:
        raise ValueError("positive finite mu2 required")
    n = len(basis)
    matrix = np.zeros((n, n), dtype=float)
    for i, left in enumerate(basis):
        for j in range(i, n):
            right = basis[j]
            value = _integral_01(
                left.deriv() * right.deriv() + mu2 * left * right
            )
            matrix[i, j] = value
            matrix[j, i] = value
    return matrix


def projection_vector(basis: Sequence[Polynomial], weight: Polynomial) -> np.ndarray:
    return np.array([_integral_01(weight * mode) for mode in basis], dtype=float)


def global_linear_system(
    parameters: EnvelopmentParameters,
) -> tuple[np.ndarray, np.ndarray, list[Polynomial], dict[str, np.ndarray]]:
    """Return Hessian H and source b for H z = b.

    z = (s, t, c_0, ..., c_{N-1}, x), where s and t are seam value and
    normal traction coordinates and x=log(R_child/R_parent).
    """

    validate_parameters(parameters)
    basis = profile_basis(parameters.interior_modes, parameters.mu2)
    gram = local_gram_matrix(basis, parameters.mu2)
    budget = projection_vector(basis, rho_profile())
    source = projection_vector(basis, source_profile())
    n_profile = len(basis)
    e_value = np.zeros(n_profile, dtype=float)
    e_slope = np.zeros(n_profile, dtype=float)
    e_value[0] = 1.0
    e_slope[1] = 1.0

    gamma = parameters.global_budget_weight
    q = parameters.budget_nesting_coupling
    eta_s = parameters.seam_value_weight
    chi_s = parameters.seam_value_nesting_coupling
    eta_t = parameters.seam_slope_weight
    chi_t = parameters.seam_slope_nesting_coupling
    nu = parameters.nesting_weight

    h_pp = (
        gram
        + gamma * np.outer(budget, budget)
        + eta_s * np.outer(e_value, e_value)
        + eta_t * np.outer(e_slope, e_slope)
    )
    h_px = -(
        gamma * q * budget + eta_s * chi_s * e_value + eta_t * chi_t * e_slope
    )
    h_xx = gamma * q * q + eta_s * chi_s * chi_s + eta_t * chi_t * chi_t + nu

    hessian = np.zeros((n_profile + 1, n_profile + 1), dtype=float)
    hessian[:-1, :-1] = h_pp
    hessian[:-1, -1] = h_px
    hessian[-1, :-1] = h_px
    hessian[-1, -1] = h_xx

    rhs = np.zeros(n_profile + 1, dtype=float)
    rhs[:-1] = parameters.source_amplitude * source
    rhs[-1] = nu * parameters.nesting_reference

    auxiliaries = {
        "gram": gram,
        "budget": budget,
        "source": source,
        "e_value": e_value,
        "e_slope": e_slope,
    }
    return hessian, rhs, basis, auxiliaries


def solve_global_stationary(
    parameters: EnvelopmentParameters | None = None,
) -> dict[str, Any]:
    parameters = parameters or EnvelopmentParameters()
    hessian, rhs, basis, aux = global_linear_system(parameters)
    eigenvalues = np.linalg.eigvalsh(hessian)
    if float(np.min(eigenvalues)) <= 0.0:
        raise RuntimeError("global reduced Hessian is not positive definite")
    solution = np.linalg.solve(hessian, rhs)
    profile_coordinates = solution[:-1]
    x = float(solution[-1])
    return {
        "parameters": parameters,
        "hessian": hessian,
        "rhs": rhs,
        "basis": basis,
        "aux": aux,
        "solution": solution,
        "profile_coordinates": profile_coordinates,
        "seam_value": float(profile_coordinates[0]),
        "seam_slope": float(profile_coordinates[1]),
        "interior_coefficients": profile_coordinates[2:].copy(),
        "log_nesting": x,
        "nesting_ratio": math.exp(x),
        "hessian_eigenvalues": eigenvalues,
        "min_hessian_eigenvalue": float(np.min(eigenvalues)),
        "condition_number": float(np.linalg.cond(hessian)),
        "stationarity_residual": float(np.linalg.norm(hessian @ solution - rhs)),
    }


def profile_polynomial(profile_coordinates: Sequence[float], basis: Sequence[Polynomial]) -> Polynomial:
    coordinates = np.asarray(profile_coordinates, dtype=float)
    if coordinates.shape != (len(basis),):
        raise ValueError("profile coordinate count must match basis")
    result = Polynomial([0.0])
    for coefficient, mode in zip(coordinates, basis):
        result = result + float(coefficient) * mode
    return result


def seam_signature(profile: Polynomial) -> dict[str, float]:
    derivative = profile.deriv()
    return {
        "center_value": float(profile(0.0)),
        "center_slope": float(derivative(0.0)),
        "seam_value": float(profile(1.0)),
        "seam_slope": float(derivative(1.0)),
    }


def action_components(
    z: Sequence[float], parameters: EnvelopmentParameters | None = None
) -> dict[str, float]:
    parameters = parameters or EnvelopmentParameters()
    validate_parameters(parameters)
    hessian, _, basis, aux = global_linear_system(parameters)
    vector = np.asarray(z, dtype=float)
    if vector.shape != (hessian.shape[0],):
        raise ValueError("state vector has wrong shape")
    profile_coordinates = vector[:-1]
    x = float(vector[-1])
    gram = aux["gram"]
    budget_vector = aux["budget"]
    source_vector = aux["source"]
    s = float(profile_coordinates[0])
    t = float(profile_coordinates[1])
    budget_mismatch = float(budget_vector @ profile_coordinates - parameters.budget_nesting_coupling * x)
    value_mismatch = s - parameters.seam_value_nesting_coupling * x
    slope_mismatch = t - parameters.seam_slope_nesting_coupling * x

    local = 0.5 * float(profile_coordinates @ gram @ profile_coordinates)
    global_budget = 0.5 * parameters.global_budget_weight * budget_mismatch**2
    seam_value = 0.5 * parameters.seam_value_weight * value_mismatch**2
    seam_slope = 0.5 * parameters.seam_slope_weight * slope_mismatch**2
    nesting = 0.5 * parameters.nesting_weight * (x - parameters.nesting_reference) ** 2
    source = -parameters.source_amplitude * float(source_vector @ profile_coordinates)
    total = local + global_budget + seam_value + seam_slope + nesting + source
    return {
        "local_bulk": local,
        "global_envelopment_budget": global_budget,
        "parent_child_seam_value": seam_value,
        "parent_child_seam_slope": seam_slope,
        "relational_nesting": nesting,
        "source": source,
        "total": total,
    }


def action_value(z: Sequence[float], parameters: EnvelopmentParameters | None = None) -> float:
    return action_components(z, parameters)["total"]


def action_gradient(
    z: Sequence[float], parameters: EnvelopmentParameters | None = None
) -> np.ndarray:
    parameters = parameters or EnvelopmentParameters()
    hessian, rhs, _, _ = global_linear_system(parameters)
    vector = np.asarray(z, dtype=float)
    if vector.shape != rhs.shape:
        raise ValueError("state vector has wrong shape")
    return hessian @ vector - rhs


def strict_convexity_certificate(
    parameters: EnvelopmentParameters | None = None,
) -> dict[str, Any]:
    parameters = parameters or EnvelopmentParameters()
    solution = solve_global_stationary(parameters)
    hessian = solution["hessian"]
    eigenvalues = solution["hessian_eigenvalues"]
    return {
        "version": VERSION,
        "verdict": UNIQUENESS_VERDICT,
        "functional": (
            "1/2 int[(u')^2+mu2 u^2] + gamma/2(int rho u-q x)^2 + "
            "eta_s/2(s-chi_s x)^2 + eta_t/2(t-chi_t x)^2 + "
            "nu/2(x-x_ref)^2 - J int sigma u"
        ),
        "variation_coordinates": [
            "seam_value_s",
            "seam_normal_traction_t",
            "interior_profile_coefficients",
            "x=log(R_child/R_parent)",
        ],
        "quadratic_variation": (
            "int[(delta u')^2+mu2(delta u)^2] + gamma(int rho delta u-q delta x)^2 + "
            "eta_s(delta s-chi_s delta x)^2 + eta_t(delta t-chi_t delta x)^2 + nu(delta x)^2"
        ),
        "strict_convexity_conditions": [
            "mu2>0",
            "gamma>0",
            "eta_s>0",
            "eta_t>0",
            "nu>0",
        ],
        "hessian_dimension": int(hessian.shape[0]),
        "hessian_min_eigenvalue": float(np.min(eigenvalues)),
        "hessian_max_eigenvalue": float(np.max(eigenvalues)),
        "hessian_condition_number": solution["condition_number"],
        "hessian_positive_definite": bool(np.min(eigenvalues) > 0.0),
        "stationarity_residual": solution["stationarity_residual"],
        "unique_stationary_solution_in_reduced_class": True,
        "full_BHSM_global_hessian_proved_positive": False,
        "physical_uniqueness_claimed": False,
    }


def degeneracy_lift_certificate(
    parameters: EnvelopmentParameters | None = None,
) -> dict[str, Any]:
    parameters = parameters or EnvelopmentParameters()
    solution = solve_global_stationary(parameters)
    z_star = solution["solution"].copy()
    basis = solution["basis"]
    if parameters.interior_modes < 1:
        raise ValueError("at least one interior mode required")
    delta = np.zeros_like(z_star)
    # First pure-interior basis coordinate is index 2.  It has zero center and
    # zero seam value/slope, so this deformation is invisible to Cauchy data.
    delta[2] = parameters.degeneracy_probe_amplitude
    z_alt = z_star + delta

    p_star = profile_polynomial(z_star[:-1], basis)
    p_alt = profile_polynomial(z_alt[:-1], basis)
    sig_star = seam_signature(p_star)
    sig_alt = seam_signature(p_alt)
    signature_delta = {
        key: sig_alt[key] - sig_star[key] for key in sorted(sig_star)
    }
    action_star = action_components(z_star, parameters)
    action_alt = action_components(z_alt, parameters)
    exact_quadratic_rise = 0.5 * float(delta @ solution["hessian"] @ delta)
    observed_rise = action_alt["total"] - action_star["total"]

    return {
        "version": VERSION,
        "verdict": DEGENERACY_VERDICT,
        "probe": "add epsilon times the normalized r^2*(1-r)^2 interior mode to the globally stationary cap",
        "probe_amplitude": parameters.degeneracy_probe_amplitude,
        "stationary_signature": sig_star,
        "locally_degenerate_signature": sig_alt,
        "signature_difference": signature_delta,
        "max_abs_signature_difference": max(abs(value) for value in signature_delta.values()),
        "stationary_action_components": action_star,
        "alternative_action_components": action_alt,
        "global_action_rise": observed_rise,
        "quadratic_theorem_rise": exact_quadratic_rise,
        "quadratic_identity_residual": abs(observed_rise - exact_quadratic_rise),
        "stationary_gradient_norm": float(np.linalg.norm(action_gradient(z_star, parameters))),
        "alternative_gradient_norm": float(np.linalg.norm(action_gradient(z_alt, parameters))),
        "same_center_and_seam_Cauchy_data": max(abs(value) for value in signature_delta.values()) < 1e-12,
        "global_action_distinguishes_profiles": observed_rise > 0.0,
        "local_boundary_equivalence_implies_global_variational_equivalence": False,
    }


def seam_output_certificate(
    parameters: EnvelopmentParameters | None = None,
) -> dict[str, Any]:
    parameters = parameters or EnvelopmentParameters()
    solution = solve_global_stationary(parameters)
    profile = profile_polynomial(solution["profile_coordinates"], solution["basis"])
    signature = seam_signature(profile)
    return {
        "version": VERSION,
        "verdict": SEAM_OUTPUT_VERDICT,
        "regular_center_conditions": {
            "u(0)": signature["center_value"],
            "u_prime(0)": signature["center_slope"],
        },
        "derived_seam_outputs": {
            "u(1)": signature["seam_value"],
            "u_prime(1)": signature["seam_slope"],
        },
        "variational_coordinates_match_outputs": {
            "seam_value_coordinate": solution["seam_value"],
            "seam_slope_coordinate": solution["seam_slope"],
        },
        "relational_log_nesting": solution["log_nesting"],
        "diagnostic_nesting_ratio": solution["nesting_ratio"],
        "parent_radius_normalization": "R_parent=1 only for theorem witness",
        "cosmological_R_H_inserted_as_physical_number": False,
        "seam_prescribed_before_global_variation": False,
        "physical_seam_claimed": False,
    }


def _l2_profile_difference(
    coordinates_a: np.ndarray,
    basis_a: Sequence[Polynomial],
    coordinates_b: np.ndarray,
    basis_b: Sequence[Polynomial],
) -> float:
    pa = profile_polynomial(coordinates_a, basis_a)
    pb = profile_polynomial(coordinates_b, basis_b)
    difference = pa - pb
    return math.sqrt(max(0.0, _integral_01(difference * difference)))


def galerkin_convergence_payload(max_modes: int = 8) -> dict[str, Any]:
    if not isinstance(max_modes, int) or max_modes < 4:
        raise ValueError("max_modes must be an integer >=4")
    reference_parameters = EnvelopmentParameters(interior_modes=max_modes)
    reference = solve_global_stationary(reference_parameters)
    rows: list[dict[str, Any]] = []
    for modes in range(1, max_modes + 1):
        parameters = EnvelopmentParameters(interior_modes=modes)
        solution = solve_global_stationary(parameters)
        l2_error = _l2_profile_difference(
            solution["profile_coordinates"],
            solution["basis"],
            reference["profile_coordinates"],
            reference["basis"],
        )
        rows.append(
            {
                "interior_modes": modes,
                "seam_value": solution["seam_value"],
                "seam_slope": solution["seam_slope"],
                "log_nesting": solution["log_nesting"],
                "nesting_ratio": solution["nesting_ratio"],
                "stationarity_residual": solution["stationarity_residual"],
                "min_hessian_eigenvalue": solution["min_hessian_eigenvalue"],
                "l2_profile_error_vs_max_mode_reference": l2_error,
            }
        )
    return {
        "version": VERSION,
        "max_modes": max_modes,
        "rows": rows,
        "last_profile_error": rows[-1]["l2_profile_error_vs_max_mode_reference"],
        "stationary_solution_computable_at_all_resolutions": all(
            row["stationarity_residual"] < 1e-11 for row in rows
        ),
        "positive_reduced_hessian_at_all_resolutions": all(
            row["min_hessian_eigenvalue"] > 0.0 for row in rows
        ),
        "physical_continuum_convergence_claimed": False,
    }


def global_functional_payload(
    parameters: EnvelopmentParameters | None = None,
) -> dict[str, Any]:
    parameters = parameters or EnvelopmentParameters()
    solution = solve_global_stationary(parameters)
    profile = profile_polynomial(solution["profile_coordinates"], solution["basis"])
    payload = {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "parameters": asdict(parameters),
        "parameter_status": "synthetic frozen theorem-witness coefficients; not measured or fitted",
        "state": {
            "seam_value": solution["seam_value"],
            "seam_slope": solution["seam_slope"],
            "interior_coefficients": [float(value) for value in solution["interior_coefficients"]],
            "log_nesting": solution["log_nesting"],
            "diagnostic_nesting_ratio": solution["nesting_ratio"],
        },
        "seam_signature": seam_signature(profile),
        "action_components": action_components(solution["solution"], parameters),
        "stationarity_residual": solution["stationarity_residual"],
        "hessian_min_eigenvalue": solution["min_hessian_eigenvalue"],
        "strictly_convex_reduced_functional": True,
        "seam_is_variational_output": True,
        "nesting_is_variational_output": True,
        "physical_BHSM_coefficients_derived": False,
        "physical_cap_selected": False,
        "physical_prediction_emitted": False,
    }
    return {**payload, "payload_sha256": sha256_payload(payload)}


def physical_readiness_payload() -> dict[str, Any]:
    checks = {
        "global_envelopment_variational_architecture_formulated": True,
        "reduced_global_strict_convexity_theorem": True,
        "local_seam_degeneracy_lifted_in_reduced_class": True,
        "seam_value_and_traction_co_selected": True,
        "relational_nesting_co_selected": True,
        "reduced_resolution_convergence_harness": True,
        "actual_unified_BHSM_coefficients_inserted": False,
        "cosmological_parent_stationary_solution": False,
        "physical_regular_child_cap_stationary_solution": False,
        "complete_gauge_metric_ghost_reduction": False,
        "full_global_physical_hessian_non_degenerate": False,
        "all_competing_global_stationary_caps_excluded": False,
        "three_transverse_moving_seam_channels_action_selected": False,
        "physical_DtN_relative_heat_kernel_bundle": False,
        "zero_retuning_neutrino_kill_screen_executed_physically": False,
        "full_particle_force_and_flavor_completion": False,
    }
    return {
        "version": VERSION,
        "mathematical_global_selection_mechanism_valid": True,
        "physical_global_cap_selection_valid": False,
        "checks": checks,
        "missing_checks": [name for name, value in checks.items() if not value],
        "physical_prediction_emitted": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "v14_59_conceptual_roadblock": "LIFTED_IN_REDUCED_GLOBAL_VARIATIONAL_CLASS",
        "v14_59_physical_cap_roadblock": "OPEN_UNTIL_FULL_ACTION_GLOBAL_HESSIAN_IS_DERIVED",
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> Mapping[str, dict[str, Any]]:
    return {
        "BHSM_global_envelopment_functional_v14_60.json": global_functional_payload(),
        "BHSM_global_hessian_uniqueness_certificate_v14_60.json": strict_convexity_certificate(),
        "BHSM_local_seam_degeneracy_lift_v14_60.json": degeneracy_lift_certificate(),
        "BHSM_global_seam_output_certificate_v14_60.json": seam_output_certificate(),
        "BHSM_global_galerkin_convergence_v14_60.json": galerkin_convergence_payload(),
        "BHSM_physical_completion_readiness_v14_60.json": physical_readiness_payload(),
        "BHSM_completion_gate_v14_60.json": completion_gate_payload(),
    }


def materialize(output_directory: str | Path) -> list[Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        path = output / name
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written
