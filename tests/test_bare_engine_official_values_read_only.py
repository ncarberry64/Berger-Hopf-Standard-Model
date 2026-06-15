from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_engine_triangulation import build_payload, engine_comparison  # noqa: E402


def test_engine_comparison_shows_existing_engine_closer_for_current_rows() -> None:
    rows = engine_comparison(ROOT)
    assert len(rows) == 6
    assert all(row.which_engine_is_closer == "existing_bare" for row in rows)
    assert any(row.scheme_sensitive for row in rows if row.sector in {"up", "down"})


def test_official_frozen_values_match_read_only_docs() -> None:
    frozen = json.loads((ROOT / "docs" / "frozen_predictions.json").read_text())
    rows = {row.ratio_name: row for row in engine_comparison(ROOT)}
    for ratio in ("c/t", "u/t", "s/b", "d/b"):
        assert rows[ratio].official_or_existing_bare_prediction == frozen["outputs"][ratio]["bare"]
        assert (
            rows[ratio].official_or_existing_dressed_candidate_prediction
            == frozen["outputs"][ratio]["dressed_candidate"]
        )


def test_quark_scheme_warnings_are_preserved_in_comparison_and_notes() -> None:
    payload = build_payload(ROOT)
    quark_rows = [row for row in payload["engine_comparison"] if row["sector"] in {"up", "down"}]
    assert quark_rows
    assert all(row["scheme_sensitive"] is True for row in quark_rows)
    assert "quark ratios are scheme-sensitive where applicable" in payload["notes"]


def test_spectral_action_is_not_existing_engine() -> None:
    payload = build_payload(ROOT)
    summary = payload["missing_invariant_diagnostics"]["summary"]
    assert summary["closer_counts"]["existing_bare"] == 6
    assert summary["spectral_action_closer_count"] == 0
    assert "SPECTRAL_ACTION_NOT_EXISTING_ENGINE" in payload["verdict_labels"]
