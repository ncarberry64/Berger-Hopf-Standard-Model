import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from scalar_decoupling import ScalarMode, check_scalar_gap
from scalar_decoupling_theorem import build_scalar_decoupling_theorem_report
from scalar_state_ledger import (
    FORBIDDEN_EXTRA_LIGHT_SCALAR,
    OPEN_SCALAR_RISK,
    scalar_state_ledger,
)
from topographic_screening import curvature_filter_strength, derivative_coupling_suppression, topographic_screening_report


def test_scalar_decoupling_theorem_scaffold_passes_current_inventory():
    report = build_scalar_decoupling_theorem_report()

    assert report.status == "SCALAR_DECOUPLING_SCAFFOLD_PASSES"
    assert report.theorem_complete is False
    assert report.current_audit["exactly_one_light_higgs_projection"] is True
    assert report.current_audit["passes"] is True
    assert report.forbidden_or_open_current_modes == ()


def test_scalar_state_ledger_has_falsifier_templates_but_no_current_forbidden_mode():
    ledger = scalar_state_ledger()
    definitions = {row["category"] for row in ledger["category_definitions"]}
    current = {row["category"] for row in ledger["current_inventory"]}

    assert FORBIDDEN_EXTRA_LIGHT_SCALAR in definitions
    assert OPEN_SCALAR_RISK in definitions
    assert FORBIDDEN_EXTRA_LIGHT_SCALAR not in current
    assert OPEN_SCALAR_RISK not in current


def test_unscreened_light_scalar_is_not_hidden():
    modes = [
        ScalarMode("h", "higgs", 125.0, "higgs_projection", 1.0, True),
        ScalarMode("bad", "orthogonal", 1.0, "dangerous_light", 1.0, False),
    ]
    report = check_scalar_gap(modes, gap=1000.0)

    assert report["passes"] is False
    assert report["dangerous_light_modes"][0]["status"] == "dangerous_light"


def test_topographic_screening_examples_are_bounded_and_conditional():
    report = topographic_screening_report()

    assert derivative_coupling_suppression(1.0, 1000.0) < 1.0
    assert 0.0 <= curvature_filter_strength(1.0, 1000.0) < 1.0
    assert report["theorem_complete"] is False
    assert all(row["limitations"] for row in report["conditions"])


def test_scalar_decoupling_theorem_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_scalar_decoupling_theorem_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_scalar_decoupling_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    md = root / "theory" / "bhsm_v1_5_scalar_decoupling.md"
    data_path = root / "theory" / "bhsm_v1_5_scalar_decoupling.json"
    note = root / "manuscript" / "BHSM_v1_5_scalar_decoupling_note.md"
    notebook = root / "notebooks" / "39_scalar_decoupling.ipynb"

    for path in (md, data_path, note, notebook):
        assert path.exists(), path

    data = json.loads(data_path.read_text())
    text = md.read_text().lower()

    assert data["theorem_complete"] is False
    assert data["status"] == "SCALAR_DECOUPLING_SCAFFOLD_PASSES"
    assert "forbidden/open current modes: `0`" in text
    assert "does not prove" in note.read_text().lower()
