from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_action import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_required_neutral_action_claim_boundaries_are_visible() -> None:
    paths = (
        "README.md",
        "docs/neutral_action_source_search.md",
        "docs/neutral_action_stiffness.md",
        "docs/physical_neutral_curvature_map.md",
        "docs/action_derived_response_cone.md",
        "docs/neutral_action_spectral_closure.md",
    )
    text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    assert all(statement in text for statement in REQUIRED_STATEMENTS)


def test_public_docs_do_not_overclaim_action_or_mass_closure() -> None:
    text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("README.md", "STATUS.md", "CLAIMS.md", "docs/neutral_action_spectral_closure.md")
    ).lower()
    assert "complete neutral action closure is proven" not in text
    assert "empirically validates neutrino mass" not in text
    assert "central electron-neutrino mass" not in text
