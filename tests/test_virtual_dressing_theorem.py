import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from virtual_dressing_theorem import (
    VIRTUAL_DRESSING_ADOPTION_CANDIDATE,
    VIRTUAL_DRESSING_DERIVED,
    build_virtual_dressing_theorem_report,
    export_virtual_dressing_theorem_json,
    export_virtual_dressing_theorem_markdown,
)
from weak_projection_dressing import weak_projection_dressing_steps, weak_projection_factor_for_middle_up


def test_virtual_dressing_stays_candidate_not_derived():
    report = build_virtual_dressing_theorem_report()

    assert report.status == VIRTUAL_DRESSING_ADOPTION_CANDIDATE
    assert report.status != VIRTUAL_DRESSING_DERIVED
    assert report.theorem_complete is False
    assert report.rule_factor == 0.5
    assert report.derived_without_empirical_residuals is True
    assert any("full loop" in item for item in report.open_obligations)


def test_weak_projection_steps_are_internal_and_pass():
    steps = weak_projection_dressing_steps()

    assert weak_projection_factor_for_middle_up() == 0.5
    assert {step.id for step in steps} == {"WP1", "WP2", "WP3"}
    assert all(step.passes for step in steps)
    assert all(step.limitations for step in steps)


def test_virtual_dressing_changes_only_ct_and_preserves_vub_rule():
    report = build_virtual_dressing_theorem_report()

    assert report.changed_outputs == ("up_quarks.middle",)
    assert report.unrelated_sectors_changed == ()
    assert report.preserves_u_over_t is True
    assert report.preserves_ckm_sin_theta_13 is True


def test_virtual_dressing_theorem_exports_generate_cleanly(tmp_path):
    md = tmp_path / "virtual.md"
    data_path = tmp_path / "virtual.json"

    export_virtual_dressing_theorem_markdown(md)
    export_virtual_dressing_theorem_json(data_path)

    data = json.loads(data_path.read_text())
    assert data["status"] == VIRTUAL_DRESSING_ADOPTION_CANDIDATE
    assert data["theorem_complete"] is False
    assert "not canonically adopted" in md.read_text()


def test_virtual_dressing_theorem_modules_do_not_import_residual_or_prediction_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("virtual_dressing_theorem.py", "weak_projection_dressing.py")
    )
    forbidden_tokens = (
        "build_prediction_ledger",
        "build_residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "best_fit",
        "minimize",
    )

    assert all(token not in sources for token in forbidden_tokens)


def test_virtual_dressing_theorem_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_virtual_dressing_theorem_report()

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


def test_generated_gate2_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "virtual_dressing_theorem_report.md",
        root / "theory" / "virtual_dressing_theorem_report.json",
        root / "manuscript" / "BHSM_virtual_dressing_theorem_note.md",
        root / "notebooks" / "44_virtual_dressing_theorem.ipynb",
    )
    for path in paths:
        assert path.exists(), path
    data = json.loads(paths[1].read_text())
    assert data["status"] == VIRTUAL_DRESSING_ADOPTION_CANDIDATE
    assert data["theorem_complete"] is False
    assert "candidate" in paths[2].read_text().lower()
