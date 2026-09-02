"""Materialize the AE4 future-collapse relative-boundary domain."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_future_collapse_relative_boundary_domain import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    future_collapse_domain_contract,
    recovered_child_correspondence_assets,
    reflection_no_go_resolution,
    retarded_child_schur_complement,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN.json"
INPUTS = (
    A / "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json",
    A / "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER.json",
    A / "BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json",
    ROOT / "artifacts/BHSM_aether_n3_event_complete_child_correspondence_v17_84.json",
    ROOT / "artifacts/BHSM_aether_n3_child_bvp_dtn_match_v17_86.json",
    ROOT / "artifacts/BHSM_aether_persistent_nonequilibrium_child_v17_87.json",
    ROOT / "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json",
    ROOT / "artifacts/BHSM_aether_n3_complete_child_persistence_v17_99.json",
    ROOT / "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE.json",
    ROOT / "theory/bhsm_action_ae2_nonfermion_threshold.md",
    ROOT / "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    return value


def theorem_witness() -> dict[str, Any]:
    parent = np.asarray(((2.1, 0.2), (0.2, 1.7)), dtype=complex)
    coupling = np.asarray(((0.31, -0.08j), (0.05 + 0.02j, 0.27)), dtype=complex)
    child = np.asarray(((1.8 + 0.4j, 0.13), (0.13, 1.45 + 0.25j)), dtype=complex)
    return retarded_child_schur_complement(parent, coupling, child)


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    json_sources = [_load(path) for path in INPUTS[:-2]]
    witness = theorem_witness()
    domain = future_collapse_domain_contract()
    reflection = reflection_no_go_resolution()
    recovered = recovered_child_correspondence_assets()
    boundary = claim_boundary()
    validation = {
        "all_source_artifacts_validated": all(row["validation_passed"] for row in json_sources),
        "causal_identity_exact": witness["causal_dissipation_identity_residual"] < 2.0e-15,
        "child_passive": witness["child_retarded_imaginary_part_positive_semidefinite"],
        "effective_parent_passive": witness["effective_retarded_imaginary_part_positive_semidefinite"],
        "future_domain_selected": domain["child_condition"].startswith("FUTURE_RETARDED"),
        "reflection_not_reused": not domain["reciprocal_reflected_cap_selected"],
        "AE31_no_go_preserved": not reflection["AE31_no_go_contradicted"],
        "v17_child_chain_reused": (
            recovered["v17_84_first_variation_and_F_child_formula_reused"]
            and recovered["v17_86_metric_lapse_finite_chart_slice_evaluated"]
            and recovered["v17_88_to_v17_98_retained_boundary_map_closed"]
            and recovered[
                "v17_99_positive_duration_complete_child_persistence_validated"
            ]
            and recovered["AE2_zero_threshold_nonfermion_resonance_excluded"]
        ),
        "v21_cross_resolution_child_chain_reused": (
            recovered[
                "v21_35_exact_attachment_complete_persistent_orders"
            ] == [3, 4, 5, 6]
            and recovered[
                "v21_35_asymptotic_high_shell_inverse_derived"
            ]
        ),
        "N12_continuum_child_and_forward_clock_reused": (
            recovered["N12_continuum_event_child_certified"]
            and recovered["N12_local_singular_hitting_reset_relation_certified"]
            and recovered["N12_physical_time_orientation"] == "ONE_FORWARD"
        ),
        "stale_five_block_list_retired": not recovered[
            "five_v17_84_era_missing_block_list_is_current"
        ],
        "finite_continuum_bridge_later_closed": boundary[
            "AE4_FINITE_N6_TO_M0_NORMAL_SCHUR_BRIDGE_CERTIFIED"
        ],
        "global_forward_reachability_not_overclaimed": not boundary[
            "AE4_GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED"
        ],
        "physical_child_not_overclaimed": not boundary["AE4_CURRENT_C2_FUTURE_CHILD_BLOCK_EVALUATED"],
    }
    return _canonical({
        "artifact": "BHSM_AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "retarded_schur_complement_witness": witness,
        "future_collapse_domain_contract": domain,
        "reflection_no_go_resolution": reflection,
        "recovered_child_correspondence_assets": recovered,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    })


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("future-collapse relative-boundary domain failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
