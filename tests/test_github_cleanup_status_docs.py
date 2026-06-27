from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_public_entrypoint_and_required_docs_exist() -> None:
    required = (
        "README.md",
        "STATUS.md",
        "CLAIMS.md",
        "QUICKSTART.md",
        "CLI_REFERENCE.md",
        "ARTIFACT_INDEX.md",
        "ROADMAP.md",
        "docs/README.md",
    )
    assert all((ROOT / path).is_file() for path in required)

    readme = read("README.md")
    assert "artifact-backed computational framework" in readme
    assert "[CLAIMS.md](CLAIMS.md)" in readme
    assert "[STATUS.md](STATUS.md)" in readme
    assert len(readme.splitlines()) < 180


def test_status_has_required_areas_and_clean_taxonomy() -> None:
    status = read("STATUS.md")
    required_rows = (
        "Frozen internal predictions",
        "Python computational interface",
        "Prediction registry",
        "CLI reports",
        "Prediction gallery",
        "Artifact-backed adapters",
        "CKM matrix",
        "PMNS matrix",
        "CP phase / Z6 holonomy",
        "Boundary constants",
        "Mass ratios",
        "W calibration policy",
        "Electron-neutrino comparison policy",
        "CP O_int",
        "X_ch",
        "Neutrino physical basis/scale",
        "FeynRules minimal model",
        "UFO export",
        "MadGraph smoke test",
    )
    assert all(row in status for row in required_rows)
    assert "CANDIDATE / OPEN" in status
    assert "callable symbolic candidate exists" in status
    assert "RUNTIME_GATED" in status


def test_claims_and_policy_boundaries_are_centralized() -> None:
    claims = read("CLAIMS.md")
    assert "## Allowed" in claims
    assert "## Not Supported" in claims
    assert "W is an independent prediction" in claims
    assert "Electron-neutrino mass is centrally measured" in claims
    assert "A symbolic CP `O_int` candidate is production-ready" in claims

    readme = read("README.md").lower()
    repeated_warning_markers = sum(
        readme.count(marker)
        for marker in ("does not claim", "not production-ready", "not closed", "promoted: false")
    )
    assert repeated_warning_markers <= 3


def test_quickstart_and_docs_index_cover_reviewer_path() -> None:
    quickstart = read("QUICKSTART.md")
    for command in (
        "python -m bhsm.interface registry",
        "python -m bhsm.interface status W_boson",
        "python -m bhsm.interface gallery --format markdown",
        "python -m bhsm.interface artifact-sources",
        "python -m bhsm.interface formula-registry",
        "python -m bhsm.interface compute-artifact CKM_matrix_BHSM",
        "python -m bhsm.interface compute-artifact PMNS_matrix_BHSM",
        "python -m bhsm.interface artifact-report --anchor W_boson --format json",
        "python -m bhsm.interface cp-o-int-field-action --format json",
        "python -m bhsm.interface theorem-blockers",
    ):
        assert command in quickstart

    docs_index = read("docs/README.md")
    for section in (
        "Overview",
        "Python Interface",
        "Prediction Registry And CLI",
        "Gallery And Notebooks",
        "Artifact-Backed Adapters",
        "Theorem Closure",
        "CP O_int Sprint Docs",
        "Claim Policy",
        "Release And Administration History",
    ):
        assert section in docs_index


def test_frozen_prediction_hashes_are_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected

