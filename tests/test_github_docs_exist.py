from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_github_facing_docs_exist() -> None:
    for relative in [
        "docs/github_landing_status.md",
        "docs/github_claim_summary.md",
        "docs/github_quickstart.md",
        "docs/github_release_checklist_full_bhsm_v1.md",
        "docs/forbidden_claims.md",
        "docs/allowed_public_language.md",
        "docs/current_bhsm_status.md",
        "docs/current_bhsm_status.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_readme_refreshed_for_full_bhsm_candidate() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "# Berger-Hopf Standard Model (BHSM)" in text
    assert (
        "Current status: structural architecture integrated conditional; numerical closure open."
        in text
    )
    assert "What BHSM Is" in text
    assert "What Is Test-Backed" in text
    assert "What Is Not Yet Proven" in text
    assert "Frozen Prediction Layer" in text
    assert "Candidate Synthesis Layer" in text
    assert "Connected Topographic-Curvature Extension" in text
    assert "How To Reproduce" in text
    assert "Claim Hygiene" in text
