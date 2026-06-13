import json
from math import isclose

from bhsm_v1 import compare_bhsm_v1_branches
from ckm_mixing_dressing_audit import (
    STATUS,
    best_candidate,
    build_ckm_mixing_dressing_audit,
    candidate_powers,
    export_ckm_mixing_dressing_audit_json,
    export_ckm_mixing_dressing_audit_markdown,
)


def _residuals(row):
    return {residual.quantity: residual for residual in row.residuals}


def test_predeclared_candidates_only():
    candidates = candidate_powers()

    assert [candidate.label for candidate in candidates] == [
        "no_correction",
        "Z^(1/4)",
        "Z^(1/8)",
        "Z^(1/16)",
    ]
    assert all(candidate.status == STATUS for candidate in candidates)


def test_dressing_scope_changes_only_theta23_channel():
    rows = build_ckm_mixing_dressing_audit()
    baseline = rows[0]

    for row in rows[1:]:
        assert isclose(row.sin_theta_12, baseline.sin_theta_12)
        assert row.sin_theta_23 < baseline.sin_theta_23
        assert isclose(row.sin_theta_13, baseline.sin_theta_13)
        assert isclose(row.delta, baseline.delta)


def test_candidate_rows_report_all_matrix_and_j_residuals():
    rows = build_ckm_mixing_dressing_audit()
    expected = {"Vud", "Vus", "Vub", "Vcd", "Vcs", "Vcb", "Vtd", "Vts", "Vtb", "J_CKM"}

    for row in rows:
        residuals = _residuals(row)
        assert set(residuals) == expected
        assert all(residual.relative_error >= 0 for residual in residuals.values())
        assert len(row.matrix_magnitudes) == 3
        assert all(len(matrix_row) == 3 for matrix_row in row.matrix_magnitudes)


def test_fractional_z_candidates_improve_vcb_vts_without_claiming_adoption():
    rows = build_ckm_mixing_dressing_audit()
    baseline = rows[0]
    best = best_candidate(rows)

    assert baseline.candidate.label == "no_correction"
    assert best.candidate.label in {"Z^(1/4)", "Z^(1/8)", "Z^(1/16)"}
    assert best.improves_vcb_vts is True
    assert best.candidate.status == "EXPLORATORY_CANDIDATE"


def test_exports_render_and_keep_freeze_warning(tmp_path):
    md_path = tmp_path / "ckm_mixing_dressing_candidate_audit.md"
    json_path = tmp_path / "ckm_mixing_dressing_candidate_audit.json"

    export_ckm_mixing_dressing_audit_markdown(md_path)
    export_ckm_mixing_dressing_audit_json(json_path)

    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert "EXPLORATORY_CANDIDATE" in markdown
    assert "Any adopted mixing-dressing rule must be frozen before future external comparisons." in markdown
    assert payload["status"] == "EXPLORATORY_CANDIDATE"
    assert len(payload["rows"]) == 4


def test_frozen_branches_remain_unchanged():
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
