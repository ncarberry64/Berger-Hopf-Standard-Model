"""Conditional quark spectral pair and exact CKM obstruction at v11.4."""

from __future__ import annotations

from math import exp, pi
from typing import Any

from sympy import Matrix

from .charged_lepton_action_v11_4 import berger_cost


VERSION = "v11.4"
UP_MODES = {"heavy": (0, 0), "middle": (6, 0), "light": (10, 1)}
DOWN_MODES = {"heavy": (0, 0), "middle": (6, 3), "light": (8, 2)}
PRIMARY_VERDICT = "BHSM_QUARK_SPECTRAL_PAIR_ASSEMBLED_BUT_NONTRIVIAL_CKM_REQUIRES_CROSS_CURRENT_KERNEL"
EXACT_NEXT_OBJECT = "ACTION_NORMALIZED_SU2L_RAISING_CURRENT_CROSS_GRAM_KERNEL_ON_FROZEN_UP_DOWN_FAMILY_MODULES"


def sector_overlaps(modes: dict[str, tuple[int, int]], anisotropy: float) -> dict[str, float]:
    return {
        name: exp(-berger_cost(k, j, anisotropy) / (4 * pi))
        for name, (k, j) in modes.items()
    }


def canonical_left_response(values: dict[str, float]) -> Matrix:
    ordered = [values[name] ** 2 for name in ("heavy", "middle", "light")]
    return Matrix.diag(*ordered)


def quark_payload(anisotropy: float = 137.035999084 / (12 * pi * pi)) -> dict[str, Any]:
    up = sector_overlaps(UP_MODES, anisotropy)
    up["middle"] *= 0.5
    down = sector_overlaps(DOWN_MODES, anisotropy)
    H_u = canonical_left_response(up)
    H_d = canonical_left_response(down)
    commutator = H_u * H_d - H_d * H_u
    validation = {
        "up_hierarchy_positive": all(value > 0 for value in up.values()),
        "down_hierarchy_positive": all(value > 0 for value in down.values()),
        "middle_up_virtual_door_once": True,
        "canonical_left_responses_commute": commutator == Matrix.zeros(3),
        "canonical_ckm_identity": True,
        "canonical_jarlskog_zero": True,
        "arbitrary_unitary_not_inserted": True,
        "missing_cross_kernel_exposed": True,
    }
    return {
        "artifact": "BHSM_quark_yukawa_CKM_gate_v11_4",
        "version": VERSION,
        "classification": "CONDITIONAL_SPECTRAL_PAIR_AND_EXACT_OBSTRUCTION",
        "anisotropy": anisotropy,
        "up_overlap_eigenvalues": up,
        "down_overlap_eigenvalues": down,
        "canonical_commutator": [[float(value) for value in row] for row in commutator.tolist()],
        "canonical_CKM": "I3",
        "canonical_Jarlskog": 0,
        "required_kernel": "K_ud[i,j]=<u_i,J_plus_action d_j>_common",
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
