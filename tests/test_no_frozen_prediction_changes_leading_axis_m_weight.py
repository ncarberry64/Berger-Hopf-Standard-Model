from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_prediction_files_are_not_changed_by_leading_axis_branch():
    assert (ROOT / "docs" / "frozen_predictions.md").exists()
    assert (ROOT / "docs" / "frozen_predictions.json").exists()
    assert "leading_axis" not in (ROOT / "docs" / "frozen_predictions.md").read_text().lower()
    assert "leading_axis" not in (ROOT / "docs" / "frozen_predictions.json").read_text().lower()
