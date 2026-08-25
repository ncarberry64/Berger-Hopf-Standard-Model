"""Audit the certified local reset chart as a later-terminal-event route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (  # noqa: E402
    exact_action_jet_at_state,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (  # noqa: E402
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
STATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
THIRD = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_THIRD_VARIATIONS.npz"
ROOT_CERTIFICATE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
RESET = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
)
NHIM_NO_GO = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
)
THEORY = ROOT / "theory/n12_local_reset_terminal_transversality_audit.md"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json"
)
INPUTS = (
    STATE, THIRD, ROOT_CERTIFICATE, CONTINUUM, RESET, NHIM_NO_GO, THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _event_and_forcing(
    state: np.ndarray,
    reference: np.ndarray,
    state_weights: np.ndarray,
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    q_weights = state_weights[:qdim]
    reduced_weights = state_weights[qdim:]
    full = exact_full_action_jet_at_state(
        ORDER,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=POINTS,
    )
    event = exact_action_jet_at_state(
        ORDER,
        state[:qdim],
        state[qdim:2 * qdim],
        state[2 * qdim:],
        points=POINTS,
    )
    hessian_action = (
        np.asarray(full.hessian, dtype=float)
        / state_weights[:, None]
        / state_weights[None, :]
    )
    gradient_action = np.asarray(full.gradient, dtype=float) / state_weights
    values, vectors = np.linalg.eigh(np.asarray(event.hessian, dtype=float))
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    psi = vectors[:, selected]
    if float(psi @ reference) < 0.0:
        psi = -psi
    configuration_rate_action = q_weights * state[qdim:2 * qdim]
    mixed = hessian_action[qdim:, :qdim]
    rhs_action = np.concatenate((
        q_weights * gradient_action[:qdim]
        - mixed[:qdim] @ configuration_rate_action,
        -mixed[qdim:] @ configuration_rate_action,
    ))
    rhs_raw = reduced_weights * rhs_action
    return (
        float(values[selected]),
        float(psi @ rhs_raw),
        psi,
        rhs_raw,
        hessian_action,
    )


def _jet_witness() -> dict[str, object]:
    dims = dimensions(ORDER)
    qdim = dims["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    state_weights = np.concatenate((
        np.sqrt(1.0 + frequencies["coordinates"] ** 2),
        np.ones(qdim),
        np.sqrt(1.0 + frequencies["multipliers"] ** 2),
    ))
    reduced_weights = state_weights[qdim:]
    W = np.diag(reduced_weights)
    with np.load(STATE) as checkpoint:
        child = np.asarray(checkpoint["state"], dtype=float)[98:]
        reference = np.asarray(checkpoint["branch_reference"], dtype=float)
        jacobian = np.asarray(checkpoint["paired_jacobian"], dtype=float)[26:, 98:]
    tangent = null_space(jacobian)
    with np.load(THIRD) as third_file:
        third = np.asarray(third_file["child"], dtype=float)
        stored_weights = np.asarray(third_file["state_weights"], dtype=float)
    if not np.array_equal(state_weights, stored_weights):
        raise RuntimeError("stored action weights changed")

    lam, bpsi, psi, rhs_raw, hessian_action = _event_and_forcing(
        child, reference, state_weights
    )
    raw_event = W @ hessian_action[qdim:, qdim:] @ W
    values, vectors = np.linalg.eigh(raw_event)
    selected = int(np.argmax(np.abs(vectors.T @ reference)))
    complement = np.delete(vectors, selected, axis=1)
    gaps = values[selected] - np.delete(values, selected)
    q_weights = state_weights[:qdim]
    configuration_rate_action = q_weights * child[qdim:2 * qdim]
    mixed = hessian_action[qdim:, :qdim]

    lambda_gradient = np.empty(tangent.shape[1])
    bpsi_gradient = np.empty(tangent.shape[1])
    for column, action_direction in enumerate(tangent.T):
        derivative_hessian_action = np.tensordot(
            third, action_direction, axes=(2, 0)
        )
        derivative_event = W @ derivative_hessian_action[qdim:, qdim:] @ W
        lambda_gradient[column] = float(psi @ derivative_event @ psi)
        coupling = complement.T @ derivative_event @ psi
        dpsi = complement @ (coupling / gaps)
        derivative_gradient_action = hessian_action @ action_direction
        derivative_mixed = derivative_hessian_action[qdim:, :qdim]
        derivative_configuration_rate = (
            q_weights * action_direction[qdim:2 * qdim]
        )
        derivative_rhs_action = np.concatenate((
            q_weights * derivative_gradient_action[:qdim]
            - derivative_mixed[:qdim] @ configuration_rate_action
            - mixed[:qdim] @ derivative_configuration_rate,
            -derivative_mixed[qdim:] @ configuration_rate_action
            - mixed[qdim:] @ derivative_configuration_rate,
        ))
        derivative_rhs_raw = reduced_weights * derivative_rhs_action
        bpsi_gradient[column] = float(dpsi @ rhs_raw + psi @ derivative_rhs_raw)

    lambda_norm = float(np.linalg.norm(lambda_gradient))
    bpsi_norm = float(np.linalg.norm(bpsi_gradient))
    b_coefficients = -np.sign(bpsi) * bpsi_gradient / bpsi_norm
    b_direction = tangent @ b_coefficients
    step = 1.0e-6
    plus = child + step * b_direction / state_weights
    minus = child - step * b_direction / state_weights
    lambda_plus, bpsi_plus, *_ = _event_and_forcing(plus, reference, state_weights)
    lambda_minus, bpsi_minus, *_ = _event_and_forcing(minus, reference, state_weights)
    lambda_directional = float(lambda_gradient @ b_coefficients)
    bpsi_directional = -bpsi_norm
    lambda_finite = float((lambda_plus - lambda_minus) / (2.0 * step))
    bpsi_finite = float((bpsi_plus - bpsi_minus) / (2.0 * step))
    return {
        "fixed_event_child_jacobian_shape": list(jacobian.shape),
        "fixed_event_child_rank": int(np.linalg.matrix_rank(jacobian)),
        "raw_reset_tangent_dimension": int(tangent.shape[1]),
        "constraint_tangency_Frobenius_norm": float(np.linalg.norm(jacobian @ tangent)),
        "center": {"ordered_event_lambda": lam, "b_psi": bpsi},
        "projected_action_gradient_norm": {
            "ordered_event_lambda": lambda_norm,
            "b_psi": bpsi_norm,
        },
        "linearized_action_distance": {
            "ordered_event_lambda_to_zero": abs(lam) / lambda_norm,
            "b_psi_to_zero": abs(bpsi) / bpsi_norm,
        },
        "steepest_b_psi_crosscheck": {
            "action_step": step,
            "analytic_lambda_derivative": lambda_directional,
            "centered_lambda_derivative": lambda_finite,
            "lambda_relative_residual": abs(lambda_finite - lambda_directional)
            / max(abs(lambda_directional), 1.0e-300),
            "analytic_b_psi_derivative": bpsi_directional,
            "centered_b_psi_derivative": bpsi_finite,
            "b_psi_relative_residual": abs(bpsi_finite - bpsi_directional)
            / max(abs(bpsi_directional), 1.0e-300),
        },
    }


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing local-reset audit inputs: " + ", ".join(missing))
    root = _load(ROOT_CERTIFICATE)
    continuum = _load(CONTINUUM)
    reset = _load(RESET)
    no_go = _load(NHIM_NO_GO)
    if not all(record.get("validation_passed") is True for record in (
        root, continuum, reset, no_go,
    )):
        raise RuntimeError("validated local-reset audit inputs required")
    witness = _jet_witness()
    root_radius = float(root["certified_root_ball"]["radius"])
    continuum_radius = float(
        continuum["nonlinear_continuum_radius"]
        ["existing_physical_neighborhood_radius_lower"]
    )
    lambda_distance = witness["linearized_action_distance"][
        "ordered_event_lambda_to_zero"
    ]
    bpsi_distance = witness["linearized_action_distance"]["b_psi_to_zero"]
    ratios = {
        "lambda_distance_over_direct_root_radius": lambda_distance / root_radius,
        "b_psi_distance_over_direct_root_radius": bpsi_distance / root_radius,
        "lambda_distance_over_continuum_neighborhood": lambda_distance / continuum_radius,
        "b_psi_distance_over_continuum_neighborhood": bpsi_distance / continuum_radius,
    }
    crosscheck = witness["steepest_b_psi_crosscheck"]
    validation = {
        "all_inputs_validated": True,
        "fixed_event_child_block_has_rank_31": witness["fixed_event_child_rank"] == 31,
        "raw_reset_tangent_dimension_is_67": witness["raw_reset_tangent_dimension"] == 67,
        "stored_kernel_is_tangent_to_roundoff": witness[
            "constraint_tangency_Frobenius_norm"
        ] < 1.0e-10,
        "child_starts_on_positive_ordered_event_side": witness["center"][
            "ordered_event_lambda"
        ] > 0.0,
        "child_soft_forcing_is_forward_emergent": witness["center"]["b_psi"] > 0.0,
        "projected_lambda_and_bpsi_jets_are_nonzero": all(
            value > 0.0 for value in witness["projected_action_gradient_norm"].values()
        ),
        "linearized_lambda_target_is_outside_direct_root_ball_by_billions": ratios[
            "lambda_distance_over_direct_root_radius"
        ] > 1.0e9,
        "linearized_bpsi_target_is_outside_direct_root_ball_by_billions": ratios[
            "b_psi_distance_over_direct_root_radius"
        ] > 1.0e9,
        "targets_are_outside_continuum_transfer_neighborhood": min(
            ratios["lambda_distance_over_continuum_neighborhood"],
            ratios["b_psi_distance_over_continuum_neighborhood"],
        ) > 1.0e12,
        "direct_action_directional_crosscheck_is_consistent": max(
            crosscheck["lambda_relative_residual"],
            crosscheck["b_psi_relative_residual"],
        ) < 0.2,
        "no_global_reset_nonexistence_claimed": True,
        "no_finite_hit_or_stop_promoted_from_linearization": True,
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT",
        "status": (
            "CERTIFIED_LOCAL_RESET_CHART_DOES_NOT_SUPPLY_A_LATER_EVENT_"
            "OR_STOP_STRATUM"
        ),
        "classification": (
            "THE_FIXED_EVENT_CHILD_RESET_KERNEL_HAS_NONZERO_ORDERED_EVENT_"
            "AND_SOFT_FORCING_JETS,_BUT_THEIR_BEST_LINEARIZED_ZERO_TARGETS_"
            "LIE_BILLIONS_OF_CERTIFIED_ROOT_RADII_FROM_THE_CURRENT_CHILD;_"
            "THE_EXISTING_LOCAL_RESET_SUBMERSION_THEOREM_THEREFORE_CANNOT_"
            "CERTIFY_A_LATER_EVENT,_TERMINAL_ORIENTATION_REVERSAL,_OR_"
            "CANONICAL_STOP_WITHOUT_A_GLOBAL_RESET_STRATUM_CONTINUATION_THEOREM"
        ),
        "witness": witness,
        "certified_scope_comparison": {
            "direct_root_action_radius": root_radius,
            "continuum_physical_neighborhood_radius": continuum_radius,
            **ratios,
        },
        "route_adjudication": {
            "local_reset_IFT_supplies_finite_stratum": False,
            "global_reset_quotient_finite_stratum_disproved": False,
            "favorable_reset_child_selected": False,
            "new_canonical_stop_declared": False,
            "numerical_forward_campaign_authorized": False,
            "mathematical_infinite_branches_preserved": True,
        },
        "exact_next_dependency": (
            "DERIVE_AN_ACTION_OWNED_GLOBAL_CONTINUATION_OR_NONZERO_DEGREE_"
            "THEOREM_FOR_A_REGULAR_FINITE_EVENT_OR_CANONICAL_STOP_STRATUM_"
            "OF_THE_PHYSICAL_RESET_QUOTIENT,_OR_SUPPLY_AN_INDEPENDENTLY_"
            "CERTIFIED_FINITE_STRATUM;_DO_NOT_EXTRAPOLATE_THE_LOCAL_RESET_"
            "CHART_OR_SELECT_A_FAVORABLE_CHILD"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_GLOBAL_FINITE_RESET_STRATUM_EXISTENCE",
            "Gate8": "LOCKED",
            "local_reset_terminal_transversality_route": "CLOSED_INSUFFICIENT",
            "actual_finite_stratum": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
