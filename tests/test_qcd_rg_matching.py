import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from qcd_rg_matching import build_qcd_rg_matching_report
from quark_mass_reference_sets import (
    COMMON_SCALE_APPROX,
    MIXED_DEFAULT,
    PRECISION_QCD_PLACEHOLDER,
    THRESHOLD_AWARE_APPROX,
    available_reference_sets,
)


def test_reference_set_architecture_contains_required_sets():
    sets = {item.name: item for item in available_reference_sets()}

    assert set(sets) == {MIXED_DEFAULT, COMMON_SCALE_APPROX, THRESHOLD_AWARE_APPROX, PRECISION_QCD_PLACEHOLDER}
    assert sets[MIXED_DEFAULT].scheme_consistent is False
    assert sets[COMMON_SCALE_APPROX].scheme_consistent is True
    assert sets[THRESHOLD_AWARE_APPROX].scheme_consistent is True
    assert sets[PRECISION_QCD_PLACEHOLDER].comparison_final is False
    assert all(item.notes for item in sets.values())


def test_qcd_rg_report_includes_bare_and_dressed_ct_without_final_stop():
    report = build_qcd_rg_matching_report()
    rows = report.comparison_rows
    dressed_ct = [row for row in rows if row.branch == "BHSM_DRESSED_V1_CANDIDATE" and row.quantity == "c/t"]
    dressed_other = [row for row in rows if row.branch == "BHSM_DRESSED_V1_CANDIDATE" and row.quantity != "c/t"]

    assert report.theorem_complete is False
    assert report.predictions_changed is False
    assert report.stop_condition_triggered is False
    assert len(dressed_ct) == 4
    assert dressed_other == []
    assert any(row.scheme_set == THRESHOLD_AWARE_APPROX for row in rows)
    assert any(row.status == "PLACEHOLDER_NOT_COMPUTED" for row in rows)


def test_no_final_scheme_consistent_failure_is_hidden():
    report = build_qcd_rg_matching_report()

    assert report.final_scheme_consistent_failures == ()
    assert all(
        not (row.comparison_final and row.scheme_consistent and row.within_fixed_tolerance is False)
        for row in report.comparison_rows
    )


def test_qcd_rg_scaffold_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_qcd_rg_matching_report()

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


def test_qcd_rg_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    md = root / "theory" / "bhsm_v1_4_qcd_rg_matching.md"
    data_path = root / "theory" / "bhsm_v1_4_qcd_rg_matching.json"
    note = root / "manuscript" / "BHSM_v1_4_qcd_rg_matching_note.md"
    notebook = root / "notebooks" / "38_qcd_rg_matching.ipynb"

    for path in (md, data_path, note, notebook):
        assert path.exists(), path

    text = md.read_text()
    data = json.loads(data_path.read_text())

    assert "PRECISION_QCD_PLACEHOLDER" in text
    assert data["theorem_complete"] is False
    assert data["stop_condition_triggered"] is False
    assert "does not\nchange BHSM predictions" in note.read_text()
