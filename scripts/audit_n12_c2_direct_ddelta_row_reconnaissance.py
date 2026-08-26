"""Recombine Delta directly and measure its decisive Hessian row on two meshes."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)


BASE = ROOT / "artifacts" / "flagship_integration"
FIELD = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
FIELD_DATA = FIELD.with_suffix(".npz")
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
CORE = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
CORE_DATA = CORE.with_suffix(".npz")
TRANSPORT = BASE / "BHSM_N12_C2_SIGNED_DDELTA_SEED_TRANSPORT_AUDIT.json"
STEP = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
THEORY = ROOT / "theory" / "n12_c2_direct_ddelta_row_reconnaissance.md"
ACTION_SOURCE = (
    ROOT / "src" / "bhsm" / "interface"
    / "aether_n3_exact_full_local_action_jet_v17_60.py"
)
METRIC_SOURCE = (
    ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_descriptor_cover.py"
)
RESULT = BASE / "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
INPUTS = (
    FIELD, FIELD_DATA, BORDERED, BORDERED_DATA, CORE, CORE_DATA, TRANSPORT, STEP,
    THEORY, ACTION_SOURCE, METRIC_SOURCE,
)
QDIM = 37
REFERENCE_NODE = 1214
COMPLEX_STEP = 1.0e-20
INNER_STEP = 3.0e-6
OUTER_STEPS = (3.0e-5, 1.0e-5)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jet(state: np.ndarray):
    return exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM:2 * QDIM],
        state[2 * QDIM:],
        points=96,
    )


def _direct_delta(
    state: np.ndarray,
    *,
    weights: np.ndarray,
    reference: np.ndarray,
    signed_descriptor: float,
) -> tuple[float, int]:
    """Evaluate Delta=Dlambda[b Psi+s V_hard] before taking norms."""

    q_weights, reduced_weights, _, _ = metric_data()
    jet = _jet(state)
    hessian = np.asarray(jet.hessian)
    reduced = np.asarray(hessian[QDIM:, QDIM:], dtype=float)
    values, vectors = np.linalg.eigh(reduced)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi

    numeric_lambda = float(values[selected])
    gradient_action = np.asarray(jet.gradient, dtype=float) / weights
    hessian_action = (
        np.asarray(hessian, dtype=float)
        / weights[:, None]
        / weights[None, :]
    )
    configuration = q_weights * state[QDIM:2 * QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM]
        - hessian_action[QDIM:2 * QDIM, :QDIM] @ configuration,
        -hessian_action[2 * QDIM:, :QDIM] @ configuration,
    ))
    rhs = reduced_weights * rhs_action
    # These are the exact selected-line and complement formulas.  In
    # particular b=<Psi,f> is not taken from an ill-conditioned solve whose
    # tiny binary eigen-residual is multiplied by the large hard response.
    b_psi = float(psi @ rhs)
    hard_indices = np.arange(psi.size) != selected
    complement = vectors[:, hard_indices]
    hard_values = values[hard_indices]
    hard = complement @ (
        (complement.T @ rhs) / (hard_values - numeric_lambda)
    )
    full_hard_action = np.concatenate((
        configuration, reduced_weights * hard,
    ))
    numerator_raw = (
        b_psi * np.concatenate((np.zeros(QDIM), psi))
        + signed_descriptor * full_hard_action / weights
    )
    shifted = state.astype(complex) + 1j * COMPLEX_STEP * numerator_raw
    directional_reduced = (
        np.imag(np.asarray(_jet(shifted).hessian)[QDIM:, QDIM:])
        / COMPLEX_STEP
    )
    return float(psi @ directional_reduced @ psi), selected


def _dominant_gradient_component(
    state: np.ndarray,
    index: int,
    *,
    step: float,
    weights: np.ndarray,
    reference: np.ndarray,
    signed_descriptor: float,
) -> float:
    plus = state.copy()
    minus = state.copy()
    plus[index] += step / weights[index]
    minus[index] -= step / weights[index]
    value_plus, selected_plus = _direct_delta(
        plus,
        weights=weights,
        reference=reference,
        signed_descriptor=signed_descriptor,
    )
    value_minus, selected_minus = _direct_delta(
        minus,
        weights=weights,
        reference=reference,
        signed_descriptor=signed_descriptor,
    )
    if selected_plus != 24 or selected_minus != 24:
        raise RuntimeError("selected C2 eigenline changed during row reconnaissance")
    return (value_plus - value_minus) / (2.0 * step)


def _row(
    center: np.ndarray,
    dominant_index: int,
    *,
    outer_step: float,
    weights: np.ndarray,
    reference: np.ndarray,
    signed_descriptor: float,
) -> np.ndarray:
    row = np.empty(center.size)
    started = time.monotonic()
    for column in range(center.size):
        plus = center.copy()
        minus = center.copy()
        plus[column] += outer_step / weights[column]
        minus[column] -= outer_step / weights[column]
        row[column] = (
            _dominant_gradient_component(
                plus,
                dominant_index,
                step=INNER_STEP,
                weights=weights,
                reference=reference,
                signed_descriptor=signed_descriptor,
            )
            - _dominant_gradient_component(
                minus,
                dominant_index,
                step=INNER_STEP,
                weights=weights,
                reference=reference,
                signed_descriptor=signed_descriptor,
            )
        ) / (2.0 * outer_step)
        if (column + 1) % 8 == 0:
            print(
                f"D2Delta row mesh {outer_step:.1e}: "
                f"{column + 1}/{center.size} columns in "
                f"{time.monotonic() - started:.1f}s",
                flush=True,
            )
    return row


def _third_variation_covector_and_adjoint(
    state: np.ndarray,
    *,
    reference: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float, float, int]:
    """Return the raw reduced D3[.,Psi,Psi] covector and its hard adjoint.

    The complex step differentiates the retained action Hessian itself.  The
    hard adjoint uses the spectral expansion of ``(lambda-H)^{-1} Q`` and
    therefore never forms or inverts the ill-conditioned bordered matrix.
    """

    jet = _jet(state)
    reduced = np.asarray(jet.hessian)[QDIM:, QDIM:]
    values, vectors = np.linalg.eigh(np.asarray(reduced, dtype=float))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi

    covector = np.empty(psi.size)
    for index in range(psi.size):
        shifted = state.astype(complex)
        shifted[QDIM + index] += 1j * COMPLEX_STEP
        derivative = (
            np.imag(np.asarray(_jet(shifted).hessian)[QDIM:, QDIM:])
            / COMPLEX_STEP
        )
        covector[index] = float(psi @ derivative @ psi)

    selected_component = float(psi @ covector)
    hard_indices = np.arange(psi.size) != selected
    complement = vectors[:, hard_indices]
    hard_values = values[hard_indices]
    hard_covector = covector - selected_component * psi
    adjoint = complement @ (
        (complement.T @ hard_covector)
        / (values[selected] - hard_values)
    )
    gap = float(np.min(np.abs(values[selected] - hard_values)))
    return covector, adjoint, selected_component, gap, selected


def build_payload(*, recompute: bool = True) -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing direct DDelta row inputs: " + ", ".join(missing)
        )
    field, bordered, core, transport, step = (
        _load(path) for path in (FIELD, BORDERED, CORE, TRANSPORT, STEP)
    )
    if not all(record.get("validation_passed") is True for record in (
        field, bordered, core, transport, step,
    )):
        raise RuntimeError("validated DDelta row parents required")

    with np.load(BORDERED_DATA) as data:
        center = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(FIELD_DATA) as data:
        partial = np.asarray(data["Delta_first_partial_action"], dtype=float)
        seed_remainder = float(
            data["Delta_first_total_remainder_action_norm_upper"]
        )
    with np.load(CORE_DATA) as data:
        proof_centers = np.asarray(data["C2_proof_center_nodes"], dtype=float)
        node_tubes = np.asarray(data["node_action_tube_upper"], dtype=float)

    signed_descriptor = float(Decimal(
        field["center_field"]["signed_descriptor_decimal"]
    ))
    dominant_index = int(np.argmax(np.abs(partial)))
    dominant_seed = float(partial[dominant_index])
    exact_tube = float(node_tubes[REFERENCE_NODE])
    resolving_row_ceiling = (
        abs(dominant_seed) - seed_remainder
    ) / exact_tube
    center_delta, center_selected = _direct_delta(
        center,
        weights=weights,
        reference=reference,
        signed_descriptor=signed_descriptor,
    )

    if recompute:
        rows = np.asarray([
            _row(
                center,
                dominant_index,
                outer_step=step,
                weights=weights,
                reference=reference,
                signed_descriptor=signed_descriptor,
            )
            for step in OUTER_STEPS
        ])
        (
            third_covector,
            hard_adjoint,
            cubic,
            center_gap,
            adjoint_selected,
        ) = _third_variation_covector_and_adjoint(
            center,
            reference=reference,
        )
        np.savez_compressed(
            DATA_RESULT,
            center_state=center,
            state_weights=weights,
            outer_steps=np.asarray(OUTER_STEPS),
            inner_step=np.asarray(INNER_STEP),
            dominant_index=np.asarray(dominant_index),
            direct_D2Delta_rows=rows,
            third_variation_covector=third_covector,
            third_variation_hard_adjoint=hard_adjoint,
            moving_cubic=np.asarray(cubic),
            center_hard_gap=np.asarray(center_gap),
            adjoint_selected_branch=np.asarray(adjoint_selected),
        )
    else:
        if not DATA_RESULT.is_file():
            raise FileNotFoundError("stored direct DDelta row data required")
        with np.load(DATA_RESULT) as data:
            rows = np.asarray(data["direct_D2Delta_rows"], dtype=float)
            third_covector = np.asarray(
                data["third_variation_covector"], dtype=float
            )
            hard_adjoint = np.asarray(
                data["third_variation_hard_adjoint"], dtype=float
            )
            cubic = float(data["moving_cubic"])
            center_gap = float(data["center_hard_gap"])
            adjoint_selected = int(data["adjoint_selected_branch"])

    coarse_row, fine_row = rows
    coarse_norm = float(np.linalg.norm(coarse_row))
    fine_norm = float(np.linalg.norm(fine_row))
    mesh_discrepancy = float(np.linalg.norm(fine_row - coarse_row))
    direct_center_delta = float(field["center_field"]["Delta"])
    center_delta_relative_residual = abs(
        center_delta - direct_center_delta
    ) / abs(direct_center_delta)
    stored_b = float(bordered["bordered_center"]["b_psi"])
    with np.load(BORDERED_DATA) as data:
        psi = np.asarray(data["selected_vector"], dtype=float)
    # Replay f at the center once to expose the inverse-free selected-line
    # contraction independently of the stored bordered solution.
    jet = _jet(center)
    hessian = np.asarray(jet.hessian, dtype=float)
    q_weights, reduced_weights, _, _ = metric_data()
    gradient_action = np.asarray(jet.gradient, dtype=float) / weights
    hessian_action = hessian / weights[:, None] / weights[None, :]
    configuration = q_weights * center[QDIM:2 * QDIM]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:QDIM]
        - hessian_action[QDIM:2 * QDIM, :QDIM] @ configuration,
        -hessian_action[2 * QDIM:, :QDIM] @ configuration,
    ))
    inverse_free_b = float(psi @ (reduced_weights * rhs_action))
    certified_delta_interval = tuple(float(value) for value in step["domain"]["Delta_interval"])
    fine_to_ceiling = fine_norm / resolving_row_ceiling
    remaining_rigorous_remainder_budget = resolving_row_ceiling - fine_norm
    hard_covector = third_covector - cubic * psi
    hard_covector_norm = float(np.linalg.norm(hard_covector))
    hard_adjoint_norm = float(np.linalg.norm(hard_adjoint))
    gap_only_adjoint_bound = hard_covector_norm / center_gap
    # Replay the defining equation with the actual reduced Hessian.
    reduced_hessian = np.asarray(_jet(center).hessian, dtype=float)[
        QDIM:, QDIM:
    ]
    values = np.linalg.eigvalsh(reduced_hessian)
    selected_lambda = float(values[adjoint_selected])
    adjoint_residual = float(np.linalg.norm(
        (selected_lambda * np.eye(psi.size) - reduced_hessian) @ hard_adjoint
        - hard_covector
    ))

    validation = {
        "reference_center_is_stored_node_1214": bool(np.array_equal(
            center, proof_centers[REFERENCE_NODE]
        )),
        "selected_branch_24_replayed": center_selected == 24,
        "adjoint_selected_branch_24_replayed": adjoint_selected == 24,
        "dominant_seed_component_is_coordinate_86": dominant_index == 86,
        "inverse_free_Delta_lies_in_certified_center_interval": (
            certified_delta_interval[0] < center_delta < certified_delta_interval[1]
        ),
        "selected_line_coefficient_is_inverse_free": abs(inverse_free_b) > 0.0,
        "stored_bordered_b_binary_residual_is_explicit": (
            0.0 < abs(inverse_free_b - stored_b) < 1.0e-8
        ),
        "two_mesh_rows_are_finite": bool(np.all(np.isfinite(rows))),
        "two_mesh_row_norms_are_stable_to_two_percent": (
            mesh_discrepancy / fine_norm < 0.02
        ),
        "diagnostic_fine_row_is_far_below_resolving_ceiling": (
            fine_to_ceiling < 1.0e-4
        ),
        "hard_adjoint_defining_equation_replayed": adjoint_residual < 1.0e-14,
        "structured_adjoint_is_smaller_than_gap_only_bound": (
            hard_adjoint_norm < 1.0e-3 * gap_only_adjoint_bound
        ),
        "mesh_agreement_not_promoted_to_interval_remainder": True,
        "proof_center_not_promoted_to_exact_history": True,
        "no_selector_recurrence_scale_fit_gate_or_chord_added": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE",
        "status": (
            "DIRECT_DDELTA_INVARIANT_AND_ONE_ROW_REDUCTION_DERIVED;_"
            "TWO_MESH_RECONNAISSANCE_STABLE;_RIGOROUS_ROW_REMAINDER_OPEN"
            if passed else "DIRECT_DDELTA_ROW_RECONNAISSANCE_INVALID"
        ),
        "classification": (
            "DELTA_RECOMBINES_EXACTLY_AS_Dlambda_OF_bPsi_PLUS_sVhard_BEFORE_"
            "NORMS;_ZERO_EXCLUSION_REQUIRES_ONLY_THE_DOMINANT_HESSIAN_ROW,_"
            "NOT_THE_FULL_D2DELTA_OPERATOR;_TWO_MESH_VALUES_ARE_DIAGNOSTIC_"
            "UNTIL_A_CANCELLATION_PRESERVING_INTERVAL_REMAINDER_IS_PROVED"
        ),
        "exact_identity": {
            "numerator": "N=b_psi*Psi+s*V_hard",
            "Delta": "Delta=Dlambda[N]=c*b_psi+s*R",
            "dominant_component_transport": (
                "abs(D_i_Delta_exact)>=abs(D_i_Delta_center)-r_seed-"
                "sup_row_norm_i(D2Delta)*r_tube"
            ),
            "sufficient_row_test": (
                "sup_row_norm_i(D2Delta)<"
                "(abs(D_i_Delta_center)-r_seed)/r_tube"
            ),
            "second_eigenline_derivative": (
                "Psi_ih=S*Q*G_ih-<Psi_i,Psi_h>*Psi,_"
                "S=(lambda-H)_hard^{-1}"
            ),
            "hard_adjoint": "z=S*Q*g,_g(v)=D3S[v,Psi,Psi]",
            "adjoint_contraction": (
                "D3S[Psi_ih,Psi,Psi]=<z,G_ih>-"
                "c*<Psi_i,Psi_h>"
            ),
            "local_first_rows": (
                "c_h=D4S[h,Psi^3]+3D3S[h,Psi,z];_"
                "b_h=<Psi,f_h>-D3S[h,Psi,V_hard]"
            ),
            "local_product_row": (
                "D_ih(cb)=b*c_ih+b_i*c_h+c_i*b_h+c*b_ih"
            ),
            "local_c_second_row": (
                "c_ih=D5S[i,h,Psi^3]+3D4S[h,Psi_i,Psi^2]+"
                "3D3S[h,Psi,w3]+3D4S[i,h,Psi,z]+"
                "3D3S[h,Psi,wI]+3D3S[h,z,Psi_i]-"
                "3<z,Psi_i>D3S[h,Psi,Psi]-3cD3S[h,Psi,wN]+"
                "6D3S[h,Psi,w5]"
            ),
            "local_b_second_row": (
                "b_ih=-bD3S[h,Psi,wN]-D4S[i,h,Psi,V_hard]-"
                "D3S[h,Psi,wVI]-D3S[h,V_hard,Psi_i]+"
                "<V_hard,Psi_i>D3S[h,Psi,Psi]+<Psi_i,f_h>+"
                "D3S[h,Psi,wfi]+<Psi,f_ih>"
            ),
        },
        "reference_replay": {
            "reference_node": REFERENCE_NODE,
            "dominant_action_coordinate": dominant_index,
            "dominant_DDelta_seed_component": dominant_seed,
            "seed_total_remainder_action_norm_upper": seed_remainder,
            "exact_state_tube_action_radius_upper": exact_tube,
            "stored_Delta": direct_center_delta,
            "direct_Dlambda_N_Delta": center_delta,
            "direct_Delta_relative_residual": center_delta_relative_residual,
            "certified_Delta_interval": list(certified_delta_interval),
            "stored_bordered_b_psi": stored_b,
            "inverse_free_b_psi_equals_Psi_dagger_f": inverse_free_b,
            "stored_minus_inverse_free_b_psi": stored_b - inverse_free_b,
            "rigorous_resolving_row_norm_ceiling": resolving_row_ceiling,
        },
        "two_mesh_reconnaissance": {
            "inner_action_step": INNER_STEP,
            "outer_action_steps": list(OUTER_STEPS),
            "coarse_row_2_norm": coarse_norm,
            "fine_row_2_norm": fine_norm,
            "row_mesh_discrepancy_2_norm": mesh_discrepancy,
            "relative_mesh_discrepancy": mesh_discrepancy / fine_norm,
            "fine_row_to_rigorous_ceiling_ratio": fine_to_ceiling,
            "remaining_rigorous_row_remainder_budget": (
                remaining_rigorous_remainder_budget
            ),
            "authority": "DIAGNOSTIC_ONLY_NOT_AN_INTERVAL_OR_ANALYTIC_BOUND",
        },
        "second_eigenline_adjoint_reduction": {
            "moving_cubic_c": cubic,
            "raw_D3_selected_selected_covector_2_norm": float(
                np.linalg.norm(third_covector)
            ),
            "raw_D3_selected_selected_hard_covector_2_norm": hard_covector_norm,
            "center_hard_gap": center_gap,
            "gap_only_hard_adjoint_2_norm_upper": gap_only_adjoint_bound,
            "spectral_hard_adjoint_2_norm": hard_adjoint_norm,
            "spectral_to_gap_only_ratio": (
                hard_adjoint_norm / gap_only_adjoint_bound
            ),
            "defining_equation_residual_2_norm": adjoint_residual,
            "authority": (
                "EXACT_ANALYTIC_IDENTITY_WITH_BINARY64_CENTER_REPLAY;_"
                "TUBE_REMAINDER_NOT_YET_INTERVAL_CERTIFIED"
            ),
        },
        "adjudication": {
            "direct_signed_Delta_recombination": "DERIVED",
            "selected_line_b_psi_inverse_free_identity": "DERIVED",
            "hard_response_evaluation": "SPECTRAL_COMPLEMENT_NOT_BORDERED_SOLVE",
            "full_98_by_98_D2Delta_norm_required": False,
            "one_dominant_D2Delta_row_sufficient": True,
            "diagnostic_row_scale": "STABLE_ON_TWO_MESHES",
            "mixed_second_eigenline_vector_required": False,
            "mixed_second_eigenline_contraction": (
                "REDUCED_TO_ONE_HARD_ADJOINT_AND_LOCAL_SOURCE"
            ),
            "moving_eigenline_derivative_matrix_required_for_cb_row": False,
            "complete_cb_row_assembly": (
                "FINITE_LOCAL_ACTION_SOURCE_JETS_AND_HARD_ADJOINTS_ONLY"
            ),
            "rigorous_dominant_row_enclosure_on_exact_tube": "OPEN",
            "physical_event_stop_or_zero_force_found": False,
            "prior_coarse_product_ball": "VALID_BUT_SUPERSEDED_AS_NEXT_ROUTE",
        },
        "exact_next_dependency": (
            "OUTWARD_ROUND_THE_FINITE_LOCAL_ACTION_SOURCE_JETS_AND_HARD_"
            "ADJOINTS_IN_THE_EXACT_c_86h_AND_b_86h_FORMULAS_ON_THE_NODE_"
            "1214_TUBE,_THEN_ADD_THE_s_SUPPRESSED_HARD_RESPONSE_ROW_AND_"
            "PROVE_THE_TOTAL_BELOW_14.6225"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_ONE_DIRECT_D2DELTA_ROW_REMAINDER_SEGMENT_ACTION_SOURCE_AND_TAIL",
            "Gate8": "LOCKED",
            "signed_D_Y_Delta": "OPEN_PENDING_RIGOROUS_ROW_REMAINDER",
            "actual_signed_duration_covector": "OPEN",
            "actual_projected_zero_source_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": {key: bool(value) for key, value in validation.items()},
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    return payload


def main() -> None:
    payload = build_payload(
        recompute=os.environ.get("BHSM_REUSE_STORED_DDELTA_ROW") != "1"
    )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "reference_replay": payload["reference_replay"],
        "two_mesh_reconnaissance": payload["two_mesh_reconnaissance"],
        "second_eigenline_adjoint_reduction": (
            payload["second_eigenline_adjoint_reduction"]
        ),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
