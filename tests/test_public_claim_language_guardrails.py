from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_forbidden_claims import audit as audit_forbidden_claims  # noqa: E402


def test_forbidden_claim_examples_are_documented() -> None:
    text = (ROOT / "docs" / "forbidden_claims.md").read_text(encoding="utf-8")
    for phrase in [
        "BHSM proves the Standard Model.",
        "BHSM has replaced the Standard Model.",
        "BHSM fully derives the Standard Model.",
        "BHSM solves dark matter.",
        "BHSM disproves particle dark matter.",
        "The BHSM mass engine is closed.",
        "The heat-kernel spectral action is the official mass engine.",
        "All Standard Model constants are derived.",
        "The full gauge group is derived.",
    ]:
        assert phrase in text


def test_allowed_public_language_is_documented() -> None:
    text = (ROOT / "docs" / "allowed_public_language.md").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "candidate completion framework",
        "repo-audited candidate architecture",
        "test-backed discrete geometric skeleton",
        "conditional fermion ledger generation",
        "mass numerical closure unresolved",
        "replacement by derivation remains the long-term goal",
        "collective-curvature dark-matter interpretation candidate",
        "connected topographic-gravity extension",
    ]:
        assert phrase in text


def test_public_forbidden_claim_audit_passes() -> None:
    result = audit_forbidden_claims()
    assert result["passed"] is True
    assert result["findings"] == []
