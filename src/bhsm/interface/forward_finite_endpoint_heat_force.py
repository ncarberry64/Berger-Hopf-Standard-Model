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


def common_scale_heat_value_and_force(
    blocks: Sequence[Mapping[str, Any]],
    *,
    heat_length: float = 1.0,
    gap_tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Evaluate the exact common-scale Ward derivative of the heat sum.

    On the normalized proper-time domain the simultaneous physical scaling
    ``R -> exp(a) R`` and ``d tau -> exp(a) d tau`` gives
    ``P(a)=exp(-2a)P``.  With the retained parent heat length fixed,

        d/da[-STr E1(ell^2 P(a))/2] = -STr exp(-ell^2 P).

    ``coefficient`` on each block carries its existing supertrace sign and
    multiplicity.
    """

    if not math.isfinite(heat_length) or heat_length <= 0.0:
        raise ValueError("heat_length must be positive and finite")
    if not math.isfinite(gap_tolerance) or gap_tolerance < 0.0:
        raise ValueError("gap_tolerance must be finite and nonnegative")
    total_value = 0.0
    total_force = 0.0
    rows = []
    for index, block in enumerate(blocks):
        coefficient = float(block.get("coefficient", 1.0))
        if not math.isfinite(coefficient):
            raise ValueError("direct-sum coefficient must be finite")
        matrix = _hermitian(np.asarray(block["operator"]), f"operator {index}")
        eigenvalues = np.linalg.eigvalsh(matrix)
        gap = float(eigenvalues[0])
        if gap <= gap_tolerance:
            raise ValueError("strictly positive quotient operator required")
        scaled = heat_length**2 * eigenvalues
        value = float(np.sum(-0.5 * exp1(scaled)))
        force = float(-np.sum(np.exp(-scaled)))
        total_value += coefficient * value
        total_force += coefficient * force
        rows.append({
            "index": index,
            "coefficient": coefficient,
            "dimension": int(matrix.shape[0]),
            "minimum_eigenvalue": gap,
            "common_scale_heat_force": coefficient * force,
        })
    return {
        "Gamma_heat": total_value,
        "common_scale_heat_force": total_force,
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


def common_scale_zeta_value_and_force(
    radii: np.ndarray,
    measure_weights: np.ndarray,
    *,
    coefficient: float = 59.0 / 30.0,
) -> dict[str, Any]:
    """Evaluate the zeta term and its simultaneous radius/measure scale force.

    Since ``Gamma_SM_zeta=-c*sum(w_j/R_j)``, scaling both the proper-time
    weights and radii by ``exp(a)`` leaves the action term invariant.  This is
    the moving-duration completion of the fixed-measure radius derivative.
    """

    base = zeta_casimir_value_and_force(
        radii, measure_weights, {}, coefficient=coefficient
    )
    return {
        "Gamma_SM_zeta": base["Gamma_SM_zeta"],
        "common_scale_zeta_force": 0.0,
        "coefficient": float(coefficient),
    }


def finite_core_heat_trace_log_upper_bound(
    *,
    dimension: int,
    proper_duration_upper: float,
    heat_length: float = 1.0,
    scalar_potential_lower: float = 0.0,
    factorization_coefficient_upper: float | None = None,
) -> dict[str, Any]:
    """Bound a mixed-boundary finite-core heat trace without inversion.

    A piecewise-linear form-core vector vanishes at the artificial far edge
    and is free at the retained birth edge.  The sharp one-sided Poincare
    inequality therefore gives ``||u'|| >= pi ||u||/(2T)``.  For a scalar
    Schrodinger form this adds to a supplied nonnegative potential lower
    bound.  For a factorized form ``||u' + W u||^2``, the reverse triangle
    inequality gives ``(pi/(2T)-||W||_infinity)_+^2``.

    The result is returned primarily in log space because the BHSM C2 cores
    can make the certified bound far smaller than binary64 can represent.
    No generalized mass matrix or kinetic/Dirac block is inverted.
    """

    size = int(dimension)
    duration = float(proper_duration_upper)
    ell = float(heat_length)
    potential = float(scalar_potential_lower)
    if size < 1:
        raise ValueError("dimension must be a positive integer")
    if not math.isfinite(duration) or duration <= 0.0:
        raise ValueError("proper_duration_upper must be positive and finite")
    if not math.isfinite(ell) or ell <= 0.0:
        raise ValueError("heat_length must be positive and finite")
    if not math.isfinite(potential) or potential < 0.0:
        raise ValueError("scalar_potential_lower must be finite and nonnegative")

    poincare_rate = math.pi / (2.0 * duration)
    if factorization_coefficient_upper is None:
        gap_lower = poincare_rate**2 + potential
        form_class = "SCALAR_SCHRODINGER"
        coefficient_upper = None
    else:
        coefficient_upper = float(factorization_coefficient_upper)
        if not math.isfinite(coefficient_upper) or coefficient_upper < 0.0:
            raise ValueError(
                "factorization_coefficient_upper must be finite and nonnegative"
            )
        gap_lower = max(0.0, poincare_rate - coefficient_upper) ** 2
        form_class = "FIRST_ORDER_FACTORIZATION"

    log_upper = math.log(size) - ell**2 * gap_lower
    log10_upper = log_upper / math.log(10.0)
    exponential_exponent = -ell**2 * gap_lower
    return {
        "form_class": form_class,
        "dimension": size,
        "proper_duration_upper": duration,
        "heat_length": ell,
        "poincare_rate_lower": poincare_rate,
        "scalar_potential_lower": potential,
        "factorization_coefficient_upper": coefficient_upper,
        "generalized_gap_lower": gap_lower,
        "heat_trace_upper_bound_prefactor": size,
        "heat_trace_upper_bound_exponent": exponential_exponent,
        "heat_trace_upper_bound_expression": (
            f"{size}*exp({exponential_exponent:.17e})"
        ),
        "log_heat_trace_upper_bound": log_upper,
        "log10_heat_trace_upper_bound": log10_upper,
        "upper_bound_underflows_binary64": log_upper < math.log(np.finfo(float).tiny),
        "explicit_matrix_inverse_formed": False,
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
    "common_scale_heat_value_and_force",
    "zeta_casimir_value_and_force",
    "common_scale_zeta_value_and_force",
    "finite_core_heat_trace_log_upper_bound",
    "replacement_heat_minus_zeta_force",
]
