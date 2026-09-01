"""Test structural graded phase independence on the retained matter family."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_phase_resolvent import (  # noqa: E402
    hs_weyl_spatial_supertrace_enclosure,
    robin_neumann_relative_heat_trace,
)


FLAGSHIP = ROOT / "artifacts/flagship_integration"
DOMAIN = FLAGSHIP / "BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO.json"
BRST = FLAGSHIP / "BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json"
QUANTUM = ROOT / "artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json"
ACCOUNTING = ROOT / "artifacts/BHSM_aether_quantum_functional_accounting_v16_00.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_boundary_phase_resolvent.py"
RESULT = FLAGSHIP / "BHSM_N12_FORWARD_GRADED_PHASE_INDEPENDENCE_NO_GO.json"
INPUTS = (DOMAIN, BRST, QUANTUM, ACCOUNTING, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite graded phase audit value")
        return value
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all graded phase-independence inputs are required")
    domain, brst, quantum, accounting = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS[:-1]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (domain, brst, quantum, accounting)
    ):
        raise RuntimeError("validated graded phase inputs are required")

    heat_time = 1.0
    radius = 1.0
    robin = 1.0
    a = heat_time / radius**2
    relative_temporal = robin_neumann_relative_heat_trace(heat_time, robin)
    spatial = hs_weyl_spatial_supertrace_enclosure(a, cutoff=20)
    product_lower = relative_temporal * spatial["graded_upper"]
    product_upper = relative_temporal * spatial["graded_lower"]

    ledger = quantum["graded_operator_ledger"]
    validation = {
        "all_inputs_validated": True,
        "domain_family_survives": domain["sector_ledger"][
            "matter_normal_boundary_generator"
        ]["continuous_domain_family"],
        "HS_species_and_sign_replayed": (
            ledger["Hubbard_Strattonovich"]["species"] == 4
            and ledger["Hubbard_Strattonovich"]["supertrace_sign"] == 1
        ),
        "Weyl_species_and_sign_replayed": (
            ledger["Weyl"]["species"] == 48
            and ledger["Weyl"]["supertrace_sign"] == -1
        ),
        "longitudinal_ghost_pair_already_cancelled": brst["adjudication"][
            "longitudinal_ghost_BRST_pair"
        ] == "CANCELS_EXACTLY",
        "matter_spatial_supertrace_strictly_negative": spatial[
            "graded_upper"
        ] < 0.0,
        "Robin_relative_temporal_trace_strictly_negative": (
            relative_temporal < 0.0
        ),
        "graded_heat_integrand_phase_difference_strictly_positive": (
            product_lower > 0.0 and product_upper >= product_lower
        ),
        "one_common_regulator_required": accounting[
            "common_observable_order"
        ]["absolute_gauge_normalization_and_nonzero_Yukawa_share_regulator"],
        "no_phase_action_term_reference_subtraction_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_GRADED_PHASE_INDEPENDENCE_NO_GO",
        "status": "UNIVERSAL_GRADED_PHASE_INDEPENDENCE_IDENTITY_INVALIDATED",
        "classification": (
            "ON_THE_UNSELECTED_COMMON_MATTER_CAYLEY_SUBFAMILY_THE_EXACT_"
            "ROBIN_MINUS_NEUMANN_TEMPORAL_RELATIVE_HEAT_TRACE_MULTIPLIES_"
            "THE_RETAINED_FOUR_HS_MINUS_48_WEYL_SPATIAL_SUPERTRACE._AT_"
            "UNIT_HEAT_TIME_AND_RADIUS_BOTH_FACTORS_ARE_CERTIFIED_NEGATIVE,_"
            "SO_THE_GRADED_HEAT_RESPONSE_CHANGES_STRICTLY_WITH_THE_ALLOWED_"
            "PHASE._WARD_BRST_THEREFORE_CANNOT_SUPPLY_A_UNIVERSAL_DOMAIN_"
            "INDEPENDENCE_IDENTITY_FOR_THE_UNCHANGED_RETAINED_ACTION"
        ),
        "exact_relative_heat_identity": {
            "operator": "K_h=-d2/dx2_ON_THE_HALF_LINE,_u'(0)=h*u(0)",
            "formula": (
                "Tr(exp(-t*K_h)-exp(-t*K_0))="
                "[exp(h^2*t)*erfc(h*sqrt(t))-1]/2"
            ),
            "heat_time": heat_time,
            "robin_parameter": robin,
            "value": relative_temporal,
        },
        "retained_matter_spatial_supertrace": {
            "formula": (
                "4*sum_(m>=1)m^2*exp(-a*m^2)-48*sum_(n>=0)"
                "(n+1)(n+2)*exp(-a*(n+3/2)^2)"
            ),
            "dimensionless_heat_time": a,
            "radius": radius,
            "enclosure": spatial,
        },
        "graded_heat_integrand_phase_difference": {
            "formula": (
                "Delta_STr_heat(t)=Delta_Tr_temporal(t)*"
                "STr_HS_minus_Weyl_spatial(t/R4^2)"
            ),
            "strict_lower": product_lower,
            "strict_upper": product_upper,
            "zero_excluded": product_lower > 0.0,
        },
        "witness_scope": {
            "common_scalar_Cayley_subfamily": (
                "THEOREM_CLASS_SUBFAMILY_OF_THE_UNSELECTED_NORMAL_MATTER_"
                "DOMAINS_NOT_AN_ACTION_SELECTED_N12_DOMAIN"
            ),
            "structural_heat_time_independence_identity_tested": True,
            "complete_fixed_regulator_E1_integral_evaluated": False,
            "actual_history_specific_accidental_cancellation_excluded": False,
        },
        "adjudication": {
            "universal_Ward_BRST_phase_independence_identity": False,
            "complete_fixed_regulator_history_specific_phase_cancellation": (
                "NOT_PROVED_AND_NOT_INFERRED_FROM_ONE_HEAT_TIME"
            ),
            "action_owned_normal_matter_generator": "STILL_REQUIRED_UNLESS_A_FULL_HISTORY_SPECIFIC_INDEPENDENCE_THEOREM_IS_PROVED",
            "zero_source_force": "OPEN_DOMAIN_DEPENDENT",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DERIVE_THE_NORMAL_MATTER_BOUNDARY_GENERATOR_FROM_EXISTING_"
            "RETAINED_ACTION_TERMS;_THE_UNIVERSAL_WARD_BRST_PHASE_"
            "INDEPENDENCE_ROUTE_IS_INVALIDATED._ONLY_AN_ACTUAL_FULL_"
            "HISTORY_FIXED_REGULATOR_THEOREM_COVERING_THE_ENTIRE_SURVIVING_"
            "CAYLEY_FAMILY_COULD_REPLACE_THAT_GENERATOR"
        ),
        "claim_boundary": {
            "one_heat_time_promoted_to_complete_E1_integral": False,
            "actual_N12_history_specific_cancellation_excluded": False,
            "new_action_term_added": False,
            "phase_selected": False,
            "frozen_predictions_changed": False,
            "new_physics_added": False,
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
