import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_effective_bridge_balance as charged_bridge
import incidence_normalized_overlap_bridge as bridge
import neutral_bridge_pmns_source as neutral_bridge


FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_unified_rule_neutral_and_charged_exact_values():
    assert bridge.neutral_bridge_source().bridge_seed == Fraction(1, 3)
    assert bridge.charged_bridge_source().bridge_seed == Fraction(16, 189)
    assert bridge.bridge_seed(Fraction(21), Fraction(4, 3)) == Fraction(16, 189)
    assert Fraction(16, 189) == Fraction(1, 21) * Fraction(4, 3) ** 2
    assert bridge.bridge_ratio_charged_to_neutral() == Fraction(16, 63)


def test_new_rule_matches_existing_charged_and_neutral_bridge_records():
    assert bridge.charged_bridge_source().bridge_seed == charged_bridge.g_bridge()
    assert bridge.charged_bridge_source().bridge_seed == charged_bridge.g_bridge_factorization()
    assert bridge.neutral_bridge_source().bridge_seed == neutral_bridge.G_NU
    assert bridge.neutral_bridge_source().bridge_seed == neutral_bridge.diagnostic().g_nu


def test_charged_overlap_metadata_remains_open_localizable():
    metadata = bridge.charged_overlap_metadata()
    assert metadata.charged_overlap_factor == Fraction(4, 3)
    assert metadata.motivation == "down Hopf multiplier 4 divided by rank-three closure 3"
    assert metadata.action_source_status == "OPEN_LOCALIZABLE"
    assert bridge.STATUS_TABLE["charged_overlap_4_over_3_action_source"] == "OPEN_LOCALIZABLE"


def test_statuses_do_not_claim_numerical_closure():
    report = bridge.report_as_dict()
    assert report["public_status"] == bridge.PUBLIC_STATUS
    assert report["public_status"] == (
        "structural architecture integrated conditional; numerical closure open"
    )
    assert report["frozen_predictions_changed"] is False
    assert report["official_predictions_changed"] is False
    assert report["statuses"]["incidence_normalized_overlap_bridge_rule"] == (
        "PARTIALLY_LOCALIZED"
    )
    assert report["statuses"]["full_numerical_closure"] == "OPEN"
    assert report["numerical_closure"] == "OPEN"


def test_json_report_matches_module_report():
    report_path = ROOT / "data" / "incidence_normalized_overlap_bridge_source.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))
    report = bridge.report_as_dict()
    assert data["public_status"] == report["public_status"]
    assert data["unified_rule"] == report["unified_rule"]
    assert data["neutral"]["bridge_seed"] == "1/3"
    assert data["charged"]["bridge_seed"] == "16/189"
    assert data["charged"]["overlap_action_source"] == "OPEN_LOCALIZABLE"
    assert data["bridge_ratio_charged_to_neutral"] == "16/63"


def test_no_empirical_input_fixture_introduced():
    text = Path(bridge.__file__).read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "observed_mass",
        "CKM data",
        "PMNS data",
        "neutrino data",
        "empirical target",
        "measured alpha",
    )
    for item in blocked:
        assert item not in text


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
