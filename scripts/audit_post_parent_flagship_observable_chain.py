"""Reassess the shortest flagship observable chain after the parent no-go.

This is a provenance audit only.  It reads retained artifacts and refuses to
promote a mathematical certificate, conditional charge, or internal scale
ratio into a held-out physical prediction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
PARENT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_STATIONARY_SECTION_GATE.json"
)
ABSOLUTE_UNIT = ROOT / "artifacts/BHSM_absolute_unit_propagation_v5_8.json"
CHARGE = ROOT / "artifacts/BHSM_action_selected_charge_current_shape_schur_gate_v14_88.json"
CLOCK = ROOT / "artifacts/BHSM_aether_joint_hamiltonian_selection_v15_2.json"
FLAVOR = ROOT / "artifacts/BHSM_action_selected_8d_vacuum_flavor_completion_v9_0.json"
TRANSPORT = ROOT / "artifacts/BHSM_common_scheme_observable_transport_v7_2.json"
RESULT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_POST_PARENT_FLAGSHIP_OBSERVABLE_GATE.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    inputs = (CONTINUUM, PARENT, ABSOLUTE_UNIT, CHARGE, CLOCK, FLAVOR, TRANSPORT)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing flagship-observable inputs: " + ", ".join(missing))

    continuum = json.loads(CONTINUUM.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    absolute_unit = json.loads(ABSOLUTE_UNIT.read_text(encoding="utf-8"))
    charge = json.loads(CHARGE.read_text(encoding="utf-8"))
    clock = json.loads(CLOCK.read_text(encoding="utf-8"))
    flavor = json.loads(FLAVOR.read_text(encoding="utf-8"))
    transport = json.loads(TRANSPORT.read_text(encoding="utf-8"))

    ratios = absolute_unit["unit_anchor"]["preserved_relative_ratios"]
    validation = {
        "continuum_child_is_available": continuum["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True,
        "matched_parent_is_not_executable": parent["R_P_executable"] is False,
        "Q_xi_and_Delta_H_are_not_evaluated": (
            parent["Q_xi_evaluated"] is False and parent["Delta_H_evaluated"] is False
        ),
        "absolute_anchor_is_not_generated": (
            absolute_unit["primary_result"] == "BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED"
        ),
        "nonzero_charge_is_not_action_selected": (
            charge["FR_status"]["nonzero_physical_charge"] == "NOT_ACTION_SELECTED"
        ),
        "reference_cycle_is_not_action_selected": (
            clock["clock"]["action_selected_stable_core_cycle"] is False
        ),
        "physical_flavor_matrix_is_not_promoted": flavor["physical_matrix_promoted"] is False,
        "distinct_falsifiable_prediction_remains_absent": (
            transport["remaining_exact_obstruction"]
            == "ABSENCE_OF_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PREDICTION"
        ),
        "no_prediction_frozen_or_compared": True,
    }
    payload = {
        "artifact": "BHSM_POST_PARENT_FLAGSHIP_OBSERVABLE_GATE",
        "classification": (
            "NO_CURRENT_ACTION_OWNED_BLIND_PHYSICAL_OBSERVABLE_EXECUTABLE_"
            "AFTER_MATCHED_PARENT_NO_GO"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "owned_starting_point": {
            "continuum_event_child_certified": True,
            "role": "resolution-independent mathematical child construction",
            "is_by_itself_a_held_out_physical_prediction": False,
        },
        "candidate_chain_audit": [
            {
                "candidate": "matched_parent_Q_xi_and_Delta_H",
                "status": "NOT_EXECUTABLE",
                "first_blocker": parent["first_missing_action_owned_datum"],
                "parent_substitution_or_manual_zero_allowed": False,
            },
            {
                "candidate": "internal_absolute_unit_ratios",
                "status": "DERIVED_INTERNAL_RATIOS_NOT_EXTERNAL_OBSERVABLE",
                "values": ratios,
                "first_blocker": "ABSOLUTE_UNIT_ANCHOR_AND_PARTICLE_OBSERVABLE_MAP_ABSENT",
            },
            {
                "candidate": "intrinsic_nonzero_charge_or_current",
                "status": "NOT_ACTION_SELECTED",
                "first_blocker": "ACTION_SELECTED_NONZERO_PHYSICAL_STATE_AND_COMMON_DOMAIN_ABSENT",
            },
            {
                "candidate": "clocked_or_Floquet_energy",
                "status": "NOT_ACTION_SELECTED",
                "first_blocker": "ACTION_SELECTED_STABLE_REFERENCE_CYCLE_AND_PHYSICAL_CLOCK_ABSENT",
            },
            {
                "candidate": "flavor_or_mixing_observable",
                "status": "NOT_ACTION_SELECTED",
                "first_blocker": flavor["next_missing_object"],
            },
        ],
        "shortest_nonfabricated_flagship_route": {
            "route": (
                "CERTIFIED_CONTINUUM_CHILD_TO_ACTION_SELECTED_INTRINSIC_CHILD_STATE_"
                "AND_OBSERVABLE_MAP_TO_DIMENSIONLESS_BLIND_PREDICTION"
            ),
            "first_missing_object": (
                "ACTION_SELECTED_INTRINSIC_PHYSICAL_STATE_AND_OBSERVABLE_MAP_ON_"
                "THE_CERTIFIED_CONTINUUM_CHILD"
            ),
            "why_this_precedes_numerical_evaluation": (
                "all presently located child-only numbers are either mathematical "
                "certificate data, internal scale ratios without an external map, "
                "or values conditional on an unselected state, charge, cycle, or domain"
            ),
            "matched_parent_route_may_resume_only_if_action_owned": True,
        },
        "prediction_frozen": False,
        "held_out_comparison_performed": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": True,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "first_missing_object": payload["shortest_nonfabricated_flagship_route"]
        ["first_missing_object"],
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
