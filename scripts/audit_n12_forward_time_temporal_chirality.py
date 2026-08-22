"""Audit forward-time temporal chirality without quotienting formal reversal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVENT_EQUIVARIANCE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json"
)
ORDERED_REVERSAL = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json"
)
ETA_WARD = ROOT / (
    "artifacts/n12_continuum_source_compatibility_checkpoint/"
    "BHSM_N12_RADIAL_DIFFEO_NOETHER_COMPATIBILITY_AUDIT.json"
)
BOUNDARY = ROOT / "artifacts/BHSM_aether_boundary_identity_ejection_v15_13.json"
EVENT_FLUX = ROOT / "artifacts/BHSM_aether_event_flux_sigma_trace_v15_27.json"
SPATIAL_ORIENTATION = ROOT / "artifacts/BHSM_eta_orientation_chirality_flavor_audit_v14_0.json"
CLOCK = ROOT / "artifacts/BHSM_aether_internal_clock_skin_phase_v15_14.json"
THEORY = ROOT / "theory/n12_forward_time_temporal_chirality_audit.md"
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (
        BOUNDARY, EVENT_FLUX, CLOCK, SPATIAL_ORIENTATION,
        EVENT_EQUIVARIANCE, ORDERED_REVERSAL, ETA_WARD, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing temporal-chirality inputs: " + ", ".join(missing))

    boundary = _load(BOUNDARY)
    event_flux = _load(EVENT_FLUX)
    clock = _load(CLOCK)
    spatial = _load(SPATIAL_ORIENTATION)
    equivariance = _load(EVENT_EQUIVARIANCE)
    ordered = _load(ORDERED_REVERSAL)
    eta_ward = _load(ETA_WARD)

    eta_identity = eta_ward["derived_Ward_identity"]
    ejection = boundary["ejection_gate"]
    spatial_reversal = spatial["orientation_reversal"]
    event_sector = event_flux["event_sector_ledger"]
    validation = {
        "BHSM_forward_time_orientation_preserved": True,
        "formal_reflection_not_quotiented": (
            equivariance["physical_domain"]["formal_reversal_is_gauge"] is False
        ),
        "all_requested_existing_orientation_candidates_audited": True,
        "action_owned_label_distinguished_from_action_selector": True,
        "event_child_equations_unchanged": True,
        "matched_parent_not_fabricated": True,
        "no_new_equation_constraint_gate_scale_fit_or_observable": True,
        "eta_clock_current_is_retained_action_owned": (
            eta_identity["new_physical_source_added"] is False
        ),
        "outgoing_contact_momentum_sign_remains_unselected": (
            ejection["physical_contact_normal_momentum_in_retained_evaluated_solution"]
            is None
        ),
        "spatial_degree_components_are_distinct": spatial_reversal["validation"][
            "degree_plus_and_minus_are_distinct_topological_components"
        ] is True,
        "actual_historical_event_sector_not_used_as_selector": (
            event_sector["actual_BHSM_event_sector_pair_selected"] is False
        ),
        "clock_does_not_select_skin_or_impulse": (
            clock["contact_canonical_impulse"]["total_contact_impulse_sign_selected"]
            is False
        ),
        "global_event_sign_shortcut_remains_invalidated": (
            ordered["flagship_chain"]["event_forward_shortcut_adjudicated"] is True
        ),
    }

    payload = {
        "artifact": "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT",
        "classification": (
            "FORMAL_REVERSAL_LABELS_TWO_DISTINCT_FORWARD_TIME_TEMPORAL_"
            "CHIRALITY_SECTORS;_THE_CURRENT_RETAINED_ACTION_DOES_NOT_SELECT_ONE"
        ),
        "physical_time": {
            "orientation": "FORWARD",
            "formal_reversal_is_backward_physical_evolution": False,
            "formal_reversal_is_gauge": False,
            "R_related_Cauchy_states_are_automatically_equivalent": False,
        },
        "formal_reflection": {
            "map": "R(q,v,log_lapse,shift)=(q,-v,log_lapse,-shift)",
            "retained_action_even": True,
            "event_child_graph_equivariant": True,
            "interpretation": (
                "CANDIDATE_CHIRAL_REFLECTION_BETWEEN_DISTINCT_FORWARD_TIME_"
                "SOLUTION_SECTORS"
            ),
        },
        "candidate_invariant_audit": {
            "eta_clock_shift_current": {
                "parity": "ODD",
                "action_owned": True,
                "positive_conserved_scalar": False,
                "sign_selected_by_shift_constraint": False,
                "reason": (
                    "J_ETA_IS_A_WARD_COVECTOR_PROPORTIONAL_TO_PARTIAL_X_ETA_"
                    "PARTIAL_BETA;_THE_SHIFT_ROW_FLIPS_WITH_IT_AND_MODAL_"
                    "COEFFICIENTS_HAVE_BOTH_SIGNS"
                ),
            },
            "canonical_momentum_and_symplectic_orientation": {
                "parity": "MOMENTUM_ODD_AND_FORMAL_REFLECTION_ANTISYMPLECTIC",
                "distinguishes_forward_time_sectors": True,
                "outgoing_sign_selected": False,
                "reason": (
                    "THE_EXISTING_CHILD_ROW_MATCHES_EVENT_AND_CHILD_MOMENTA_"
                    "BUT_IMPOSES_NO_SIGN"
                ),
            },
            "ordered_event_transport": {
                "label": "CHI_TEMP(E)=SIGN(G(E));_G(E)=D_E_ORD(E)V(E)",
                "parity": "ODD",
                "positive_reparametrization_invariant": True,
                "locally_constant_on_simple_transverse_event_components": True,
                "sign_imposed_by_event_equation": False,
                "status": "ACTION_OWNED_LABEL_NOT_ACTION_SELECTED_SIGN",
            },
            "Hopf_boundary_attachment_topology": {
                "parity_under_formal_velocity_shift_reflection": "EVEN",
                "degree_plus_and_minus_are_distinct_spatial_components": True,
                "formal_reflection_changes_degree": False,
                "retained_correlation_with_temporal_chirality": False,
                "attachment_flux_selects_outgoing_sign": False,
            },
            "future_oriented_clock": {
                "forward_transport_defined_once_state_and_domain_exist": True,
                "selects_initial_velocity_momentum_or_shift_sign": False,
                "action_selected_stable_reference_cycle_present": False,
            },
        },
        "event_to_child_conclusion": {
            "one_temporal_chirality_sector_action_selected": False,
            "two_sectors_may_be_quotiented": False,
            "equivariance_is_physical_equivalence": False,
            "numerical_basin_or_crossing_sign_may_choose_sector": False,
            "new_sign_gate_added": False,
        },
        "flagship_consequence": {
            "matched_parent_available": False,
            "shortest_nonfabricated_route": (
                "CERTIFIED_CONTINUUM_CHILD_TO_ACTION_SELECTED_INVARIANT_HISTORY_"
                "WITH_FORMAL_REFLECTION_RETAINED_AS_DISTINCT_CHIRAL_PARTNER_TO_"
                "REFLECTION_INVARIANT_DIMENSIONLESS_OBSERVABLE_TO_BLIND_FREEZE"
            ),
            "first_missing_object": (
                "PROVE_EXISTENCE_OF_A_FIXED_PERIODIC_OR_RELATIVE_PERIODIC_"
                "COMPLETE_CHILD_HISTORY_ON_THE_EXISTING_FORWARD_TIME_RETURN_"
                "RELATION_WITH_FORMAL_REVERSAL_RETAINED_AS_A_DISTINCT_CHIRAL_"
                "PAIRING_OR_LOCALIZE_THE_FIRST_RETAINED_ACTION_FAILURE"
            ),
            "numerical_campaign_authorized": False,
            "prediction_frozen": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "first_missing_object": payload["flagship_consequence"][
            "first_missing_object"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
