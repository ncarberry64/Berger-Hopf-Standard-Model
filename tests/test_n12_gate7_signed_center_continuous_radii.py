import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import certify_n12_gate7_signed_center_continuous_radii as report


@pytest.fixture
def fixture(monkeypatch, tmp_path):
    monkeypatch.setattr(report, "ROOT", tmp_path)
    for name in ("cert.py", "producer.py", "helper.py", "theory.md"):
        (tmp_path / name).write_bytes(b"source\r\n")
    monkeypatch.setattr(report, "__file__", str(tmp_path / "producer.py"))
    monkeypatch.setattr(report, "THEORY", tmp_path / "theory.md")
    monkeypatch.setattr(report, "radii", SimpleNamespace(
        __file__=str(tmp_path / "helper.py"),
        continuous_two_radius_screen=report.radii.continuous_two_radius_screen))
    np.savez(tmp_path / "endpoint.npz", independent_signed_descriptors=np.array([1.]))
    (tmp_path / "center.npz").write_bytes(b"center data")
    center = SimpleNamespace(
        RESULT=tmp_path / "center.json", DATA=tmp_path / "center.npz",
        ENDPOINT=tmp_path / "endpoint.json",
        cert=SimpleNamespace(__file__=str(tmp_path / "cert.py"), TRIAL_DESCRIPTOR_SCALE=1.))
    monkeypatch.setattr(report, "center", center)
    record = {
        "status": "SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED", "validation_passed": True,
        "validation": {"complete_midpoint_UU_CU_UC_CC_blocks_included": True},
        "inputs": {name: report._sha(tmp_path/name) for name in ("endpoint.npz", "cert.py")},
        "data_SHA256": report._sha(center.DATA),
        "coefficients": {"Y": [.1, .1], "Z1": [[0., 0.], [0., 0.]],
                         "central_quadratic": [0., 0.], "mixed_quadratic": [0., 0.],
                         "signed_transverse_quadratic_center": [0., 0.]},
        "screen": {"positive_self_map_found": False},
    }
    center.RESULT.write_text(json.dumps(record), encoding="utf-8")
    return center, record


def test_complete_report_is_deterministic_and_preserves_original(fixture):
    center, _ = fixture
    original = center.RESULT.read_bytes()
    first = report.build_payload()
    second = report.build_payload()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert center.RESULT.read_bytes() == original
    assert first["continuous_adjudication"]["status"] == "STORED_POLYNOMIAL_SELF_MAP"
    assert first["retained_grid_screen"]["positive_self_map_found"] is False
    assert not first["FULL_BHSM_COMPLETE"]


def test_incomplete_midpoint_chain_is_rejected(fixture):
    center, record = fixture
    record["validation"]["complete_midpoint_UU_CU_UC_CC_blocks_included"] = False
    center.RESULT.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(RuntimeError, match="complete validated"):
        report.build_payload()


@pytest.mark.parametrize("name", ["endpoint.npz", "cert.py", "center.npz"])
def test_changed_center_or_ceiling_provenance_is_rejected(fixture, name):
    center, _ = fixture
    (center.RESULT.parent / name).write_bytes(b"changed")
    with pytest.raises(RuntimeError, match="changed"):
        report.build_payload()


def test_text_hash_matches_center_normalization(fixture):
    center, _ = fixture
    path = Path(center.cert.__file__)
    before = report._sha(path)
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    assert report._sha(path) == before
