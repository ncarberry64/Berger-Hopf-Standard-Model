"""Short proposal-only LM/Broyden transport for the exact-identity N12 map."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)
from propose_n12_quadrature_constraint_correction import (
    ORDER,
    _normalized_rows,
)


STEPS = int(os.environ.get("BHSM_N12_CACHED_LM_STEPS", "6"))
DROP_CACHED_J_ON_EXIT = os.environ.get(
    "BHSM_N12_DROP_CACHED_J_ON_EXIT", "0"
) == "1"
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    ".tmp_direct_n12_exact_identity_constraint_proposal.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_CACHED_LM_RESULT",
    ".tmp_direct_n12_exact_identity_cached_lm.json",
))


def _eta(joint: np.ndarray) -> tuple[float, float]:
    qdim = dimensions(ORDER)["coordinates"]
    sdim = 2 * qdim + dimensions(ORDER)["multipliers"]
    event = joint[:sdim]
    child = joint[sdim:]
    return (
        _eta_legendre_minimum(
            ORDER, event[:qdim], event[2 * qdim:], points=2000
        )["minimum"],
        _eta_legendre_minimum(
            ORDER, child[:qdim], child[2 * qdim:], points=2000
        )["minimum"],
    )


def main() -> None:
    source = np.load(CHECKPOINT)
    state = np.asarray(source["state"], dtype=float)
    reference = np.asarray(source["branch_reference"], dtype=float)
    reference /= np.linalg.norm(reference)
    jacobian = np.asarray(source["paired_jacobian"], dtype=float).copy()
    qdim = dimensions(ORDER)["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    state_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    joint_weights = np.concatenate((state_weights, state_weights))
    rows = _normalized_rows(state, reference)
    history = []
    for iteration in range(STEPS):
        singular = np.linalg.svd(jacobian, compute_uv=False)
        sigma = float(singular[-1])
        old_norm = float(np.linalg.norm(rows))
        candidates = []
        for multiple in (0.25, 1.0, 4.0, 16.0, 64.0):
            damping = max(1.0e-12, multiple * sigma)
            correction = -jacobian.T @ np.linalg.solve(
                jacobian @ jacobian.T
                + damping**2 * np.eye(jacobian.shape[0]),
                rows,
            )
            predicted_change = jacobian @ correction
            for factor in (1.0, 0.5, 0.25, 0.125):
                action_step = factor * correction
                candidate_state = state + action_step / joint_weights
                event_eta, child_eta = _eta(candidate_state)
                if event_eta <= 0.0 or child_eta <= 0.0:
                    continue
                candidate_rows = _normalized_rows(candidate_state, reference)
                candidate_norm = float(np.linalg.norm(candidate_rows))
                predicted = rows + factor * predicted_change
                predicted_reduction = old_norm - float(np.linalg.norm(predicted))
                actual_reduction = old_norm - candidate_norm
                candidates.append({
                    "state": candidate_state,
                    "rows": candidate_rows,
                    "norm": candidate_norm,
                    "multiple": multiple,
                    "damping": damping,
                    "factor": factor,
                    "action_step": action_step,
                    "event_eta": event_eta,
                    "child_eta": child_eta,
                    "actual_predicted_ratio": (
                        actual_reduction / predicted_reduction
                        if predicted_reduction > 0.0 else None
                    ),
                })
        improving = [item for item in candidates if item["norm"] < old_norm]
        if not improving:
            history.append({
                "iteration": iteration,
                "exact_norm_before": old_norm,
                "accepted": False,
                "reason": "NO_EXACT_ADMISSIBLE_CACHED_MODEL_DESCENT",
                "cached_sigma_min": sigma,
            })
            break
        best = min(improving, key=lambda item: item["norm"])
        old_state = state
        old_rows = rows
        state = best["state"]
        rows = best["rows"]
        action_secant = (state - old_state) * joint_weights
        residual_secant = rows - old_rows
        model_secant = jacobian @ action_secant
        defect = residual_secant - model_secant
        denominator = float(action_secant @ action_secant)
        normalized_defect = float(
            np.linalg.norm(defect) / max(1.0e-30, np.linalg.norm(residual_secant))
        )
        if denominator > 0.0:
            jacobian += np.outer(defect, action_secant) / denominator
        history.append({
            "iteration": iteration,
            "exact_norm_before": old_norm,
            "exact_norm_after": best["norm"],
            "exact_reduction": old_norm - best["norm"],
            "accepted": True,
            "LM_sigma_multiple": best["multiple"],
            "LM_damping": best["damping"],
            "step_factor": best["factor"],
            "action_step_norm": float(np.linalg.norm(best["action_step"])),
            "event_eta": best["event_eta"],
            "child_eta": best["child_eta"],
            "actual_predicted_reduction_ratio": best[
                "actual_predicted_ratio"
            ],
            "normalized_Broyden_secant_defect": normalized_defect,
            "cached_sigma_min_before": sigma,
        })
    event_eta, child_eta = _eta(state)
    saved = {
        "state": state,
        "n6_ordered_branch_index": source["n6_ordered_branch_index"],
        "branch_reference": reference,
        "soft_right_direction": source["soft_right_direction"],
        "recent_accepted_states": np.asarray([state]),
    }
    if not DROP_CACHED_J_ON_EXIT:
        saved.update({
            "paired_j_full": source["paired_j_full"],
            "paired_j_half": source["paired_j_half"],
            "paired_jacobian": jacobian,
        })
    np.savez(CHECKPOINT, **saved)
    payload = {
        "classification": (
            "N12_EXACT_IDENTITY_CACHED_LM_DESCENT_ACCEPTED"
            if any(item["accepted"] for item in history) else
            "N12_EXACT_IDENTITY_CACHED_MODEL_STALE_REFRESH_REQUIRED"
        ),
        "source_and_updated_checkpoint": str(CHECKPOINT),
        "exact_corrected_F12_norm": float(np.linalg.norm(rows)),
        "exact_corrected_F12_maximum": float(np.max(np.abs(rows))),
        "event_eta_minimum": event_eta,
        "child_eta_minimum": child_eta,
        "accepted_steps": sum(bool(item["accepted"]) for item in history),
        "history": history,
        "exact_57_row_merit_authority": True,
        "cached_Jacobian_and_Broyden_are_proposal_only": True,
        "cached_Jacobian_dropped_for_required_exact_refresh": (
            DROP_CACHED_J_ON_EXIT
        ),
        "new_physics_equation_constraint_gate_scale_or_fit": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
