"""Materialize the existing N12 canonical stop as the AE4 terminal domain."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_canonical_stop_domain_bridge import (
    ACTION_VERSION,
    CLASSIFICATION,
    canonical_stop_domain_bridge,
    claim_boundary,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
STOP = F / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
TRANSVERSE = F / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_STOP_TRANSVERSALITY.json"
FIRST_HIT = F / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"
OPEN_FAMILY = F / "BHSM_N12_GATE7_OPEN_FAMILY_STOP_TRANSVERSALITY_REDUCTION.json"
ENDPOINT = F / "BHSM_N12_ACTION_OWNED_ENDPOINT_LOAD_REDUCTION.json"
CORE = F / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
AE4_DOMAIN = A / "BHSM_AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN.json"
TERMINAL_TRANSPORT = A / "BHSM_AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE.json"
INPUTS = (
    STOP,
    TRANSVERSE,
    FIRST_HIT,
    OPEN_FAMILY,
    ENDPOINT,
    CORE,
    AE4_DOMAIN,
    TERMINAL_TRANSPORT,
    ROOT / "src/bhsm/interface/ae4_current_c2_canonical_stop_domain_bridge.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    (
        stop,
        transverse,
        first_hit,
        open_family,
        endpoint,
        core,
        ae4_domain,
        terminal_transport,
    ) = (_load(path) for path in INPUTS[:8])
    if not all(
        record.get("validation_passed") is True
        for record in (
            stop,
            transverse,
            first_hit,
            open_family,
            endpoint,
            core,
            ae4_domain,
            terminal_transport,
        )
    ):
        raise RuntimeError("validated stop, endpoint, core, and AE4 inputs required")

    bridge = canonical_stop_domain_bridge(
        exact_stop_certified=(
            stop["status"]
            == "ONE_EXACT_FORWARD_RESET_HISTORY_REACHES_A_CANONICAL_EARLIEST_STOP"
        ),
        stop_transverse=transverse["consequence"][
            "canonical_earliest_stop_is_transverse"
        ],
        first_hit_interval_certified=(
            first_hit["status"]
            == "CANONICAL_TRANSVERSE_FIRST_HIT_TIME_INTERVAL_CERTIFIED"
        ),
        open_stop_stratum_derived=(
            stop["Gate7_consequence"]["open_stop_reaching_seed_stratum"]
            == "FOLLOWS_FROM_STRICT_FIXED_TIME_SIGN_BRACKET_AND_RETAINED_"
            "REGULAR_FLOW_CONTINUOUS_DEPENDENCE"
        ),
        endpoint_domain_owned=(
            endpoint["claim_boundary"]["endpoint_domain_ownership"] == "CLOSED"
        ),
        canonical_stop_uses_friedrichs=(
            endpoint["endpoint_load_adjudication"]["canonical_stop"]
            == "FRIEDRICHS_FORM_CLOSURE_OF_THE_RETAINED_NONNEGATIVE_MINIMAL_FORM"
        ),
    )
    boundary = claim_boundary()
    validation = {
        "canonical_stop_branch_is_action_owned_and_nonempty": bridge[
            "canonical_stop_branch_available"
        ],
        "canonical_stop_uses_retained_Friedrichs_closure": (
            bridge["terminal_domain"]
            == "FRIEDRICHS_FORM_CLOSURE_OF_RETAINED_NONNEGATIVE_MINIMAL_FORM"
        ),
        "stop_branch_requires_no_independent_finite_tail_load": (
            bridge["independent_finite_terminal_load_required"] is False
        ),
        "moving_endpoint_variation_is_preserved": bridge[
            "moving_stop_and_bulk_coefficient_jets_required"
        ],
        "event_child_Weyl_branch_not_silently_closed": not bridge[
            "event_branch_child_Weyl_family_reclassified_as_closed"
        ],
        "finite_1222_core_edge_remains_nonphysical": (
            core["endpoint_event_child_partition"]["far_core_edge_is_physical_endpoint"]
            is False
            and not bridge["finite_proof_core_edge_promoted_to_stop"]
        ),
        "AE4_future_only_domain_retained": ae4_domain["claim_boundary"][
            "AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN_CLASS_SELECTED"
        ],
        "terminal_jet_transport_no_go_consumed_without_overclaim": (
            terminal_transport["claim_boundary"][
                "AE4_CURRENT_C2_TERMINAL_HS_JETS_DERIVED"
            ]
            is False
            and terminal_transport["scientific_result"][
                "finite_core_can_erase_unknown_terminal_HS_jets"
            ]
            is False
        ),
        "stop_matched_operator_not_overclaimed": not boundary[
            "AE4_CURRENT_C2_STOP_MATCHED_OPERATOR_PATH_EVALUATED"
        ],
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "scientific_result": {
            "existing_canonical_stop_recovered": True,
            "stop_reaching_reset_stratum": "NONEMPTY_OPEN_72_DIMENSIONAL",
            "endpoint_domain_on_stop_branch": bridge["terminal_domain"],
            "factorized_terminal_graph": bridge["factorized_terminal_graph"],
            "finite_terminal_load_and_its_HS_jets_needed_on_stop_branch": False,
            "moving_stop_and_bulk_HS_variations_still_needed": True,
            "event_branch_child_Weyl_family_status": "OPEN_UNCHANGED",
            "global_terminal_chart_reachability_needed_on_this_stop_branch": False,
            "global_terminal_chart_reachability_promoted": False,
        },
        "bridge": bridge,
        "hindsight_dependency_reduction": {
            "superseded_wording": (
                "DERIVE_A_MAXIMAL_CHILD_FINITE_TERMINAL_LOAD_AND_HS_JETS_ON_"
                "EVERY_REALIZED_HISTORY"
            ),
            "current_stop_branch_owner": (
                "ASSEMBLE_THE_ACTION_OWNED_OPERATOR_COEFFICIENT_PATH_TO_THE_"
                "EXISTING_TRANSVERSE_FIRST_STOP_AND_APPLY_ITS_FRIEDRICHS_"
                "FORM_CLOSURE_WITH_MOVING_ENDPOINT_JETS"
            ),
            "why": (
                "THE_REPOSITORY_ALREADY_CERTIFIES_ONE_EXACT_CANONICAL_FIRST_"
                "STOP_AND_PROMOTES_IT_BY_TRANSVERSALITY_TO_A_NONEMPTY_OPEN_"
                "RESET_STRATUM"
            ),
        },
        "claim_boundary": boundary,
        "exact_next_calculation": (
            "CONSTRUCT_THE_STOP_MATCHED_NONLINEAR_CURRENT_C2_log_R4_AND_"
            "PROPER_DURATION_COEFFICIENT_PATH_WITH_ITS_HS_MOVING_ENDPOINT_"
            "JETS,_THEN_PROPAGATE_THE_FIRST_ORDER_PRODUCT_DIRAC_WEYL_GRAPH_"
            "WITH_THE_ACTION_SELECTED_FRIEDRICHS_TERMINAL_DOMAIN_AND_"
            "INTEGRATE_THE_AE4_E1_HESSIAN"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE4 canonical-stop domain bridge validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
