"""Exact primitives and claim guards for CKM channel-equivalence audits."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path


S_CH = (1, 2, 4)
FORBIDDEN_INPUTS = (
    "empirical CKM fitting",
    "PDG/reference values",
    "W calibration",
    "charged-mass fitting",
    "neutrino limits",
    "legacy threshold tables",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def input_guard() -> dict[str, object]:
    return {
        "empirical_inputs_used": False,
        "forbidden_theorem_inputs": list(FORBIDDEN_INPUTS),
        "forbidden_theorem_inputs_used": [],
    }


def channel_counts() -> dict[str, int]:
    s_l, s_u, s_d = S_CH
    return {
        "N_ud": s_u * s_d,
        "N_total_end": (s_l + s_u + s_d) ** 2,
        "N_sum_self": s_l**2 + s_u**2 + s_d**2,
        "N_max_self": s_d**2,
    }
