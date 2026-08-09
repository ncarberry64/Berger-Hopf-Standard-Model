"""Relational process, clock calibration, and conditional energy theorem."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any


@dataclass(frozen=True)
class Process:
    source: str
    target: str
    depth: Fraction

    def __post_init__(self) -> None:
        if self.depth < 0:
            raise ValueError("process depth must be nonnegative")

    def then(self, other: "Process") -> "Process":
        if self.target != other.source:
            raise ValueError("processes are not composable")
        return Process(self.source, other.target, self.depth + other.depth)


def clock_ratio(process: Process, reference_cycle_depth: Fraction) -> Fraction:
    if reference_cycle_depth <= 0:
        raise ValueError("reference cycle depth must be positive")
    return process.depth / reference_cycle_depth


def clocked_energy(generator_eigenvalue: float, clock_period: float, hbar: float = 1.0) -> float:
    """Conditional Stone-generator map E=(hbar/tau_clock) kappa."""
    kappa, tau, quantum = map(float, (generator_eigenvalue, clock_period, hbar))
    if not all(math.isfinite(value) for value in (kappa, tau, quantum)) or tau <= 0.0 or quantum <= 0.0:
        raise ValueError("finite kappa and positive finite clock_period/hbar required")
    return quantum * kappa / tau


def clock_energy_payload() -> dict[str, Any]:
    p = Process("A", "B", Fraction(2, 3))
    q = Process("B", "C", Fraction(5, 7))
    composed = p.then(q)
    return {
        "version": "v15.0",
        "fundamental_order": "dimensionless_additive_process_cocycle_chi",
        "composition_witness": {
            "chi_gamma_1": str(p.depth),
            "chi_gamma_2": str(q.depth),
            "chi_composite": str(composed.depth),
        },
        "chi_called_fundamental_time": False,
        "clock_map": "t_eff/tau_ref=chi(process)/chi(reference_cycle)",
        "clock_gate": "CONDITIONAL_RELATIVE_CLOCK_CONSTRUCTED_IF_A_STABLE_RECURRING_REFERENCE_PROCESS_EXISTS",
        "absolute_seconds_derived": False,
        "circularity_check": "chi and composition are defined before clocks; the reference cycle calibrates rather than defines relational order",
        "dimensionless_generator": "U(chi)=exp(-i*chi*K)",
        "energy_map": "E_eff=(hbar/tau_clock)*kappa",
        "linearity_reason": "strongly_continuous_unitary_representation_of_the_additive_process_parameter_Stone_generator",
        "energy_gate": "CONDITIONAL_ON_UNITARY_REPRESENTATION_AND_EMERGENT_CLOCK_CALIBRATION",
        "conventional_energy_is_fundamental": False,
        "core_has_conventional_energy": False,
        "F_kappa_arbitrarily_selected": False,
        "clock_period_is_new_Aether_action_parameter": False,
        "new_continuous_parameter_adopted": False,
    }
