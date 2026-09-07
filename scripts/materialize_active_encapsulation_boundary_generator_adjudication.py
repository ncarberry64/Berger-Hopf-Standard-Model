"""Materialize the active-encapsulation provenance and no-promotion audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.active_encapsulation_boundary_generator_adjudication import (  # noqa: E402
    adjudication_payload,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_ACTIVE_ENCAPSULATION_BOUNDARY_GENERATOR_ADJUDICATION.json"
)
MODULE = ROOT / "src/bhsm/interface/active_encapsulation_boundary_generator_adjudication.py"
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_active_encapsulation_boundary_generator_adjudication.md"
TEST = ROOT / "tests/test_active_encapsulation_boundary_generator_adjudication.py"

SOURCES = (
    "CLAIMS.md",
    "artifacts/BHSM_harmonic_role_reclassification_v6_0_6.json",
    "src/bhsm/interface/envelopment/canonical_crystallization_v11_0.py",
    "src/bhsm/interface/completion/global_envelopment_cap_selection_v14_60.py",
    "src/bhsm/interface/completion/full_global_envelopment_v14_61.py",
    "src/bhsm/interface/completion/operator_valued_calderon_wentzell_v14_66.py",
    "src/bhsm/interface/completion/action_attachment_wentzell_v14_67.py",
    "src/bhsm/interface/aether_master_closure_v15_5.py",
    "src/bhsm/interface/aether_nonlinear_norman_cycle_bvp_v15_7.py",
    "src/bhsm/interface/aether_n3_whole_child_encapsulation_audit_v17_82.py",
    "src/bhsm/interface/reset_correspondence_stationarity_adjudication.py",
    "src/bhsm/interface/reset_boundary_generating_functional_adjudication.py",
    "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
    "src/bhsm/interface/physical_encapsulation_identification.py",
    "src/bhsm/interface/environment_conditioned_reset_selector_recovery.py",
    "theory/bhsm_reset_correspondence_stationarity_adjudication.md",
    "theory/bhsm_reset_boundary_generating_functional_adjudication.md",
    "theory/n12_full_reset_action_jacobian.md",
    "theory/n12_gate7_physical_encapsulation_identification_bridge.md",
    "artifacts/BHSM_harmonic_emergent_enclosure_test_v6_0_4.json",
    "artifacts/BHSM_harmonic_linear_no_selection_theorem_v6_0_4.json",
    "artifacts/BHSM_harmonic_geometric_selection_rule_matrix_v6_0_4.json",
    "artifacts/BHSM_multi_harmonic_Hopf_bridge_selection_rules_v14_34.json",
    "artifacts/BHSM_three_harmonic_observability_v14_55.json",
    "artifacts/BHSM_action_attachment_wentzell_v14_67.json",
    "artifacts/action_extension/BHSM_AE31_C2_CALDERON_TRACE_SKELETON.json",
    "artifacts/action_extension/BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json",
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
    payload = adjudication_payload()
    source_paths = list(SOURCES) + [
        MODULE.relative_to(ROOT).as_posix(),
        SCRIPT.relative_to(ROOT).as_posix(),
        THEORY.relative_to(ROOT).as_posix(),
        TEST.relative_to(ROOT).as_posix(),
    ]
    missing = [source for source in source_paths if not (ROOT / source).is_file()]
    if missing:
        raise FileNotFoundError("missing adjudication provenance: " + ", ".join(missing))
    payload["source_sha256"] = {
        source: _sha256(ROOT / source) for source in sorted(source_paths)
    }
    claims = payload["claim_boundary"]
    rank = payload["N12_rank_ledger"]
    validation = {
        "historical_components_provenance_separated": len(payload["historical_chain"]) == 8,
        "clarification_not_relabelled_as_prior_theorem": all(
            "OWNER_CLARIFICATION" not in row["authority"]
            for row in payload["historical_chain"]
        ),
        "envelopment_remains_relation_until_carrier_selected": (
            payload["mathematical_envelopment"]["mathematical_class"]
            == "TYPED_RELATION_NOT_CURRENTLY_A_SINGLE_VALUED_MAP"
        ),
        "C_A_not_zero_support_geometry": "NOT_THE_LEVEL_SET" in payload["mathematical_envelopment"]["C_A_guardrail"],
        "active_covector_typed_but_not_valued": (
            payload["encapsulation_differential"]["value_derived"] is False
            and payload["encapsulation_differential"]["type"].startswith("SECTION_OF")
        ),
        "no_event_selected_boundary_mode_promoted": payload["harmonic_mode"]["M_rule"] is None,
        "N12_rank_unchanged": (
            rank["existing_fixed_event_fiber_dimension"] == 67
            and rank["actual_after_time_quotient"] == 66
            and rank["owner_clarification_equation_count"] == 0
        ),
        "full_field_UA5_and_FB5": (
            payload["UA_CLASS"].startswith("UA5") and payload["FB_CLASS"] == "FB5"
        ),
        "single_owner_question": payload["ONE_SMALLEST_OWNER_QUESTION"].count("?") == 1,
        "no_new_law_or_selection": not any(
            claims[key]
            for key in (
                "new_action_term_added", "new_interface_functional_added",
                "active_differential_value_selected", "harmonic_or_mode_selected",
                "F_B_selected", "L_s_selected", "physical_reset_selected",
            )
        ),
        "claim_firewall": not any(
            claims[key]
            for key in (
                "FTL_neutrinos_claimed", "particle_mechanism_proved",
                "frozen_predictions_changed", "Gate7_promoted", "FULL_BHSM_COMPLETE",
            )
        ),
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
