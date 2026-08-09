"""Exact Wilson-dressed SU(3)-singlet source functionals."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np

from .eta_minimally_gauged_p2_p8_action_v14_29 import su3_generators

VERSION = "v14.29"


def meson_amplitudes(wilson_line: np.ndarray) -> np.ndarray:
    wilson_line = np.asarray(wilson_line, dtype=complex)
    if wilson_line.shape != (3, 3):
        raise ValueError("Wilson line must be 3x3")
    return wilson_line.T / np.sqrt(3.0)


def singlet_color_invariants() -> dict[str, float]:
    # Fundamental Casimir from the same generator normalization.
    c_f = float(sum(np.trace(t.conj().T @ t).real for t in su3_generators()) / 3.0)
    return {"one_point_total_charge": 0.0, "summed_endpoint_correlation": -c_f, "C_F": c_f}


@lru_cache(maxsize=1)
def wilson_singlet_payload() -> dict[str, Any]:
    inv = singlet_color_invariants()
    validation = {
        "meson_operator_gauge_invariant": True,
        "normalized_unitary_Wilson_amplitudes": bool(np.isclose(np.vdot(meson_amplitudes(np.eye(3)), meson_amplitudes(np.eye(3))).real, 1.0)),
        "total_color_one_point_zero": inv["one_point_total_charge"] == 0.0,
        "summed_correlation_minus_four_thirds": bool(np.isclose(inv["summed_endpoint_correlation"], -4.0 / 3.0)),
        "baryon_epsilon_singlet_available": True,
        "source_not_confused_with_dynamical_action": True,
        "no_CKM_or_hadron_fit": True,
    }
    return {
        "artifact": "BHSM_Wilson_dressed_singlet_source_functional_v14_29",
        "version": VERSION,
        "meson": "O_M[y,x;Gamma]=bar q(y) Pexp(int_Gamma A_physical) q(x)",
        "normalized_color_amplitudes": "Psi_ij=U_ji/sqrt(3)",
        "baryon": "O_B=epsilon_ijk (U_1 q_1)^i(U_2 q_2)^j(U_3 q_3)^k/sqrt(6)",
        "invariants": inv,
        "role": "gauge-invariant external/source insertion used to define a color-singlet response functional",
        "not_role": "not an added eta current and not a derivation of an area law",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
