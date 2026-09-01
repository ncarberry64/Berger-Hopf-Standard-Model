import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from coordinate_protected_block import coordinate_protected_states
from mirror_exclusion_derivation import build_mirror_exclusion_report
from zero_mode_alignment import (
    ALIGNED,
    OPEN_ALIGNMENT_GAP,
    build_alignment_audit_report,
    build_zero_mode_alignment_maps,
    export_zero_mode_alignment_json,
    export_zero_mode_alignment_markdown,
    formal_zero_mode_labels,
)


def test_exactly_three_formal_and_coordinate_protected_states_are_present():
    formal = formal_zero_mode_labels()
    coordinate = coordinate_protected_states()

    assert len(formal) == 3
    assert {item.sector for item in formal} == {"lepton", "up", "down"}
    assert all(item.chirality == -1 for item in formal)
    assert all(item.boundary_policy_satisfied for item in formal)
    assert all(item.boundary_policy_status == "HEAVY_MODE_PROTECTED_SEPARATELY" for item in formal)
    assert len(coordinate) == 3
    assert all(item.coordinate_protected for item in coordinate)
    assert all(item.heat_lift_preserves for item in coordinate)
    assert all(item.sector_coupling_vanishes for item in coordinate)


def test_alignment_maps_report_one_aligned_and_two_open_gaps():
    maps = build_zero_mode_alignment_maps()
    by_sector = {item.formal_label.sector: item for item in maps}

    assert set(by_sector) == {"lepton", "up", "down"}
    assert by_sector["lepton"].status == ALIGNED
    assert by_sector["lepton"].matching_coordinate_index == 0
    assert by_sector["up"].status == OPEN_ALIGNMENT_GAP
    assert by_sector["up"].matching_coordinate_index == 18
    assert by_sector["down"].status == OPEN_ALIGNMENT_GAP
    assert by_sector["down"].matching_coordinate_index == 36
    assert all(item.sector_matches for item in maps)
    assert all(item.chirality_matches for item in maps)


def test_alignment_audit_keeps_open_alignment_gap_visible():
    report = build_alignment_audit_report()

    assert report.all_three_formal_labels_present is True
    assert report.all_three_coordinate_states_present is True
    assert report.one_to_one_alignment is False
    assert report.open_alignment_gap_remains is True
    assert report.mirror_exclusion_intact is True
    assert report.theorem_complete is False
    assert any(not criterion.passes for criterion in report.criteria)


def test_mirror_exclusion_remains_intact_after_alignment_audit():
    mirror_report = build_mirror_exclusion_report()
    alignment_report = build_alignment_audit_report()

    assert mirror_report.excluded_count == 3
    assert mirror_report.open_mirror_risk_count == 0
    assert alignment_report.mirror_exclusion_intact is True


def test_no_forbidden_empirical_modules_are_imported_by_alignment_scaffold():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("coordinate_protected_block.py", "zero_mode_alignment.py")
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


def test_zero_mode_alignment_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_alignment_audit_report()

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


def test_zero_mode_alignment_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "alignment.md"
    json_path = tmp_path / "alignment.json"

    export_zero_mode_alignment_markdown(md_path)
    export_zero_mode_alignment_json(json_path)

    text = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert "OPEN_ALIGNMENT_GAP" in text
    assert data["one_to_one_alignment"] is False
    assert data["open_alignment_gap_remains"] is True
    assert data["mirror_exclusion_intact"] is True
    assert data["theorem_complete"] is False


def test_generated_zero_mode_alignment_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "zero_mode_alignment_report.md",
        root / "theory" / "zero_mode_alignment_report.json",
        root / "manuscript" / "v1_3j_zero_mode_alignment_note.md",
        root / "notebooks" / "32_zero_mode_alignment.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    md_text = artifact_paths[0].read_text()
    data = json.loads(artifact_paths[1].read_text())
    note_text = artifact_paths[2].read_text()

    assert "OPEN_ALIGNMENT_GAP" in md_text
    assert data["one_to_one_alignment"] is False
    assert data["open_alignment_gap_remains"] is True
    assert data["theorem_complete"] is False
    assert "does not prove the full" in note_text
    assert "fully proven" not in note_text.lower()
