"""Compact hindsight audit of the corrected N12 ordered-event closure.

This is a read-only diagnostic.  It does not evaluate a replacement residual,
modify the N12 checkpoint, or authorize a proposal.  In particular, the
decision about whether proposal-only shaking is warranted is inferred from
the already-recorded exact-merit history; it is not a new acceptance gate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(".")
OUTPUT = ROOT / ".tmp_direct_n12_exact_identity_hindsight_event_audit.json"
CHECKPOINT = ROOT / ".tmp_direct_n12_exact_identity_constraint_proposal.npz"
CONSTRAINT = ROOT / ".tmp_direct_n12_exact_identity_constraint_correction.json"
CACHED = ROOT / ".tmp_direct_n12_exact_identity_cached_lm.json"
LM1 = ROOT / ".tmp_direct_n12_exact_identity_lm_1.json"
LM2 = ROOT / ".tmp_direct_n12_exact_identity_lm_2.json"
FRESH = ROOT / ".tmp_direct_n12_exact_identity_final_fresh_center.json"
RESIDUAL = ROOT / ".tmp_direct_n12_exact_identity_final_residual.json"
EIGENLINE = ROOT / ".tmp_direct_n12_exact_identity_ordered_eigenline_ball_2e10.json"
PROFILE = ROOT / ".tmp_direct_n12_exact_identity_targeted_event_profile.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


constraint = load(CONSTRAINT)
cached = load(CACHED)
lm1 = load(LM1)
lm2 = load(LM2)
fresh = load(FRESH)
residual = load(RESIDUAL)
eigenline = load(EIGENLINE)
checkpoint = np.load(CHECKPOINT)
jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)
rows = np.asarray(residual["exact_residual_vector"], dtype=float)

event_row_index = 2 * 12 + 1
event_row = float(rows[event_row_index])
other_rows_norm = float(np.linalg.norm(np.delete(rows, event_row_index)))

# The proposal direction lies in the paired normal row-space and has minimal
# first-order disturbance of the other 56 rows.  This is diagnostic geometry,
# not a reduced physical equation.
_, singular, vh = np.linalg.svd(jacobian, full_matrices=False)
normal_basis = vh.T
other_jacobian = np.delete(jacobian, event_row_index, axis=0) @ normal_basis
_, _, other_vh = np.linalg.svd(other_jacobian, full_matrices=True)
coupled_normal_coordinates = other_vh.T[:, -1]
coupled_direction = normal_basis @ coupled_normal_coordinates
coupled_derivative = float(jacobian[event_row_index] @ coupled_direction)
linear_event_newton = (
    -event_row / coupled_derivative * coupled_direction
    if abs(coupled_derivative) > 0.0
    else np.full_like(coupled_direction, np.nan)
)

lm1_step = lm1["exact_merit_continuation"][0]
lm2_step = lm2["exact_merit_continuation"][0]
paired_steps = []
for source, record, start in (
    (LM1.name, lm1_step, float(lm1["center_norm"])),
    (LM2.name, lm2_step, float(lm2["center_norm"])),
):
    finish = float(record["exact_norm_after"])
    action_step = float(record["cumulative_action_norm"])
    paired_steps.append({
        "source": source,
        "exact_before": start,
        "exact_after": finish,
        "exact_reduction": start - finish,
        "reduction_factor": start / finish,
        "action_coordinate_step_norm": action_step,
        "exact_reduction_per_action_path": (
            (start - finish) / action_step if action_step > 0.0 else None
        ),
        "actual_predicted_reduction_ratio": record.get(
            "actual_to_predicted_reduction_ratio"
        ),
        "event_eta": record["event_eta"],
        "child_eta": record["child_eta"],
        "accepted": record["accepted"],
    })

profile_payload = None
if PROFILE.exists():
    profile = load(PROFILE)
    admissible = [row for row in profile["profile"] if row["admissible"]]
    signs = [float(row["signed_scaled_ordered_event_residual"]) for row in admissible]
    center_event = float(profile["center_signed_scaled_ordered_event_residual"])
    nonzero = [
        row for row in admissible
        if row["factor_of_linear_ordered_event_Newton_step"] != 0.0
    ]
    for row in admissible:
        factor = float(row["factor_of_linear_ordered_event_Newton_step"])
        row["linear_predicted_ordered_event_residual"] = (1.0 - factor) * center_event
        row["ordered_event_linear_prediction_defect"] = abs(
            float(row["signed_scaled_ordered_event_residual"])
            - row["linear_predicted_ordered_event_residual"]
        )
    best_nonzero = min(nonzero, key=lambda row: row["exact_full_residual"])
    smallest_event = min(nonzero, key=lambda row: abs(
        row["signed_scaled_ordered_event_residual"]
    ))
    profile_payload = {
        "source": PROFILE.name,
        "source_SHA256": sha256(PROFILE),
        "center_exact_full_residual": profile["center_exact_full_residual"],
        "center_signed_scaled_ordered_event_residual": profile[
            "center_signed_scaled_ordered_event_residual"
        ],
        "center_other_56_rows_norm": profile["center_other_56_rows_norm"],
        "paired_normal_rank": profile["paired_normal_rank"],
        "paired_smallest_normal_singular_value": profile[
            "paired_smallest_normal_singular_value"
        ],
        "coupled_ordered_event_derivative": profile[
            "coupled_ordered_event_derivative"
        ],
        "linear_ordered_event_Newton_action_norm": profile[
            "linear_ordered_event_Newton_action_norm"
        ],
        "best_admissible_sample": profile["best_admissible_sample"],
        "best_nonzero_sample": best_nonzero,
        "smallest_absolute_event_sample": smallest_event,
        "maximum_event_linear_prediction_defect": max(
            row["ordered_event_linear_prediction_defect"] for row in admissible
        ),
        "admissible_sign_change": bool(min(signs) <= 0.0 <= max(signs)),
        "sign_brackets": profile["ordered_event_sign_brackets"],
        "sign_change_promotable_as_root_evidence": False,
        "reason": (
            "No nonzero sample improves the full exact merit.  At these "
            "sub-4e-11 action steps, the event row and nominally nulled other "
            "rows depart from the paired first-order prediction by more than "
            "the intended event correction.  The observed sign oscillations "
            "therefore localize evaluator precision/noise, not a physical "
            "event crossing or positive floor."
        ),
    }

payload = {
    "classification": "N12_COUPLED_ORDERED_EVENT_HINDSIGHT_AUDITED",
    "scope": "CORRECTED_IDENTITY_RESPONSE_AND_VALIDATED_N6_BRANCH_12_ERA_ONLY",
    "measurement_era_separation": {
        "wrong_branch_or_trapezoidal_identity_histories_excluded": True,
        "reason": (
            "Those histories used a different branch selector and/or a "
            "quadrature-dependent approximation to the retained identity "
            "response; their residual values are not a descent chronology "
            "for the corrected evaluator."
        ),
        "stable_decimal_event_reevaluation_is_a_measurement_change": True,
        "cached_binary64_norm_before_stable_reevaluation": cached[
            "exact_corrected_F12_norm"
        ],
        "stable_decimal_same_checkpoint_norm": lm1["center_norm"],
    },
    "corrected_exact_merit_history": [
        {
            "stage": "pre_constraint_fiber",
            "exact_F12_norm": constraint["exact_normalized_full_residual_before"],
        },
        {
            "stage": "accepted_constraint_fiber",
            "exact_F12_norm": constraint["exact_normalized_full_residual_after"],
        },
        {
            "stage": "cached_binary64_transport_diagnostic",
            "exact_F12_norm": cached["exact_corrected_F12_norm"],
        },
        {
            "stage": "stable_decimal_paired_center",
            "exact_F12_norm": lm1["center_norm"],
        },
        {
            "stage": "paired_step_1",
            "exact_F12_norm": lm2["center_norm"],
        },
        {
            "stage": "paired_step_2_current",
            "exact_F12_norm": fresh["exact_full_residual"],
        },
    ],
    "paired_exact_step_evidence": paired_steps,
    "current_coupled_ordered_event_geometry": {
        "branch_provenance": "VALIDATED_REPAIRED_N6_EVENT_RECORD_INDEX_12",
        "N12_selected_branch_index": eigenline[
            "transported_N12_eigenline_index"
        ],
        "ordered_neighbor_gap_lower_bound": eigenline["bounds"][
            "eigenline_gap_lower"
        ],
        "ordered_scale": lm2["ordered_scale"],
        "exact_F12_norm": fresh["exact_full_residual"],
        "signed_scaled_ordered_event_row": event_row,
        "other_56_rows_norm": other_rows_norm,
        "event_block_norm": residual["event_block_norm"],
        "child_block_norm": residual["child_block_norm"],
        "normal_rank": fresh["normal_rank"],
        "smallest_normal_singular_value": fresh[
            "smallest_normal_singular_value"
        ],
        "coupled_event_derivative_at_paired_center": coupled_derivative,
        "linear_coupled_event_step_action_norm": float(
            np.linalg.norm(linear_event_newton)
        ),
        "normal_Newton_correction_norm": fresh[
            "normal_Newton_correction_norm"
        ],
        "Newton_Kantorovich_product": fresh["Newton_Kantorovich_product"],
        "event_eta": fresh["event_eta"],
        "child_eta": fresh["child_eta"],
    },
    "targeted_exact_profile": profile_payload,
    "slowdown_classification": {
        "genuine_slowdown_demonstrated": False,
        "positive_event_floor_demonstrated": False,
        "normal_rank_loss_demonstrated": False,
        "evidence": (
            "The two refreshed paired steps reduced the exact merit by large "
            "factors while preserving eta, and the current Kantorovich "
            "diagnostic is small.  This is basin entry/certification evidence, "
            "not a stalled positive-asymptote history."
        ),
        "structured_shaking_authorized_by_this_audit": False,
    },
    "next_action": (
        "FINISH_THE_EXISTING_CORRECTED_N12_RADII_AND_PERSISTENCE_CERTIFICATE;_"
        "USE_TARGETED_EVENT_RECONNAISSANCE_ONLY_TO_AUDIT_BRANCH_AND_COUPLING"
    ),
    "unchanged_exact_F12": True,
    "checkpoint_modified": False,
    "proposal_executed": False,
    "new_physics_equation_constraint_gate_or_scale": False,
    "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": False,
    "FULL_BHSM_COMPLETE": False,
    "sources": {
        path.name: sha256(path)
        for path in (CHECKPOINT, CONSTRAINT, CACHED, LM1, LM2, FRESH, RESIDUAL, EIGENLINE)
    },
}

OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
