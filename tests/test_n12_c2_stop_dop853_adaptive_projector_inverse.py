"""Checks for the projector and bordered inverse on the exact DOP853 cover."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
SPECTRUM = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"
PROJECTOR = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_SELECTED_PROJECTOR_GRAPH.json"
INVERSE = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_HARD_INVERSE.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def keys(payload: dict) -> list[tuple[int, int, int]]:
    return [
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"]))
        for row in payload["rows"]
    ]


def test_projector_consumes_the_exact_adaptive_spectrum_cover() -> None:
    spectrum = load(SPECTRUM)
    projector = load(PROJECTOR)
    assert projector["validation_passed"] is True
    assert keys(projector) == keys(spectrum)
    assert len(projector["rows"]) == 1722
    assert all(row["selected_branch"] == 24 for row in projector["rows"])
    assert all(row["graph_Neumann_closed"] is True for row in projector["rows"])
    assert projector["summary"]["maximum_selected_projector_motion_upper"] == 0.26738491116648233
    assert projector["summary"]["maximum_selected_projector_motion_upper"] < 1.0
    assert projector["validation"]["no_cubic_Hermite_surrogate_inserted"] is True


def test_bordered_inverse_is_analytical_and_finite_on_every_cell() -> None:
    spectrum = load(SPECTRUM)
    projector = load(PROJECTOR)
    inverse = load(INVERSE)
    assert inverse["validation_passed"] is True
    assert keys(inverse) == keys(projector) == keys(spectrum)
    for spectral, graph, row in zip(
        spectrum["rows"], projector["rows"], inverse["rows"]
    ):
        gap = min(
            float(spectral["negative_selected_gap_lower"]),
            float(spectral["selected_positive_gap_lower"]),
        )
        motion = float(graph["selected_projector_motion_upper"])
        assert row["bordered_dimension"] == 62
        assert row["hard_dimension"] == 60
        assert row["bordered_inverse_closed"] is True
        assert math.isclose(
            row["instantaneous_bordered_inverse_2_norm_upper"],
            max(1.0, 1.0 / gap), rel_tol=2.0e-10,
        )
        assert math.isclose(
            row["center_chart_condition_factor_upper"],
            (1.0 + motion) / (1.0 - motion), rel_tol=2.0e-10,
        )
    assert inverse["summary"]["minimum_selected_to_hard_gap_lower"] == 1.6382875139534257e-07
    assert inverse["validation"]["no_full_kinetic_Dirac_or_history_inverse_used"] is True


def test_projector_and_inverse_input_hashes_match_disk() -> None:
    for payload in (load(PROJECTOR), load(INVERSE)):
        for relative, expected in payload["inputs"].items():
            assert normalized_sha256(ROOT / relative) == expected
        assert payload["FULL_BHSM_COMPLETE"] is False
        assert payload["FLAGSHIP_READY"] is False
