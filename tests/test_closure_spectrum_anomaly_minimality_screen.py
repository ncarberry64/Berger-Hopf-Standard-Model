import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_closure_spectrum_selection import anomaly_minimality_status  # noqa: E402


def test_anomaly_minimality_recognizes_minimal_ingredients():
    assert anomaly_minimality_status(1) == "minimal_leptonic_single_channel_ingredient"
    assert anomaly_minimality_status(2) == "minimal_weak_orientation_pair_ingredient"
    assert anomaly_minimality_status(3) == "minimal_three_channel_charge_anomaly_ingredient"
    assert anomaly_minimality_status(4) == "composite_not_needed_for_minimal_charge_anomaly_bridge"
    assert anomaly_minimality_status(5) == "higher_prime_unsupported_by_current_charge_anomaly_minimality"


def test_anomaly_minimality_doc():
    text = (ROOT / "theory" / "closure_spectrum_anomaly_minimality_screen.md").read_text()
    assert "one leptonic/single-channel closure" in text
    assert "one weak two-orientation active interface" in text
    assert "one three-channel active/quark-like closure" in text
    assert "This is not a proof of uniqueness" in text
