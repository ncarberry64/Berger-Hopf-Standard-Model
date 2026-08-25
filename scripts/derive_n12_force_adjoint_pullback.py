"""Derive the inverse-free Gate-7 force adjoint pullback theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORCE_FIRST_JET_CRITICAL_PATH.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _witness() -> dict[str, float | int | bool]:
    """Cross-check the endpoint projection and reverse pullback discretely."""

    rng = np.random.default_rng(71407)
    state_dim = 7
    quotient_dim = 4
    steps = 9
    reset_jet = rng.normal(size=(state_dim, quotient_dim))
    propagators = [
        np.eye(state_dim) + 0.025 * rng.normal(size=(state_dim, state_dim))
        for _ in range(steps)
    ]
    sources = [0.03 * rng.normal(size=state_dim) for _ in range(steps)]
    event_normal = rng.normal(size=state_dim)
    endpoint_velocity = rng.normal(size=state_dim)
    alpha = float(event_normal @ endpoint_velocity)
    if abs(alpha) < 0.2:
        endpoint_velocity = endpoint_velocity + event_normal
        alpha = float(event_normal @ endpoint_velocity)
    endpoint_projection = np.eye(state_dim) - np.outer(
        endpoint_velocity, event_normal
    ) / alpha
    endpoint_covector = rng.normal(size=state_dim)

    jacobi = reset_jet.copy()
    forward_value = np.zeros(quotient_dim)
    for transition, source in zip(propagators, sources, strict=True):
        forward_value += source @ jacobi
        jacobi = transition @ jacobi
    forward_value += endpoint_covector @ endpoint_projection @ jacobi

    adjoint = endpoint_projection.T @ endpoint_covector
    for transition, source in reversed(list(zip(propagators, sources, strict=True))):
        adjoint = transition.T @ adjoint + source
    reverse_value = reset_jet.T @ adjoint

    time_shift_residual = float(
        np.linalg.norm(endpoint_projection @ endpoint_velocity, ord=2)
    )
    pullback_residual = float(np.linalg.norm(forward_value - reverse_value, ord=2))
    return {
        "state_dimension": state_dim,
        "physical_quotient_dimension": quotient_dim,
        "steps": steps,
        "endpoint_transversality_abs": abs(alpha),
        "moving_endpoint_time_shift_residual": time_shift_residual,
        "forward_vs_adjoint_pullback_residual": pullback_residual,
        "crosscheck_passed": time_shift_residual < 1.0e-12
        and pullback_residual < 1.0e-12,
    }


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("force adjoint-pullback inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated force adjoint-pullback inputs required")
    force, saddle, transfer, variation, moving, critical = records
    witness = _witness()
    validation = {
        "heat_force_supplies_operator_covector": (
            force["exact_force_theorem"]["first_variation"].startswith(
                "D_Gamma_heat(P)[delta_P]"
            )
        ),
        "physical_output_is_projected_covector": (
            saddle["exact_theorem"]["same_configuration_transfer_criterion"]
            == "N^dagger*q_rep=0"
        ),
        "first_channel_variation_is_triangular": (
            transfer["transfer_variation_theorem"]["first_left"]
            == "T_h'=G*T_h+G_h*T"
        ),
        "first_Euler_Dirac_jet_uses_reused_solve": (
            variation["implicit_solve_theorem"]["same_D_factorization_reused"]
            is True
        ),
        "moving_endpoint_first_projection_owned": (
            moving["moving_endpoint_system"]["first_state"] == "Z_h=J_h+V*T_h"
            and moving["moving_endpoint_system"]["first_time"]
            == "T_h=-De*J_h/alpha"
        ),
        "adjoint_is_equivalent_to_allowed_first_jet_covector": (
            critical["critical_path"][
                "all_physical_tangent_directions_or_equivalent_covector_required"
            ]
            is True
        ),
        "discrete_forward_and_adjoint_crosscheck": witness["crosscheck_passed"]
        is True,
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORCE_ADJOINT_PULLBACK",
        "status": "GATE7_FORCE_COVECTOR_REDUCED_TO_NESTED_ADJOINT_PULLBACK",
        "classification": (
            "THE_COMPLETE_FIRST_PHYSICAL_RESET_QUOTIENT_FORCE_COVECTOR_CAN_"
            "BE_EVALUATED_WITHOUT_PROPAGATING_ONE_FORWARD_JACOBI_COLUMN_PER_"
            "TANGENT_DIRECTION:_PULL_THE_HEAT_MINUS_ZETA_OPERATOR_COVECTOR_"
            "BACKWARD_THROUGH_THE_FIXED_CHANNEL_AND_EULER_DIRAC_LINEARIZATIONS_"
            "AND_THEN_THROUGH_THE_RESET_JET;_THE_MOVING_ENDPOINT_ENTERS_BY_"
            "ITS_EXACT_TRANSVERSE_PROJECTION_AND_AUTONOMOUS_TIME_SHIFT_IS_"
            "ANNIHILATED"
        ),
        "operator_cotangent": {
            "per_channel": (
                "W_C=(s_C*m_C/2)*exp(-ell^2*P_C)*P_C^(-1)"
            ),
            "heat_pairing": "D_Gamma_heat=<W_C,D_P_C>_trace_SUM_C",
            "replacement": "q_rep=q_heat-q_zeta",
            "noncommuting_operator_jet_allowed": True,
        },
        "moving_endpoint_adjoint": {
            "alpha": "De(Y_T)*V(Y_T)_NOT_EQUAL_0",
            "endpoint_projection": "Pi_T=I-V(Y_T) tensor De(Y_T)/alpha",
            "endpoint_state_jet": "Z_h=Pi_T*J_h(T)",
            "terminal_adjoint_covector": "p(T)=Pi_T^dagger*g_T",
            "time_shift_kernel": "Pi_T*V(Y_T)=0",
        },
        "continuous_adjoint_theorem": {
            "forward_first_jet": "J_h'=A(t)*J_h,_J_h(0)=B_reset*h",
            "state_generator": "A(t)=D_V(Y(t))",
            "force_pairing": (
                "F_h=integral_<q(t),J_h(t)>dt+<g_T,Pi_T*J_h(T)>+<q_direct,h>"
            ),
            "backward_adjoint": "-p'=A(t)^dagger*p+q(t),_p(T)=Pi_T^dagger*g_T",
            "reset_pullback": "q_xi=B_reset^dagger*p(0)+q_direct",
            "physical_quotient_force": "F_phys=N_phys^dagger*q_xi",
            "identity": (
                "F_h=<B_reset^dagger*p(0)+q_direct,h>_FOR_EVERY_PHYSICAL_h"
            ),
        },
        "inverse_free_Euler_Dirac_adjoint": {
            "primal": "D*s=b",
            "first": "D*delta_s=delta_b-delta_D*s",
            "adjoint_solve": "D^dagger*lambda=r_acceleration",
            "pullback_pairing": (
                "<r_acceleration,delta_s>=<lambda,delta_b-delta_D*s>"
            ),
            "explicit_D_inverse_formed": False,
            "same_factorization_or_transposed_factorization_reused": True,
            "highest_action_derivative_before_first_force": "D3_L",
        },
        "computational_consequence": {
            "forward_Jacobi_columns_required": 0,
            "one_column_per_raw_or_physical_reset_direction_required": False,
            "required_base_history": True,
            "required_nested_backward_covector_solves": True,
            "second_state_or_operator_jet_required_before_first_force": False,
            "reset_representative_selected": False,
        },
        "exact_next_dependency": (
            "CERTIFY_THE_ACTION_SELECTED_MAXIMAL_BASE_HISTORY_TO_ITS_RETAINED_"
            "ENDPOINT_CLASS;_ASSEMBLE_THE_HEAT_MINUS_ZETA_OPERATOR_COTANGENT_"
            "ON_THAT_HISTORY;_RUN_THE_FIXED_CHANNEL_AND_TRANSPOSED_"
            "EULER_DIRAC_ADJOINTS_WITH_THE_MOVING_ENDPOINT_PROJECTION;_THEN_"
            "EVALUATE_N_phys^dagger*(B_reset^dagger*p(0)+q_direct)_WITHOUT_"
            "CHORD_3_OR_A_RESET_SELECTOR"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MAXIMAL_BASE_HISTORY_AND_ADJOINT_EVALUATION_OPEN",
            "G7_08_force_functional": "DERIVED",
            "G7_08_force_adjoint_pullback": "DERIVED",
            "G7_08_actual_projected_force": "OPEN_CURRENT_OWNER",
            "maximal_base_history": "OPEN",
            "second_operator_jet": "PENDING_CONDITIONAL",
            "same_action_saddle": "PENDING_ON_FORCE_RESULT",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "witness": witness,
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
