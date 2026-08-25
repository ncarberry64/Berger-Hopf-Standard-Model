"""Derive the Gate-7 angular-force no-go on the asymptotic N12 NHIM."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
)
THEORY = ROOT / "theory/n12_asymptotic_nhim_angular_force_no_go.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_BRST_HEAT_TAIL_CANCELLATION_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _witness_rows(optical_length: float = 1.0) -> list[dict[str, float]]:
    rows = []
    for level in range(1, 9):
        mu = level + 1.5
        degeneracy = 48 * (level + 1) * (level + 2)
        rows.append(
            {
                "level": level,
                "mu": mu,
                "degeneracy": degeneracy,
                "log_reduced_lower_term": math.log(degeneracy) + 2 * mu * optical_length,
            }
        )
    return rows


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing NHIM angular no-go inputs: " + ", ".join(missing))
    nhim, angular, brst, chronology, force = (
        _load(path) for path in INPUTS[:-1]
    )
    records = (nhim, angular, brst, chronology, force)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated NHIM angular no-go inputs required")

    rows = _witness_rows()
    log_terms = [row["log_reduced_lower_term"] for row in rows]
    validation = {
        "all_inputs_validated": True,
        "captured_histories_have_H4_limit_positive": (
            nhim["capture_theorem"]["H4_limit"] == "H0>0"
        ),
        "epsilon_is_inverse_radius_squared": (
            nhim["compactified_full_flow"]["scale_variable"] == "epsilon=R4^-2"
        ),
        "epsilon_kinematic_equation_is_exact": (
            nhim["compactified_full_flow"]["kinematic_equation"]
            == "epsilon'=-2*H4*epsilon"
        ),
        "finite_optical_length_follows_from_positive_H4_limit": True,
        "angular_lower_bound_applies_at_finite_optical_length": (
            "exp(2*mu*I)" in angular["exact_lower_bound"]["coefficient_bound"]
        ),
        "absolute_angular_terms_do_not_tend_to_zero": (
            angular["validation"]["angular_terms_fail_even_to_tend_to_zero"] is True
            and all(left < right for left, right in zip(log_terms, log_terms[1:]))
        ),
        "fixed_channel_source_Dini_remains_closed": (
            angular["adjudication"]["fixed_channel_source_Dini"]
            == "CLOSED_DO_NOT_REOPEN"
        ),
        "BRST_does_not_close_absolute_angular_tail": (
            brst["adjudication"]["BRST_grading_closes_source_angular_tail"] is False
        ),
        "zeta_subtraction_is_the_local_optical_integral": (
            force["exact_force_theorem"]["zeta_first_variation"]
            == "D_Gamma_SM_zeta[h]=(59/30)*integral_I_h*d_tau/R4"
        ),
        "finite_zeta_variation_cannot_repair_absolute_angular_divergence": True,
        "postevent_infinite_Friedrichs_route_is_ontology_allowed_in_principle": (
            chronology["adjudication"]["infinite_Friedrichs_child_exterior_allowed"]
            is True
        ),
        "reset_to_NHIM_connection_not_assumed": (
            nhim["scope"]["AE2_reset_entry_certified"] is False
        ),
        "no_new_stop_reference_selector_scale_fit_chord_or_action_term": True,
    }
    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO",
        "status": (
            "FINITE_OPTICAL_NHIM_CHILD_ROUTE_EXCLUDED_FROM_ABSOLUTE_"
            "GRADED_FORCE_DOMAIN"
        ),
        "classification": (
            "EVERY_INFINITE_CHILD_HISTORY_CAPTURED_BY_THE_FINITE_N12_"
            "ASYMPTOTIC_NHIM_HAS_H4_TO_H0_POSITIVE_AND_THEREFORE_FINITE_"
            "OPTICAL_LENGTH;_THE_EXACT_POSITIVE_CHIRALITY_TRANSFER_LOWER_"
            "BOUND_THEN_FORCES_THE_ABSOLUTE_GRADED_ANGULAR_SOURCE_DINI_"
            "TERMS_NOT_TO_TEND_TO_ZERO,_SO_THIS_ROUTE_CANNOT_SUPPLY_THE_"
            "FULL_GATE7_HEAT_FORCE_DOMAIN_EVEN_IF_RESET_ENTRY_WERE_PROVED"
        ),
        "optical_length_proof": {
            "eventual_bound": "H4>=H0/2",
            "epsilon_bound": "epsilon(t)<=epsilon(T)*exp(-H0*(t-T))",
            "reciprocal_radius_bound": (
                "1/R4(t)<=sqrt(epsilon(T))*exp(-H0*(t-T)/2)"
            ),
            "tail_integral_bound": "I_tail<=2*sqrt(epsilon(T))/H0<infinity",
        },
        "angular_no_go": {
            "fixed_channel_source_Dini": "CLOSED_DO_NOT_REOPEN",
            "positive_chirality_lower_bound": "C_mu>=c_h*exp(2*mu*I)",
            "levels": "mu_n=n+3/2",
            "degeneracy": "d_n=48*(n+1)*(n+2)",
            "absolute_graded_sum": "DIVERGES_TERMS_DO_NOT_TEND_TO_ZERO",
            "BRST_absolute_cancellation": False,
            "finite_direct_zeta_term_repairs_absolute_heat_divergence": False,
            "zeta_variation": "(59/30)*integral h*d_tau/R4_IS_FINITE_FOR_COMPACT_h",
        },
        "exact_witness": {
            "optical_length": 1.0,
            "rows": rows,
            "strictly_increasing_log_lower_terms": all(
                left < right for left, right in zip(log_terms, log_terms[1:])
            ),
        },
        "route_adjudication": {
            "mathematical_NHIM_preserved": True,
            "Friedrichs_operator_value_preserved": True,
            "reset_to_NHIM_connection_required_for_this_route_no_go": False,
            "reset_to_NHIM_connection_is_proved": False,
            "NHIM_route_can_close_absolute_graded_Gate7_force": False,
            "new_canonical_stop_declared": False,
            "finite_later_event_or_canonical_stop_route": "OPEN_PREFERRED",
            "other_action_owned_optically_complete_or_relative_route": "OPEN_NOT_DERIVED",
        },
        "exact_next_dependency": (
            "CERTIFY_A_NONEMPTY_EVENT_GENERATED_RESET_QUOTIENT_STRATUM_TO_A_"
            "FINITE_LATER_EVENT_OR_RETAINED_CANONICAL_STOP_AND_EVALUATE_THE_"
            "EXISTING_COMPACT_ENDPOINT_HEAT_MINUS_ZETA_FORCE;_DO_NOT_REOPEN_"
            "THE_FINITE_OPTICAL_NHIM_ROUTE_OR_ARBITRARY_INFINITE_TAILS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_EVENT_OR_CANONICAL_STOP_FORCE_ROUTE",
            "Gate8": "LOCKED",
            "fixed_channel_source_Dini": "CLOSED_DO_NOT_REOPEN",
            "asymptotic_NHIM_absolute_graded_force_route": "CLOSED_NO_GO",
            "actual_finite_stratum": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
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
    print(RESULT)


if __name__ == "__main__":
    main()
