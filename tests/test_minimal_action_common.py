from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.minimal_action import STATUS_TAXONOMY, build_minimal_action_report, close_minimal_action
from bhsm.interface.minimal_action.action_terms import load_minimal_action_axioms
from bhsm.interface.minimal_action.sector_projectors import projectors_are_orthogonal


ROOT = Path(__file__).resolve().parents[1]


def test_minimal_action_has_five_terms_and_three_orthogonal_projectors() -> None:
    report = build_minimal_action_report()
    assert report.action_expression == "S_boundary + S_sector + S_phase + S_charged + S_neutral"
    assert [term.key for term in report.terms] == ["boundary", "sector", "phase", "charged", "neutral"]
    assert len(report.sector_projectors) == 3
    assert projectors_are_orthogonal(report.sector_projectors)
    assert all(row.rank == 1 and sum(row.diagonal) == 1 for row in report.sector_projectors)


def test_statuses_use_clean_taxonomy_and_one_missing_object() -> None:
    report = build_minimal_action_report()
    assert all(row.status_after in STATUS_TAXONOMY for row in report.results)
    assert all(not row.promoted for row in report.results)
    assert all(row.remaining_missing_object for row in report.results)
    assert not report.empirical_derivation_inputs_used
    assert not report.internet_required
    assert not report.external_hep_tools_required


def test_author_axiom_template_is_disabled_and_bounded() -> None:
    payload = load_minimal_action_axioms()
    assert payload["source_status"] == "DISCOVERED"
    assert len(payload["axioms"]) == 3
    assert all(row["enabled"] is False for row in payload["axioms"])
    assert all(row["maximum_status"] == "CONDITIONAL_ACTION_THEOREM" for row in payload["axioms"])

    parsed = json.loads((ROOT / "data/theorem_inputs/minimal_action_axioms_template.json").read_text())
    assert parsed["author_supplied"] is True


def test_incomplete_enabled_axiom_cannot_promote() -> None:
    payload = {
        "axioms": [{
            "axiom_key": "INCOMPLETE",
            "enabled": True,
            "complete_definition": True,
            "affected_theorems": ["cp_o_int"],
            "maximum_status": "CONDITIONAL_ACTION_THEOREM",
            "definitions": {"action_source": "candidate"},
        }]
    }
    result = close_minimal_action("cp_o_int", axioms=payload)
    assert result.status_after == "OPEN_MISSING_ACTION_SOURCE"
    assert result.promoted is False
