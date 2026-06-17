from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_prediction_files_are_not_changed_by_y0_axis_branch():
    assert (ROOT / "docs" / "frozen_predictions.md").exists()
    assert (ROOT / "docs" / "frozen_predictions.json").exists()
    assert "y0_axis" not in (ROOT / "docs" / "frozen_predictions.md").read_text().lower()
    assert "y0_axis" not in (ROOT / "docs" / "frozen_predictions.json").read_text().lower()
