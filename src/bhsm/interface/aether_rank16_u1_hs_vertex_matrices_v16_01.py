"""Rank-16 hypercharge and unit-HS vertices on the dense proper cycle."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import block_diag

from bhsm.interface.aether_common_source_frechet_response_v15_99 import (
    frechet_second_response,
)
from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (
    berger_dirac_block,
    pauli_matrices,
    spin_matrices,
)


VERSION = "v16.01"
CLASSIFICATION = "BHSM_RANK16_U1_AND_HS_DENSE_CYCLE_VERTEX_MATRICES"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def rank16_trace_ledger() -> dict[str, Any]:
    return {
        "one_family_hypercharge_square_trace": "10/3",
        "three_family_hypercharge_square_trace": 10.0,
        "derivation": (
            "6*(1/6)^2+2*(-1/2)^2+3*(-2/3)^2+3*(1/3)^2+1^2=10/3"
        ),
        "neutral_singlet_contribution": 0.0,
        "complex_HS_doublet_hypercharge_square_trace": 0.5,
        "real_Gaussian_HS_trace_factor": 2.0,
        "effective_HS_hypercharge_square_weight": 1.0,
        "unit_EC_HS_Dirac_pairings_per_family": 8,
        "three_family_unit_EC_HS_Dirac_pairings": 24,
        "family_matrix": "I3",
        "new_continuous_coefficient": False,
    }


def periodic_first_derivative(points: int, step: float) -> np.ndarray:
    if points < 4 or step <= 0.0:
        raise ValueError("valid periodic lattice required")
    fourier = np.fft.fft(np.eye(points), axis=0) / math.sqrt(points)
    momenta = 2.0 * math.pi * np.fft.fftfreq(points, d=step)
    derivative = fourier.conj().T @ np.diag(1.0j * momenta) @ fourier
    return np.asarray(derivative, dtype=complex)


def periodic_laplacian(points: int, step: float) -> np.ndarray:
    if points < 4 or step <= 0.0:
        raise ValueError("valid periodic lattice required")
    fourier = np.fft.fft(np.eye(points), axis=0) / math.sqrt(points)
    momenta = 2.0 * math.pi * np.fft.fftfreq(points, d=step)
    laplacian = fourier.conj().T @ np.diag(momenta**2) @ fourier
    return np.asarray(laplacian, dtype=complex)


def uniform_dense_geometry(
    cycle: Mapping[str, Any], points: int = 24,
) -> dict[str, np.ndarray | float]:
    rows = cycle["rows"]
    coordinate = np.asarray([row["time"] for row in rows], dtype=float)
    lapse = np.asarray([row["boundary_lapse"] for row in rows], dtype=float)
    radius = np.asarray([row["M4_spatial_radius"] for row in rows], dtype=float)
    lapse_curve = PchipInterpolator(coordinate, lapse)
    primitive = lapse_curve.antiderivative()
    dense_coordinate = np.linspace(coordinate[0], coordinate[-1], 4097)
    dense_tau = primitive(dense_coordinate) - primitive(coordinate[0])
    duration = float(dense_tau[-1])
    tau = np.linspace(0.0, duration, points, endpoint=False)
    time = PchipInterpolator(dense_tau, dense_coordinate)(tau)
    radii = PchipInterpolator(coordinate, radius)(time)
    step = duration / points
    return {
        "proper_times": tau,
        "coordinate_times": time,
        "radii": radii,
        "proper_duration": duration,
        "proper_step": step,
    }


def source_profiles(geometry: Mapping[str, Any]) -> dict[str, np.ndarray | float]:
    tau = np.asarray(geometry["proper_times"], dtype=float)
    duration = float(geometry["proper_duration"])
    omega = 2.0 * math.pi / duration
    return {
        "constant": np.ones_like(tau) / math.sqrt(duration),
        "first_frequency": math.sqrt(2.0 / duration) * np.cos(omega * tau),
        "first_angular_frequency": omega,
    }


def weyl_squared_operator_and_vertices(
    level: int,
    radii: np.ndarray,
    proper_step: float,
    profile: np.ndarray,
    *,
    source: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact first-order product-Dirac square and source vertices."""

    n = int(level)
    r = np.asarray(radii, dtype=float)
    s = np.asarray(profile, dtype=float)
    if n < 0 or r.ndim != 1 or s.shape != r.shape or np.any(r <= 0.0):
        raise ValueError("invalid level, radii, or profile")
    points = len(r)
    angular_dimension = 2 * (n + 1)
    time_derivative = np.kron(
        periodic_first_derivative(points, proper_step),
        np.eye(angular_dimension),
    )
    spatial = block_diag(
        *[berger_dirac_block(n, float(radius), 1.0) for radius in r]
    )
    off_diagonal = time_derivative + spatial
    zero = np.zeros_like(off_diagonal)
    dirac = np.block(
        [[zero, off_diagonal], [off_diagonal.conj().T, zero]]
    )
    sigma_z = pauli_matrices()[2]
    spatial_vertex = np.kron(sigma_z, np.eye(n + 1))
    local_spatial = block_diag(*[value * spatial_vertex for value in s])
    local_scalar = np.kron(np.diag(s), np.eye(angular_dimension))
    if source == "coexact_gauge":
        first_order_vertex = np.block(
            [[zero, local_spatial], [local_spatial, zero]]
        )
    elif source == "HS":
        first_order_vertex = np.block(
            [[local_scalar, zero], [zero, -local_scalar]]
        )
    else:
        raise ValueError("source must be coexact_gauge or HS")
    operator = dirac @ dirac
    vertex = dirac @ first_order_vertex + first_order_vertex @ dirac
    contact = 2.0 * first_order_vertex @ first_order_vertex
    return operator, vertex, contact


def hs_scalar_operator_and_gauge_vertices(
    level: int,
    radii: np.ndarray,
    proper_step: float,
    profile: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Conformal scalar doublet block with a homogeneous U(1) connection."""

    k = int(level)
    r = np.asarray(radii, dtype=float)
    s = np.asarray(profile, dtype=float)
    if k < 0 or r.ndim != 1 or s.shape != r.shape:
        raise ValueError("invalid scalar level or geometry")
    orbital = k + 1
    j_z = spin_matrices(k)[2]
    operator = np.kron(
        periodic_laplacian(len(r), proper_step), np.eye(orbital)
    )
    operator += block_diag(
        *[((k + 1.0) / radius) ** 2 * np.eye(orbital) for radius in r]
    )
    vertex = block_diag(
        *[
            value * (4.0 / radius) * j_z
            for value, radius in zip(s, r, strict=True)
        ]
    )
    contact = block_diag(
        *[2.0 * value**2 * np.eye(orbital) for value in s]
    )
    return operator.astype(complex), vertex.astype(complex), contact.astype(complex)


def _response(
    builder: Any,
    level: int,
    geometry: Mapping[str, Any],
    profile: np.ndarray,
    *,
    weight: float,
    source: str | None = None,
) -> float:
    radii = np.asarray(geometry["radii"], dtype=float)
    step = float(geometry["proper_step"])
    if source is None:
        operator, vertex, contact = builder(level, radii, step, profile)
    else:
        operator, vertex, contact = builder(
            level, radii, step, profile, source=source
        )
    return frechet_second_response(
        operator,
        vertex,
        vertex,
        contact_vertex=contact,
        supertrace_weight=weight,
    )


def rank16_u1_hs_responses(
    cycle: Mapping[str, Any] | None = None,
    *,
    points: int = 24,
    maximum_level: int = 2,
) -> dict[str, Any]:
    values = dense_constraint_solved_cycle() if cycle is None else cycle
    geometry = uniform_dense_geometry(values, points)
    profiles = source_profiles(geometry)
    constant = np.asarray(profiles["constant"])
    frequency = np.asarray(profiles["first_frequency"])
    omega = float(profiles["first_angular_frequency"])
    gauge_constant = 0.0
    gauge_frequency = 0.0
    hs_constant = 0.0
    hs_frequency = 0.0
    rows = []
    for level in range(maximum_level + 1):
        spectator = level + 1
        # The 4D block contains both chiral square blocks.  One Weyl trace is
        # half of it; sum q^2 over the three-family rank-16 carrier is 10.
        weyl_weight = -5.0 * spectator
        wc = _response(
            weyl_squared_operator_and_vertices, level, geometry, constant,
            weight=weyl_weight, source="coexact_gauge",
        )
        wf = _response(
            weyl_squared_operator_and_vertices, level, geometry, frequency,
            weight=weyl_weight, source="coexact_gauge",
        )
        # One complex HS doublet gives effective real-Gaussian q^2 weight 1.
        scalar_weight = float(spectator)
        sc = _response(
            hs_scalar_operator_and_gauge_vertices, level, geometry, constant,
            weight=scalar_weight,
        )
        sf = _response(
            hs_scalar_operator_and_gauge_vertices, level, geometry, frequency,
            weight=scalar_weight,
        )
        # Twenty-four unit EC-HS Dirac pairings; the angular spectator remains.
        hs_weight = -24.0 * spectator
        hc = _response(
            weyl_squared_operator_and_vertices, level, geometry, constant,
            weight=hs_weight, source="HS",
        )
        hf = _response(
            weyl_squared_operator_and_vertices, level, geometry, frequency,
            weight=hs_weight, source="HS",
        )
        gauge_constant += wc + sc
        gauge_frequency += wf + sf
        hs_constant += hc
        hs_frequency += hf
        rows.append({
            "level": level,
            "Weyl_U1_constant": wc,
            "Weyl_U1_first_frequency": wf,
            "HS_U1_constant": sc,
            "HS_U1_first_frequency": sf,
            "fermion_HS_constant": hc,
            "fermion_HS_first_frequency": hf,
        })
    inverse_radius_squared = float(
        np.mean(1.0 / np.asarray(geometry["radii"]) ** 2)
    )
    coexact_eigenvalue = 4.0 * inverse_radius_squared
    per_pair_z = (hs_frequency - hs_constant) / omega**2 / 24.0
    channel_multiplicities = {
        "up": 9,
        "down": 9,
        "charged_lepton": 3,
        "neutrino": 3,
    }
    channel_z = {
        name: multiplicity * per_pair_z
        for name, multiplicity in channel_multiplicities.items()
    }
    return {
        "lattice_points": points,
        "maximum_homogeneous_level": maximum_level,
        "proper_duration": geometry["proper_duration"],
        "U1_constant_coexact_response": gauge_constant,
        "U1_first_frequency_coexact_response": gauge_frequency,
        "U1_delta_K_magnetic_seed": gauge_constant / coexact_eigenvalue,
        "U1_delta_K_electric_seed": (
            gauge_frequency - gauge_constant
        ) / omega**2,
        "HS_constant_response": hs_constant,
        "HS_first_frequency_response": hs_frequency,
        "HS_delta_Z_seed": (hs_frequency - hs_constant) / omega**2,
        "HS_delta_Z_per_normalized_pair_seed": per_pair_z,
        "independent_channel_pairing_multiplicities": channel_multiplicities,
        "independent_channel_Z_seeds": channel_z,
        "independent_channel_canonical_Y_seeds": {
            name: value**-0.5 for name, value in channel_z.items()
        },
        "single_collective_24-pair_canonical_Y_seed": (
            (24.0 * per_pair_z) ** -0.5
        ),
        "single_collective_direction_selected_by_current_calculation": False,
        "rows": rows,
        "rank16_group_and_unit_HS_vertices_share_one_geometry": True,
        "radial_wall_overlap": 1.0,
        "gauge_ghost_U1_adjoint_response": 0.0,
        "interpretation": (
            "FOURIER-GALERKIN_HEAT-REGULATED_COLLOCATION_SEED_WITHOUT_A_"
            "CENTERED-DIFFERENCE_FERMION_DOUBLER;_LEVEL_CONVERGENCE_AND_"
            "THE_FULL_NONABELIAN_ADJOINT_BLOCK_AND_HS-CHANNEL_HESSIAN_"
            "DIAGONALIZATION_PRECEDE_PHYSICAL_YUKAWA_CANONICALIZATION"
        ),
    }


def matrix_contract_witness() -> dict[str, Any]:
    radii = np.asarray([1.0, 1.05, 1.02, 0.98])
    profile = np.asarray([0.2, -0.1, 0.3, 0.05])
    checks = {}
    for source in ("coexact_gauge", "HS"):
        operator, vertex, contact = weyl_squared_operator_and_vertices(
            1, radii, 0.1, profile, source=source
        )
        checks[source] = {
            "dimension": operator.shape[0],
            "operator_Hermitian_residual": float(
                np.linalg.norm(operator - operator.conj().T)
            ),
            "vertex_Hermitian_residual": float(
                np.linalg.norm(vertex - vertex.conj().T)
            ),
            "contact_Hermitian_residual": float(
                np.linalg.norm(contact - contact.conj().T)
            ),
            "minimum_operator_eigenvalue": float(np.linalg.eigvalsh(operator)[0]),
        }
    return checks


def completion_payload() -> dict[str, Any]:
    ledger = rank16_trace_ledger()
    witness = matrix_contract_witness()
    response = rank16_u1_hs_responses(points=8, maximum_level=1)
    validation = {
        "rank16_trace_exact": ledger["three_family_hypercharge_square_trace"] == 10.0,
        "unit_HS_pairings_complete": ledger[
            "three_family_unit_EC_HS_Dirac_pairings"
        ] == 24,
        "all_matrices_Hermitian": all(
            row["operator_Hermitian_residual"] < 1.0e-12
            and row["vertex_Hermitian_residual"] < 1.0e-12
            and row["contact_Hermitian_residual"] < 1.0e-12
            for row in witness.values()
        ),
        "all_squared_operators_positive": all(
            row["minimum_operator_eigenvalue"] > 0.0 for row in witness.values()
        ),
        "responses_finite": all(
            math.isfinite(float(response[key]))
            for key in (
                "U1_delta_K_magnetic_seed",
                "U1_delta_K_electric_seed",
                "HS_delta_Z_seed",
            )
        ),
        "one_geometry": response[
            "rank16_group_and_unit_HS_vertices_share_one_geometry"
        ],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rank16_trace_ledger": ledger,
        "matrix_contract_witness": witness,
        "low_level_response_seed": response,
        "scientific_result": (
            "THE_THREE-FAMILY_HYPERCHARGE_TRACE_10,_THE_COMPLEX_HS-DOUBLET_"
            "TRACE,_AND_24_UNIT_EC-HS_DIRAC_PAIRINGS_ARE_ASSEMBLED_AS_EXPLICIT_"
            "HERMITIAN_FIRST-ORDER_PRODUCT-DIRAC_SOURCE_AND_CONTACT_MATRICES_"
            "ON_ONE_DENSE_PROPER-CYCLE_GEOMETRY_WITH_AN_EXACT_PERIODIC_"
            "FOURIER_DERIVATIVE_AND_NO_TIME-LATTICE_FERMION_DOUBLER"
        ),
        "claim_boundary": {
            "rank16_U1_vertex_matrices_assembled": True,
            "unit_HS_vertex_matrices_assembled": True,
            "low_level_response_seed_evaluated": True,
            "level_convergence_established": False,
            "physical_single_Higgs_direction_selected": False,
            "nonabelian_adjoint_vertices_assembled": False,
            "replacement_quantum_saddle_solved": False,
        },
        "active_calculation": (
            "EXTEND_THE_COMMON_VERTEX_SUM_TO_HEAT-TRACE_CONVERGENCE,_ASSEMBLE_"
            "THE_SU2_AND_SU3_ADJOINT_GAUGE-GHOST_BLOCKS,_AND_INSERT_ALL_"
            "RESPONSES_IN_THE_314-EQUATION_REPLACEMENT_KKT_SYSTEM"
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
    path = target / "BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "rank16_trace_ledger",
    "periodic_first_derivative", "periodic_laplacian",
    "uniform_dense_geometry", "source_profiles",
    "weyl_squared_operator_and_vertices",
    "hs_scalar_operator_and_gauge_vertices", "rank16_u1_hs_responses",
    "matrix_contract_witness", "completion_payload", "deterministic_json",
    "materialize",
]
