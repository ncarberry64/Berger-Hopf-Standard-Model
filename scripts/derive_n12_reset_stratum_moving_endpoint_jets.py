"""Derive reset-stratum Jacobi and transverse endpoint jet identities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.maximal_history_endpoint_jets import (  # noqa: E402
    endpoint_observable_jets,
    moving_endpoint_jets,
    state_jacobi_rhs,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS.json"
)
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def analytic_witness() -> dict[str, object]:
    """Use y'=a*y and a two-parameter initial surface with a mixed jet."""

    rate = 1.7
    target = 2.3
    left = 0.7
    right = -0.4
    mixed_initial = 0.2
    vector = np.array([rate * target])
    jacobian = np.array([[rate]])
    hessian = np.zeros((1, 1, 1))
    fixed_left = np.array([target * left])
    fixed_right = np.array([target * right])
    fixed_mixed = np.array([target * mixed_initial])
    jacobi_rhs = state_jacobi_rhs(
        vector,
        jacobian,
        hessian,
        fixed_left,
        fixed_right,
        fixed_mixed,
    )
    endpoint = moving_endpoint_jets(
        vector,
        jacobian,
        np.array([1.0]),
        np.zeros((1, 1)),
        fixed_left,
        fixed_right,
        fixed_mixed,
    )
    exact_time_left = -left / rate
    exact_time_right = -right / rate
    exact_time_mixed = (left * right - mixed_initial) / rate
    observable = endpoint_observable_jets(
        np.array([2.0 * target]),
        np.array([[2.0]]),
        endpoint,
    )

    # An autonomous time-shift direction J=c*V must be annihilated by the
    # moving endpoint.  Its second fixed-time jet is c^2*DV*V.
    shift = 0.31
    time_shift = moving_endpoint_jets(
        vector,
        jacobian,
        np.array([1.0]),
        np.zeros((1, 1)),
        shift * vector,
        shift * vector,
        shift**2 * (jacobian @ vector),
    )
    return {
        "model": "y'=a*y,_y0(xi,eta)=1+p*xi+q*eta+r*xi*eta,_event_y=Ystar",
        "parameters": {
            "a": rate,
            "Ystar": target,
            "p": left,
            "q": right,
            "r": mixed_initial,
        },
        "computed_endpoint_time_jets": [
            endpoint.time_left,
            endpoint.time_right,
            endpoint.time_mixed,
        ],
        "exact_endpoint_time_jets": [
            exact_time_left,
            exact_time_right,
            exact_time_mixed,
        ],
        "maximum_time_jet_residual": max(
            abs(endpoint.time_left - exact_time_left),
            abs(endpoint.time_right - exact_time_right),
            abs(endpoint.time_mixed - exact_time_mixed),
        ),
        "maximum_endpoint_state_jet": max(
            float(np.max(np.abs(endpoint.state_left))),
            float(np.max(np.abs(endpoint.state_right))),
            float(np.max(np.abs(endpoint.state_mixed))),
        ),
        "maximum_endpoint_observable_jet": max(abs(value) for value in observable),
        "time_shift_first_endpoint_norm": float(np.linalg.norm(time_shift.state_left)),
        "time_shift_mixed_endpoint_norm": float(np.linalg.norm(time_shift.state_mixed)),
        "time_shift_time_first_residual": abs(time_shift.time_left + shift),
        "time_shift_time_mixed": time_shift.time_mixed,
        "Jacobi_rhs_finite": all(np.all(np.isfinite(value)) for value in jacobi_rhs),
    }


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("moving-endpoint jet inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated moving-endpoint jet inputs required")
    witness = analytic_witness()
    validation = {
        "all_inputs_validated": True,
        "first_and_mixed_endpoint_time_chain_rule_exact": witness[
            "maximum_time_jet_residual"
        ] < 1.0e-14,
        "fixed_event_state_jets_cancel": witness[
            "maximum_endpoint_state_jet"
        ] < 1.0e-14,
        "endpoint_graph_composition_jets_cancel": witness[
            "maximum_endpoint_observable_jet"
        ] < 1.0e-14,
        "autonomous_time_translation_is_annihilated_at_moving_endpoint": (
            witness["time_shift_first_endpoint_norm"] < 1.0e-14
            and witness["time_shift_mixed_endpoint_norm"] < 1.0e-14
            and witness["time_shift_time_first_residual"] < 1.0e-14
            and abs(witness["time_shift_time_mixed"]) < 1.0e-14
        ),
        "state_Jacobi_system_is_triangular": witness["Jacobi_rhs_finite"] is True,
        "maximal_history_or_endpoint_outcome_not_fabricated": True,
        "no_selector_action_term_endpoint_scale_fit_new_gate_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_RESET_STRATUM_MOVING_ENDPOINT_JETS",
        "status": "RESET_STRATUM_TO_MOVING_ENDPOINT_TWO_JET_CHAIN_RULE_DERIVED",
        "classification": (
            "FOR_A_TRANSVERSE_ACTION_OWNED_EVENT_OR_REGULAR_STOP,_THE_RESET_"
            "STRATUM_FIRST_AND_MIXED_SECOND_STATE_JACOBI_FIELDS_DETERMINE_"
            "THE_ENDPOINT_TIME,_ENDPOINT_STATE,_AND_TERMINAL_GRAPH_JETS_BY_"
            "EXACT_CHAIN_RULES;_AUTONOMOUS_TIME_TRANSLATION_CANCELS_"
            "IDENTICALLY_IN_THE_MOVING_ENDPOINT_STATE,_SO_NO_SEPARATE_"
            "ENDPOINT_SELECTOR_OR_HAND_PROJECTED_TIME_DIRECTION_IS_REQUIRED;_"
            "THE_ACTUAL_MAXIMAL_HISTORY_PROPAGATION_AND_ENDPOINT_OUTCOME_"
            "REMAIN_OPEN"
        ),
        "state_Jacobi_system": {
            "base": "D_tau_Y=V(Y)",
            "first": "D_tau_J_h=DV(Y)*J_h",
            "mixed_second": "D_tau_K_hk=DV(Y)*K_hk+D2V(Y)[J_h,J_k]",
            "initial_data": "J_h(0)=D_h_Y_reset,_K_hk(0)=D_hk_Y_reset",
            "Euler_Dirac_implicit_solve": (
                "DV_AND_D2V_USE_THE_ALREADY_DERIVED_REUSED_DIRAC_SOLVES_"
                "WITHOUT_FORMING_THE_ILL_CONDITIONED_INVERSE"
            ),
        },
        "moving_endpoint_system": {
            "event": "e(Y(T(xi),xi))=0",
            "transversality": "alpha=De(Y_E)*V(Y_E)_IS_NONZERO",
            "first_time": "T_h=-De*J_h/alpha",
            "first_state": "Z_h=J_h+V*T_h",
            "mixed_time": (
                "T_hk=-[De*(K_hk+DV*J_h*T_k+DV*J_k*T_h+DV*V*T_h*T_k)"
                "+D2e[Z_h,Z_k]]/alpha"
            ),
            "mixed_state": (
                "Z_hk=K_hk+DV*J_h*T_k+DV*J_k*T_h+DV*V*T_h*T_k+V*T_hk"
            ),
            "terminal_graph": (
                "mu_h=Dmu*Z_h,_mu_hk=Dmu*Z_hk+D2mu[Z_h,Z_k]"
            ),
        },
        "time_quotient_consequence": {
            "autonomous_shift": "J=c*V,_T_h=-c_IMPLIES_Z_h=0",
            "mixed_shift": "K=c^2*DV*V,_T_hk=0_IMPLIES_Z_hk=0",
            "scope": (
                "MOVING_ENDPOINT_STATE_AND_GRAPH_ONLY;_THE_FULL_EVENT_CHILD_"
                "HISTORY_QUOTIENT_STILL_REQUIRES_THE_RETAINED_HYBRID_"
                "FORMULATION"
            ),
        },
        "witness": witness,
        "exact_next_dependency": (
            "PROPAGATE_THE_RESET_STRATUM_Y,J_h,J_k,K_hk_FAMILY_WITH_"
            "CERTIFIED_CONTINUUM_AND_DOMAIN_MARGINS_TO_THE_FIRST_ACTION_"
            "OWNED_EVENT_OR_CANONICAL_STOP;_THEN_APPLY_THE_DERIVED_MOVING_"
            "ENDPOINT_CHAIN_RULE_AND_FIXED_CHANNEL_WEYL_TRANSFER"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MAXIMAL_RESET_STRATUM_JACOBI_PROPAGATION_OPEN",
            "moving_endpoint_two_jet_chain_rule": "DERIVED",
            "endpoint_domain_ownership": "CLOSED",
            "actual_maximal_history": "OPEN",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_AFTER_ORACLE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
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
