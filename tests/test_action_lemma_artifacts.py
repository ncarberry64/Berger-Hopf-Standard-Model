import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_all_v2_1_action_lemma_artifacts_parse():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v2_1.json"))
    assert len(paths) == 8
    for path in paths:
        assert json.loads(path.read_text(encoding="utf-8"))

