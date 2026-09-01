"""Compatible action pieces on the current AE3 C2 finite-core domain.

This module does not assemble a new particle spectrum.  It reuses the
action-owned product-Dirac finite-element pencil and attaches the source-jet
algebra already derived for a squared Dirac operator.  The result is a local
quadratic/source piece on the actual C2 form core, not a full interacting
field oracle and not a selected physical history.
"""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_REDUCED_PRODUCT_DIRAC_HS_SOURCE_JET"

_A = np.asarray(((2.0, 1.0), (1.0, 2.0)))
_C = np.asarray(((-1.0, 0.0), (0.0, 1.0)))


def assemble_tridiagonal(diagonal: np.ndarray, off_diagonal: np.ndarray) -> np.ndarray:
    """Return the real symmetric matrix represented by two diagonals."""

    diagonal = np.asarray(diagonal, dtype=float)
    off_diagonal = np.asarray(off_diagonal, dtype=float)
    if diagonal.ndim != 1 or off_diagonal.shape != (max(diagonal.size - 1, 0),):
        raise ValueError("off diagonal must have length diagonal.size-1")
    matrix = np.diag(diagonal)
    if off_diagonal.size:
        matrix += np.diag(off_diagonal, 1) + np.diag(off_diagonal, -1)
    return matrix


def assemble_element_forms(elements: np.ndarray) -> dict[str, np.ndarray]:
    """Assemble two-node symmetric element forms with the far node removed."""

    values = np.asarray(elements, dtype=float)
    if values.ndim != 3 or values.shape[1:] != (2, 2):
        raise ValueError("elements must have shape (segments,2,2)")
    if not np.all(np.isfinite(values)) or not np.allclose(
        values, np.swapaxes(values, 1, 2), atol=0.0, rtol=0.0
    ):
        raise ValueError("finite symmetric element forms required")
    segments = values.shape[0]
    diagonal = np.zeros(segments)
    off_diagonal = np.zeros(max(segments - 1, 0))
    for index, local in enumerate(values):
        diagonal[index] += local[0, 0]
        if index + 1 < segments:
            diagonal[index + 1] += local[1, 1]
            off_diagonal[index] += local[0, 1]
    return {"diagonal": diagonal, "off_diagonal": off_diagonal}


def reduced_product_dirac_hs_source_jet(
    *,
    proper_durations: np.ndarray,
    base_W: np.ndarray,
    source_profile: np.ndarray,
    generator_eigenvalue: float = 1.0,
) -> dict[str, Any]:
    """Differentiate the reduced squared-Dirac form under ``W -> W+eps*q*p``.

    On element ``e`` the retained product-Dirac form is

    ``K_e = S/h_e + W_e**2 M_e + W_e C``.

    For a real commuting LR/HS source ``delta W_e=q p_e`` this function
    returns the exact first derivative ``V_e`` and second/contact derivative
    ``Q_e``.  It intentionally does not identify this diagonal reduced probe
    with the transverse electromagnetic vertex required for ``F_2(0)``.
    """

    durations = np.asarray(proper_durations, dtype=float)
    W = np.asarray(base_W, dtype=float)
    profile = np.asarray(source_profile, dtype=float)
    q = float(generator_eigenvalue)
    if (
        durations.ndim != 1
        or W.shape != durations.shape
        or profile.shape != durations.shape
        or durations.size < 1
        or np.any(durations <= 0.0)
        or not np.all(np.isfinite(durations))
        or not np.all(np.isfinite(W))
        or not np.all(np.isfinite(profile))
        or not np.isfinite(q)
    ):
        raise ValueError("finite element data, positive durations, and finite q required")

    mass_elements = durations[:, None, None] * _A[None, :, :] / 6.0
    delta_W = q * profile
    vertex_elements = (
        2.0 * W[:, None, None] * delta_W[:, None, None] * mass_elements
        + delta_W[:, None, None] * _C[None, :, :]
    )
    contact_elements = 2.0 * delta_W[:, None, None] ** 2 * mass_elements
    vertex = assemble_element_forms(vertex_elements)
    contact = assemble_element_forms(contact_elements)
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "source_kind": "UNIT_COMMUTING_REDUCED_LR_HS_PROBE",
        "source_is_dynamical_field_coordinate": False,
        "electromagnetic_vertex_claimed": False,
        "segments": int(durations.size),
        "generator_eigenvalue": q,
        "mass_elements": mass_elements,
        "vertex_elements": vertex_elements,
        "contact_elements": contact_elements,
        "vertex_diagonal": vertex["diagonal"],
        "vertex_off_diagonal": vertex["off_diagonal"],
        "contact_diagonal": contact["diagonal"],
        "contact_off_diagonal": contact["off_diagonal"],
        "first_derivative_exact": True,
        "second_contact_derivative_exact": True,
        "explicit_inverse_formed": False,
    }


def section_fit_ledger() -> dict[str, Any]:
    """Record which puzzle sections this local result can and cannot advance."""

    return {
        "method": "NON_SERIAL_PUZZLE_SECTION_ASSEMBLY",
        "fit_rule": (
            "A_PIECE_MAY_ADVANCE_ANY_SECTION_WHEN_ITS_ACTION_BACKGROUND_DOMAIN_"
            "STATE_FACTORIZATION_SCALE_AND_PROVENANCE_INTERFACES_MATCH"
        ),
        "advanced_sections": {
            "current_full_field_action": [
                "C2_lowest_Weyl_product_Dirac_quadratic_pencils_both_chiralities",
                "exact_unit_reduced_LR_HS_first_source_derivative",
                "exact_unit_reduced_LR_HS_second_contact_derivative",
                "family_central_I3_tensor_attachment",
            ],
            "particle_identity_transport": [
                "existing_charged_family_fibers_can_tensor_with_this_C2_operator_piece"
            ],
            "muon_magnetic_moment": [
                "current_C2_two_point_operator_piece_only"
            ],
        },
        "unfitted_interfaces": {
            "current_full_field_action": [
                "dynamical_HS_coordinate_and_broken_LR_saddle",
                "gauge_ghost_and_transverse_electromagnetic_source_blocks",
                "nonzero_fermion_background_and_cross_derivatives",
                "maximal_history_exterior_operator",
            ],
            "particle_identity_transport": [
                "family_noncentral_returned_mass_operator",
                "action_selected_simple_particle_poles",
            ],
            "muon_magnetic_moment": [
                "transverse_photon_vertex",
                "Ward_identity_and_action_derived_renormalization",
                "complete_loop_amplitude_and_q_squared_to_zero_limit",
            ],
        },
        "prediction_emitted": False,
        "full_field_action_complete": False,
        "full_BHSM_complete": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "assemble_element_forms",
    "assemble_tridiagonal",
    "reduced_product_dirac_hs_source_jet",
    "section_fit_ledger",
]
