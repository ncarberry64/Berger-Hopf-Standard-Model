import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from boundary_mirror_channel import (
    BOUNDARY_MIRROR_CHANNEL_CONDITIONAL,
    build_boundary_mirror_channel_report,
    export_boundary_mirror_channel_json,
    export_boundary_mirror_channel_markdown,
)
from chiral_projector_closure import (
    CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL,
    build_chiral_projector_closure_report,
    export_chiral_projector_closure_json,
    export_chiral_projector_closure_markdown,
)
from constants import S_OVERLAP
from full_mirror_exclusion import (
    MIRROR_EXCLUSION_CONDITIONAL,
    build_full_mirror_exclusion_report,
    export_full_mirror_exclusion_json,
    export_full_mirror_exclusion_markdown,
)
from higgs_u1_mirror_channel import (
    HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL,
    build_higgs_u1_mirror_channel_report,
    export_higgs_u1_mirror_channel_json,
    export_higgs_u1_mirror_channel_markdown,
)
from ht_domain_bridge import build_ht_domain_bridge_report
from index_mirror_closure_decision import (
    HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY,
    build_index_mirror_closure_decision,
    export_index_mirror_closure_decision_json,
    export_index_mirror_closure_decision_markdown,
)
from index_sector_count import SECTOR_COUNT_PROVEN, build_sector_count_report, export_sector_count_json, export_sector_count_markdown
from topological_index_operator import (
    INDEX_THEOREM_CONDITIONAL,
    build_topological_index_operator_report,
    export_topological_index_operator_json,
    export_topological_index_operator_markdown,
)
from twisted_dirac_index_closure import (
    build_twisted_dirac_index_closure_report,
    export_twisted_dirac_index_closure_json,
    export_twisted_dirac_index_closure_markdown,
)


def test_sector_count_is_lepton_up_down_not_coordinate_first():
    report = build_sector_count_report()

    assert report.status == SECTOR_COUNT_PROVEN
    assert report.one_each_lepton_up_down is True
    assert report.duplicate_lepton_coordinate_artifact is False
    assert report.missing_up_down_state is False
    assert report.extra_visible_protected_state is False
    assert report.old_coordinate_first_kernel_used is False


def test_index_theorem_is_conditional_not_proven():
    topo = build_topological_index_operator_report()
    closure = build_twisted_dirac_index_closure_report()

    assert topo.status == INDEX_THEOREM_CONDITIONAL
    assert topo.scaffold_index == 3
    assert topo.exactly_three_visible_states is True
    assert topo.theorem_complete is False
    assert closure.status == INDEX_THEOREM_CONDITIONAL
    assert closure.theorem_complete is False
    assert closure.open_obligations


def test_mirror_channels_are_conditional_not_overclaimed():
    chiral = build_chiral_projector_closure_report()
    higgs = build_higgs_u1_mirror_channel_report()
    boundary = build_boundary_mirror_channel_report()
    mirror = build_full_mirror_exclusion_report()

    assert chiral.status == CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL
    assert higgs.status == HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL
    assert boundary.status == BOUNDARY_MIRROR_CHANNEL_CONDITIONAL
    assert mirror.status == MIRROR_EXCLUSION_CONDITIONAL
    assert mirror.theorem_complete is False
    assert "not marked MIRROR_EXCLUSION_PROVEN" in " ".join(mirror.limitations)


def test_ht_dependency_moves_to_domain_stability_not_full_theorem():
    decision = build_index_mirror_closure_decision()
    bridge = build_ht_domain_bridge_report()

    assert decision.ht_dependency_status == HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY
    assert decision.theorem_complete is False
    assert bridge.domain_bridge_status == HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY
    assert bridge.theorem_complete is False


def test_v23_exports_generate(tmp_path):
    outputs = {
        "topo_md": tmp_path / "topo.md",
        "topo_json": tmp_path / "topo.json",
        "index_md": tmp_path / "index.md",
        "index_json": tmp_path / "index.json",
        "sector_md": tmp_path / "sector.md",
        "sector_json": tmp_path / "sector.json",
        "mirror_md": tmp_path / "mirror.md",
        "mirror_json": tmp_path / "mirror.json",
        "chiral_md": tmp_path / "chiral.md",
        "chiral_json": tmp_path / "chiral.json",
        "higgs_md": tmp_path / "higgs.md",
        "higgs_json": tmp_path / "higgs.json",
        "boundary_md": tmp_path / "boundary.md",
        "boundary_json": tmp_path / "boundary.json",
        "decision_md": tmp_path / "decision.md",
        "decision_json": tmp_path / "decision.json",
    }
    export_topological_index_operator_markdown(outputs["topo_md"])
    export_topological_index_operator_json(outputs["topo_json"])
    export_twisted_dirac_index_closure_markdown(outputs["index_md"])
    export_twisted_dirac_index_closure_json(outputs["index_json"])
    export_sector_count_markdown(outputs["sector_md"])
    export_sector_count_json(outputs["sector_json"])
    export_full_mirror_exclusion_markdown(outputs["mirror_md"])
    export_full_mirror_exclusion_json(outputs["mirror_json"])
    export_chiral_projector_closure_markdown(outputs["chiral_md"])
    export_chiral_projector_closure_json(outputs["chiral_json"])
    export_higgs_u1_mirror_channel_markdown(outputs["higgs_md"])
    export_higgs_u1_mirror_channel_json(outputs["higgs_json"])
    export_boundary_mirror_channel_markdown(outputs["boundary_md"])
    export_boundary_mirror_channel_json(outputs["boundary_json"])
    export_index_mirror_closure_decision_markdown(outputs["decision_md"])
    export_index_mirror_closure_decision_json(outputs["decision_json"])

    assert json.loads(outputs["topo_json"].read_text())["status"] == INDEX_THEOREM_CONDITIONAL
    assert json.loads(outputs["index_json"].read_text())["status"] == INDEX_THEOREM_CONDITIONAL
    assert json.loads(outputs["sector_json"].read_text())["status"] == SECTOR_COUNT_PROVEN
    assert json.loads(outputs["mirror_json"].read_text())["status"] == MIRROR_EXCLUSION_CONDITIONAL
    assert json.loads(outputs["chiral_json"].read_text())["status"] == CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL
    assert json.loads(outputs["higgs_json"].read_text())["status"] == HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL
    assert json.loads(outputs["boundary_json"].read_text())["status"] == BOUNDARY_MIRROR_CHANNEL_CONDITIONAL
    assert json.loads(outputs["decision_json"].read_text())["ht_dependency_status"] == HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY


def test_requested_v23_report_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/topological_index_operator_report.md",
        "theory/topological_index_operator_report.json",
        "theory/twisted_dirac_index_closure_report.md",
        "theory/twisted_dirac_index_closure_report.json",
        "theory/sector_count_report.md",
        "theory/sector_count_report.json",
        "theory/full_mirror_exclusion_report.md",
        "theory/full_mirror_exclusion_report.json",
        "theory/chiral_projector_closure_report.md",
        "theory/chiral_projector_closure_report.json",
        "theory/higgs_u1_boundary_mirror_report.md",
        "theory/higgs_u1_boundary_mirror_report.json",
        "theory/index_mirror_closure_decision.md",
        "theory/index_mirror_closure_decision.json",
        "manuscript/BHSM_v2_3_index_mirror_exclusion_note.md",
        "notebooks/53_index_mirror_exclusion.ipynb",
    )

    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []
    assert "HIGGS_U1_BOUNDARY_MIRROR_CHANNEL_CONDITIONAL" in root.joinpath("theory/higgs_u1_boundary_mirror_report.md").read_text()
    assert "False" in root.joinpath("manuscript/BHSM_v2_3_index_mirror_exclusion_note.md").read_text()


def test_v23_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    sources = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "topological_index_operator.py",
            "twisted_dirac_index_closure.py",
            "index_sector_count.py",
            "full_mirror_exclusion.py",
            "chiral_projector_closure.py",
            "higgs_u1_mirror_channel.py",
            "boundary_mirror_channel.py",
            "index_mirror_closure_decision.py",
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


def test_v23_does_not_change_frozen_outputs():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_index_mirror_closure_decision()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    changed = [row for row in compare_bhsm_v1_branches()["rows"] if row["changed"]]

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert changed == [{"quantity": "c/t", "bare": 0.008310500554068288, "dressed": 0.004155250277034144, "changed": True}]
