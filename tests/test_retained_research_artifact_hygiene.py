"""An explicit retention record must never exempt changed or new large data."""
import hashlib
import json

from tools import audit_public_readiness as audit


def test_retention_requires_exact_bytes_and_does_not_admit_unlisted_files(tmp_path, monkeypatch):
    path = tmp_path / "artifacts/retained.npz"
    path.parent.mkdir()
    path.write_bytes(b"reviewed research array")
    registry = tmp_path / "data/retained_large_research_artifacts.json"
    registry.parent.mkdir()
    registry.write_text(json.dumps({"artifacts": [{
        "path": "artifacts/retained.npz",
        "canonical_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }]}), encoding="utf-8")
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "LARGE_FILE_THRESHOLD", 1)
    monkeypatch.setattr(audit, "tracked_files", lambda: ["artifacts/retained.npz"])
    assert audit.check_hygiene()["passed"]
    path.write_bytes(b"different research data")
    assert not audit.check_hygiene()["passed"]
    path.write_bytes(b"reviewed research array")
    extra = tmp_path / "artifacts/unreviewed.npz"
    extra.write_bytes(b"unreviewed")
    monkeypatch.setattr(audit, "tracked_files", lambda: ["artifacts/retained.npz", "artifacts/unreviewed.npz"])
    assert not audit.check_hygiene()["passed"]
