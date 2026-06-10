import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from complete_operator_identification_closure import (
    COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP,
    build_complete_operator_identification_closure_report,
    export_complete_operator_identification_closure_json,
    export_complete_operator_identification_closure_markdown,
)
from operator_identification_theorem import COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM
from complete_twisted_dirac_operator import COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL
from constants import S_OVERLAP
from full_bhsm_theorem_completion import (
    FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
    build_full_bhsm_theorem_completion_report,
    export_full_bhsm_theorem_completion_json,
    export_full_bhsm_theorem_completion_markdown,
)
from full_ht_theorem_closure import (
    BHSM_THEOREM_FAILURE,
    FULL_HT_THEOREM_PROVEN,
    STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
    build_full_ht_theorem_closure_report,
    export_full_ht_theorem_closure_json,
    export_full_ht_theorem_closure_markdown,
)
from index_theorem_final_proof import build_index_theorem_final_proof_report, export_index_theorem_final_proof_json, export_index_theorem_final_proof_markdown
from lower_bound_transfer_closure import build_lower_bound_transfer_closure_report, export_lower_bound_transfer_closure_json, export_lower_bound_transfer_closure_markdown
from mirror_exclusion_final_proof import build_mirror_exclusion_final_proof_report, export_mirror_exclusion_final_proof_json, export_mirror_exclusion_final_proof_markdown
from projector_commutator_closure import build_projector_commutator_closure_report, export_projector_commutator_closure_json, export_projector_commutator_closure_markdown
from projector_graph_domain_closure import build_projector_graph_domain_closure_report, export_projector_graph_domain_closure_json, export_projector_graph_domain_closure_markdown


def test_complete_operator_identification_is_the_single_named_gap():
    report = build_complete_operator_identification_closure_report()

    assert report.source_status == COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM
    assert report.final_status == COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL
    assert report.theorem_complete is False
    assert report.next_target_theorem == "COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP"
    assert "lichnerowicz_bundle_curvature_remainder" in report.blocking_components


def test_downstream_closures_do_not_upgrade_from_conditional_operator_assumption():
    comm = build_projector_commutator_closure_report()
    projector = build_projector_graph_domain_closure_report()
    lower = build_lower_bound_transfer_closure_report()

    assert comm.final_status == "PROJECTOR_COMMUTATORS_CONDITIONAL"
    assert comm.theorem_complete is False
    assert projector.final_status == "PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL"
    assert projector.theorem_complete is False
    assert lower.final_status == "HT_LOWER_BOUND_TRANSFER_CONDITIONAL"
    assert lower.theorem_complete is False


def test_index_mirror_stay_conditional_without_complete_operator_proofs():
    index = build_index_theorem_final_proof_report()
    mirror = build_mirror_exclusion_final_proof_report()

    assert index.final_status == "INDEX_THEOREM_CONDITIONAL"
    assert index.exactly_one_each_sector is True
    assert index.theorem_complete is False
    assert mirror.final_status == "MIRROR_EXCLUSION_CONDITIONAL"
    assert mirror.theorem_complete is False


def test_full_ht_closure_uses_only_allowed_final_outcomes():
    report = build_full_ht_theorem_closure_report()
    allowed = {
        FULL_HT_THEOREM_PROVEN,
        STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
        BHSM_THEOREM_FAILURE,
    }

    assert report.final_result in allowed
    assert report.final_result == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert report.theorem_complete is False
    assert report.single_named_gap == COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP
    assert report.recommended_next_branch == "bhsm-v2.9-complete-bundle-connection-curvature"


def test_full_bhsm_completion_uses_only_allowed_final_outcomes():
    report = build_full_bhsm_theorem_completion_report()
    allowed = {
        FULL_BHSM_THEOREM_PACKAGE_COMPLETE,
        STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP,
        BHSM_THEOREM_FAILURE,
    }

    assert report.final_result in allowed
    assert report.final_result == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert report.final_paper_allowed is False
    assert report.theorem_complete is False
    assert report.single_named_gap == COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP


def test_if_full_ht_proven_then_all_six_blockers_are_closed():
    report = build_full_ht_theorem_closure_report()
    if report.final_result == FULL_HT_THEOREM_PROVEN:
        assert report.complete_operator_status == "COMPLETE_OPERATOR_IDENTIFICATION_PROVEN"
        assert report.commutator_status == "PROJECTOR_COMMUTATORS_CONTROLLED"
        assert report.projector_graph_domain_status == "PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN"
        assert report.lower_bound_transfer_status == "HT_LOWER_BOUND_TRANSFER_PROVEN"
        assert report.index_status == "INDEX_THEOREM_PROVEN"
        assert report.mirror_status == "MIRROR_EXCLUSION_PROVEN"
    else:
        assert report.theorem_complete is False


def test_if_full_bhsm_complete_no_required_node_is_conditional():
    report = build_full_bhsm_theorem_completion_report()
    if report.final_result == FULL_BHSM_THEOREM_PACKAGE_COMPLETE:
        text = json.dumps(report.__dict__)
        assert "CONDITIONAL" not in text
        assert "OPEN" not in text
    else:
        assert report.final_paper_allowed is False


def test_v25_exports_generate(tmp_path):
    paths = {
        "operator_md": tmp_path / "operator.md",
        "operator_json": tmp_path / "operator.json",
        "comm_md": tmp_path / "comm.md",
        "comm_json": tmp_path / "comm.json",
        "projector_md": tmp_path / "projector.md",
        "projector_json": tmp_path / "projector.json",
        "lower_md": tmp_path / "lower.md",
        "lower_json": tmp_path / "lower.json",
        "index_md": tmp_path / "index.md",
        "index_json": tmp_path / "index.json",
        "mirror_md": tmp_path / "mirror.md",
        "mirror_json": tmp_path / "mirror.json",
        "ht_md": tmp_path / "ht.md",
        "ht_json": tmp_path / "ht.json",
        "bhsm_md": tmp_path / "bhsm.md",
        "bhsm_json": tmp_path / "bhsm.json",
    }
    export_complete_operator_identification_closure_markdown(paths["operator_md"])
    export_complete_operator_identification_closure_json(paths["operator_json"])
    export_projector_commutator_closure_markdown(paths["comm_md"])
    export_projector_commutator_closure_json(paths["comm_json"])
    export_projector_graph_domain_closure_markdown(paths["projector_md"])
    export_projector_graph_domain_closure_json(paths["projector_json"])
    export_lower_bound_transfer_closure_markdown(paths["lower_md"])
    export_lower_bound_transfer_closure_json(paths["lower_json"])
    export_index_theorem_final_proof_markdown(paths["index_md"])
    export_index_theorem_final_proof_json(paths["index_json"])
    export_mirror_exclusion_final_proof_markdown(paths["mirror_md"])
    export_mirror_exclusion_final_proof_json(paths["mirror_json"])
    export_full_ht_theorem_closure_markdown(paths["ht_md"])
    export_full_ht_theorem_closure_json(paths["ht_json"])
    export_full_bhsm_theorem_completion_markdown(paths["bhsm_md"])
    export_full_bhsm_theorem_completion_json(paths["bhsm_json"])

    assert json.loads(paths["operator_json"].read_text())["final_status"] == COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL
    assert json.loads(paths["ht_json"].read_text())["final_result"] == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP
    assert json.loads(paths["bhsm_json"].read_text())["final_result"] == STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP


def test_requested_v25_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/full_ht_theorem_closure_report.md",
        "theory/full_ht_theorem_closure_report.json",
        "theory/complete_operator_identification_closure_report.md",
        "theory/complete_operator_identification_closure_report.json",
        "theory/projector_commutator_closure_report.md",
        "theory/projector_commutator_closure_report.json",
        "theory/projector_graph_domain_closure_report.md",
        "theory/projector_graph_domain_closure_report.json",
        "theory/lower_bound_transfer_closure_report.md",
        "theory/lower_bound_transfer_closure_report.json",
        "theory/index_theorem_final_proof_report.md",
        "theory/index_theorem_final_proof_report.json",
        "theory/mirror_exclusion_final_proof_report.md",
        "theory/mirror_exclusion_final_proof_report.json",
        "theory/full_bhsm_theorem_completion_report.md",
        "theory/full_bhsm_theorem_completion_report.json",
        "manuscript/BHSM_v2_5_full_ht_theorem_closure_note.md",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP in root.joinpath("theory/full_bhsm_theorem_completion_report.md").read_text()


def test_v25_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "full_ht_theorem_closure.py",
            "complete_operator_identification_closure.py",
            "projector_commutator_closure.py",
            "projector_graph_domain_closure.py",
            "lower_bound_transfer_closure.py",
            "index_theorem_final_proof.py",
            "mirror_exclusion_final_proof.py",
            "full_bhsm_theorem_completion.py",
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
    )
    assert all(token not in sources for token in forbidden)


def test_v25_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_full_bhsm_theorem_completion_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
