import json
from math import isclose
from pathlib import Path

import numpy as np

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from formal_kernel_operator import (
    DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
    DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
    build_formal_kernel_dirac_matrix,
    default_formal_kernel_operator_config,
    export_formal_kernel_operator_json,
    export_formal_kernel_operator_markdown,
    formal_kernel_coordinates,
    formal_kernel_projectors,
    formal_kernel_sector_coupling_block,
    operator_variant_summary,
    protection_term,
)
from level2_formal_kernel_ht import (
    FORMAL_KERNEL_GAP_RESTORED,
    build_formal_kernel_correction_audit,
    build_formal_kernel_ht_report,
    export_formal_kernel_ht_gap_json,
    export_formal_kernel_ht_gap_markdown,
    legacy_vs_formal_gap_table,
    scan_formal_kernel_ht_gap,
)
from spectral_gap import MU_H


def test_corrected_variant_uses_formal_kernel_not_coordinate_first_block():
    summary = operator_variant_summary()

    assert summary["old_variant"] == DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST
    assert summary["new_variant"] == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert summary["old_protected_coordinates"] == (0, 1, 2)
    assert summary["formal_protected_coordinates"] == (0, 18, 36)
    assert summary["protected_sectors"] == ("lepton", "up", "down")
    assert summary["avoids_old_lepton_only_modes"] is True


def test_formal_kernel_projector_rank_and_identities():
    term = protection_term()
    p0, p_perp = formal_kernel_projectors()

    assert term.protected_coordinates == (0, 18, 36)
    assert term.projector_rank == 3
    assert term.idempotent is True
    assert term.orthogonal_to_complement is True
    assert np.allclose(p0 @ p0, p0)
    assert np.allclose(p0 @ p_perp, np.zeros_like(p0))


def test_corrected_formal_kernel_matrix_is_symmetric_and_protects_kernel():
    matrix = build_formal_kernel_dirac_matrix()
    d2 = matrix.T @ matrix

    assert np.allclose(matrix, matrix.T)
    for index in formal_kernel_coordinates():
        assert np.allclose(matrix[index, :], 0.0)
        assert np.allclose(matrix[:, index], 0.0)
        assert d2[index, index] == 0.0
    assert not np.allclose(matrix[1, :], 0.0)
    assert not np.allclose(matrix[2, :], 0.0)


def test_sector_coupling_vanishes_on_corrected_formal_kernel_block():
    block = formal_kernel_sector_coupling_block()

    for index in (0, 18, 36):
        assert np.allclose(block[index, :], 0.0)
        assert np.allclose(block[:, index], 0.0)


def test_formal_kernel_gap_is_recomputed_and_restored():
    audit = build_formal_kernel_correction_audit()
    report = audit.ht_report

    assert audit.status == FORMAL_KERNEL_GAP_RESTORED
    assert audit.formal_kernel_protected is True
    assert audit.sector_coupling_vanishes_on_formal_kernel is True
    assert report.model_level == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert report.protected_coordinates == (0, 18, 36)
    assert report.protected_sectors == ("lepton", "up", "down")
    assert report.first_complement_eigenvalue > report.required_dirac_lower_bound
    assert report.first_ht_complement_gap >= MU_H
    assert report.margin > 0.0
    assert audit.theorem_complete is False


def test_legacy_vs_formal_gap_table_reports_old_and_corrected_rows():
    rows = legacy_vs_formal_gap_table()

    assert rows[0]["variant"] == DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST
    assert rows[1]["variant"] == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert rows[0]["protected_coordinates"] == (0, 1, 2)
    assert rows[1]["protected_coordinates"] == (0, 18, 36)
    assert rows[1]["passes"] is True


def test_formal_kernel_scan_reports_pass_fail_and_moving_coordinates():
    rows = scan_formal_kernel_ht_gap(k_max_values=(4, 6), a_values=(1.0,))

    assert len(rows) == 2
    assert rows[0]["protected_coordinates"] == (0, 18, 36)
    assert rows[1]["protected_coordinates"] == (0, 32, 64)
    assert all(row["passes"] is True for row in rows)
    assert all(row["status"] == FORMAL_KERNEL_GAP_RESTORED for row in rows)
    assert all(row["theorem_complete"] is False for row in rows)


def test_no_forbidden_empirical_modules_are_imported_by_formal_kernel_operator():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("formal_kernel_operator.py", "level2_formal_kernel_ht.py")
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


def test_formal_kernel_operator_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_formal_kernel_correction_audit()
    build_formal_kernel_ht_report()

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


def test_formal_kernel_exports_generate_cleanly(tmp_path):
    operator_md = tmp_path / "operator.md"
    operator_json = tmp_path / "operator.json"
    ht_md = tmp_path / "ht.md"
    ht_json = tmp_path / "ht.json"

    export_formal_kernel_operator_markdown(operator_md)
    export_formal_kernel_operator_json(operator_json)
    export_formal_kernel_ht_gap_markdown(ht_md)
    export_formal_kernel_ht_gap_json(ht_json)

    assert DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL in operator_md.read_text()
    assert json.loads(operator_json.read_text())["summary"]["formal_protected_coordinates"] == [0, 18, 36]
    assert FORMAL_KERNEL_GAP_RESTORED in ht_md.read_text()
    data = json.loads(ht_json.read_text())
    assert data["audit"]["status"] == FORMAL_KERNEL_GAP_RESTORED
    assert data["audit"]["theorem_complete"] is False


def test_generated_formal_kernel_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "formal_kernel_operator_report.md",
        root / "theory" / "formal_kernel_operator_report.json",
        root / "theory" / "formal_kernel_ht_gap_report.md",
        root / "theory" / "formal_kernel_ht_gap_report.json",
        root / "manuscript" / "v1_3l_formal_kernel_operator_note.md",
        root / "notebooks" / "34_formal_kernel_operator.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    operator_text = artifact_paths[0].read_text()
    ht_text = artifact_paths[2].read_text()
    ht_data = json.loads(artifact_paths[3].read_text())
    note_text = artifact_paths[4].read_text()

    assert DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL in operator_text
    assert FORMAL_KERNEL_GAP_RESTORED in ht_text
    assert ht_data["audit"]["formal_protected_coordinates"] == [0, 18, 36]
    assert ht_data["audit"]["theorem_complete"] is False
    assert "not proven" in note_text
    assert "fully proven" not in note_text.lower()
