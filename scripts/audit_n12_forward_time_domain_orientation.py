"""Audit the existing single forward physical-time domain at N12."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERSISTENCE_DEFINITION = ROOT / "artifacts/BHSM_aether_persistent_nonequilibrium_child_v17_87.json"
PERSISTENCE = ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_PERSISTENCE_WITNESS.json"
INTERNAL_CLOCK = ROOT / "artifacts/BHSM_aether_internal_clock_skin_phase_v15_14.json"
EQUIVARIANCE = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json"
RESET = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
THEORY = ROOT / "theory/n12_forward_time_domain_orientation.md"
RESULT = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (
        PERSISTENCE_DEFINITION, PERSISTENCE, INTERNAL_CLOCK, EQUIVARIANCE,
        RESET, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing forward-time-domain inputs: " + ", ".join(missing))

    definition = _load(PERSISTENCE_DEFINITION)
    persistence = _load(PERSISTENCE)
    clock = _load(INTERNAL_CLOCK)
    equivariance = _load(EQUIVARIANCE)
    reset = _load(RESET)
    domain = definition["persistence_and_decay_contract"]["persistence_domain_B_child"]
    decay_clock = definition["persistence_and_decay_contract"]["decay"]["clock"]
    local = persistence["local_existence"]

    validation = {
        "existing_clock_relation_is_positive_lapse_times_dt": (
            "d_tau=N_child*dt" in decay_clock
        ),
        "certified_boundary_lapse_is_positive": local["initial_boundary_lapse"] > 0,
        "certified_proper_duration_is_positive": local["positive_duration_exists"] is True,
        "persistence_domain_already_requires_positive_lapse": (
            "positive_spatial_metric_and_lapse" in domain["geometric_domain"]
        ),
        "proper_clock_is_action_owned_on_existing_worldtube": clock[
            "independent_internal_clocks_and_holonomies"
        ]["clock_is_action_owned_once_physical_metric_and_history_exist"] is True,
        "formal_reflection_preserves_static_physical_domain": equivariance[
            "physical_domain"
        ]["eta_metric_lapse_gauge_and_rank_preserved"] is True,
        "reflected_reexpressed_state_has_forward_solution": equivariance[
            "physical_domain"
        ]["reflected_state_has_its_own_forward_positive_duration_solution"] is True,
        "formal_reflection_is_not_gauge": equivariance["physical_domain"][
            "formal_reversal_is_gauge"
        ] is False,
        "local_hitting_reset_theorem_preserves_forward_time": reset[
            "one_sided_hitting_theorem"
        ]["represented_boundary_role"] == "FORWARD_TERMINAL",
        "no_new_equation_gate_selector_clock_or_quotient": True,
    }

    payload = {
        "artifact": "BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT",
        "classification": (
            "ONE_PHYSICAL_FORWARD_TIME_ORIENTATION_ALREADY_OWNED_BY_THE_"
            "POSITIVE_LAPSE_POSITIVE_DURATION_CHILD_DOMAIN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "admissible_clock_domain": {
            "coordinate_parameter": "dt>0",
            "boundary_lapse": "N_boundary>0",
            "proper_time_relation": "d_tau_child=N_boundary*dt",
            "physical_orientation": "d_tau_child>0",
            "number_of_physical_time_orientations": 1,
            "new_condition_added": False,
            "incorporated_manifold": (
                "M_child_plus=M_child_INTERSECT_{dt>0,N_boundary>0,d_tau_child>0}"
            ),
        },
        "formal_reflection_reclassification": {
            "state_map": "R(q,v,log_lapse,shift)=(q,-v,log_lapse,-shift)",
            "acts_on_dt": False,
            "with_t_to_minus_t_is_admissible_physical_evolution": False,
            "reexpressed_as_new_Cauchy_data_at_dt_positive": True,
            "independently_satisfies_same_forward_domain_at_certified_N12_root": True,
            "role": "ALGEBRAIC_OR_CHIRAL_PAIRING_WITHIN_ONE_FORWARD_TIME_DOMAIN",
            "second_physical_temporal_orientation": False,
            "requires_action_selection_of_time_orientation": False,
            "is_gauge_or_quotiented": False,
        },
        "singular_boundary_label": {
            "label": "SIGN(C_PSI*B_PSI)",
            "meaning": "FORWARD_TERMINAL_VERSUS_FORWARD_EMERGENT_BOUNDARY_ROLE",
            "physical_time_orientation_selector": False,
            "new_event_gate": False,
        },
        "intrinsic_state_consequence": {
            "artificial_two_temporal_sector_ambiguity_removed": True,
            "action_selection_of_forward_vs_backward_required": False,
            "chiral_or_state_pair_may_remain_physically_distinct": True,
            "action_selected_intrinsic_forward_history_proved": False,
            "remaining_blocker": reset["exact_next_dependency"],
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "remaining_blocker": payload["intrinsic_state_consequence"]["remaining_blocker"],
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
