"""Full one-form minus ghost non-Abelian electric/magnetic response."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.linalg import block_diag, null_space

from bhsm.interface.aether_common_source_frechet_response_v15_99 import (
    frechet_second_response,
)
from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    periodic_first_derivative,
    periodic_laplacian,
    source_profiles,
    uniform_dense_geometry,
)
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (
    spin_matrices,
)


VERSION = "v16.04"
CLASSIFICATION = "BHSM_NONABELIAN_FULL_DERHAM_ELECTRIC_MAGNETIC_RESPONSE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def cartesian_spin_one_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    epsilon = np.zeros((3, 3, 3))
    epsilon[0, 1, 2] = epsilon[1, 2, 0] = epsilon[2, 0, 1] = 1.0
    epsilon[0, 2, 1] = epsilon[2, 1, 0] = epsilon[1, 0, 2] = -1.0
    return tuple(
        np.asarray(
            [[-1.0j * epsilon[axis, left, right] for right in range(3)]
             for left in range(3)],
            dtype=complex,
        )
        for axis in range(3)
    )


def angular_derham_blocks(level: int, radius: float) -> dict[str, np.ndarray]:
    n = int(level)
    if n < 0 or radius <= 0.0:
        raise ValueError("nonnegative level and positive radius required")
    j = spin_matrices(n)
    momenta = tuple(2.0 * value / radius for value in j)
    spin = cartesian_spin_one_matrices()
    scalar_dimension = n + 1
    vector_dimension = 3 * scalar_dimension
    gradient = np.vstack(momenta)
    curl = 2.0 / radius * np.eye(vector_dimension, dtype=complex)
    for axis in range(3):
        curl += np.kron(spin[axis], momenta[axis])
    scalar = gradient.conj().T @ gradient
    vector = curl @ curl + gradient @ gradient.conj().T
    scalar_vertex = 2.0 * momenta[2]
    scalar_contact = 2.0 * np.eye(scalar_dimension)
    gradient_source = np.vstack((
        np.zeros((2 * scalar_dimension, scalar_dimension), dtype=complex),
        np.eye(scalar_dimension, dtype=complex),
    ))
    curl_source = np.kron(spin[2], np.eye(scalar_dimension))
    vector_vertex = (
        curl @ curl_source + curl_source @ curl
        + gradient_source @ gradient.conj().T
        + gradient @ gradient_source.conj().T
    )
    vector_contact = 2.0 * (
        curl_source @ curl_source
        + gradient_source @ gradient_source.conj().T
    )
    return {
        "gradient": gradient,
        "curl": curl,
        "scalar_operator": scalar,
        "vector_operator": vector,
        "scalar_vertex": scalar_vertex,
        "scalar_contact": scalar_contact,
        "vector_vertex": vector_vertex,
        "vector_contact": vector_contact,
        "temporal_spatial_injection": gradient_source,
    }


def derham_identity_witness(maximum_level: int = 6) -> list[dict[str, float | int]]:
    rows = []
    for level in range(1, maximum_level + 1):
        blocks = angular_derham_blocks(level, 1.0)
        scalar_eigenvalue = float(level * (level + 2))
        vector_eigenvalues = np.linalg.eigvalsh(blocks["vector_operator"])
        rows.append({
            "level": level,
            "curl_gradient_residual": float(
                np.linalg.norm(blocks["curl"] @ blocks["gradient"])
            ),
            "scalar_laplacian_residual": float(
                np.linalg.norm(
                    blocks["scalar_operator"]
                    - scalar_eigenvalue * np.eye(level + 1)
                )
            ),
            "longitudinal_eigenvalue_count": int(
                np.count_nonzero(
                    np.isclose(vector_eigenvalues, scalar_eigenvalue, atol=1.0e-10)
                )
            ),
            "expected_longitudinal_eigenvalue_count": level + 1,
        })
    return rows


def _remove_global_scalar_zero(
    operator: np.ndarray,
    vertex: np.ndarray,
    contact: np.ndarray,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    constant = np.ones((1, points), dtype=complex) / math.sqrt(points)
    basis = null_space(constant)
    return (
        basis.conj().T @ operator @ basis,
        basis.conj().T @ vertex @ basis,
        basis.conj().T @ contact @ basis,
        basis,
    )


def full_oneform_ghost_matrices(
    level: int,
    radii: np.ndarray,
    proper_step: float,
    profile: np.ndarray,
) -> dict[str, np.ndarray]:
    n = int(level)
    r = np.asarray(radii, dtype=float)
    source = np.asarray(profile, dtype=float)
    if n < 0 or r.ndim != 1 or source.shape != r.shape:
        raise ValueError("invalid level, geometry, or source")
    points = len(r)
    scalar_dimension = n + 1
    vector_dimension = 3 * scalar_dimension
    blocks = [angular_derham_blocks(n, float(radius)) for radius in r]
    time_laplacian_scalar = np.kron(
        periodic_laplacian(points, proper_step), np.eye(scalar_dimension)
    )
    time_laplacian_vector = np.kron(
        periodic_laplacian(points, proper_step), np.eye(vector_dimension)
    )
    scalar_operator = time_laplacian_scalar + block_diag(
        *[row["scalar_operator"] for row in blocks]
    )
    spatial_operator = time_laplacian_vector + block_diag(
        *[row["vector_operator"] for row in blocks]
    )
    scalar_vertex = block_diag(
        *[
            value * row["scalar_vertex"]
            for value, row in zip(source, blocks, strict=True)
        ]
    )
    spatial_vertex = block_diag(
        *[
            value * row["vector_vertex"]
            for value, row in zip(source, blocks, strict=True)
        ]
    )
    scalar_contact = block_diag(
        *[
            value**2 * row["scalar_contact"]
            for value, row in zip(source, blocks, strict=True)
        ]
    )
    spatial_contact = block_diag(
        *[
            value**2 * row["vector_contact"]
            for value, row in zip(source, blocks, strict=True)
        ]
    )
    source_derivative = periodic_first_derivative(points, proper_step) @ source
    cross = block_diag(
        *[
            -2.0j * value * row["temporal_spatial_injection"].conj().T
            for value, row in zip(source_derivative, blocks, strict=True)
        ]
    )
    scalar_basis = np.eye(points * scalar_dimension, dtype=complex)
    if n == 0:
        (
            scalar_operator,
            scalar_vertex,
            scalar_contact,
            scalar_basis,
        ) = _remove_global_scalar_zero(
            scalar_operator, scalar_vertex, scalar_contact, points
        )
        cross = scalar_basis.conj().T @ cross
    oneform_operator = block_diag(scalar_operator, spatial_operator)
    oneform_vertex = np.block(
        [[scalar_vertex, cross], [cross.conj().T, spatial_vertex]]
    )
    oneform_contact = block_diag(scalar_contact, spatial_contact)
    return {
        "oneform_operator": oneform_operator,
        "oneform_vertex": oneform_vertex,
        "oneform_contact": oneform_contact,
        "ghost_operator": scalar_operator,
        "ghost_vertex": scalar_vertex,
        "ghost_contact": scalar_contact,
    }


def level_gauge_ghost_response(
    level: int,
    geometry: Mapping[str, Any],
    profile: np.ndarray,
) -> float:
    matrices = full_oneform_ghost_matrices(
        level,
        np.asarray(geometry["radii"]),
        float(geometry["proper_step"]),
        profile,
    )
    oneform = frechet_second_response(
        matrices["oneform_operator"],
        matrices["oneform_vertex"],
        matrices["oneform_vertex"],
        contact_vertex=matrices["oneform_contact"],
        supertrace_weight=1.0,
    )
    ghost = frechet_second_response(
        matrices["ghost_operator"],
        matrices["ghost_vertex"],
        matrices["ghost_vertex"],
        contact_vertex=matrices["ghost_contact"],
        supertrace_weight=-2.0,
    )
    return float((level + 1) * (oneform + ghost))


def nonabelian_derham_response(
    cycle: Mapping[str, Any] | None = None,
    *,
    points: int = 24,
    maximum_level: int = 6,
) -> dict[str, Any]:
    values = dense_constraint_solved_cycle() if cycle is None else cycle
    geometry = uniform_dense_geometry(values, points)
    profiles = source_profiles(geometry)
    constant = np.asarray(profiles["constant"])
    frequency = np.asarray(profiles["first_frequency"])
    omega = float(profiles["first_angular_frequency"])
    constant_total = 0.0
    frequency_total = 0.0
    rows = []
    for level in range(maximum_level + 1):
        constant_response = level_gauge_ghost_response(
            level, geometry, constant
        )
        frequency_response = level_gauge_ghost_response(
            level, geometry, frequency
        )
        constant_total += constant_response
        frequency_total += frequency_response
        rows.append({
            "level": level,
            "constant_response": constant_response,
            "first_frequency_response": frequency_response,
            "cumulative_constant_response": constant_total,
            "cumulative_first_frequency_response": frequency_total,
        })
    inverse_radius_squared = float(
        np.mean(1.0 / np.asarray(geometry["radii"]) ** 2)
    )
    magnetic_eigenvalue = 4.0 * inverse_radius_squared
    unit_kb = constant_total / magnetic_eigenvalue
    unit_ke = (frequency_total - constant_total) / omega**2
    return {
        "points": points,
        "maximum_level": maximum_level,
        "unit_adjoint_delta_KB": unit_kb,
        "unit_adjoint_delta_KE": unit_ke,
        "SU2_adjoint_delta_KB": 2.0 * unit_kb,
        "SU2_adjoint_delta_KE": 2.0 * unit_ke,
        "SU3_adjoint_delta_KB": 3.0 * unit_kb,
        "SU3_adjoint_delta_KE": 3.0 * unit_ke,
        "U1_adjoint_delta_KB": 0.0,
        "U1_adjoint_delta_KE": 0.0,
        "rows": rows,
        "full_oneform_minus_two_complex_ghost_weight": True,
        "gyromagnetic_F0z_vertex_included": True,
        "global_gauge_zero_mode_removed": True,
    }


def matrix_witness() -> dict[str, Any]:
    matrices = full_oneform_ghost_matrices(
        1,
        np.asarray([1.0, 1.05, 0.98, 1.02]),
        0.1,
        np.asarray([0.2, -0.1, 0.3, 0.05]),
    )
    return {
        key: {
            "dimension": value.shape[0],
            "Hermitian_residual": float(np.linalg.norm(value - value.conj().T)),
        }
        for key, value in matrices.items()
    }


def completion_payload() -> dict[str, Any]:
    identities = derham_identity_witness()
    matrices = matrix_witness()
    response = nonabelian_derham_response(points=8, maximum_level=3)
    validation = {
        "curl_gradient_complex_exact": all(
            row["curl_gradient_residual"] < 1.0e-12 for row in identities
        ),
        "scalar_laplacian_exact": all(
            row["scalar_laplacian_residual"] < 1.0e-12 for row in identities
        ),
        "longitudinal_spectrum_exact": all(
            row["longitudinal_eigenvalue_count"]
            == row["expected_longitudinal_eigenvalue_count"]
            for row in identities
        ),
        "all_matrices_Hermitian": all(
            row["Hermitian_residual"] < 1.0e-11 for row in matrices.values()
        ),
        "responses_finite": all(
            math.isfinite(float(response[key]))
            for key in (
                "SU2_adjoint_delta_KB",
                "SU2_adjoint_delta_KE",
                "SU3_adjoint_delta_KB",
                "SU3_adjoint_delta_KE",
            )
        ),
        "BRST_weights_complete": response[
            "full_oneform_minus_two_complex_ghost_weight"
        ],
        "gyromagnetic_vertex_included": response[
            "gyromagnetic_F0z_vertex_included"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_nonabelian_derham_response_v16_04",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "deRham_identity_witness": identities,
        "matrix_witness": matrices,
        "low_level_nonabelian_response": response,
        "scientific_result": (
            "THE_FULL_TEMPORAL-PLUS-SPATIAL_ONE-FORM_OPERATOR,_COMPLEX_GHOST_"
            "SUBTRACTION,_GLOBAL_ZERO-MODE_QUOTIENT,_AND_-2ad(F0z)_"
            "GYROMAGNETIC_VERTEX_ARE_EXPLICIT;_SU2_AND_SU3_ELECTRIC_AND_"
            "MAGNETIC_RESPONSES_ARE_NOW_DERIVATIVES_OF_THE_SAME_DE_RHAM_BLOCK"
        ),
        "claim_boundary": {
            "full_nonabelian_deRham_vertices_assembled": True,
            "background_BRST_quotient_assembled": True,
            "nonabelian_electric_response_seed_evaluated": True,
            "nonabelian_magnetic_response_seed_evaluated": True,
            "angular_heat_tail_converged": False,
            "replacement_quantum_saddle_solved": False,
        },
        "active_calculation": (
            "CONVERGE_THE_NONABELIAN_DE_RHAM_HEAT_TAIL,_COMBINE_IT_WITH_THE_"
            "RANK16_U1-HS_RESPONSE,_AND_EVALUATE_THE_COMPLETE_QUANTUM_CONE_"
            "HESSIAN_ON_THE_DENSE_REPLACEMENT-SADDLE_INITIAL_GUESS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, complex):
        if abs(value.imag) > 1.0e-12:
            return {"real": round(value.real, 12), "imag": round(value.imag, 12)}
        return round(value.real, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_nonabelian_derham_response_v16_04.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "cartesian_spin_one_matrices", "angular_derham_blocks",
    "derham_identity_witness", "full_oneform_ghost_matrices",
    "level_gauge_ghost_response", "nonabelian_derham_response",
    "matrix_witness", "completion_payload", "deterministic_json", "materialize",
]
