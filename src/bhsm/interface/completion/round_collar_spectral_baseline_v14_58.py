"""BHSM v14.58 exact round-collar spectral baseline.

This module replaces arbitrary finite DtN matrices with an exactly specified
reduced product-collar operator on a round S3 seam.  It proves a trace-class
seam DtN contrast for that reduced model, identifies the cap-domain sign fork,
and proves that round homogeneous response cannot generate noncentral flavor
mixing.

It is not the physical BHSM cosmological-parent/particle-child operator.  No
physical neutrino mass, splitting, PMNS matrix, coupling, scale, lifetime, or
cross section is emitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

VERSION = "v14.58"

PRIMARY_VERDICT = (
    "BHSM_V14_58_THE_ROUND_PRODUCT_COLLAR_REPLACES_SYNTHETIC_DTN_MATRICES_"
    "WITH_EXACT_SPECTRAL_FORMULAS_AND_PROVES_A_TRACE_CLASS_SEAM_CONTRAST_"
    "BUT_THE_CONTRAST_SIGN_DEPENDS_ON_THE_UNDERIVED_INNER_CAP_DOMAIN_AND_"
    "ROUND_SYMMETRY_FORBIDS_NONCENTRAL_FLAVOR_MIXING"
)
TRACE_CLASS_VERDICT = (
    "BHSM_THE_DIRAC_LAPLACE_DTN_DIFFERENCE_BETWEEN_A_FINITE_ROUND_PRODUCT_"
    "COLLAR_AND_A_DECAYING_HALF_CYLINDER_IS_TRACE_CLASS_ON_THE_COMMON_S3_"
    "SEAM_BECAUSE_ITS_MODE_EIGENVALUES_DECAY_EXPONENTIALLY"
)
DOMAIN_FORK_VERDICT = (
    "BHSM_DIRICHLET_AND_NEUMANN_INNER_CAP_DOMAINS_GIVE_OPPOSITE_DTN_"
    "CONTRAST_SIGNS_SO_THE_PHYSICAL_CAP_DOMAIN_MUST_BE_DERIVED_FROM_THE_"
    "ACTION_AND_REGULARITY_NOT_SELECTED_FOR_PHENOMENOLOGY"
)
SYMMETRY_VERDICT = (
    "BHSM_A_ROUND_HOMOGENEOUS_DTN_OPERATOR_IS_SCALAR_ON_EACH_IRREDUCIBLE_"
    "HARMONIC_BLOCK_AND_CANNOT_GENERATE_THE_NONCENTRAL_THREE_CHANNEL_WAKE_"
    "REQUIRED_FOR_FLAVOR_MIXING_OR_CP"
)
EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_BERGER_ANISOTROPIC_MOVING_SEAM_DIRAC_LAPLACE_OPERATOR_"
    "WITH_A_REGULAR_CORE_CAP_DOMAIN_COMPLETE_GAUGE_ZERO_MODE_PROJECTOR_"
    "AND_OFF_DIAGONAL_SHAPE_DERIVATIVES_INSERTED_INTO_THE_NO_RETUNING_"
    "NEUTRINO_KILL_SCREEN"
)


@dataclass(frozen=True)
class RoundCollarParameters:
    radius: float = 1.0
    collar_length: float = 0.8
    mass: float = 0.2
    n_max: int = 64


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


def validate_parameters(parameters: RoundCollarParameters) -> None:
    if not math.isfinite(parameters.radius) or parameters.radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(parameters.collar_length) or parameters.collar_length <= 0.0:
        raise ValueError("positive finite collar_length required")
    if not math.isfinite(parameters.mass) or parameters.mass < 0.0:
        raise ValueError("finite nonnegative mass required")
    if not isinstance(parameters.n_max, int) or parameters.n_max < 0:
        raise ValueError("nonnegative integer n_max required")


def round_s3_dirac_laplace_mode(n: int, radius: float, mass: float = 0.0) -> dict[str, Any]:
    if not isinstance(n, int) or n < 0:
        raise ValueError("nonnegative integer mode required")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(mass) or mass < 0.0:
        raise ValueError("finite nonnegative mass required")
    dirac_magnitude = (n + 1.5) / radius
    eigenvalue = dirac_magnitude * dirac_magnitude + mass * mass
    multiplicity = 2 * (n + 1) * (n + 2)
    return {
        "n": n,
        "dirac_eigenvalues": [-dirac_magnitude, dirac_magnitude],
        "dirac_laplace_eigenvalue": eigenvalue,
        "multiplicity": multiplicity,
    }


def round_s3_scalar_laplace_mode(n: int, radius: float, mass: float = 0.0) -> dict[str, Any]:
    if not isinstance(n, int) or n < 0:
        raise ValueError("nonnegative integer mode required")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(mass) or mass < 0.0:
        raise ValueError("finite nonnegative mass required")
    eigenvalue = n * (n + 2) / (radius * radius) + mass * mass
    return {"n": n, "eigenvalue": eigenvalue, "multiplicity": (n + 1) ** 2}


def mode_kappa(n: int, radius: float, mass: float = 0.0) -> float:
    return math.sqrt(round_s3_dirac_laplace_mode(n, radius, mass)["dirac_laplace_eigenvalue"])


def parent_half_cylinder_dtn(kappa: float) -> float:
    if not math.isfinite(kappa) or kappa <= 0.0:
        raise ValueError("positive finite kappa required")
    return kappa


def child_finite_collar_dtn(kappa: float, collar_length: float, inner_domain: str) -> float:
    if not math.isfinite(kappa) or kappa <= 0.0:
        raise ValueError("positive finite kappa required")
    if not math.isfinite(collar_length) or collar_length <= 0.0:
        raise ValueError("positive finite collar length required")
    x = kappa * collar_length
    if inner_domain == "dirichlet":
        return kappa / math.tanh(x)
    if inner_domain == "neumann":
        return kappa * math.tanh(x)
    raise ValueError("inner_domain must be dirichlet or neumann")


def dtn_contrast(kappa: float, collar_length: float, inner_domain: str) -> float:
    return child_finite_collar_dtn(kappa, collar_length, inner_domain) - parent_half_cylinder_dtn(kappa)


def stable_dirichlet_contrast(kappa: float, collar_length: float) -> float:
    """Return kappa(coth(kappa L)-1) without catastrophic cancellation."""
    if not math.isfinite(kappa) or kappa <= 0.0:
        raise ValueError("positive finite kappa required")
    if not math.isfinite(collar_length) or collar_length <= 0.0:
        raise ValueError("positive finite collar length required")
    return 2.0 * kappa / math.expm1(2.0 * kappa * collar_length)


def stable_neumann_contrast(kappa: float, collar_length: float) -> float:
    """Return kappa(tanh(kappa L)-1) stably."""
    if not math.isfinite(kappa) or kappa <= 0.0:
        raise ValueError("positive finite kappa required")
    if not math.isfinite(collar_length) or collar_length <= 0.0:
        raise ValueError("positive finite collar length required")
    exponential = math.exp(-2.0 * kappa * collar_length)
    return -2.0 * kappa * exponential / (1.0 + exponential)


def weighted_dirichlet_contrast_term(n: int, parameters: RoundCollarParameters) -> float:
    validate_parameters(parameters)
    mode = round_s3_dirac_laplace_mode(n, parameters.radius, parameters.mass)
    kappa = math.sqrt(mode["dirac_laplace_eigenvalue"])
    return float(mode["multiplicity"] * stable_dirichlet_contrast(kappa, parameters.collar_length))


def _tail_moments(start: int, q: float) -> tuple[float, float, float, float]:
    if start < 0 or not isinstance(start, int):
        raise ValueError("nonnegative integer start required")
    if not (0.0 < q < 1.0):
        raise ValueError("q must lie strictly between zero and one")
    one_minus = 1.0 - q
    k0 = 1.0 / one_minus
    k1 = q / (one_minus * one_minus)
    k2 = q * (1.0 + q) / (one_minus ** 3)
    k3 = q * (1.0 + 4.0 * q + q * q) / (one_minus ** 4)
    factor = q ** start
    s0 = factor * k0
    s1 = factor * (start * k0 + k1)
    s2 = factor * (start * start * k0 + 2.0 * start * k1 + k2)
    s3 = factor * (start ** 3 * k0 + 3.0 * start * start * k1 + 3.0 * start * k2 + k3)
    return s0, s1, s2, s3


def dirichlet_trace_tail_upper_bound(start: int, parameters: RoundCollarParameters) -> float:
    """Conservative tail bound for sum_{n>=start} multiplicity*Delta N_n."""
    validate_parameters(parameters)
    if not isinstance(start, int) or start < 0:
        raise ValueError("nonnegative integer start required")
    radius = parameters.radius
    length = parameters.collar_length
    q = math.exp(-2.0 * length / radius)
    c = 1.5 + parameters.mass * radius
    s0, s1, s2, s3 = _tail_moments(start, q)
    # (n+1)(n+2)(n+c) = n^3 + (c+3)n^2 + (3c+2)n + 2c.
    polynomial_tail = s3 + (c + 3.0) * s2 + (3.0 * c + 2.0) * s1 + 2.0 * c * s0
    denominator = 1.0 - math.exp(-3.0 * length / radius)
    prefactor = 4.0 * (q ** 1.5) / (radius * denominator)
    return float(prefactor * polynomial_tail)


def dirichlet_trace_certificate(parameters: RoundCollarParameters) -> dict[str, Any]:
    validate_parameters(parameters)
    partial = sum(weighted_dirichlet_contrast_term(n, parameters) for n in range(parameters.n_max + 1))
    tail_bound = dirichlet_trace_tail_upper_bound(parameters.n_max + 1, parameters)
    return {
        "partial_trace_through_n_max": partial,
        "tail_upper_bound": tail_bound,
        "certified_interval": [partial, partial + tail_bound],
        "n_max": parameters.n_max,
        "trace_class_proved_for_reduced_seam_operator": True,
        "proof_mechanism": "polynomial degeneracy times exponential DtN contrast decay",
    }


def dtn_contrast_matrix(kappa: float, collar_length: float, inner_domain: str, block_dimension: int = 3) -> np.ndarray:
    if not isinstance(block_dimension, int) or block_dimension <= 0:
        raise ValueError("positive integer block_dimension required")
    value = dtn_contrast(kappa, collar_length, inner_domain)
    return value * np.eye(block_dimension, dtype=np.complex128)


def commutator_norm(a: np.ndarray, b: np.ndarray) -> float:
    left = np.asarray(a, dtype=np.complex128)
    right = np.asarray(b, dtype=np.complex128)
    return float(np.linalg.norm(left @ right - right @ left, ord="fro"))


def off_diagonal_norm(matrix: np.ndarray) -> float:
    array = np.asarray(matrix, dtype=np.complex128)
    return float(np.linalg.norm(array - np.diag(np.diag(array)), ord="fro"))


def round_symmetry_obstruction_payload(parameters: RoundCollarParameters | None = None) -> dict[str, Any]:
    parameters = parameters or RoundCollarParameters()
    validate_parameters(parameters)
    kappa = mode_kappa(0, parameters.radius, parameters.mass)
    response = dtn_contrast_matrix(kappa, parameters.collar_length, "dirichlet", 3)
    omega = np.exp(2j * np.pi / 3.0)
    fourier = np.array(
        [[1.0, 1.0, 1.0], [1.0, omega, omega ** 2], [1.0, omega ** 2, omega]],
        dtype=np.complex128,
    ) / math.sqrt(3.0)
    oriented = np.array(
        [[0.0, 1.0j, 0.2], [-1.0j, 0.0, 0.4j], [0.2, -0.4j, 0.0]],
        dtype=np.complex128,
    )
    return {
        "verdict": SYMMETRY_VERDICT,
        "homogeneous_block_response": response.real.tolist(),
        "commutator_with_fourier_basis_norm": commutator_norm(response, fourier),
        "commutator_with_oriented_shape_generator_norm": commutator_norm(response, oriented),
        "off_diagonal_norm": off_diagonal_norm(response),
        "noncentral_wake_generated": False,
        "reason": "round homogeneous response is scalar on each irreducible block by symmetry",
    }


def scale_covariance_payload(parameters: RoundCollarParameters | None = None, scale: float = 3.25) -> dict[str, Any]:
    parameters = parameters or RoundCollarParameters()
    validate_parameters(parameters)
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("positive finite scale required")
    n = 3
    original_kappa = mode_kappa(n, parameters.radius, parameters.mass)
    original = stable_dirichlet_contrast(original_kappa, parameters.collar_length)
    scaled = RoundCollarParameters(
        radius=scale * parameters.radius,
        collar_length=scale * parameters.collar_length,
        mass=parameters.mass / scale,
        n_max=parameters.n_max,
    )
    scaled_kappa = mode_kappa(n, scaled.radius, scaled.mass)
    scaled_value = stable_dirichlet_contrast(scaled_kappa, scaled.collar_length)
    return {
        "scale_factor": scale,
        "original_contrast": original,
        "scaled_contrast": scaled_value,
        "expected_scaled_contrast": original / scale,
        "absolute_residual": abs(scaled_value - original / scale),
        "dimensionless_shape_data_unchanged": True,
        "absolute_scale_selected": False,
    }


def background_operator_contract_payload(parameters: RoundCollarParameters | None = None) -> dict[str, Any]:
    parameters = parameters or RoundCollarParameters()
    validate_parameters(parameters)
    payload = {
        "version": VERSION,
        "mode": "analytic_reduced_not_physical",
        "seam": "round S3(radius)",
        "parent_domain": "decaying half-cylinder [0,infinity) x S3",
        "child_domain": "finite product collar [-L,0] x S3",
        "quadratic_operator": "-partial_r^2 + Dirac_S3^2 + mass^2",
        "parent_seam_metric_matches_child": True,
        "parent_dtn_mode": "kappa",
        "child_dtn_dirichlet_mode": "kappa*coth(kappa*L)",
        "child_dtn_neumann_mode": "kappa*tanh(kappa*L)",
        "parameters": asdict(parameters),
        "physical_derivation_claimed": False,
        "inner_cap_domain_action_selected": False,
        "cosmological_parent_solution_supplied": False,
        "moving_seam_supplied": False,
        "gauge_bundle_supplied": False,
    }
    return {**payload, "payload_sha256": sha256_payload(payload)}


def exact_spectrum_payload(parameters: RoundCollarParameters | None = None, listed_modes: int = 12) -> dict[str, Any]:
    parameters = parameters or RoundCollarParameters()
    validate_parameters(parameters)
    if not isinstance(listed_modes, int) or listed_modes <= 0:
        raise ValueError("positive integer listed_modes required")
    modes = [round_s3_dirac_laplace_mode(n, parameters.radius, parameters.mass) for n in range(listed_modes)]
    return {
        "version": VERSION,
        "operator": "Dirac_S3^2 + mass^2",
        "formula": "lambda_n=(n+3/2)^2/R^2+m^2; multiplicity=2(n+1)(n+2)",
        "modes": modes,
        "spinor_zero_modes_present": False,
        "lowest_gap": modes[0]["dirac_laplace_eigenvalue"],
        "physical_Berger_spectrum": False,
    }


def trace_class_payload(parameters: RoundCollarParameters | None = None) -> dict[str, Any]:
    parameters = parameters or RoundCollarParameters()
    validate_parameters(parameters)
    certificate = dirichlet_trace_certificate(parameters)
    first_terms = []
    for n in range(8):
        kappa = mode_kappa(n, parameters.radius, parameters.mass)
        first_terms.append(
            {
                "n": n,
                "kappa": kappa,
                "multiplicity": round_s3_dirac_laplace_mode(n, parameters.radius, parameters.mass)["multiplicity"],
                "dirichlet_contrast": stable_dirichlet_contrast(kappa, parameters.collar_length),
                "neumann_contrast": stable_neumann_contrast(kappa, parameters.collar_length),
            }
        )
    return {
        "version": VERSION,
        "verdict": TRACE_CLASS_VERDICT,
        "domain_fork_verdict": DOMAIN_FORK_VERDICT,
        "parameters": asdict(parameters),
        "certificate": certificate,
        "first_modes": first_terms,
        "full_bulk_relative_heat_kernel_trace_class_proved": False,
        "continuum_shape_derivative_of_relative_determinant_derived": False,
    }


def physical_readiness_payload() -> dict[str, Any]:
    checks = {
        "exact_round_product_spectrum": True,
        "matched_common_round_seam": True,
        "hermitian_reduced_dtn_maps": True,
        "reduced_seam_dtn_difference_trace_class": True,
        "inner_cap_domain_action_selected": False,
        "cosmological_parent_background_solved": False,
        "particle_child_background_solved": False,
        "berger_anisotropic_dirac_spectrum": False,
        "moving_seam_shape_derivatives": False,
        "complete_gauge_zero_mode_projector": False,
        "full_bulk_relative_heat_kernel_control": False,
        "noncentral_three_channel_wake": False,
        "absolute_scale_selected": False,
        "no_retuning_physical_target_execution": False,
    }
    return {
        "version": VERSION,
        "reduced_analytic_baseline_valid": True,
        "physical_operator_bundle_valid": False,
        "checks": checks,
        "missing_checks": [name for name, value in checks.items() if not value],
        "physical_prediction_emitted": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_neutrino_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> Mapping[str, dict[str, Any]]:
    parameters = RoundCollarParameters()
    return {
        "BHSM_round_collar_background_operator_contract_v14_58.json": background_operator_contract_payload(parameters),
        "BHSM_round_S3_dirac_laplace_spectrum_v14_58.json": exact_spectrum_payload(parameters),
        "BHSM_round_collar_dtn_trace_class_certificate_v14_58.json": trace_class_payload(parameters),
        "BHSM_round_symmetry_flavor_obstruction_v14_58.json": round_symmetry_obstruction_payload(parameters),
        "BHSM_round_collar_scale_covariance_v14_58.json": scale_covariance_payload(parameters),
        "BHSM_physical_operator_readiness_v14_58.json": physical_readiness_payload(),
        "BHSM_completion_gate_v14_58.json": completion_gate_payload(),
    }


def materialize(output_directory: str | Path) -> list[Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, payload in sorted(artifact_payloads().items()):
        path = output / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        written.append(path)
    return written
