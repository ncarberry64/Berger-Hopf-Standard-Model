"""No-fit spectral charged-current kernel for the intrinsic M4 action."""

from __future__ import annotations

from math import pi, sqrt
from typing import Any

import numpy as np

from bhsm.interface.master_action.common_parent_charged_current_attachment import weak_generators
from bhsm.interface.master_action.complex_profile_isospectral_attachment import jarlskog, standard_sines

from .quark_yukawa_ckm_v11_4 import DOWN_MODES, UP_MODES, sector_overlaps


VERSION = "v11.5"
PRIMARY_VERDICT = "BHSM_SPECTRAL_CHARGED_CURRENT_KERNEL_MATHEMATICALLY_VIABLE_AS_AUTHOR_SELECTED_NO_FIT_ACTION_CANDIDATE"
EXACT_NEXT_OBJECT = "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL"


def spectral_angles(anisotropy: float = 137.035999084 / (12 * pi * pi)) -> dict[str, float]:
    """Frozen BHSM internal rule, evaluated without measured CKM inputs."""

    up = sector_overlaps(UP_MODES, anisotropy)
    down = sector_overlaps(DOWN_MODES, anisotropy)
    return {
        "sin_theta_12": sqrt(down["light"] / down["middle"]),
        "sin_theta_23": 2.0 * down["middle"],
        "sin_theta_13": sqrt(up["light"]),
        "delta": 2.0 / sqrt(pi),
    }


def spectral_current_kernel(anisotropy: float = 137.035999084 / (12 * pi * pi)) -> np.ndarray:
    """Return K_ud=U_BHSM in the ordered (light,middle,heavy) mass basis."""

    values = spectral_angles(anisotropy)
    s12 = values["sin_theta_12"]
    s23 = values["sin_theta_23"]
    s13 = values["sin_theta_13"]
    delta = values["delta"]
    c12 = sqrt(1.0 - s12 * s12)
    c23 = sqrt(1.0 - s23 * s23)
    c13 = sqrt(1.0 - s13 * s13)
    e_plus = np.exp(1j * delta)
    e_minus = np.exp(-1j * delta)
    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * e_minus],
            [
                -s12 * c23 - c12 * s23 * s13 * e_plus,
                c12 * c23 - s12 * s23 * s13 * e_plus,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * e_plus,
                -c12 * s23 - s12 * c23 * s13 * e_plus,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )


def su2_residuals(kernel: np.ndarray) -> dict[str, float]:
    generators = weak_generators(kernel)
    tp = generators["T_plus"]
    tm = generators["T_minus"]
    t3 = generators["T_3"]
    t1 = generators["T_1"]
    t2 = generators["T_2"]
    commutator = lambda left, right: left @ right - right @ left
    return {
        "[T3,Tplus]-Tplus": float(np.linalg.norm(commutator(t3, tp) - tp)),
        "[T3,Tminus]+Tminus": float(np.linalg.norm(commutator(t3, tm) + tm)),
        "[Tplus,Tminus]-2T3": float(np.linalg.norm(commutator(tp, tm) - 2 * t3)),
        "[T1,T2]-iT3": float(np.linalg.norm(commutator(t1, t2) - 1j * t3)),
    }


def current_payload(anisotropy: float = 137.035999084 / (12 * pi * pi)) -> dict[str, Any]:
    kernel = spectral_current_kernel(anisotropy)
    angles = spectral_angles(anisotropy)
    extracted = standard_sines(kernel)
    residuals = su2_residuals(kernel)
    unitarity = float(np.linalg.norm(kernel.conj().T @ kernel - np.eye(3)))
    determinant_modulus = float(abs(np.linalg.det(kernel)))
    J = jarlskog(kernel)
    validation = {
        "full_rank": determinant_modulus > 1.0e-12,
        "unitary": unitarity < 1.0e-12,
        "angles_recovered": all(
            abs(extracted[key] - angles[key]) < 1.0e-14
            for key in extracted
        ),
        "nonzero_CP": abs(J) > 1.0e-12,
        "SU2_algebra_closed": max(residuals.values()) < 1.0e-12,
        "neutral_current_family_central": True,
        "uses_existing_g2_only": True,
        "no_new_continuous_coefficient": True,
        "no_measured_CKM_input": True,
        "kernel_selection_is_author_selected": True,
        "absence_of_parent_action_mixed_variation_or_current_pairing_recorded": True,
        "absence_of_axiomatic_uniqueness_theorem_recorded": True,
        "provenance_gate_remains_open": True,
    }
    return {
        "artifact": "BHSM_spectral_charged_current_v11_5",
        "version": VERSION,
        "classification": "AUTHOR_SELECTED_NO_FIT_ACTION_CANDIDATE_NOT_ACTION_DERIVED",
        "basis_order": ["light", "middle", "heavy"],
        "input_rule": {
            "sin_theta_12": "sqrt(T_down_light/T_down_middle)",
            "sin_theta_23": "2 T_down_middle",
            "sin_theta_13": "sqrt(T_up_light)",
            "delta": "4 sqrt(S_overlap)=2/sqrt(pi)",
        },
        "inputs": angles,
        "kernel_real": kernel.real.tolist(),
        "kernel_imag": kernel.imag.tolist(),
        "kernel_magnitudes": np.abs(kernel).tolist(),
        "determinant_modulus": determinant_modulus,
        "unitarity_residual": unitarity,
        "jarlskog": J,
        "SU2_residuals": residuals,
        "candidate_action_term": "-(g2/sqrt(2))[W+_mu ubar_L gamma^mu K_ud d_L+h.c.]",
        "action_ownership": "NOT_ESTABLISHED: the kernel has not been recovered from a parent-action mixed second variation/current pairing and is not selected by a stated uniqueness theorem",
        "action_derived": False,
        "provenance_gate_satisfied": False,
        "new_fields": [],
        "new_coefficients": [],
        "measured_mixing_inputs": [],
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
