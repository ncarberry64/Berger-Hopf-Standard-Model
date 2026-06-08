import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def _read(path: str) -> str:
    return ROOT.joinpath(path).read_text()


def test_gate1_v1_3_summary_exists_and_uses_corrected_formal_kernel():
    md = _read("theory/bhsm_v1_3_formal_kernel_ht_summary.md")
    data = json.loads(_read("theory/bhsm_v1_3_formal_kernel_ht_summary.json"))

    assert "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL" in md
    assert "(0,18,36)" in md
    assert "(0,1,2)" in md
    assert data["corrected_reference"] == "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL"
    assert data["formal_kernel"]["k_max_4_coordinates"] == [0, 18, 36]
    assert data["theorem_complete"] is False


def test_gate1_summary_contains_v1_3_a_through_o_and_no_overclaim():
    md = _read("theory/bhsm_v1_3_formal_kernel_ht_summary.md")
    lower = md.lower()

    for suffix in "ABCDEFGHIJKLMNO":
        assert f"v1.3{suffix}" in md

    forbidden = (
        "fully proven",
        "complete proof",
        "full theorem proven",
        "no-extra-light-state theorem is proven",
        "FULL_OPERATOR_PROVEN",
    )
    assert all(phrase.lower() not in lower for phrase in forbidden)
    assert "full no-extra-light-state theorem remains" in lower


def test_gate1_manuscript_addendum_exists_and_preserves_limitations():
    text = _read("manuscript/BHSM_v1_3_formal_kernel_ht_addendum.md")
    lower = text.lower()

    assert "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL" in text
    assert "coordinate-first block `(0,1,2)` is superseded" in text
    assert "does not claim" in lower
    assert "frozen bhsm v1.0/v1.1 predictions" in lower


def test_global_completion_campaign_report_exists_and_tracks_all_gates():
    md = _read("theory/bhsm_completion_campaign_report.md")
    data = json.loads(_read("theory/bhsm_completion_campaign_report.json"))

    assert data["theorem_complete"] is False
    assert data["frozen_outputs_changed"] is False
    assert len(data["gates"]) == 5
    assert all(gate["stop_condition_triggered"] is False for gate in data["gates"])
    assert "DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL" in md
    assert "bhsm-v1.4-precision-qcd-rg" in md


def test_completion_campaign_addendum_preserves_global_claim_discipline():
    text = _read("manuscript/BHSM_completion_campaign_addendum.md")
    lower = text.lower()

    assert "does not claim" not in lower or "full" in lower or "not proven" in lower
    assert "fully proven" not in lower
    assert "completed first-principles proof" not in lower
    assert "not proven" in lower
    assert "empirical-residual" in lower
