import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from uniform_relative_bounds import (
    build_uniform_relative_bound_report,
    export_uniform_relative_bound_json,
    export_uniform_relative_bound_markdown,
    mode_block_band_width,
    scan_uniform_relative_bounds,
)
from ht_operator import default_level2_config


def test_uniform_scan_includes_multiple_kmax_values():
    rows = scan_uniform_relative_bounds(k_max_values=(4, 6, 8), a_values=(1.0,), perturbations=({},))

    assert {row.k_max for row in rows} == {4, 6, 8}
    assert all(row.basis_size > 0 for row in rows)
    assert all(row.theorem_complete is False for row in rows)


def test_uniform_trend_classification_is_explicit():
    report = build_uniform_relative_bound_report(k_max_values=(4, 6, 8), perturbations=({},))

    assert report.classification in {
        "UNIFORM_BOUND_SUPPORTED",
        "UNIFORM_BOUND_CANDIDATE",
        "FINITE_BASIS_ONLY",
        "FAILS_UNIFORM_SCAN",
        "OPEN",
    }
    assert report.classification == "UNIFORM_BOUND_CANDIDATE"
    assert {trend.quantity for trend in report.trends} == {
        "a_K",
        "b_K",
        "sparsity",
        "band_width",
        "structured_lower_bound",
        "finite_basis_lower_bound",
    }
    assert all(trend.status for trend in report.trends)


def test_uniform_scan_reports_bk_zero_and_stable_bandwidth():
    report = build_uniform_relative_bound_report(k_max_values=(4, 6, 8), perturbations=({},))

    assert report.all_b_k_zero is True
    assert report.max_band_width == 2
    assert next(trend for trend in report.trends if trend.quantity == "band_width").status == "stable"
    assert next(trend for trend in report.trends if trend.quantity == "b_K").status == "stable"


def test_structured_lower_bound_stays_above_required_threshold():
    rows = scan_uniform_relative_bounds(k_max_values=(4, 6, 8), a_values=(1.0,), perturbations=({},))

    assert all(row.passes_required_bound for row in rows)
    assert all(row.structured_lower_bound >= row.required_dirac_lower_bound for row in rows)
    assert all(row.finite_basis_lower_bound >= row.required_dirac_lower_bound for row in rows)


def test_mode_block_bandwidth_is_bounded_in_scanned_basis():
    assert mode_block_band_width(default_level2_config(k_max=4)) == 2
    assert mode_block_band_width(default_level2_config(k_max=8)) == 2


def test_uniform_report_is_not_labeled_full_proof():
    report = build_uniform_relative_bound_report(k_max_values=(4, 6), a_values=(1.0,), perturbations=({},))

    assert report.theorem_complete is False
    assert report.classification == "UNIFORM_BOUND_CANDIDATE"
    assert any("finite truncation evidence" in item for item in report.limitations)
    assert any("Zero-mode/complement" in item for item in report.blockers_to_infinite_basis_upgrade)


def test_uniform_bounds_do_not_import_empirical_modules():
    root = Path(__file__).parents[1]
    source = root.joinpath("src", "uniform_relative_bounds.py").read_text()
    forbidden = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "mass_ratio(",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in source for token in forbidden)


def test_uniform_bound_audit_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_uniform_relative_bound_report(k_max_values=(4, 6), a_values=(1.0,), perturbations=({},))

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


def test_uniform_report_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "uniform.md"
    json_path = tmp_path / "uniform.json"

    export_uniform_relative_bound_markdown(md_path)
    export_uniform_relative_bound_json(json_path)

    assert "Uniform Relative-Bound Audit" in md_path.read_text()
    data = json.loads(json_path.read_text())
    assert data["theorem_complete"] is False
    assert data["classification"] == "UNIFORM_BOUND_CANDIDATE"
    assert len(data["rows"]) == 108
