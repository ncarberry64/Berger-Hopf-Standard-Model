from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/derive_n12_gate7_current_green_supplemental_midpoint_blocks.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("supplemental_midpoint_blocks", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_supplement_recovers_exactly_the_missing_unique_pairs() -> None:
    module = _module()
    assert module.NEW_PAIRS == 73 * 26 + 26 * 27 // 2 == 2249


def test_aggregate_reconstructs_symmetric_complement_block(tmp_path, monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(module, "WORK", tmp_path)
    recovered = tmp_path / "recovered.npz"
    np.savez(recovered, marker=np.asarray(1))
    recovered_sha = module._sha(recovered)
    fingerprint = "F" * 64
    completion = SimpleNamespace(
        retained_directions=np.zeros((99, 73)),
        complement_directions=np.zeros((99, 26)),
        frame_qr_diagonal=np.ones(74),
        coordinate_basis_residual=0.0,
        normal_frame_residual=0.0,
        full_basis_condition_2=1.0,
    )
    monkeypatch.setattr(module, "_load_geometry", lambda: {})
    monkeypatch.setattr(module, "_completion", lambda interval, geometry: (completion, recovered))
    monkeypatch.setattr(module, "_fingerprint", lambda: fingerprint)
    for row in range(26):
        cu = np.full((99, 73), row + 0.25)
        upper = np.empty((99, 26 - row))
        for offset in range(26 - row):
            upper[:, offset] = 100 * row + row + offset
        np.savez_compressed(
            module._row_path(0, row),
            interval=np.asarray(0), complement_row=np.asarray(row),
            complement_retained_row=cu,
            complement_complement_upper=upper,
            diagnostics=np.zeros(5),
            elapsed_seconds=np.asarray(1.0),
            shard_revision=np.asarray(module.SHARD_REVISION),
            campaign_fingerprint=np.asarray(fingerprint),
            recovered_shard_SHA256=np.asarray(recovered_sha),
        )
    result = module._aggregate_interval(0)
    with np.load(result) as source:
        cu = np.asarray(source["complement_retained"])
        cc = np.asarray(source["complement_complement"])
        assert int(source["evaluated_new_direction_pairs"]) == 2249
    assert cu.shape == (99, 26, 73)
    assert cc.shape == (99, 26, 26)
    np.testing.assert_array_equal(cc, cc.transpose(0, 2, 1))
    assert np.all(cu[:, 7] == 7.25)
    assert np.all(cc[:, 3, 11] == 311)

