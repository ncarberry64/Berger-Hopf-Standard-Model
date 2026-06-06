from math import isclose

from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from quark_running import (
    MZ,
    MT_LIKE_SCALE,
    TEN_GEV,
    alpha_s_one_loop,
    build_common_scale_references,
    common_scale_residual_markdown_section,
    compare_bhsm_to_common_scale,
    export_quark_running_report_json,
    export_quark_running_report_markdown,
    mass_running_factor_one_loop,
    quark_running_report,
    run_mass_one_loop,
)


def test_running_factor_is_one_when_scales_match():
    assert mass_running_factor_one_loop(MZ, MZ) == 1.0
    assert run_mass_one_loop(1.27, 1.27, 1.27) == 1.27


def test_alpha_s_decreases_as_scale_increases():
    assert alpha_s_one_loop(10.0) > alpha_s_one_loop(MZ)
    assert alpha_s_one_loop(MT_LIKE_SCALE) < alpha_s_one_loop(MZ)


def test_masses_run_monotonically_in_expected_direction():
    charm = 1.27

    assert run_mass_one_loop(charm, 1.27, TEN_GEV) < charm
    assert run_mass_one_loop(charm, 1.27, MZ) < run_mass_one_loop(charm, 1.27, TEN_GEV)
    assert run_mass_one_loop(charm, MZ, TEN_GEV) > charm


def test_canonical_bhsm_ratios_do_not_change():
    before = compute_yukawa_ratios(build_bhsm_model())

    compare_bhsm_to_common_scale(build_bhsm_model(), MZ)
    quark_running_report(build_bhsm_model())

    after = compute_yukawa_ratios(build_bhsm_model())
    assert before == after
    assert isclose(after["up_quarks"]["middle"], 0.008310500554068288)


def test_common_scale_references_are_approximate_scaffold():
    refs = build_common_scale_references(MZ)

    assert refs["c"].scheme == "COMMON_SCALE_APPROX"
    assert refs["c"].scale == f"{MZ:g} GeV"
    assert any("APPROXIMATE_RUNNING_SCAFFOLD" in note for note in refs["c"].notes)
    assert any("No threshold matching" in note for note in refs["t"].notes)


def test_common_scale_comparison_is_separate_from_mixed_default():
    model = build_bhsm_model()
    rows = compare_bhsm_to_common_scale(model, MZ)

    assert len(rows) == 4
    assert all(row["status"] == "APPROXIMATE_RUNNING_SCAFFOLD" for row in rows)
    assert all(row["scheme"] == "COMMON_SCALE_APPROX" for row in rows)
    assert any(row["id"] == "mass_ratio.up_quarks.middle" for row in rows)


def test_residual_markdown_section_mentions_common_scale_approx():
    text = common_scale_residual_markdown_section(build_bhsm_model(), target_scales=(MZ,))

    assert "COMMON_SCALE_APPROX Residual Section" in text
    assert "APPROXIMATE_RUNNING_SCAFFOLD" in text
    assert "mass_ratio.up_quarks.middle" in text


def test_quark_running_reports_export(tmp_path):
    md_path = tmp_path / "running.md"
    json_path = tmp_path / "running.json"

    export_quark_running_report_markdown(build_bhsm_model(), md_path)
    export_quark_running_report_json(build_bhsm_model(), json_path)

    assert "# BHSM Quark Running Audit" in md_path.read_text()
    assert "APPROXIMATE_RUNNING_SCAFFOLD" in json_path.read_text()


def test_no_claim_status_is_upgraded_by_running_scaffold():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["yukawa_overlap_structure"].status == ClaimStatus.STRONG_SCREEN
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN
