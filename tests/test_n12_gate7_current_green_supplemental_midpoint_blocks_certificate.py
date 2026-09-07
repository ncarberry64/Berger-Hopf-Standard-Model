from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/certify_n12_gate7_current_green_supplemental_midpoint_blocks.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("supplemental_blocks_certificate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_aggregate_validator_accepts_only_complete_symmetric_blocks(tmp_path) -> None:
    module = _module()
    path = tmp_path / "midpoint_000.npz"
    values = {
        "interval": np.asarray(0),
        "shard_revision": np.asarray(module.supplement.SHARD_REVISION),
        "campaign_fingerprint": np.asarray("F" * 64),
        "recovered_shard_SHA256": np.asarray("R" * 64),
        "evaluated_new_direction_pairs": np.asarray(2249),
        "complement_retained": np.zeros((99, 26, 73)),
        "complement_complement": np.zeros((99, 26, 26)),
        "retained_directions": np.zeros((99, 73)),
        "complement_directions": np.zeros((99, 26)),
        "frame_qr_diagonal": np.ones(74),
        "row_diagnostics": np.zeros((26, 5)),
        "row_elapsed_seconds": np.ones(26),
        "coordinate_basis_residual": np.asarray(0.0),
        "normal_frame_residual": np.asarray(0.0),
        "full_basis_condition_2": np.asarray(1.0),
    }
    np.savez_compressed(path, **values)
    assert module._valid_aggregate(path, 0, "F" * 64, "R" * 64)
    values["complement_complement"][0, 0, 1] = 1.0
    np.savez_compressed(path, **values)
    assert not module._valid_aggregate(path, 0, "F" * 64, "R" * 64)


@pytest.mark.parametrize("changed", [
    "complement_retained", "complement_complement", "row_diagnostics",
    "row_elapsed_seconds",
])
def test_certificate_rejects_aggregate_that_disagrees_with_valid_rows(tmp_path, changed):
    """Individually well-formed caches must also describe the same calculation."""
    module = _module()
    rng = np.random.default_rng(20260906)
    cu = rng.normal(size=(99, 26, 73))
    cc = rng.normal(size=(99, 26, 26))
    cc = cc + cc.transpose(0, 2, 1)
    diagnostics = np.abs(rng.normal(size=(26, 5)))
    elapsed = np.arange(1.0, 27.0)
    rows = []
    for row in range(26):
        path = tmp_path / f"row_{row:02d}.npz"
        np.savez_compressed(
            path, complement_retained_row=cu[:, row],
            complement_complement_upper=cc[:, row, row:],
            diagnostics=diagnostics[row], elapsed_seconds=elapsed[row],
        )
        rows.append(path)
    values = dict(complement_retained=cu, complement_complement=cc,
                  row_diagnostics=diagnostics, row_elapsed_seconds=elapsed)
    aggregate = tmp_path / "midpoint_000.npz"
    np.savez_compressed(aggregate, **values)
    assert module._aggregate_matches_rows(aggregate, rows)
    assert not module._aggregate_matches_rows(aggregate, rows[:-1])
    values[changed].flat[0] += 1.0
    np.savez_compressed(aggregate, **values)
    assert not module._aggregate_matches_rows(aggregate, rows)
