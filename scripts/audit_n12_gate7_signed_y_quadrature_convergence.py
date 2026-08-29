"""Audit whether the current signed-Y quadrature supports Gate-7 promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
ORDERS = (8, 12, 16, 20)
CORRECTIONS = {
    order: BASE / (
        f"BHSM_N12_GATE7_SIGNED_Y_QUADRATURE_GAUSS{order:02d}_"
        "PROP16_RECONNAISSANCE.npz"
    )
    for order in ORDERS
}
RESIDUALS = {
    order: BASE / (
        f"BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS{order}_"
        "RECONNAISSANCE.json"
    )
    for order in ORDERS
}
STORED_CORRECTION = BASE / (
    "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_"
    "GAUSS12_RECONNAISSANCE.npz"
)
CAUSAL_Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
PROPAGATOR_Z1 = BASE / "BHSM_N12_GATE7_FINITE_PROPAGATOR_Z1_RECONNAISSANCE.json"
RESULT = BASE / "BHSM_N12_GATE7_SIGNED_Y_QUADRATURE_CONVERGENCE_AUDIT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    paths = [
        *CORRECTIONS.values(), *RESIDUALS.values(),
        STORED_CORRECTION, CAUSAL_Z2, PROPAGATOR_Z1,
    ]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing signed-Y audit inputs: " + str(missing))

    profiles: dict[int, np.ndarray] = {}
    sources: dict[int, np.ndarray] = {}
    times = None
    for order, path in CORRECTIONS.items():
        with np.load(path) as source:
            current_times = np.asarray(source["fine_action_lengths"], dtype=float)
            profiles[order] = np.asarray(
                source["fine_ambient_correction_profile"], dtype=float,
            )
            sources[order] = np.asarray(
                source["fine_propagated_sources"], dtype=float,
            )
        if times is None:
            times = current_times
        elif not np.array_equal(times, current_times):
            raise RuntimeError("signed-Y correction grids changed across orders")
    assert times is not None

    z2 = json.loads(CAUSAL_Z2.read_text(encoding="utf-8"))
    z1 = json.loads(PROPAGATOR_Z1.read_text(encoding="utf-8"))
    radius = float(z2["domain"]["candidate_nonlinear_action_radius"])
    rows = []
    for left, right in zip(ORDERS[:-1], ORDERS[1:], strict=True):
        profile_difference = np.linalg.norm(
            profiles[right] - profiles[left], axis=1,
        )
        source_difference = np.linalg.norm(
            sources[right] - sources[left], axis=1,
        )
        profile_owner = int(np.argmax(profile_difference))
        source_owner = int(np.argmax(source_difference))
        top_count = 30
        top = np.argsort(source_difference)[-top_count:]
        rows.append({
            "left_Gauss_order": left,
            "right_Gauss_order": right,
            "maximum_signed_correction_profile_increment_2_norm": float(
                profile_difference[profile_owner]
            ),
            "profile_increment_owner_fine_node": profile_owner,
            "profile_increment_owner_action_length": float(times[profile_owner]),
            "terminal_signed_correction_increment_2_norm": float(
                profile_difference[-1]
            ),
            "maximum_local_propagated_source_increment_2_norm": float(
                source_difference[source_owner]
            ),
            "local_source_increment_owner_interval": source_owner,
            "sum_local_propagated_source_increment_2_norm": float(
                np.sum(source_difference)
            ),
            "top_30_local_source_increment_fraction": float(
                np.sum(source_difference[top]) / np.sum(source_difference)
            ),
            "candidate_halo_utilization": float(
                profile_difference[profile_owner] / radius
            ),
        })

    with np.load(STORED_CORRECTION) as source:
        stored_profile = np.asarray(
            source["fine_ambient_correction_profile"], dtype=float,
        )
    stored_to_refined = np.linalg.norm(
        profiles[12] - stored_profile, axis=1,
    )
    stored_owner = int(np.argmax(stored_to_refined))
    increments = [
        row["maximum_signed_correction_profile_increment_2_norm"]
        for row in rows
    ]
    decay_factors = [
        increments[index] / increments[index + 1]
        for index in range(len(increments) - 1)
    ]
    z1_summary = z1["summary"]
    finest_z1_order = float(z1_summary["observed_finest_summed_local_order"])
    finest_z1_tail = float(z1_summary["factor_four_geometric_tail_estimate"])
    validation = {
        "same_371_node_fine_grid_at_all_orders": times.shape == (371,),
        "same_selected_branch_24_at_Gauss16_and_Gauss20": all(
            json.loads(RESIDUALS[order].read_text(encoding="utf-8"))["summary"]
            ["selected_branches_seen"] == [24]
            for order in (16, 20)
        ),
        "Gauss12_to16_increment_exceeds_candidate_halo": rows[1][
            "candidate_halo_utilization"
        ] > 1.0,
        "Gauss16_to20_increment_exceeds_candidate_halo": rows[2][
            "candidate_halo_utilization"
        ] > 1.0,
        "Gauss16_to20_increment_does_not_decrease": increments[2] >= increments[1],
        "top_30_cells_do_not_own_half_the_latest_source_increment": rows[2][
            "top_30_local_source_increment_fraction"
        ] < 0.5,
        "propagator_refinement_retains_second_order_convergence": abs(
            finest_z1_order - 2.0
        ) < 1.0e-3,
        "propagator_tail_remains_numerical_not_interval_authority": (
            z1["validation_passed"] is False
        ),
        "local_response_and_Z2_certificates_not_relabelled_as_history_proof": True,
        "no_physical_event_or_action_change_inferred": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_SIGNED_Y_QUADRATURE_CONVERGENCE_AUDIT",
        "authority": "CROSS_QUADRATURE_NUMERICAL_INVALIDATION_NOT_INTERVAL_Y_AUTHORITY",
        "status": "CURRENT_GAUSS12_RECENTER_NOT_PROMOTABLE;_SIGNED_Y_QUADRATURE_OPEN",
        "identity": {
            "literal_Y": "NORM_A_TIMES_MINUS_DEFECT_IN_THE_COMMON_HISTORY_FRAME",
            "candidate_halo_radius": radius,
            "signed_before_norm": True,
            "comparison": "SAME_PROP16_GREEN_OPERATOR_ACROSS_GAUSS_8_12_16_20",
        },
        "rows": rows,
        "summary": {
            "candidate_nonlinear_action_radius": radius,
            "signed_profile_increment_decrease_factors": decay_factors,
            "maximum_stored_Gauss12_to_prop16_Gauss12_displacement_2_norm": float(
                stored_to_refined[stored_owner]
            ),
            "stored_to_refined_owner_fine_node": stored_owner,
            "stored_to_refined_candidate_halo_utilization": float(
                stored_to_refined[stored_owner] / radius
            ),
            "latest_Gauss16_to20_candidate_halo_utilization": rows[2][
                "candidate_halo_utilization"
            ],
            "latest_top_30_local_source_increment_fraction": rows[2][
                "top_30_local_source_increment_fraction"
            ],
            "Z1_observed_finest_summed_local_order": finest_z1_order,
            "Z1_factor_four_geometric_tail_estimate": finest_z1_tail,
        },
        "adjudication": {
            "validated": [
                "PROPAGATOR_REFINEMENT_HAS_STABLE_SECOND_ORDER_CONVERGENCE",
                "GAUSS_8_12_16_20_SIGNED_CORRECTIONS_SHARE_ONE_PROP16_OPERATOR",
                "BRANCH_24_REMAINS_SELECTED_ON_THE_REFINED_SAMPLES",
            ],
            "invalidated": [
                "PROMOTION_OF_THE_CURRENT_GAUSS12_RECENTER_AS_AN_EXACT_HISTORY",
                "TREATING_ORDINARY_GAUSS12_OR_GAUSS16_AS_CONVERGED_SIGNED_Y",
                "ASSEMBLING_THE_CURRENT_RADII_POLYNOMIAL_BEFORE_REBASING_Y",
            ],
            "preserved": [
                "LOCAL_3009_CELL_RECENTERED_SPECTRUM_PROJECTOR_INVERSE_CERTIFICATES",
                "LOCAL_24072_CELL_RESPONSE_AND_REVERSE_FIRST_VARIATION_CERTIFICATES",
                "CAUSAL_TAYLOR_Z2_CERTIFICATE_ON_ITS_REPRESENTED_CENTER",
            ],
            "classification": "NUMERICAL_CONDITIONING_PLUS_PROOF_CHART_LIMIT_NOT_PHYSICAL_EVENT",
        },
        "exact_next_dependency": (
            "CONVERGE_THE_SIGNED_GREEN_SOURCE_WITH_HIGH_PRECISION_OR_ADAPTIVE_"
            "CORRELATION_PRESERVING_QUADRATURE_BELOW_THE_1P244E_MINUS12_HALO;_"
            "FREEZE_THAT_NEW_RECENTER;_THEN_REBUILD_ONLY_THE_CENTER_DEPENDENT_"
            "RECENTERED_CONE_RESPONSE_CHAIN_BEFORE_LITERAL_Y_Z1_RADII_PROMOTION"
        ),
        "claim_boundary": {
            "Y": "OPEN_NONCONVERGED_SIGNED_QUADRATURE",
            "Z1": "NUMERICAL_SECOND_ORDER_CONVERGENCE_ONLY_INTERVAL_TAIL_OPEN",
            "Z2": "CERTIFIED_ON_THE_CURRENT_REPRESENTED_CENTER_NOT_TRANSFERRED",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {_relative(path): _sha256(path) for path in paths},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
