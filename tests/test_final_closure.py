import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from final_closure import (
    BHSM_STRONG_SCAFFOLD,
    FULL_BHSM_COMPLETE,
    build_final_closure_report,
    build_final_theorem_ledger,
    export_final_closure_json,
    export_final_closure_markdown,
    export_final_open_obligations_markdown,
    export_final_theorem_ledger_json,
    export_final_theorem_ledger_markdown,
)


def test_final_closure_status_is_strong_scaffold_not_complete():
    report = build_final_closure_report()

    assert report.final_status == BHSM_STRONG_SCAFFOLD
    assert report.final_status != FULL_BHSM_COMPLETE
    assert report.full_bhsm_complete is False
    assert report.full_theorem_package_complete is False
    assert report.theorem_complete is False
    assert "not a fully closed" in report.correct_final_claim


def test_final_ledger_contains_open_and_forbidden_nodes():
    rows = {row.id: row for row in build_final_theorem_ledger()}

    assert rows["frozen_predictions"].closed is True
    assert rows["ht_gap"].closed is False
    assert rows["qcd_rg"].status == "OPEN"
    assert rows["forbidden_claims"].status == "FORBIDDEN"
    assert "Do not claim FULL_HT_THEOREM_PROVEN" in rows["ht_gap"].forbidden_upgrade


def test_final_closure_exports_generate_cleanly(tmp_path):
    report_md = tmp_path / "closure.md"
    report_json = tmp_path / "closure.json"
    ledger_md = tmp_path / "ledger.md"
    ledger_json = tmp_path / "ledger.json"
    open_md = tmp_path / "open.md"

    export_final_closure_markdown(report_md)
    export_final_closure_json(report_json)
    export_final_theorem_ledger_markdown(ledger_md)
    export_final_theorem_ledger_json(ledger_json)
    export_final_open_obligations_markdown(open_md)

    data = json.loads(report_json.read_text())
    assert data["final_status"] == BHSM_STRONG_SCAFFOLD
    assert data["theorem_complete"] is False
    assert "BHSM Final Theorem Ledger" in ledger_md.read_text()
    assert "full twisted Dirac" in open_md.read_text()


def test_final_closure_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_final_closure_report()

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


def test_generated_final_closure_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "bhsm_final_closure_report.md",
        root / "theory" / "bhsm_final_closure_report.json",
        root / "theory" / "bhsm_final_theorem_ledger.md",
        root / "theory" / "bhsm_final_theorem_ledger.json",
        root / "theory" / "bhsm_final_open_obligations.md",
        root / "manuscript" / "BHSM_final_closure_addendum.md",
    )
    for path in paths:
        assert path.exists(), path
    data = json.loads(paths[1].read_text())
    text = paths[0].read_text() + paths[5].read_text()
    assert data["final_status"] == BHSM_STRONG_SCAFFOLD
    assert data["full_bhsm_complete"] is False
    assert "strong no-retuning" in text
    assert "fully closed first-principles theorem package" in text


def test_final_closure_avoids_empirical_residual_machinery():
    root = Path(__file__).parents[1]
    source = (root / "src" / "final_closure.py").read_text()

    forbidden_tokens = (
        "build_prediction_ledger",
        "build_residual_audit",
        "empirical_ckm",
        "reference_mass",
        "residual_minim",
    )
    for token in forbidden_tokens:
        assert token not in source
