import json
from math import isclose
from pathlib import Path

import numpy as np

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from ht_operator import default_level2_config
from operator_norm_bounds import spectral_norm
from sector_coupling_bounds import (
    level2_sector_coupling_dirac_block,
    level2_sector_coupling_squared_perturbation,
)
from structured_sector_bounds import (
    build_structured_sector_bound_report,
    default_structured_sector_scan,
    export_structured_sector_bound_json,
    export_structured_sector_bound_markdown,
    sector_block_decomposition,
    sector_coupling_selection_rules,
    structured_coupling_rules,
    structured_relative_bound_certificate,
)


def test_structured_block_decomposition_covers_full_sector_perturbation():
    config = default_level2_config()
    perturbation = level2_sector_coupling_squared_perturbation(config)
    blocks = sector_block_decomposition(perturbation, config)
    reconstructed = sum(blocks.values())

    assert np.allclose(reconstructed, perturbation)
    assert set(blocks) == {
        ("lepton", "lepton"),
        ("lepton", "up"),
        ("lepton", "down"),
        ("up", "lepton"),
        ("up", "up"),
        ("up", "down"),
        ("down", "lepton"),
        ("down", "up"),
        ("down", "down"),
    }


def test_no_coupling_to_protected_zero_modes_is_reported():
    config = default_level2_config()
    zero_count = int(config.boundary_params["zero_mode_count"])
    dirac_block = level2_sector_coupling_dirac_block(config)
    squared_perturbation = level2_sector_coupling_squared_perturbation(config)
    rules = {rule.id: rule for rule in structured_coupling_rules(config)}

    assert np.allclose(dirac_block[:zero_count, :], 0.0)
    assert np.allclose(dirac_block[:, :zero_count], 0.0)
    assert np.allclose(squared_perturbation[:zero_count, :], 0.0)
    assert np.allclose(squared_perturbation[:, :zero_count], 0.0)
    assert rules["zero_mode_vanishes"].value is True


def test_selection_rules_preserve_hopf_charge_j_and_chirality():
    rules = sector_coupling_selection_rules(default_level2_config())

    assert rules
    assert all(not rule.same_sector for rule in rules)
    assert all(rule.preserves_q for rule in rules)
    assert all(rule.preserves_j for rule in rules)
    assert all(rule.preserves_chirality for rule in rules)


def test_block_wise_norm_bounds_are_conservative():
    report = build_structured_sector_bound_report()

    for row in report.block_norm_table:
        assert float(row["spectral_norm"]) >= 0.0
        assert float(row["row_sum_norm"]) >= 0.0
    total_norm = spectral_norm(level2_sector_coupling_squared_perturbation(default_level2_config()))
    assert max(float(row["spectral_norm"]) for row in report.block_norm_table) <= total_norm + 1e-12


def test_structured_relative_bound_is_candidate_not_theorem():
    certificate = structured_relative_bound_certificate(default_level2_config())

    assert certificate.sufficient is True
    assert certificate.classification == "RELATIVE_BOUND_CANDIDATE"
    assert certificate.structured_lower_bound >= certificate.required_dirac_lower_bound
    assert certificate.theorem_complete is False
    assert any("finite-basis" in item for item in certificate.limitations)


def test_structured_scan_is_sufficient_but_not_promoted_to_proof():
    rows = default_structured_sector_scan()

    assert len(rows) == 84
    assert all(row["sufficient"] is True for row in rows)
    assert all(row["classification"] == "RELATIVE_BOUND_CANDIDATE" for row in rows)
    assert all(row["theorem_complete"] is False for row in rows)


def test_finite_rank_banded_and_compactness_diagnostics_are_explicit():
    report = build_structured_sector_bound_report()

    assert "finite rank at fixed k_max" in report.finite_rank_certificate
    assert "not finite-rank certified" in report.finite_rank_certificate
    assert "mode-block ordering" in report.banded_support_certificate
    assert "no compactness theorem" in report.compactness_diagnostic
    assert report.decay_fit["status"] in {"NO_STRONG_DECAY", "DECAY_CANDIDATE", "INSUFFICIENT_DATA"}


def test_structured_bounds_do_not_import_empirical_modules():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("structured_sector_bounds.py", "relative_bound_program.py")
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


def test_structured_sector_audit_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_structured_sector_bound_report()
    default_structured_sector_scan()

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


def test_structured_sector_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "structured.md"
    json_path = tmp_path / "structured.json"

    export_structured_sector_bound_markdown(md_path)
    export_structured_sector_bound_json(json_path)

    assert "Structured Sector-Coupling Bound Report" in md_path.read_text()
    data = json.loads(json_path.read_text())
    assert data["theorem_complete"] is False
    assert data["relative_certificate"]["classification"] == "RELATIVE_BOUND_CANDIDATE"
