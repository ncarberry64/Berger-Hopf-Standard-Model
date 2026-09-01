"""Current-C2 reduced HS/fermion mixed-variation theorem.

This module differentiates only the already attached squared product-Dirac
piece. It does not transplant the historical proper-cycle HS determinant or
introduce a dynamical HS kernel into AE3.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_REDUCED_HS_FERMION_MIXED_VARIATION"


def _tridiagonal_matvec(
    diagonal: np.ndarray, off_diagonal: np.ndarray, vector: np.ndarray
) -> np.ndarray:
    result = diagonal * vector
    if off_diagonal.size:
        result[:-1] += off_diagonal * vector[1:]
        result[1:] += off_diagonal * vector[:-1]
    return result


def _tridiagonal_frobenius(
    diagonal: np.ndarray, off_diagonal: np.ndarray
) -> float:
    return float(
        np.sqrt(
            np.vdot(diagonal, diagonal).real
            + 2.0 * np.vdot(off_diagonal, off_diagonal).real
        )
    )


def reduced_bilinear_variations(
    *,
    vertex_diagonal: np.ndarray,
    vertex_off_diagonal: np.ndarray,
    contact_diagonal: np.ndarray,
    contact_off_diagonal: np.ndarray,
    fermion_background: np.ndarray,
) -> dict[str, Any]:
    """Differentiate ``bar(c) K(H) c`` through second order in ``H``.

    ``K(H)=K0+H*V+H^2*Q/2``.  At a coefficient background ``c_star``, the
    reduced HS source is ``bar(c_star)V c_star``, its HS curvature is
    ``bar(c_star)Q c_star``, and the two mixed Hessian legs are ``V c_star``
    and its adjoint.  The background-independent first nonzero interaction is
    the third variation ``D_H D_bar(c) D_c S=V``.
    """

    vd = np.asarray(vertex_diagonal, dtype=complex)
    vo = np.asarray(vertex_off_diagonal, dtype=complex)
    qd = np.asarray(contact_diagonal, dtype=complex)
    qo = np.asarray(contact_off_diagonal, dtype=complex)
    background = np.asarray(fermion_background, dtype=complex)
    dimension = vd.size
    if (
        dimension < 1
        or vo.shape != (dimension - 1,)
        or qd.shape != (dimension,)
        or qo.shape != (dimension - 1,)
        or background.shape != (dimension,)
        or not all(
            np.all(np.isfinite(item)) for item in (vd, vo, qd, qo, background)
        )
        or any(np.any(item.imag != 0.0) for item in (vd, vo, qd, qo))
    ):
        raise ValueError("finite compatible real-symmetric variation data required")

    vertex_on_background = _tridiagonal_matvec(vd, vo, background)
    contact_on_background = _tridiagonal_matvec(qd, qo, background)
    source = np.vdot(background, vertex_on_background)
    curvature = np.vdot(background, contact_on_background)
    norm = float(np.linalg.norm(background))
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "dimension": dimension,
        "fermion_coefficient_background_norm": norm,
        "nonzero_fermion_coefficient_background_supplied": norm > 0.0,
        "reduced_HS_source": {
            "real": float(source.real),
            "imaginary": float(source.imag),
        },
        "reduced_HS_curvature": {
            "real": float(curvature.real),
            "imaginary": float(curvature.imag),
        },
        "mixed_HS_fermion_Hessian_norm": float(
            np.linalg.norm(vertex_on_background)
        ),
        "third_variation_vertex_frobenius_norm": _tridiagonal_frobenius(vd, vo),
        "fourth_variation_contact_frobenius_norm": _tridiagonal_frobenius(qd, qo),
        "zero_background_mixed_Hessian_vanishes_exactly": bool(
            norm == 0.0
            and np.all(vertex_on_background == 0.0)
            and source == 0.0
            and curvature == 0.0
        ),
        "first_nonzero_background_independent_interaction": (
            "D_H_D_barfermion_D_fermion_S_REDUCED_EQUALS_V"
        ),
        "family_factor": "I3",
        "family_projector_selects_spatial_coefficient_background": False,
        "physical_broken_LR_saddle_derived": False,
    }


@dataclass(frozen=True)
class HSKernelCandidate:
    candidate_id: str
    same_AE3_action: bool
    same_current_C2_domain: bool
    dynamical_HS_kernel: bool
    physical_direction_selected: bool
    no_new_continuous_coefficient: bool
    status: str

    @property
    def attachable(self) -> bool:
        return all(
            (
                self.same_AE3_action,
                self.same_current_C2_domain,
                self.dynamical_HS_kernel,
                self.physical_direction_selected,
                self.no_new_continuous_coefficient,
            )
        )


def hs_kernel_candidate_screen() -> dict[str, Any]:
    """Separate reusable HS structures from a current AE3 dynamical kernel."""

    rows = (
        HSKernelCandidate(
            "CURRENT_C2_REDUCED_PRODUCT_DIRAC_SOURCE_AND_CONTACT_JET",
            True,
            True,
            False,
            False,
            True,
            "ATTACHED_INTERACTION_TENSORS_BUT_NO_PURE_HS_QUADRATIC_KERNEL",
        ),
        HSKernelCandidate(
            "V16_05_COMMON_GAUGE_HS_HEAT_PUSHFORWARD",
            False,
            False,
            True,
            False,
            True,
            "REUSABLE_PROPER_CYCLE_KERNEL_WRONG_BACKGROUND_AND_DOMAIN",
        ),
        HSKernelCandidate(
            "V16_02_FOUR_CHANNEL_HS_NORMALIZATION",
            False,
            False,
            True,
            False,
            True,
            "CHANNEL_KINETIC_FORM_REUSABLE_PHYSICAL_DIRECTION_UNSELECTED",
        ),
        HSKernelCandidate(
            "V15_75_FIRST_ORDER_EINSTEIN_CARTAN_CONTORSION_SCHUR_COMPLEMENT",
            False,
            False,
            True,
            False,
            True,
            "UNIQUE_COEFFICIENT_FREE_ACTION_EXTENSION_CANDIDATE_NOT_AE3_ATTACHED",
        ),
        HSKernelCandidate(
            "V15_72_LEGENDRE_CROSSING_COMPOSITE_BRANCH",
            False,
            False,
            True,
            True,
            True,
            "HISTORICAL_BRANCH_USES_UNEVALUATED_LSTAR_AND_SUPERSEDED_GAUGE_RESIDUE",
        ),
    )
    payload = []
    for candidate in rows:
        row = asdict(candidate)
        row["attachable"] = candidate.attachable
        payload.append(row)
    attachable = [row for row in payload if row["attachable"]]
    return {
        "candidate_rows": payload,
        "attachable_count": len(attachable),
        "selected_current_AE3_kernel": (
            attachable[0]["candidate_id"] if len(attachable) == 1 else None
        ),
        "strongest_minimal_nonarbitrary_extension_candidate": (
            "V15_75_FIRST_ORDER_EINSTEIN_CARTAN_CONTORSION_SCHUR_COMPLEMENT"
        ),
        "extension_requires_new_action_version_authority": True,
        "screen_passed": len(attachable) == 0,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "current_C2_zero_background_mixed_variation_derived": True,
        "current_C2_third_LR_HS_vertex_retained": True,
        "current_C2_dynamical_HS_kernel_derived": False,
        "current_C2_nonzero_fermion_background_instantiated": False,
        "current_C2_broken_LR_saddle_derived": False,
        "historical_family_mode_state_preserved": True,
        "family_mode_state_is_not_a_classical_Sobolev_fermion_background": True,
        "particle_spectrum_rebuilt": False,
        "next_action_decision": (
            "AUTHORIZE_AND_DERIVE_THE_COEFFICIENT_FREE_FIRST_ORDER_EINSTEIN_"
            "CARTAN_CURRENT_C2_SCHUR_COMPLEMENT_AS_A_NEW_ACTION_VERSION,_OR_"
            "SUPPLY_ANOTHER_PARENT_OWNED_CURRENT_C2_HS_KERNEL,_OR_RETAIN_AE3_"
            "WITHOUT_A_DYNAMICAL_BROKEN_LR_SECTOR"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "HSKernelCandidate",
    "claim_boundary",
    "hs_kernel_candidate_screen",
    "reduced_bilinear_variations",
]
