from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_collective_curvature_threshold import build_results_payload  # noqa: E402


FORBIDDEN_OVERCLAIMS = [
    "dark matter is solved",
    "particle dark matter is disproven",
    "introduces a new official mass formula",
    "is an official mass formula",
    "official dark-matter claim",
    "numerical closure achieved",
    "fully proven",
]


def _candidate_text() -> str:
    paths = [
        ROOT / "theory" / "collective_curvature_threshold_layer.md",
        ROOT / "theory" / "collective_curvature_mass_engine_bridge.md",
        ROOT / "theory" / "collective_curvature_dark_matter_interpretation.md",
        ROOT / "theory" / "collective_curvature_threshold_results.json",
    ]
    return "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)


def test_candidate_only_hygiene_and_no_official_formula() -> None:
    payload = build_results_payload()
    assert payload["status"] == "candidate_only"
    assert payload["candidate_layer"]["official"] is False
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False


def test_forbidden_overclaims_absent() -> None:
    text = _candidate_text()
    for phrase in FORBIDDEN_OVERCLAIMS:
        assert phrase not in text


def test_guardrails_are_explicit() -> None:
    payload = build_results_payload()
    guardrails = payload["guardrails"]
    assert guardrails["does_not_claim_dark_matter_solved"] is True
    assert guardrails["does_not_disprove_particle_dark_matter"] is True
    assert guardrails["does_not_change_official_predictions"] is True
    assert guardrails["requires_empirical_gravity_tests"] is True
    assert "galaxy rotation curves" in guardrails["future_empirical_tests"]
    assert "CMB consistency" in guardrails["future_empirical_tests"]


def test_no_sector_or_per_particle_tuning_language_in_payload() -> None:
    serialized = json.dumps(build_results_payload()).lower()
    assert "per-particle" not in serialized
    assert "sector-specific parameter" not in serialized
    assert "official\": true" not in serialized
