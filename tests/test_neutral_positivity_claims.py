from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_spectral import POSITIVITY_REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_required_claim_boundaries_are_documented() -> None:
    paths = (
        "README.md",
        "docs/neutral_kernel_exact_audit.md",
        "docs/neutral_admissible_domain.md",
        "docs/neutral_positivity_proof.md",
        "docs/neutral_positivity_counterexample.md",
    )
    text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    assert all(statement in text for statement in POSITIVITY_REQUIRED_STATEMENTS)


def test_forbidden_observer_and_raw_psd_claims_are_absent() -> None:
    public = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("README.md", "STATUS.md", "CLAIMS.md", "docs/neutral_positivity_proof.md")
    ).lower()
    assert "the neutrino does not exist at all unless someone observes it" not in public
    assert "raw neutral kernel is positive semidefinite" not in public
    assert "threshold clipping is a proof" not in public
