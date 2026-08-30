"""Action-owned BHSM Yukawa tensors, masses, and relative mixing.

Gauge invariance fixes the four retained channel types, but not their family
matrices.  This module therefore accepts a matrix only when it is selected by
the same-action HS Hessian on the current background.  Singular values give
mass responses, and CKM/PMNS-type matrices are relative left singular frames;
no measured mass or mixing entry is an input.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import linalg


Array = np.ndarray


YUKAWA_CHANNELS = {
    "up": "Q_H_u_c",
    "down": "Q_Hdagger_d_c",
    "charged_lepton": "L_Hdagger_e_c",
    "neutrino": "L_H_nu_c",
}


@dataclass(frozen=True)
class ActionYukawaMatrix:
    channel: str
    matrix: Array
    action_version: str
    background_id: str
    hs_direction_id: str
    provenance: tuple[str, ...]
    selected_by_same_action_hessian: bool
    fitted_to_observable: bool = False

    def __post_init__(self) -> None:
        matrix = np.asarray(self.matrix, dtype=complex)
        if self.channel not in YUKAWA_CHANNELS:
            raise ValueError("unknown BHSM Yukawa channel")
        if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
            raise ValueError("BHSM family Yukawa matrix must be finite 3x3")
        if not self.selected_by_same_action_hessian:
            raise ValueError("Yukawa matrix must be selected by the same-action HS Hessian")
        if self.fitted_to_observable:
            raise ValueError("observable-fitted Yukawa matrices are forbidden")
        if not self.hs_direction_id or not self.provenance:
            raise ValueError("HS direction and Yukawa provenance are required")
        object.__setattr__(self, "matrix", matrix)

    @property
    def invariant_monomial(self) -> str:
        return YUKAWA_CHANNELS[self.channel]


@dataclass(frozen=True)
class FermionMassResponse:
    channel: str
    mass_matrix: Array
    singular_masses: Array
    left_frame: Array
    right_frame: Array
    minimum_relative_squared_mass_gap: float
    simple_spectrum: bool


def fermion_mass_response(
    yukawa: ActionYukawaMatrix,
    physical_hs_amplitude: float,
    *,
    simplicity_tolerance: float = 1.0e-10,
) -> FermionMassResponse:
    if not np.isfinite(physical_hs_amplitude) or physical_hs_amplitude < 0.0:
        raise ValueError("physical HS amplitude must be finite and nonnegative")
    mass_matrix = physical_hs_amplitude * yukawa.matrix
    left, singular, right_adjoint = linalg.svd(mass_matrix, full_matrices=True)
    squared = np.sort(singular**2)
    scale = max(float(np.max(squared, initial=0.0)), np.finfo(float).tiny)
    gaps = np.diff(squared) / scale
    minimum_gap = float(np.min(gaps, initial=np.inf))
    return FermionMassResponse(
        channel=yukawa.channel,
        mass_matrix=mass_matrix,
        singular_masses=singular,
        left_frame=left,
        right_frame=right_adjoint.conj().T,
        minimum_relative_squared_mass_gap=minimum_gap,
        simple_spectrum=bool(minimum_gap > simplicity_tolerance),
    )


def relative_left_mixing(
    first: FermionMassResponse,
    second: FermionMassResponse,
    *,
    require_simple_spectra: bool = True,
) -> Array:
    if require_simple_spectra and (not first.simple_spectrum or not second.simple_spectrum):
        raise RuntimeError("degenerate mass response does not select a unique mixing basis")
    return first.left_frame.conj().T @ second.left_frame


__all__ = [
    "ActionYukawaMatrix",
    "FermionMassResponse",
    "YUKAWA_CHANNELS",
    "fermion_mass_response",
    "relative_left_mixing",
]
