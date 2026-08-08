"""BHSM v14.57 DtN/relative-heat-kernel insertion and neutrino kill screen.

Bounded results
---------------
1. The exact finite-mode insertion algebra from parent/child Dirichlet-to-
   Neumann data and a relative heat-kernel derivative bundle into a fixed-pair
   three-component wake generator is implemented.
2. A provenance-locked physical-input validator rejects synthetic, fitted,
   incomplete, or post-target-tuned coefficient bundles.
3. A deterministic diagnostic fixture verifies Hermiticity, relative-zeta
   identities, unitary monodromy, two independent relative eigenphases, and
   moving-seam residual insertion. It is not a physical neutrino prediction.
4. A no-retuning global neutrino kill-screen contract is implemented, but
   physical execution remains blocked because the current archive does not
   contain matched parent/child gauge-fixed operators and a proved trace-class
   relative heat kernel.

No physical mass, mass splitting, PMNS matrix, matter potential, lifetime,
cross section, cosmological radius, or particle spectrum is emitted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

VERSION = "v14.57"

PRIMARY_VERDICT = (
    "BHSM_V14_57_THE_DTN_RELATIVE_HEAT_KERNEL_INSERTION_ALGEBRA_AND_NO_"
    "RETUNING_NEUTRINO_KILL_SCREEN_ARE_CLOSED_BUT_PHYSICAL_EXECUTION_IS_"
    "BLOCKED_UNTIL_A_PROVENANCE_COMPLETE_ACTION_DERIVED_MATCHED_PARENT_"
    "CHILD_OPERATOR_BUNDLE_EXISTS"
)
RELATIVE_SPECTRAL_VERDICT = (
    "BHSM_FOR_POSITIVE_FINITE_MODE_OPERATORS_THE_RELATIVE_HEAT_TRACE_ZETA_"
    "VALUE_AND_ZETA_DERIVATIVE_REDUCE_EXACTLY_TO_SPECTRAL_SUMS_AND_A_"
    "PRIMED_LOG_DETERMINANT_DIFFERENCE"
)
NO_RETUNING_VERDICT = (
    "BHSM_A_NEUTRINO_RESULT_IS_ADMISSIBLE_ONLY_WHEN_OPERATOR_PROVENANCE_"
    "MODEL_COEFFICIENTS_INITIAL_STATE_DETECTOR_MAP_AND_TARGET_LEDGER_ARE_"
    "HASH_FROZEN_BEFORE_COMPARISON_AND_NO_POST_COMPARISON_PARAMETER_CHANGE_"
    "IS_ALLOWED"
)
EXACT_NEXT_OBJECT = (
    "MATCHED_COSMOLOGICAL_PARENT_CHILD_BACKGROUND_AND_GAUGE_FIXED_DIRAC_"
    "LAPLACE_SPECTRA_WITH_A_PROVENANCE_COMPLETE_DTN_RELATIVE_HEAT_KERNEL_"
    "BUNDLE_AND_A_BLINDED_EXPERIMENTAL_NEUTRINO_TARGET_LEDGER"
)

REQUIRED_PROOF_FLAGS = (
    "matched_parent_child_backgrounds",
    "action_owned_parent_child_contrast",
    "gauge_fixed_operator_domain",
    "complete_zero_mode_projector",
    "hermitian_dtn_maps",
    "trace_class_relative_heat_kernel",
    "small_time_control",
    "large_time_control",
    "shape_derivatives_action_derived",
    "moving_seam_bvp_converged",
    "fixed_pair_identity_preserved",
    "no_retuning_policy_enforced",
)

REQUIRED_HASH_FIELDS = (
    "source_commit_sha",
    "parent_background_sha256",
    "child_background_sha256",
    "parent_operator_sha256",
    "child_operator_sha256",
    "derivation_sha256",
    "coefficient_bundle_sha256",
    "target_ledger_sha256",
)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_GIT40 = re.compile(r"^[0-9a-f]{40}$")


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


def _complex_value(value: Any) -> complex:
    if isinstance(value, (int, float, complex, np.number)):
        result = complex(value)
    elif (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
        and len(value) == 2
    ):
        result = complex(float(value[0]), float(value[1]))
    else:
        raise ValueError(f"invalid complex entry: {value!r}")
    if not (math.isfinite(result.real) and math.isfinite(result.imag)):
        raise ValueError("finite matrix entries required")
    return result


def matrix_from_json(values: Sequence[Sequence[Any]], dimension: int = 3) -> np.ndarray:
    matrix = np.array(
        [[_complex_value(value) for value in row] for row in values],
        dtype=np.complex128,
    )
    if matrix.shape != (dimension, dimension):
        raise ValueError(f"expected {dimension}x{dimension} matrix")
    return matrix


def matrix_to_json(matrix: np.ndarray, tolerance: float = 1e-15) -> list[list[Any]]:
    array = np.asarray(matrix, dtype=np.complex128)
    output: list[list[Any]] = []
    for row in array:
        encoded_row: list[Any] = []
        for value in row:
            real = float(value.real)
            imag = float(value.imag)
            if abs(real) < tolerance:
                real = 0.0
            if abs(imag) < tolerance:
                imag = 0.0
            encoded_row.append(real if imag == 0.0 else [real, imag])
        output.append(encoded_row)
    return output


def hermiticity_residual(matrix: np.ndarray) -> float:
    array = np.asarray(matrix, dtype=np.complex128)
    return float(np.linalg.norm(array - array.conj().T, ord="fro"))


def unitarity_residual(matrix: np.ndarray) -> float:
    array = np.asarray(matrix, dtype=np.complex128)
    identity = np.eye(array.shape[0], dtype=np.complex128)
    return float(np.linalg.norm(array.conj().T @ array - identity, ord="fro"))


def commutator_norm(a: np.ndarray, b: np.ndarray) -> float:
    left = np.asarray(a, dtype=np.complex128)
    right = np.asarray(b, dtype=np.complex128)
    return float(np.linalg.norm(left @ right - right @ left, ord="fro"))


def validate_hermitian(matrix: np.ndarray, tolerance: float = 1e-10) -> None:
    if hermiticity_residual(matrix) > tolerance:
        raise ValueError("Hermitian matrix required")


def validate_projector(projector: np.ndarray, tolerance: float = 1e-10) -> None:
    validate_hermitian(projector, tolerance)
    if np.linalg.norm(projector @ projector - projector, ord="fro") > tolerance:
        raise ValueError("Hermitian idempotent projector required")


def positive_spectrum(matrix: np.ndarray, zero_tolerance: float = 1e-10) -> np.ndarray:
    validate_hermitian(matrix)
    eigenvalues = np.linalg.eigvalsh(matrix).real
    if np.min(eigenvalues) < -zero_tolerance:
        raise ValueError("positive-semidefinite operator required")
    return eigenvalues[eigenvalues > zero_tolerance]


def relative_heat_trace(
    child_operator: np.ndarray,
    parent_operator: np.ndarray,
    time: float,
    zero_tolerance: float = 1e-10,
) -> float:
    if not math.isfinite(time) or time <= 0.0:
        raise ValueError("positive finite heat time required")
    child = positive_spectrum(child_operator, zero_tolerance)
    parent = positive_spectrum(parent_operator, zero_tolerance)
    return float(np.exp(-time * child).sum() - np.exp(-time * parent).sum())


def relative_zeta_value(
    child_operator: np.ndarray,
    parent_operator: np.ndarray,
    s: float,
    zero_tolerance: float = 1e-10,
) -> float:
    if not math.isfinite(s):
        raise ValueError("finite real zeta argument required")
    child = positive_spectrum(child_operator, zero_tolerance)
    parent = positive_spectrum(parent_operator, zero_tolerance)
    return float(np.power(child, -s).sum() - np.power(parent, -s).sum())


def relative_zeta_zero(
    child_operator: np.ndarray,
    parent_operator: np.ndarray,
    zero_tolerance: float = 1e-10,
) -> float:
    return relative_zeta_value(child_operator, parent_operator, 0.0, zero_tolerance)


def relative_zeta_prime_zero(
    child_operator: np.ndarray,
    parent_operator: np.ndarray,
    zero_tolerance: float = 1e-10,
) -> float:
    child = positive_spectrum(child_operator, zero_tolerance)
    parent = positive_spectrum(parent_operator, zero_tolerance)
    return float(-np.log(child).sum() + np.log(parent).sum())


def primed_logdet_difference(
    child_operator: np.ndarray,
    parent_operator: np.ndarray,
    zero_tolerance: float = 1e-10,
) -> float:
    """Return log det'(child)-log det'(parent)."""
    return -relative_zeta_prime_zero(child_operator, parent_operator, zero_tolerance)


def projected_dtn_matching_operator(
    child_dtn: np.ndarray,
    parent_dtn: np.ndarray,
    interface_hessian: np.ndarray,
    physical_projector: np.ndarray,
) -> np.ndarray:
    for matrix in (child_dtn, parent_dtn, interface_hessian):
        validate_hermitian(matrix)
    validate_projector(physical_projector)
    raw = child_dtn - parent_dtn - interface_hessian
    projected = physical_projector @ raw @ physical_projector
    return 0.5 * (projected + projected.conj().T)


def hermitian_linear_combination(
    coefficients: Sequence[float], generators: Sequence[np.ndarray]
) -> np.ndarray:
    if len(coefficients) != len(generators) or not coefficients:
        raise ValueError("matching nonempty coefficient/generator lists required")
    result = np.zeros_like(np.asarray(generators[0], dtype=np.complex128))
    for coefficient, generator in zip(coefficients, generators):
        if not math.isfinite(float(coefficient)):
            raise ValueError("finite coefficients required")
        validate_hermitian(generator)
        result = result + float(coefficient) * generator
    return 0.5 * (result + result.conj().T)


def remove_common_phase(generator: np.ndarray) -> np.ndarray:
    validate_hermitian(generator)
    dimension = generator.shape[0]
    return generator - np.trace(generator).real / dimension * np.eye(dimension)


def unitary_from_hermitian(generator: np.ndarray, proper_time: float) -> np.ndarray:
    validate_hermitian(generator)
    if not math.isfinite(proper_time) or proper_time < 0.0:
        raise ValueError("finite nonnegative proper time required")
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    phases = np.exp(-1j * eigenvalues * proper_time)
    return eigenvectors @ np.diag(phases) @ eigenvectors.conj().T


def normalized_probabilities(state: np.ndarray) -> tuple[float, float, float]:
    vector = np.asarray(state, dtype=np.complex128).reshape(-1)
    if vector.shape != (3,):
        raise ValueError("three-component wake state required")
    weights = np.abs(vector) ** 2
    total = float(weights.sum())
    if total <= 0.0:
        raise ValueError("nonzero wake state required")
    probabilities = weights / total
    return tuple(float(value) for value in probabilities)  # type: ignore[return-value]


def independent_relative_gaps(generator: np.ndarray, cycle_period: float) -> tuple[float, float]:
    validate_hermitian(generator)
    if not math.isfinite(cycle_period) or cycle_period <= 0.0:
        raise ValueError("positive cycle period required")
    eigenvalues = np.linalg.eigvalsh(generator).real
    eigenvalues.sort()
    return (
        float((eigenvalues[1] - eigenvalues[0]) * cycle_period),
        float((eigenvalues[2] - eigenvalues[0]) * cycle_period),
    )


def _required_matrix(bundle: Mapping[str, Any], name: str) -> np.ndarray:
    matrices = bundle.get("matrices")
    if not isinstance(matrices, Mapping) or name not in matrices:
        raise ValueError(f"missing matrix: {name}")
    return matrix_from_json(matrices[name])


def validate_bundle(bundle: Mapping[str, Any], physical: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    mode = bundle.get("mode")
    if mode not in {"diagnostic", "physical"}:
        errors.append("mode must be diagnostic or physical")
    if physical and mode != "physical":
        errors.append("physical execution requires mode=physical")

    proof_flags = bundle.get("proof_flags")
    if not isinstance(proof_flags, Mapping):
        errors.append("missing proof_flags mapping")
        proof_flags = {}
    missing_flags = [flag for flag in REQUIRED_PROOF_FLAGS if proof_flags.get(flag) is not True]
    if physical and missing_flags:
        errors.extend(f"proof flag false: {flag}" for flag in missing_flags)

    provenance = bundle.get("provenance")
    if not isinstance(provenance, Mapping):
        errors.append("missing provenance mapping")
        provenance = {}
    if provenance.get("measured_data_used_to_choose_coefficients") is not False:
        errors.append("coefficients must not be chosen from measured neutrino data")
    if provenance.get("coefficients_frozen_before_target_access") is not True:
        errors.append("coefficients must be frozen before target access")
    if provenance.get("post_comparison_retuning_allowed") is not False:
        errors.append("post-comparison retuning must be forbidden")
    if physical:
        source_commit = provenance.get("source_commit_sha", "")
        if not isinstance(source_commit, str) or _GIT40.fullmatch(source_commit) is None:
            errors.append("valid 40-hex source_commit_sha required")
        for field in REQUIRED_HASH_FIELDS[1:]:
            value = provenance.get(field, "")
            if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
                errors.append(f"valid SHA-256 required: {field}")

    matrix_names = (
        "parent_dtn",
        "child_dtn",
        "interface_hessian",
        "physical_projector",
        "parent_heat_operator",
        "child_heat_operator",
        "shape_generator_1",
        "shape_generator_2",
        "shape_generator_3",
        "detector_basis",
        "matter_kick_generator",
    )
    decoded: dict[str, np.ndarray] = {}
    for name in matrix_names:
        try:
            decoded[name] = _required_matrix(bundle, name)
        except Exception as exc:  # fail-closed report
            errors.append(f"{name}: {exc}")

    for name in (
        "parent_dtn",
        "child_dtn",
        "interface_hessian",
        "parent_heat_operator",
        "child_heat_operator",
        "shape_generator_1",
        "shape_generator_2",
        "shape_generator_3",
        "matter_kick_generator",
    ):
        if name in decoded:
            try:
                validate_hermitian(decoded[name])
            except ValueError as exc:
                errors.append(f"{name}: {exc}")
    if "physical_projector" in decoded:
        try:
            validate_projector(decoded["physical_projector"])
        except ValueError as exc:
            errors.append(f"physical_projector: {exc}")
    for name in ("parent_heat_operator", "child_heat_operator"):
        if name in decoded:
            try:
                positive_spectrum(decoded[name])
            except ValueError as exc:
                errors.append(f"{name}: {exc}")
    if "detector_basis" in decoded and unitarity_residual(decoded["detector_basis"]) > 1e-10:
        errors.append("detector_basis must be unitary")

    coefficients = bundle.get("coefficients")
    if not isinstance(coefficients, Mapping):
        errors.append("missing coefficients mapping")
        coefficients = {}
    derivatives = coefficients.get("zeta_prime_shape_derivatives")
    if not isinstance(derivatives, Sequence) or isinstance(derivatives, (str, bytes)) or len(derivatives) != 3:
        errors.append("three zeta_prime_shape_derivatives required")
    else:
        try:
            if not all(math.isfinite(float(value)) for value in derivatives):
                errors.append("finite zeta derivatives required")
        except Exception:
            errors.append("numeric zeta derivatives required")
    try:
        cycle_period = float(coefficients.get("cycle_period"))
        if not math.isfinite(cycle_period) or cycle_period <= 0.0:
            errors.append("positive cycle_period required")
    except Exception:
        errors.append("numeric cycle_period required")

    targets = bundle.get("target_ledger")
    if physical:
        if not isinstance(targets, Mapping):
            errors.append("physical target_ledger required")
        elif targets.get("blinded_before_model_freeze") is not True:
            errors.append("target ledger must be blinded before model freeze")

    return {
        "valid": not errors,
        "physical_execution_requested": physical,
        "mode": mode,
        "errors": errors,
        "missing_proof_flags": missing_flags,
    }


def effective_wake_generator(bundle: Mapping[str, Any]) -> np.ndarray:
    validation = validate_bundle(bundle, physical=False)
    if not validation["valid"]:
        raise ValueError("invalid coefficient bundle: " + "; ".join(validation["errors"]))
    child_dtn = _required_matrix(bundle, "child_dtn")
    parent_dtn = _required_matrix(bundle, "parent_dtn")
    interface_hessian = _required_matrix(bundle, "interface_hessian")
    projector = _required_matrix(bundle, "physical_projector")
    local = projected_dtn_matching_operator(
        child_dtn, parent_dtn, interface_hessian, projector
    )
    generators = [
        _required_matrix(bundle, "shape_generator_1"),
        _required_matrix(bundle, "shape_generator_2"),
        _required_matrix(bundle, "shape_generator_3"),
    ]
    coefficients = bundle["coefficients"]
    derivatives = [float(value) for value in coefficients["zeta_prime_shape_derivatives"]]
    nonlocal_term = hermitian_linear_combination(derivatives, generators)
    return remove_common_phase(local + nonlocal_term)


def moving_seam_bvp_residual(
    seam_amplitudes: Sequence[complex],
    derivative_amplitudes: Sequence[complex],
    generator: np.ndarray,
    cycle_period: float,
    holonomy_phase: float = 0.0,
) -> dict[str, Any]:
    q = np.asarray(seam_amplitudes, dtype=np.complex128).reshape(-1)
    dq = np.asarray(derivative_amplitudes, dtype=np.complex128).reshape(-1)
    if q.shape != (3,) or dq.shape != (3,):
        raise ValueError("three seam amplitudes and derivatives required")
    if not math.isfinite(holonomy_phase):
        raise ValueError("finite holonomy phase required")
    monodromy = unitary_from_hermitian(generator, cycle_period)
    holonomy = np.exp(-1j * holonomy_phase)
    phase_closure = monodromy @ q - holonomy * q
    dynamic_residual = 1j * dq - generator @ q
    return {
        "dynamic_residual_norm": float(np.linalg.norm(dynamic_residual)),
        "phase_closure_residual_norm": float(np.linalg.norm(phase_closure)),
        "combined_residual_norm": float(
            math.hypot(np.linalg.norm(dynamic_residual), np.linalg.norm(phase_closure))
        ),
    }


def _rotation_12(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.complex128)


def _rotation_13(theta: float, phase: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    em = np.exp(-1j * phase)
    ep = np.exp(1j * phase)
    return np.array([[c, 0.0, s * em], [0.0, 1.0, 0.0], [-s * ep, 0.0, c]], dtype=np.complex128)


def _rotation_23(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, s], [0.0, -s, c]], dtype=np.complex128)


def diagnostic_bundle() -> dict[str, Any]:
    """Synthetic pipeline fixture; all values are nonphysical diagnostics."""
    g12 = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=np.complex128)
    g23 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]], dtype=np.complex128)
    g13i = np.array([[0.0, 0.0, -1j], [0.0, 0.0, 0.0], [1j, 0.0, 0.0]], dtype=np.complex128)
    detector = _rotation_23(0.47) @ _rotation_13(0.21, 0.73) @ _rotation_12(0.31)
    parent_dtn = np.array(
        [[1.40, 0.08, 0.00], [0.08, 1.92, 0.06], [0.00, 0.06, 2.48]],
        dtype=np.complex128,
    )
    child_dtn = np.array(
        [[1.77, 0.19, 0.04], [0.19, 2.23, 0.17], [0.04, 0.17, 2.91]],
        dtype=np.complex128,
    )
    interface = np.diag([0.11, 0.07, 0.13]).astype(np.complex128)
    parent_heat = np.array(
        [[1.20, 0.04, 0.00], [0.04, 2.10, 0.03], [0.00, 0.03, 3.00]],
        dtype=np.complex128,
    )
    child_heat = np.array(
        [[1.43, 0.07, 0.02], [0.07, 2.37, 0.05], [0.02, 0.05, 3.31]],
        dtype=np.complex128,
    )
    kick = 0.17 * g12 - 0.13 * g23 + 0.09 * g13i
    payload: dict[str, Any] = {
        "artifact": "BHSM_diagnostic_dtn_heat_kernel_bundle_v14_57",
        "version": VERSION,
        "mode": "diagnostic",
        "physical_interpretation_forbidden": True,
        "provenance": {
            "source_commit_sha": "0" * 40,
            "parent_background_sha256": "1" * 64,
            "child_background_sha256": "2" * 64,
            "parent_operator_sha256": "3" * 64,
            "child_operator_sha256": "4" * 64,
            "derivation_sha256": "5" * 64,
            "coefficient_bundle_sha256": "6" * 64,
            "target_ledger_sha256": "7" * 64,
            "measured_data_used_to_choose_coefficients": False,
            "coefficients_frozen_before_target_access": True,
            "post_comparison_retuning_allowed": False,
            "provenance_status": "synthetic_test_fixture_not_action_derived",
        },
        "proof_flags": {
            flag: False for flag in REQUIRED_PROOF_FLAGS
        },
        "matrices": {
            "parent_dtn": matrix_to_json(parent_dtn),
            "child_dtn": matrix_to_json(child_dtn),
            "interface_hessian": matrix_to_json(interface),
            "physical_projector": matrix_to_json(np.eye(3)),
            "parent_heat_operator": matrix_to_json(parent_heat),
            "child_heat_operator": matrix_to_json(child_heat),
            "shape_generator_1": matrix_to_json(g12),
            "shape_generator_2": matrix_to_json(g23),
            "shape_generator_3": matrix_to_json(g13i),
            "detector_basis": matrix_to_json(detector),
            "matter_kick_generator": matrix_to_json(kick),
        },
        "coefficients": {
            "zeta_prime_shape_derivatives": [0.071, -0.046, 0.033],
            "cycle_period": 1.70,
            "moving_seam_bvp_scale": 1.0,
            "values_are_synthetic": True,
        },
        "target_ledger": {
            "blinded_before_model_freeze": True,
            "diagnostic_only": True,
            "physical_windows": [],
        },
    }
    payload["diagnostic_fixture_sha256"] = sha256_payload(payload)
    return payload


def diagnostic_pipeline_payload() -> dict[str, Any]:
    bundle = diagnostic_bundle()
    generator = effective_wake_generator(bundle)
    period = float(bundle["coefficients"]["cycle_period"])
    monodromy = unitary_from_hermitian(generator, period)
    detector = _required_matrix(bundle, "detector_basis")
    kick_generator = _required_matrix(bundle, "matter_kick_generator")
    kick = unitary_from_hermitian(kick_generator, 1.0)
    initial = np.array([1.0, 0.0, 0.0], dtype=np.complex128)
    vacuum_state = detector.conj().T @ monodromy @ detector @ initial
    matter_state = detector.conj().T @ monodromy @ kick @ detector @ initial
    parent_heat = _required_matrix(bundle, "parent_heat_operator")
    child_heat = _required_matrix(bundle, "child_heat_operator")
    gaps = independent_relative_gaps(generator, period)
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    q0 = eigenvectors[:, 1]
    dq0 = -1j * generator @ q0
    holonomy_phase = float(eigenvalues[1] * period)
    bvp = moving_seam_bvp_residual(
        q0, dq0, generator, period, holonomy_phase=holonomy_phase
    )
    return {
        "artifact": "BHSM_synthetic_dtn_heat_kernel_wake_pipeline_v14_57",
        "version": VERSION,
        "physical_prediction": False,
        "generator": matrix_to_json(generator),
        "generator_hermiticity_residual": hermiticity_residual(generator),
        "generator_trace_after_common_phase_removal": float(np.trace(generator).real),
        "generator_eigenvalues": [float(value) for value in np.linalg.eigvalsh(generator)],
        "relative_eigenphase_gaps": list(gaps),
        "monodromy_unitarity_residual": unitarity_residual(monodromy),
        "matter_kick_unitarity_residual": unitarity_residual(kick),
        "free_kick_commutator_norm": commutator_norm(monodromy, kick),
        "vacuum_detector_probabilities": list(normalized_probabilities(vacuum_state)),
        "matter_detector_probabilities": list(normalized_probabilities(matter_state)),
        "relative_heat_trace_samples": {
            str(time): relative_heat_trace(child_heat, parent_heat, time)
            for time in (0.05, 0.2, 1.0, 4.0)
        },
        "relative_zeta_zero": relative_zeta_zero(child_heat, parent_heat),
        "relative_zeta_prime_zero": relative_zeta_prime_zero(child_heat, parent_heat),
        "primed_logdet_difference": primed_logdet_difference(child_heat, parent_heat),
        "zeta_logdet_identity_residual": abs(
            relative_zeta_prime_zero(child_heat, parent_heat)
            + primed_logdet_difference(child_heat, parent_heat)
        ),
        "moving_seam_bvp_insertion": {
            **bvp,
            "diagnostic_holonomy_phase": holonomy_phase,
            "relative_periodic_eigenmode_witness": True,
        },
        "pair_identity_changed": False,
        "diagnostic_only": True,
    }


def relative_heat_kernel_contract_payload() -> dict[str, Any]:
    bundle = diagnostic_bundle()
    parent = _required_matrix(bundle, "parent_heat_operator")
    child = _required_matrix(bundle, "child_heat_operator")
    return {
        "artifact": "BHSM_relative_heat_kernel_spectral_contract_v14_57",
        "version": VERSION,
        "finite_mode_formulas": {
            "relative_heat_trace": "Theta_rel(t)=Tr exp(-t A_child)-Tr exp(-t A_parent)",
            "relative_zeta": "zeta_rel(s)=sum lambda_child^(-s)-sum lambda_parent^(-s)",
            "zeta_zero": "zeta_rel(0)=rank'(A_child)-rank'(A_parent)",
            "zeta_prime_zero": "zeta_rel'(0)=-log det'(A_child)+log det'(A_parent)",
        },
        "diagnostic_parent_positive_eigenvalues": [float(v) for v in positive_spectrum(parent)],
        "diagnostic_child_positive_eigenvalues": [float(v) for v in positive_spectrum(child)],
        "diagnostic_zeta_zero": relative_zeta_zero(child, parent),
        "diagnostic_zeta_prime_zero": relative_zeta_prime_zero(child, parent),
        "continuum_physical_requirements": [
            "common gauge-fixed Hilbert-space comparison",
            "complete zero-mode subtraction",
            "trace-class relative heat kernel for every t>0",
            "controlled small-time asymptotic subtraction",
            "controlled large-time decay",
            "shape derivatives justified under trace/integral interchange",
        ],
        "relative_spectral_verdict": RELATIVE_SPECTRAL_VERDICT,
        "physical_completion": False,
    }


def dtn_insertion_contract_payload() -> dict[str, Any]:
    bundle = diagnostic_bundle()
    local = projected_dtn_matching_operator(
        _required_matrix(bundle, "child_dtn"),
        _required_matrix(bundle, "parent_dtn"),
        _required_matrix(bundle, "interface_hessian"),
        _required_matrix(bundle, "physical_projector"),
    )
    generators = [
        _required_matrix(bundle, "shape_generator_1"),
        _required_matrix(bundle, "shape_generator_2"),
        _required_matrix(bundle, "shape_generator_3"),
    ]
    derivatives = bundle["coefficients"]["zeta_prime_shape_derivatives"]
    nonlocal_term = hermitian_linear_combination(derivatives, generators)
    total = remove_common_phase(local + nonlocal_term)
    return {
        "artifact": "BHSM_dtn_heat_kernel_wake_insertion_contract_v14_57",
        "version": VERSION,
        "formulae": {
            "local_matching_operator": "M=P(N_child-N_parent-J_interface)P",
            "nonlocal_shape_term": "H_nonlocal=sum_A (partial_A zeta_rel'(0)) G_A",
            "wake_generator": "H_wake=traceless_hermitian_part(M+H_nonlocal)",
            "monodromy": "U(T)=exp(-i T H_wake)",
            "moving_seam_equation": "i dot q-H_wake q=0 with U(T)q(0)=exp(-i theta_h)q(0)",
        },
        "diagnostic_local_matching_operator": matrix_to_json(local),
        "diagnostic_nonlocal_shape_term": matrix_to_json(nonlocal_term),
        "diagnostic_effective_wake_generator": matrix_to_json(total),
        "three_shape_generators_pairwise_commutator_norms": [
            commutator_norm(generators[0], generators[1]),
            commutator_norm(generators[0], generators[2]),
            commutator_norm(generators[1], generators[2]),
        ],
        "physical_coefficient_bundle_present": False,
        "synthetic_fixture_is_prediction": False,
    }


def no_retuning_kill_screen_contract_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_no_retuning_global_neutrino_kill_screen_v14_57",
        "version": VERSION,
        "policy": [
            "freeze source commit and all operator/background/derivation hashes",
            "freeze all coefficients, initial states, baselines, matter profiles, and detector map",
            "freeze a blinded experimental target ledger before opening model outputs",
            "run the full target ledger in one execution",
            "permit no parameter changes after any target comparison",
            "report every failed target and covariance block; do not subset after viewing",
        ],
        "hard_fail_conditions": [
            "any proof flag false",
            "any provenance hash absent or malformed",
            "measured neutrino data used to select a coefficient",
            "post-comparison retuning allowed",
            "parent and child DtN contrast not action-owned",
            "relative heat kernel not trace class or zero modes incomplete",
            "wake generator non-Hermitian or monodromy nonunitary",
            "fewer than two independent relative eigenphase gaps",
            "pair identity changes during propagation",
            "target ledger opened before coefficient freeze",
            "only a favorable subset of targets reported",
        ],
        "minimum_global_target_classes": [
            "vacuum disappearance",
            "vacuum appearance",
            "matter-modified propagation",
            "neutrino/antineutrino comparison",
            "baseline and energy scaling",
            "normalization and probability conservation",
            "source and detector channel consistency",
        ],
        "no_retuning_verdict": NO_RETUNING_VERDICT,
        "physical_target_values_bundled": False,
        "physical_execution_status": "BLOCKED_PENDING_BLINDED_TARGET_LEDGER_AND_ACTION_DERIVED_OPERATOR_BUNDLE",
    }


def current_archive_readiness_payload() -> dict[str, Any]:
    fixture = diagnostic_bundle()
    diagnostic_validation = validate_bundle(fixture, physical=False)
    physical_validation = validate_bundle(fixture, physical=True)
    return {
        "artifact": "BHSM_current_archive_neutrino_readiness_v14_57",
        "version": VERSION,
        "diagnostic_pipeline_valid": diagnostic_validation["valid"],
        "physical_pipeline_valid": physical_validation["valid"],
        "physical_blockers": physical_validation["errors"],
        "missing_proof_flags": physical_validation["missing_proof_flags"],
        "archive_assessment": (
            "the insertion and kill-screen software path exists, but the supplied bundle "
            "is intentionally synthetic and every action-provenance proof flag remains false"
        ),
        "physical_result_emitted": False,
        "primary_verdict": PRIMARY_VERDICT,
    }


def completion_gate_payload() -> dict[str, Any]:
    readiness = current_archive_readiness_payload()
    return {
        "artifact": "BHSM_completion_gate_v14_57",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "closed": [
            "finite-mode parent/child DtN insertion algebra",
            "finite-mode relative heat-trace and zeta identities",
            "three-shape-generator nonlocal wake insertion",
            "unitary three-eigenphase diagnostic monodromy",
            "moving-seam residual insertion contract",
            "strict physical coefficient-bundle validator",
            "no-retuning global neutrino kill-screen workflow",
        ],
        "invalidated_or_reclassified": [
            "a synthetic coefficient fixture is an action-derived physical result",
            "three Hermitian matrices alone prove a continuum trace-class relative determinant",
            "a structurally unitary monodromy predicts physical neutrino splittings",
            "post-target coefficient adjustment is an admissible completion strategy",
            "the current archive already contains a provenance-complete physical operator bundle",
        ],
        "open": [
            "matched cosmological parent and particle child background solution",
            "gauge-fixed parent and child Dirac/Laplace operator domains",
            "action-derived parent and child DtN matrices on the same three shape harmonics",
            "complete zero-mode projector",
            "trace-class continuum relative heat kernel with asymptotic control",
            "action-derived shape derivatives of zeta_rel_prime_zero",
            "converged moving-seam periodic BVP on the physical background",
            "blinded external neutrino target ledger and covariance blocks",
            "one-shot no-retuning physical kill-screen execution",
            "physical masses, splittings, detector map, matter response, CP behavior, and widths",
        ],
        "physical_execution_valid": readiness["physical_pipeline_valid"],
        "mark_I": "REACHED",
        "mark_II": "CONDITIONAL",
        "mark_III": "NOT_REACHED",
        "full_BHSM_complete": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physical_neutrino_prediction_emitted": False,
        "full_repository_suite_run": False,
        "usb_touched": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_diagnostic_dtn_heat_kernel_bundle_v14_57.json": diagnostic_bundle(),
        "BHSM_dtn_heat_kernel_wake_insertion_contract_v14_57.json": dtn_insertion_contract_payload(),
        "BHSM_relative_heat_kernel_spectral_contract_v14_57.json": relative_heat_kernel_contract_payload(),
        "BHSM_synthetic_dtn_heat_kernel_wake_pipeline_v14_57.json": diagnostic_pipeline_payload(),
        "BHSM_no_retuning_global_neutrino_kill_screen_v14_57.json": no_retuning_kill_screen_contract_payload(),
        "BHSM_current_archive_neutrino_readiness_v14_57.json": current_archive_readiness_payload(),
        "BHSM_completion_gate_v14_57.json": completion_gate_payload(),
    }


def materialize(output: str | Path) -> list[Path]:
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, payload in artifact_payloads().items():
        path = destination / filename
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    return written
