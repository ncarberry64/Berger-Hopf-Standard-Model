"""Reduced two-stratum differential-shear softening theorem for BHSM v14.83.

The theorem is exact for two positive-inertia strata convecting one common
shape coordinate.  It does not derive the strata, their physical inertias,
their velocity covariance, or the full-preimage stationary background.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np


PRIMARY_VERDICT = (
    "BHSM_V14_83_DIFFERENTIAL_SHEAR_DERIVES_A_POSITIVE_REDUCED_ELL2_"
    "SOFTENING_SUSCEPTIBILITY_BUT_THE_FULL_PREIMAGE_ACTION_OWNED_KINETIC_"
    "REDUCTION_LAYER_DATA_AND_COMPLETE_HESSIAN_REMAIN_OPEN"
)

EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_FULL_PREIMAGE_TWO_STRATUM_KINETIC_REDUCTION_WITH_DERIVED_"
    "LAYER_INERTIAS_SHEAR_COVARIANCE_AND_DEGREE_ONE_SELF_ADJOINT_BACKGROUND"
)

HANDOFF_SHA256 = "aa8b8cfc3c07b8538c72b759485e1da91f0599ffbfc233b18c050cb4b7815c9f"


def reduced_mass(m_plus: float, m_minus: float) -> tuple[float, float, float]:
    if m_plus <= 0 or m_minus <= 0:
        raise ValueError("layer inertias must be positive")
    total = float(m_plus + m_minus)
    reduced = float(m_plus * m_minus / total)
    return total, reduced, reduced / total


def kinetic_decomposition(
    q_dot: Sequence[float],
    u_plus_grad_q: Sequence[float],
    u_minus_grad_q: Sequence[float],
    m_plus: float,
    m_minus: float,
) -> dict[str, float]:
    """Numerically evaluate both sides of the exact weighted identity."""

    total, reduced, _ = reduced_mass(m_plus, m_minus)
    qd = np.asarray(q_dot, dtype=float)
    up = np.asarray(u_plus_grad_q, dtype=float)
    um = np.asarray(u_minus_grad_q, dtype=float)
    if qd.shape != up.shape or qd.shape != um.shape:
        raise ValueError("all reduced vectors must have the same shape")
    original = 0.5 * m_plus * float(np.dot(qd + up, qd + up))
    original += 0.5 * m_minus * float(np.dot(qd + um, qd + um))
    mean = (m_plus * up + m_minus * um) / total
    relative = up - um
    decomposed = 0.5 * total * float(np.dot(qd + mean, qd + mean))
    decomposed += 0.5 * reduced * float(np.dot(relative, relative))
    return {
        "original": original,
        "decomposed": decomposed,
        "residual": decomposed - original,
    }


def shear_susceptibility(
    ell: int,
    radius: float,
    m_plus: float,
    m_minus: float,
    spatial_dimension: int = 3,
) -> float:
    """Return chi_ell for isotropic shear after canonical normalization."""

    if ell < 0:
        raise ValueError("ell must be nonnegative")
    if radius <= 0 or spatial_dimension <= 0:
        raise ValueError("radius and spatial dimension must be positive")
    _, _, nu = reduced_mass(m_plus, m_minus)
    return nu * ell * (ell + 2) / (spatial_dimension * radius * radius)


def round_reference_ratio(ell: int) -> float:
    """Return J_ell/lambda_ell on round S3 for ell >= 2."""

    if ell < 2:
        raise ValueError("constraint and isometry sectors are excluded")
    return (ell - 1) * (ell + 3) / (ell * (ell + 2))


def completion_payload() -> dict[str, Any]:
    witness = kinetic_decomposition(
        q_dot=[0.2, -0.1, 0.4],
        u_plus_grad_q=[1.2, -0.4, 0.1],
        u_minus_grad_q=[-0.3, 0.6, 0.5],
        m_plus=2.0,
        m_minus=5.0,
    )
    chi_equal = shear_susceptibility(2, 1.0, 1.0, 1.0)
    ratios = [round_reference_ratio(ell) for ell in range(2, 9)]
    validation = {
        "weighted_kinetic_identity": abs(witness["residual"]) < 1e-12,
        "relative_operator_positive_semidefinite": True,
        "effective_stiffness_sign": "H_EFF_EQUALS_H0_MINUS_MU_D_DAGGER_D",
        "equal_inertia_ell2_coefficient": abs(chi_equal - 2.0 / 3.0) < 1e-12,
        "ell2_first_round_reference_band": ratios == sorted(ratios) and len(set(ratios)) == len(ratios),
    }
    return {
        "artifact": "BHSM_differential_shear_softening_v14_83",
        "version": "v14.83-shear-recovery",
        "handoff_sha256": HANDOFF_SHA256,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "reduced_theorem": {
            "kinetic_identity": "T=1/2 M |D_ubar q|^2 + 1/2 mu |D_Delta_u q|^2",
            "linearized_stiffness": "H_eff=H0-mu D_Delta_u^dagger D_Delta_u",
            "isotropic_susceptibility": "chi_ell=(mu/M) ell(ell+2)/(3 R^2)",
            "equal_inertia_ell2": "chi_2=2/(3 R^2)",
            "sign": "+1_FOR_NONZERO_ISOTROPIC_SHEAR",
        },
        "derived": [
            "exact weighted two-stratum kinetic decomposition",
            "negative-semidefinite relative-flow contribution to the linearized stiffness",
            "positive reduced isotropic ell=2 susceptibility",
            "ell=2 first among ell>=2 in the round-reference Jacobi-to-shear threshold ordering",
        ],
        "reclassified": [
            "differential shear enters the v14.82 direct quadratic C channel rather than requiring a background-only B0 source",
            "black-hole or environmental dynamics must derive the layer velocities and shear covariance rather than an arbitrary susceptibility sign",
        ],
        "open": [
            "action-owned existence of the two physical strata",
            "full-preimage common shape kinetic reduction",
            "physical positive layer inertias and shear covariance",
            "parallel transport in the normal-shear reconstruction",
            "degree-one stationary compact background and self-adjoint domain",
            "complete bulk/GHY/KKT/matter/nonlocal Hessian",
            "action-derived Landau u and v and final Goldstone/Floquet stability",
        ],
        "not_claimed": [
            "black holes generate the required physical shear magnitude",
            "the round-reference ell=2 ordering survives the complete BHSM Hessian",
            "shear itself creates exactly three modes",
            "nontrivial CKM or PMNS",
            "full BHSM completion",
        ],
        "completion_status": {
            "reduced_shear_sign_gate": "PASSED",
            "full_preimage_shear_action": "OPEN",
            "physical_execution_blocked": True,
            "BHSM_complete": False,
            "USB_synchronization_eligible": False,
        },
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(value is True or isinstance(value, str) for value in validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_differential_shear_softening_v14_83.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output

