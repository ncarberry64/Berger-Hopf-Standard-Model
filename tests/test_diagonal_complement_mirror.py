import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from diagonal_complement_bound import (
    build_complement_lower_bound_report,
    diagonal_mode_inventory,
    export_diagonal_complement_bound_json,
    export_diagonal_complement_bound_markdown,
    first_diagonal_complement_mode,
)
from mirror_mode_exclusion import (
    OPEN_MIRROR_RISK,
    build_mirror_mode_audit_report,
    export_mirror_mode_audit_json,
    export_mirror_mode_audit_markdown,
    generate_mirror_mode_candidates,
)
from spectral_bounds import required_dirac_lower_bound
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac_index_audit import (
    build_twisted_dirac_index_audit,
    export_twisted_dirac_index_audit_json,
    export_twisted_dirac_index_audit_markdown,
)
from zero_mode_index import protected_family_zero_modes


def test_diagonal_inventory_contains_modes_and_protected_scaffold_flags():
    rows = diagonal_mode_inventory()

    assert rows
    assert sum(row.coordinate_protected for row in rows) == 3
    assert sum(row.formal_zero_candidate for row in rows) == 3
    assert any(row.included_in_complement_bound for row in rows)
    assert all(row.limitations for row in rows)


def test_first_diagonal_complement_mode_clears_required_bound():
    report = build_complement_lower_bound_report()
    first = first_diagonal_complement_mode()
    required = required_dirac_lower_bound(natural_lambda2(), MU_H)

    assert isclose(report.required_dirac_lower_bound, 0.8038064161349437, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(report.required_dirac_lower_bound, required, rel_tol=0.0, abs_tol=1e-12)
    assert report.first_complement_mode == first
    assert report.finite_coordinate_complement_lower_bound > report.required_dirac_lower_bound
    assert report.passes_required_bound is True
    assert report.bound_status == "FINITE_DIAGONAL_BOUND_PASSES"
    assert report.theorem_complete is False


def test_diagonal_report_marks_formal_coordinate_alignment_gap_open():
    report = build_complement_lower_bound_report()

    assert report.coordinate_zero_mode_count == 3
    assert report.formal_zero_candidate_count == 3
    assert report.formal_coordinate_alignment_status in {"OPEN_ALIGNMENT_GAP", "FINITE_COORDINATE_ALIGNED"}
    assert report.formal_coordinate_alignment_status == "OPEN_ALIGNMENT_GAP"
    assert any("not yet proven identical" in item for item in report.limitations)


def test_mirror_candidates_are_generated_and_classified_explicitly():
    mirrors = generate_mirror_mode_candidates()
    protected = protected_family_zero_modes()

    assert len(mirrors) == len(protected) == 3
    assert {mirror.sector for mirror in mirrors} == {"lepton", "up", "down"}
    assert all(mirror.chirality == 1 for mirror in mirrors)
    assert all(mirror.present_in_finite_basis for mirror in mirrors)
    assert all(mirror.classification for mirror in mirrors)
    assert all(mirror.classification == OPEN_MIRROR_RISK for mirror in mirrors)


def test_open_mirror_risk_is_reported_not_hidden():
    report = build_mirror_mode_audit_report()

    assert report.open_mirror_risk_count == 3
    assert report.all_mirrors_excluded is False
    assert report.mirror_exclusion_status == OPEN_MIRROR_RISK
    assert report.theorem_complete is False
    assert any(criterion.status == "OPEN" for criterion in report.criteria)


def test_twisted_dirac_index_audit_separates_scaffold_and_topological_status():
    audit = build_twisted_dirac_index_audit()

    assert audit.finite_scaffold_index == 3
    assert audit.boundary_functional_index == 3
    assert audit.topological_index_assumption == 3
    assert audit.target_index == 3
    assert audit.target_kernel_dimension == 3
    assert audit.diagonal_bound_clears_required is True
    assert audit.open_mirror_risk_count == 3
    assert audit.index_status == "INDEX_SCAFFOLD"
    assert audit.full_theorem_status == "OPEN"
    assert audit.theorem_complete is False


def test_no_forbidden_empirical_modules_are_imported_by_diagonal_mirror_scaffold():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("diagonal_complement_bound.py", "mirror_mode_exclusion.py", "twisted_dirac_index_audit.py")
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


def test_diagonal_mirror_audit_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_twisted_dirac_index_audit()

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


def test_diagonal_mirror_exports_generate_cleanly(tmp_path):
    diag_md = tmp_path / "diag.md"
    diag_json = tmp_path / "diag.json"
    mirror_md = tmp_path / "mirror.md"
    mirror_json = tmp_path / "mirror.json"
    audit_md = tmp_path / "audit.md"
    audit_json = tmp_path / "audit.json"

    export_diagonal_complement_bound_markdown(diag_md)
    export_diagonal_complement_bound_json(diag_json)
    export_mirror_mode_audit_markdown(mirror_md)
    export_mirror_mode_audit_json(mirror_json)
    export_twisted_dirac_index_audit_markdown(audit_md)
    export_twisted_dirac_index_audit_json(audit_json)

    assert "FINITE_DIAGONAL_BOUND_PASSES" in diag_md.read_text()
    assert json.loads(diag_json.read_text())["passes_required_bound"] is True
    assert OPEN_MIRROR_RISK in mirror_md.read_text()
    assert json.loads(mirror_json.read_text())["open_mirror_risk_count"] == 3
    assert "INDEX_SCAFFOLD" in audit_md.read_text()
    assert json.loads(audit_json.read_text())["theorem_complete"] is False


def test_generated_diagonal_mirror_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "diagonal_complement_bound_report.md",
        root / "theory" / "diagonal_complement_bound_report.json",
        root / "theory" / "mirror_mode_exclusion_report.md",
        root / "theory" / "mirror_mode_exclusion_report.json",
        root / "theory" / "twisted_dirac_index_audit.md",
        root / "theory" / "twisted_dirac_index_audit.json",
        root / "manuscript" / "v1_3h_diagonal_mirror_note.md",
        root / "notebooks" / "30_diagonal_complement_mirror_audit.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    diag_text = artifact_paths[0].read_text()
    mirror_text = artifact_paths[2].read_text()
    audit_data = json.loads(artifact_paths[5].read_text())
    note_text = artifact_paths[6].read_text()

    assert "FINITE_DIAGONAL_BOUND_PASSES" in diag_text
    assert OPEN_MIRROR_RISK in mirror_text
    assert audit_data["open_mirror_risk_count"] == 3
    assert audit_data["theorem_complete"] is False
    assert "does not prove the full theorem" in note_text
    assert "fully proven" not in note_text.lower()
