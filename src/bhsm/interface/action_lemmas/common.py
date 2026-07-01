"""Shared exact arithmetic and claim boundaries for BHSM action lemmas."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path


FORBIDDEN_INPUTS = (
    "empirical CKM fitting",
    "charged-mass fitting",
    "PDG/reference values",
    "W calibration",
    "neutrino limits",
    "legacy threshold tables",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def input_guard() -> dict[str, object]:
    return {
        "forbidden_theorem_inputs": list(FORBIDDEN_INPUTS),
        "forbidden_theorem_inputs_used": [],
        "empirical_inputs_used": False,
    }
