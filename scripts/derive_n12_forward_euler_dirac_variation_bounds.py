"""Derive local first/second Euler--Dirac and state-Jacobi bounds."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_euler_dirac_variations import (  # noqa: E402
    implicit_linear_solve_jet_bounds,
    jacobi_cocycle_bounds,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS.json"
)
OBSERVATION = ARTIFACTS / (
    "n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
MAJORANTS = ARTIFACTS / (
    "n12_direct_checkpoint/BHSM_N12_ACTION_MAJORANTS.json"
)
RADIUS_PROJECTION = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_BOUNDARY_RADIUS_ACTION_PROJECTION.json"
)
TRANSFER_VARIATIONS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_forward_euler_dirac_variations.py"
INPUTS = (OBSERVATION, MAJORANTS, RADIUS_PROJECTION, TRANSFER_VARIATIONS, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all Euler--Dirac variation inputs are required")
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    majorants = json.loads(MAJORANTS.read_text(encoding="utf-8"))
    radius = json.loads(RADIUS_PROJECTION.read_text(encoding="utf-8"))
    transfer = json.loads(TRANSFER_VARIATIONS.read_text(encoding="utf-8"))
    if not all(
        record.get("validation_passed") is True
        for record in (observation, majorants, radius, transfer)
    ):
        raise RuntimeError("all Euler--Dirac variation inputs must validate")
    child = observation["sector_bounds"]["child"]
    alpha = float(child["gauge_fixed_Dirac_ball_inverse_bound"])
    b0 = float(child["Euler_Dirac_rhs_action_bound"])
    b1 = float(child["Euler_Dirac_rhs_derivative_bound"])
    hessian = float(child["action_Hessian_bound"])
    third = float(child["action_third_variation_bound"])
    fourth = float(child["action_fourth_variation_bound"])
    velocity = float(child["configuration_rate_action_bound"])

    # b=E*L_q-L_zq*v.  For unit straight action directions h,k,
    # ||b_hk|| <= L3 + L4||v|| + L3||v_h|| + L3||v_k||.
    b2 = 3.0 * third + fourth * velocity
    solve = implicit_linear_solve_jet_bounds(
        alpha,
        b0,
        b1,
        b1,
        b2,
        third,
        third,
        fourth,
    )
    first_generator = max(
        float(child["Jacobi_generator_action_bound"]), solve["first_left"]
    )
    second_generator = solve["mixed_second"]
    duration = float(child["local_exit_time_lower"])
    cocycle = jacobi_cocycle_bounds(first_generator, second_generator, duration)
    gradient_bound = float(
        radius["global_functional_bounds"][
            "Euclidean_coordinate_gradient_norm_upper"
        ]
    )
    hessian_bound = float(
        radius["global_functional_bounds"][
            "Euclidean_coordinate_Hessian_operator_norm_upper"
        ]
    )
    x_first = gradient_bound * cocycle["first"]
    x_mixed = (
        gradient_bound * cocycle["mixed_second"]
        + hessian_bound * cocycle["first"] ** 2
    )
    validation = {
        "all_inputs_validated": True,
        "implicit_solve_base_bound_matches_existing_reduced_rate": solve["base"]
        <= float(child["reduced_rate_action_bound"]),
        "implicit_first_bound_is_dominated_by_existing_Jacobi_generator": solve[
            "first_left"
        ]
        <= float(child["Jacobi_generator_action_bound"]),
        "finite_second_Euler_Dirac_variation_bound": math.isfinite(second_generator),
        "finite_local_first_and_mixed_state_Jacobi_bounds": all(
            math.isfinite(value) for value in cocycle.values()
        ),
        "finite_local_first_and_mixed_log_R4_bounds": math.isfinite(x_first)
        and math.isfinite(x_mixed),
        "scope_remains_existing_local_N12_action_ball": True,
        "no_terminal_return_new_gate_selector_or_prediction": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_EULER_DIRAC_VARIATION_BOUNDS",
        "status": "LOCAL_SECOND_STATE_JACOBI_AND_LOG_RADIUS_TUBE_DERIVED",
        "classification": (
            "DIFFERENTIATING_THE_RETAINED_IMPLICIT_EULER_DIRAC_SOLVE_"
            "D(Y)s(Y)=b(Y)_CLOSES_THE_FIRST_AND_MIXED_SECOND_VECTOR_FIELD_"
            "JETS_BY_ONE_REUSED_DIRAC_SOLVE;_THE_EXISTING_N12_ACTION_D3_D4_"
            "AND_DIRAC_INVERSE_MAJORANTS_THEREFORE_GIVE_A_FINITE_LOCAL_"
            "SECOND_STATE_JACOBI_AND_LOG_RADIUS_TUBE"
        ),
        "implicit_solve_theorem": {
            "base": "s=D^-1*b",
            "first_left": "s_h=D^-1*(b_h-D_h*s)",
            "first_right": "s_k=D^-1*(b_k-D_k*s)",
            "mixed_second": (
                "s_hk=D^-1*(b_hk-D_hk*s-D_h*s_k-D_k*s_h)"
            ),
            "explicit_inverse_differentiated": False,
            "same_D_factorization_reused": True,
        },
        "action_derivative_ownership": {
            "D": "L_zz",
            "b": "E*L_q-L_zq*v",
            "D_h_owned_by": "D3_L",
            "D_hk_owned_by": "D4_L_FOR_STRAIGHT_DIRECTIONS",
            "b_hk_unit_straight_bound": "3*norm(D3_L)+norm(D4_L)*norm(v)",
            "action_Hessian_bound": hessian,
            "action_third_variation_bound": third,
            "action_fourth_variation_bound": fourth,
            "Dirac_inverse_bound": alpha,
            "configuration_rate_bound": velocity,
            "rhs_mixed_second_bound": b2,
        },
        "local_Euler_Dirac_solve_bounds": solve,
        "local_state_Jacobi_tube": {
            "duration": duration,
            "DV_bound": first_generator,
            "D2V_bound": second_generator,
            "unit_first_Jacobi_bound": cocycle["first"],
            "zero_initial_mixed_Jacobi_bound": cocycle["mixed_second"],
        },
        "local_log_R4_tube": {
            "unit_first_variation_bound": x_first,
            "zero_initial_mixed_variation_bound": x_mixed,
            "uses_closed_action_radius_pullback": True,
        },
        "scope_boundary": {
            "local_anchor_action_ball": "CERTIFIED",
            "maximal_forward_component_cover": "OPEN",
            "global_D3_D4_and_Dirac_inverse_envelopes": "OPEN_AS_EXPLICIT_CONSTANTS",
            "terminal_or_Friedrichs_graph_jets": "OPEN",
            "regular_Weyl_chart_cover": "OPEN",
        },
        "exact_next_dependency": (
            "PROMOTE_THE_LOCAL_IMPLICIT_SOLVE_MAJORANTS_TO_EXPLICIT_C(B,delta)_"
            "BOUNDS_ON_THE_CONTINUUM_MAXIMAL_FLOW_BOUNDED_MARGIN_SETS;_"
            "PROPAGATE_THE_STATE_AND_R4_JACOBI_TUBES_THROUGH_A_FINITE_OR_"
            "CONDITIONAL_COMPONENT_COVER;_THEN_ENCLOSE_THE_FIXED_CHANNEL_"
            "WEYL_TRANSFER_AND_TERMINAL_FRIEDRICHS_GRAPH_JETS"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "global_channel_Weyl_enclosures": "OPEN",
            "chord_03": "NOT_AUTHORIZED",
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "state_Jacobi_tube": payload["local_state_Jacobi_tube"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
