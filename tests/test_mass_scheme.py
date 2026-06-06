import json
from math import isclose

from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from mass_scheme import (
    build_ratio_reference,
    compare_bhsm_ratios_to_schemes,
    default_mass_references,
    export_mass_scheme_report_json,
    export_mass_scheme_report_markdown,
    is_scheme_consistent,
    mass_scheme_report,
)
from prediction_ledger import build_prediction_ledger
from residual_audit import build_residual_audit


def test_current_quark_ratio_references_are_scheme_sensitive():
    ledger = build_prediction_ledger(build_bhsm_model())
    quark_rows = [
        row for row in ledger
        if row.id.startswith("mass_ratio.up_quarks") or row.id.startswith("mass_ratio.down_quarks")
    ]
    quark_rows = [row for row in quark_rows if not row.id.endswith(".heavy")]

    assert quark_rows
    assert all(row.metadata["scheme_sensitive"] is True for row in quark_rows)
    assert all(row.metadata["scheme_consistent"] is False for row in quark_rows)
    assert all(row.metadata["scheme"] for row in quark_rows)
    assert all(row.metadata["scale"] for row in quark_rows)


def test_lepton_ratios_are_scheme_stable():
    ledger = build_prediction_ledger(build_bhsm_model())
    lepton_rows = [
        row for row in ledger
        if row.id.startswith("mass_ratio.charged_leptons") and not row.id.endswith(".heavy")
    ]

    assert lepton_rows
    assert all(row.metadata["scheme_sensitive"] is False for row in lepton_rows)
    assert all(row.metadata["scheme_consistent"] is True for row in lepton_rows)
    assert all(row.metadata["scheme"] == "pole" for row in lepton_rows)


def test_no_quark_residual_is_final_fail_under_mixed_default():
    audit = build_residual_audit(build_prediction_ledger(build_bhsm_model()))
    quark_rows = [row for row in audit if row.prediction_id.startswith("mass_ratio.") and "quarks" in row.prediction_id]

    assert quark_rows
    assert all(row.severity != "FAIL" for row in quark_rows)
    assert all(row.severity in {"SCHEME_SENSITIVE", "EXACT_OR_STATUS"} for row in quark_rows)


def test_bhsm_canonical_values_are_unchanged_by_scheme_audit():
    ratios = compute_yukawa_ratios(build_bhsm_model())

    assert isclose(ratios["up_quarks"]["middle"], 0.008310500554068288)
    assert isclose(ratios["up_quarks"]["light"], 1.2690463017606151e-05)
    assert isclose(ratios["down_quarks"]["middle"], 0.021933971495439474)
    assert isclose(ratios["down_quarks"]["light"], 0.0011165200546001757)


def test_no_mass_values_are_silently_changed():
    references = default_mass_references()["MIXED_DEFAULT"]

    assert references["c"].value == 1.27
    assert references["t"].value == 172.69
    assert references["u"].value == 0.00216
    assert references["s"].value == 0.0934
    assert references["b"].value == 4.18
    assert references["d"].value == 0.00467
    assert build_ratio_reference("c", "t", references).ratio == 1.27 / 172.69


def test_common_scale_placeholder_is_marked_incomplete():
    references = default_mass_references()["COMMON_SCALE_PLACEHOLDER"]

    assert references["c"].scheme == "COMMON_SCALE_PLACEHOLDER"
    assert is_scheme_consistent(references["c"], references["t"]) is False
    assert "OPEN" in references["c"].scale


def test_mass_scheme_comparison_runs_for_available_schemes():
    model = build_bhsm_model()

    mixed = compare_bhsm_ratios_to_schemes(model, "MIXED_DEFAULT")
    placeholder = compare_bhsm_ratios_to_schemes(model, "COMMON_SCALE_PLACEHOLDER")

    assert len(mixed) == 6
    assert len(placeholder) == 6
    assert any(row["id"] == "mass_ratio.up_quarks.middle" for row in mixed)
    assert all("scheme_consistent" in row for row in mixed)


def test_scheme_reports_export_to_json_and_markdown(tmp_path):
    json_path = tmp_path / "mass_scheme.json"
    md_path = tmp_path / "mass_scheme.md"

    export_mass_scheme_report_json(json_path)
    export_mass_scheme_report_markdown(md_path)

    data = json.loads(json_path.read_text())
    markdown = md_path.read_text()
    assert "MIXED_DEFAULT" in data["schemes"]
    assert "COMMON_SCALE_PLACEHOLDER" in data["schemes"]
    assert "# BHSM Mass Scheme Audit" in markdown
    assert "Quark cross-generation comparisons remain scheme-sensitive" in markdown


def test_mass_scheme_report_contains_limitations():
    report = mass_scheme_report()

    assert report["limitations"]
    assert any("QCD running" in item for item in report["limitations"])
