import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "src" / "bhsm_model.py"
EXPECTED_MODEL_SHA256 = "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b"


def test_hash_audited_model_has_explicit_lf_checkout_policy():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "src/bhsm_model.py text eol=lf" in attributes


def test_hash_audited_model_uses_canonical_lf_bytes():
    raw = MODEL.read_bytes()
    assert b"\r\n" not in raw
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_MODEL_SHA256


def test_existing_raw_byte_integrity_checks_are_not_skipped():
    for relative in (
        "tests/test_coordinate_method_benchmark.py",
        "tests/test_git_good_standing_policy.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert '"src/bhsm_model.py"' in source
        assert ".read_bytes()" in source
        assert "pytest.mark.skip" not in source
        assert "pytest.skip" not in source


def test_frozen_prediction_hashes_remain_unchanged():
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
