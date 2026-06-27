import json
from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_action_candidate import load_field_action_template
from bhsm.interface.theorem_closure.cp_o_int_sprint_c_report import build_cp_o_int_field_action_report

ROOT = Path(__file__).resolve().parents[1]


def test_default_field_action_template_is_disabled():
    template = load_field_action_template(repository=ROOT)
    result = build_cp_o_int_field_action_report(repository=ROOT)
    assert template["enabled"] is False
    assert template["maximum_status_if_loaded"] == "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    assert result.conditional_author_axiom_used is False
    assert result.promoted is False


def test_enabled_complete_template_is_capped_at_conditional(tmp_path):
    template = load_field_action_template(repository=ROOT)
    template.update({
        "enabled": True,
        "field_representation": {"field": "author candidate"},
        "lorentz_structure": {"structure": "author candidate"},
        "gauge_admissibility": {"rule": "author candidate"},
        "coupling_normalization": {"rule": "author candidate"},
        "boundary_operator": {"operator": "author candidate"},
        "action_density": "author candidate density",
        "integration_measure": "author candidate measure",
        "locality": "author candidate locality",
    })
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(template), encoding="utf-8")
    result = build_cp_o_int_field_action_report(path, ROOT)
    assert result.status_after == "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    assert result.candidate_status == "AVAILABLE_AUTHOR_AXIOM_CONDITIONAL"
    assert result.action_level_closure_achieved is False
    assert result.production_eligible is False
