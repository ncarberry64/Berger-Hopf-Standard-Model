"""Observable sensitivity on the retained finite-rank CAR covariance family.

These are algebraic diagnostics, not physical self-energies or selected states.
The exact affine criterion must not be applied to a nonlinear pole functional.
"""
from __future__ import annotations

import math
import numpy as np

REFERENCE = np.diag([1., 1., 0., 0.]).astype(complex)
CONJUGATION = np.block([[np.zeros((2, 2)), np.eye(2)],
                        [np.eye(2), np.zeros((2, 2))]]).astype(complex)
CHARGE = np.diag([1., -1., -1., 1.]).astype(complex)


def phase_covariance(theta: float, phase: float = 0.) -> np.ndarray:
    """Extend the retained real rotation by its independent complex phase."""
    if not all(math.isfinite(x) for x in (theta, phase)):
        raise ValueError("finite angle and phase required")
    c = math.cos(theta)
    z = math.sin(theta) * complex(math.cos(phase), math.sin(phase))
    frame = np.asarray([[c, 0], [0, c], [0, -z], [z, 0]], dtype=complex)
    return frame @ frame.conj().T


def _matrix(matrix) -> np.ndarray:
    result = np.asarray(matrix, dtype=complex)
    if (result.shape != (4, 4) or not np.all(np.isfinite(result))
            or not np.array_equal(result, result.conj().T)):
        raise ValueError("finite exactly Hermitian 4-by-4 matrix required")
    return result


def affine_response_screen(matrix) -> dict:
    """Exact-form coefficients for F(C)=constant+Tr(B C) on this family.

    Report evaluation in binary64; zero floating coefficients are not an
    outward proof for a numerically approximated physical operator.
    """
    bmat = _matrix(matrix)
    a = math.fsum([bmat[2, 2].real, bmat[3, 3].real,
                   -bmat[0, 0].real, -bmat[1, 1].real])
    b = complex(bmat[0, 3]-bmat[1, 2])
    diameter = math.hypot(a, 2*abs(b))
    if not all(math.isfinite(x) for x in (a, b.real, b.imag, diameter)):
        raise ValueError("response coefficients exceed binary64 range")
    return {
        "a": a, "b_real": b.real, "b_imag": b.imag,
        "affine_difference_formula": "a*sin(theta)^2+sin(2*theta)*Re(exp(i*phase)*b)",
        "affine_difference_range": [(a-diameter)/2, (a+diameter)/2],
        "affine_range_diameter": diameter,
        "floating_coefficients_exactly_zero": a == 0 and b == 0,
        "maximum_reference_tangent_response": 2*abs(b),
        "scope": "This four-mode family and an affine functional only",
        "physical_promotion": False,
    }


def direct_affine_difference(matrix, theta: float, phase: float = 0.) -> float:
    return float(np.trace(_matrix(matrix) @ (phase_covariance(theta, phase)-REFERENCE)).real)


def algebraic_controls() -> dict[str, np.ndarray]:
    imaginary = np.zeros((4, 4), dtype=complex)
    imaginary[0, 3], imaginary[3, 0] = 1j, -1j
    return {"identity": np.eye(4, dtype=complex), "charge": CHARGE.copy(),
            "reference_occupation": REFERENCE.copy(),
            "imaginary_mixed_response": imaginary}


def claim_boundary() -> dict:
    return {
        "complex_phase_CAR_family_derived": True,
        "exact_affine_response_criterion_on_this_family_derived": True,
        "real_angle_only_test_can_miss_state_sensitivity": True,
        "state_nonuniqueness_alone_excludes_every_observable": False,
        "affine_criterion_applies_to_arbitrary_nonlinear_pole_functional": False,
        "test_at_one_covariance_proves_global_state_independence": False,
        "full_Hadamard_class_observable_independence_proved": False,
        "physical_lepton_dressing_response_operator_derived": False,
        "physical_lepton_dressing_invariant_state_independent": False,
        "action_selected_state_derived": False,
        "new_physical_state_or_self_energy_inserted": False,
        "empirical_input_used": False,
        "numerical_outward_certificate": False,
        "FULL_BHSM_COMPLETE": False,
    }
