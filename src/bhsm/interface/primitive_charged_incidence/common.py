"""Exact primitives for the charged-incidence audit."""

from __future__ import annotations

from fractions import Fraction
from math import gcd
from pathlib import Path


OMEGA_CH = (3, 6, 12)
SECTORS = ("lepton", "up", "down")
FORBIDDEN_THEOREM_INPUTS = (
    "PDG/reference values",
    "W calibration",
    "charged-mass fitting",
    "CKM reference fitting",
    "neutrino limits",
    "legacy threshold tables",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def gcd_all(values: tuple[int, ...]) -> int:
    result = 0
    for value in values:
        result = gcd(result, abs(value))
    return result


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def no_empirical_inputs() -> dict[str, object]:
    return {
        "forbidden_theorem_inputs": list(FORBIDDEN_THEOREM_INPUTS),
        "forbidden_theorem_inputs_used": [],
        "empirical_inputs_used": False,
    }
