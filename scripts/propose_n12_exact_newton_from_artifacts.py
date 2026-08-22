"""Form one proposal-only exact-normal Newton state from validated artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ORDER = 12
SOURCE = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT",
    ".tmp_direct_n12_exact_identity_constraint_proposal.npz",
))
RESIDUAL = Path(os.environ.get(
    "BHSM_N12_RESIDUAL_RESULT",
    ".tmp_direct_n12_exact_identity_final_residual.json",
))
PROPOSAL = Path(os.environ.get(
    "BHSM_N12_NEWTON_PROPOSAL",
    ".tmp_direct_n12_exact_identity_newton_proposal.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_NEWTON_PROPOSAL_RESULT",
    ".tmp_direct_n12_exact_identity_newton_proposal.json",
))


def main() -> None:
    source = np.load(SOURCE)
    state = np.asarray(source["state"], dtype=float)
    jacobian = np.asarray(source["paired_jacobian"], dtype=float)
    payload = json.loads(RESIDUAL.read_text(encoding="utf-8"))
    rows = np.asarray(payload["exact_residual_vector"], dtype=float)
    qdim = dimensions(ORDER)["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    joint_weights = np.concatenate((weights, weights))
    u, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
    correction = vh.T @ ((u.T @ (-rows)) / singular)
    proposed = state + correction / joint_weights
    np.savez(
        PROPOSAL,
        state=proposed,
        n6_ordered_branch_index=source["n6_ordered_branch_index"],
        branch_reference=source["branch_reference"],
        soft_right_direction=vh[-1],
    )
    result = {
        "classification": "N12_EXACT_NORMAL_NEWTON_PROPOSAL_ONLY",
        "source_checkpoint": str(SOURCE),
        "source_exact_residual": str(RESIDUAL),
        "proposal_checkpoint": str(PROPOSAL),
        "source_exact_F12_norm": float(np.linalg.norm(rows)),
        "normal_rank": int(np.count_nonzero(singular > (
            np.finfo(float).eps * max(jacobian.shape) * singular[0]
        ))),
        "smallest_normal_singular_value": float(singular[-1]),
        "action_coordinate_correction_norm": float(np.linalg.norm(correction)),
        "predicted_linear_residual_norm": float(np.linalg.norm(
            rows + jacobian @ correction
        )),
        "exact_candidate_evaluation_required_before_acceptance": True,
        "new_physics_equation_constraint_gate_scale_or_fit": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
