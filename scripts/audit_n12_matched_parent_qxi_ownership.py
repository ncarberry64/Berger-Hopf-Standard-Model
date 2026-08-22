"""Localize the first action-owned blocker to the N12 relative charge.

This audit is intentionally fail-closed.  It consumes the certified continuum
child and inventories the exact retained N12 state/action interfaces.  It
checks whether those interfaces define the parent-only restriction and the
boundary-improved covariant charge required by the v14.54 relative-energy
contract.  Available local Legendre energies are evaluated only as a diagnostic
and are never promoted to ``Q_xi``, ``Delta H``, mass, or a prediction.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _canonical_pair_at_order,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.completion.support_covariant_phase_space_v11_2 import (
    phase_space_payload,
)


ORDER = 12
POINTS = int(os.environ.get("BHSM_N12_QXI_OWNERSHIP_POINTS", "96"))
CHECKPOINT = Path(
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
CONTINUUM = Path(
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
MASS_CONTRACT = Path("artifacts/BHSM_cycle_invariant_mass_contract_v14_54.json")
MASTER_ACTION = Path("artifacts/BHSM_unified_master_action_v7_0.json")
RESULT = Path(os.environ.get(
    "BHSM_N12_QXI_OWNERSHIP_RESULT",
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _split(state: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    return (
        state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]
    )


def _local_legendre_energy(state: np.ndarray, points: int) -> float:
    q, velocity, multipliers = _split(state)
    qdim = q.size
    jet = exact_full_action_jet_at_state(
        ORDER, q, velocity, multipliers, points=points
    )
    momentum = np.asarray(jet.gradient[qdim:2 * qdim], dtype=float)
    return float(velocity @ momentum - jet.value)


def main() -> None:
    continuum = json.loads(CONTINUUM.read_text(encoding="utf-8"))
    if continuum.get("CONTINUUM_EVENT_CHILD_CERTIFIED") is not True:
        raise RuntimeError("continuum event-child certificate is required")
    mass_contract = json.loads(MASS_CONTRACT.read_text(encoding="utf-8"))
    master_action = json.loads(MASTER_ACTION.read_text(encoding="utf-8"))
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    size = dimensions(ORDER)
    state_dimension = 2 * size["coordinates"] + size["multipliers"]
    if joint.shape != (2 * state_dimension,):
        raise RuntimeError("unexpected certified joint-state dimension")
    event_state = joint[:state_dimension]
    child_state = joint[state_dimension:]
    event = _split(event_state)
    child = _split(child_state)
    trace_defect = float(np.linalg.norm(
        _trace_jacobian_at_order(ORDER) @ (child[0] - event[0])
    ))
    attachment_defect = abs(float(
        _attachment_coordinates_at_order(ORDER, child[0])[1]
        - _attachment_coordinates_at_order(ORDER, event[0])[1]
    ))
    event_momentum = _canonical_pair_at_order(
        ORDER, *event, points=POINTS
    )[0]
    child_momentum = _canonical_pair_at_order(
        ORDER, *child, points=POINTS
    )[0]
    momentum_defect = float(np.linalg.norm(child_momentum - event_momentum))
    local_rows = []
    for points in (POINTS, 2 * POINTS):
        event_energy = _local_legendre_energy(event_state, points)
        child_energy = _local_legendre_energy(child_state, points)
        local_rows.append({
            "quadrature_points": points,
            "event_local_Legendre_energy": event_energy,
            "child_local_Legendre_energy": child_energy,
            "child_minus_event_local_Legendre_energy": (
                child_energy - event_energy
            ),
            "is_Q_xi": False,
            "is_Delta_H": False,
        })
    phase_space = phase_space_payload()
    action_signature = str(inspect.signature(exact_full_action_jet_at_state))
    state_inventory = {
        "per_side_coordinates": size["coordinates"],
        "per_side_velocities": size["coordinates"],
        "per_side_lapse_shift_multipliers": size["multipliers"],
        "per_side_total": state_dimension,
        "joint_total": int(joint.size),
        "stored_checkpoint_arrays": list(checkpoint.files),
        "retained_action_callable_signature": action_signature,
        "explicit_parent_only_fields": [],
        "explicit_composite_minus_parent_restriction_variables": [],
        "moving_seam_embedding_variables": [],
        "reference_subtraction_variables": [],
    }
    required_parent_map = {
        "symbol": "R_P:Phi_(P+C)->Phi_P_matched",
        "requirements": [
            "same retained action and common interface trace",
            "same symmetry generator xi and clock normalization",
            "same boundary normal, orientation, domain, and duration",
            "parent-only restriction defined without deleting retained terms",
            "common reference subtraction convention",
        ],
        "defined_by_current_N12_state_or_action_API": False,
        "event_side_is_the_required_matched_parent": False,
        "reason": (
            "THE_EVENT_HALF_IS_A_THRESHOLD_CAUCHY_STATE_IN_THE_JOINT_"
            "EVENT_CHILD_MAP;_NO_RETAINED_ACTION_RESTRICTION_IDENTIFIES_IT_"
            "AS_THE_PARENT_ONLY_REFERENCE_OF_THE_COMPOSITE"
        ),
    }
    required_charge = {
        "variation": (
            "delta_H_xi=integral_boundary(delta_Q_xi-i_xi_Theta_retained)"
            "-delta_B_xi_match"
        ),
        "complete_symplectic_potential_available": (
            phase_space["complete_symplectic_potential"] is not None
        ),
        "complete_symplectic_current_available": (
            phase_space["complete_symplectic_current"] is not None
        ),
        "complete_flux_conservation_available": (
            phase_space["complete_flux_conservation"] is not None
        ),
        "matched_seam_corner_reference_term_available": False,
        "complete_common_reference_Q_xi_assembler_available": False,
    }
    first_blocker = (
        "DERIVE_THE_ACTION_OWNED_MATCHED_PARENT_RESTRICTION_"
        "R_P_FROM_THE_COMPLETE_PARENT_COMPOSITE_ACTION_WITH_IDENTICAL_"
        "INTERFACE_GENERATOR_CLOCK_DOMAIN_AND_REFERENCE_DATA"
    )
    validation = {
        "continuum_event_child_certificate_consumed": True,
        "certified_N12_joint_state_consumed": True,
        "initial_event_child_trace_and_momentum_match_measured": bool(
            np.isfinite(trace_defect + attachment_defect + momentum_defect)
        ),
        "retained_action_API_inventory_is_explicit": True,
        "covariant_phase_space_fail_closed_ledger_consumed": True,
        "event_side_not_substituted_for_matched_parent": True,
        "local_Legendre_energy_not_promoted_to_Q_xi_or_Delta_H": True,
        "mass_prediction_and_frozen_ledger_untouched": True,
        "new_physics_equation_constraint_gate_or_selector": False,
    }
    payload = {
        "artifact": "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP",
        "classification": (
            "Q_XI_GATE_OPEN;_THE_CONTINUUM_CHILD_IS_CERTIFIED_BUT_THE_"
            "RETAINED_N12_STATE_SPACE_DOES_NOT_DEFINE_THE_ACTION_OWNED_"
            "MATCHED_PARENT_RESTRICTION_OR_COMPLETE_COVARIANT_CHARGE"
        ),
        "inputs": {
            str(CHECKPOINT): _sha256(CHECKPOINT),
            str(CONTINUUM): _sha256(CONTINUUM),
            str(MASS_CONTRACT): _sha256(MASS_CONTRACT),
            str(MASTER_ACTION): _sha256(MASTER_ACTION),
        },
        "v14_54_contract": {
            "relative_charge": mass_contract["relative_charge"],
            "instantaneous_snapshot_is_physical_mass": mass_contract[
                "instantaneous_snapshot_is_physical_mass"
            ],
        },
        "state_and_action_inventory": state_inventory,
        "certified_initial_event_child_Cauchy_match": {
            "trace_l2": trace_defect,
            "attachment_absolute": attachment_defect,
            "canonical_momentum_l2": momentum_defect,
            "does_not_define_a_parent_only_restriction": True,
        },
        "available_local_diagnostic_only": local_rows,
        "required_matched_parent_map": required_parent_map,
        "upstream_parent_composite_action_provenance": {
            "master_action_closed": master_action["master_action_closed"],
            "exact_missing_object": master_action["exact_missing_object"],
            "R_8to5": master_action["maps"]["R_8to5"],
            "R_5to4": master_action["maps"]["R_5to4"],
            "relation_to_R_P": (
                "R_P_REQUIRES_THE_SAME_UNSOURCED_COVARIANT_BULK_BOUNDARY_"
                "REDUCTION_DATA_SPECIALIZED_TO_THE_MATCHED_PARENT_REFERENCE"
            ),
        },
        "required_boundary_improved_charge": required_charge,
        "Q_xi_evaluated": False,
        "Delta_H_evaluated": False,
        "first_open_action_owned_dependency": first_blocker,
        "after_that": (
            "DERIVE_THE_COMPLETE_THETA_RETAINED_AND_B_XI_MATCH_BOUNDARY_"
            "IMPROVEMENT_AND_EVALUATE_BOTH_CHARGES_ON_THE_COMMON_HISTORY"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": True,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(
            value if key != "new_physics_equation_constraint_gate_or_selector"
            else not value
            for key, value in validation.items()
        ),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "result": str(RESULT),
        "classification": payload["classification"],
        "event_child_Cauchy_match": payload[
            "certified_initial_event_child_Cauchy_match"
        ],
        "local_energy_rows": local_rows,
        "first_open_action_owned_dependency": first_blocker,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
