import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_all_v1_9_artifacts_parse_and_remain_claim_bounded():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v1_9.json"))
    assert len(paths) >= 10
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload
        text = json.dumps(payload).lower()
        assert "experimentally confirmed" not in text
        assert "detector reconstruction validated" not in text


def test_frozen_prediction_hashes_are_unchanged():
    for relative, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected

