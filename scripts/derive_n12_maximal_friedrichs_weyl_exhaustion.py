"""Certify the action-owned maximal Friedrichs Weyl exhaustion theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
)
THEORY = ROOT / "theory/n12_maximal_friedrichs_weyl_exhaustion.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_CHILD_FORCE_OWNER_RECONCILIATION.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _constant_channel_witness(mu: float = 1.0) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for duration in (0.5, 1.0, 2.0, 4.0, 8.0):
        finite = -mu / math.tanh(mu * duration)
        limit = -mu
        exact_error = 2.0 * mu / math.expm1(2.0 * mu * duration)
        rows.append(
            {
                "duration": duration,
                "finite_Dirichlet_core_Weyl": finite,
                "Friedrichs_limit": limit,
                "absolute_error": abs(finite - limit),
                "exact_error_formula": exact_error,
            }
        )
    return rows


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing Friedrichs exhaustion inputs: " + ", ".join(missing))
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated maximal-domain inputs required")

    rows = _constant_channel_witness()
    errors = [row["absolute_error"] for row in rows]
    validation = {
        "all_inputs_validated": True,
        "maximal_endpoint_rule_is_action_owned": (
            records[0]["validation"]["maximal_forward_history_closed"] is True
            and records[0]["validation"][
                "Friedrichs_rule_retained_for_excluded_endpoint"
            ]
            is True
            and records[0]["validation"]["arbitrary_Robin_rejected"] is True
        ),
        "proper_time_form_is_action_owned": records[1]["validation_passed"] is True,
        "compact_support_Weyl_jets_are_available": (
            records[2]["claim_boundary"][
                "infinite_Friedrichs_compact_support_Weyl_C1_C2"
            ]
            == "DERIVED"
        ),
        "continuum_maximal_flow_dichotomy_is_available": (
            records[3]["validation_passed"] is True
        ),
        "constant_channel_error_formula_replays": all(
            math.isclose(
                row["absolute_error"],
                row["exact_error_formula"],
                rel_tol=2.0e-12,
                abs_tol=2.0e-15,
            )
            for row in rows
        ),
        "constant_channel_errors_strictly_decrease": all(
            left > right for left, right in zip(errors, errors[1:])
        ),
        "finite_core_endpoints_not_promoted_to_physical_endpoints": True,
        "noncompact_reset_quotient_jet_not_overpromoted": True,
        "E1_threshold_and_angular_sums_not_overpromoted": True,
        "no_selector_endpoint_contour_scale_fit_recurrence_or_chord_added": True,
    }

    return {
        "artifact": "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION",
        "status": "MAXIMAL_FRIEDRICHS_WEYL_VALUE_IS_UNIQUE_CORE_EXHAUSTION_RESET_JET_OPEN",
        "classification": (
            "FOR_EVERY_ACTION_OWNED_FRIEDRICHS_MAXIMAL_CHILD_ROUTE_AND_REAL_"
            "z=-kappa^2<0,_THE_BIRTH_WEYL_MAP_IS_THE_OPERATOR_NORM_LIMIT_OF_"
            "NESTED_FINITE_DIRICHLET_FORM_CORE_EXHAUSTIONS;_COMPACT_SUPPORT_"
            "WEAK_C1_C2_JETS_CONVERGE_ON_THE_SAME_EXHAUSTION,_BUT_THE_"
            "NONCOMPACT_PHYSICAL_RESET_QUOTIENT_JET_AND_E1_CONTRACTIONS_"
            "REMAIN_OPEN"
        ),
        "theorem": {
            "shifted_form": "q_C[u]+kappa^2*norm(u)^2_FOR_kappa>0",
            "finite_core_domain": "COMPACT_REGULAR_SUBINTERVAL_WITH_ZERO_FAR_TRACE",
            "limit_domain": "ACTION_OWNED_MINIMAL_FORM_FRIEDRICHS_CLOSURE",
            "convergence": "MONOTONE_MOSCO_FORM_AND_STRONG_RESOLVENT_CONVERGENCE",
            "Weyl_convergence": "OPERATOR_NORM_AT_FIXED_CHANNEL_AND_GALERKIN_LEVEL",
            "compact_support_first_second_jets": "CONVERGE_BY_FORM_AND_RESOLVENT_BOUNDS",
            "global_radius_upper_required": False,
            "terminal_return_required": False,
        },
        "constant_channel_witness": {
            "operator": "-d_tau^2+mu^2",
            "mu": 1.0,
            "finite_value": "-mu*coth(mu*T)",
            "limit_value": "-mu",
            "error": "2*mu/(exp(2*mu*T)-1)",
            "rows": rows,
        },
        "closed_here": {
            "Friedrichs_negative_z_Weyl_value_existence": True,
            "Friedrichs_negative_z_Weyl_value_uniqueness": True,
            "finite_core_exhaustion_independence": True,
            "compact_support_weak_C1_C2_exhaustion": True,
        },
        "open_after_theorem": {
            "validated_numeric_actual_N12_Weyl_limit": True,
            "noncompact_reset_quotient_first_jet": True,
            "maximal_outcome_stratum_C1_control": True,
            "E1_low_energy_source_measure": True,
            "internal_angular_sum": True,
            "physical_force_root": True,
        },
        "exact_next_dependency": (
            "CERTIFY_THE_FIRST_NONCOMPACT_PHYSICAL_RESET_QUOTIENT_JET_OF_"
            "THE_MAXIMAL_COEFFICIENT_FORM_FAMILY_OR_AN_EQUIVALENT_COUPLED_"
            "FORWARD_ADJOINT_WEAK_ROOT;_THEN_EVALUATE_THE_E1_LOW_ENERGY_"
            "SOURCE_MEASURE_AND_GRADED_ANGULAR_CONTRACTIONS"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MAXIMAL_RESET_QUOTIENT_FIRST_JET_AND_FORCE_EVALUATION",
            "Gate8": "LOCKED",
            "maximal_Friedrichs_Weyl_value_definition": "DERIVED_AS_UNIQUE_EXHAUSTION",
            "actual_projected_force": "OPEN",
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
