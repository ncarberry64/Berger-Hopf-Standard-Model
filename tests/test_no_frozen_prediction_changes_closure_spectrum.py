import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_unchanged_for_closure_spectrum_gate():
    assert _sha256(ROOT / "docs" / "frozen_predictions.md") == (
        "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439"
    )
    assert _sha256(ROOT / "docs" / "frozen_predictions.json") == (
        "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17"
    )
