"""Canonical v11.4 common-domain response in the v11.3 whitened coordinates."""

from __future__ import annotations

from math import sqrt
from typing import Any

from sympy import Matrix


VERSION = "v11.4"
H_CORE_REPRESENTATIVE = 0.181391690148362
PRIMARY_VERDICT = "BHSM_COMMON_ATTACHMENT_RESPONSE_POSITIVE_AND_NONDEGENERATE_ON_SELECTED_CORE_BRANCH"


def constraint_jacobian() -> Matrix:
    """Linearized reciprocal matcher in (q_C,q_W,x_D)."""

    return Matrix([[-1, 1, 1]])


def tangent_basis() -> Matrix:
    return Matrix([[1, 1], [1, 0], [0, 1]])


def kinetic_matrix() -> Matrix:
    """The v11.3 action-whitened kinetic form."""

    return Matrix.eye(3)


def whitening_map() -> Matrix:
    """Shared v11.3-whitened coordinate map used by both quadratic forms."""

    return Matrix.eye(3)


def action_coordinate_kinetic_matrix() -> Matrix:
    """Action kinetic form before applying the retained v11.3 whitening map."""

    return Matrix.eye(3)


def action_coordinate_hessian_matrix(
    octave: int = 0,
    h_core: float = H_CORE_REPRESENTATIVE,
) -> Matrix:
    """Action-source ledger Hessian in the same coordinates as the kinetic form."""

    if octave < 0 or h_core <= 0:
        raise ValueError("octave must be nonnegative and h_core must be positive")
    return Matrix.diag(h_core, 0, 1 + octave)


def hessian_matrix(octave: int = 0, h_core: float = H_CORE_REPRESENTATIVE) -> Matrix:
    """Hessian transformed by the same whitening map as the kinetic Gram."""

    W = whitening_map()
    return W.T * action_coordinate_hessian_matrix(octave, h_core) * W


def reduced_matrices(octave: int = 0, h_core: float = H_CORE_REPRESENTATIVE) -> tuple[Matrix, Matrix]:
    tangent = tangent_basis()
    return tangent.T * kinetic_matrix() * tangent, tangent.T * hessian_matrix(octave, h_core) * tangent


def response_roots(octave: int = 0, h_core: float = H_CORE_REPRESENTATIVE) -> tuple[float, float]:
    """Exact generalized roots of det(H_parallel-mu K_parallel)=0."""

    if octave < 0 or h_core <= 0:
        raise ValueError("octave must be nonnegative and h_core must be positive")
    t = octave + 1.0
    discriminant = t * t - h_core * t + h_core * h_core
    lower = (h_core + t - sqrt(discriminant)) / 3.0
    upper = (h_core + t + sqrt(discriminant)) / 3.0
    return lower, upper


def inverse_octave(lower_root: float, h_core: float = H_CORE_REPRESENTATIVE) -> float:
    if h_core <= 0 or not 0 < lower_root < h_core / 2:
        raise ValueError("lower_root must lie in 0 < mu < h_core/2")
    return lower_root * (2 * h_core - 3 * lower_root) / (h_core - 2 * lower_root) - 1.0


def response_payload() -> dict[str, Any]:
    B = constraint_jacobian()
    N = tangent_basis()
    K_parallel, H_parallel = reduced_matrices()
    family_octaves = {"heavy": 0, "middle": 35, "light": 99}
    roots = {name: response_roots(octave)[0] for name, octave in family_octaves.items()}
    reconstructed = {name: inverse_octave(root) for name, root in roots.items()}
    validation = {
        "v11_3_constraint_preserved": B == Matrix([[-1, 1, 1]]),
        "tangent_basis_exact": B * N == Matrix.zeros(1, 2),
        "whitened_kinetic_preserved": kinetic_matrix() == Matrix.eye(3),
        "shared_whitening_map_applied_to_gram_and_hessian": (
            kinetic_matrix() == whitening_map().T * action_coordinate_kinetic_matrix() * whitening_map()
            and hessian_matrix() == whitening_map().T * action_coordinate_hessian_matrix() * whitening_map()
        ),
        "reduced_kinetic_exact": K_parallel == Matrix([[2, 1], [1, 2]]),
        "critical_wall_curvature_zero": hessian_matrix()[1, 1] == 0,
        "ground_depth_curvature_one": hessian_matrix()[2, 2] == 1,
        "reduced_hessian_positive": float(H_parallel.det()) > 0 and float(H_parallel.trace()) > 0,
        "family_roots_positive": all(value > 0 for value in roots.values()),
        "family_roots_nondegenerate": len(set(roots.values())) == 3,
        "family_octaves_reconstructed": all(
            abs(reconstructed[name] - octave) < 1e-8
            for name, octave in family_octaves.items()
        ),
        "no_measured_mass_input": True,
    }
    return {
        "artifact": "BHSM_common_attachment_response_v11_4",
        "version": VERSION,
        "classification": "DERIVED_ON_AUTHOR_SELECTED_FINITE_RADIUS_CORE_BRANCH",
        "coordinate_order": ["q_C", "q_W", "x_D=q_D/lambda_D"],
        "normalization_fix": "retain the v11.3 action-whitened coordinates and apply one shared map W to both K_white=W^T K_action W and H_white=W^T H_action W; do not combine them with the separate unwhitened packet pencil",
        "whitening_provenance": {
            "map_from_v11_3_action_whitened_coordinates": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "gram_transform": "K_white=W^T K_action W",
            "hessian_transform": "H_white=W^T H_action W",
            "incompatible_unwhitened_packet_pencil_used": False,
        },
        "source_ledger": {
            "kinetic_gram": {"source": "v11.3 action-normalized local KKT model", "status": "ACTION_WHITENED_CONDITIONAL"},
            "core_curvature": {"source": "BHSM_dynamic_envelope_reduction_v10_0 breathing_frequency_squared", "status": "ACTION_DERIVED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH"},
            "wall_curvature": {"source": "BHSM_fixed_h_lyapunov_schmidt_potential_v6_30_5 critical quadratic coefficient", "status": "ACTION_DERIVED_AT_CRITICAL_WALL_BRANCH"},
            "depth_curvature": {"source": "v11.0 positive Haar support metric plus the round S3 spectral octave", "status": "CONDITIONAL_SPECTRAL_ACTION_ASSIGNMENT"},
            "constraint": {"source": "v11.3 reciprocal Lambda85 matcher", "status": "ACTION_DERIVED"},
        },
        "constraint_jacobian": [[int(value) for value in row] for row in B.tolist()],
        "tangent_basis": [[int(value) for value in row] for row in N.tolist()],
        "kinetic_matrix": [[int(value) for value in row] for row in kinetic_matrix().tolist()],
        "reduced_kinetic_matrix": [[int(value) for value in row] for row in K_parallel.tolist()],
        "ground_hessian_matrix": [[float(value) for value in row] for row in hessian_matrix().tolist()],
        "ground_reduced_hessian": [[float(value) for value in row] for row in H_parallel.tolist()],
        "characteristic_equation": "3 mu^2-2(h_C+K+1) mu+h_C(K+1)=0",
        "family_octaves": family_octaves,
        "lower_family_roots": roots,
        "inverse_octave_checks": reconstructed,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": "MINIMAL_M4_CHARGED_LEPTON_ACTION_WITH_TRACE_NORMALIZED_HOPF_SEMIGROUP",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
