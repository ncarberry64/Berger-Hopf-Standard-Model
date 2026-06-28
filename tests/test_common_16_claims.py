from pathlib import Path

from bhsm.interface.common_16 import REQUIRED_STATEMENTS, build_final_completion_report


ROOT = Path(__file__).resolve().parents[1]


def test_required_claim_boundaries_are_documented() -> None:
    text = (ROOT / "docs/common_16_closure_report.md").read_text(encoding="utf-8")
    for statement in REQUIRED_STATEMENTS:
        assert statement in text


def test_common_16_report_does_not_claim_completion() -> None:
    report = build_final_completion_report()
    assert report.completion_claimed is False
    assert report.empirical_inputs_used is False
    assert report.frozen_predictions_changed is False
    assert report.official_prediction_logic_changed is False
