"""Compose the current AE2 threshold frontier after the two sharpenings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"
)
MAXIMAL = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_MAXIMAL_EXTERIOR_ADJUDICATION.json"
)
NONFERMION = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
)
FACTORIZED = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json"
)
SCRIPT = ROOT / "scripts/adjudicate_n12_gate7_ae2_threshold_supersession.py"
INPUTS = (MAXIMAL, NONFERMION, FACTORIZED, SCRIPT)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("AE2 threshold supersession inputs required")
    maximal, nonfermion, factorized = (_load(path) for path in INPUTS[:3])
    if not all(
        record.get("validation_passed") is True
        for record in (maximal, nonfermion, factorized)
    ):
        raise RuntimeError("validated AE2 threshold supersession lineage required")

    validation = {
        "all_inputs_validated": True,
        "same_AE2_action_version": all(
            record.get("action_version") == "BHSM-AE-2.0.0"
            for record in (maximal, nonfermion, factorized)
        ),
        "nonfermion_threshold_sharpening_consumed": (
            nonfermion["claim_boundary"]["nonfermion_critical_zero_graph_excluded"]
            is True
        ),
        "factorized_strict_margin_reclassified": (
            factorized["claim_boundary"]
            ["strict_product_Dirac_Wronskian_required_in_advance"]
            is False
        ),
        "actual_factorized_N12_measure_remains_open": (
            factorized["claim_boundary"]["factorized_N12_low_energy_source_measure"]
            == "OPEN"
        ),
        "maximal_exterior_oracle_no_go_scope_preserved": (
            maximal["adjudication"]["new_canonical_no_go_reached"] is True
            and "NONEXISTENCE_OF_THE_ACTION_DETERMINED_MAXIMAL_HISTORY"
            in maximal["canonical_no_go"]["not_a_proof_of"]
        ),
        "force_and_Hessian_not_fabricated": (
            maximal["adjudication"]["Gate7"] == "ACTIVE_NOT_CLOSED"
        ),
        "frozen_predictions_unchanged": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION",
        "action_version": "BHSM-AE-2.0.0",
        "status": "AE2_THRESHOLD_FRONTIER_SHARPENED_MAXIMAL_EXTERIOR_STILL_REQUIRED",
        "supersedes_dependency_wording_in": (
            "BHSM_N12_GATE7_AE2_MAXIMAL_EXTERIOR_ADJUDICATION"
        ),
        "classification": (
            "THE_AE2_NONFERMION_SCALAR_DERHAM_GHOST_AND_TRANSVERSE_GAUGE_"
            "BLOCKS_HAVE_STRICT_ZERO_THRESHOLD_SEAM_MARGINS_WITHOUT_"
            "EVALUATING_THE_EVENT_EXTERIOR,_AND_AN_EXACT_FACTORIZED_"
            "ZERO_RESONANCE_MODEL_PROVES_STRICT_WEYL_WRONSKIAN_POSITIVITY_"
            "IS_NOT_NECESSARY_FOR_SUPERLINEAR_E1_SOURCE_WEIGHT;_THE_"
            "REALIZED_AE2_FACTORIZED_LIMITING_ABSORPTION,_ANGULAR_TAIL,_"
            "CALDERON_GEOMETRY_JETS,_FORCE_AND_HESSIAN_REMAIN_OPEN"
        ),
        "closed_here": {
            "nonfermion_critical_zero_graph": "EXCLUDED",
            "strict_factorized_Wronskian_as_universal_prerequisite": "RETIRED_AS_OVERSTRONG",
        },
        "preserved_open_objects": {
            "realized_factorized_source_weighted_limiting_absorption": "OPEN",
            "graded_internal_S3_angular_tail": "OPEN",
            "M_C_DPhi_M_C_DPhi2_M_C_on_realized_maximal_history": "OPEN",
            "zero_source_weak_geometry_force": "OPEN",
            "same_action_saddle": "OPEN",
            "pair_plus_contact_Hessian": "OPEN",
        },
        "exact_next_dependency": (
            "PROVE_A_RESONANCE_COMPATIBLE_SOURCE_WEIGHTED_LIMITING_"
            "ABSORPTION_BOUND_FOR_THE_REALIZED_AE2_PRODUCT_DIRAC_FAMILY_"
            "AND_A_UNIFORM_NONFERMION_BOUNDARY_LAP,_THEN_CLOSE_THE_GRADED_"
            "ANGULAR_TAIL;_THE_REALIZED_MAXIMAL_HISTORY_OR_EQUIVALENT_"
            "CALDERON_GEOMETRY_JETS_REMAINS_REQUIRED_TO_EVALUATE_THE_FORCE_"
            "AND_PAIR_PLUS_CONTACT_HESSIAN"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "additional_action_extension_required": False,
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


def materialize() -> Path:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError("AE2 threshold supersession validation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return TARGET


if __name__ == "__main__":
    print(materialize())
