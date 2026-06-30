from __future__ import annotations

import hashlib
import json
import zlib
from pathlib import Path

import numpy as np

from bhsm.interface.benchmarks.cern_open_data import (
    REAL_DATA_STATUS,
    load_cms_dimuon_vectors,
    load_manifest,
    verify_download,
)
from bhsm.interface.benchmarks.cern_open_data_benchmark import build_report


ROOT = Path(__file__).resolve().parents[1]
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def _fixture(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    source = tmp_path / "dimuon.csv"
    source.write_text(
        "Type,Run,Event,E1,px1 ,py1,pz1,pt1,eta1,phi1,Q1,E2,px2,py2,pz2,pt2,eta2,phi2,Q2,M\n"
        "GG,1,2,5,3,4,0,5,0,0,-1,13,0,5,12,5,0,0,1,18\n"
        "GT,1,3,10,0,0,10,0,0,0,-1,2,1,0,0,1,0,0,1,12\n",
        encoding="utf-8",
    )
    raw = source.read_bytes()
    manifest = {
        "record_id": 303,
        "title": "fixture",
        "doi": "10.7483/OPENDATA.CMS.4M97.3SQ9",
        "record_url": "https://opendata.cern.ch/record/303",
        "license": "CC0-1.0",
        "benchmark_scope": "test",
        "file": {
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "portal_checksum": f"adler32:{zlib.adler32(raw) & 0xFFFFFFFF:08x}",
        },
    }
    return source, manifest


def test_manifest_records_cern_provenance_and_scope() -> None:
    manifest = load_manifest(ROOT / "data/manifests/cms_open_data_dimuon_2010.json")
    assert manifest["record_id"] == 303
    assert manifest["doi"] == "10.7483/OPENDATA.CMS.4M97.3SQ9"
    assert manifest["license"] == "CC0-1.0"
    assert "not track reconstruction" in manifest["benchmark_scope"]


def test_loader_verifies_checksums_and_extracts_two_four_vectors(tmp_path: Path) -> None:
    source, manifest = _fixture(tmp_path)
    verify_download(source, manifest)
    vectors = load_cms_dimuon_vectors(source, manifest)
    assert vectors.event_count == 2
    assert vectors.vector_count == 4
    np.testing.assert_allclose(vectors.states[0], [5.0, 3.0, 4.0, 0.0])
    np.testing.assert_allclose(vectors.states[3], [2.0, 1.0, 0.0, 0.0])


def test_real_data_report_is_equivalent_and_claim_bounded(tmp_path: Path) -> None:
    source, manifest = _fixture(tmp_path)
    vectors = load_cms_dimuon_vectors(source, manifest)
    report = build_report(
        vectors.states, manifest, vectors.source_sha256, repeats=1, replication_factor=2
    )
    assert report["status"] == REAL_DATA_STATUS
    assert report["configuration"]["unique_four_vector_count"] == 4
    assert report["configuration"]["processed_four_vectors_per_pass"] == 8
    assert report["correctness"]["all_kernels_equivalent"] is True
    assert report["correctness"]["scale_aware_float64_consistency"]["all_within_bound"] is True
    assert "not track fitting or track reconstruction" in report["claim_boundaries"]


def test_frozen_predictions_remain_byte_identical() -> None:
    for relative, expected in FROZEN_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected
