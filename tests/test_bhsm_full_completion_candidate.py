import json
from pathlib import Path

from bhsm_full_completion_candidate import (
    FULL_STATUS,
    boundary_payload,
    build_mixing_candidate_report,
    ckm_exponent_derivation_payload,
    full_manifest_payload,
    gauge_payload,
    quark_rg_payload,
    scorecard_rows,
)
from bhsm_v1 import compare_bhsm_v1_branches


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.md",
    "candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.json",
    "theory/derive_z_virt_u2_candidate.md",
    "audits/z_virt_u2_derivation_audit.py",
    "audits/z_virt_u2_derivation_audit.md",
    "audits/z_virt_u2_derivation_audit.json",
    "theory/derive_ckm_mixing_exponent_candidate.md",
    "audits/ckm_mixing_exponent_derivation_audit.py",
    "audits/ckm_mixing_exponent_derivation_audit.md",
    "audits/ckm_mixing_exponent_derivation_audit.json",
    "audits/full_ckm_completion_candidate_audit.py",
    "audits/full_ckm_completion_candidate_audit.md",
    "audits/full_ckm_completion_candidate_audit.json",
    "theory/charged_lepton_virtual_dressing_candidate.md",
    "audits/charged_lepton_dressing_candidate_audit.py",
    "audits/charged_lepton_dressing_candidate_audit.md",
    "audits/charged_lepton_dressing_candidate_audit.json",
    "candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md",
    "candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.json",
    "audits/common_scale_quark_rg_audit.py",
    "audits/common_scale_quark_rg_audit.md",
    "audits/common_scale_quark_rg_audit.json",
    "theory/quark_rg_scheme_note.md",
    "audits/gauge_coupling_completion_audit.py",
    "audits/gauge_coupling_completion_audit.md",
    "audits/gauge_coupling_completion_audit.json",
    "theory/gauge_normalization_note.md",
    "theory/boundary_operator_completion_attempt.md",
    "audits/boundary_operator_derivation_audit.py",
    "audits/boundary_operator_derivation_audit.md",
    "audits/boundary_operator_derivation_audit.json",
    "audits/scalar_higgs_gap_completion_audit.py",
    "audits/scalar_higgs_gap_completion_audit.md",
    "audits/scalar_higgs_gap_completion_audit.json",
    "theory/scalar_higgs_gap_completion_note.md",
    "docs/bhsm_completion_scorecard.md",
    "docs/bhsm_completion_scorecard.json",
)


def _read(path: str) -> str:
    return ROOT.joinpath(path).read_text(encoding="utf-8")


def test_required_completion_candidate_files_exist():
    missing = [path for path in REQUIRED_FILES if not ROOT.joinpath(path).is_file()]

    assert missing == []


def test_frozen_predictions_docs_are_not_candidate_outputs():
    frozen_md = _read("docs/frozen_predictions.md")
    frozen_json = _read("docs/frozen_predictions.json")

    assert "BHSM_FULL_COMPLETION_V1_CANDIDATE" not in frozen_md
    assert "BHSM_FULL_COMPLETION_V1_CANDIDATE" not in frozen_json
    assert "BHSM_MIXING_DRESSED_V1_CANDIDATE" not in frozen_md
    assert "BHSM_MIXING_DRESSED_V1_CANDIDATE" not in frozen_json


def test_official_branches_remain_unchanged():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_full_manifest_is_not_official_and_lists_open_items():
    payload = json.loads(_read("candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.json"))

    assert payload["status"] == FULL_STATUS
    assert payload["frozen_branch_check"]["dressed_branch_changes_only_c_over_t"] is True
    assert "derive Z_virt^{u,2}=1/2" in payload["unresolved_derivations"]
    assert "derive or reject CKM exponent 1/16" in payload["unresolved_derivations"]
    assert full_manifest_payload()["status"] == FULL_STATUS


def test_candidate_files_are_clearly_not_official():
    for path in (
        "candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.md",
        "candidates/BHSM_MIXING_DRESSED_V1_CANDIDATE.md",
        "candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md",
    ):
        text = _read(path)
        assert "NOT_OFFICIAL" in text or "not official" in text


def test_no_candidate_document_makes_forbidden_positive_claims():
    candidate_text = "\n".join(
        _read(path)
        for path in REQUIRED_FILES
        if path.endswith((".md", ".json"))
    ).lower()

    forbidden_positive_phrases = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "standard model replacement",
        "confirmation by the particle-physics community",
    )
    for phrase in forbidden_positive_phrases:
        assert phrase not in candidate_text


def test_ckm_candidate_improves_pressure_points_without_j_damage():
    report = build_mixing_candidate_report()

    assert report.improves_vcb is True
    assert report.improves_vts is True
    assert report.non_23_damage_flag is False
    assert report.j_damage_flag is False


def test_lepton_boundary_quark_rg_and_gauge_statuses_are_conservative():
    lepton = json.loads(_read("audits/charged_lepton_dressing_candidate_audit.json"))
    boundary = json.loads(_read("audits/boundary_operator_derivation_audit.json"))
    quark_rg = json.loads(_read("audits/common_scale_quark_rg_audit.json"))
    gauge = json.loads(_read("audits/gauge_coupling_completion_audit.json"))

    assert lepton["classification"] == "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL"
    assert lepton["eta_classification"] == "ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert lepton["candidate_status"] == "CANDIDATE_NOT_OFFICIAL"
    assert lepton["closes_lepton_precision_blocker"] is False
    assert boundary["classification"] == "ACTION_LINKED"
    assert boundary_payload()["overstated"] is False
    assert quark_rg["classification"] == "EXTERNAL_INPUT_REQUIRED"
    assert quark_rg_payload()["precision_verdict"] == "not issued"
    assert gauge["classification"] == "GAUGE_COARSE_SURVIVAL"
    assert "normalization" in gauge_payload()


def test_ckm_exponent_remains_open_derivation_required():
    payload = json.loads(_read("audits/ckm_mixing_exponent_derivation_audit.json"))

    assert payload["classification"] == "OPEN_DERIVATION_REQUIRED"
    assert payload["candidate_label"] == "CANDIDATE_EXPONENT_NOT_DERIVED"
    assert ckm_exponent_derivation_payload()["classification"] == "OPEN_DERIVATION_REQUIRED"


def test_scorecard_json_validates_and_uses_allowed_statuses():
    payload = json.loads(_read("docs/bhsm_completion_scorecard.json"))
    allowed = {
        "CLEAN_SURVIVAL",
        "CANDIDATE_SURVIVAL",
        "CAVEATED_SURVIVAL",
        "OPEN_DERIVATION_REQUIRED",
        "FAILED_EXPLANATION",
        "FAILED_SCREEN",
        "NOT_OFFICIAL",
    }

    assert len(payload) == len(scorecard_rows())
    assert {row["status"] for row in payload} <= allowed
    assert any(row["item"] == "CKM 2-3 mixing dressing" for row in payload)
