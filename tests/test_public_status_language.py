from __future__ import annotations

from pathlib import Path

from bhsm.interface.neutrino_closure_status import NEUTRINO_PUBLIC_STATUS


ROOT = Path(__file__).resolve().parents[1]
NEUTRINO_RECORD_FILES = (
    "docs/README.md",
    "docs/neutrino_numerical_closure.md",
    "docs/neutral_action_spectral_closure.md",
)


def test_current_public_surfaces_use_precise_neutral_status() -> None:
    contents = {path: (ROOT / path).read_text(encoding="utf-8") for path in NEUTRINO_RECORD_FILES}
    for path in NEUTRINO_RECORD_FILES:
        assert NEUTRINO_PUBLIC_STATUS in contents[path]
        assert "numerical closure open" not in contents[path].lower()
    for path in ("README.md", "STATUS.md"):
        current = (ROOT / path).read_text(encoding="utf-8")
        assert "v18.73" in current
        assert "FULL_BHSM_COMPLETE = FALSE" in current


def test_public_status_does_not_add_forbidden_neutral_claims() -> None:
    combined = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("README.md", "STATUS.md", *NEUTRINO_RECORD_FILES)
    ).lower()
    for forbidden in (
        "raw neutral kernel is positive semidefinite",
        "complete neutral action closure",
        "empirically validated",
        "central electron-neutrino mass measurement",
        "feynrules ready",
        "madgraph ready",
    ):
        assert forbidden not in combined
