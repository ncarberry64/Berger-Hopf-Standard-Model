import json
from math import isclose
from pathlib import Path

import numpy as np

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from ht_operator import default_level2_config
from operator_norm_bounds import operator_norm_bounds, weyl_lower_bound
from sector_coupling_bounds import (
    config_without_sector_coupling,
    default_sector_coupling_scan,
    export_sector_coupling_bound_report_json,
    export_sector_coupling_bound_report_markdown,
    level2_sector_coupling_dirac_block,
    level2_sector_coupling_squared_perturbation,
    scan_sector_coupling_bounds,
    sector_coupling_bound_report,
)
from spectral_gap import natural_lambda2
from twisted_dirac import build_level2_dirac_matrix


def test_sector_coupling_block_is_isolated_correctly():
    report = sector_coupling_bound_report()
    config = default_level2_config()
    block = level2_sector_coupling_dirac_block(config)
    disabled_block = level2_sector_coupling_dirac_block(config_without_sector_coupling(config))

    assert np.any(np.abs(block) > 0.0)
    assert np.allclose(disabled_block, 0.0)
    assert np.allclose(block, block.T)
    assert report.sector_coupling > 0


def test_squared_perturbation_matches_full_minus_uncoupled_operator():
    config = default_level2_config()
    full = build_level2_dirac_matrix(config)
    base = build_level2_dirac_matrix(config_without_sector_coupling(config))
    perturbation = level2_sector_coupling_squared_perturbation(config)

    assert np.allclose(perturbation, full.T @ full - base.T @ base)


def test_norm_bounds_are_finite_nonnegative_and_ordered():
    config = default_level2_config()
    perturbation = level2_sector_coupling_squared_perturbation(config)
    bounds = {bound.name: bound for bound in operator_norm_bounds(perturbation)}

    assert all(bound.value >= 0.0 for bound in bounds.values())
    assert bounds["frobenius_norm"].value >= bounds["spectral_norm"].value - 1e-12
    assert bounds["row_sum_norm"].value >= 0.0


def test_weyl_lower_bound_is_conservative_for_baseline():
    report = sector_coupling_bound_report(lambda2=natural_lambda2())

    assert report.stability.weyl_lower_bound == weyl_lower_bound(
        report.base_complement_lower_bound,
        report.sector_perturbation_spectral_norm,
    )
    assert report.stability.weyl_lower_bound <= report.full_complement_lower_bound + 1e-12
    assert report.stability.finite_basis_passes is True


def test_baseline_norm_bound_is_sufficient_but_theorem_remains_open():
    report = sector_coupling_bound_report()

    assert report.stability.classification == "NORM_BOUND_SUFFICIENT"
    assert report.stability.norm_bound_sufficient is True
    assert report.stability.weyl_lower_bound >= report.required_dirac_lower_bound
    assert report.theorem_complete is False
    assert report.stability.theorem_complete is False


def test_insufficient_norm_bound_is_not_misreported_as_analytic_proof():
    rows = scan_sector_coupling_bounds(
        k_max_values=[16],
        a_values=[0.573],
        perturbations=[{"sector_coupling": 0.02}],
        lambda2=natural_lambda2(),
    )

    row = rows[0]
    assert row["finite_basis_passes"] is True
    assert row["norm_bound_sufficient"] is False
    assert row["classification"] == "NORM_BOUND_INSUFFICIENT_BUT_FINITE_BASIS_PASSES"
    assert row["theorem_complete"] is False


def test_required_robustness_scan_reports_mixed_bound_statuses():
    rows = default_sector_coupling_scan()

    assert len(rows) == 72
    assert all(row["zero_mode_count"] == 3 for row in rows)
    assert all(row["finite_basis_passes"] is True for row in rows)
    assert {row["classification"] for row in rows} == {
        "NORM_BOUND_SUFFICIENT",
        "NORM_BOUND_INSUFFICIENT_BUT_FINITE_BASIS_PASSES",
    }


def test_relative_bound_estimate_is_explicit():
    report = sector_coupling_bound_report()

    assert report.relative_bound.a_k >= 0.0
    assert report.relative_bound.b_k == 0.0
    assert report.relative_bound.assumptions
    assert report.relative_bound.limitations


def test_no_forbidden_empirical_modules_are_imported_by_sector_bounds():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("sector_coupling_bounds.py", "operator_norm_bounds.py")
    )
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


def test_sector_coupling_audit_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    sector_coupling_bound_report()
    default_sector_coupling_scan()

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


def test_sector_coupling_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "sector_bounds.md"
    json_path = tmp_path / "sector_bounds.json"

    export_sector_coupling_bound_report_markdown(md_path)
    export_sector_coupling_bound_report_json(json_path)

    assert "Sector-Coupling Operator-Norm Audit" in md_path.read_text()
    data = json.loads(json_path.read_text())
    assert data["theorem_complete"] is False
    assert data["baseline"]["stability"]["classification"] == "NORM_BOUND_SUFFICIENT"
