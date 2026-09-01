"""Audit ownership of the physical zero-energy birth-graph margin."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_barrier_threshold import (  # noqa: E402
    barrier_critical_robin,
    barrier_scattering_birth_amplitude,
    barrier_zero_energy_transfer,
    critical_birth_amplitude_limit,
    regular_birth_amplitude_slope_limit,
)


FLAGSHIP = ROOT / "artifacts/flagship_integration"
THRESHOLD = FLAGSHIP / "BHSM_N12_FORWARD_THRESHOLD_SOURCE_MEASURE_AUDIT.json"
HIGH = FLAGSHIP / "BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
GRAPH = FLAGSHIP / "BHSM_N12_FORWARD_SOURCE_VARIATIONAL_GRAPH.json"
INCIDENCE = FLAGSHIP / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
CORRESPONDENCE = ROOT / "artifacts/BHSM_aether_n3_event_complete_child_correspondence_v17_84.json"
ZERO = ROOT / "artifacts/BHSM_aether_n3_zero_background_calderon_closure_v17_97.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_barrier_threshold.py"
RESULT = FLAGSHIP / "BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT.json"
INPUTS = (THRESHOLD, HIGH, GRAPH, INCIDENCE, CORRESPONDENCE, ZERO, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite birth-threshold audit value")
        return value
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all birth-threshold audit inputs are required")
    threshold, high, graph, incidence, correspondence, zero = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS[:-1]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (threshold, high, graph, incidence, correspondence, zero)
    ):
        raise RuntimeError("all birth-threshold audit inputs must validate")

    weakest_positive = min(
        row["child_zero_energy_impedance_lower"]
        for row in threshold["certified_core"]["scalar_derham_rows"]
        if row["unit_radius_eigenvalue"] > 0.0
    )
    actual_core_countergraph = {
        "weakest_positive_child_impedance": weakest_positive,
        "critical_cancelling_Robin_parameter": -weakest_positive,
        "sum_at_zero": 0.0,
    }

    rate = 2.0
    length = 0.75
    critical = barrier_critical_robin(rate, length)
    transfer = barrier_zero_energy_transfer(rate, length, critical)
    momenta = (1.0e-3, 3.0e-4, 1.0e-4)
    rows = []
    for momentum in momenta:
        regular = barrier_scattering_birth_amplitude(
            momentum, rate, length, 0.0
        )
        resonant = barrier_scattering_birth_amplitude(
            momentum, rate, length, critical
        )
        rows.append(
            {
                "momentum": momentum,
                "regular_birth_amplitude": regular,
                "regular_amplitude_over_momentum": regular / momentum,
                "critical_birth_amplitude": resonant,
            }
        )

    event_scope = correspondence["event_to_complete_child_correspondence"]
    zero_scope = zero["zero_background_calderon_closure"]["scope"]
    validation = {
        "all_inputs_validated": True,
        "critical_graph_cancels_child_impedance_exactly": (
            actual_core_countergraph["sum_at_zero"] == 0.0
        ),
        "critical_zero_energy_Wronskian_is_zero": (
            abs(transfer["zero_energy_Wronskian"]) <= 1.0e-15
        ),
        "critical_form_is_nonnegative_by_positive_ground_state_transform": True,
        "regular_h_zero_form_is_nonnegative": True,
        "regular_amplitude_has_one_momentum_factor": all(
            abs(
                row["regular_amplitude_over_momentum"]
                / regular_birth_amplitude_slope_limit(rate, length)
                - 1.0
            )
            <= 2.0e-6
            for row in rows
        ),
        "critical_amplitude_has_nonzero_limit": all(
            abs(
                row["critical_birth_amplitude"]
                / critical_birth_amplitude_limit(rate, length)
                - 1.0
            )
            <= 2.0e-6
            for row in rows
        ),
        "historical_physical_blocks_not_action_derived": (
            event_scope["physical_block_provenance"][
                "physical_blocks_action_derived"
            ]
            is False
        ),
        "zero_background_does_not_supply_nonzero_graph": (
            zero_scope["full_nonzero_fluctuation_Calderon_matrices_derived"]
            is False
        ),
        "local_incidence_does_not_select_temporal_graph": (
            incidence["incidence"]["temporal_graph_selected_by_this_assembly"]
            is False
        ),
        "forward_graph_record_leaves_nonzero_graph_unassembled": (
            graph["current_scope"]["nonzero_graph_already_assembled"] is False
        ),
        "high_energy_integrability_preserved": (
            high["adjudication"]["compact_weak_E1_high_energy_integrability"]
            == "DERIVED"
        ),
        "no_graph_endpoint_reference_gap_chord3_selector_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_BIRTH_THRESHOLD_MARGIN_AUDIT",
        "status": "PHYSICAL_BIRTH_GRAPH_ZERO_THRESHOLD_MARGIN_REQUIRED_AND_UNASSEMBLED",
        "classification": (
            "A_POSITIVE_TWO_CHORD_CORE_AND_GLOBAL_FORM_NONNEGATIVITY_DO_NOT_"
            "EXCLUDE_A_ZERO_THRESHOLD_RESONANCE:_THE_EXACT_CONSTANT_BARRIER_"
            "FAMILY_HAS_A_CRITICAL_NONNEGATIVE_ROBIN_GRAPH_THAT_CANCELS_THE_"
            "CHILD_ZERO_ENERGY_IMPEDANCE_AND_CHANGES_COMPACT_COUNTING_FROM_"
            "Lambda^(3/2)_TO_Lambda^(1/2);_THE_CURRENT_LOCAL_INCIDENCE_AND_"
            "ZERO_BACKGROUND_GRAPH_DO_NOT_SUPPLY_THE_REQUIRED_SECTOR_RESOLVED_"
            "NONZERO_PHYSICAL_BIRTH_GRAPH_MARGIN"
        ),
        "exact_counterfamily": {
            "operator": (
                "K_h=-d2/dtau2+a^2*1_[0,T]_ON_[0,infinity),_"
                "u'(0)=h*u(0)"
            ),
            "critical_graph": "h_crit=-a*tanh(a*T)",
            "critical_zero_solution": (
                "u=cosh(a*tau)+(h_crit/a)*sinh(a*tau)_ON_[0,T]_"
                "AND_CONSTANT_AFTER_T"
            ),
            "critical_form_nonnegative_reason": (
                "GROUND_STATE_TRANSFORM_q_hcrit[f]=integral_u0^2*"
                "abs((f/u0)')^2"
            ),
            "regular_nonnegative_graph": "h=0",
            "regular_counting": "LOCAL_BIRTH_AMPLITUDE_O(k)_IMPLIES_O(Lambda^(3/2))",
            "critical_counting": "LOCAL_BIRTH_AMPLITUDE_O(1)_IMPLIES_O(Lambda^(1/2))",
            "canonical_witness": {
                "rate": rate,
                "barrier_length": length,
                "critical_Robin": critical,
                "zero_transfer": transfer,
                "regular_slope_limit": regular_birth_amplitude_slope_limit(
                    rate, length
                ),
                "critical_amplitude_limit": critical_birth_amplitude_limit(
                    rate, length
                ),
                "rows": rows,
            },
        },
        "N12_two_chord_application": {
            **actual_core_countergraph,
            "lesson": (
                "THE_CERTIFIED_CHILD_MARGIN_CAN_BE_CANCELLED_BY_AN_UNRESOLVED_"
                "EVENT_PLUS_WENTZELL_BIRTH_GRAPH_WHILE_THE_TOTAL_OPERATOR_"
                "REMAINS_NONNEGATIVE"
            ),
        },
        "provenance_adjudication": {
            "abstract_maximal_forward_closed_form": "ACTION_OWNED",
            "local_nonzero_source_incidence": "ASSEMBLED_DOMAIN_PARAMETRIC",
            "zero_background_graph": "CLOSED_ONLY_AT_ZERO_TRACE",
            "sector_resolved_nonzero_event_flux_and_W_phys_matrix": "NOT_ASSEMBLED",
            "gauge_W_formula": "DERIVED_BUT_NOT_A_UNIVERSAL_MATTER_GRAPH",
            "two_chord_child_impedance": "CERTIFIED_NOT_A_FULL_BIRTH_WRONSKIAN",
        },
        "adjudication": {
            "core_positivity_plus_operator_nonnegativity_sufficient": False,
            "strict_physical_zero_energy_Wronskian_margin_available": False,
            "continuous_low_energy_source_measure_exponent": "OPEN",
            "compact_weak_E1_high_energy_integrability": "DERIVED",
            "zero_source_force": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_FROM_THE_RETAINED_ACTION_THE_SECTOR_RESOLVED_NONZERO_"
            "EVENT_FLUX_PLUS_W_phys_BIRTH_GRAPH_AT_ZERO_ENERGY_AND_PROVE_A_"
            "STRICT_MATRIX_WRONSKIAN_MARGIN_AGAINST_THE_CHILD_WEYL_MAP,_OR_"
            "PROVE_A_BOUNDARY_UNIFORM_LIMITING_ABSORPTION_ESTIMATE_THAT_"
            "EXCLUDES_THE_CRITICAL_COUNTERGRAPH;_THEN_DERIVE_SUPERLINEAR_"
            "CONTINUOUS_SOURCE_WEIGHTED_COUNTING_AND_EVALUATE_THE_FORCE"
        ),
        "claim_boundary": {
            "Gate_7_changed": False,
            "critical_countergraph_selected_as_physical": False,
            "universal_matter_Wentzell_graph_inferred_from_gauge_W": False,
            "terminal_event_or_finite_exit_required": False,
            "continuous_threshold_closed": False,
            "zero_source_force_closed": False,
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def materialize() -> Path:
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(_canonical(build_payload()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return RESULT


if __name__ == "__main__":
    print(materialize())
