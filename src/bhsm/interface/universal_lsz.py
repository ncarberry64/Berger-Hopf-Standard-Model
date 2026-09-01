"""Inverse-free LSZ-equivalent external-state normalization.

For a simple pole of ``Gamma2(z)=K0+z K1``, the descriptor normalization is
``left^dagger K1 right``.  Normalizing the left/right modes by its square root
makes that bilinear equal to one without forming a propagator inverse.  The
remaining common phase is conventional and cannot change a squared physical
amplitude.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath

import numpy as np

from bhsm.interface.universal_quadratic_spectrum import PoleResidue


Array = np.ndarray


@dataclass(frozen=True)
class LSZExternalMode:
    spectral_parameter: complex
    right_mode: Array
    left_mode: Array
    descriptor_normalization_residual: float
    pole_simple: bool
    action_selected: bool
    mode_id: str
    provenance: tuple[str, ...]

    def require_physical_external_state(self, tolerance: float = 1.0e-10) -> None:
        missing: list[str] = []
        if not self.pole_simple:
            missing.append("simple_isolated_pole")
        if not self.action_selected:
            missing.append("action_selected_external_mode")
        if self.descriptor_normalization_residual > tolerance:
            missing.append("unit_LSZ_descriptor_residue")
        if missing:
            raise RuntimeError("external-state promotion blocked by: " + ", ".join(missing))


def normalize_simple_pole(
    pole: PoleResidue,
    kinetic_symbol: Array,
    *,
    mode_id: str,
    action_selected: bool,
    provenance: tuple[str, ...],
    zero_tolerance: float = 1.0e-14,
) -> LSZExternalMode:
    kinetic = np.asarray(kinetic_symbol, dtype=complex)
    if kinetic.shape != pole.residue.shape:
        raise ValueError("kinetic symbol and pole residue dimensions differ")
    if not pole.finite:
        raise ValueError("an infinite descriptor pole cannot define an LSZ state")
    normalization = complex(pole.left_mode.conj().T @ kinetic @ pole.right_mode)
    if abs(normalization) <= zero_tolerance:
        raise ArithmeticError("pole has zero descriptor derivative normalization")
    root = cmath.sqrt(normalization)
    right = np.asarray(pole.right_mode, dtype=complex) / root
    left = np.asarray(pole.left_mode, dtype=complex) / np.conjugate(root)
    check = complex(left.conj().T @ kinetic @ right)
    residual = float(abs(check - 1.0))
    return LSZExternalMode(
        spectral_parameter=pole.spectral_parameter,
        right_mode=right,
        left_mode=left,
        descriptor_normalization_residual=residual,
        pole_simple=pole.simple,
        action_selected=bool(action_selected),
        mode_id=mode_id,
        provenance=provenance,
    )


def lsz_amplitude(
    amputated_amplitude: complex,
    external_modes: tuple[LSZExternalMode, ...],
) -> complex:
    """Promote an amplitude already contracted with unit-residue modes."""

    if not external_modes:
        raise ValueError("an LSZ amplitude needs at least one external mode")
    for mode in external_modes:
        mode.require_physical_external_state()
    value = complex(amputated_amplitude)
    if not np.isfinite(value):
        raise ValueError("amputated amplitude must be finite")
    return value


__all__ = ["LSZExternalMode", "lsz_amplitude", "normalize_simple_pole"]
