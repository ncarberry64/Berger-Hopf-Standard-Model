"""Materialize the AE4 existing-asset systems integration."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_existing_asset_system_integration import (
    ACTION_VERSION,
    CLASSIFICATION,
    authoritative_frontier_reconciliation,
    hindsight_gate_reduction,
    integrated_claim_boundary,
    museum_science_export_contract,
    one_operator_completion_graph,
    reused_upstream_asset_ledger,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json"
INPUTS = tuple(
    A / name
    for name in (
        "BHSM_AE31_C2_COLOR_SINGLET_RESIDUAL_RESPONSE_BRIDGE.json",
        "BHSM_AE31_C2_R2_ELECTRON_CAPTURE_SELECTION_RULE.json",
        "BHSM_AE31_C2_CAPTURE_NEUTRINO_PROPAGATION_GATE.json",
        "BHSM_AE31_C2_NEUTRAL_SEMIGROUP_RESPONSE_TRANSPORT.json",
        "BHSM_AE31_C2_NEUTRAL_SEED_IDENTIFICATION_BRIDGE.json",
        "BHSM_AE31_C2_NEUTRAL_WAKE_GENERATOR_ADJUDICATION.json",
        "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json",
        "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json",
        "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER.json",
    )
) + (
    ROOT / "artifacts/BHSM_aether_n3_event_complete_child_correspondence_v17_84.json",
    ROOT / "artifacts/BHSM_aether_n3_child_bvp_dtn_match_v17_86.json",
    ROOT / "artifacts/BHSM_aether_persistent_nonequilibrium_child_v17_87.json",
    ROOT / "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json",
    ROOT / "artifacts/BHSM_aether_n3_complete_child_persistence_v17_99.json",
    ROOT / "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json",
    ROOT / "artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE.json",
    ROOT / "artifacts/qxi_relative_energy_preparation/BHSM_POST_PARENT_FLAGSHIP_OBSERVABLE_GATE.json",
    ROOT / "src/bhsm/interface/ae4_existing_asset_system_integration.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    source_artifacts = [_load(path) for path in INPUTS[:-1]]
    ledger = reused_upstream_asset_ledger()
    reduction = hindsight_gate_reduction()
    graph = one_operator_completion_graph()
    boundary = integrated_claim_boundary()
    museum = museum_science_export_contract()
    frontier = authoritative_frontier_reconciliation()
    validation = {
        "all_input_artifacts_validated": all(row["validation_passed"] for row in source_artifacts),
        "all_reused_evidence_present": boundary["AE4_ALL_REUSED_ASSET_EVIDENCE_PRESENT"],
        "no_spectrum_rebuild": not boundary["AE4_PARTICLE_SPECTRUM_REBUILT"],
        "independent_Wilson_gate_retired": any(row["hindsight_status"] == "ONTOLOGY_RETIRED" for row in reduction),
        "one_operator_root": graph["single_global_operator_realization_remaining"] == 1,
        "v17_to_current_N12_child_chain_reused": all(
            row["validation_passed"] for row in source_artifacts[-12:]
        ),
        "v21_exact_attachment_finite_children_reused": (
            "N3_TO_N6_EXACT_ATTACHMENT_WEAK_COMPLETE_PERSISTENT_CHILDREN"
            in source_artifacts[-7]["cross_resolution_reconnaissance"][
                "scientific_status"
            ]
        ),
        "continuum_bridge_later_closed": (
            boundary["AE4_FINITE_N6_TO_M0_NORMAL_SCHUR_BRIDGE_CERTIFIED"]
            and frontier["CONTINUUM_EVENT_CHILD_CERTIFIED"]
        ),
        "current_forward_reachability_blocker_not_hidden": (
            not frontier["GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED"]
            and "FORWARD" in frontier["parallel_global_readout_object"]
        ),
        "primary_full_field_join_not_hidden": (
            "STRATIFIED_OPERATOR" in boundary["exact_next_calculation"]
            and "NONZERO_FERMION" in boundary["exact_next_calculation"]
        ),
        "no_independent_oracles": graph["independent_operator_oracles_remaining"] == 0,
        "global_realization_not_overclaimed": not boundary["AE4_GLOBAL_RETARDED_STRATIFIED_OPERATOR_REALIZED"],
        "museum_claim_firewall_retained": museum["export_only_from_machine_claim_boundaries"],
    }
    return {
        "artifact": "BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "reused_upstream_asset_ledger": ledger,
        "hindsight_gate_reduction": reduction,
        "one_operator_completion_graph": graph,
        "authoritative_frontier_reconciliation": frontier,
        "integrated_claim_boundary": boundary,
        "museum_science_export_contract": museum,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE4 system integration failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
