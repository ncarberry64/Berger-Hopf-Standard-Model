import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bundle_dirac_derivation import build_bundle_dirac_derivation_report
from complete_berger_hopf_operator import build_complete_berger_hopf_operator_report
from complete_operator_identification_decision import (
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_complete_operator_identification_decision,
    export_complete_operator_identification_decision_json,
    export_complete_operator_identification_decision_markdown,
)
from constants import S_OVERLAP
from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, formal_kernel_basis_vectors
from full_bhsm_theorem_completion import build_full_bhsm_theorem_completion_report
from full_ht_theorem_closure import HT_LOWER_BOUND_TRANSFER_GAP, build_full_ht_theorem_closure_report
from operator_identification_theorem import (
    COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM,
    COMPLETE_OPERATOR_IDENTIFICATION_PROVEN,
    build_operator_identification_theorem_report,
    export_operator_identification_theorem_json,
    export_operator_identification_theorem_markdown,
)
from operator_missing_term_audit import build_operator_missing_term_audit_report, export_operator_missing_term_audit_json, export_operator_missing_term_audit_markdown
from operator_term_inventory import BLOCKING_CLASSIFICATIONS, build_operator_term_inventory_report, export_operator_term_inventory_json, export_operator_term_inventory_markdown
from complete_berger_hopf_operator import export_complete_berger_hopf_operator_json, export_complete_berger_hopf_operator_markdown
from bundle_dirac_derivation import export_bundle_dirac_derivation_json, export_bundle_dirac_derivation_markdown


SINGLE_THEOREM_GAP = HT_LOWER_BOUND_TRANSFER_GAP


def test_every_complete_operator_term_is_classified_and_single_gap_is_visible():
    report = build_operator_term_inventory_report()

    assert report.all_terms_classified is True
    assert report.required_open_or_missing_terms == ()
    assert report.theorem_complete is True
    assert all(term.classification for term in report.terms)
    assert [term.term_id for term in report.terms if term.classification in BLOCKING_CLASSIFICATIONS] == []


def test_missing_term_audit_names_single_operator_term_without_hiding_it():
    report = build_operator_missing_term_audit_report()

    assert report.hidden_missing_terms is False
    assert report.blocking_term == ""
    assert report.unique_blocking_terms == ()
    assert report.status == "OPERATOR_MISSING_TERM_AUDIT_CLEAN"
    assert not any(row.blocking for row in report.rows)


def test_complete_operator_and_bundle_derivation_refuse_theorem_completion():
    operator = build_complete_berger_hopf_operator_report()
    derivation = build_bundle_dirac_derivation_report()

    assert operator.unresolved_terms == ()
    assert operator.theorem_complete is True
    assert derivation.unresolved_step == ""
    assert derivation.theorem_complete is True


def test_operator_identification_theorem_is_blocked_not_proven():
    report = build_operator_identification_theorem_report()

    assert report.status == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert report.theorem_complete is True
    assert report.blocking_term == ""
    assert report.next_target_theorem == ""
    assert report.exact_obstruction == "No obstruction."


def test_final_v26_decision_uses_allowed_result_and_blocks_final_paper():
    decision = build_complete_operator_identification_decision()

    assert decision.final_result == COMPLETE_OPERATOR_IDENTIFICATION_PROVEN
    assert decision.theorem_complete is True
    assert decision.blocking_term == ""
    assert decision.recommended_next_branch == ""
    assert decision.recommended_target_theorem == ""
    assert decision.final_paper_allowed is False


def test_formal_kernel_is_sector_labeled_and_coordinate_first_kernel_is_not_used():
    basis = formal_kernel_basis_vectors()

    assert DEFAULT_FORMAL_COORDINATES == (0, 18, 36)
    assert OLD_COORDINATE_FIRST_KERNEL == (0, 1, 2)
    assert DEFAULT_FORMAL_COORDINATES != OLD_COORDINATE_FIRST_KERNEL
    assert tuple(row.coordinate_hint_kmax4 for row in basis) == DEFAULT_FORMAL_COORDINATES
    assert tuple(row.sector for row in basis) == ("lepton", "up", "down")


def test_downstream_theorems_do_not_upgrade_from_v26_blocker():
    ht = build_full_ht_theorem_closure_report()
    bhsm = build_full_bhsm_theorem_completion_report()

    assert ht.theorem_complete is False
    assert ht.recommended_next_branch == "bhsm-v2.16-ht-lower-bound-transfer"
    assert ht.recommended_target_theorem == SINGLE_THEOREM_GAP
    assert "index/mirror" in ht.exact_obstruction.lower()
    assert bhsm.theorem_complete is False
    assert bhsm.final_paper_allowed is False


def test_v26_modules_do_not_import_empirical_flavor_or_residual_machinery():
    root = Path(__file__).parents[1]
    text = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "complete_berger_hopf_operator.py",
            "bundle_dirac_derivation.py",
            "operator_term_inventory.py",
            "operator_missing_term_audit.py",
            "operator_identification_theorem.py",
            "complete_operator_identification_decision.py",
        )
    )
    forbidden = (
        "from prediction_ledger",
        "import prediction_ledger",
        "from residual_audit",
        "import residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "compute_ckm",
        "compute_pmns",
        "PDG",
    )
    assert all(token not in text for token in forbidden)


def test_v26_exports_generate(tmp_path):
    exporters = (
        (export_complete_berger_hopf_operator_markdown, export_complete_berger_hopf_operator_json, "operator"),
        (export_bundle_dirac_derivation_markdown, export_bundle_dirac_derivation_json, "bundle"),
        (export_operator_term_inventory_markdown, export_operator_term_inventory_json, "inventory"),
        (export_operator_missing_term_audit_markdown, export_operator_missing_term_audit_json, "missing"),
        (export_operator_identification_theorem_markdown, export_operator_identification_theorem_json, "theorem"),
        (export_complete_operator_identification_decision_markdown, export_complete_operator_identification_decision_json, "decision"),
    )

    for export_md, export_json, name in exporters:
        md_path = tmp_path / f"{name}.md"
        json_path = tmp_path / f"{name}.json"
        export_md(md_path)
        export_json(json_path)
        assert md_path.read_text()
        assert json.loads(json_path.read_text())


def test_requested_v26_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/complete_berger_hopf_operator_report.md",
        "theory/complete_berger_hopf_operator_report.json",
        "theory/bundle_dirac_derivation_report.md",
        "theory/bundle_dirac_derivation_report.json",
        "theory/operator_term_inventory_report.md",
        "theory/operator_term_inventory_report.json",
        "theory/operator_missing_term_audit.md",
        "theory/operator_missing_term_audit.json",
        "theory/operator_identification_theorem_report.md",
        "theory/operator_identification_theorem_report.json",
        "theory/complete_operator_identification_decision.md",
        "theory/complete_operator_identification_decision.json",
        "manuscript/BHSM_v2_6_complete_operator_identification_note.md",
        "notebooks/56_complete_operator_identification.ipynb",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert COMPLETE_OPERATOR_IDENTIFICATION_PROVEN in root.joinpath("theory/complete_operator_identification_decision.md").read_text()


def test_v26_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_complete_operator_identification_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
