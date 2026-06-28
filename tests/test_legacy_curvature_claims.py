from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_scale import LEGACY_REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]


def test_required_legacy_claim_boundaries_are_visible() -> None:
    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "README.md",
            "docs/legacy_curvature_threshold_artifacts.md",
            "docs/curvature_mass_functional_adapter.md",
            "docs/neutral_curvature_mapping.md",
            "docs/legacy_neutral_scale_candidate.md",
            "docs/neutrino_numerical_closure.md",
        )
    )
    assert all(statement in docs for statement in LEGACY_REQUIRED_STATEMENTS)


def test_status_and_claims_preserve_open_neutral_gates() -> None:
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    claims = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    assert "ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL" in status
    assert "r_prop" in status
    assert "Legacy particle threshold tables are no-fit BHSM predictions" in claims

