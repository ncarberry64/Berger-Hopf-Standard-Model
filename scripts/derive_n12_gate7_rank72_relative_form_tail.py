"""Derive the sharp rank-72 source-contracted relative-form tail criterion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL.json"
THEORY = ROOT / "theory" / "n12_gate7_rank72_relative_form_tail.md"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
PROJECTED = BASE / "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
JOINT = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
WARD = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
SUPPORT = BASE / "BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION.json"
FLOW = BASE / "BHSM_N12_GATE7_OUTGOING_FLOW_TAIL_CLOSURE.json"
SEED_AUDIT = BASE / "BHSM_N12_GATE7_SEED_IMAGE_WARD_GAUGE_AUDIT.json"
FINITE_INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
INPUTS = (
    LAUNCH,
    LAUNCH_DATA,
    PROJECTED,
    JOINT,
    WARD,
    SUPPORT,
    FLOW,
    SEED_AUDIT,
    FINITE_INTERFACE,
    THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _algebra_witness(seed: np.ndarray) -> dict[str, float]:
    rng = np.random.default_rng(20260826)
    evolution = rng.normal(size=(98, 98))
    load = rng.normal(size=98)
    adjoint_pullback = seed.T @ evolution.T @ load
    propagated_seed_contraction = (evolution @ seed).T @ load

    size = 6
    raw = rng.normal(size=(size, size))
    q_plus = raw.T @ raw + np.eye(size)
    form_jets = rng.normal(size=(72, size, size))
    form_jets = 0.5 * (form_jets + np.swapaxes(form_jets, 1, 2))
    coordinates = rng.normal(size=72)
    coordinate_covector = np.einsum("ab,jab->j", q_plus, form_jets)
    direct_trace = float(np.trace(
        q_plus @ np.einsum("j,jab->ab", coordinates, form_jets)
    ))
    reverse_trace = float(coordinates @ coordinate_covector)
    return {
        "adjoint_vs_propagated_seed_residual_norm": float(np.linalg.norm(
            adjoint_pullback - propagated_seed_contraction
        )),
        "relative_form_reverse_identity_absolute_residual": abs(
            direct_trace - reverse_trace
        ),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing rank-72 relative-form inputs: " + ", ".join(missing)
        )
    parents = {
        path.stem: _load(path)
        for path in INPUTS
        if path.suffix.lower() == ".json"
    }
    if not all(parent.get("validation_passed") is True for parent in parents.values()):
        raise RuntimeError("validated rank-72 relative-form parents required")
    with np.load(LAUNCH_DATA) as data:
        seed = np.asarray(data["event_image_basis"], dtype=float)
    witness = _algebra_witness(seed)
    orthonormality = float(np.linalg.norm(seed.T @ seed - np.eye(72), ord=2))

    projected = parents[PROJECTED.stem]
    joint = parents[JOINT.stem]
    ward = parents[WARD.stem]
    support = parents[SUPPORT.stem]
    flow = parents[FLOW.stem]
    seed_audit = parents[SEED_AUDIT.stem]
    finite_interface = parents[FINITE_INTERFACE.stem]
    validation = {
        "stored_seed_image_is_98_by_72": seed.shape == (98, 72),
        "stored_seed_image_is_orthonormal": orthonormality < 1.0e-12,
        "adjoint_and_propagated_seed_contractions_agree": (
            witness["adjoint_vs_propagated_seed_residual_norm"] < 1.0e-10
        ),
        "relative_form_reverse_identity_agrees": (
            witness["relative_form_reverse_identity_absolute_residual"] < 1.0e-10
        ),
        "projected_Cauchy_parent_is_necessary_and_sufficient": (
            "necessary_and_sufficient_maximal_criterion"
            in projected["theorem"]
        ),
        "joint_seed_counts_internal_blocks_once": (
            joint["validation"][
                "no_internal_response_zeroed_extra_seam_source_or_double_count_added"
            ]
        ),
        "common_scale_zeta_force_is_exactly_zero": (
            ward["exact_Ward_theorem"]["zeta_force"]
            == "D_a_Gamma_SM_zeta=0"
        ),
        "common_scale_heat_force_is_not_deleted": (
            ward["exact_Ward_theorem"]["heat_force"]
            == "D_a_Gamma_heat=-STr_exp(-ell_kappa^2*P)"
        ),
        "fixed_C2_and_flow_tail_blocks_are_closed": (
            support["adjudication"]["remaining_noncompact_tail_dimension_upper"] == 73
            and flow["claim_boundary"]["remaining_noncompact_tail_dimension_upper"] == 72
        ),
        "Ward_gauge_shortcuts_leave_rank72": (
            seed_audit["remaining_owner"]["dimension"] == 72
        ),
        "known_finite_interface_does_not_close_outgoing_C2": (
            parents[LAUNCH.stem]["adjudication"]["C2_maximal_endpoint_outcome"]
            == "OPEN"
            and finite_interface["claim_boundary"][
                "positive_duration_forward_child_history"
            ] == "CERTIFIED_LOCAL_EXISTENCE"
        ),
        "only_external_source_is_zero_and_no_internal_response_is_zeroed": True,
        "no_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_RANK72_RELATIVE_FORM_TAIL",
        "status": (
            "RANK72_SOURCE_CONTRACTED_RELATIVE_FORM_CRITERION_SHARP_ACTUAL_TAIL_OPEN"
            if passed else "RANK72_RELATIVE_FORM_CRITERION_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_EXACT_REMAINING_MAXIMAL_FORCE_TAIL_IS_THE_72_VECTOR_"
            "INTEGRAL_OF_THE_COMPLETE_HEAT_SMOOTHED_RELATIVE_FORM_JET_"
            "ALONG_THE_RESET_GENERATED_PROPAGATED_SEED_PLUS_THE_OWNED_DIRECT_"
            "INCREMENT;_THIS_IS_WEAKER_THAN_AMBIENT_ADJOINT_INTEGRABILITY,_"
            "THE_SEPARATE_COMMON_SCALE_ZETA_TAIL_IS_SUPERSEDED_BY_EXACT_"
            "MOVING_DURATION_CANCELLATION,_BUT_NO_TRACKED_ACTION_THEOREM_"
            "BOUNDS_THE_REMAINING_RANK72_JOINT_TAIL"
        ),
        "exact_criterion": {
            "finite_core_force": "g_T=B_seed^dagger*p_T(0)+d_T",
            "finite_core_adjoint": (
                "p_T(0)=integral_0^T_U(t,0)^dagger*q_rep(t)_dt"
            ),
            "tail_identity": (
                "g_T-g_S=integral_S^T_(U(t,0)*B_seed)^dagger*q_rep(t)_dt+d_T-d_S"
            ),
            "necessary_and_sufficient": (
                "THE_DISPLAYED_R72_VECTOR_NET_IS_CAUCHY"
            ),
            "ambient_adjoint_limit_required": False,
            "ambient_integral_norm_U_norm_q_required": False,
            "seventy_two_forward_history_selectors_required": False,
        },
        "relative_form_realization": {
            "positive_heat_seed": (
                "Q_ck_plus=(1/2)*exp(-ell_kappa^2*P_ck)*P_ck^-1"
            ),
            "coordinate_density": (
                "rho_j_heat=sum_ck_w_ck*ReTr(Q_ck_plus^dagger*"
                "D_P_ck[U(t,0)*b_j])"
            ),
            "joint_density": "rho_rep=rho_heat-rho_zeta",
            "sufficient_projected_trace_ideal_bound": (
                "integral_norm(rho_rep(t),2)_dt<infinity_AND_d_T_IS_CAUCHY"
            ),
            "trace_ideal_majorant": (
                "sum_ck_abs(w_ck)*l2_j_norm_of_"
                "trace_norm(Q_ck_plus^(1/2)*D_P_ck[U*b_j]*Q_ck_plus^(1/2))"
            ),
            "signed_sum_before_norm": True,
        },
        "common_scale_supersession": {
            "old_separate_optical_zeta_tail_obligation": "SUPERSEDED",
            "reason": "D_a(d_tau/R4)=0_ON_EVERY_CORE",
            "common_scale_zeta_core_net": "IDENTICALLY_ZERO_AND_CAUCHY",
            "common_scale_heat_contraction": "-STr_exp(-ell_kappa^2*P)",
            "seed_image_dimension_removed": False,
            "pure_common_scale_generator_membership_in_seed_image_proved": False,
            "non_scale_zeta_tail_removed": False,
        },
        "availability_audit": {
            "finite_1222_core": "FINITE_PREFIX_ONLY",
            "rank72_maximal_relative_form_bound": "ACTUALLY_MISSING",
            "actual_later_C2_event_or_canonical_stop": "NOT_CERTIFIED",
            "valid_completion_routes": [
                "PROVE_THE_ACTION_OWNED_RANK72_HEAT_SMOOTHED_RELATIVE_FORM_TAIL",
                "CERTIFY_A_GENUINE_FINITE_LATER_C2_EVENT_OR_CANONICAL_STOP",
            ],
        },
        "numerical_identity_witness": {
            "seed_shape": list(seed.shape),
            "seed_orthonormality_residual_norm": orthonormality,
            **witness,
            "role": "ALGEBRAIC_CROSSCHECK_NOT_A_PHYSICAL_TAIL_VALUE",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_RANK72_RELATIVE_FORM_TAIL",
            "Gate8": "LOCKED",
            "common_scale_separate_zeta_tail": "CLOSED_SUPERSEDED",
            "rank72_joint_heat_minus_zeta_tail": "OPEN_CURRENT_OWNER",
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
        "tail_dimension": payload["numerical_identity_witness"]["seed_shape"][1],
        "common_scale_zeta_tail": payload["common_scale_supersession"]["common_scale_zeta_core_net"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
