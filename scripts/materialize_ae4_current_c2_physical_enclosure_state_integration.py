"""Materialize the current-C2 physical-enclosure state integration."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_physical_enclosure_state_integration import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    hindsight_supersession_contract,
    reconciled_identification_rows,
    transport_composition_contract,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
INPUTS = (
    F / "BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json",
    A / "BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
    A / "BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json",
    A / "BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json",
    A / "BHSM_AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE.json",
    F / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json",
    ROOT
    / "artifacts/n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json",
    ROOT
    / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json",
    ROOT / "src/bhsm/interface/ae4_current_c2_physical_enclosure_state_integration.py",
    ROOT / "scripts/materialize_ae4_current_c2_physical_enclosure_state_integration.py",
    ROOT / "theory/ae4_current_c2_physical_enclosure_state_integration.md",
)
TARGET = A / "BHSM_AE4_CURRENT_C2_PHYSICAL_ENCLOSURE_STATE_INTEGRATION.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    old_bridge, enclosure, integration, flux, domain, stop, continuum, time = (
        _load(path) for path in INPUTS[:8]
    )
    rows = reconciled_identification_rows()
    boundary = claim_boundary()
    old_missing = set(old_bridge["bridge_evaluation"]["missing_required_obligations"])
    validation = {
        "old_AE2_bridge_failed_closed": not old_bridge["bridge_evaluation"][
            "physical_encapsulation_identified"
        ],
        "old_AE2_carrier_rows_were_open": {"PEI_03", "PEI_04"}.issubset(old_missing),
        "AE3_owner_authorized_carrier_is_validated": enclosure["validation_passed"],
        "AE3_local_enclosure_is_action_owned": enclosure[
            "ACTION_OWNED_PHYSICAL_LOCALIZATION_AND_ENCLOSURE_DERIVED"
        ],
        "AE3_state_transport_is_derived": enclosure[
            "BHSM_NATIVE_FAMILY_MODE_STATE_TRANSPORTED_THROUGH_LOCALIZATION"
        ],
        "all_nine_state_fibers_present": len(
            enclosure["family_mode_C2_instantiation"]["rows"]
        )
        == 9,
        "transport_square_certified": enclosure["physical_transport_square"][
            "certificate_passed"
        ],
        "AE4_existing_assets_integrated": integration["integrated_claim_boundary"][
            "AE4_EXISTING_PARTICLE_AND_ENCLOSURE_ASSETS_SYSTEM_INTEGRATED"
        ],
        "AE4_six_sector_assembly_derived": flux["claim_boundary"][
            "AE4_STRATIFIED_FULL_FIELD_DIRECT_SUM_ASSEMBLY_DERIVED"
        ],
        "AE4_event_balance_identity_derived": flux["claim_boundary"][
            "AE4_EVENT_CANONICAL_FLUX_BALANCE_IDENTITY_DERIVED"
        ],
        "physical_event_balance_not_overpromoted": not flux["claim_boundary"][
            "AE4_CURRENT_C2_NOETHER_HAMILTONIAN_BALANCE_PHYSICALLY_CLOSED"
        ],
        "canonical_stop_domain_selected": domain["claim_boundary"][
            "AE4_CURRENT_C2_CANONICAL_STOP_FRIEDRICHS_ENDPOINT_SELECTED"
        ],
        "exact_canonical_stop_reached": stop["claim_boundary"][
            "exact_center_stop_witness"
        ]
        == "CERTIFIED",
        "continuum_event_child_validated": continuum["validation_passed"],
        "one_forward_time_reused": time["validation_passed"],
        "old_no_carrier_status_superseded_only_after_AE3": (
            hindsight_supersession_contract()["old_kernel_A_no_carrier_is_current"]
            is False
        ),
        "local_state_bridge_promoted": boundary[
            "BHSM_NATIVE_PARTICLE_STATE_TO_LOCAL_ENCLOSURE_BRIDGE_DERIVED"
        ],
        "complete_AE4_interacting_encapsulation_not_promoted": not boundary[
            "PHYSICAL_ENCAPSULATION_IDENTIFIED_AT_COMPLETE_AE4_INTERACTING_LEVEL"
        ],
        "no_spectrum_rebuild": not boundary["PARTICLE_SPECTRUM_REBUILT"],
        "remaining_rows_are_value_level_not_carrier_level": (
            "OPEN" in rows["PEI_07"]["status"]
            and "OPEN" in rows["PEI_09"]["status"]
        ),
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_PHYSICAL_ENCLOSURE_STATE_INTEGRATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "scientific_result": {
            "statement": (
                "THE_CURRENT_SELECTED_STOP_EVENT_CHILD_LINEAGE_CARRIES_EACH_"
                "PROVENANCE_FROZEN_BHSM_PARTICLE_FAMILY_MODE_STATE_FIBER_"
                "INTO_THE_ACTION_OWNED_AE3_SIGMA_ZERO_LOCAL_SAME_SPACETIME_"
                "ENCLOSURE_WITHOUT_REBUILDING_THE_PARTICLE_SPECTRUM"
            ),
            "claim_scope": (
                "LOCAL_CARRIER_IDENTITY_AND_STATE_TRANSPORT,_NOT_YET_THE_"
                "COMPLETE_INTERACTING_AE4_STATIONARY_BALANCE"
            ),
            "nine_state_fibers": enclosure["family_mode_C2_instantiation"]["rows"],
        },
        "transport_composition": transport_composition_contract(),
        "hindsight_supersession": hindsight_supersession_contract(),
        "reconciled_identification_rows": rows,
        "claim_boundary": boundary,
        "museum_export": {
            "local_enclosure_state_transport": "BHSM_DERIVED",
            "complete_interacting_AE4_encapsulation": "NOT_YET_DERIVED",
            "particle_poles_masses_vertices_collisions": "NOT_DERIVED_BY_THIS_RESULT",
            "particle_spectrum_rebuild_claim_allowed": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("physical-enclosure state integration validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
