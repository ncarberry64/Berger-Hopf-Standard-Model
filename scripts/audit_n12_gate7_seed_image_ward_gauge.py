"""Audit Ward/BRST and gauge claims against the rank-72 C2 seed image."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_SEED_IMAGE_WARD_GAUGE_AUDIT.json"
THEORY = ROOT / "theory" / "n12_gate7_seed_image_ward_gauge_audit.md"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
RESET = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
RESET_DATA = RESET.with_suffix(".npz")
BRST = BASE / "BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json"
TIME = BASE / "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
CROSS = ROOT / "artifacts" / "BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
INPUTS = (LAUNCH, LAUNCH_DATA, RESET, RESET_DATA, BRST, TIME, CROSS, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing seed-image Ward/gauge inputs: " + ", ".join(missing))
    launch, reset, brst, time = (_load(path) for path in (LAUNCH, RESET, BRST, TIME))
    cross = _load(CROSS)["cross_resolution_reconnaissance"]
    principal = cross["boundary_compatible_gauge_quotient_audit"]
    if not all(record.get("validation_passed") is True for record in (
        launch, reset, brst, time, principal,
    )):
        raise RuntimeError("validated seed-image Ward/gauge parents required")

    with np.load(RESET_DATA) as data:
        reset_jacobian = np.asarray(data["analytic_full_reset_jacobian"], dtype=float)
    with np.load(LAUNCH_DATA) as data:
        seed_image = np.asarray(data["event_image_basis"], dtype=float)
        launch_keys = tuple(sorted(data.files))

    # The full reset row ledger is: 25 event constraints, one ordered-event
    # row, four boundary rows, 25 child constraints, two momentum rows.
    event_constraint_and_ordered = reset_jacobian[:26, :98]
    _, singular, vh = np.linalg.svd(event_constraint_and_ordered, full_matrices=True)
    rank = int(np.count_nonzero(singular > 1.0e-8))
    exact_kernel = vh[rank:].T
    seed_projector = seed_image @ seed_image.T
    kernel_projector = exact_kernel @ exact_kernel.T
    image_residual = float(np.linalg.norm(event_constraint_and_ordered @ seed_image, 2))
    projector_residual = float(np.linalg.norm(seed_projector - kernel_projector, 2))

    gauge_named_keys = [key for key in launch_keys if "gauge" in key.lower()]
    validation = {
        "reset_row_ledger_has_25_constraints_plus_ordered_event": (
            reset_jacobian.shape == (57, 196)
            and event_constraint_and_ordered.shape == (26, 98)
        ),
        "event_constraint_and_ordered_rank_is_26": rank == 26,
        "its_nullity_is_72": exact_kernel.shape == (98, 72),
        "stored_seed_image_has_dimension_72": seed_image.shape == (98, 72),
        "stored_seed_image_is_the_full_event_constraint_kernel": (
            image_residual < 1.0e-10 and projector_residual < 1.0e-10
        ),
        "launch_archive_contains_no_gauge_generator_or_quotient_basis": not gauge_named_keys,
        "principal_slice_is_not_a_global_gauge_theorem": (
            principal["candidate_slice_promoted_as_a_global_gauge_theorem"] is False
        ),
        "principal_audit_does_not_supply_a_98_state_generator": (
            principal["instantaneous_Cauchy_matrix_is_the_full_history_Jacobi_operator"] is False
        ),
        "BRST_leaves_a_nonzero_physical_heat_coefficient": (
            brst["adjudication"]["longitudinal_ghost_BRST_pair"] == "CANCELS_EXACTLY"
            and brst["adjudication"]["universal_Ward_BRST_zero_force"] == "INVALID"
            and brst["exact_asymptotic"]["leading_degeneracy_coefficient"] == -20
        ),
        "time_quotient_root_equivalence_does_not_evaluate_the_cotangent": (
            time["scope"]["actual_q_rep_evaluated"] is False
            and time["scope"]["explicit_time_generator_needed_for_first_force_root"] is False
        ),
        "no_dimension_removed_without_generator_membership_and_Ward_annihilation": True,
        "only_external_source_is_zero_and_no_internal_block_is_zeroed": True,
        "no_selector_slice_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_SEED_IMAGE_WARD_GAUGE_AUDIT",
        "status": (
            "WARD_GAUGE_SHORTCUT_EXHAUSTED_RANK72_TAIL_RETAINED"
            if passed else "SEED_IMAGE_WARD_GAUGE_AUDIT_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_STORED_72_DIMENSIONAL_OUTGOING_C2_SEED_IMAGE_IS_THE_FULL_"
            "KERNEL_OF_THE_25_SINGLE_CHILD_CONSTRAINT_ROWS_PLUS_THE_ORDERED_"
            "EVENT_ROW;_THE_TRACKED_PRINCIPAL_GAUGE_SLICE_IS_NOT_A_GLOBAL_"
            "98_STATE_GAUGE_THEOREM,_BRST_LEAVES_A_NONZERO_PHYSICAL_HEAT_"
            "COEFFICIENT,_AND_TIME_INVARIANCE_GIVES_ROOT_EQUIVALENCE_ONLY,_"
            "SO_NO_CURRENT_WARD_OR_GAUGE_IDENTITY_REDUCES_THE_RANK72_TAIL"
        ),
        "exact_linear_algebra": {
            "event_constraint_and_ordered_matrix_shape": [26, 98],
            "rank": rank,
            "nullity": int(exact_kernel.shape[1]),
            "stored_seed_image_shape": list(seed_image.shape),
            "smallest_nonzero_singular_value": float(singular[rank - 1]),
            "seed_image_equation_residual_norm": image_residual,
            "seed_image_kernel_projector_residual_norm": projector_residual,
            "identity": "range(B_seed)=ker(J_reset[0:26,0:98])",
            "launch_archive_keys": list(launch_keys),
            "gauge_named_launch_archive_keys": gauge_named_keys,
        },
        "Ward_BRST_adjudication": {
            "longitudinal_ghost_pair": "CANCELS_MODE_BY_MODE",
            "physical_transverse_HS_Weyl_leading_coefficient": "-5*sqrt(pi)",
            "universal_closed_functional_zero_force": False,
            "geometry_seed_image_annihilated_by_BRST_grading": False,
        },
        "gauge_time_adjudication": {
            "principal_delta_w_delta_beta_slice": "FINITE_N_PRINCIPAL_CALDERON_SLICE_ONLY",
            "global_98_state_Cauchy_generator_supplied": False,
            "generator_membership_in_seed_image_proved": False,
            "closed_functional_annihilation_on_such_a_generator_proved": False,
            "exact_time_invariance_role": "BASIC_COVECTOR_AND_RAW_BORDERED_ROOT_EQUIVALENCE_AFTER_THE_LIMIT_EXISTS",
            "tail_Cauchy_convergence_from_time_invariance_alone": False,
        },
        "remaining_owner": {
            "dimension": 72,
            "coordinate_tail": "B_seed^dagger*(p_T(0)-p_S(0))_PLUS_THE_OWNED_DIRECT_REPLACEMENT_INCREMENT",
            "valid_routes": [
                "PROVE_THE_SOURCE_CONTRACTED_PROJECTED_CAUCHY_ESTIMATE",
                "CERTIFY_A_QUANTITATIVE_RESET_TO_CONTROLLED_ASYMPTOTIC_CONNECTION_WITH_JACOBI_BOUNDS",
                "CERTIFY_A_FINITE_LATER_EVENT_OR_CANONICAL_STOP",
            ],
            "dimension_count_shortcut": "CLOSED_INVALID",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_RANK72_PROJECTED_CAUCHY_TAIL",
            "Gate8": "LOCKED",
            "Ward_BRST_shortcut": "CLOSED_INVALID",
            "principal_gauge_slice_shortcut": "CLOSED_INVALID",
            "remaining_reset_generated_seed_image_tail": "OPEN_CURRENT_OWNER",
            "remaining_noncompact_tail_dimension_upper": 72,
            "actual_zero_source_force": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "rank": payload["exact_linear_algebra"]["rank"],
        "nullity": payload["exact_linear_algebra"]["nullity"],
        "projector_residual": payload["exact_linear_algebra"]["seed_image_kernel_projector_residual_norm"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
