from __future__ import annotations

from bhsm.interface.neutrino_scale import index_legacy_curvature_artifacts


def test_legacy_curvature_artifacts_are_bundled_and_indexed_offline() -> None:
    rows = index_legacy_curvature_artifacts()
    assert len(rows) == 4
    assert all(row.use_allowed_for_theory for row in rows)
    assert not any(row.use_allowed_for_empirical_calibration for row in rows)
    assert all(len(row.sha256) == 64 for row in rows)
    assert {row.artifact_key for row in rows} == {
        "local_curvature_threshold_eft",
        "curvature_mass_gap_eft",
        "hyperspherical_mass_framework",
        "origin_of_mass_latex",
    }


def test_legacy_index_records_mass_gap_and_hyperspherical_support() -> None:
    rows = {row.artifact_key: row for row in index_legacy_curvature_artifacts()}
    assert any("m_gap" in formula for formula in rows["curvature_mass_gap_eft"].recognized_formulas)
    assert any("S^3" in formula for formula in rows["hyperspherical_mass_framework"].recognized_formulas)

