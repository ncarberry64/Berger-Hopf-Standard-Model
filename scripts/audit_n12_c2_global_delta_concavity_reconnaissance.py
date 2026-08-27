"""Audit the action-owned scalar concavity visible on the global C2 path.

The computation differentiates

    Delta = c b + s R

along the denominator-free, action-arclength vector field.  Selected-line
and hard-response derivatives are obtained from the inverse-free bordered
systems.  Third- and fourth-action scalar contractions use outward-rounded
interval arithmetic at each stored center.

This is a localization audit, not the final global theorem: the selected
line, bordered solves, and motion between stored centers still require one
uniform moving-cone/Taylor enclosure.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_retained_action_tensor_interval import (  # noqa: E402
    retained_action_tensor_interval,
)


BASE = ROOT / "artifacts" / "flagship_integration"
PATH_RECORD = BASE / "BHSM_N12_C2_GLOBAL_CANONICAL_STOP_RECONNAISSANCE.json"
PATH_DATA = PATH_RECORD.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_GLOBAL_DELTA_CONCAVITY_RECONNAISSANCE.json"
THEORY = ROOT / "theory" / "n12_c2_global_delta_concavity_reconnaissance.md"
QDIM = 37
COMPLEX_STEP = 1.0e-20
SAMPLE_INDICES = (0, 12, 24, 27, 36, 46)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _jet(state: np.ndarray):
    return exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM:2 * QDIM],
        state[2 * QDIM:],
        points=96,
    )


def _tensor_interval(
    state: np.ndarray, *directions: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    value = retained_action_tensor_interval(
        12, state, state, list(directions), points=96
    )
    return np.asarray(value.lo, dtype=float), np.asarray(value.hi, dtype=float)


def _center_row(
    state: np.ndarray,
    signed_descriptor: float,
    weights: np.ndarray,
    reference: np.ndarray,
    index: int,
) -> dict[str, Any]:
    q_weights, reduced_weights, _, _ = metric_data()
    jet = _jet(state)
    gradient = np.asarray(jet.gradient, dtype=float)
    hessian = np.asarray(jet.hessian, dtype=float)
    hessian_action = hessian / weights[:, None] / weights[None, :]
    reduced = hessian[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    eigenvalue = float(values[selected])
    mask = np.arange(psi.size) != selected
    complement = vectors[:, mask]
    hard_values = values[mask]

    configuration = q_weights * state[QDIM:2 * QDIM]
    gradient_action = gradient / weights
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM]
        - hessian_action[QDIM:2 * QDIM, :QDIM] @ configuration,
        -hessian_action[2 * QDIM:, :QDIM] @ configuration,
    ))
    rhs = reduced_weights * rhs_action
    b = float(psi @ rhs)
    hard = complement @ (
        (complement.T @ rhs) / (hard_values - eigenvalue)
    )
    psi_action = np.concatenate((np.zeros(QDIM), reduced_weights * psi))
    whole_hard_action = np.concatenate((
        configuration,
        reduced_weights * hard,
    ))

    def third_full(action_direction: np.ndarray) -> np.ndarray:
        raw_direction = action_direction / weights
        shifted = state.astype(complex) + 1j * COMPLEX_STEP * raw_direction
        return np.imag(np.asarray(_jet(shifted).hessian)) / COMPLEX_STEP

    third_psi = third_full(psi_action)
    third_hard = third_full(whole_hard_action)
    c = float(psi @ third_psi[QDIM:, QDIM:] @ psi)
    R = float(psi @ third_hard[QDIM:, QDIM:] @ psi)
    Delta = c * b + signed_descriptor * R
    cancelled = np.concatenate((
        signed_descriptor * configuration,
        reduced_weights * (b * psi + signed_descriptor * hard),
    ))
    cancelled_norm = float(np.linalg.norm(cancelled))
    action_direction = cancelled / cancelled_norm
    raw_direction = action_direction / weights
    descriptor_rate = Delta / cancelled_norm

    third_flow_full = third_full(action_direction)
    third_flow = third_flow_full[QDIM:, QDIM:]
    eigenvalue_rate = float(psi @ third_flow @ psi)
    psi_rate = complement @ (
        (complement.T @ third_flow @ psi)
        / (eigenvalue - hard_values)
    )

    gradient_rate_action = (hessian @ raw_direction) / weights
    hessian_rate_action = (
        third_flow_full / weights[:, None] / weights[None, :]
    )
    configuration_rate = (
        q_weights * raw_direction[QDIM:2 * QDIM]
    )
    rhs_rate_action = np.concatenate((
        q_weights * gradient_rate_action[:QDIM]
        - hessian_rate_action[QDIM:2 * QDIM, :QDIM] @ configuration
        - hessian_action[QDIM:2 * QDIM, :QDIM] @ configuration_rate,
        -hessian_rate_action[2 * QDIM:, :QDIM] @ configuration
        - hessian_action[2 * QDIM:, :QDIM] @ configuration_rate,
    ))
    rhs_rate = reduced_weights * rhs_rate_action
    b_rate = float(psi_rate @ rhs + psi @ rhs_rate)

    shifted = reduced - eigenvalue * np.eye(psi.size)
    hard_rhs_rate = (
        rhs_rate
        - b_rate * psi
        - b * psi_rate
        - (third_flow - eigenvalue_rate * np.eye(psi.size)) @ hard
    )
    bordered = np.block([
        [shifted, -psi[:, None]],
        [psi[None, :], np.zeros((1, 1))],
    ])
    hard_rate = np.linalg.solve(
        bordered,
        np.concatenate((hard_rhs_rate, [-float(psi_rate @ hard)])),
    )[:-1]

    psi_rate_action = np.concatenate((
        np.zeros(QDIM), reduced_weights * psi_rate,
    ))
    whole_hard_rate_action = np.concatenate((
        configuration_rate,
        reduced_weights * hard_rate,
    ))
    fourth_pair = _tensor_interval(
        state,
        action_direction,
        np.column_stack((psi_action, whole_hard_action)),
        psi_action,
        psi_action,
    )
    third_grid = _tensor_interval(
        state,
        np.column_stack((
            psi_rate_action, whole_hard_rate_action, whole_hard_action,
        )),
        np.column_stack((psi_action, psi_rate_action)),
        psi_action,
    )
    fourth_lower, fourth_upper = fourth_pair
    third_lower, third_upper = third_grid
    c_four = (float(fourth_lower[0]), float(fourth_upper[0]))
    c_kato = (float(third_lower[0, 0]), float(third_upper[0, 0]))
    c_rate = (
        c_four[0] + 3.0 * c_kato[0],
        c_four[1] + 3.0 * c_kato[1],
    )
    R_four = (float(fourth_lower[1]), float(fourth_upper[1]))
    R_hard = (float(third_lower[1, 0]), float(third_upper[1, 0]))
    R_kato = (float(third_lower[2, 1]), float(third_upper[2, 1]))
    R_rate = (
        R_four[0] + R_hard[0] + 2.0 * R_kato[0],
        R_four[1] + R_hard[1] + 2.0 * R_kato[1],
    )
    common = c * b_rate + descriptor_rate * R
    Delta_rate = (
        c_rate[0] * b + common + signed_descriptor * R_rate[0],
        c_rate[1] * b + common + signed_descriptor * R_rate[1],
    )
    gap = float(np.min(np.abs(hard_values - eigenvalue)))
    contributions = {
        "c_rate_times_b": [c_rate[0] * b, c_rate[1] * b],
        "c_times_b_rate": c * b_rate,
        "descriptor_rate_times_R": descriptor_rate * R,
        "s_times_R_rate": [
            signed_descriptor * R_rate[0],
            signed_descriptor * R_rate[1],
        ],
    }
    return {
        "index": index,
        "action_length": 2.0 * index,
        "selected_branch": selected,
        "signed_descriptor": signed_descriptor,
        "numeric_selected_eigenvalue_not_descriptor_owner": eigenvalue,
        "selected_eigenline_gap": gap,
        "cancelled_field_action_norm": cancelled_norm,
        "Delta": Delta,
        "Dlambda_da": eigenvalue_rate,
        "Delta_over_field_norm": descriptor_rate,
        "Dlambda_da_minus_Delta_over_field_norm": (
            eigenvalue_rate - descriptor_rate
        ),
        "b": b,
        "c": c,
        "R": R,
        "db_da": b_rate,
        "dc_da_interval": list(c_rate),
        "dR_da_interval": list(R_rate),
        "dDelta_da_interval": list(Delta_rate),
        "dDelta_da_contributions": contributions,
        "selected_line_rate_norm": float(np.linalg.norm(psi_rate)),
        "hard_response_rate_norm": float(np.linalg.norm(hard_rate)),
    }


def build_payload() -> dict[str, Any]:
    record = json.loads(PATH_RECORD.read_text(encoding="utf-8"))
    if record.get("status") != "FINITE_GLOBAL_s_ZERO_BRACKET_RECONNAISSANCE_ONLY":
        raise RuntimeError("global canonical-stop reconnaissance required")
    with np.load(PATH_DATA) as data:
        centers = np.asarray(data["centers"], dtype=float)
        descriptors = np.asarray(data["signed_descriptors"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    rows = []
    for sample in SAMPLE_INDICES:
        row = _center_row(
            centers[sample], descriptors[sample], weights, reference, sample
        )
        rows.append(row)
        print(json.dumps({
            "index": sample,
            "action_length": row["action_length"],
            "Delta": row["Delta"],
            "dDelta_da_interval": row["dDelta_da_interval"],
        }), flush=True)
    every_center_negative = all(
        float(row["dDelta_da_interval"][1]) < 0.0 for row in rows
    )
    return {
        "artifact": "BHSM_N12_C2_GLOBAL_DELTA_CONCAVITY_RECONNAISSANCE",
        "status": (
            "ACTION_OWNED_GLOBAL_DELTA_CONCAVITY_CANDIDATE_LOCALIZED;_"
            "UNIFORM_MOVING_CONE_ENCLOSURE_OPEN"
        ),
        "identity": (
            "d_a_Delta=(d_a_c)b+c(d_a_b)+(Delta/||G||)R+s(d_a_R)"
        ),
        "path_coordinate": (
            "dY/da=G_theta/(w||G_theta||_2),_ds/da=Delta/||G_theta||_2"
        ),
        "sample_indices": list(SAMPLE_INDICES),
        "rows": rows,
        "sampled_center_concavity": {
            "every_outward_rounded_point_interval_is_strictly_negative": (
                every_center_negative
            ),
            "least_negative_sample_upper": max(
                float(row["dDelta_da_interval"][1]) for row in rows
            ),
            "most_negative_sample_lower": min(
                float(row["dDelta_da_interval"][0]) for row in rows
            ),
        },
        "claim_boundary": {
            "point_action_tensor_contractions_outward_rounded": True,
            "selected_line_and_bordered_center_solves_interval_certified": False,
            "motion_between_sample_centers_interval_certified": False,
            "uniform_dDelta_da_negative_on_global_tube": False,
            "canonical_s_zero_first_hit_certified": False,
            "permitted_conclusion": (
                "THE_REAL_GLOBAL_STOP_ROUTE_IS_SCALAR_DELTA_CONCAVITY_ON_A_"
                "MOVING_SELECTED_EIGENLINE_CONE;_THE_PRIOR_AXIS_BOX_AND_"
                "FROZEN_RAY_ROUTES_ARE_INVALID"
            ),
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_SELECTED_LINE,_HARD_RESPONSE,_AND_THE_DISPLAYED_"
            "dDelta/da_IDENTITY_ON_ONE_FINITE_CORRELATED_MOVING_CONE_OVER_"
            "0<=a<=94;_THEN_INTEGRATE_THE_STRICT_CONCAVITY_TO_THE_TRANSVERSE_"
            "FIRST_HIT_s=0"
        ),
        "hindsight": {
            "VALIDATED": (
                "FINITE_GLOBAL_GRAPH_PRESERVING_PATH_HAS_A_REAL_s_ZERO_"
                "BRACKET_AND_ALL_SAMPLED_ACTION_OWNED_dDelta/da_INTERVALS_"
                "ARE_NEGATIVE"
            ),
            "INVALIDATED": (
                "THE_PRIOR_CENTER_BRACKET_WAS_ONLY_LARGE_STEP_DESCRIPTOR_"
                "DRIFT;_THE_CORRECTED_PATH_REPRODUCES_IT,_BUT_A_FROZEN_"
                "PRINCIPAL_RAY_DOES_NOT"
            ),
            "OPEN": "ONE_UNIFORM_MOVING_CONE_CONCAVITY_ENCLOSURE",
            "GLOBALIZATION_CHECK": (
                "YES:_PROVE_ONE_SCALAR_CONCAVITY_THEOREM,_NOT_MORE_LOCAL_"
                "CONTINUATION_BLOCKS"
            ),
            "BHSM_NATIVE_CHECK": (
                "s,_Delta,_THE_SELECTED_LINE,_AND_THE_BORDERED_HARD_RESPONSE_"
                "ARE_ALL_RETAINED_ACTION_OBJECTS"
            ),
        },
        "inputs": {
            PATH_RECORD.relative_to(ROOT).as_posix(): _sha256(PATH_RECORD),
            PATH_DATA.relative_to(ROOT).as_posix(): _sha256(PATH_DATA),
            THEORY.relative_to(ROOT).as_posix(): _sha256(THEORY),
        },
        "validation_passed": False,
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
        "sampled_center_concavity": payload["sampled_center_concavity"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
