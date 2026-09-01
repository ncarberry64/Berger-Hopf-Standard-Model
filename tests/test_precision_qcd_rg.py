import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from precision_qcd_inputs import (
    COMMON_SCALE_APPROX,
    MIXED_DEFAULT,
    PDG_STYLE_REFERENCE_PLACEHOLDER,
    PRECISION_QCD_PLACEHOLDER,
    THRESHOLD_AWARE_APPROX,
    qcd_reference_sets,
)
from precision_rg_matching import build_precision_qcd_rg_report
from quark_ratio_uncertainties import classify_tolerance, propagate_ratio_uncertainty, quark_tolerance_band
from quark_threshold_matching import (
    ONE_LOOP_BASELINE,
    THREE_LOOP_PLACEHOLDER,
    THRESHOLD_AWARE_ONE_LOOP,
    TWO_LOOP_PLACEHOLDER,
    ThresholdMatchingConfig,
    alpha_s_at_target,
    running_mass,
)


def test_reference_sets_have_required_metadata():
    sets = {item.name: item for item in qcd_reference_sets()}

    assert set(sets) == {
        MIXED_DEFAULT,
        COMMON_SCALE_APPROX,
        THRESHOLD_AWARE_APPROX,
        PDG_STYLE_REFERENCE_PLACEHOLDER,
        PRECISION_QCD_PLACEHOLDER,
    }
    for ref_set in sets.values():
        assert ref_set.status
        assert ref_set.notes
        for row in ref_set.inputs:
            assert row.particle
            assert row.unit
            assert row.scheme
            assert row.source_label
            assert row.notes


def test_placeholders_are_not_mislabeled_as_precision_calculations():
    sets = {item.name: item for item in qcd_reference_sets()}

    for name in (PDG_STYLE_REFERENCE_PLACEHOLDER, PRECISION_QCD_PLACEHOLDER):
        ref_set = sets[name]
        assert ref_set.placeholder is True
        assert ref_set.final is False
        assert ref_set.approximate is False
        assert all(row.value is None for row in ref_set.inputs)

    two_loop = running_mass("c", 1.27, 1.27, ThresholdMatchingConfig(method=TWO_LOOP_PLACEHOLDER))
    three_loop = running_mass("c", 1.27, 1.27, ThresholdMatchingConfig(method=THREE_LOOP_PLACEHOLDER))
    assert two_loop.implemented is False
    assert three_loop.implemented is False
    assert two_loop.mass_running is None
    assert three_loop.mass_running is None


def test_running_architecture_has_one_loop_and_threshold_rows():
    one_loop_alpha = alpha_s_at_target(ThresholdMatchingConfig(method=ONE_LOOP_BASELINE))
    threshold_alpha = alpha_s_at_target(ThresholdMatchingConfig(method=THRESHOLD_AWARE_ONE_LOOP))
    report = build_precision_qcd_rg_report()

    assert one_loop_alpha is not None and one_loop_alpha > 0
    assert threshold_alpha is not None and threshold_alpha > 0
    assert report.alpha_s_rows[ONE_LOOP_BASELINE] == one_loop_alpha
    assert report.alpha_s_rows[THRESHOLD_AWARE_ONE_LOOP] == threshold_alpha
    assert report.alpha_s_rows["TWO_LOOP_PLACEHOLDER"] is None
    assert report.alpha_s_rows["THREE_LOOP_PLACEHOLDER"] is None


def test_comparison_rows_include_bare_and_dressed_candidate_ct_only_for_dressed():
    report = build_precision_qcd_rg_report()
    dressed = [row for row in report.comparisons if row.branch == "BHSM_DRESSED_V1_CANDIDATE"]
    bare = [row for row in report.comparisons if row.branch == "BHSM_BARE_V1"]

    assert len(bare) == 20
    assert len(dressed) == 5
    assert {row.quantity for row in dressed} == {"c/t"}
    assert any(row.reference_set == THRESHOLD_AWARE_APPROX for row in report.comparisons)
    assert any(row.tolerance_classification == "APPROX_SCAFFOLD_TENSION" for row in report.comparisons)
    assert report.real_tensions == ()
    assert report.theorem_complete is False


def test_uncertainty_and_tolerance_scaffolds_are_explicit():
    missing = propagate_ratio_uncertainty(1.0, 2.0, None, None, predicted=0.4)
    with_uncertainty = propagate_ratio_uncertainty(1.0, 2.0, 0.1, 0.2, predicted=0.4)

    assert missing.ratio == 0.5
    assert missing.uncertainty is None
    assert with_uncertainty.uncertainty is not None
    assert with_uncertainty.pull is not None
    assert quark_tolerance_band() == 0.25
    assert classify_tolerance(0.1, scheme_consistent=True, final=True, approximate=False) == "PASS"
    assert classify_tolerance(0.9, scheme_consistent=True, final=True, approximate=False) == "REAL_BHSM_TENSION"
    assert classify_tolerance(0.9, scheme_consistent=True, final=False, approximate=True) == "APPROX_SCAFFOLD_TENSION"


def test_precision_qcd_rg_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_precision_qcd_rg_report()

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


def test_precision_qcd_modules_do_not_import_residual_or_tuning_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "precision_qcd_inputs.py",
            "precision_rg_matching.py",
            "quark_threshold_matching.py",
            "quark_ratio_uncertainties.py",
        )
    )
    forbidden = (
        "build_residual_audit",
        "prediction_ledger",
        "minimize",
        "curve_fit",
        "best_fit",
        "adopted_factor",
        "canonical_geometry_config(",
    )
    assert all(token not in source for token in forbidden)


def test_precision_qcd_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "bhsm_v1_4_precision_qcd_rg.md",
        root / "theory" / "bhsm_v1_4_precision_qcd_rg.json",
        root / "theory" / "quark_ratio_precision_comparison.md",
        root / "theory" / "quark_ratio_precision_comparison.json",
        root / "manuscript" / "BHSM_v1_4_precision_qcd_rg_note.md",
        root / "notebooks" / "40_precision_qcd_rg.ipynb",
    )
    for path in paths:
        assert path.exists(), path

    data = json.loads(paths[1].read_text())
    text = paths[0].read_text()
    note = paths[4].read_text().lower()

    assert data["theorem_complete"] is False
    assert data["frozen_predictions_changed"] is False
    assert "PDG_STYLE_REFERENCE_PLACEHOLDER" in text
    assert "PRECISION_QCD_PLACEHOLDER" in text
    assert "does not claim precision" in note
