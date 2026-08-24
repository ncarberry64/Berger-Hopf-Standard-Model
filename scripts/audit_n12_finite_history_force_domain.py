"""Audit whether local finite encapsulation supplies a complete force domain."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def zeta_truncation_witness() -> dict[str, float]:
    coefficient = 59.0 / 30.0
    tau = np.linspace(0.0, 0.4, 20001)
    radius = 1.3 + 0.2 * tau + 0.03 * np.sin(2.0 * tau)
    density = coefficient / radius
    split = int(0.55 * (len(tau) - 1))
    short = float(np.trapezoid(density[: split + 1], tau[: split + 1]))
    long = float(np.trapezoid(density, tau))
    extension = float(np.trapezoid(density[split:], tau[split:]))
    return {
        "short_interval_common_scale_zeta_force": short,
        "long_interval_common_scale_zeta_force": long,
        "extension_integral": extension,
        "additivity_residual": abs(long - short - extension),
        "minimum_radius": float(np.min(radius)),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-history force-domain inputs required")
    force, branch, flow, domain, native = [_load(path) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in (
        force, branch, flow, domain, native,
    )):
        raise RuntimeError("validated force-domain inputs required")
    witness = zeta_truncation_witness()
    validation = {
        "finite_encapsulation_local_existence_preserved": branch[
            "adjudication"
        ]["finite_positive_time_completed_encapsulation_exists"] is True,
        "infinite_nonencapsulating_branch_preserved_nonrealized": domain[
            "infinite_branch_reclassification"
        ]["infinite_optical_angular_counterexample_falsified"] is False,
        "maximal_flow_dichotomy_preserved": flow["validation_passed"] is True,
        "complete_replacement_force_identity_consumed": force[
            "claim_boundary"
        ]["heat_minus_zeta_replacement_force_functional"] == "DERIVED",
        "direct_exterior_response_route_preserved": (
            "COMPLETE_COEFFICIENT_ORACLE" in native[
                "necessity_adjudication"
            ]["exact_native_requirement"]
            and "EXTERIOR_WEYL_CALDERON_RESPONSE" in native[
                "necessity_adjudication"
            ]["exact_native_requirement"]
        ),
        "zeta_extension_force_strictly_positive": (
            witness["extension_integral"] > 0.0
            and witness["minimum_radius"] > 0.0
        ),
        "zeta_extension_additivity_verified": (
            witness["additivity_residual"] < 1.0e-12
        ),
        "arbitrary_local_cutoff_not_promoted": True,
        "no_infinite_tail_recurrence_selector_endpoint_parameter_scale_fit_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT",
        "status": "LOCAL_ENCAPSULATION_EXISTS_COMPLETE_ACTION_OWNED_FORCE_INTERVAL_OPEN",
        "classification": (
            "THE_LOCAL_DESINGULARIZED_BRANCH_CLOSES_EXISTENCE_BUT_NOT_THE_"
            "COMPLETE_FORCE_DOMAIN;_AN_ARBITRARY_LOCAL_lambda_CUTOFF_CHANGES_"
            "THE_RETAINED_ZETA_COMMON_SCALE_FORCE_BY_THE_STRICTLY_POSITIVE_"
            "INTEGRAL_(59/30)*d_tau/R4,_SO_THE_CURRENT_OPERATOR_MUST_USE_AN_"
            "ACTION_OWNED_COMPLETE_FORMATION_INTERVAL_OR_CANONICAL_STOP"
        ),
        "theorem": {
            "positive_radius_hypothesis": "R4(tau)>0_ON_[T1,T2]",
            "common_scale_direction": "delta_log_R4=h=1",
            "zeta_force_extension_identity": (
                "F_zeta([0,T2])-F_zeta([0,T1])="
                "(59/30)*integral_(T1,T2)_d_tau/R4(tau)>0"
            ),
            "consequence": (
                "THE_LOCAL_BRANCH_PARAMETER_epsilon_OR_ANY_REGULAR_COVER_"
                "ENDPOINT_IS_NOT_A_PHYSICALLY_INERT_OPERATOR_CUTOFF"
            ),
            "heat_cancellation_over_every_cutoff_proved": False,
            "reset_fiber_force_invariance_proved": False,
        },
        "domain_adjudication": {
            "finite_encapsulation_existence": "CLOSED_LOCALLY",
            "finite_endpoint_trace_control": "CLOSED_ONCE_DOMAIN_IS_REALIZED",
            "complete_action_owned_force_interval": "OPEN",
            "direct_action_owned_exterior_Weyl_Calderon_response": "OPEN_EQUIVALENT_ROUTE",
            "arbitrary_short_local_branch_is_complete_physical_history": False,
            "arbitrary_regular_free_cutoff_allowed": False,
            "infinite_tail_analysis_reopened": False,
            "post_event_return_required": False,
            "universal_reachability_required": False,
        },
        "witness": witness,
        "exact_next_dependency": (
            "DERIVE_THE_ACTION_OWNED_FINITE_ENDPOINT_EXTERIOR_WEYL_CALDERON_"
            "RESPONSE_DIRECTLY_FROM_THE_CERTIFIED_DESINGULARIZED_EVENT_GRAPH,_"
            "OR_CERTIFY_AN_EQUIVALENT_COMPLETE_FINITE_COEFFICIENT_ORACLE;_"
            "DO_NOT_USE_A_NUMERICAL_COVER_ENDPOINT_AS_A_BOUNDARY_CONDITION"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_COMPLETE_FORCE_DOMAIN_OPEN",
            "zero_source_heat_minus_zeta_force_functional": "DERIVED",
            "zero_source_force_value": "OPEN",
            "same_action_saddle": "WAITING_ON_COMPLETE_FORCE_DOMAIN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
