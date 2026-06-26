import json
import math
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_generator as kf
import full_threshold_operator_eligibility as threshold


DATA = ROOT / "data" / "full_threshold_operator_eligibility_v1.json"
DOC = ROOT / "docs" / "full_threshold_operator_eligibility_v1.md"
CLAIMS = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def records_by_slot():
    return {
        (record.sector, record.mode): record
        for record in threshold.threshold_eligibility_records()
    }


def test_known_up_6_0_threshold_is_preserved():
    record = records_by_slot()[("up", (6, 0))]
    assert record.threshold_status == "DERIVED_CONDITIONAL"
    assert record.threshold_factor == Fraction(1, 2)
    assert record.operator_insertion == "ln 2"
    evidence = threshold.evidence_for_slot("up", 1, (6, 0))
    assert evidence is not None
    assert evidence.subspace_dimension == 2
    assert evidence.projector_rank == 1
    assert evidence.source == "weak-double projection bridge"


def test_rank_projection_formula_and_ln2_insertion():
    factor = threshold.rank_projection_threshold_factor(1, 2)
    assert factor == Fraction(1, 2)
    assert threshold.operator_insertion_from_factor(factor) == "ln 2"
    assert math.isclose(-math.log(float(factor)), math.log(2.0))


def test_no_invented_thresholds_for_other_charged_slots():
    rows = records_by_slot()
    expected_no_source = (
        ("lepton", (1, 2)),
        ("lepton", (3, 3)),
        ("up", (8, 1)),
        ("down", (0, 3)),
        ("down", (4, 2)),
    )
    for key in expected_no_source:
        record = rows[key]
        assert record.threshold_status == "NO_THRESHOLD_SOURCE_FOUND"
        assert record.threshold_factor is None
        assert record.operator_insertion is None
        assert record.has_virtual_door_subspace is False
        assert record.has_sector_projector is False


def test_reference_slots_are_not_threshold_targets():
    for sector in kf.CHARGED_SECTORS:
        record = records_by_slot()[(sector, (0, 0))]
        assert record.slot == 0
        assert record.is_reference_slot is True
        assert record.threshold_status == "REFERENCE_SLOT_NOT_THRESHOLD_TARGET"
        assert record.threshold_factor is None
        assert record.operator_insertion is None


def test_generator_threshold_rules_are_cleanly_separated():
    assert kf.threshold_rule_status(kf.THRESHOLD_RULE_NONE) == "BASELINE_DIAGNOSTIC"
    assert kf.threshold_rule_status(kf.THRESHOLD_RULE_DERIVED_ONLY) == "DERIVED_CONDITIONAL_ONLY"
    assert kf.threshold_rule_status(kf.THRESHOLD_RULE_SYMBOLIC_OPEN) == (
        "ELIGIBILITY_TABLE_PRESENT_OPEN_SLOTS_SYMBOLIC"
    )
    assert kf.threshold_insertions(kf.THRESHOLD_RULE_NONE) == []
    assert kf.threshold_insertions(kf.THRESHOLD_RULE_DERIVED_ONLY) == [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "value": "ln 2",
            "source": "Z_virt^{u,2}=1/2 weak-double projection bridge",
            "operator_level": True,
        }
    ]


def test_threshold_none_and_derived_only_affect_only_up_middle_slot():
    bare = kf.minimal_K_f_for_rule("up", 1, kf.RULE_A_SINGLE_OPERATOR_TRACE)
    none = kf.dressed_K_u_for_rule(
        1,
        kf.RULE_A_SINGLE_OPERATOR_TRACE,
        kf.THRESHOLD_RULE_NONE,
    )
    derived = kf.dressed_K_u_for_rule(
        1,
        kf.RULE_A_SINGLE_OPERATOR_TRACE,
        kf.THRESHOLD_RULE_DERIVED_ONLY,
    )
    assert none == tuple(tuple(float(value) for value in row) for row in bare)
    assert derived[1][1] == none[1][1] + math.log(2.0)
    assert derived[0][0] == none[0][0]
    assert derived[2][2] == none[2][2]
    assert derived[0][1] == none[0][1]
    assert derived[1][2] == none[1][2]


def test_symbolic_open_threshold_rule_refuses_numeric_insertions():
    try:
        kf.threshold_insertions(kf.THRESHOLD_RULE_SYMBOLIC_OPEN)
    except ValueError as exc:
        assert "eligibility data but no extra numeric insertions" in str(exc)
    else:
        raise AssertionError("symbolic-open threshold rule should not emit numeric insertions")


def test_json_artifact_records_full_threshold_verdict():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == threshold.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["statuses"]["up_6_0_Zvirt_threshold"] == "DERIVED_CONDITIONAL"
    assert data["statuses"]["full_threshold_operator"] == "OPEN"
    assert data["statuses"]["numerical_closure"] == "OPEN"
    assert data["verdict"]["threshold_eligibility_verdict"] == (
        "ONLY_UP_6_0_THRESHOLD_DERIVED_CONDITIONAL"
    )
    assert data["verdict"]["known_derived_insertions"] == 1
    assert data["derived_operator_insertions"] == [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "insertion": "ln 2",
            "formula": "K_f -> K_f + [-ln(D_fi)] |i_f><i_f|",
            "status": "DERIVED_CONDITIONAL",
            "operator_level": True,
        }
    ]


def test_docs_status_backlog_preserve_threshold_boundaries():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        threshold.PUBLIC_STATUS,
        "full_threshold_operator_eligibility_v1",
        "threshold_rank_projection_rule",
        "up_6_0_Zvirt_threshold=DERIVED_CONDITIONAL",
        "up_8_1_threshold_source=NO_THRESHOLD_SOURCE_FOUND",
        "lepton_1_2_threshold_source=NO_THRESHOLD_SOURCE_FOUND",
        "lepton_3_3_threshold_source=NO_THRESHOLD_SOURCE_FOUND",
        "down_0_3_threshold_source=NO_THRESHOLD_SOURCE_FOUND",
        "down_4_2_threshold_source=NO_THRESHOLD_SOURCE_FOUND",
        "reference_slot_threshold_source=REFERENCE_SLOT_NOT_THRESHOLD_TARGET",
        "full_threshold_operator=OPEN",
        "numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined

    forbidden = (
        "new threshold factor derived",
        "full threshold operator proven",
        "numerical closure achieved",
        "official predictions updated",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_no_empirical_imports_in_threshold_modules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (Path(threshold.__file__), Path(kf.__file__))
    )
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
    )
    for item in blocked:
        assert item not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = threshold.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
