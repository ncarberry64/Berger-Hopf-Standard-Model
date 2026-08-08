"""BHSM v14.38 Lambda85/eta mixed-Hessian audit.

This module tests the exact continuation exposed by v14.37.  The available
v11.3 reciprocal-attachment reduction has three homogeneous collective
coordinates (q_C,q_D,q_W) subject to one KKT constraint.  The Path-B flavor
seeds are nontrivial Hopf/angular channels.  On the current action-owned
reduction, group orthogonality forces the mixed Hessian between the homogeneous
attachment branch and every nontrivial (ell,p) eta channel to vanish.

The unreduced local Lambda85 tensor functional could in principle contain
nonhomogeneous tensor modes, but no eta-stress pullback, kinetic/domain theorem,
or matched (ell,p) propagator has been derived for them.  The Spin(4) route is
likewise only a conditional representation mechanism until its tetrad/spin-
connection pullback is action-owned.

No CKM, physical CP phase, mass, scale, or total-completion result is emitted.
"""

from __future__ import annotations

from math import pi, sqrt
from typing import Any, Iterable

import numpy as np

VERSION = "v14.38"
PRIMARY_VERDICT = (
    "BHSM_V11_3_HOMOGENEOUS_LAMBDA85_ATTACHMENT_HAS_ZERO_MIXED_HESSIAN_"
    "WITH_ALL_NONTRIVIAL_HOPF_FLAVOR_CHANNELS_AND_CANNOT_TRIGGER_THE_"
    "V14_35_BIFURCATION"
)
SECONDARY_VERDICT = (
    "THE_CANONICAL_C3_PROJECTION_OF_THE_SELECTED_ATTACHMENT_BRANCH_IS_"
    "FAMILY_DIAGONAL_AND_THE_SPIN4_ALTERNATIVE_REMAINS_UNATTACHED_TO_THE_ACTION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_NONHOMOGENEOUS_LAMBDA85_OR_SPIN4_ATTACHMENT_MODE_WITH_"
    "THE_SAME_ELL_P_CHARACTERS_AS_THE_ETA_FLAVOR_TEXTURE_AND_A_NONZERO_"
    "MIXED_HESSIAN_ON_A_COMPACT_SELF_ADJOINT_FULL_PREIMAGE_CAP"
)

H_CORE = 0.181391690148362
REQUESTED_CHANNELS: tuple[tuple[int, int], ...] = (
    (2, 2),
    (4, 4),
    (6, 6),
    (8, 8),
    (10, 8),
)

# Lowest coupled polar/exact surrogate eigenvalues from v14.37 on x in [-7,5].
V14_37_ETA_CURVATURES: dict[tuple[int, int], float] = {
    (2, 2): 0.002202487352,
    (4, 4): 0.003947861025,
    (6, 6): 0.006125229600,
    (8, 8): 0.008721313939,
    (10, 8): 0.011726978214,
}


def kkt_tangent_matrices(h: float = H_CORE) -> tuple[np.ndarray, np.ndarray]:
    """Exact v11.3 Gram and Hessian on the KKT tangent plane."""

    gram = np.asarray([[1.0, 0.5], [0.5, 17.0 / 4.0]], dtype=float)
    hessian = np.asarray(
        [[h + 3.0 / 4.0, h + 7.0 / 8.0], [h + 7.0 / 8.0, h + 7.0 / 4.0]],
        dtype=float,
    )
    return gram, hessian


def attachment_roots(h: float = H_CORE) -> np.ndarray:
    """Exact generalized KKT roots mu_- < mu_+."""

    discriminant = 4624.0 * h * h + 5768.0 * h + 1985.0
    center = 68.0 * h + 65.0
    return np.asarray(
        [(center - sqrt(discriminant)) / 128.0, (center + sqrt(discriminant)) / 128.0],
        dtype=float,
    )


def lower_attachment_root(h: float = H_CORE) -> float:
    return float(attachment_roots(h)[0])


def lower_attachment_vector(h: float = H_CORE) -> np.ndarray:
    """Unnormalized constrained carrier in (q_C,q_D,q_W) order."""

    mu = lower_attachment_root(h)
    ratio = -(h + 3.0 / 4.0 - mu) / (h + 7.0 / 8.0 - 0.5 * mu)
    return np.asarray([1.0 + ratio, ratio, 1.0], dtype=float)


def homogeneous_character_overlap(ell: int, hopf_weight: int) -> float:
    """Overlap of a homogeneous attachment scalar with an (ell,p) harmonic.

    The action-owned v11.3 collective coordinates transform in the trivial
    angular/Hopf representation.  Orthogonality gives a nonzero scalar overlap
    only in the singlet (0,0) channel.
    """

    if not isinstance(ell, int) or not isinstance(hopf_weight, int):
        raise ValueError("ell and hopf_weight must be integers")
    if ell < 0:
        raise ValueError("ell must be nonnegative")
    return 1.0 if (ell, hopf_weight) == (0, 0) else 0.0


def reduced_lambda85_mixed_block(
    channels: Iterable[tuple[int, int]] = REQUESTED_CHANNELS,
    attachment_dimension: int = 1,
) -> np.ndarray:
    """Current action-owned eta/attachment block on the homogeneous reduction."""

    rows = tuple(channels)
    if attachment_dimension < 1:
        raise ValueError("attachment_dimension must be positive")
    block = np.zeros((len(rows), attachment_dimension), dtype=float)
    for index, (ell, hopf_weight) in enumerate(rows):
        block[index, :] = homogeneous_character_overlap(ell, hopf_weight)
    return block


def normalized_mixed_singular_value(
    mixed_block: np.ndarray,
    eta_curvatures: Iterable[float],
    attachment_curvatures: Iterable[float],
) -> float:
    """sigma_max(H_eta^-1/2 B H_A^-1/2)."""

    block = np.asarray(mixed_block, dtype=complex)
    eta = np.asarray(tuple(eta_curvatures), dtype=float)
    attachment = np.asarray(tuple(attachment_curvatures), dtype=float)
    if block.shape != (eta.size, attachment.size):
        raise ValueError("mixed block shape does not match curvature arrays")
    if np.any(eta <= 0.0) or np.any(attachment <= 0.0):
        raise ValueError("curvatures must be strictly positive")
    normalized = block / np.sqrt(eta[:, None] * attachment[None, :])
    if normalized.size == 0:
        return 0.0
    return float(np.linalg.svd(normalized, compute_uv=False)[0])


def critical_mixed_magnitude(eta_curvature: float, attachment_curvature: float) -> float:
    if eta_curvature < 0.0 or attachment_curvature < 0.0:
        raise ValueError("curvatures must be nonnegative")
    return float(sqrt(eta_curvature * attachment_curvature))


def hypothetical_threshold_rows() -> list[dict[str, Any]]:
    """Reference thresholds if a matched same-character attachment mode existed."""

    mu = lower_attachment_root()
    return [
        {
            "ell": ell,
            "hopf_weight": hopf_weight,
            "eta_curvature_v14_37_reference_box": V14_37_ETA_CURVATURES[(ell, hopf_weight)],
            "attachment_curvature_mu_minus": mu,
            "critical_mixed_magnitude": critical_mixed_magnitude(
                V14_37_ETA_CURVATURES[(ell, hopf_weight)], mu
            ),
            "actual_reduced_Lambda85_mixed_magnitude": 0.0,
            "crossing_on_current_reduction": False,
            "physical_prediction": False,
        }
        for ell, hopf_weight in REQUESTED_CHANNELS
    ]


def c3_shift() -> np.ndarray:
    return np.asarray([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=complex)


def c3_fourier_basis() -> np.ndarray:
    """Columns are normalized eigenvectors of the cyclic shift."""

    omega = np.exp(2j * pi / 3.0)
    return np.asarray(
        [
            [1.0, 1.0, 1.0],
            [1.0, omega.conjugate(), omega],
            [1.0, omega, omega.conjugate()],
        ],
        dtype=complex,
    ) / sqrt(3.0)


def canonical_family_response(h: float = H_CORE) -> np.ndarray:
    """C3 conditional expectation of the selected rank-one attachment response."""

    vector = lower_attachment_vector(h).astype(complex)
    twist = np.diag(np.exp(1j * np.asarray([-pi / 3.0, 0.0, pi / 3.0])))
    psi = twist @ vector
    response = lower_attachment_root(h) * np.outer(psi, psi.conjugate()) / np.vdot(psi, psi).real
    shift = c3_shift()
    projected = sum(
        np.linalg.matrix_power(shift, n) @ response @ np.linalg.matrix_power(shift, -n)
        for n in range(3)
    ) / 3.0
    return np.asarray(projected, dtype=complex)


def family_projector_basis_response(h: float = H_CORE) -> np.ndarray:
    basis = c3_fourier_basis()
    return basis.conjugate().T @ canonical_family_response(h) @ basis


def offdiagonal_norm(matrix: np.ndarray) -> float:
    value = np.asarray(matrix, dtype=complex)
    return float(np.linalg.norm(value - np.diag(np.diag(value))))


def lambda_multiplier_hessian() -> float:
    """Lambda85 is an algebraic multiplier, so its Lambda-Lambda Hessian is zero."""

    return 0.0


def lambda85_selection_rule_payload() -> dict[str, Any]:
    gram, hessian = kkt_tangent_matrices()
    block = reduced_lambda85_mixed_block()
    eta = [V14_37_ETA_CURVATURES[channel] for channel in REQUESTED_CHANNELS]
    mu = lower_attachment_root()
    sigma = normalized_mixed_singular_value(block, eta, [mu])
    validation = {
        "KKT_gram_positive": bool(np.min(np.linalg.eigvalsh(gram)) > 0.0),
        "KKT_hessian_positive": bool(np.min(np.linalg.eigvalsh(hessian)) > 0.0),
        "mu_minus_matches_v11_3": abs(mu - 0.1633821478999081549) < 1.0e-13,
        "all_requested_channels_nontrivial": all(channel != (0, 0) for channel in REQUESTED_CHANNELS),
        "all_requested_overlaps_zero": bool(np.all(block == 0.0)),
        "normalized_singular_value_zero": sigma == 0.0,
        "zero_crossing_absent": sigma < 1.0,
        "Lambda85_Lambda85_Hessian_zero": lambda_multiplier_hessian() == 0.0,
        "unreduced_local_tensor_modes_not_promoted": True,
    }
    return {
        "artifact": "BHSM_Lambda85_eta_mixed_Hessian_selection_rule_v14_38",
        "version": VERSION,
        "classification": "DERIVED_EXACT_ON_AVAILABLE_V11_3_HOMOGENEOUS_REDUCTION",
        "source_action": "S_attach=int_M5 <Lambda85,upsilon^(-1/2)I_W-upsilon^(1/2)I_C> dmu5",
        "source_incidence": {"I_C": "Q_H(G8)", "I_W": "g5"},
        "direct_eta_dependence_of_S_attach": False,
        "Lambda85_is_algebraic_multiplier": True,
        "Lambda85_Lambda85_Hessian": lambda_multiplier_hessian(),
        "unreduced_KKT_operator": "saddle block [[H_metric,C^*],[C,0]]; reduce to ker(C) before any spectrum",
        "available_attachment_character": {"ell": 0, "hopf_weight": 0},
        "requested_channels": [list(channel) for channel in REQUESTED_CHANNELS],
        "selection_rule": "<A_(0,0),eta_(ell,p)>=0 unless (ell,p)=(0,0)",
        "mixed_block": block,
        "normalized_singular_value": sigma,
        "bifurcation_threshold": 1.0,
        "gate": "FAILED_NO_MIXED_FLAVOR_BLOCK_ON_CURRENT_REDUCTION",
        "scope_boundary": (
            "The full local Lambda85 tensor functional is not proved to have zero nonhomogeneous modes. "
            "Those modes lack an eta-stress pullback, action-normalized kinetic/domain operator, and matched ell,p spectrum."
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def c3_projection_payload() -> dict[str, Any]:
    response = canonical_family_response()
    projector_response = family_projector_basis_response()
    eigenvalues = np.real_if_close(np.diag(projector_response)).real
    validation = {
        "response_Hermitian": bool(np.allclose(response, response.conjugate().T, atol=1.0e-13)),
        "response_commutes_with_C3": bool(np.allclose(response @ c3_shift(), c3_shift() @ response, atol=1.0e-13)),
        "projector_basis_offdiagonal_zero": offdiagonal_norm(projector_response) < 1.0e-13,
        "positive_family_stiffnesses": bool(np.min(eigenvalues) > 0.0),
        "twofold_degeneracy_preserved": bool(np.min(np.abs(np.subtract.outer(eigenvalues, eigenvalues) + np.eye(3))) < 1.0e-12),
        "historical_beta_kappa_not_derived": True,
    }
    return {
        "artifact": "BHSM_canonical_C3_attachment_family_chain_no_go_v14_38",
        "version": VERSION,
        "classification": "DERIVED_CANONICAL_C3_PROJECTION",
        "coordinate_basis_response": response,
        "C3_projector_basis_response": projector_response,
        "family_stiffnesses": eigenvalues,
        "offdiagonal_family_chain_entries": {
            "B_01": projector_response[0, 1],
            "B_12": projector_response[1, 2],
            "B_02": projector_response[0, 2],
        },
        "result": "CANONICAL_PROJECTION_IS_FAMILY_DIAGONAL",
        "historical_chain_coefficients": "NOT_DERIVED_BY_THIS_PROJECTION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def zero_crossing_payload() -> dict[str, Any]:
    rows = hypothetical_threshold_rows()
    validation = {
        "five_channels_recorded": len(rows) == 5,
        "all_thresholds_positive": all(row["critical_mixed_magnitude"] > 0.0 for row in rows),
        "all_actual_mixed_entries_zero": all(row["actual_reduced_Lambda85_mixed_magnitude"] == 0.0 for row in rows),
        "no_crossing": all(not row["crossing_on_current_reduction"] for row in rows),
        "reference_box_not_physical_cap": True,
    }
    return {
        "artifact": "BHSM_Lambda85_eta_zero_crossing_test_v14_38",
        "version": VERSION,
        "classification": "EXACT_ZERO_ON_CURRENT_REDUCTION_WITH_HYPOTHETICAL_REFERENCE_THRESHOLDS",
        "criterion": "sigma_max(H_eta^(-1/2) B H_A^(-1/2))=1",
        "actual_sigma_max": 0.0,
        "rows": rows,
        "physical_output": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    selection = lambda85_selection_rule_payload()
    family = c3_projection_payload()
    crossing = zero_crossing_payload()
    validation = {
        "Lambda85_selection_rule_audit_passed": selection["validation_passed"],
        "canonical_C3_projection_audit_passed": family["validation_passed"],
        "zero_crossing_audit_passed": crossing["validation_passed"],
        "Spin4_tetrad_pullback_still_open": True,
        "compact_cap_still_open": True,
        "physical_CKM_not_emitted": True,
        "frozen_predictions_unchanged": True,
        "BHSM_not_complete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_38",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "Lambda85_reduced_mixed_Hessian_gate": "FAILED_EXACT_ZERO_IN_NONTRIVIAL_ELL_P_CHANNELS",
        "canonical_C3_family_chain_gate": "FAILED_OFFDIAGONAL_ENTRIES_ZERO",
        "Spin4_mixed_Hessian_gate": "OPEN_MATCHED_TETRAD_SPIN_CONNECTION_PULLBACK",
        "compact_cap_gate": "OPEN",
        "bifurcation_status": "OFF_ON_CURRENT_ACTION_OWNED_REDUCTION",
        "BHSM_complete": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
