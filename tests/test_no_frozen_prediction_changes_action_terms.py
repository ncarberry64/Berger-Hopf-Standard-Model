import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_unchanged_for_action_term_realization_audit():
    assert _sha256(ROOT / "docs" / "frozen_predictions.md") == (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    )
    assert _sha256(ROOT / "docs" / "frozen_predictions.json") == (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    )

