from pathlib import Path
import hashlib


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_prediction_files_unchanged_for_higgs_scalar_sprint():
    md = ROOT / "docs" / "frozen_predictions.md"
    js = ROOT / "docs" / "frozen_predictions.json"
    assert hashlib.sha256(md.read_bytes()).hexdigest().upper() == (
        "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439"
    )
    assert hashlib.sha256(js.read_bytes()).hexdigest().upper() == (
        "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17"
    )
