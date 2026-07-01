import hashlib
import json
from pathlib import Path

from bhsm.interface.ckm_bidirectional_channel import build_ckm_bidirectional_channel_report


ROOT = Path(__file__).resolve().parents[1]
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_bidirectional_report_preserves_claim_and_frozen_boundaries():
    report = build_ckm_bidirectional_channel_report()
    assert report["status"] == "CONDITIONAL_HERMITIAN_BIDIRECTIONAL_CKM_CHANNEL_CANDIDATE"
    assert report["frozen_predictions_modified"] is False
    assert report["official_prediction_logic_modified"] is False
    assert report["physics_validation_claimed"] is False
    assert report["full_completion_claimed"] is False
    for relative, expected in FROZEN_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


def test_bidirectional_artifacts_parse_without_empirical_inputs():
    paths = sorted((ROOT / "artifacts").glob("BHSM_ckm_*_v2_3.json"))
    assert len(paths) == 6
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload
        assert '"empirical_inputs_used": true' not in path.read_text(encoding="utf-8").lower()
