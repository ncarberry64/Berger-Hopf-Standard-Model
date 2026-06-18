from pathlib import Path
import hashlib


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_prediction_files_unchanged_for_one_loop_rg_sprint():
    md = ROOT / "docs" / "frozen_predictions.md"
    js = ROOT / "docs" / "frozen_predictions.json"

    assert hashlib.sha256(md.read_bytes()).hexdigest().upper() == (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    )
    assert hashlib.sha256(js.read_bytes()).hexdigest().upper() == (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    )
