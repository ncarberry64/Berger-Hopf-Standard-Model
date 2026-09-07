from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from bhsm.interface.environment_conditioned_reset_selector_recovery import (
    ONE_OWNER_QUESTION,
    RECOVERY_VERDICT,
    candidate_ledger,
    n3_n12_comparison,
    r_rec_lineage,
    recovery_payload,
    spacetime_edge_lineage,
    z_return_lineage,
)
from scripts.materialize_environment_conditioned_reset_selector_recovery import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_environment_conditioned_reset_selector_recovery.py"
TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_ENVIRONMENT_CONDITIONED_RESET_SELECTOR_RECOVERY.json"
)


def test_every_candidate_has_provenance_authority_power_and_disposition() -> None:
    rows = candidate_ledger()
    assert len(rows) == 9
    assert len({row.candidate_id for row in rows}) == len(rows)
    assert all(row.provenance and row.authority.startswith("P") for row in rows)
    assert all(row.current_e5_power.startswith("K") for row in rows)
    dispositions = {part for row in rows for part in row.disposition.split("/")}
    assert {
        "LOST_TRANSLATION", "PARTIAL_RULE", "SUPERSEDED_RULE",
        "OWNER_SEMANTICS_ONLY", "ABSENT",
    } <= dispositions


def test_historical_k5_is_not_promoted_to_current_authority() -> None:
    rows = {row.candidate_id: row for row in candidate_ledger()}
    old = rows["C06_CONSTANT_METRIC_ERASING_ACTUALIZATION"]
    assert old.historical_power == "K5_HISTORICAL"
    assert old.current_e5_power == "K0"
    assert old.disposition == "SUPERSEDED_RULE"
    payload = recovery_payload()
    assert payload["current_full_field_K4_or_K5"] == []
    assert payload["selected_reset"] is None


def test_rec_symbols_are_outputs_not_selector_inputs() -> None:
    r_rec = r_rec_lineage()
    z_return = z_return_lineage()
    assert r_rec["input_or_output"] == "OUTPUT_AFTER_RECONSTRUCTION"
    assert r_rec["determines_scale"] is True
    assert r_rec["determines_child_state"] is False
    assert z_return["input_or_output"] == "OUTPUT_AFTER_RECONSTRUCTION"
    assert "Trace_return" in z_return["original_equation"]


def test_spacetime_edge_preserves_ontology_boundaries() -> None:
    edge = spacetime_edge_lineage()
    assert edge["older_transition_law_found"] is False
    assert "metric" in edge["not_transported_as_pregeometric_primitives"]
    assert "firewall=SPACETIME_EDGE" in edge["forbidden_identifications"]
    assert "action location" in edge["open"]


def test_n3_local_determinacy_does_not_imply_n12_uniqueness() -> None:
    comparison = n3_n12_comparison()
    assert comparison["N3"]["selection_statement"].startswith("K5 only conditionally")
    assert comparison["N12"]["fixed_event_fiber_dimension"] == 67
    assert comparison["N12"]["after_time_quotient"] == 66
    assert comparison["N12"]["normal_chart_role"].endswith("not physical selector")


def test_recovery_verdict_and_single_owner_question_fail_closed() -> None:
    payload = build_payload()
    assert payload["RECOVERY_VERDICT"] == RECOVERY_VERDICT
    assert payload["ONE_SMALLEST_OWNER_QUESTION"] == ONE_OWNER_QUESTION
    assert ONE_OWNER_QUESTION.count("?") == 1
    assert payload["effect_on_E5"].startswith("UNCHANGED")
    assert payload["generator_charge"]["unlocked"] is False
    assert payload["ABCD"] == "D_UNCHANGED"
    assert payload["validation_passed"] is True


def test_claim_firewall_and_deterministic_materialization() -> None:
    claims = build_payload()["claim_boundary"]
    assert claims == {
        "new_action_term_added": False,
        "new_interface_functional_added": False,
        "new_physical_law_added": False,
        "new_coefficient_added": False,
        "reset_selected": False,
        "FULL_BHSM_COMPLETE": False,
        "frozen_predictions_changed": False,
    }
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True
    assert stored["RECOVERY_VERDICT"] == RECOVERY_VERDICT
