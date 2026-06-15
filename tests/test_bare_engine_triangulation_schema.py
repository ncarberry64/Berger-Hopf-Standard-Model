from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_engine_triangulation import (  # noqa: E402
    ALLOWED_VERDICTS,
    BRANCH,
    build_payload,
    export_outputs,
)


def test_triangulation_results_schema_and_allowed_labels() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "bare_engine_triangulation_results.json").read_text())

    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert set(parsed["inputs"]) == {
        "frozen_predictions_source",
        "spectral_action_source",
        "reference_ratio_source",
    }
    assert parsed["engine_comparison"]
    assert set(parsed["missing_invariant_diagnostics"]) == {
        "mode_invariants",
        "correlations",
        "summary",
    }
    assert parsed["candidate_invariant_families"]
    assert set(parsed["verdict_labels"]) <= ALLOWED_VERDICTS
    assert payload["verdict_labels"] == parsed["verdict_labels"]


def test_required_reports_exist_and_are_candidate_only() -> None:
    export_outputs(ROOT)
    paths = [
        ROOT / "theory" / "bare_engine_triangulation_audit.md",
        ROOT / "theory" / "bare_engine_triangulation_results.json",
        ROOT / "theory" / "bare_engine_missing_invariant_candidates.md",
    ]
    for path in paths:
        assert path.exists()
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths if path.suffix == ".md")
    assert "candidate-only" in text
    assert "no new official mass formula" in text
    assert "not upgraded to derived" in text
    assert "derived full standard model" not in text


def test_payload_records_read_only_ckm_entry_without_using_it_for_mass_fit() -> None:
    payload = build_payload(ROOT)
    ckm = payload["read_only_ckm_entries"]
    assert ckm["source"] == "docs/frozen_predictions.json"
    assert ckm["used_in_mass_engine_fit"] is False
    assert ckm["sin_theta_13"]["changed"] is False
