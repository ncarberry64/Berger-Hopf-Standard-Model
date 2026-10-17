"""An explicit retention record must never exempt changed or new large data."""
import hashlib
import json
from pathlib import Path

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


def test_muon_first_order_retention_preserves_exact_historical_evidence():
    root = Path(__file__).resolve().parents[1]
    relative = "artifacts/muon_first_order_complement_20261006/run_2/first_order_compact_reduction.npz"
    registry = json.loads((root / "data/retained_large_research_artifacts.json").read_text(encoding="utf-8"))
    rows = [row for row in registry["artifacts"] if row["path"] == relative]
    assert len(rows) == 1
    retained = rows[0]
    payload = (root / relative).read_bytes()
    assert retained["canonical_bytes"] == len(payload) == 11125650
    assert retained["sha256"] == hashlib.sha256(payload).hexdigest() == "f35ae512a03639ccc887bdeead0350a8cdec147b15db5b66ed6f94da794bfdb2"
    historical = json.loads((root / "artifacts/muon_first_order_complement_20261006/run_2/output_hashes.json").read_text(encoding="utf-8"))
    assert retained["sha256"] == historical["first_order_compact_reduction.npz"]
    assert retained["classification"] == "HISTORICAL_SCIENTIFIC_EVIDENCE"
    assert retained["artifact_regenerated"] is False
    assert retained["consumed_as_new_physical_data"] is False
    assert (root / retained["retention_review"]).is_file()
