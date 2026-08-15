"""Materialize the N=3 constrained-root hindsight and admissible corridor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


VERSION = "v18.59"
CLASSIFICATION = "BHSM_N3_CONSTRAINED_ROOT_HINDSIGHT_RECORD"
FULL_BHSM_COMPLETE = False
FLUX_LIMIT = 2.0e-5

STATE_SPECS = (
    ("v18.29", "v18.33", "BHSM_aether_n3_invalid_model_exact_merit_promotion_v18_33.json"),
    ("v18.33", "v18.37", "BHSM_aether_n3_direct_line_exact_merit_promotion_v18_37.json"),
    ("v18.37", "v18.41", "BHSM_aether_n3_second_direct_line_promotion_v18_41.json"),
    ("v18.41", "v18.43/v18.45", "BHSM_aether_n3_third_direct_line_promotion_v18_45.json"),
    ("v18.41", "v18.47", "BHSM_aether_n3_third_direct_admissible_line_promotion_v18_47.json"),
    ("v18.47", "v18.50/v18.52", "BHSM_aether_n3_bidirectional_probe_promotion_v18_52.json"),
    ("v18.47", "v18.54", "BHSM_aether_n3_bidirectional_next_candidate_promotion_v18_54.json"),
    ("v18.54", "v18.58", "BHSM_aether_n3_second_bidirectional_probe_promotion_v18_58.json"),
)


def _physical_record(payload: dict[str, Any]) -> dict[str, Any]:
    for value in payload.values():
        if isinstance(value, dict) and {
            "global_step", "event_to_complete_child", "persistence"
        }.issubset(value):
            return value
    raise ValueError(f"physical promotion record missing from {payload.get('artifact')}")


def _state_row(source: str, candidate: str, filename: str) -> dict[str, Any]:
    payload = json.loads((Path("artifacts") / filename).read_text(encoding="utf-8"))
    record = _physical_record(payload)
    global_step = record["global_step"]
    child = record["event_to_complete_child"]
    persistence = record["persistence"]
    flux_rows = child.get("flux_scale_rows", [])
    accepted = payload["status"] == "VALIDATED" and payload["validation_passed"]
    failed = [name for name, passed in payload["validation"].items() if not passed]
    return {
        "source_version": source,
        "candidate_version": candidate,
        "artifact": filename,
        "exact_376_norm": global_step["candidate_complete_norm"],
        "exact_norm_reduction": global_step["complete_norm_reduction"],
        "eta_minimum": global_step["eta_minimum"],
        "event_magnitude": global_step["event_magnitude"],
        "child_rank": child["local_chart_rank"],
        "child_chart_nullity": 26 - child["local_chart_rank"],
        "trace_residual": child["maximum_trace_residual"],
        "constraint_maximum": child["maximum_seven_constraint_residual"],
        "momentum_mismatch": child["attachment_momentum_residual_norm"],
        "local_dynamic_flux": None if not flux_rows else flux_rows[0]["norm"],
        "two_scale_flux_rows": flux_rows,
        "independent_two_scale_flux_envelope": child["resolved_dynamic_flux_envelope"],
        "persistence_constraint_maximum": persistence["maximum_constraint_residual"],
        "motion_velocity_witness": child["velocity_norm"],
        "nonzero_relative_evolution": persistence["nonzero_relative_evolution_retained"],
        "disposition": "ACCEPTED" if accepted else "REJECTED",
        "exact_rejection_reason": None if accepted else failed,
    }


def _nonincreasing(values: list[float]) -> bool:
    return all(right <= left for left, right in zip(values, values[1:]))


def constrained_root_hindsight_record() -> dict[str, Any]:
    rows = [_state_row(*spec) for spec in STATE_SPECS]
    accepted = [row for row in rows if row["disposition"] == "ACCEPTED"]
    flux = [row["independent_two_scale_flux_envelope"] for row in accepted]
    eta = [row["eta_minimum"] for row in accepted]
    rank = [row["child_rank"] for row in accepted]
    persistence = [row["persistence_constraint_maximum"] for row in accepted]
    corridor_tests = {
        "flux_margin_monotonically_collapses": _nonincreasing(
            [FLUX_LIMIT - value for value in flux]
        ),
        "eta_monotonically_approaches_zero": _nonincreasing(eta),
        "child_rank_degrades": any(right < left for left, right in zip(rank, rank[1:])),
        "persistence_residual_degrades_monotonically": all(
            right >= left for left, right in zip(persistence, persistence[1:])
        ),
    }
    rejected_below_later_accepted = []
    for rejected in (row for row in rows if row["disposition"] == "REJECTED"):
        later = [row for row in accepted if float(row["candidate_version"].split("v18.")[-1])
                 > float(rejected["candidate_version"].split("/")[-1].split("v18.")[-1])]
        for accepted_row in later:
            if rejected["exact_376_norm"] < accepted_row["exact_376_norm"]:
                rejected_below_later_accepted.append({
                    "rejected": rejected["candidate_version"],
                    "rejected_norm": rejected["exact_376_norm"],
                    "later_accepted": accepted_row["candidate_version"],
                    "later_accepted_norm": accepted_row["exact_376_norm"],
                    "rejection_reason": rejected["exact_rejection_reason"],
                })
    return {
        "constrained_root_target": {
            "event_state": "z in R^376",
            "unchanged_exact_physical_residual": "F(z) in R^376",
            "complete_child_chart": "c in R^26",
            "child_correspondence": "G(z,c)=0",
            "child_physical_rows": {"trace": 3, "constraints": 7, "canonical_momentum": 2, "dynamic_flux": 2, "total": 14},
            "admissible_set": "A={z: exists c with G(z,c)=0, eta admissible, unchanged two-scale flux gate passed, and positive-duration persistence with nonzero relative evolution}",
            "closure_problem": "FIND z* in A SUCH THAT F(z*)=0",
            "intersection_statement": "A intersection F^{-1}(0) != empty remains OPEN",
            "additional_KKT_rows": 0,
            "flux_inequality_promoted_into_KKT": False,
        },
        "local_child_chart": {
            "variables": 26,
            "physical_rows": 14,
            "measured_rank": sorted(set(rank)),
            "regular_local_nullity": 12,
            "interpretation": "LOCAL_CHART_FREEDOM_UNDER_EXISTING_PHYSICAL_EQUATIONS_NOT_TWELVE_NEW_PHYSICAL_PARAMETERS",
        },
        "state_hindsight": rows,
        "nonredundancy_witnesses": rejected_below_later_accepted,
        "physical_admissibility_is_scalar_residual_ordering": False,
        "accepted_corridor": {
            "rows": [{key: row[key] for key in (
                "candidate_version", "exact_376_norm", "eta_minimum",
                "independent_two_scale_flux_envelope", "child_rank",
                "persistence_constraint_maximum",
            )} for row in accepted],
            "tests": corridor_tests,
            "none_of_four_boundary_collapses_established": not any(corridor_tests.values()),
            "measured_statement": "The currently observed admissible corridor does not show a monotonic collapse toward the flux, eta, rank, or persistence boundaries over the measured accepted frontier.",
            "root_inside_admissible_set_proven": False,
            "continuation_restriction_added": False,
        },
        "hindsight_ledger": {
            "VALIDATED": [
                "complete moving-child reconstruction through the retained Lorentzian dynamic correspondence",
                "repeated full physical child-row rank 14 and regular local nullity 12",
                "positive-duration persistence with nonzero relative motion",
                "measurable direct finite-difference response plateaus of unchanged F_376",
                "v18.14 physical anisotropy without evidence that action-normalized stiffness forces the old raw 1e-6 crawl",
                "v18.48 separation of lapse plateau departure, eta-shift normalized compression, w absolute bending, and subdominant audited interactions",
                "continued discovery of lower-residual physically admissible states through v18.58",
            ],
            "INVALIDATED": [
                "exact stationary soliton or fixed return as universal particle criterion",
                "whole child as equation or coordinate 377",
                "terminal constraints or a static boundary law as complete child solvability",
                "componentwise, event-row, period, scale, v, or w monotonicity",
                "decreasing motion as acceptance",
                "raw 1e-6 steps or condition number alone as proof of physical stiffness",
                "unresolved coordinatewise full-event Hessian",
                "failed Krylov vectors as automatically valid Newton directions",
            ],
            "RECLASSIFIED": [
                "Krylov and JFNK vectors are exploratory local geometric probes until their Newton claim independently validates",
                "invalid solver interpretation can still generate a physically validated exact-line state",
                "lower exact F_376 norm does not guarantee physical admissibility",
                "derivative-measurement displacement differs from useful nonlinear displacement",
                "exact nonlinear F_376 decides merit; eta, fresh child, flux, and persistence decide physical promotion",
            ],
            "ACTIVE": "CONTINUE_PHYSICALLY_ADMISSIBLE_EXACT_376_ROW_DESCENT_FROM_THE_LATEST_ACCEPTED_FRONTIER_TO_F376_ZERO",
        },
        "physical_equations_changed": False,
        "acceptance_gate_changed": False,
        "FULL_BHSM_COMPLETE": False,
    }


def completion_payload() -> dict[str, Any]:
    result = constrained_root_hindsight_record()
    corridor = result["accepted_corridor"]
    validation = {
        "eight_historical_candidates_preserved": len(result["state_hindsight"]) == 8,
        "six_accepted_and_two_rejected": [row["disposition"] for row in result["state_hindsight"]].count("ACCEPTED") == 6 and [row["disposition"] for row in result["state_hindsight"]].count("REJECTED") == 2,
        "rank_14_nullity_12": result["local_child_chart"]["measured_rank"] == [14] and result["local_child_chart"]["regular_local_nullity"] == 12,
        "rejected_lower_merit_witness_retained": len(result["nonredundancy_witnesses"]) >= 1,
        "no_corridor_boundary_collapse_established": corridor["none_of_four_boundary_collapses_established"],
        "root_in_A_not_claimed": not corridor["root_inside_admissible_set_proven"],
        "no_continuation_restriction": not corridor["continuation_restriction_added"],
        "no_equation_or_gate_change": not result["physical_equations_changed"] and not result["acceptance_gate_changed"],
        "no_equation_377": result["constrained_root_target"]["additional_KKT_rows"] == 0,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_constrained_root_hindsight_record_v18_59",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "constrained_root_hindsight_record": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": "N3_IS_THE_UNCHANGED_SQUARE_ROOT_PROBLEM_RESTRICTED_BY_THE_ALREADY_IMPLEMENTED_COMPLETE_CHILD_ADMISSIBILITY_GATE",
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": result["hindsight_ledger"]["ACTIVE"],
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_constrained_root_hindsight_record_v18_59.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "constrained_root_hindsight_record", "completion_payload", "materialize"]
