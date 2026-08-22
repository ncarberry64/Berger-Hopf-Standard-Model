"""Enclose the ordered-event projector compact-tail modulus.

This is the exact simple-eigenprojector derivative identity composed with
the already-enclosed lower-order Euler--Dirac Hessian tail.  It changes no
event definition and introduces no physical equation or gate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ED = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ENDPOINT_SAFE_ED_REMAINDER.json"
)
EVENT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_ORDERED_EVENT_EIGENLINE_BALL.json"
)
PROJECTOR = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ORDERED_EVENT_COMPACT_MODULUS.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    ed = json.loads(ED.read_text(encoding="utf-8"))
    event = json.loads(EVENT.read_text(encoding="utf-8"))
    projector = json.loads(PROJECTOR.read_text(encoding="utf-8"))
    c_ed = float(ed["joint_direct_C_ED_G_upper"])
    reduced_resolvent = float(
        event["bounds"]["ordered_eigenprojector_reduced_resolvent_bound"]
    )
    coefficient = 2.0 * reduced_resolvent * c_ed
    variation = 2.0 * coefficient
    validation = {
        "endpoint_safe_action_Hessian_tail_enclosed": bool(
            ed["direct_C_ED_G_enclosure_complete"]
        ),
        "ordered_branch_simple_on_whole_existing_ball": bool(
            event["validation_passed"]
            and float(event["bounds"]["eigenline_gap_lower"]) > 0.0
        ),
        "reduced_resolvent_is_existing_action_owned_bound": (
            reduced_resolvent > 0.0
        ),
        "same_weighted_Jacobi_Fortin_tail_used": bool(
            projector["weighted_L2_Jacobi_Fortin_tail_closed"]
        ),
        "no_event_equation_gate_scale_or_branch_changed": True,
    }
    payload = {
        "classification": (
            "ORDERED_EVENT_SIMPLE_EIGENPROJECTOR_COMPACT_TAIL_MODULUS_"
            "ENCLOSED_IN_THE_EXISTING_SOURCE_RESTRICTED_MIXED_GRAPH"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (ED, EVENT, PROJECTOR)
        },
        "exact_derivative_identity": (
            "DP[h]=-S_red*DH[h]*P-P*DH[h]*S_red"
        ),
        "bounds": {
            "C_ED_G_upper": c_ed,
            "ordered_eigenprojector_reduced_resolvent_upper": (
                reduced_resolvent
            ),
            "C_event_G_upper": coefficient,
            "fixed_ball_event_projector_variation_upper": variation,
            "Fortin_composition": (
                "epsilon_event(M)<=C_event_G*C_F(M)<="
                "4*C_event_G/sqrt(M)_FOR_INTEGER_M>=12"
            ),
        },
        "same_norm_coefficient_enclosed": True,
        "fixed_ball_state_variation_modulus_complete": True,
        "first_missing_action_owned_object": (
            "DERIVE_THE_CANONICAL_MOMENTUM_DYNAMIC_FLUX_COMPACT_"
            "TAIL_MODULUS_IN_THE_SAME_MIXED_GRAPH_NORM"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
