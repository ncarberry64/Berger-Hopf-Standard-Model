import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str):
    return json.loads(read_text(path))


def test_readme_contains_release_status_split() -> None:
    readme = read_text("README.md")
    assert "Berger-Hopf Standard Model v1.0.0" in readme
    assert "complete internal boundary no-fit prediction package" in readme
    assert "External empirical comparison is implemented as a separate comparison-only layer" in readme
    assert "Empirical data are not used to derive BHSM constants or boundary predictions" in readme
    assert "internal boundary no-fit package complete; external empirical comparison layer separate/open" in readme
    assert "BHSM is empirically proven" not in readme
    assert "BHSM fully replaces the Standard Model experimentally" not in readme
    assert "BHSM is validated by DESI" not in readme
    assert "BHSM predicts observed masses exactly" not in readme


def test_release_metadata_files_exist_and_parse() -> None:
    for path in [
        "CHANGELOG.md",
        "RELEASE_NOTES_v1.0.0.md",
        "CITATION.cff",
        ".zenodo.json",
        "AUTHORS.md",
        "LICENSE.md",
        "docs/how_to_cite.md",
        "docs/release_checklist_v1.0.0.md",
    ]:
        assert (ROOT / path).exists(), path

    zenodo = read_json(".zenodo.json")
    assert zenodo["title"] == "Berger-Hopf Standard Model v1.0.0: Complete Internal Boundary No-Fit Package"
    assert zenodo["license"] == "LicenseRef-AllRightsReserved"

    citation = read_text("CITATION.cff")
    assert "cff-version: 1.2.0" in citation
    assert 'version: "1.0.0"' in citation
    assert 'license: "LicenseRef-AllRightsReserved"' in citation

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        parsed = yaml.safe_load(citation)
        assert parsed["version"] == "1.0.0"
        assert parsed["license"] == "LicenseRef-AllRightsReserved"


def test_release_manifest_and_completion_artifact_are_consistent() -> None:
    manifest = read_json("artifacts/BHSM_v1_release_manifest.json")
    completion = read_json("artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json")

    assert manifest["release"] == "v1.0.0"
    assert manifest["release_candidate_source"] == "BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json"
    assert manifest["internal_boundary_package"] == "COMPLETE_EXPORTED"
    assert manifest["boundary_no_fit_prediction_package"] == "COMPLETE_EXPORTED"
    assert manifest["external_empirical_comparison_package"] == "IMPLEMENTED_COMPARISON_ONLY_LAYER"
    assert manifest["external_empirical_comparison_status"] == "DATA_ABSENT_OR_DATA_OPTIONAL"
    assert manifest["doi"] == "PENDING_ZENODO_RELEASE"
    assert manifest["empirical_derivation_inputs_used"] is False
    assert manifest["boundary_predictions_modified_by_comparison"] is False
    assert manifest["official_predictions_changed"] is False

    assert completion["release_candidate"] == "BHSM_COMPLETE_V1"
    assert completion["internal_boundary_package"] == "COMPLETE_EXPORTED"
    assert completion["boundary_predictions_modified_by_comparison"] is False


def test_manuscript_exists_and_preserves_claim_boundaries() -> None:
    manuscript = read_text("manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.md")
    assert "# The Berger-Hopf Standard Model v1.0.0" in manuscript
    assert "Norman P. Carberry" in manuscript
    assert "Independent Researcher, Oconomowoc, Wisconsin, USA" in manuscript
    assert "This work reports the v1.0.0 release" in manuscript
    assert "a = alpha^{-1}/(12*pi^2)" in manuscript
    assert "S = 1/(4*pi)" in manuscript
    assert "kappa_H = mu_H = 64*pi^5" in manuscript
    assert "beta_l*tau = kappa_l*tau = 4/(1323*pi^(3/2))" in manuscript
    assert "external_empirical_comparison_package = IMPLEMENTED_COMPARISON_ONLY_LAYER" in manuscript
    assert "Appendix A: Artifact Manifest" in manuscript
    assert "Appendix B: Test and Audit Summary" in manuscript
    assert "Appendix C: Release Checklist" in manuscript
    assert "does not claim empirical validation" in manuscript
    assert "empirically proven" not in manuscript
    assert "validated by DESI" not in manuscript
    assert "predicts observed masses exactly" not in manuscript


def test_release_docs_record_no_empirical_feedback() -> None:
    combined = "\n".join(
        read_text(path)
        for path in [
            "README.md",
            "docs/current_status.md",
            "docs/claim_boundaries.md",
            "docs/falsification_criteria.md",
            "docs/reproducibility.md",
            "RELEASE_NOTES_v1.0.0.md",
        ]
    )
    assert "empirical_derivation_inputs_used = false" in combined
    assert "boundary_predictions_modified_by_comparison = false" in combined
    assert "official_predictions_changed = false" in combined
    assert "separate comparison-only layer" in combined
    assert "NOT_EVALUATED_DATA_ABSENT" in combined


def test_no_invented_doi_in_release_files() -> None:
    release_paths = [
        "README.md",
        "CITATION.cff",
        ".zenodo.json",
        "docs/how_to_cite.md",
        "RELEASE_NOTES_v1.0.0.md",
        "artifacts/BHSM_v1_release_manifest.json",
        "manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.md",
        "manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.bib",
    ]
    combined = "\n".join(read_text(path) for path in release_paths)
    assert "PENDING_ZENODO_RELEASE" in combined
    assert re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", combined) is None


def test_frozen_prediction_files_unchanged() -> None:
    import hashlib

    expected = {
        "docs/frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
        "docs/frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
    }
    for path, digest in expected.items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest().upper()
        assert actual == digest


def test_pdf_status_is_explicit() -> None:
    release_manifest = read_text("manuscript/BHSM_v1_release_manifest.md")
    pdf = ROOT / "manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.pdf"
    if pdf.exists():
        assert pdf.stat().st_size > 0
    else:
        assert "PDF_BUILD_NOT_AVAILABLE_IN_ENVIRONMENT" in release_manifest
