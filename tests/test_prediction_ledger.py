import json
from math import isfinite

from bhsm_model import build_bhsm_model
from prediction_ledger import (
    build_prediction_ledger,
    export_prediction_ledger_json,
    export_prediction_ledger_markdown,
    finite_relative_errors,
    predictions_by_sector,
)
from yukawa_overlap import mass_ratio


REQUIRED_SECTORS = {
    "fermion_mass_ratios",
    "ckm",
    "pmns_effective",
    "gauge_couplings",
    "higgs_electroweak",
    "ht_gap",
    "scalar_decoupling",
}


def test_prediction_ledger_builds_from_bhsm_model():
    ledger = build_prediction_ledger(build_bhsm_model())

    assert ledger
    assert {row.sector for row in ledger} == REQUIRED_SECTORS


def test_no_prediction_has_empty_limitations():
    ledger = build_prediction_ledger(build_bhsm_model())

    assert all(row.limitations for row in ledger)
    assert all(all(item.strip() for item in row.limitations) for row in ledger)


def test_mass_ratio_values_are_computed_from_overlap_function():
    model = build_bhsm_model()
    ledger = build_prediction_ledger(model)
    row_by_id = {row.id: row for row in ledger}

    for sector, modes in model.generation_modes.items():
        for mode in modes:
            row = row_by_id[f"mass_ratio.{sector}.{mode.generation_rank}"]
            assert row.predicted == mass_ratio(mode.k, mode.j, a=model.geometry_config.a)


def test_exported_json_parses_cleanly(tmp_path):
    ledger = build_prediction_ledger(build_bhsm_model())
    path = tmp_path / "predictions.json"

    export_prediction_ledger_json(ledger, path)

    data = json.loads(path.read_text())
    assert len(data) == len(ledger)
    assert all("id" in row and "sector" in row for row in data)


def test_relative_errors_are_finite_where_numeric_references_exist():
    ledger = build_prediction_ledger(build_bhsm_model())

    for row in ledger:
        if row.reference is not None and row.predicted is not None and row.relative_error is not None:
            assert isfinite(row.relative_error)
    assert finite_relative_errors(ledger)


def test_ht_and_scalar_statuses_remain_proxy_or_scaffold():
    ledger = build_prediction_ledger(build_bhsm_model())
    ht_rows = predictions_by_sector(ledger, "ht_gap")
    scalar_rows = predictions_by_sector(ledger, "scalar_decoupling")

    assert ht_rows
    assert scalar_rows
    assert {row.status for row in ht_rows} == {"PROXY_AUDIT"}
    assert {row.status for row in scalar_rows} == {"FINITE_BASIS_SCAFFOLD"}


def test_markdown_and_json_exports_avoid_fully_proven_phrase(tmp_path):
    ledger = build_prediction_ledger(build_bhsm_model())
    md_path = tmp_path / "predictions.md"
    json_path = tmp_path / "predictions.json"

    export_prediction_ledger_markdown(ledger, md_path)
    export_prediction_ledger_json(ledger, json_path)

    text = md_path.read_text().lower() + "\n" + json_path.read_text().lower()
    assert "fully proven" not in text


def test_predictions_by_sector_filters_rows():
    ledger = build_prediction_ledger(build_bhsm_model())
    rows = predictions_by_sector(ledger, "gauge_couplings")

    assert len(rows) == 5
    assert all(row.sector == "gauge_couplings" for row in rows)
