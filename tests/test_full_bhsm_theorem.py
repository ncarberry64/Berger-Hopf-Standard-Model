import json
from math import isclose
from pathlib import Path

from bhsm_theorem_completion_decision import (
    BHSM_THEOREM_CANDIDATE_WITH_OPEN_ASSUMPTIONS,
    build_bhsm_theorem_completion_decision,
    export_bhsm_theorem_completion_decision_json,
    export_bhsm_theorem_completion_decision_markdown,
)
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from full_bhsm_theorem import (
    BHSM_THEOREM_PACKAGE_INCOMPLETE,
    build_full_bhsm_theorem_report,
    export_full_bhsm_theorem_json,
    export_full_bhsm_theorem_markdown,
    export_full_bhsm_theorem_obligations_markdown,
)
from full_operator_domain import build_full_operator_domain_report
from mirror_exclusion_theorem import MIRROR_EXCLUSION_CONDITIONAL, build_mirror_exclusion_theorem_report
from scalar_full_action_theorem import SCALAR_FULL_ACTION_PROOF_OPEN, build_scalar_full_action_theorem_report
from twisted_dirac_index_theorem import INDEX_THEOREM_CONDITIONAL, build_twisted_dirac_index_theorem_report


def test_wrapper_theorem_reports_remain_open_where_proofs_are_missing():
    domain = build_full_operator_domain_report()
    index = build_twisted_dirac_index_theorem_report()
    mirror = build_mirror_exclusion_theorem_report()
    scalar = build_scalar_full_action_theorem_report()

    assert domain.theorem_complete is False
    assert index.status == INDEX_THEOREM_CONDITIONAL
    assert mirror.status == MIRROR_EXCLUSION_CONDITIONAL
    assert scalar.status == SCALAR_FULL_ACTION_PROOF_OPEN
    assert scalar.exactly_one_higgs_projection is True
    assert scalar.open_scalar_risk_count == 0
    assert mirror.chiral_channel_excludes_all_generated is True
    assert mirror.higgs_u1_channel_closed is False


def test_full_bhsm_theorem_package_is_incomplete_not_overclaimed():
    report = build_full_bhsm_theorem_report()

    assert report.status == BHSM_THEOREM_PACKAGE_INCOMPLETE
    assert report.theorem_complete is False
    assert report.final_paper_allowed is False
    assert report.frozen_outputs_changed is False
    node_ids = {node.id for node in report.nodes}
    assert {"operator_domain", "ht_gap", "index", "mirror_exclusion", "scalar_topographic", "virtual_dressing", "qcd_rg", "unified_action"} <= node_ids
    assert any("topological index" in item for item in report.open_obligations)


def test_theorem_completion_decision_blocks_final_paper():
    decision = build_bhsm_theorem_completion_decision()

    assert decision.final_status == BHSM_THEOREM_CANDIDATE_WITH_OPEN_ASSUMPTIONS
    assert decision.final_paper_allowed is False
    assert decision.zenodo_release_allowed is False
    assert "Do not prepare final paper" in decision.exact_next_action


def test_theorem_completion_exports(tmp_path):
    report_md = tmp_path / "full.md"
    report_json = tmp_path / "full.json"
    obligations_md = tmp_path / "obligations.md"
    decision_md = tmp_path / "decision.md"
    decision_json = tmp_path / "decision.json"

    export_full_bhsm_theorem_markdown(report_md)
    export_full_bhsm_theorem_json(report_json)
    export_full_bhsm_theorem_obligations_markdown(obligations_md)
    export_bhsm_theorem_completion_decision_markdown(decision_md)
    export_bhsm_theorem_completion_decision_json(decision_json)

    assert json.loads(report_json.read_text())["status"] == BHSM_THEOREM_PACKAGE_INCOMPLETE
    assert json.loads(decision_json.read_text())["final_paper_allowed"] is False
    assert "Open Obligations" in obligations_md.read_text()
    assert "BHSM Theorem Completion Decision" in decision_md.read_text()


def test_completion_decision_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_bhsm_theorem_completion_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]


def test_generated_completion_artifacts_exist_and_are_conservative():
    root = Path(__file__).parents[1]
    paths = (
        root / "theory" / "full_bhsm_theorem_report.md",
        root / "theory" / "full_bhsm_theorem_report.json",
        root / "theory" / "full_bhsm_theorem_obligations.md",
        root / "theory" / "bhsm_theorem_completion_decision.md",
        root / "theory" / "bhsm_theorem_completion_decision.json",
    )
    for path in paths:
        assert path.exists(), path
    text = "\n".join(path.read_text() for path in paths if path.suffix == ".md")
    assert "FULL_BHSM_THEOREM_PACKAGE_COMPLETE" not in json.loads(paths[3].with_suffix(".json").read_text()).get("final_status", "")
    assert "Final paper allowed: `False`" in text
