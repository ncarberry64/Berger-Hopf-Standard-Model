import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from qcd_precision_closure import (
    PRECISION_INPUTS_REQUIRED,
    PRECISION_QCD_MATCHING_COMPLETE,
    build_qcd_precision_closure_report,
    export_qcd_precision_closure_json,
    export_qcd_precision_closure_markdown,
)
from rg_threshold_uncertainty import threshold_uncertainty_rows


def test_qcd_precision_closure_requires_precision_inputs():
    report = build_qcd_precision_closure_report()

    assert report.status == PRECISION_INPUTS_REQUIRED
    assert report.status != PRECISION_QCD_MATCHING_COMPLETE
    assert report.theorem_complete is False
    assert report.final_precision_set_supplied is False
    assert report.placeholder_rows > 0
    assert report.approximate_scheme_consistent_rows > 0


def test_qcd_precision_closure_reference_sets_are_metadata_complete():
    report = build_qcd_precision_closure_report()

    for ref in report.matching_report.reference_sets:
        assert ref.name
        assert ref.status
        assert ref.notes
        for input_row in ref.inputs:
            assert input_row.scheme
            assert input_row.source_label
            assert input_row.unit == "GeV"


def test_threshold_uncertainty_rows_are_explicit_placeholders_where_needed():
    rows = threshold_uncertainty_rows()

    assert rows
    assert any(row.reference_set == "PRECISION_QCD_PLACEHOLDER" and not row.implemented for row in rows)
    assert all(row.status and row.limitations for row in rows)


def test_qcd_closure_exports_generate_cleanly(tmp_path):
    md = tmp_path / "qcd.md"
    data_path = tmp_path / "qcd.json"

    export_qcd_precision_closure_markdown(md)
    export_qcd_precision_closure_json(data_path)

    data = json.loads(data_path.read_text())
    assert data["status"] == PRECISION_INPUTS_REQUIRED
    assert data["theorem_complete"] is False
    assert "No precision QCD values are invented" in md.read_text()


def test_qcd_closure_modules_do_not_import_residual_or_prediction_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("qcd_precision_closure.py", "rg_threshold_uncertainty.py")
    )
    forbidden_tokens = (
        "build_prediction_ledger",
        "build_residual_audit",
        "best_fit",
        "minimize",
    )

    assert all(token not in sources for token in forbidden_tokens)


def test_qcd_precision_closure_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_qcd_precision_closure_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert bare_after.outputs["up_quark_ratios"]["light"] == dressed_after.outputs["up_quark_ratios"]["light"]
    assert bare_after.outputs["ckm"]["angles"]["sin_theta_13"] == dressed_after.outputs["ckm"]["angles"]["sin_theta_13"]
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_generated_gate3_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "qcd_precision_closure_report.md",
        root / "theory" / "qcd_precision_closure_report.json",
        root / "manuscript" / "BHSM_qcd_precision_closure_note.md",
        root / "notebooks" / "45_qcd_precision_closure.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    data = json.loads(paths[1].read_text())
    assert data["status"] == PRECISION_INPUTS_REQUIRED
    assert data["theorem_complete"] is False
    assert "precision inputs required" in paths[2].read_text().lower()
