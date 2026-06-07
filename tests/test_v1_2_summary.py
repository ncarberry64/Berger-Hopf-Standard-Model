from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from v1_2_summary import (
    build_v1_2_action_origin_summary,
    export_v1_2_summary_json,
    export_v1_2_summary_markdown,
)


def test_v1_2_summary_exports_exist_and_contain_required_claims(tmp_path):
    md_path = tmp_path / "summary.md"
    json_path = tmp_path / "summary.json"

    export_v1_2_summary_markdown(md_path)
    export_v1_2_summary_json(json_path)

    md = md_path.read_text()
    js = json_path.read_text()
    assert "Omega_ell = -q + 2j = 3" in md
    assert "Omega_u = q - 2j = 6" in md
    assert "Omega_d = q + 4j = 12" in md
    assert "UNIQUE_UNDER_BHSM_AXIOMS" in md
    assert '"theorem_complete": false' in js


def test_v1_2_summary_statuses_and_tables():
    summary = build_v1_2_action_origin_summary()

    assert summary["parent_action_reduction_status"] == "REDUCED_FROM_PARENT_ACTION"
    assert summary["minimality_status"] == "MINIMAL_UNDER_TESTED_PARENT_TERMS"
    assert summary["uniqueness_status"] == "UNIQUE_UNDER_BHSM_AXIOMS"
    assert summary["theorem_complete"] is False
    assert {row["removed_term"] for row in summary["minimality_table"]} == {
        "I_HOPF",
        "I_U1",
        "I_BASE",
        "I_WEAK",
        "I_COF",
        "I_BDY",
    }
    assert {row["variant"] for row in summary["uniqueness_variant_table"]} == {
        "flip_hopf_orientation",
        "flip_weak_chirality",
        "remove_coframe_triplet",
        "coframe_singlet",
        "shift_boundary_winding",
        "swap_weak_component_sign",
        "trace_u1_dynamical",
        "disable_higgs_u1",
    }


def test_v1_2_summary_does_not_overclaim():
    text = "\n".join(
        [
            Path("theory/bhsm_v1_2_action_origin_summary.md").read_text() if Path("theory/bhsm_v1_2_action_origin_summary.md").exists() else "",
            Path("manuscript/BHSM_v1_2_action_origin_addendum.md").read_text() if Path("manuscript/BHSM_v1_2_action_origin_addendum.md").exists() else "",
        ]
    ).lower()

    assert "complete internal action proven" not in text
    assert "fully proven" not in text
    assert "full uniqueness of the complete internal action" in text or text == "\n"


def test_v1_2_summary_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_v1_2_action_origin_summary()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
