import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import up_sector_dressing_dependency_trace as trace  # noqa: E402


AUDIT_JSON = ROOT / "data" / "bhsm_up_sector_dressing_dependency_trace.json"
CLOSURE_MAP = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOC = ROOT / "docs" / "bhsm_up_sector_dressing_dependency_trace.md"
VIRTUAL_DOOR_DOC = ROOT / "docs" / "bhsm_up_sector_virtual_door_applicability.md"
STATUS_DOC = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_discovered_up_sector_dressing_sources_are_classified():
    rows = trace.dependency_trace_rows()
    assert len(rows) >= 8
    assert trace.all_sources_classified(rows)
    statuses = {row.status for row in rows}
    assert trace.STRUCTURAL_SOURCE in statuses
    assert trace.LEGACY_NUMERICAL_CANDIDATE in statuses
    assert trace.FROZEN_PREDICTION_REFERENCE in statuses
    assert trace.COMPARISON_ONLY in statuses


def test_frozen_prediction_references_are_not_derivations():
    frozen_rows = [
        row for row in trace.dependency_trace_rows()
        if row.status == trace.FROZEN_PREDICTION_REFERENCE
    ]
    assert frozen_rows
    for row in frozen_rows:
        assert row.links_to_two_door_pair is False
        assert row.uses_observed_data is False
        assert (
            "not a derivation" in row.reason
            or "cannot be used as a derivation" in row.reason
            or "without deriving" in row.reason
            or "without proving" in row.reason
        )


def test_comparison_only_sources_are_not_derivations():
    comparison_rows = [
        row for row in trace.dependency_trace_rows()
        if row.status == trace.COMPARISON_ONLY
    ]
    assert comparison_rows
    for row in comparison_rows:
        assert row.uses_observed_data is True
        assert row.links_to_two_door_pair is False
    assert trace.any_derivation_uses_observed_data() is False


def test_legacy_numerical_candidate_is_not_marked_derived():
    rows = trace.rows_by_status()[trace.LEGACY_NUMERICAL_CANDIDATE]
    assert rows
    assert trace.audit_statuses()["legacy_Z_virt_u2_numerical_candidate"] == (
        "LOCALIZED_NOT_DERIVED"
    )
    assert all(row.status != "DERIVED_CONDITIONAL" for row in rows)


def test_no_explicit_two_door_link_keeps_applicability_open():
    assert trace.actual_dressing_source_links_to_two_door_pair() is False
    assert trace.applicability_status() == "OPEN_LOCALIZABLE"
    assert trace.dimension_ratio_status() == "STRONG_DERIVATION_CANDIDATE"
    statuses = trace.audit_statuses()
    assert statuses["Z_virt_u2_applicability"] == "OPEN_LOCALIZABLE"
    assert statuses["Z_virt_u2_dimension_ratio"] == "STRONG_DERIVATION_CANDIDATE"


def test_explicit_two_door_link_could_upgrade_conditionally():
    row = trace.DressingDependencyRow(
        object="pure-fiber middle-up rule",
        source_file="test-only",
        source_line_or_key="test",
        depends_on="V_pair^u and A_virt^u",
        feeds_into="actual correction",
        uses_observed_data=False,
        links_to_two_door_pair=True,
        status=trace.STRUCTURAL_SOURCE,
        reason="test-only explicit link",
    )
    assert trace.applicability_status([row]) == "DERIVED_CONDITIONAL"
    assert trace.dimension_ratio_status([row]) == "DERIVED_CONDITIONAL"


def test_audit_json_and_closure_map_capture_dependency_trace_decision():
    audit = load_json(AUDIT_JSON)
    closure = load_json(CLOSURE_MAP)
    assert audit["public_status"] == trace.PUBLIC_STATUS
    assert audit["up_sector_dressing_dependency_trace"] == "COMPLETED"
    assert audit["Z_virt_u2_applicability"] == "OPEN_LOCALIZABLE"
    assert audit["Z_virt_u2_dimension_ratio"] == "STRONG_DERIVATION_CANDIDATE"
    assert audit["legacy_Z_virt_u2_numerical_candidate"] == "LOCALIZED_NOT_DERIVED"
    assert audit["Z_virt_u2_mass_fit_route"] == "FORBIDDEN_AS_DERIVATION"
    assert any(row["status"] == "COMPARISON_ONLY" for row in audit["dependency_trace"])
    assert any(row["status"] == "FROZEN_PREDICTION_REFERENCE" for row in audit["dependency_trace"])

    assert closure["up_sector_dressing_dependency_trace"]["status"] == "COMPLETED"
    assert closure["Z_virt_u2_applicability"]["status"] == "OPEN_LOCALIZABLE"
    assert closure["Z_virt_u2_dimension_ratio"]["status"] == "STRONG_DERIVATION_CANDIDATE"
    assert closure["legacy_Z_virt_u2_numerical_candidate"]["status"] == "LOCALIZED_NOT_DERIVED"
    assert closure["Z_virt_u2_mass_fit_route"]["status"] == "FORBIDDEN_AS_DERIVATION"


def test_no_observed_data_or_prediction_modules_set_z_virt():
    source = (ROOT / "src" / "up_sector_dressing_dependency_trace.py").read_text(
        encoding="utf-8"
    )
    forbidden_imports = ("mass_scheme", "prediction_ledger", "residual_audit", "ckm", "pmns", "neutrino")
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source

    audit = load_json(AUDIT_JSON)
    for item in ("charm/top ratio", "up/top ratio", "CKM values", "PMNS values", "measured alpha"):
        assert item in audit["forbidden_inputs"]


def test_docs_preserve_public_status_and_claim_boundary():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (DOC, VIRTUAL_DOOR_DOC, STATUS_DOC, CLAIM_TABLE, BACKLOG)
    )
    assert trace.PUBLIC_STATUS in combined
    assert "Z_virt_u2_applicability: OPEN_LOCALIZABLE" in combined
    assert "Z_virt_u2_dimension_ratio: STRONG_DERIVATION_CANDIDATE" in combined
    assert "legacy_Z_virt_u2_numerical_candidate: LOCALIZED_NOT_DERIVED" in combined
    assert "No frozen predictions are changed" in combined
    forbidden = (
        "BHSM is proven",
        "BHSM is complete",
        "empirically validated",
        "numerically closed",
        "charm/top agreement derives Z_virt",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_predictions_remain_unchanged_by_trace_module():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    report = trace.build_report()
    assert report.frozen_predictions_changed is False
    assert report.official_predictions_changed is False
