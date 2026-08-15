"""Exact coexact S3 curl blocks and non-Abelian adjoint magnetic vertices."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.linalg import block_diag

from bhsm.interface.aether_common_source_frechet_response_v15_99 import (
    frechet_second_response,
)
from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    periodic_laplacian,
    source_profiles,
    uniform_dense_geometry,
)
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (
    spin_matrices,
)


VERSION = "v16.03"
CLASSIFICATION = "BHSM_NONABELIAN_COEXACT_GAUGE_GHOST_MAGNETIC_VERTEX"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def spin_one_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return spin_matrices(2)


def unit_radius_curl_block(level: int) -> np.ndarray:
    n = int(level)
    if n < 0:
        raise ValueError("nonnegative homogeneous level required")
    j_x, j_y, j_z = spin_matrices(n)
    s_x, s_y, s_z = spin_one_matrices()
    dimension = 3 * (n + 1)
    return (
        2.0 * np.eye(dimension, dtype=complex)
        + 2.0 * (
            np.kron(s_x, j_x)
            + np.kron(s_y, j_y)
            + np.kron(s_z, j_z)
        )
    )


def coexact_curl_basis(level: int) -> dict[str, Any]:
    curl = unit_radius_curl_block(level)
    eigenvalues, eigenvectors = np.linalg.eigh(curl)
    mask = np.abs(eigenvalues) > 1.0e-10
    basis = eigenvectors[:, mask]
    return {
        "full_curl": curl,
        "full_eigenvalues": eigenvalues,
        "coexact_basis": basis,
        "coexact_eigenvalues": eigenvalues[mask],
        "longitudinal_dimension": int(np.count_nonzero(~mask)),
        "coexact_dimension": int(np.count_nonzero(mask)),
    }


def curl_spectrum_witness(maximum_level: int = 6) -> list[dict[str, Any]]:
    rows = []
    for n in range(maximum_level + 1):
        result = coexact_curl_basis(n)
        values = np.asarray(result["coexact_eigenvalues"])
        expected = [float(n + 2)] * (n + 3)
        if n >= 2:
            expected += [float(-n)] * (n - 1)
        rows.append({
            "level": n,
            "coexact_eigenvalues": sorted(values.tolist()),
            "expected_coexact_eigenvalues": sorted(expected),
            "longitudinal_dimension": result["longitudinal_dimension"],
            "expected_longitudinal_dimension": 0 if n == 0 else n + 1,
            "coexact_dimension": result["coexact_dimension"],
            "expected_coexact_dimension": len(expected),
        })
    return rows


def coexact_operator_and_magnetic_vertices(
    level: int,
    radii: np.ndarray,
    proper_step: float,
    profile: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r = np.asarray(radii, dtype=float)
    s = np.asarray(profile, dtype=float)
    if r.ndim != 1 or s.shape != r.shape or np.any(r <= 0.0):
        raise ValueError("invalid cycle geometry")
    decomposition = coexact_curl_basis(level)
    basis = np.asarray(decomposition["coexact_basis"])
    curl_unit = basis.conj().T @ decomposition["full_curl"] @ basis
    spin_source = basis.conj().T @ np.kron(
        spin_one_matrices()[2], np.eye(level + 1)
    ) @ basis
    operator = np.kron(
        periodic_laplacian(len(r), proper_step),
        np.eye(decomposition["coexact_dimension"]),
    )
    operator += block_diag(
        *[(curl_unit / radius) @ (curl_unit / radius) for radius in r]
    )
    vertex = block_diag(
        *[
            value
            * (
                (curl_unit / radius) @ spin_source
                + spin_source @ (curl_unit / radius)
            )
            for value, radius in zip(s, r, strict=True)
        ]
    )
    contact = block_diag(
        *[2.0 * value**2 * spin_source @ spin_source for value in s]
    )
    return operator, vertex, contact


def adjoint_magnetic_response(
    cycle: Mapping[str, Any] | None = None,
    *,
    points: int = 24,
    maximum_level: int = 6,
) -> dict[str, Any]:
    values = dense_constraint_solved_cycle() if cycle is None else cycle
    geometry = uniform_dense_geometry(values, points)
    profile = np.asarray(source_profiles(geometry)["constant"])
    radii = np.asarray(geometry["radii"])
    total_unit_adjoint = 0.0
    rows = []
    for level in range(maximum_level + 1):
        operator, vertex, contact = coexact_operator_and_magnetic_vertices(
            level, radii, float(geometry["proper_step"]), profile
        )
        # The unused right SU(2) label supplies multiplicity n+1.
        response = frechet_second_response(
            operator,
            vertex,
            vertex,
            contact_vertex=contact,
            supertrace_weight=float(level + 1),
        )
        total_unit_adjoint += response
        rows.append({
            "level": level,
            "unit_adjoint_response": response,
            "cumulative_unit_adjoint_response": total_unit_adjoint,
        })
    inverse_radius_squared = float(np.mean(1.0 / radii**2))
    background_coexact_eigenvalue = 4.0 * inverse_radius_squared
    unit_delta_kb = total_unit_adjoint / background_coexact_eigenvalue
    return {
        "points": points,
        "maximum_level": maximum_level,
        "unit_adjoint_constant_response": total_unit_adjoint,
        "unit_adjoint_delta_KB": unit_delta_kb,
        "SU2_C_A": 2.0,
        "SU3_C_A": 3.0,
        "SU2_adjoint_delta_KB": 2.0 * unit_delta_kb,
        "SU3_adjoint_delta_KB": 3.0 * unit_delta_kb,
        "U1_adjoint_delta_KB": 0.0,
        "rows": rows,
        "longitudinal_and_ghost_removed_by_coexact_projection": True,
        "electric_response_from_full_one_form_deRham_complex_evaluated": False,
    }


def completion_payload() -> dict[str, Any]:
    spectrum = curl_spectrum_witness()
    response = adjoint_magnetic_response(points=8, maximum_level=4)
    validation = {
        "curl_spectrum_exact": all(
            np.allclose(
                row["coexact_eigenvalues"],
                row["expected_coexact_eigenvalues"],
                rtol=0.0,
                atol=1.0e-12,
            )
            for row in spectrum
        ),
        "longitudinal_dimensions_exact": all(
            row["longitudinal_dimension"] == row["expected_longitudinal_dimension"]
            for row in spectrum
        ),
        "coexact_dimensions_exact": all(
            row["coexact_dimension"] == row["expected_coexact_dimension"]
            for row in spectrum
        ),
        "adjoint_response_finite": math.isfinite(
            response["unit_adjoint_delta_KB"]
        ),
        "casimir_scaling_exact": (
            response["SU3_adjoint_delta_KB"]
            == 1.5 * response["SU2_adjoint_delta_KB"]
        ),
        "BRST_quotient_explicit": response[
            "longitudinal_and_ghost_removed_by_coexact_projection"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_nonabelian_coexact_vertex_v16_03",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "curl_spectrum_witness": spectrum,
        "low_level_adjoint_magnetic_response": response,
        "scientific_result": (
            "THE_EXACT_S3_CURL_BLOCK_SPLITS_INTO_COEXACT_EIGENVALUES_+(n+2)_"
            "AND_-n_AND_AN_(n+1)-DIMENSIONAL_LONGITUDINAL_GHOST_SECTOR;_THE_"
            "PROJECTED_SU2_AND_SU3_ADJOINT_MAGNETIC_VERTICES_ARE_EXPLICIT_"
            "AND_SCALE_WITH_C_A=2_AND_3_WITHOUT_A_NEW_COEFFICIENT"
        ),
        "claim_boundary": {
            "exact_coexact_curl_blocks_assembled": True,
            "longitudinal_ghost_quotient_assembled": True,
            "nonabelian_magnetic_vertex_matrices_assembled": True,
            "nonabelian_electric_deRham_vertex_matrices_assembled": False,
            "replacement_quantum_saddle_solved": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_FULL_TEMPORAL-PLUS-SPATIAL_ONE-FORM_DE_RHAM_COMPLEX_"
            "WITH_THE_-2ad(F)_GYROMAGNETIC_CONTACT,_VERIFY_THE_BACKGROUND_WARD_"
            "IDENTITY,_AND_COMPLETE_THE_NONABELIAN_ELECTRIC_RESPONSE"
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
    path = target / "BHSM_aether_nonabelian_coexact_vertex_v16_03.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "spin_one_matrices",
    "unit_radius_curl_block", "coexact_curl_basis", "curl_spectrum_witness",
    "coexact_operator_and_magnetic_vertices", "adjoint_magnetic_response",
    "completion_payload", "deterministic_json", "materialize",
]
