from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_report import evaluate_cp_o_int_stages

ROOT = Path(__file__).resolve().parents[1]


def candidate(**overrides):
    payload = {
        "enabled": True,
        "author_supplied": True,
        "formal_statement": "conditional statement",
        "domain": "candidate fields",
        "codomain": "candidate amplitudes",
        "field_representation": {"field_content": "psi", "representation": "R"},
        "lorentz_structure": {"expression": "O_int", "index_structure": "scalar"},
        "gauge_admissibility": {"gauge_representation": "singlet", "allowed_sectors": ["candidate"]},
        "phase_attachment_rule": "exp(i delta_BH) O_int + h.c.",
        "coupling_normalization": {"coupling_symbol": "g_O", "normalization": "author axiom", "mass_dimension": "candidate"},
        "action_term": "g_O exp(i delta_BH) O_int + h.c.",
        "allowed_status_if_loaded": "DERIVED_CONDITIONAL_AUTHOR_AXIOM",
        "path": "synthetic-author-template.json",
    }
    payload.update(overrides)
    return payload


def test_missing_components_return_the_deepest_specific_status():
    cases = (
        ("field_representation", {}, "OPEN_MISSING_FIELD_REPRESENTATION"),
        ("lorentz_structure", {}, "OPEN_MISSING_LORENTZ_STRUCTURE"),
        ("gauge_admissibility", {}, "OPEN_MISSING_GAUGE_ADMISSIBILITY"),
        ("coupling_normalization", {}, "OPEN_MISSING_COUPLING_NORMALIZATION"),
        ("action_term", "", "OPEN_MISSING_ACTION_SOURCE"),
    )
    for key, value, expected in cases:
        assert evaluate_cp_o_int_stages(candidate(**{key: value}), ROOT).status_after == expected


def test_complete_author_candidate_cannot_become_action_level_closure():
    result = evaluate_cp_o_int_stages(candidate(), ROOT)
    assert result.status_after == "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    assert result.conditional_author_axiom_used is True
    assert result.action_level_closure_achieved is False
    assert result.promoted is False
    assert result.deepest_valid_stage == "Stage 8: Callable theorem availability"
