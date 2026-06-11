import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = (
    "README.md",
    "CITATION.cff",
    "LICENSE.md",
    "RELEASE_NOTES.md",
    "manuscript/BHSM_final_paper.md",
    "docs/claim_status_table.md",
    "docs/frozen_predictions.md",
    "docs/reproducibility.md",
    "docs/falsification_criteria.md",
    "docs/zenodo_release_notes.md",
)


def _read(relative_path: str) -> str:
    return ROOT.joinpath(relative_path).read_text(encoding="utf-8")


def test_required_final_release_files_exist():
    missing = [path for path in REQUIRED_FILES if not ROOT.joinpath(path).is_file()]
    assert missing == []


def test_release_metadata_is_v120_and_has_no_invented_doi():
    citation = _read("CITATION.cff")
    zenodo = json.loads(_read(".zenodo.json"))
    release_notes = _read("docs/zenodo_release_notes.md") + "\n" + _read("RELEASE_NOTES.md")

    assert "version: \"v1.2.0\"" in citation
    assert "date-released: \"2026-06-11\"" in citation
    assert zenodo["version"] == "v1.2.0"
    assert "10.5281/zenodo" not in citation
    assert "10.5281/zenodo" not in json.dumps(zenodo)
    assert "Zenodo DOI is assigned after release archival" in release_notes


def test_claim_status_categories_and_forbidden_claims_are_visible():
    claim_table = _read("docs/claim_status_table.md")
    paper = _read("manuscript/BHSM_final_paper.md")
    docs = claim_table + "\n" + paper + "\n" + _read("docs/zenodo_release_notes.md")

    for status in (
        "DERIVED_CONDITIONAL",
        "VERIFIED_TEST",
        "STRONG_SCREEN",
        "PROXY_AUDIT",
        "OPEN",
        "FORBIDDEN",
    ):
        assert status in docs

    forbidden_phrases = (
        "full derivation of the Standard Model from first principles",
        "proof of confinement",
        "proof of quantum gravity",
        "final replacement of the Standard Model",
        "experimental confirmation by the particle-physics community",
        "post-data retuning",
    )
    for phrase in forbidden_phrases:
        assert phrase in docs


def test_frozen_prediction_docs_preserve_key_values():
    frozen_md = _read("docs/frozen_predictions.md")
    frozen_json = json.loads(_read("docs/frozen_predictions.json"))

    assert "`BHSM_BARE_V1`" in frozen_md
    assert "`BHSM_DRESSED_V1_CANDIDATE`" in frozen_md
    assert "1.157054135733433" in frozen_md
    assert "0.07957747154594767" in frozen_md
    assert frozen_json["constants"]["a"] == 1.157054135733433
    assert frozen_json["constants"]["S"] == 0.07957747154594767
    assert frozen_json["outputs"]["c/t"]["dressed_candidate"] == 0.004155250277034144
    assert frozen_json["outputs"]["u/t"]["changed"] is False
    assert frozen_json["outputs"]["sin_theta_13"]["changed"] is False


def test_final_paper_keeps_proxy_and_open_language_for_ht_and_scalar():
    paper = _read("manuscript/BHSM_final_paper.md")

    assert "`PROXY_AUDIT` / open full spectrum" in paper
    assert "full twisted Dirac/H_T spectrum beyond proxy/scaffold audits" in paper
    assert "| Scalar/topographic decoupling | finite-basis scaffold / open full action proof |" in paper
    assert "The release does not claim experimental confirmation" in paper
