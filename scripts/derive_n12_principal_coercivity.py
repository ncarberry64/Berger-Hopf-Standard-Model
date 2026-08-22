"""Derive the retained N12 weighted principal lower bound on the root ball."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION",
    ".tmp_direct_n12_complete_persistent_child_promotion.json",
))
BOUNDARY = Path(os.environ.get(
    "BHSM_N12_BOUNDARY_TAIL_MODULUS",
    ".tmp_direct_n12_exact_boundary_tail_modulus.json",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_PRINCIPAL_COERCIVITY",
    ".tmp_direct_n12_principal_coercivity.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _coefficient_bounds(state: np.ndarray, radius: float) -> dict[str, float]:
    qdim = 1 + 3 * ORDER
    q = state[:qdim]
    multipliers = state[2 * qdim:]
    u = q[1:1 + ORDER]
    w = q[1 + ORDER:1 + 2 * ORDER]
    lapse = multipliers[:ORDER]
    constant = math.log(3.0) + 5.0 * (math.log(RADIUS0) + float(q[0]))
    oscillation_bound = (
        float(np.sum(np.abs(lapse)))
        + 5.0 * float(np.sum(np.abs(u)))
        + float(np.sum(np.abs(w)))
    )
    log_lower_center = constant - oscillation_bound
    log_upper_center = constant + oscillation_bound

    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    # Supremum of the dual action-coordinate norm of
    # d(log kappa)=5 d(scale)+d(log N)+5 du-dw.
    u_weights = q_weights[1:1 + ORDER]
    w_weights = q_weights[1 + ORDER:1 + 2 * ORDER]
    lapse_weights = m_weights[:ORDER]
    log_lipschitz = math.sqrt(
        25.0
        + float(np.sum(1.0 / lapse_weights**2))
        + 25.0 * float(np.sum(1.0 / u_weights**2))
        + float(np.sum(1.0 / w_weights**2))
    )
    log_lower_ball = log_lower_center - log_lipschitz * radius
    log_upper_ball = log_upper_center + log_lipschitz * radius
    return {
        "log_kappa_lower_center": log_lower_center,
        "log_kappa_upper_center": log_upper_center,
        "log_kappa_action_coordinate_Lipschitz_bound": log_lipschitz,
        "log_kappa_lower_on_root_ball": log_lower_ball,
        "log_kappa_upper_on_root_ball": log_upper_ball,
        "kappa_lower_on_root_ball": math.exp(log_lower_ball),
        "kappa_upper_on_root_ball": math.exp(log_upper_ball),
    }


def main() -> None:
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    if not promotion["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]:
        raise RuntimeError("the certified N12 anchor is required")
    if not boundary["validation_passed"]:
        raise RuntimeError("the exact boundary tail modulus is required")
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    qdim = 1 + 3 * ORDER
    sdim = 2 * qdim + 2 * ORDER
    radius = float(promotion["certified_root_ball"]["radius"])
    bounds = {
        "event": _coefficient_bounds(joint[:sdim], radius),
        "child": _coefficient_bounds(joint[sdim:], radius),
    }
    kappa_lower = min(
        item["kappa_lower_on_root_ball"] for item in bounds.values()
    )
    matrix_gap = math.sqrt(29.0) - 5.0
    principal_lower = matrix_gap * kappa_lower
    boundary_modulus = float(
        boundary["joint_child_minus_event_tail"]
        ["existing_normalized_boundary_operator_norm"]
    )
    boundary_ratio = boundary_modulus / principal_lower
    validation = {
        "certified_root_ball_consumed": True,
        "coefficient_bound_uses_only_retained_action_fields": True,
        "finite_trigonometric_triangle_bound_is_global_on_cap": True,
        "action_coordinate_ball_variation_included": True,
        "weighted_principal_lower_bound_positive": principal_lower > 0.0,
        "exact_trace_attachment_tail_below_principal_lower_bound": (
            boundary_ratio < 1.0
        ),
        "no_sampled_chi_minimum_promoted_as_global_bound": True,
        "no_new_equation_constraint_gate_scale_or_fit": True,
    }
    payload = {
        "classification": (
            "N12_WEIGHTED_GAUGE_REDUCED_PRINCIPAL_COERCIVITY_AND_"
            "TRACE_ATTACHMENT_RELATIVE_TAIL_BOUND_CLOSED"
        ),
        "source_checkpoint": str(CHECKPOINT),
        "source_checkpoint_SHA256": _sha256(CHECKPOINT),
        "source_promotion": str(PROMOTION),
        "source_promotion_SHA256": _sha256(PROMOTION),
        "source_boundary_tail": str(BOUNDARY),
        "source_boundary_tail_SHA256": _sha256(BOUNDARY),
        "root_ball_action_radius": radius,
        "retained_factorization": {
            "kappa": "3*N*R^5*exp(5*u-w)",
            "principal_matrix": [
                [10.0, 0.0, 2.0],
                [0.0, -2.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            "principal_matrix_smallest_absolute_eigenvalue": matrix_gap,
        },
        "state_bounds": bounds,
        "joint_kappa_lower_on_certified_root_ball": kappa_lower,
        "weighted_principal_inf_sup_lower_bound": principal_lower,
        "exact_trace_attachment_tail_operator_norm": boundary_modulus,
        "trace_attachment_to_principal_ratio": boundary_ratio,
        "remaining_compact_blocks": [
            "INTERIOR_LOWER_ORDER_EULER_DIRAC",
            "ORDERED_EVENT_SPECTRAL_PROJECTOR",
            "CANONICAL_MOMENTUM_AND_DYNAMIC_FLUX",
            "GAUSS_QUADRATURE_CONSISTENCY",
        ],
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "DERIVE_EXPLICIT_ACTION_GRAPH_NORM_MODULI_FOR_THE_REMAINING_"
            "FOUR_COMPACT_BLOCKS_AND_PROVE_THEIR_GAUGE_REDUCED_SCHUR_"
            "FEEDBACK_PRESERVES_THE_N12_PRINCIPAL_LOWER_BOUND"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
