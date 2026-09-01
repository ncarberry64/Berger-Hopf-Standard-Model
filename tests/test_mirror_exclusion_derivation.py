import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from chiral_projector import EXCLUDED_BY_CHIRAL_PROJECTOR, evaluate_chiral_projection
from constants import S_OVERLAP
from higgs_u1_boundary_phase import OPEN as HIGGS_OPEN
from higgs_u1_boundary_phase import evaluate_higgs_u1_phase
from mirror_exclusion_derivation import (
    EXCLUDED,
    OPEN,
    build_mirror_exclusion_report,
    derive_mirror_exclusion,
    evaluate_boundary_functional,
    export_mirror_exclusion_report_json,
    export_mirror_exclusion_report_markdown,
)


def test_all_three_mirror_candidates_are_analyzed_with_three_channels():
    derivations = derive_mirror_exclusion()

    assert len(derivations) == 3
    assert {item.mirror_id for item in derivations} == {"mirror_lepton", "mirror_up", "mirror_down"}
    for item in derivations:
        assert item.chiral_projector_result.status
        assert item.higgs_u1_phase_result.status
        assert item.boundary_functional_result.status
        assert item.theorem_complete is False


def test_chiral_projector_excludes_opposite_chirality_from_internal_structure():
    for sector in ("lepton", "up", "down"):
        rule = evaluate_chiral_projection(sector, candidate_chirality=1)
        assert rule.protected_chirality == -1
        assert rule.candidate_chirality == 1
        assert rule.status == EXCLUDED_BY_CHIRAL_PROJECTOR
        assert rule.derived_from_internal_structure is True


def test_higgs_u1_and_boundary_channels_remain_conservative_open_channels():
    for sector in ("lepton", "up", "down"):
        higgs = evaluate_higgs_u1_phase(sector, candidate_chirality=1)
        boundary = evaluate_boundary_functional(sector, k=0, j=0, q=0)

        assert higgs.status == HIGGS_OPEN
        assert higgs.derived_from_internal_structure is False
        assert boundary.status == OPEN
        assert boundary.derived_from_internal_structure is False
        assert boundary.omega_value == 0
        assert boundary.residual == -boundary.target


def test_final_mirror_classification_is_excluded_with_explicit_source_channel():
    report = build_mirror_exclusion_report()

    assert report.excluded_count == 3
    assert report.open_mirror_risk_count == 0
    assert report.scaffold_index == 3
    assert report.theorem_complete is False
    for item in report.derivations:
        assert item.final_classification == EXCLUDED
        assert item.exclusion_channels == (EXCLUDED_BY_CHIRAL_PROJECTOR,)


def test_no_forbidden_empirical_modules_are_imported_by_mirror_derivation():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("chiral_projector.py", "higgs_u1_boundary_phase.py", "mirror_exclusion_derivation.py")
    )
    forbidden = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "mass_ratio(",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in source for token in forbidden)


def test_mirror_derivation_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_mirror_exclusion_report()

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


def test_mirror_exclusion_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "mirror_exclusion.md"
    json_path = tmp_path / "mirror_exclusion.json"

    export_mirror_exclusion_report_markdown(md_path)
    export_mirror_exclusion_report_json(json_path)

    text = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert EXCLUDED_BY_CHIRAL_PROJECTOR in text
    assert data["excluded_count"] == 3
    assert data["open_mirror_risk_count"] == 0
    assert data["theorem_complete"] is False


def test_generated_mirror_exclusion_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "mirror_exclusion_derivation_report.md",
        root / "theory" / "mirror_exclusion_derivation_report.json",
        root / "manuscript" / "v1_3i_mirror_exclusion_note.md",
        root / "notebooks" / "31_mirror_exclusion_derivation.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    md_text = artifact_paths[0].read_text()
    data = json.loads(artifact_paths[1].read_text())
    note_text = artifact_paths[2].read_text()

    assert EXCLUDED_BY_CHIRAL_PROJECTOR in md_text
    assert data["excluded_count"] == 3
    assert data["open_mirror_risk_count"] == 0
    assert data["theorem_complete"] is False
    assert "does not prove the full `H_T` theorem" in note_text
    assert "fully proven" not in note_text.lower()
