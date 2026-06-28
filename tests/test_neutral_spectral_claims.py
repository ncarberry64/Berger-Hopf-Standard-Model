from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_spectral import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_required_spectral_claim_boundaries_are_visible() -> None:
    paths = (
        "README.md",
        "docs/neutrino_mass_gap_action.md",
        "docs/legacy_dimensional_gate.md",
        "docs/neutral_stiffness_ratio.md",
        "docs/neutral_spectral_gap.md",
        "docs/neutral_kernel_positivity.md",
    )
    text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    assert all(statement in text for statement in REQUIRED_STATEMENTS)
    assert "empirically validates neutrino mass" not in text.lower()


def test_status_and_claims_preserve_open_numerical_closure() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    claims = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    assert "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE" in status
    assert "OPEN_MISSING_NUMERIC_STIFFNESS_RATIO" in status
    assert "legacy gravitational curvature expression" in claims
