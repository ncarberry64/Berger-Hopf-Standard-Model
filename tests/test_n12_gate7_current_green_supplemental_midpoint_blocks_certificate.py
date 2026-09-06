from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


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

