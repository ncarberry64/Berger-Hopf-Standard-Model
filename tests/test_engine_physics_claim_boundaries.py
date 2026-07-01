from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_claim_boundary_language_is_present():
    text = (ROOT / "docs/engine_vs_physics_claim_boundary.md").read_text(encoding="utf-8")
    assert "does not constitute empirical validation" in text
    assert "does not claim full Standard Model derivation" in text
    assert "physical eV/GeV neutrino mass closure" in text

