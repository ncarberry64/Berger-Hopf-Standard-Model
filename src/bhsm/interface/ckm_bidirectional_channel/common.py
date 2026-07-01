"""Exact dimensions and input guards for the v2.3 CKM channel audit."""

from __future__ import annotations

from pathlib import Path


S_LEPTON = 1
S_UP = 2
S_DOWN = 4
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


def channel_dimensions() -> dict[str, int]:
    return {
        "s_u": S_UP,
        "s_d": S_DOWN,
        "N_one_way_ud": S_UP * S_DOWN,
        "N_one_way_du": S_DOWN * S_UP,
        "N_bidirectional_ud_du": 2 * S_UP * S_DOWN,
        "N_sum_self": S_LEPTON**2 + S_UP**2 + S_DOWN**2,
        "N_total_end": (S_LEPTON + S_UP + S_DOWN) ** 2,
        "N_max_self": S_DOWN**2,
    }


def input_guard() -> dict[str, object]:
    return {
        "empirical_inputs_used": False,
        "forbidden_theorem_inputs": list(FORBIDDEN_INPUTS),
        "forbidden_theorem_inputs_used": [],
        "frozen_predictions_modified": False,
        "official_prediction_logic_modified": False,
    }

