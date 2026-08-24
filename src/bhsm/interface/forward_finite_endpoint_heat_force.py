"""Exact first variation of the retained finite-endpoint heat functional.

The routines in this module are domain agnostic: the caller supplies the
positive self-adjoint finite-endpoint operator and its action-derived
geometry jets.  No temporal graph, endpoint condition, reset-fiber member,
or periodic continuation is selected here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from typing import Any

import numpy as np
from scipy.special import exp1


def _hermitian(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=complex)
    if (
        matrix.ndim != 2
        or matrix.shape[0] != matrix.shape[1]
        or not np.all(np.isfinite(matrix))
    ):
        raise ValueError(f"{name} must be a finite square matrix")
    if not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=1.0e-11):
        raise ValueError(f"{name} must be Hermitian")
    return 0.5 * (matrix + matrix.conj().T)


def heat_regulator_value_and_force(
    operator: np.ndarray,
    geometry_jets: Mapping[str, np.ndarray],
    *,
    heat_length: float = 1.0,
    gap_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Evaluate Gamma and D Gamma for ``f(P)=-E1(ell^2 P)/2``.

    For a positive self-adjoint matrix ``P`` and any Hermitian action-owned
    first variation ``dP``, cyclicity of the trace gives the exact identity

        D Tr f(P)[dP] = Tr(f'(P)dP),
        f'(P) = exp(-ell^2 P)/(2P).

    The identity remains valid when ``P`` and ``dP`` do not commute.
    """

    if not math.isfinite(heat_length) or heat_length <= 0.0:
        raise ValueError("heat_length must be positive and finite")
    if not math.isfinite(gap_tolerance) or gap_tolerance < 0.0:
        raise ValueError("gap_tolerance must be finite and nonnegative")
    matrix = _hermitian(operator, "operator")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    gap = float(eigenvalues[0])
    if gap <= gap_tolerance:
        raise ValueError("strictly positive quotient operator required")
    scaled = heat_length**2 * eigenvalues
    regulator = -0.5 * exp1(scaled)
    derivative_values = 0.5 * np.exp(-scaled) / eigenvalues
    gradient = (eigenvectors * derivative_values) @ eigenvectors.conj().T
    forces: dict[str, float] = {}
    for name, value in geometry_jets.items():
        jet = _hermitian(value, f"geometry jet {name}")
        if jet.shape != matrix.shape:
            raise ValueError("every geometry jet must match the operator")
        force = np.trace(gradient @ jet)
        if abs(float(force.imag)) > 1.0e-9 * max(1.0, abs(float(force.real))):
            raise ValueError("Hermitian force acquired a nonreal trace")
        forces[str(name)] = float(force.real)
    return {
        "Gamma_heat": float(np.sum(regulator)),
        "minimum_eigenvalue": gap,
        "dimension": int(matrix.shape[0]),
        "forces": forces,
        "gradient": gradient,
    }


def direct_sum_heat_value_and_force(
    blocks: Sequence[Mapping[str, Any]],
    *,
    heat_length: float = 1.0,
    gap_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Assemble a signed/multiplicity-weighted direct-sum heat force."""

    total_value = 0.0
    total_forces: dict[str, float] = {}
    rows = []
    for index, block in enumerate(blocks):
        coefficient = float(block.get("coefficient", 1.0))
        if not math.isfinite(coefficient):
            raise ValueError("direct-sum coefficient must be finite")
        result = heat_regulator_value_and_force(
            np.asarray(block["operator"]),
            block["geometry_jets"],
            heat_length=heat_length,
            gap_tolerance=gap_tolerance,
        )
        total_value += coefficient * result["Gamma_heat"]
        for name, value in result["forces"].items():
            total_forces[name] = total_forces.get(name, 0.0) + coefficient * value
        rows.append({
            "index": index,
            "coefficient": coefficient,
            "dimension": result["dimension"],
            "minimum_eigenvalue": result["minimum_eigenvalue"],
        })
    return {
        "Gamma_heat": total_value,
        "forces": total_forces,
        "blocks": rows,
    }


def zeta_casimir_value_and_force(
    radii: np.ndarray,
    measure_weights: np.ndarray,
    log_radius_directions: Mapping[str, np.ndarray],
    *,
    coefficient: float = 59.0 / 30.0,
) -> dict[str, Any]:
    """Evaluate the retained local zeta/Casimir term and its radius force.

    ``Gamma_SM_zeta=-c*sum_j w_j/R_j`` and therefore
    ``D Gamma_SM_zeta[h]=c*sum_j w_j*h_j/R_j`` for ``delta log R=h``.
    The weights are supplied by the action-owned proper-time quadrature.
    """

    r = np.asarray(radii, dtype=float)
    weights = np.asarray(measure_weights, dtype=float)
    if (
        r.ndim != 1
        or weights.shape != r.shape
        or np.any(r <= 0.0)
        or not np.all(np.isfinite(r))
        or not np.all(np.isfinite(weights))
    ):
        raise ValueError("finite positive radii and matching finite weights required")
    if not math.isfinite(coefficient):
        raise ValueError("zeta coefficient must be finite")
    density = coefficient * weights / r
    forces: dict[str, float] = {}
    for name, value in log_radius_directions.items():
        direction = np.asarray(value, dtype=float)
        if direction.shape != r.shape or not np.all(np.isfinite(direction)):
            raise ValueError("every log-radius direction must match the radii")
        forces[str(name)] = float(density @ direction)
    return {
        "Gamma_SM_zeta": float(-np.sum(density)),
        "forces": forces,
        "coefficient": float(coefficient),
    }


def replacement_heat_minus_zeta_force(
    heat: Mapping[str, Any], zeta: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the replacement correction ``Gamma_heat-Gamma_SM_zeta``."""

    heat_forces = {str(k): float(v) for k, v in heat["forces"].items()}
    zeta_forces = {str(k): float(v) for k, v in zeta["forces"].items()}
    if set(heat_forces) != set(zeta_forces):
        raise ValueError("heat and zeta force directions must agree")
    return {
        "Gamma_heat_minus_zeta": float(heat["Gamma_heat"])
        - float(zeta["Gamma_SM_zeta"]),
        "forces": {
            name: heat_forces[name] - zeta_forces[name]
            for name in heat_forces
        },
    }


__all__ = [
    "heat_regulator_value_and_force",
    "direct_sum_heat_value_and_force",
    "zeta_casimir_value_and_force",
    "replacement_heat_minus_zeta_force",
]
