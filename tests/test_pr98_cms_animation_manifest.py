import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets/pr98_cms_open_data_animation"


def test_pr98_animation_manifest_and_sample_are_pinned_and_compact():
    manifest = json.loads((ASSETS / "pr98_cms_sample_manifest.json").read_text(encoding="utf-8"))
    sample = json.loads((ASSETS / "pr98_cms_four_vector_sample.json").read_text(encoding="utf-8"))
    assert manifest["cern_open_data_record"] == 303
    assert manifest["doi"] == "10.7483/OPENDATA.CMS.4M97.3SQ9"
    assert manifest["merge_commit"] == "e20f4eb1cba6a0619cee27676fd3035028d8738e"
    assert manifest["unique_muon_four_vectors"] == 200000
    assert manifest["timed_workload_four_vectors"] == 2000000
    assert manifest["speedup_vs_vectorized_control"] == 3.225
    assert manifest["backward_error"] == "<2.4 machine-epsilon"
    assert manifest["ci_gate"] == "<128 machine-epsilon"
    assert manifest["sha256"] == "1ac3a44aa66562fa201882ac6e7fd550ac186df3586c0478095df4c77c529710"
    assert sample["vector_count"] == 128
    assert len(sample["vectors"]) == 128
    assert (ASSETS / "pr98_cms_four_vector_sample.json").stat().st_size < 100_000
    animation_path = ASSETS / "pr98_cms_engine_validation_continuous.gif"
    assert animation_path.stat().st_size < 2_000_000
    with Image.open(animation_path) as animation:
        assert animation.n_frames >= 28
        assert animation.size == (900, 500)
        durations = []
        for index in range(animation.n_frames):
            animation.seek(index)
            durations.append(animation.info["duration"])
        assert max(durations) <= 120
    assert ET.parse(ASSETS / "pr98_cms_engine_validation.svg").getroot().tag.endswith("svg")


def test_pr98_animation_does_not_change_frozen_predictions():
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
