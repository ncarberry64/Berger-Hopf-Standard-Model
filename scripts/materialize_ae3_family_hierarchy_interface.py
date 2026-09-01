"""Materialize the AE3 family-hierarchy necessary-interface theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_family_hierarchy_interface import (
    family_hierarchy_puzzle_ledger,
)


ARTIFACTS = ROOT / "artifacts"
TARGET = ARTIFACTS / "action_extension/BHSM_AE3_FAMILY_HIERARCHY_INTERFACE.json"
INPUTS = (
    ARTIFACTS / "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
    ARTIFACTS / "action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json",
    ARTIFACTS / "BHSM_aether_cycle_family_centrality_v15_87.json",
    ARTIFACTS / "BHSM_aether_physical_inverse_closure_v16_36.json",
    ARTIFACTS / "BHSM_generation_projector_action_attachment_v8_2.json",
    ROOT / "src/bhsm/interface/ae3_family_hierarchy_interface.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("family hierarchy inputs required: " + ", ".join(missing))
    ae3 = _load(INPUTS[0])
    c2 = _load(INPUTS[1])
    centrality = _load(INPUTS[2])
    inverse = _load(INPUTS[3])
    generation = _load(INPUTS[4])
    ledger = family_hierarchy_puzzle_ledger()
    route_a = ledger["decision_surface"]["route_A_action_selected_C3_breaking"]
    route_b = ledger["decision_surface"]["route_B_triality_changing_intertwiner"]
    validation = {
        "AE3_localization_and_transport_valid": ae3["validation_passed"] is True,
        "current_C2_quadratic_piece_valid": c2["validation_passed"] is True,
        "historical_family_centrality_theorem_valid": centrality["validation_passed"] is True,
        "physical_inverse_requirement_matrix_valid": inverse["validation_passed"] is True,
        "generation_projectors_valid": generation["validation_passed"] is True,
        "present_composition_exactly_family_central": ledger["centrality_certificate"][
            "certificate_passed"
        ]
        is True,
        "present_composition_cannot_split_three_families": ledger[
            "centrality_certificate"
        ]["three_distinct_family_singular_values_possible"]
        is False,
        "route_A_exhibits_three_distinct_singular_values": route_a[
            "three_distinct_singular_values"
        ]
        is True,
        "route_A_breaks_C3_but_preserves_projector_locality": (
            route_a["C3_commutator_norm"] > 0.0
            and route_a["maximum_projector_commutator_norm"] == 0.0
        ),
        "route_B_exhibits_three_distinct_singular_values": route_b[
            "three_distinct_singular_values"
        ]
        is True,
        "route_B_preserves_C3_but_changes_family_projectors": (
            route_b["C3_commutator_norm"] < 1.0e-12
            and route_b["maximum_projector_commutator_norm"] > 0.0
        ),
        "no_family_route_selected": ledger["decision_surface"][
            "route_selected_by_current_evidence"
        ]
        is None,
        "no_particle_spectrum_rebuild": ledger["particle_spectrum_rebuilt"] is False,
        "no_prediction_emitted": ledger["prediction_emitted"] is False,
    }
    return {
        "artifact": "BHSM_AE3_FAMILY_HIERARCHY_INTERFACE",
        "action_version": "BHSM-AE-3.0.0",
        **ledger,
        "claim_boundary": {
            "derived": [
                "present_AE3_attachment_composition_is_family_central",
                "present_composition_cannot_derive_three_distinct_charged_lepton_masses",
                "two_structurally_sufficient_noncentral_interface_classes",
            ],
            "not_derived": [
                "which_noncentral_route_the_BHSM_action_selects",
                "charged_lepton_mass_eigenvalues",
                "quark_mass_eigenvalues",
                "CKM_or_PMNS_matrices",
            ],
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3 family hierarchy interface validation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
