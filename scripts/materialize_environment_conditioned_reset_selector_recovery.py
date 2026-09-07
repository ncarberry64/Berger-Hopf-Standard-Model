"""Materialize the provenance-only environment-conditioned selector recovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.environment_conditioned_reset_selector_recovery import (  # noqa: E402
    RECOVERY_VERDICT,
    recovery_payload,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_ENVIRONMENT_CONDITIONED_RESET_SELECTOR_RECOVERY.json"
)
MODULE = ROOT / "src/bhsm/interface/environment_conditioned_reset_selector_recovery.py"
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_environment_conditioned_reset_selector_recovery.md"
TEST = ROOT / "tests/test_environment_conditioned_reset_selector_recovery.py"


SOURCES = (
    "src/bhsm/interface/envelopment/canonical_crystallization_v11_0.py",
    "src/bhsm/interface/completion/aether_parent_stratification_v15_0.py",
    "src/bhsm/interface/completion/exact_berger_dirac_cap_obstruction_v14_59.py",
    "src/bhsm/interface/completion/global_envelopment_cap_selection_v14_60.py",
    "src/bhsm/interface/completion/boundary_triple_heat_semigroup_v14_65.py",
    "src/bhsm/interface/completion/operator_valued_calderon_wentzell_v14_66.py",
    "src/bhsm/interface/completion/action_attachment_wentzell_v14_67.py",
    "src/bhsm/interface/completion/global_attachment_incidence_curvature_v14_68.py",
    "src/bhsm/interface/aether_master_closure_v15_5.py",
    "src/bhsm/interface/aether_nonlinear_norman_cycle_bvp_v15_7.py",
    "src/bhsm/interface/aether_backward_closure_existing_answer_audit_v15_8.py",
    "src/bhsm/interface/aether_internal_clock_skin_phase_v15_14.py",
    "src/bhsm/interface/aether_material_skin_variation_v15_15.py",
    "src/bhsm/interface/aether_coupled_skin_selector_v15_16.py",
    "src/bhsm/interface/aether_hybrid_actualization_persistence_v15_52.py",
    "src/bhsm/interface/aether_full_sobolev_hybrid_actualization_v15_57.py",
    "src/bhsm/interface/aether_scale_child_ownership_audit_v16_78.py",
    "src/bhsm/interface/aether_n3_whole_child_encapsulation_audit_v17_82.py",
    "src/bhsm/interface/aether_n3_event_complete_child_correspondence_v17_84.py",
    "src/bhsm/interface/aether_n3_terminal_child_boundary_map_v17_85.py",
    "src/bhsm/interface/aether_n3_lorentzian_child_cauchy_correspondence_v17_88.py",
    "src/bhsm/interface/aether_n3_firewall_core_child_ownership_v17_98.py",
    "src/bhsm/interface/environmental_child_compatibility_selection.py",
    "src/bhsm/interface/current_semantic_normalization.py",
    "scripts/audit_n12_intrinsic_state_return_section.py",
    "theory/n12_finite_encapsulation_local_branch.md",
    "theory/n12_gate7_component_separator_audit.md",
    "theory/bhsm_spacetime_edge_ontology_repair.md",
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json",
    "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
)


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def build_payload() -> dict[str, Any]:
    payload = recovery_payload()
    source_paths = list(SOURCES) + [
        MODULE.relative_to(ROOT).as_posix(),
        SCRIPT.relative_to(ROOT).as_posix(),
        THEORY.relative_to(ROOT).as_posix(),
        TEST.relative_to(ROOT).as_posix(),
    ]
    payload["source_sha256"] = {
        source: _sha256(ROOT / source)
        for source in sorted(source_paths)
        if (ROOT / source).is_file()
    }
    validation = {
        "nine_serious_candidates_classified": len(payload["candidates"]) == 9,
        "every_candidate_has_P_and_K": all(
            row["authority"].startswith("P")
            and row["current_e5_power"].startswith("K")
            for row in payload["candidates"]
        ),
        "historical_K5_not_promoted": (
            payload["current_full_field_K4_or_K5"] == []
            and any(
                row["historical_power"] == "K5_HISTORICAL"
                and row["disposition"] == "SUPERSEDED_RULE"
                for row in payload["candidates"]
            )
        ),
        "N3_not_promoted_to_N12": (
            payload["N3_to_N12"]["N12"]["fixed_event_fiber_dimension"] == 67
            and "NO_N12_K4_OR_K5" in payload["N3_to_N12"]["N12"]["diagnosis"]
        ),
        "R_rec_is_output": payload["R_rec_lineage"]["input_or_output"].startswith("OUTPUT"),
        "z_return_is_output": payload["z_return_lineage"]["input_or_output"].startswith("OUTPUT"),
        "E5_unchanged": payload["effect_on_E5"].startswith("UNCHANGED"),
        "owner_question_is_one_question": payload["ONE_SMALLEST_OWNER_QUESTION"].count("?") == 1,
        "recovery_fails_closed": payload["RECOVERY_VERDICT"] == RECOVERY_VERDICT,
        "no_new_law_or_interface": (
            not payload["claim_boundary"]["new_physical_law_added"]
            and not payload["claim_boundary"]["new_interface_functional_added"]
        ),
        "no_reset_or_prediction_changed": (
            not payload["claim_boundary"]["reset_selected"]
            and not payload["claim_boundary"]["frozen_predictions_changed"]
        ),
        "full_BHSM_not_claimed": not payload["claim_boundary"]["FULL_BHSM_COMPLETE"],
    }
    payload["validation"] = validation
    payload["validation_passed"] = all(validation.values())
    return payload


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        deterministic_json(build_payload()), encoding="utf-8", newline="\n"
    )
    return TARGET


if __name__ == "__main__":
    print(main())
