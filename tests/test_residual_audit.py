import json
from math import isfinite

from bhsm_model import build_bhsm_model
from prediction_ledger import build_prediction_ledger
from residual_audit import (
    build_residual_audit,
    export_residual_audit_json,
    export_residual_audit_markdown,
    log_error,
    sector_residual_summary,
    worst_residuals,
)


def test_residual_audit_builds_from_prediction_ledger():
    ledger = build_prediction_ledger(build_bhsm_model())
    audit = build_residual_audit(ledger)

    assert len(audit) == len(ledger)
    assert {row.prediction_id for row in audit} == {row.id for row in ledger}


def test_worst_residual_tracks_canonical_geometry_up_sector():
    audit = build_residual_audit(build_prediction_ledger(build_bhsm_model()))
    worst = worst_residuals(audit, n=3)

    assert worst[0].prediction_id == "mass_ratio.up_quarks.middle"
    assert any(row.prediction_id == "mass_ratio.up_quarks.light" for row in audit)
    assert any(row.prediction_id == "mass_ratio.up_quarks.middle" for row in worst)


def test_log_errors_are_finite_for_positive_predictions_with_references():
    audit = build_residual_audit(build_prediction_ledger(build_bhsm_model()))

    positive_rows = [
        row for row in audit
        if row.predicted is not None
        and row.reference is not None
        and isinstance(row.predicted, (int, float))
        and isinstance(row.reference, (int, float))
        and row.predicted > 0
        and row.reference > 0
    ]
    assert positive_rows
    assert all(row.log_error is not None and isfinite(row.log_error) for row in positive_rows)


def test_scheme_sensitive_rows_are_marked():
    audit = build_residual_audit(build_prediction_ledger(build_bhsm_model()))
    scheme_rows = [row for row in audit if row.severity == "SCHEME_SENSITIVE"]

    assert scheme_rows
    assert all("quarks" in row.prediction_id for row in scheme_rows)
    assert any(row.prediction_id == "mass_ratio.up_quarks.light" for row in scheme_rows)


def test_no_parameters_or_prediction_values_are_changed_by_audit():
    ledger = build_prediction_ledger(build_bhsm_model())
    before = {row.id: row.predicted for row in ledger}

    build_residual_audit(ledger)

    after = {row.id: row.predicted for row in ledger}
    assert before == after


def test_prediction_ledger_values_are_not_silently_overwritten():
    ledger = build_prediction_ledger(build_bhsm_model())
    audit = build_residual_audit(ledger)
    predicted_by_id = {row.id: row.predicted for row in ledger}

    for row in audit:
        assert row.predicted == predicted_by_id[row.prediction_id]


def test_exports_parse_and_render(tmp_path):
    audit = build_residual_audit(build_prediction_ledger(build_bhsm_model()))
    md_path = tmp_path / "residuals.md"
    json_path = tmp_path / "residuals.json"

    export_residual_audit_markdown(audit, md_path)
    export_residual_audit_json(audit, json_path)

    markdown = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert "# BHSM Residual Audit" in markdown
    assert data
    assert all("prediction_id" in row for row in data)


def test_sector_residual_summary_contains_all_sectors():
    audit = build_residual_audit(build_prediction_ledger(build_bhsm_model()))
    summary = sector_residual_summary(audit)

    assert set(summary) == {
        "fermion_mass_ratios",
        "ckm",
        "pmns_effective",
        "gauge_couplings",
        "higgs_electroweak",
        "ht_gap",
        "scalar_decoupling",
    }


def test_log_error_helper_returns_expected_ratio_sign():
    assert log_error(10.0, 1.0) == 1.0
    assert log_error(1.0, 10.0) == -1.0
    assert log_error(0.0, 1.0) is None
