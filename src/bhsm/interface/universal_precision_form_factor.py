"""Basis-independent electromagnetic form-factor projection.

The loop/vertex evaluator supplies a renormalized on-shell vertex and the two
action-owned tensor structures.  This module solves only the general matching
problem and exposes ``a=(g-2)/2=F2(0)`` after Gate-7, Ward, and renormalization
promotion gates are satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import linalg

from bhsm.interface.universal_loop_renormalization import RenormalizedVertex
from bhsm.interface.universal_lsz import LSZExternalMode


Array = np.ndarray


@dataclass(frozen=True)
class ElectromagneticFormFactors:
    q_squared: float
    F1: complex
    F2: complex
    relative_projection_residual: float
    basis_condition_2: float


def project_electromagnetic_form_factors(
    vertex: Array,
    dirac_basis: Array,
    pauli_basis: Array,
    *,
    q_squared: float,
) -> ElectromagneticFormFactors:
    vertex = np.asarray(vertex, dtype=complex).reshape(-1)
    dirac = np.asarray(dirac_basis, dtype=complex).reshape(-1)
    pauli = np.asarray(pauli_basis, dtype=complex).reshape(-1)
    if vertex.shape != dirac.shape or vertex.shape != pauli.shape:
        raise ValueError("vertex and form-factor bases must have the same shape")
    design = np.column_stack((dirac, pauli))
    coefficients, _, rank, singular = linalg.lstsq(design, vertex, check_finite=True)
    if rank != 2:
        raise ArithmeticError("Dirac and Pauli form-factor structures are not independent")
    reconstructed = design @ coefficients
    denominator = max(np.linalg.norm(vertex), np.finfo(float).tiny)
    residual = float(np.linalg.norm(vertex - reconstructed) / denominator)
    condition = float(singular[0] / singular[-1])
    return ElectromagneticFormFactors(
        q_squared=float(q_squared),
        F1=complex(coefficients[0]),
        F2=complex(coefficients[1]),
        relative_projection_residual=residual,
        basis_condition_2=condition,
    )


@dataclass(frozen=True)
class MuonGMinus2Readout:
    form_factors: ElectromagneticFormFactors
    action_version: str
    background_id: str
    renormalization_scheme_id: str | None
    gate7_closed: bool
    ward_identity_closed: bool
    external_muon_mode_action_selected: bool

    def require_physical_promotion(self, tolerance: float = 1.0e-9) -> None:
        missing: list[str] = []
        if not self.gate7_closed:
            missing.append("Gate7_closed_background")
        if not self.ward_identity_closed:
            missing.append("Ward_Slavnov_Taylor_closure")
        if self.renormalization_scheme_id is None:
            missing.append("BHSM_renormalization_scheme")
        if not self.external_muon_mode_action_selected:
            missing.append("action_selected_muon_external_mode")
        if abs(self.form_factors.q_squared) > tolerance:
            missing.append("q_squared_zero_limit")
        if abs(self.form_factors.F1 - 1.0) > tolerance:
            missing.append("charge_Ward_normalization_F1_zero_equals_one")
        if self.form_factors.relative_projection_residual > tolerance:
            missing.append("complete_vertex_form_factor_basis")
        if abs(self.form_factors.F2.imag) > tolerance:
            missing.append("real_on_shell_F2")
        if missing:
            raise RuntimeError("muon g-2 promotion blocked by: " + ", ".join(missing))

    def anomalous_magnetic_moment(self) -> float:
        self.require_physical_promotion()
        return float(self.form_factors.F2.real)

    def metadata(self) -> dict:
        return {
            "definition": "a_mu=(g_mu-2)/2=F2(q_squared=0)",
            "action_version": self.action_version,
            "background_id": self.background_id,
            "renormalization_scheme_id": self.renormalization_scheme_id,
            "experimental_target_used": False,
            "physical_promotion_ready": bool(
                self.gate7_closed
                and self.ward_identity_closed
                and self.renormalization_scheme_id is not None
                and self.external_muon_mode_action_selected
            ),
        }


def muon_gminus2_from_renormalized_vertex(
    vertex: RenormalizedVertex,
    dirac_basis: Array,
    pauli_basis: Array,
    incoming_mode: LSZExternalMode,
    outgoing_mode: LSZExternalMode,
    *,
    q_squared: float,
    modes_identified_as_muon_by_action_spectrum: bool,
    tolerance: float = 1.0e-10,
) -> MuonGMinus2Readout:
    """Compose the promoted loop vertex and LSZ states into the g-2 readout."""

    vertex.require_physical_promotion(tolerance=tolerance)
    incoming_mode.require_physical_external_state(tolerance=tolerance)
    outgoing_mode.require_physical_external_state(tolerance=tolerance)
    if incoming_mode.mode_id != outgoing_mode.mode_id:
        raise ValueError("elastic electromagnetic form factor needs one external mode id")
    form_factors = project_electromagnetic_form_factors(
        vertex.finite_value,
        dirac_basis,
        pauli_basis,
        q_squared=q_squared,
    )
    return MuonGMinus2Readout(
        form_factors=form_factors,
        action_version=vertex.action_version,
        background_id=vertex.background_id,
        renormalization_scheme_id=vertex.scheme_id,
        gate7_closed=vertex.gate7_closed,
        ward_identity_closed=vertex.maximum_relative_ward_residual <= tolerance,
        external_muon_mode_action_selected=bool(
            modes_identified_as_muon_by_action_spectrum
            and incoming_mode.action_selected
            and outgoing_mode.action_selected
        ),
    )


__all__ = [
    "ElectromagneticFormFactors",
    "MuonGMinus2Readout",
    "muon_gminus2_from_renormalized_vertex",
    "project_electromagnetic_form_factors",
]
