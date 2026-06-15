from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dark_matter_interpretation_is_candidate_only() -> None:
    text = (
        ROOT / "theory" / "collective_curvature_dark_matter_interpretation.md"
    ).read_text(encoding="utf-8")
    assert "Status: `candidate_only`" in text
    assert "COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE" in text
    assert "EFFECTIVE_DARK_MATTER_AS_CURVATURE_RESIDUE_CANDIDATE" in text
    assert "K_obs = K_visible + K_collective" in text
    assert "K_DM_eff = K_collective" in text
    assert "rho_DM_eff = (1/(4*pi*G)) * nabla^2 Phi_collective" in text


def test_dark_matter_empirical_tests_are_required() -> None:
    payload = json.loads(
        (ROOT / "theory" / "collective_curvature_threshold_results.json").read_text(
            encoding="utf-8"
        )
    )
    tests = set(payload["guardrails"]["future_empirical_tests"])
    assert {
        "galaxy rotation curves",
        "baryonic Tully-Fisher relation",
        "weak/strong lensing",
        "cluster lensing",
        "colliding clusters",
        "large-scale structure",
        "CMB consistency",
        "Solar System constraints",
    } <= tests


def test_dark_matter_solution_claims_are_not_present() -> None:
    text = (
        ROOT / "theory" / "collective_curvature_dark_matter_interpretation.md"
    ).read_text(encoding="utf-8").lower()
    assert "dark matter is solved" not in text
    assert "particle dark matter is disproven" not in text
    assert "rotation curves are solved" not in text
    assert "bullet cluster is solved" not in text
