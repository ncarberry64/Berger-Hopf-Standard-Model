from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_scale import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_required_scale_claim_boundaries_are_visible() -> None:
    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "README.md",
            "docs/neutral_dimensionful_scale.md",
            "docs/neutrino_propagation_mass.md",
            "docs/neutrino_numerical_closure.md",
        )
    )
    assert all(statement in docs for statement in REQUIRED_STATEMENTS)


def test_status_and_claims_preserve_open_neutral_scale() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    claims = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    assert "OPEN_MISSING_NEUTRAL_SCALE" in status
    assert "emits no eV/GeV mass" in claims
    assert "FeynRules/UFO/MadGraph readiness" in claims

