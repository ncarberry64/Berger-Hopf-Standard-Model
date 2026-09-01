"""Current-C2 lowest-level coexact hypercharge source derivatives.

The source is the unit spatial coexact U(1)_Y insertion inherited from the
rank-16 product-Dirac calculation.  It is not identified with the physical
photon before an action-owned broken electroweak saddle and mixing map exist.
"""

from __future__ import annotations

from typing import Any

import numpy as np


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "CURRENT_C2_LOWEST_WEYL_COEXACT_HYPERCHARGE_SOURCE_JET"

_S = np.asarray(((1.0, -1.0), (-1.0, 1.0)), dtype=complex)
_A = np.asarray(((2.0, 1.0), (1.0, 2.0)), dtype=complex)
_C = np.asarray(((-1.0, 0.0), (0.0, 1.0)), dtype=complex)
_SIGMA_Z = np.asarray(((1.0, 0.0), (0.0, -1.0)), dtype=complex)


def assemble_block_element_forms(elements: np.ndarray) -> dict[str, np.ndarray]:
    """Assemble two-node block elements after eliminating the far node."""

    values = np.asarray(elements, dtype=complex)
    if values.ndim != 3 or values.shape[1] != values.shape[2] or values.shape[1] % 2:
        raise ValueError("elements must have shape (segments,2d,2d)")
    if values.shape[0] < 1 or not np.all(np.isfinite(values)):
        raise ValueError("finite nonempty element family required")
    if not np.allclose(values, values.conj().transpose(0, 2, 1), atol=1.0e-13):
        raise ValueError("Hermitian element forms required")
    segments = values.shape[0]
    angular = values.shape[1] // 2
    diagonal = np.zeros((segments, angular, angular), dtype=complex)
    off_diagonal = np.zeros((max(segments - 1, 0), angular, angular), dtype=complex)
    for index, local in enumerate(values):
        diagonal[index] += local[:angular, :angular]
        if index + 1 < segments:
            diagonal[index + 1] += local[angular:, angular:]
            off_diagonal[index] += local[:angular, angular:]
    return {"diagonal_blocks": diagonal, "off_diagonal_blocks": off_diagonal}


def lowest_weyl_coexact_hypercharge_source_jet(
    *,
    proper_durations: np.ndarray,
    inverse_radii: np.ndarray,
    source_profile: np.ndarray,
    chirality: int,
) -> dict[str, Any]:
    """Return exact K, dK, and d2K blocks for the n=0 U(1)_Y source.

    At ``n=0`` the round Berger spatial Dirac block is
    ``D_e=(3/2) R_e^-1 I2``.  For the two squared first-order factors, write

    ``W_e(epsilon)=s[D_e+epsilon p_e sigma_z]`` with ``s=+/-1``.

    Differentiating the nonuniform finite-element form gives the exact
    transverse spatial source vertex and contact term on the current C2 core.
    """

    h = np.asarray(proper_durations, dtype=float)
    inverse = np.asarray(inverse_radii, dtype=float)
    profile = np.asarray(source_profile, dtype=float)
    sign = int(chirality)
    if (
        h.ndim != 1
        or inverse.shape != h.shape
        or profile.shape != h.shape
        or h.size < 1
        or np.any(h <= 0.0)
        or np.any(inverse <= 0.0)
        or not np.all(np.isfinite(h))
        or not np.all(np.isfinite(inverse))
        or not np.all(np.isfinite(profile))
        or sign not in (-1, 1)
    ):
        raise ValueError("positive finite C2 elements, profiles, and chirality +/-1 required")

    identity = np.eye(2, dtype=complex)
    background_elements = []
    vertex_elements = []
    contact_elements = []
    spatial_values = 1.5 * inverse
    for duration, spatial, source in zip(h, spatial_values, profile, strict=True):
        mass = duration * _A / 6.0
        W = sign * spatial * identity
        delta_W = sign * source * _SIGMA_Z
        background_elements.append(
            np.kron(_S / duration, identity)
            + np.kron(mass, W @ W)
            + np.kron(_C, W)
        )
        vertex_elements.append(
            np.kron(mass, W @ delta_W + delta_W @ W)
            + np.kron(_C, delta_W)
        )
        contact_elements.append(np.kron(mass, 2.0 * delta_W @ delta_W))

    background_array = np.asarray(background_elements)
    vertex_array = np.asarray(vertex_elements)
    contact_array = np.asarray(contact_elements)
    background = assemble_block_element_forms(background_array)
    vertex = assemble_block_element_forms(vertex_array)
    contact = assemble_block_element_forms(contact_array)
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "angular_level": 0,
        "angular_dimension": 2,
        "spatial_Dirac_block": "(3/2)*R4^-1*I2",
        "unit_source_generator": "sigma_z",
        "source_kind": "SPATIAL_COEXACT_U1_HYPERCHARGE",
        "chirality": sign,
        "segments": int(h.size),
        "background_elements": background_array,
        "vertex_elements": vertex_array,
        "contact_elements": contact_array,
        "background_diagonal_blocks": background["diagonal_blocks"],
        "background_off_diagonal_blocks": background["off_diagonal_blocks"],
        "vertex_diagonal_blocks": vertex["diagonal_blocks"],
        "vertex_off_diagonal_blocks": vertex["off_diagonal_blocks"],
        "contact_diagonal_blocks": contact["diagonal_blocks"],
        "contact_off_diagonal_blocks": contact["off_diagonal_blocks"],
        "first_derivative_exact": True,
        "second_contact_derivative_exact": True,
        "source_generator_traceless": bool(np.trace(_SIGMA_Z) == 0.0),
        "source_generator_square_is_identity": bool(
            np.array_equal(_SIGMA_Z @ _SIGMA_Z, identity)
        ),
        "physical_photon_identified": False,
        "explicit_inverse_formed": False,
    }


def coexact_hypercharge_puzzle_ledger() -> dict[str, Any]:
    return {
        "advanced_sections": {
            "full_field_action": [
                "current_C2_lowest_Weyl_U1Y_coexact_fermion_source_jet",
                "current_C2_lowest_Weyl_U1Y_contact_jet",
            ],
            "muon_magnetic_moment": [
                "transverse_hypercharge_precursor_vertex_on_current_C2_core"
            ],
            "collisions_and_decays": [
                "current_C2_hypercharge_fermion_source_vertex_precursor"
            ],
        },
        "unfitted_interfaces": {
            "full_field_action": [
                "dynamical_U1Y_gauge_kinetic_and_ghost_block_on_current_C2",
                "broken_SU2L_x_U1Y_saddle_and_neutral_mixing_map",
                "maximal_history_exterior_operator",
            ],
            "muon_magnetic_moment": [
                "action_selected_muon_pole",
                "physical_photon_vertex_after_electroweak_mixing",
                "Ward_identity_renormalization_and_complete_loops",
            ],
        },
        "U1Y_source_jet_derived": True,
        "physical_electromagnetic_vertex_derived": False,
        "muon_magnetic_moment_derived": False,
        "prediction_emitted": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "assemble_block_element_forms",
    "coexact_hypercharge_puzzle_ledger",
    "lowest_weyl_coexact_hypercharge_source_jet",
]
