"""Focused norm, cover and restart checks for the current RHS insertion."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import certify_n12_current_dop853_bordered_rhs_response as current


def _row(interval: int, subspan: int, subdivisions: int) -> dict:
    return dict(interval=interval, subspan=subspan, subdivisions=subdivisions)


def test_partition_rejects_holes_overlaps_and_missing_intervals() -> None:
    good = [_row(0, 0, 2), _row(0, 1, 2), _row(1, 0, 1)]
    assert current._partition_is_exact(good, 2)
    assert not current._partition_is_exact(good[:-1], 2)
    assert not current._partition_is_exact(good + [_row(0, 0, 4)], 2)
    assert not current._partition_is_exact([_row(0, 0, 4), _row(0, 2, 4), _row(0, 3, 4)], 1)


def test_uniform_inverse_bound_controls_source_motion_without_neumann() -> None:
    # A changing orthogonal eigensystem has norm(inv K)=4 regardless of a
    # fixed-center relative perturbation diagnostic; source triangle bound
    # controls every such orthogonal rotation without a Neumann assumption.
    source_center = np.array([2.0, -3.0])
    variation = np.array([0.2, 0.4])
    source_cap, response_cap = current._finite_cap(np.linalg.norm(source_center), np.linalg.norm(variation), 4.0)
    for angle in np.linspace(0, 2 * np.pi, 21):
        c, s = np.cos(angle), np.sin(angle)
        rotation = np.array([[c, -s], [s, c]])
        inverse = rotation @ np.diag([4.0, -0.5]) @ rotation.T
        source = source_center + np.sin(angle) * variation
        assert np.linalg.norm(source) <= source_cap
        assert np.linalg.norm(inverse @ source) <= response_cap
    with pytest.raises(ValueError):
        current._finite_cap(1.0, float("inf"), 4.0)


def test_checkpoint_resume_preserves_rows_and_rejects_stale_binding(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    inputs = {"center.npz": "CENTER", "script.py": "CODE"}
    row = _row(0, 0, 4)
    path.write_text(json.dumps({"inputs": inputs}) + "\n" + json.dumps({"row": row}) + "\n" + '{"row":', encoding="utf-8")
    keys = [(0, 0, 4), (0, 1, 4)]
    restored = current._load_checkpoint(path, inputs, keys)
    assert restored == {(0, 0, 4): row}
    assert path.read_bytes().endswith(b"\n")
    assert path.with_suffix(".jsonl.interrupted-line.txt").read_text() == '{"row":'
    second = _row(0, 1, 4)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"row": second}) + "\n")
    assert current._load_checkpoint(path, inputs, keys) == {(0, 0, 4): row, (0, 1, 4): second}
    with pytest.raises(ValueError, match="binding"):
        current._load_checkpoint(path, {"center.npz": "STALE"}, [(0, 0, 4)])


def test_checkpoint_rejects_an_alien_cell(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text(json.dumps({"inputs": {}}) + "\n" + json.dumps({"row": _row(0, 1, 4)}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="alien"):
        current._load_checkpoint(path, {}, [(0, 0, 4)])


def test_current_tangent_remainder_enclosure_has_the_spectral_center() -> None:
    config = {"inverse": str(current.DEFAULT_INVERSE), "projector": str(current.DEFAULT_PROJECTOR), "center": str(current.DEFAULT_CENTER)}
    current._initialize(config)
    geometry = current._same_center_tangent_geometry(182, 2, 4)
    *_, weights, __, ___, ____ = current.response.dense._dense_arrays()
    controls = geometry["Bezier_controls"]
    np.testing.assert_array_equal(geometry["midpoint"], np.mean(controls, axis=0) / weights)
    assert abs(geometry["coefficient_ellipsoid_identity"] - 1) <= 4e-15
    projection = geometry["projection"]
    center = np.mean(controls, axis=0)
    import math
    for u in np.linspace(0, 1, 21):
        curve = sum(math.comb(7, i) * u**i * (1 - u)**(7 - i) * controls[i] for i in range(8))
        coefficients, *_ = np.linalg.lstsq(projection, curve - center, rcond=None)
        assert np.linalg.norm(projection @ coefficients - (curve - center)) < 2e-12
        assert np.linalg.norm(coefficients) <= 1 + 1e-8
