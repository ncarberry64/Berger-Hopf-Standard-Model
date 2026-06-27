import json
from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_action import load_cp_o_int_candidate_template
from bhsm.interface.theorem_closure.cp_o_int_report import build_cp_o_int_report

ROOT = Path(__file__).resolve().parents[1]


def test_default_template_is_disabled_and_cannot_promote():
    template = load_cp_o_int_candidate_template(repository=ROOT)
    result = build_cp_o_int_report(repository=ROOT)
    assert template["enabled"] is False
    assert template["allowed_status_if_loaded"] == "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    assert result.conditional_author_axiom_used is False
    assert result.promoted is False


def test_enabled_template_never_exceeds_conditional(tmp_path):
    template = load_cp_o_int_candidate_template(repository=ROOT)
    template.update({
        "enabled": True, "author_supplied": True,
        "formal_statement": "conditional", "domain": "D", "codomain": "C",
        "field_representation": "R", "lorentz_structure": "scalar",
        "gauge_admissibility": "singlet", "phase_attachment_rule": "phase*O",
        "coupling_normalization": "g", "action_term": "g phase O + h.c.",
    })
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(template), encoding="utf-8")
    result = build_cp_o_int_report(path, ROOT)
    assert result.status_after == "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    assert result.action_level_closure_achieved is False
    assert result.promoted is False
