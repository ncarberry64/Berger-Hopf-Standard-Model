import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from curvature_screening import curvature_screening_conditions, curvature_screening_factor
from derivative_screening import derivative_screening_conditions, derivative_suppression_factor
from fifth_force_exclusion import (
    FULL_SCREENING_THEOREM_PROVEN,
    build_scalar_screening_proof_report,
    explicit_direct_light_scalar_failure,
    export_fifth_force_exclusion_json,
    export_fifth_force_exclusion_markdown,
    export_scalar_screening_json,
    export_scalar_screening_markdown,
)
from scalar_action import (
    CURVATURE_SCREENED,
    DERIVATIVE_SCREENED,
    FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
    HIGGS_PROJECTED_LIGHT_MODE,
    HOPF_GAP_LIFTED,
    HT_COMPLEMENT_LIFTED,
    VIRTUAL_ONLY,
    action_level_scalar_modes,
)
from scalar_screening_action import SCREENING_SCAFFOLD_PASSES, matter_coupling_audit


def test_derivative_screened_modes_are_not_static_fifth_force_mediators():
    rows = matter_coupling_audit()
    derivative_rows = [row for row in rows if row.channel == DERIVATIVE_SCREENED]

    assert derivative_rows
    assert all(row.derivative_coupling_only for row in derivative_rows)
    assert all(not row.ordinary_on_shell_fifth_force_mediator for row in derivative_rows)
    assert all("DERIVATIVE_SCREENED" in row.status for row in derivative_rows)
    assert derivative_suppression_factor(0.0, 1.0) == 0.0
    assert derivative_suppression_factor(1.0, 1000.0) < 1.0


def test_curvature_screened_modes_are_suppressed_in_flat_limit():
    conditions = curvature_screening_conditions()
    rows = matter_coupling_audit()
    curvature_rows = [row for row in rows if row.channel == CURVATURE_SCREENED]

    assert conditions
    assert all(condition.flat_limit_suppresses for condition in conditions)
    assert curvature_screening_factor(0.0, 1.0) == 0.0
    assert all(row.curvature_coupling_only for row in curvature_rows)
    assert all(not row.ordinary_on_shell_fifth_force_mediator for row in curvature_rows)


def test_direct_light_matter_coupled_scalar_is_flagged():
    risk = explicit_direct_light_scalar_failure()

    assert risk.channel == FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    assert risk.direct_matter_coupling is True
    assert risk.ordinary_on_shell_fifth_force_mediator is True
    assert risk.status == FORBIDDEN_UNSCREENED_LIGHT_SCALAR


def test_all_v1_5_scalar_modes_receive_matter_coupling_classifications():
    modes = action_level_scalar_modes()
    rows = matter_coupling_audit()

    assert {row.mode_id for row in rows} == {mode.mode_id for mode in modes}
    assert {row.channel for row in rows} == {
        HIGGS_PROJECTED_LIGHT_MODE,
        HOPF_GAP_LIFTED,
        HT_COMPLEMENT_LIFTED,
        DERIVATIVE_SCREENED,
        CURVATURE_SCREENED,
        VIRTUAL_ONLY,
    }
    assert all(row.status for row in rows)
    assert all(row.limitations for row in rows)


def test_no_open_scalar_risk_is_hidden_in_screening_report():
    report = build_scalar_screening_proof_report()

    assert report.status == SCREENING_SCAFFOLD_PASSES
    assert report.theorem_complete is False
    assert report.status != FULL_SCREENING_THEOREM_PROVEN
    assert report.fifth_force_exclusion.open_scalar_risks == ()
    assert report.fifth_force_exclusion.forbidden_unscreened_modes == ()
    assert len(report.fifth_force_exclusion.excluded_modes) == len(action_level_scalar_modes())


def test_derivative_and_curvature_conditions_include_assumptions_and_limitations():
    derivative = derivative_screening_conditions()
    curvature = curvature_screening_conditions()

    assert all(row.static_long_range_force_absent for row in derivative)
    assert all(row.mode_remains_virtual_or_screened for row in derivative)
    assert all(not row.observable_fifth_force_survives for row in curvature)
    assert all(row.assumptions and row.limitations for row in derivative + curvature)


def test_scalar_screening_scaffold_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_scalar_screening_proof_report()

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


def test_scalar_screening_modules_do_not_import_empirical_or_residual_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "scalar_screening_action.py",
            "derivative_screening.py",
            "curvature_screening.py",
            "fifth_force_exclusion.py",
        )
    )
    forbidden_tokens = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "build_prediction_ledger",
        "build_residual_audit",
        "precision_rg_matching",
        "QuarkRatioComparison",
    )

    assert all(token not in sources for token in forbidden_tokens)


def test_scalar_screening_exports_generate_cleanly(tmp_path):
    md = tmp_path / "screening.md"
    data_path = tmp_path / "screening.json"
    exclusion_md = tmp_path / "exclusion.md"
    exclusion_json = tmp_path / "exclusion.json"

    export_scalar_screening_markdown(md)
    export_scalar_screening_json(data_path)
    export_fifth_force_exclusion_markdown(exclusion_md)
    export_fifth_force_exclusion_json(exclusion_json)

    data = json.loads(data_path.read_text())
    exclusion = json.loads(exclusion_json.read_text())
    assert data["report"]["status"] == SCREENING_SCAFFOLD_PASSES
    assert data["report"]["theorem_complete"] is False
    assert data["direct_light_scalar_failure_example"]["status"] == FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    assert exclusion["status"] == SCREENING_SCAFFOLD_PASSES
    assert "fully proven" not in md.read_text().lower()


def test_generated_v1_6_scalar_screening_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "bhsm_v1_6_scalar_screening.md",
        root / "theory" / "bhsm_v1_6_scalar_screening.json",
        root / "theory" / "fifth_force_exclusion_report.md",
        root / "theory" / "fifth_force_exclusion_report.json",
        root / "manuscript" / "BHSM_v1_6_scalar_screening_note.md",
        root / "notebooks" / "42_scalar_screening_proof.ipynb",
    )

    for path in paths:
        assert path.exists(), path

    data = json.loads(paths[1].read_text())
    text = paths[0].read_text()
    note = paths[4].read_text()

    assert data["report"]["status"] == SCREENING_SCAFFOLD_PASSES
    assert data["report"]["theorem_complete"] is False
    assert "Derivative-Screening Conditions" in text
    assert "Curvature-Screening Conditions" in text
    assert "does not claim a full scalar-screening theorem" in note
    assert "fully proven" not in (text + note).lower()
