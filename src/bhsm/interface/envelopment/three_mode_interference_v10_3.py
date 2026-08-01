"""Relativistic three-mode interference-output gate."""

from __future__ import annotations

from typing import Any

import numpy as np


INTERFERENCE_TARGET = "ACTION_DERIVED_THREE_MODE_INTERFERENCE_OUTPUT_FUNCTIONAL"


def hermitian_energy(amplitudes: np.ndarray, operator: np.ndarray) -> float:
    """Evaluate v^dagger M v for a supplied Hermitian three-mode operator."""

    vector = np.asarray(amplitudes, dtype=complex)
    matrix = np.asarray(operator, dtype=complex)
    if vector.shape != (3,) or matrix.shape != (3, 3):
        raise ValueError("three complex amplitudes and a 3x3 operator are required")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-12, rtol=0):
        raise ValueError("interference operator must be Hermitian")
    value = np.vdot(vector, matrix @ vector)
    if abs(value.imag) > 1e-10:
        raise ValueError("Hermitian energy must be real")
    return float(value.real)


def interference_payload() -> dict[str, Any]:
    payload = {
        "artifact": "BHSM_three_mode_interference_gate_v10_3",
        "state": ["A_C exp(i phi_C)", "A_W exp(i phi_W)", "A_D exp(i phi_D)"],
        "Hermitian_output_form": "epsilon_out=v^dagger M_env v",
        "M_env": None,
        "diagonal_coefficients": None,
        "cross_coefficients": None,
        "amplitudes": None,
        "relative_phases": None,
        "normalization": None,
        "boundedness": None,
        "Lorentz_transformation_behavior": None,
        "global_background_dependence": None,
        "generalized_eigenproblem": "H v_n=omega_n^2 K v_n",
        "stable_coupled_vector": None,
        "output_functional": None,
        "field_particle_propagation_classification": None,
        "physical_output_scale": None,
        "reason": "q_D and the common K/H/source blocks are absent",
        "target": INTERFERENCE_TARGET,
        "arbitrary_coefficients_inserted": False,
        "physical_output_emitted": False,
    }
    payload["validation_passed"] = (
        payload["M_env"] is None
        and payload["amplitudes"] is None
        and payload["relative_phases"] is None
        and payload["physical_output_scale"] is None
        and payload["arbitrary_coefficients_inserted"] is False
        and payload["physical_output_emitted"] is False
    )
    return payload
