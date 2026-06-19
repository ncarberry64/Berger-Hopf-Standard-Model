import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import up_sector_virtual_door_applicability as virt  # noqa: E402


AUDIT_JSON = ROOT / "data" / "bhsm_up_sector_virtual_door_applicability.json"
CLOSURE_MAP = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOC = ROOT / "docs" / "bhsm_up_sector_virtual_door_applicability.md"
STATUS_DOC = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_virtual_pair_dimension_is_two():
    pair = virt.colored_weak_virtual_pair()
    assert [door.name for door in pair] == ["door_u", "door_d"]
    assert virt.virtual_pair_dimension() == 2
    assert pair[0].interpretation == "colored upper/up-compatible virtual channel"
    assert pair[1].interpretation == "colored lower/down-compatible virtual channel"


def test_up_admissibility_projector_has_rank_one():
    pair = virt.colored_weak_virtual_pair()
    assert [virt.admissibility_projector_for_up(door) for door in pair] == [1, 0]
    assert virt.admissibility_rank_for_up() == 1


def test_z_virt_ratio_is_one_half():
    assert virt.z_virt_u2_ratio() == Fraction(1, 2)
    report = virt.report_as_dict()
    assert report["pair_dimension"] == 2
    assert report["admissible_rank"] == 1
    assert report["ratio"] == "1/2"


def test_applicability_absent_keeps_status_open_not_derived():
    assert virt.applicability_status() == "OPEN_LOCALIZABLE"
    assert virt.dimension_ratio_status() == "STRONG_DERIVATION_CANDIDATE"
    statuses = virt.audit_statuses()
    assert statuses["Z_virt_u2_applicability"] == "OPEN_LOCALIZABLE"
    assert statuses["Z_virt_u2_applicability"] != "DERIVED_CONDITIONAL"
    assert statuses["Z_virt_u2_dimension_ratio"] == "STRONG_DERIVATION_CANDIDATE"


def test_applicability_can_upgrade_only_with_explicit_derived_source_row():
    derived_row = virt.SourceAuditRow(
        object="hypothetical explicit applicability proof",
        source_file="not_committed.md",
        evidence_found="explicit proof row for test only",
        supports_two_door_pair=True,
        supports_one_admissible_door=True,
        supports_up_sector_applicability=True,
        uses_observed_masses=False,
        status="DERIVED_CONDITIONAL",
        reason="test-only derived proof row",
    )
    assert virt.applicability_status([derived_row]) == "DERIVED_CONDITIONAL"
    assert virt.dimension_ratio_status([derived_row]) == "DERIVED_CONDITIONAL"


def test_audit_json_and_closure_map_record_open_applicability():
    audit = load_json(AUDIT_JSON)
    closure = load_json(CLOSURE_MAP)
    assert audit["public_status"] == virt.PUBLIC_STATUS
    assert audit["pair_dimension"] == 2
    assert audit["A_virt_u_rank"] == 1
    assert audit["Z_virt_u2_ratio"] == "1/2"
    assert audit["Z_virt_u2_dimension_ratio"] == "STRONG_DERIVATION_CANDIDATE"
    assert audit["Z_virt_u2_applicability"] == "OPEN_LOCALIZABLE"
    assert audit["Z_virt_u2_mass_fit"] == "FORBIDDEN_AS_DERIVATION"
    assert audit["uses_observed_masses"] is False
    assert audit["uses_ckm"] is False
    assert audit["uses_pmns"] is False
    assert audit["uses_neutrino_data"] is False

    assert closure["Z_virt_u2_applicability"]["status"] == "OPEN_LOCALIZABLE"
    assert closure["Z_virt_u2_dimension_ratio"]["status"] == "STRONG_DERIVATION_CANDIDATE"
    assert closure["V_pair_u_dimension"]["status"] == "FORMALIZED_DIMENSION_2"
    assert closure["A_virt_u_rank"]["status"] == "FORMALIZED_RANK_1"


def test_source_audit_rows_do_not_use_observed_masses():
    for row in virt.source_audit_rows():
        assert row.uses_observed_masses is False
    assert any(row.supports_two_door_pair for row in virt.source_audit_rows())
    assert any(row.supports_one_admissible_door for row in virt.source_audit_rows())
    assert not any(
        row.status == "DERIVED_CONDITIONAL" and row.supports_up_sector_applicability
        for row in virt.source_audit_rows()
    )

    source = (ROOT / "src" / "up_sector_virtual_door_applicability.py").read_text(
        encoding="utf-8"
    )
    forbidden_imports = ("mass_scheme", "prediction_ledger", "residual_audit", "ckm", "pmns", "neutrino")
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source


def test_docs_preserve_public_status_and_claim_boundary():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, STATUS_DOC, CLAIM_TABLE, BACKLOG)
    )
    assert virt.PUBLIC_STATUS in combined
    assert "Z_virt_u2_dimension_ratio: STRONG_DERIVATION_CANDIDATE" in combined
    assert "Z_virt_u2_applicability: OPEN_LOCALIZABLE" in combined
    assert "dim(V_pair^u) = 2" in combined
    assert "rank(A_virt^u) = 1" in combined
    assert "No frozen predictions are changed" in combined
    forbidden = (
        "BHSM is proven",
        "BHSM is complete",
        "empirically validated",
        "numerically closed",
        "fully derived without applicability proof",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_present_and_untouched_by_module():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    report = virt.build_report()
    assert report.frozen_predictions_changed is False
    assert report.official_predictions_changed is False
