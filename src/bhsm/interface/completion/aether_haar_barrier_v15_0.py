"""BHSM v15.0 Haar-barrier theorem for the regular support stratum."""
from __future__ import annotations

from decimal import Decimal, localcontext
import math
from typing import Any


def support_depth(upsilon: float, lambda_d: float = 1.0) -> float:
    """Return q_D=-lambda_D log(upsilon) on the regular domain (0,1]."""
    u, scale = float(upsilon), float(lambda_d)
    if not (0.0 < u <= 1.0):
        raise ValueError("upsilon is defined only on the regular domain (0,1]")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("lambda_d must be positive and finite")
    return -scale * math.log(u)


def haar_distance(upsilon_a: float, upsilon_b: float, lambda_d: float = 1.0) -> float:
    """Exact one-dimensional geodesic distance for ds^2=lambda_D^2 du^2/u^2."""
    return abs(support_depth(upsilon_a, lambda_d) - support_depth(upsilon_b, lambda_d))


def decimal_haar_distance_to_one(exponent: int, lambda_d: str = "1") -> Decimal:
    """High-precision distance from upsilon=10^-exponent to upsilon=1."""
    n = int(exponent)
    if n < 0:
        raise ValueError("exponent must be nonnegative")
    with localcontext() as context:
        context.prec = 80
        return Decimal(lambda_d) * Decimal(n) * Decimal(10).ln()


def compact_depth_coordinate(upsilon: float, lambda_d: float = 1.0) -> float:
    """A bounded plotting coordinate z=q_D/(lambda_D+q_D), never a new metric."""
    q = support_depth(upsilon, lambda_d)
    return q / (float(lambda_d) + q)


def compact_coordinate_distance_to_one(z: float, lambda_d: float = 1.0) -> float:
    """Physical distance represented by z; it diverges as z approaches 1."""
    zz, scale = float(z), float(lambda_d)
    if not (0.0 <= zz < 1.0):
        raise ValueError("z must lie in [0,1)")
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("lambda_d must be positive and finite")
    return scale * zz / (1.0 - zz)


def finite_action_length_bound(duration: float, kinetic_action: float) -> float:
    """Cauchy--Schwarz bound L <= sqrt(Delta*squared-speed integral)."""
    delta, action = float(duration), float(kinetic_action)
    if not math.isfinite(delta) or delta <= 0.0:
        raise ValueError("duration must be positive and finite")
    if not math.isfinite(action) or action < 0.0:
        raise ValueError("kinetic_action must be finite and nonnegative")
    return math.sqrt(delta * action)


def haar_barrier_payload() -> dict[str, Any]:
    exponents = (1, 2, 4, 8, 16, 32)
    distances = [str(decimal_haar_distance_to_one(n)) for n in exponents]
    compact_deltas = (0.5, 0.25, 0.125, 0.0625)
    return {
        "version": "v15.0",
        "theorem": "HAAR_BARRIER_THEOREM",
        "support_depth": "q_D=-lambda_D*log(upsilon)",
        "metric": "ds_D^2=lambda_D^2*dupsilon^2/upsilon^2",
        "regular_domain": "0<upsilon<=1",
        "distance_formula": "d(u,v)=lambda_D*abs(log(u/v))",
        "distance_to_endpoint": "infinite",
        "metric_completion_contains_upsilon_zero_at_finite_distance": False,
        "high_precision_witness": {"exponents": list(exponents), "distances_to_one": distances},
        "bounded_coordinate": "z=q_D/(lambda_D+q_D)",
        "bounded_coordinate_limit": 1.0,
        "physical_distances_at_z=1-delta": [
            compact_coordinate_distance_to_one(1.0 - delta) for delta in compact_deltas
        ],
        "coordinate_compactification_changes_physical_distance": False,
        "proof": (
            "Every smooth reparameterization pulls back the same line element; its length integral "
            "is invariant. A bounded chart can place the ideal endpoint at a finite coordinate value "
            "but the pulled-back metric coefficient remains nonintegrable there."
        ),
        "finite_event_regular_trajectory_gate": (
            "For finite exterior duration and finite regular Haar kinetic action, Cauchy--Schwarz "
            "bounds path length by a finite number; the infinite-distance endpoint cannot be reached."
        ),
        "option_A_finite_accessibility": False,
        "new_parameter_introduced": False,
    }
