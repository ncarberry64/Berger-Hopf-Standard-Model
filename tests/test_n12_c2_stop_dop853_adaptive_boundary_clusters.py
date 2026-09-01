"""Checks for the exact mixed-resolution DOP853 Bernstein spectrum cover."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COARSE = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_DOP853_BOUNDARY_CLUSTER_SPECTRUM.json"
ADAPTIVE = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BOUNDARY_CLUSTER_SPECTRUM.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_coarse_replay_localizes_only_the_stronger_bootstrap_failure() -> None:
    payload = load(COARSE)
    rows = payload["rows"]
    failed = [row for row in rows if not row["boundary_cluster_certificate_closed"]]
    assert payload["validation_passed"] is False
    assert len(rows) == 1480
    assert len(failed) == 242
    assert {row["interval"] for row in failed} == set(range(68, 129))
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(
        row["negative_selected_gap_lower"] > 0.0
        and row["selected_positive_gap_lower"] > 0.0
        for row in rows
    )
    assert any(not row["all_three_quarter_gap_bootstraps_closed"] for row in rows)


def test_adaptive_cover_is_exact_closed_and_uses_the_same_dense_polynomial() -> None:
    payload = load(ADAPTIVE)
    assert payload["validation_passed"] is True
    assert payload["unresolved_cells"] == []
    assert payload["mesh"]["accepted_cover_cell_count"] == 1722
    assert payload["mesh"]["accepted_cover_cells_by_subdivisions"] == {
        "4": 1238,
        "8": 484,
    }
    assert payload["mesh"]["coarse_cells_replaced"] == 242
    assert payload["mesh"]["refinement_cells_audited_by_subdivisions"] == {
        "4": 1480,
        "8": 484,
    }
    assert payload["summary"]["minimum_selected_line_boundary_gap_lower"] > 0.0
    assert payload["claim_boundary"]["selected_line_on_stored_DOP853_stop_path"] == "CERTIFIED_SIMPLE"
    assert payload["validation"]["quarter_gap_bootstrap_not_weakened"] is True
    assert payload["validation"]["no_cubic_Hermite_surrogate_inserted"] is True


def test_adaptive_rows_partition_each_dense_interval_without_gaps() -> None:
    rows = load(ADAPTIVE)["rows"]
    grouped: dict[int, list[tuple[Fraction, Fraction]]] = defaultdict(list)
    for row in rows:
        numerator = int(row["subspan"])
        denominator = int(row["subdivisions"])
        grouped[int(row["interval"])].append((
            Fraction(numerator, denominator),
            Fraction(numerator + 1, denominator),
        ))
        assert row["Bernstein_control_count"] == 8
        assert row["selected_branch"] == 24
        assert row["all_three_quarter_gap_bootstraps_closed"] is True
        assert row["boundary_cluster_certificate_closed"] is True
    assert set(grouped) == set(range(370))
    for spans in grouped.values():
        spans.sort()
        assert spans[0][0] == 0
        assert spans[-1][1] == 1
        assert all(left[1] == right[0] for left, right in zip(spans, spans[1:]))


def test_adaptive_input_hashes_match_current_disk() -> None:
    payload = load(ADAPTIVE)
    for relative, expected in payload["inputs"].items():
        assert normalized_sha256(ROOT / relative) == expected
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["FLAGSHIP_READY"] is False
