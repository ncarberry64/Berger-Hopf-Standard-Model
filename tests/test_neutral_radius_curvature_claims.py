from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_scale import RADIUS_CURVATURE_REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_required_radius_curvature_claim_boundaries_are_visible() -> None:
    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "README.md",
            "docs/neutral_propagation_radius.md",
            "docs/neutral_physical_curvature_map.md",
            "docs/neutral_radius_curvature_closure.md",
            "docs/dimensionful_neutrino_mass_candidate.md",
        )
    )
    assert all(statement in docs for statement in RADIUS_CURVATURE_REQUIRED_STATEMENTS)


def test_status_and_claims_disclose_dimension_obstruction() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    claims = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    assert "DIMENSIONFUL_MASS_NOT_AVAILABLE" in status
    assert "mass/length" in status
    assert "dimensionally inconsistent" in claims

