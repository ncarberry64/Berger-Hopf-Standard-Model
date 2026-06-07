import json
from math import isclose
from pathlib import Path

import numpy as np

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from protected_kernel_audit import (
    FORMAL_KERNEL_NOT_PROTECTED,
    build_kernel_correction_result,
    build_protected_kernel_audit_report,
    export_protected_kernel_audit_json,
    export_protected_kernel_audit_markdown,
)
from sector_labeled_kernel import (
    coordinate_first_projector,
    export_sector_labeled_kernel_json,
    export_sector_labeled_kernel_markdown,
    formal_protected_projector,
    protected_kernel_basis_matrix,
    protected_kernel_vectors,
    sector_labeled_zero_modes,
)


def test_sector_labeled_kernel_contains_one_lepton_one_up_one_down():
    modes = sector_labeled_zero_modes()

    assert len(modes) == 3
    assert {mode.sector for mode in modes} == {"lepton", "up", "down"}
    assert {mode.coordinate_index for mode in modes} == {0, 18, 36}
    assert all(mode.present_in_basis for mode in modes)
    assert all(mode.k == 0 and mode.j == 0 and mode.q == 0 for mode in modes)
    assert all(mode.chirality == -1 for mode in modes)


def test_old_coordinate_first_protection_is_detected():
    old = coordinate_first_projector()
    formal = formal_protected_projector()

    assert old.coordinate_indices == (0, 1, 2)
    assert formal.coordinate_indices == (0, 18, 36)
    assert old.coordinate_indices != formal.coordinate_indices
    assert old.sector_distribution == {"lepton": 3}
    assert formal.sector_distribution == {"lepton": 1, "up": 1, "down": 1}


def test_formal_projector_is_idempotent_and_orthogonal_to_complement():
    formal = formal_protected_projector()
    basis = protected_kernel_basis_matrix()
    p0 = basis @ basis.T
    p_perp = np.eye(p0.shape[0]) - p0

    assert formal.rank == 3
    assert formal.idempotent is True
    assert formal.orthogonal_to_complement is True
    assert np.allclose(p0 @ p0, p0)
    assert np.allclose(p0 @ p_perp, np.zeros_like(p0))
    assert all(vector.vector_norm == 1.0 for vector in protected_kernel_vectors())


def test_formal_kernel_is_not_protected_under_current_level2_operator():
    report = build_protected_kernel_audit_report()

    assert report.formal_kernel_present is True
    assert report.formal_kernel_rank == 3
    assert report.formal_kernel_heat_preserved is False
    assert report.formal_kernel_sector_coupling_vanishes is False
    assert report.correction_result.classification == FORMAL_KERNEL_NOT_PROTECTED
    assert report.alignment_gap_closes is False
    assert report.theorem_complete is False


def test_gap_is_recomputed_with_formal_projector_and_failure_is_reported():
    result = build_kernel_correction_result()

    assert result.old_protected_coordinates == (0, 1, 2)
    assert result.formal_protected_coordinates == (0, 18, 36)
    assert result.old_ht_gap > result.formal_ht_gap
    assert result.old_margin > 0.0
    assert result.formal_margin < 0.0
    assert result.formal_gap_passes is False
    assert result.previous_gap_survives is False
    assert result.classification == FORMAL_KERNEL_NOT_PROTECTED


def test_no_forbidden_empirical_modules_are_imported_by_kernel_audit():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("sector_labeled_kernel.py", "protected_kernel_audit.py")
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


def test_sector_labeled_kernel_audit_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_protected_kernel_audit_report()

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


def test_sector_labeled_kernel_exports_generate_cleanly(tmp_path):
    kernel_md = tmp_path / "kernel.md"
    kernel_json = tmp_path / "kernel.json"
    audit_md = tmp_path / "audit.md"
    audit_json = tmp_path / "audit.json"

    export_sector_labeled_kernel_markdown(kernel_md)
    export_sector_labeled_kernel_json(kernel_json)
    export_protected_kernel_audit_markdown(audit_md)
    export_protected_kernel_audit_json(audit_json)

    assert "P0_formal_sector_labeled" in kernel_md.read_text()
    assert json.loads(kernel_json.read_text())["formal_projector"]["coordinate_indices"] == [0, 18, 36]
    assert FORMAL_KERNEL_NOT_PROTECTED in audit_md.read_text()
    data = json.loads(audit_json.read_text())
    assert data["correction_result"]["formal_gap_passes"] is False
    assert data["theorem_complete"] is False


def test_generated_sector_labeled_kernel_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "sector_labeled_kernel_report.md",
        root / "theory" / "sector_labeled_kernel_report.json",
        root / "theory" / "protected_kernel_audit.md",
        root / "theory" / "protected_kernel_audit.json",
        root / "manuscript" / "v1_3k_sector_labeled_kernel_note.md",
        root / "notebooks" / "33_sector_labeled_kernel.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    kernel_text = artifact_paths[0].read_text()
    audit_text = artifact_paths[2].read_text()
    audit_data = json.loads(artifact_paths[3].read_text())
    note_text = artifact_paths[4].read_text()

    assert "P0_formal_sector_labeled" in kernel_text
    assert FORMAL_KERNEL_NOT_PROTECTED in audit_text
    assert audit_data["correction_result"]["previous_gap_survives"] is False
    assert audit_data["theorem_complete"] is False
    assert "does not prove the full `H_T` theorem" in note_text
    assert "fully proven" not in note_text.lower()
