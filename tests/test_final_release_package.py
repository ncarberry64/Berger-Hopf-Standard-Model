import json
import re
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from full_bhsm_theorem_final_decision import build_full_bhsm_theorem_final_decision
from full_bhsm_theorem_sprint import build_full_bhsm_sprint_status
from full_ht_theorem_final import build_full_ht_theorem_final_report


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return ROOT.joinpath(relative).read_text(encoding="utf-8")


def test_final_release_files_exist_and_state_completed_theorem_package():
    expected = (
        "manuscript/BHSM_final_paper.md",
        "manuscript/BHSM_final_paper.tex",
        "theory/current_status.md",
        "theory/full_bhsm_theorem_completion_report.md",
        "theory/full_bhsm_theorem_completion_report.json",
        "theory/bhsm_theorem_completion_decision.md",
        "theory/full_bhsm_theorem_obligations.md",
        "README.md",
        "RELEASE_NOTES.md",
        "CITATION.cff",
        ".zenodo.json",
        "docs/BHSM_plain_language_overview.md",
        "docs/reviewer_attack_guide.md",
        "docs/reproducibility.md",
        "docs/frozen_predictions.md",
        "docs/theorem_status_summary.md",
        "docs/limitations_and_external_validation.md",
        "docs/claim_status_table.md",
    )
    missing = [path for path in expected if not ROOT.joinpath(path).exists()]
    assert missing == []

    combined = "\n".join(_read(path) for path in expected)
    assert "FULL_BHSM_THEOREM_PACKAGE_COMPLETE" in combined
    assert "FULL_HT_THEOREM_PROVEN" in combined
    assert "HT_LOWER_BOUND_TRANSFER_PROVEN" in combined
    assert "INDEX_THEOREM_PROVEN" in combined
    assert "MIRROR_EXCLUSION_PROVEN" in combined


def test_final_release_status_matches_sprint_decision():
    sprint = build_full_bhsm_sprint_status()
    decision = build_full_bhsm_theorem_final_decision()
    ht = build_full_ht_theorem_final_report()
    file_status = json.loads(_read("theory/full_bhsm_theorem_completion_report.json"))

    assert sprint.final_result == "FULL_BHSM_THEOREM_PACKAGE_COMPLETE"
    assert decision.final_result == "FULL_BHSM_THEOREM_PACKAGE_COMPLETE"
    assert ht.final_result == "FULL_HT_THEOREM_PROVEN"
    assert file_status["final_result"] == "FULL_BHSM_THEOREM_PACKAGE_COMPLETE"
    assert file_status["theorem_complete"] is True
    assert file_status["remaining_blockers"] == []


def test_final_release_does_not_claim_completion_from_open_or_conditional_nodes():
    data = json.loads(_read("theory/full_bhsm_theorem_completion_report.json"))
    status_text = json.dumps(data["node_status"])

    assert "OPEN" not in status_text
    assert "CONDITIONAL" not in status_text
    assert data["final_paper_allowed"] is True


def test_final_release_no_coordinate_first_kernel_or_hidden_empirical_fitting():
    final_text = (
        _read("manuscript/BHSM_final_paper.md")
        + "\n"
        + _read("manuscript/BHSM_final_paper.tex")
        + "\n"
        + _read("theory/full_bhsm_theorem_completion_report.md")
    )

    assert "DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST" not in final_text
    assert "does not use the coordinate-first kernel" in final_text
    assert "post-hoc retuning" in final_text
    assert "No-retuning" in _read("README.md") or "no-retuning" in _read("README.md")


def test_final_release_does_not_invent_zenodo_doi():
    checked = (
        "README.md",
        "RELEASE_NOTES.md",
        "CITATION.cff",
        ".zenodo.json",
        "manuscript/BHSM_final_paper.md",
        "manuscript/BHSM_final_paper.tex",
    )
    text = "\n".join(_read(path) for path in checked)

    assert "10.5281/zenodo" not in text.lower()
    assert "doi.org/10.5281" not in text.lower()
    assert "DOI pending Zenodo release" in text or "Zenodo DOI: pending" in text


def test_readme_links_resolve_locally():
    readme = _read("README.md")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
    local_links = [
        link.split("#", 1)[0]
        for link in links
        if link and not link.startswith(("http://", "https://", "mailto:"))
    ]

    missing = [link for link in local_links if link and not ROOT.joinpath(link).exists()]
    assert missing == []


def test_user_facing_docs_preserve_claim_boundaries():
    docs = (
        "README.md",
        "docs/BHSM_plain_language_overview.md",
        "docs/reviewer_attack_guide.md",
        "docs/reproducibility.md",
        "docs/frozen_predictions.md",
        "docs/theorem_status_summary.md",
        "docs/limitations_and_external_validation.md",
        "docs/claim_status_table.md",
    )
    text = "\n".join(_read(path) for path in docs)

    assert "Final theorem package: COMPLETE" in text
    assert "757 passed" in text
    assert "Zenodo DOI: pending" in text
    assert "not a claim of experimental confirmation" in text
    assert "accepted replacement of the Standard Model" in text
    assert "new particle discovery" in text
    assert "QCD confinement" in text
    assert "guaranteed correctness" in text


def test_final_release_preserves_frozen_outputs():
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    rows = compare_bhsm_v1_branches()["rows"]
    changed = [row for row in rows if row["changed"]]
    by_quantity = {row["quantity"]: row for row in rows}

    assert bare.version.branch == "BHSM_BARE_V1"
    assert dressed.version.branch == "BHSM_DRESSED_V1_CANDIDATE"
    assert isclose(bare.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert by_quantity["u/t"]["bare"] == by_quantity["u/t"]["dressed"]
    assert by_quantity["sin_theta_13"]["bare"] == by_quantity["sin_theta_13"]["dressed"]
