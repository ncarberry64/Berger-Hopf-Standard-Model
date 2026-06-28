from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_neutrino_claim_boundaries_are_exactly_visible() -> None:
    docs = "\n".join(
        (ROOT / "docs" / name).read_text(encoding="utf-8")
        for name in (
            "neutrino_propagation_mass.md",
            "neutrino_curvature_threshold.md",
            "neutrino_scale_law.md",
            "neutrino_observable_map.md",
            "neutrino_numerical_closure.md",
        )
    )
    required = (
        "In BHSM, the neutrino mass contribution is modeled as a propagation-locked",
        "If the neutral propagation response is zero, the BHSM neutrino mass",
        "Electron-neutrino comparisons remain upper-limit comparisons unless a vetted",
        "Reference values are comparison inputs only and are never theorem inputs.",
    )
    assert all(statement in docs for statement in required)


def test_current_status_and_claims_preserve_numerical_boundaries() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    claims = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    assert "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE" in status
    assert "Artifact-backed dimensionful neutral scale" in status
    assert "eV/GeV prediction or empirical" in claims
    combined = (status + claims).lower()
    assert "bhsm empirically validates neutrino mass" not in combined
    not_supported = claims.split("## Not Supported", 1)[1]
    assert "Electron-neutrino mass is centrally measured" in not_supported
