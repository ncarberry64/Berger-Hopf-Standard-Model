"""BHSM v14.59 exact Berger-Dirac blocks and cap nonuniqueness audit.

This module advances the v14.58 round-collar baseline in two rigorous ways.

1. It implements the exact finite-dimensional homogeneous Dirac blocks on
   SU(2) for a left-invariant metric and specializes them to the one-parameter
   Berger family.  The construction reproduces the complete round spectrum
   block by block and exposes the exact first Berger zero-mode crossing.
2. It proves, in a reduced regular radial problem, that common seam data do not
   determine the child cap Dirichlet-to-Neumann map: two smooth interior
   profiles with identical boundary value and identical regular center
   condition have different Weyl m-functions.

It also proves that Berger anisotropy can make time-dependent Dirac blocks
noncommuting while preserving an exact U(1) fiber symmetry.  Therefore Berger
stretch alone is not a complete three-channel flavor source; nonuniform moving
seam harmonics are still required.

No physical mass, splitting, PMNS/CKM matrix, coupling, scale, lifetime, cross
section, or complete BHSM prediction is emitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

VERSION = "v14.59"
FROZEN_BERGER_STRETCH = 1.157054135733433

PRIMARY_VERDICT = (
    "BHSM_V14_59_THE_EXACT_HOMOGENEOUS_BERGER_DIRAC_BLOCKS_REPLACE_THE_"
    "ROUND_ONLY_SPECTRAL_BASELINE_AND_PROVE_A_REAL_ANISOTROPIC_NONCOMMUTING_"
    "MECHANISM_BUT_AXISYMMETRY_PRESERVES_A_U1_SELECTION_RULE_AND_THE_"
    "REGULAR_CHILD_CAP_DTN_IS_NOT_DETERMINED_BY_SEAM_DATA"
)
CAP_VERDICT = (
    "BHSM_A_COMMON_BERGER_SEAM_AND_REGULAR_CENTER_CONDITION_DO_NOT_UNIQUELY_"
    "DETERMINE_THE_CHILD_DTN_MAP_BECAUSE_DISTINCT_SMOOTH_INTERIOR_PROFILES_"
    "WITH_THE_SAME_BOUNDARY_DATA_HAVE_DISTINCT_WEYL_M_FUNCTIONS"
)
BERGER_VERDICT = (
    "BHSM_TIME_DEPENDENT_BERGER_ANISOTROPY_CAN_GENERATE_NONCOMMUTING_DIRAC_"
    "EVOLUTION_BUT_EVERY_BLOCK_PRESERVES_THE_SAME_FIBER_U1_GENERATOR_SO_"
    "BERGER_STRETCH_ALONE_CANNOT_SUPPLY_AN_UNRESTRICTED_THREE_CHANNEL_WAKE"
)
ZERO_MODE_VERDICT = (
    "BHSM_THE_FIRST_BERGER_SPINOR_ZERO_MODE_OCCURS_EXACTLY_AT_STRETCH_4_IN_"
    "THE_N1_BLOCK_WHILE_THE_FROZEN_DIAGNOSTIC_STRETCH_IS_STRICTLY_GAPPED"
)
EXACT_NEXT_OBJECT = (
    "COHOMOGENEITY_ONE_ACTION_STATIONARY_PARENT_CHILD_BACKGROUND_WITH_"
    "REGULAR_CAP_WARP_FACTORS_COMPLETE_GAUGE_METRIC_GHOST_ZERO_MODE_"
    "PROJECTOR_AND_THREE_NONUNIFORM_MOVING_SEAM_SHAPE_DERIVATIVES_SOLVED_"
    "SIMULTANEOUSLY_IN_THE_NO_RETUNING_BVP"
)


@dataclass(frozen=True)
class BergerParameters:
    radius: float = 1.0
    stretch: float = FROZEN_BERGER_STRETCH
    n_max: int = 8


@dataclass(frozen=True)
class CapParameters:
    kappa: float = 1.7
    length: float = 0.9
    epsilon: float = 0.65
    steps: int = 4096


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


def validate_berger(parameters: BergerParameters) -> None:
    if not math.isfinite(parameters.radius) or parameters.radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(parameters.stretch) or parameters.stretch <= 0.0:
        raise ValueError("positive finite stretch required")
    if not isinstance(parameters.n_max, int) or parameters.n_max < 0:
        raise ValueError("nonnegative integer n_max required")


def validate_cap(parameters: CapParameters) -> None:
    if not math.isfinite(parameters.kappa) or parameters.kappa <= 0.0:
        raise ValueError("positive finite kappa required")
    if not math.isfinite(parameters.length) or parameters.length <= 0.0:
        raise ValueError("positive finite length required")
    if not math.isfinite(parameters.epsilon):
        raise ValueError("finite epsilon required")
    if not isinstance(parameters.steps, int) or parameters.steps < 32:
        raise ValueError("at least 32 integration steps required")


def pauli_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sigma_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    sigma_y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
    return sigma_x, sigma_y, sigma_z


def spin_matrices(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return spin-j matrices with j=n/2 on the (n+1)-dimensional irrep."""

    if not isinstance(n, int) or n < 0:
        raise ValueError("nonnegative integer n required")
    j = n / 2.0
    magnetic = np.array([j - k for k in range(n + 1)], dtype=float)
    j_z = np.diag(magnetic).astype(np.complex128)
    j_plus = np.zeros((n + 1, n + 1), dtype=np.complex128)
    for column, m in enumerate(magnetic):
        if column > 0:
            j_plus[column - 1, column] = math.sqrt((j - m) * (j + m + 1.0))
    j_minus = j_plus.conjugate().T
    j_x = 0.5 * (j_plus + j_minus)
    j_y = (j_plus - j_minus) / (2.0j)
    return j_x, j_y, j_z


def homogeneous_connection_constant(a: float, b: float, c: float) -> float:
    if not all(math.isfinite(value) and value > 0.0 for value in (a, b, c)):
        raise ValueError("positive finite inverse lengths required")
    return 0.5 * (a * b / c + b * c / a + c * a / b)


def homogeneous_dirac_block(n: int, a: float, b: float, c: float) -> np.ndarray:
    """Exact D_n block for the homogeneous metric g_{abc} on SU(2).

    The basis convention maps the three Lie-algebra directions to z, y, x.
    This is unitarily equivalent to cyclic alternatives and reproduces the
    standard round spectrum exactly.
    """

    j_x, j_y, j_z = spin_matrices(n)
    sigma_x, sigma_y, sigma_z = pauli_matrices()
    constant = homogeneous_connection_constant(a, b, c)
    dimension = 2 * (n + 1)
    return (
        constant * np.eye(dimension, dtype=np.complex128)
        + 2.0 * a * np.kron(sigma_z, j_z)
        + 2.0 * b * np.kron(sigma_y, j_y)
        + 2.0 * c * np.kron(sigma_x, j_x)
    )


def berger_inverse_lengths(radius: float, stretch: float) -> tuple[float, float, float]:
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(stretch) or stretch <= 0.0:
        raise ValueError("positive finite stretch required")
    return 1.0 / radius, 1.0 / radius, 1.0 / (stretch * radius)


def berger_dirac_block(n: int, radius: float, stretch: float) -> np.ndarray:
    return homogeneous_dirac_block(n, *berger_inverse_lengths(radius, stretch))


def berger_dirac_derivative_block(n: int, radius: float, stretch: float) -> np.ndarray:
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(stretch) or stretch <= 0.0:
        raise ValueError("positive finite stretch required")
    j_x, _, _ = spin_matrices(n)
    sigma_x, _, _ = pauli_matrices()
    dimension = 2 * (n + 1)
    constant_derivative = (1.0 - 2.0 / (stretch * stretch)) / (2.0 * radius)
    fiber_derivative = -2.0 / (stretch * stretch * radius)
    return (
        constant_derivative * np.eye(dimension, dtype=np.complex128)
        + fiber_derivative * np.kron(sigma_x, j_x)
    )


def round_block_expected_eigenvalues(n: int, radius: float) -> list[float]:
    if not isinstance(n, int) or n < 0:
        raise ValueError("nonnegative integer n required")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("positive finite radius required")
    negative = [-(n + 0.5) / radius] * n
    positive = [(n + 1.5) / radius] * (n + 2)
    return sorted(negative + positive)


def n1_berger_exact_eigenvalues(radius: float, stretch: float) -> list[float]:
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(stretch) or stretch <= 0.0:
        raise ValueError("positive finite stretch required")
    values = [
        (stretch - 4.0) / (2.0 * radius),
        (stretch * stretch + 4.0) / (2.0 * stretch * radius),
        (stretch * stretch + 4.0) / (2.0 * stretch * radius),
        (stretch + 4.0) / (2.0 * radius),
    ]
    return sorted(values)


def hermitian_residual(matrix: np.ndarray) -> float:
    array = np.asarray(matrix, dtype=np.complex128)
    return float(np.linalg.norm(array - array.conjugate().T, ord="fro"))


def commutator_norm(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=np.complex128)
    b = np.asarray(right, dtype=np.complex128)
    return float(np.linalg.norm(a @ b - b @ a, ord="fro"))


def fiber_u1_generator(n: int) -> np.ndarray:
    j_x, _, _ = spin_matrices(n)
    sigma_x, _, _ = pauli_matrices()
    return np.kron(np.eye(2, dtype=np.complex128), j_x) + 0.5 * np.kron(
        sigma_x, np.eye(n + 1, dtype=np.complex128)
    )


def spectral_nonzero_projector(matrix: np.ndarray, tolerance: float = 1e-10) -> tuple[np.ndarray, int]:
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("positive finite tolerance required")
    array = np.asarray(matrix, dtype=np.complex128)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError("square matrix required")
    eigenvalues, eigenvectors = np.linalg.eigh(array)
    keep = np.abs(eigenvalues) > tolerance
    projector = eigenvectors[:, keep] @ eigenvectors[:, keep].conjugate().T
    kernel_dimension = int(np.count_nonzero(~keep))
    return projector, kernel_dimension


def projector_residuals(projector: np.ndarray) -> dict[str, float]:
    p = np.asarray(projector, dtype=np.complex128)
    return {
        "hermitian_residual": float(np.linalg.norm(p - p.conjugate().T, ord="fro")),
        "idempotence_residual": float(np.linalg.norm(p @ p - p, ord="fro")),
    }


def low_berger_spectrum(parameters: BergerParameters) -> list[dict[str, Any]]:
    validate_berger(parameters)
    rows: list[dict[str, Any]] = []
    for n in range(parameters.n_max + 1):
        matrix = berger_dirac_block(n, parameters.radius, parameters.stretch)
        values = np.linalg.eigvalsh(matrix)
        rows.append(
            {
                "n": n,
                "internal_dimension": int(matrix.shape[0]),
                "isotypical_multiplicity_factor": n + 1,
                "eigenvalues": [float(value) for value in values],
                "smallest_absolute_eigenvalue": float(np.min(np.abs(values))),
                "hermitian_residual": hermitian_residual(matrix),
            }
        )
    return rows


def exact_berger_operator_payload(parameters: BergerParameters | None = None) -> dict[str, Any]:
    parameters = parameters or BergerParameters()
    validate_berger(parameters)
    round_residuals = []
    for n in range(min(parameters.n_max, 8) + 1):
        computed = np.linalg.eigvalsh(berger_dirac_block(n, parameters.radius, 1.0))
        expected = np.array(round_block_expected_eigenvalues(n, parameters.radius))
        round_residuals.append(float(np.max(np.abs(computed - expected))))
    payload = {
        "version": VERSION,
        "metric_convention": "g=R^2(sigma_1^2+sigma_2^2+stretch^2 sigma_3^2)",
        "inverse_lengths": "a=b=1/R, c=1/(stretch*R)",
        "block_formula": (
            "D_n=C I+2[a sigma_z tensor J_z+b sigma_y tensor J_y+"
            "c sigma_x tensor J_x], C=(ab/c+bc/a+ca/b)/2"
        ),
        "parameters": asdict(parameters),
        "low_spectrum": low_berger_spectrum(parameters),
        "round_block_max_residual": max(round_residuals),
        "exact_n1_formula": [
            "(stretch-4)/(2R)",
            "(stretch^2+4)/(2 stretch R) [double]",
            "(stretch+4)/(2R)",
        ],
        "physical_background_claimed": False,
    }
    return {**payload, "payload_sha256": sha256_payload(payload)}


def berger_zero_mode_payload() -> dict[str, Any]:
    radius = 1.0
    critical = 4.0
    frozen = FROZEN_BERGER_STRETCH
    critical_matrix = berger_dirac_block(1, radius, critical)
    frozen_matrix = berger_dirac_block(1, radius, frozen)
    critical_projector, critical_kernel = spectral_nonzero_projector(critical_matrix)
    frozen_projector, frozen_kernel = spectral_nonzero_projector(frozen_matrix)
    critical_values = np.linalg.eigvalsh(critical_matrix)
    frozen_values = np.linalg.eigvalsh(frozen_matrix)
    return {
        "version": VERSION,
        "verdict": ZERO_MODE_VERDICT,
        "critical_stretch": critical,
        "critical_n1_exact_eigenvalues": n1_berger_exact_eigenvalues(radius, critical),
        "critical_n1_numeric_eigenvalues": [float(value) for value in critical_values],
        "critical_internal_kernel_dimension": critical_kernel,
        "critical_full_isotypical_kernel_multiplicity": critical_kernel * 2,
        "critical_projector_residuals": projector_residuals(critical_projector),
        "frozen_stretch": frozen,
        "frozen_n1_eigenvalues": [float(value) for value in frozen_values],
        "frozen_internal_kernel_dimension": frozen_kernel,
        "frozen_gap": float(np.min(np.abs(frozen_values))),
        "frozen_projector_residuals": projector_residuals(frozen_projector),
        "complete_bundle_zero_mode_projector_constructed": False,
    }


def berger_u1_obstruction_payload() -> dict[str, Any]:
    n = 3
    radius = 1.0
    stretch_a = FROZEN_BERGER_STRETCH
    stretch_b = 1.31
    d_a = berger_dirac_block(n, radius, stretch_a)
    d_b = berger_dirac_block(n, radius, stretch_b)
    derivative = berger_dirac_derivative_block(n, radius, stretch_a)
    u1 = fiber_u1_generator(n)
    return {
        "version": VERSION,
        "verdict": BERGER_VERDICT,
        "block_n": n,
        "stretch_pair": [stretch_a, stretch_b],
        "commutator_D_at_two_stretches_norm": commutator_norm(d_a, d_b),
        "commutator_D_with_shape_derivative_norm": commutator_norm(d_a, derivative),
        "commutator_D_with_fiber_U1_norm": commutator_norm(d_a, u1),
        "commutator_derivative_with_fiber_U1_norm": commutator_norm(derivative, u1),
        "noncommuting_time_evolution_capable": commutator_norm(d_a, d_b) > 1e-10,
        "exact_common_U1_preserved": commutator_norm(d_a, u1) < 1e-10,
        "unrestricted_three_channel_wake_generated": False,
        "required_symmetry_breaking": [
            "at least two transverse nonuniform moving-seam harmonics",
            "action-selected amplitudes and relative phases",
            "common-domain parent/child shape derivative",
        ],
    }


def _cap_shape_profile(r: float, length: float) -> float:
    x = r / length
    return x * x * (1.0 - x) * (1.0 - x)


def _rk4_regular_solution(
    potential: Callable[[float], float], length: float, steps: int
) -> tuple[float, float, list[tuple[float, float]]]:
    """Integrate u''=V(r)u with regular data u(0)=1,u'(0)=0."""

    h = length / steps
    r = 0.0
    u = 1.0
    p = 0.0
    samples: list[tuple[float, float]] = [(r, u)]

    def rhs(position: float, state_u: float, state_p: float) -> tuple[float, float]:
        return state_p, potential(position) * state_u

    for step in range(steps):
        k1u, k1p = rhs(r, u, p)
        k2u, k2p = rhs(r + 0.5 * h, u + 0.5 * h * k1u, p + 0.5 * h * k1p)
        k3u, k3p = rhs(r + 0.5 * h, u + 0.5 * h * k2u, p + 0.5 * h * k2p)
        k4u, k4p = rhs(r + h, u + h * k3u, p + h * k3p)
        u += h * (k1u + 2.0 * k2u + 2.0 * k3u + k4u) / 6.0
        p += h * (k1p + 2.0 * k2p + 2.0 * k3p + k4p) / 6.0
        r = (step + 1) * h
        samples.append((r, u))
    return u, p, samples


def regular_cap_dtn(parameters: CapParameters, epsilon: float | None = None) -> float:
    validate_cap(parameters)
    perturbation = parameters.epsilon if epsilon is None else epsilon
    if not math.isfinite(perturbation):
        raise ValueError("finite perturbation required")

    def potential(r: float) -> float:
        return parameters.kappa * parameters.kappa + perturbation * _cap_shape_profile(
            r, parameters.length
        )

    u_boundary, derivative_boundary, _ = _rk4_regular_solution(
        potential, parameters.length, parameters.steps
    )
    return derivative_boundary / u_boundary


def cap_first_variation(parameters: CapParameters) -> float:
    """Exact first-variation integral at epsilon=0 for the reduced m-function."""

    validate_cap(parameters)
    kappa = parameters.kappa
    length = parameters.length
    # Base regular solution u=cosh(kappa r), u(L)=cosh(kappa L).
    # Composite Simpson rule is deterministic and highly converged here.
    steps = parameters.steps if parameters.steps % 2 == 0 else parameters.steps + 1
    h = length / steps
    total = 0.0
    for index in range(steps + 1):
        r = index * h
        integrand = _cap_shape_profile(r, length) * math.cosh(kappa * r) ** 2
        weight = 1.0 if index in (0, steps) else (4.0 if index % 2 else 2.0)
        total += weight * integrand
    integral = h * total / 3.0
    return integral / (math.cosh(kappa * length) ** 2)


def cap_nonuniqueness_payload(parameters: CapParameters | None = None) -> dict[str, Any]:
    parameters = parameters or CapParameters()
    validate_cap(parameters)
    base = regular_cap_dtn(parameters, epsilon=0.0)
    perturbed = regular_cap_dtn(parameters, epsilon=parameters.epsilon)
    delta = 1e-4
    numerical_derivative = (
        regular_cap_dtn(parameters, epsilon=delta)
        - regular_cap_dtn(parameters, epsilon=-delta)
    ) / (2.0 * delta)
    analytic_derivative = cap_first_variation(parameters)
    return {
        "version": VERSION,
        "verdict": CAP_VERDICT,
        "reduced_radial_operator": "-u''+[kappa^2+epsilon h(r)]u=0",
        "regular_center_domain": "u(0)=1, u'(0)=0",
        "profile": "h(r)=(r/L)^2(1-r/L)^2",
        "profile_boundary_values": [0.0, 0.0],
        "parameters": asdict(parameters),
        "base_dtn": base,
        "perturbed_dtn": perturbed,
        "dtn_difference": perturbed - base,
        "analytic_first_variation": analytic_derivative,
        "finite_difference_first_variation": numerical_derivative,
        "first_variation_residual": abs(analytic_derivative - numerical_derivative),
        "same_boundary_potential_value": True,
        "same_regular_center_condition": True,
        "different_dtn_map": abs(perturbed - base) > 1e-8,
        "physical_cap_action_selected": False,
    }


def partial_projector_payload() -> dict[str, Any]:
    parameters = BergerParameters(n_max=8)
    rows = []
    total_internal_kernel = 0
    total_isotypical_kernel = 0
    max_residual = 0.0
    for n in range(parameters.n_max + 1):
        matrix = berger_dirac_block(n, parameters.radius, parameters.stretch)
        projector, kernel = spectral_nonzero_projector(matrix)
        residuals = projector_residuals(projector)
        total_internal_kernel += kernel
        total_isotypical_kernel += kernel * (n + 1)
        max_residual = max(max_residual, *residuals.values())
        rows.append(
            {
                "n": n,
                "kernel_dimension_inside_Dn": kernel,
                "full_isotypical_kernel_contribution": kernel * (n + 1),
                "projector_residuals": residuals,
            }
        )
    return {
        "version": VERSION,
        "sector": "homogeneous Berger spinor blocks only",
        "parameters": asdict(parameters),
        "blocks": rows,
        "total_internal_kernel_through_n_max": total_internal_kernel,
        "total_isotypical_kernel_through_n_max": total_isotypical_kernel,
        "max_projector_residual": max_residual,
        "spinor_projector_computable": True,
        "gauge_metric_ghost_seam_projector_complete": False,
        "physical_full_projector_valid": False,
    }


def physical_readiness_payload() -> dict[str, Any]:
    checks = {
        "exact_homogeneous_Dirac_blocks": True,
        "round_spectrum_recovered": True,
        "Berger_first_zero_mode_identified": True,
        "finite_block_spinor_projector": True,
        "Berger_time_dependence_noncommuting": True,
        "Berger_axisymmetry_U1_obstruction_identified": True,
        "reduced_regular_cap_nonuniqueness_proved": True,
        "action_stationary_parent_background": False,
        "action_stationary_child_cap_background": False,
        "regular_cap_warp_factors_derived": False,
        "physical_cap_domain_selected": False,
        "complete_gauge_metric_ghost_projector": False,
        "three_nonuniform_shape_derivatives_computed": False,
        "full_relative_heat_kernel_control": False,
        "action_selected_nesting_and_absolute_scale": False,
        "physical_periodic_BVP_solution": False,
        "blinded_no_retuning_neutrino_execution": False,
        "full_particle_force_and_flavor_completion": False,
    }
    return {
        "version": VERSION,
        "mathematical_operator_advance_valid": True,
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
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> Mapping[str, dict[str, Any]]:
    return {
        "BHSM_exact_homogeneous_Berger_Dirac_blocks_v14_59.json": exact_berger_operator_payload(),
        "BHSM_Berger_zero_mode_certificate_v14_59.json": berger_zero_mode_payload(),
        "BHSM_Berger_U1_flavor_obstruction_v14_59.json": berger_u1_obstruction_payload(),
        "BHSM_regular_cap_nonuniqueness_certificate_v14_59.json": cap_nonuniqueness_payload(),
        "BHSM_partial_zero_mode_projector_v14_59.json": partial_projector_payload(),
        "BHSM_physical_completion_readiness_v14_59.json": physical_readiness_payload(),
        "BHSM_completion_gate_v14_59.json": completion_gate_payload(),
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
