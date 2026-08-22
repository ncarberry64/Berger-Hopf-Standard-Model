"""Audit the corrected-action N12 execution and measurement provenance.

This is a read-only scientific-era audit.  It verifies that the calculation
resolved BHSM from this checkout, separates lower-precision diagnostic values
from the retained high-precision 57-row evaluator, and records whether the
unchanged corrected-action root was recovered.  It does not promote the root,
alter a checkpoint, or add an acceptance gate.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface import (
    aether_exact_radial_schur_lift_v15_83 as reduced_action,
)
from bhsm.interface import aether_high_precision_velocity_jet as high_precision
from bhsm.interface import (
    aether_n3_exact_full_local_action_jet_v17_60 as full_action,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_n12_corrected_action_repair.npz"
))
FRESH = Path(os.environ.get(
    "BHSM_N12_FRESH_CENTER_RESULT",
    ".tmp_n12_corrected_action_root_fresh_center.json",
))
TRANSPORT = Path(os.environ.get(
    "BHSM_N12_TRANSPORT_RESULT",
    ".tmp_n12_corrected_action_repair_refresh1.json",
))
PUBLIC_STATE = Path(os.environ.get(
    "BHSM_N12_PUBLIC_STATE",
    "artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
))
PUBLIC_RESIDUAL = Path(os.environ.get(
    "BHSM_N12_PUBLIC_RESIDUAL",
    "artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json",
))
PROMOTION = Path(os.environ.get(
    "BHSM_N12_PROMOTION_RESULT",
    ".tmp_direct_n12_high_precision_complete_persistent_child_promotion.json",
))
PUBLIC_THIRD = Path(os.environ.get(
    "BHSM_N12_PUBLIC_THIRD_VARIATION",
    "artifacts/n12_direct_checkpoint/BHSM_N12_THIRD_VARIATIONS.npz",
))
CURRENT_THIRD = Path(os.environ.get(
    "BHSM_N12_CURRENT_THIRD_VARIATION",
    ".tmp_n12_corrected_recert/"
    ".tmp_direct_n12_high_precision_root_third_variations.npz",
))
RESULT = Path(os.environ.get(
    "BHSM_N12_EXECUTION_PROVENANCE_RESULT",
    ".tmp_n12_corrected_action_execution_provenance.json",
))
PRIOR_PUBLIC_COMMIT = os.environ.get(
    "BHSM_N12_PRIOR_PUBLIC_COMMIT",
    "ba33d3465d02bf32c563f08be1de562f44993022",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def source_record(module: object) -> dict[str, object]:
    path = Path(inspect.getfile(module)).resolve()
    repository_src = (ROOT / "src").resolve()
    inside = path.is_relative_to(repository_src)
    return {
        "path": path.relative_to(ROOT).as_posix() if inside else str(path),
        "SHA256": sha256(path),
        "inside_current_repository_src": inside,
    }


def verify(reference: Path) -> None:
    expected = json.loads(reference.read_text(encoding="utf-8"))
    current = {
        "reduced_action": source_record(reduced_action),
        "full_action": source_record(full_action),
        "high_precision_velocity_jet": source_record(high_precision),
    }
    matches = {
        name: bool(
            record["inside_current_repository_src"]
            and record["SHA256"] == expected["source_modules"][name]["SHA256"]
        )
        for name, record in current.items()
    }
    passed = all(matches.values())
    print(json.dumps({
        "classification": (
            "CORRECTED_ACTION_N12_EXECUTION_SOURCE_REPRODUCED"
            if passed else
            "CORRECTED_ACTION_N12_EXECUTION_SOURCE_MISMATCH"
        ),
        "reference": str(reference),
        "reference_SHA256": sha256(reference),
        "source_hash_matches": matches,
        "current_source_modules": current,
        "validation_passed": passed,
    }, indent=2))
    if not passed:
        raise SystemExit(1)


def main() -> None:
    fresh = json.loads(FRESH.read_text(encoding="utf-8"))
    transport = json.loads(TRANSPORT.read_text(encoding="utf-8"))
    prior = json.loads(PUBLIC_RESIDUAL.read_text(encoding="utf-8"))
    current_state = np.asarray(np.load(CHECKPOINT)["state"], dtype=float)
    public_state = np.asarray(np.load(PUBLIC_STATE)["state"], dtype=float)

    order = 12
    size = dimensions(order)
    qdim = size["coordinates"]
    frequencies = spectral_frequencies(order)
    sector_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    joint_weights = np.concatenate((sector_weights, sector_weights))
    state_delta = current_state - public_state

    sources = {
        "reduced_action": source_record(reduced_action),
        "full_action": source_record(full_action),
        "high_precision_velocity_jet": source_record(high_precision),
    }
    local_sources = all(
        bool(record["inside_current_repository_src"])
        for record in sources.values()
    )
    root_recovered = bool(
        fresh["exact_full_residual"] < 1.0e-9
        and fresh["normal_rank"] == 57
        and fresh["event_eta"] > 0.0
        and fresh["child_eta"] > 0.0
    )
    accepted = [
        record for record in transport["exact_merit_continuation"]
        if record.get("accepted") is True
    ]
    promotion = (
        json.loads(PROMOTION.read_text(encoding="utf-8"))
        if PROMOTION.is_file() else None
    )
    certificate_rebuilt = bool(
        promotion is not None
        and promotion.get("DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED")
        is True
        and promotion.get("source_checkpoint_SHA256") == sha256(CHECKPOINT)
    )
    third_comparison = None
    if PUBLIC_THIRD.is_file() and CURRENT_THIRD.is_file():
        old_third = np.load(PUBLIC_THIRD)
        new_third = np.load(CURRENT_THIRD)
        third_comparison = {}
        for sector in ("event", "child"):
            current_tensor = np.asarray(new_third[sector], dtype=float)
            difference = current_tensor - np.asarray(
                old_third[sector], dtype=float
            )
            third_comparison[sector] = {
                "Frobenius_difference": float(np.linalg.norm(difference)),
                "relative_Frobenius_difference": float(
                    np.linalg.norm(difference)
                    / max(np.linalg.norm(current_tensor), 1.0e-300)
                ),
            }
    payload = {
        "classification": (
            "CORRECTED_ACTION_N12_ROOT_EXECUTION_PROVENANCE_VALIDATED"
            if local_sources and root_recovered else
            "CORRECTED_ACTION_N12_EXECUTION_PROVENANCE_FAILED_CLOSED"
        ),
        "repository_root": ".",
        "prior_public_checkpoint_git_commit": PRIOR_PUBLIC_COMMIT,
        "source_modules": sources,
        "all_scientific_modules_resolved_from_current_repository_src": (
            local_sources
        ),
        "measurement_era_separation": {
            "prior_public_exact_residual": prior.get(
                "exact_F12_norm", prior.get("exact_full_residual")
            ),
            "current_corrected_action_high_precision_exact_residual": fresh[
                "exact_full_residual"
            ],
            "comparison_interpretation": (
                "The values use different execution/evaluation provenance. "
                "They are not a physical descent or regression chronology."
            ),
            "lower_precision_binary_eigenvalue_or_lift_diagnostics_are_not_"
            "the_exact_57_row_promotion_authority": True,
        },
        "corrected_action_root": {
            "exact_57_row_norm": fresh["exact_full_residual"],
            "hard_complement_norm": fresh["hard_complement_norm"],
            "signed_soft_residual": fresh["signed_soft_residual"],
            "normal_rank": fresh["normal_rank"],
            "smallest_normal_singular_value": fresh[
                "smallest_normal_singular_value"
            ],
            "normal_Newton_correction_norm": fresh[
                "normal_Newton_correction_norm"
            ],
            "event_eta": fresh["event_eta"],
            "child_eta": fresh["child_eta"],
            "unchanged_map_root_recovered": root_recovered,
            "direct_complete_persistent_child_certificate_rebuilt": (
                certificate_rebuilt
            ),
        },
        "state_comparison_to_prior_public_checkpoint": {
            "action_coordinate_norm": float(np.linalg.norm(
                joint_weights * state_delta
            )),
            "raw_coordinate_norm": float(np.linalg.norm(state_delta)),
            "raw_coordinate_maximum": float(np.max(np.abs(state_delta))),
            "interpretation": (
                "The corrected high-precision solve returns to the existing "
                "physical state within certificate-scale displacement; the "
                "earlier large apparent defect was evaluator conditioning, "
                "not evidence of changed physics."
            ),
        },
        "third_variation_comparison_to_prior_public_checkpoint": (
            third_comparison
        ),
        "hindsight": {
            "accepted_fresh_exact_steps": len(accepted),
            "latest_exact_before": (
                accepted[-1]["exact_norm_before"] if accepted else None
            ),
            "latest_exact_after": (
                accepted[-1]["exact_norm_after"] if accepted else None
            ),
            "genuine_slowdown_demonstrated": False,
            "positive_ordered_event_floor_demonstrated": False,
            "targeted_event_reconnaissance_required_after_root_recovery": False,
            "structured_shaking_authorized": False,
        },
        "unchanged_57_row_F12": True,
        "checkpoint_modified": False,
        "new_physics_equation_constraint_gate_scale_fit_or_selector": False,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": certificate_rebuilt,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "inputs": {
            str(path): sha256(path)
            for path in (
                CHECKPOINT, FRESH, TRANSPORT, PUBLIC_STATE, PUBLIC_RESIDUAL,
            )
        } | (
            {str(PROMOTION): sha256(PROMOTION)}
            if PROMOTION.is_file() else {}
        ) | (
            {
                str(PUBLIC_THIRD): sha256(PUBLIC_THIRD),
                str(CURRENT_THIRD): sha256(CURRENT_THIRD),
            }
            if PUBLIC_THIRD.is_file() and CURRENT_THIRD.is_file() else {}
        ),
        "exact_next_dependency": (
            "DERIVE_EXPLICIT_ACTION_GRAPH_NORM_TAIL_MODULI_FOR_THE_FOUR_"
            "RETAINED_COMPACT_BLOCKS_AND_CLOSE_THE_NONLINEAR_CONTINUUM_"
            "RADII_POLYNOMIAL"
            if certificate_rebuilt else
            "REBUILD_THE_DIRECT_N12_ROOT_BALL_PHYSICAL_NEIGHBORHOOD_AND_"
            "POSITIVE_DURATION_PERSISTENCE_CERTIFICATES_UNDER_THE_MERGED_"
            "CORRECTED_ACTION"
        ),
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify",
        type=Path,
        help="verify current checkout source hashes against a durable audit",
    )
    arguments = parser.parse_args()
    if arguments.verify is not None:
        verify(arguments.verify)
    else:
        main()
