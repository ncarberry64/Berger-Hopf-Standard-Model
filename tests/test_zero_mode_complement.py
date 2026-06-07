import json
from math import isclose
from pathlib import Path

import numpy as np

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from complement_projector import (
    build_complement_projector_report,
    complement_projector,
    export_complement_projector_json,
    export_complement_projector_markdown,
    protected_projector,
    protected_zero_mode_basis,
    restricted_complement_operator,
)
from constants import S_OVERLAP
from ht_operator import default_level2_config
from index_theorem_scaffold import (
    build_index_theorem_scaffold_report,
    export_index_theorem_scaffold_json,
    export_index_theorem_scaffold_markdown,
)
from sector_coupling_bounds import level2_sector_coupling_dirac_block
from spectral_bounds import spectral_bound_report
from twisted_dirac import build_level2_dirac_matrix
from zero_mode_index import (
    INDEX_SCAFFOLD,
    OPEN,
    build_zero_mode_split_report,
    export_zero_mode_index_json,
    export_zero_mode_index_markdown,
    protected_family_zero_modes,
    zero_mode_index_contributions,
)


def test_exactly_three_protected_zero_mode_candidates_are_identified():
    candidates = protected_family_zero_modes()

    assert len(candidates) == 3
    assert {candidate.sector for candidate in candidates} == {"lepton", "up", "down"}
    assert all(candidate.k == 0 and candidate.j == 0 and candidate.q == 0 for candidate in candidates)
    assert all(candidate.chirality == -1 for candidate in candidates)
    assert all(candidate.status == "PROTECTED" for candidate in candidates)
    assert sum(candidate.index_contribution for candidate in candidates) == 3


def test_index_scaffold_status_and_mirror_modes_remain_open():
    report = build_zero_mode_split_report()

    assert report.target_index == 3
    assert report.target_kernel_dimension == 3
    assert report.index_status == INDEX_SCAFFOLD
    assert report.index_status != "INDEX_THEOREM_PROVEN"
    assert report.mirror_zero_mode_status == OPEN
    assert report.theorem_complete is False
    assert {assumption.id for assumption in report.assumptions} == {"I1", "I2", "I3", "I4", "I5"}
    assert any("mirror" in assumption.statement.lower() for assumption in report.assumptions)


def test_index_contributions_sum_to_target_without_empirical_inputs():
    contributions = zero_mode_index_contributions()

    assert len(contributions) == 3
    assert sum(item.net_index_contribution for item in contributions) == 3
    assert all(item.protected_modes == 1 for item in contributions)
    assert all(item.negative_chirality_zero_modes == 1 for item in contributions)
    assert all(item.positive_chirality_zero_modes == 0 for item in contributions)


def test_projector_identities_hold_in_finite_basis():
    p0 = protected_projector()
    p_perp = complement_projector()

    assert np.allclose(p0 @ p0, p0)
    assert np.allclose(p_perp @ p_perp, p_perp)
    assert np.allclose(p0 @ p_perp, np.zeros_like(p0))
    assert np.allclose(p0 + p_perp, np.eye(p0.shape[0]))


def test_sector_coupling_vanishes_on_protected_zero_block():
    config = default_level2_config()
    zero_modes = protected_zero_mode_basis(config)
    zero_count = zero_modes.shape[1]
    sector_block = level2_sector_coupling_dirac_block(config)

    assert zero_count == 3
    assert np.allclose(sector_block[:zero_count, :], 0.0)
    assert np.allclose(sector_block[:, :zero_count], 0.0)


def test_heat_lift_and_complement_report_preserve_zero_modes():
    report = build_complement_projector_report()

    assert report.zero_mode_count == 3
    assert report.p0_idempotent is True
    assert report.p_perp_idempotent is True
    assert report.p0_p_perp_zero is True
    assert report.sector_coupling_vanishes_on_zero_block is True
    assert report.heat_lift_preserves_zero_modes is True
    assert report.complement_excludes_zero_modes is True
    assert report.commutes_with_block_decomposition is True
    assert report.theorem_complete is False


def test_complement_lower_bound_machinery_excludes_protected_zero_modes():
    config = default_level2_config()
    basis = protected_zero_mode_basis(config)
    matrix = build_level2_dirac_matrix(config)
    restricted = restricted_complement_operator(matrix.T @ matrix, config)
    report = spectral_bound_report(config=config)

    assert basis.shape[1] == 3
    assert restricted.shape[0] == len(matrix) - 3
    assert report["zero_mode_count"] == 3
    assert report["basis_size"] == len(matrix)
    assert report["exact_finite_basis_complement_eigenvalue"] > 0.0
    assert report["theorem_complete"] is False


def test_combined_index_theorem_scaffold_remains_incomplete():
    report = build_index_theorem_scaffold_report()

    assert report.scaffold_status == "INDEX_AND_COMPLEMENT_SCAFFOLD"
    assert report.target_kernel_dimension == 3
    assert report.target_index == 3
    assert report.complement_projector_report.projector_status == "COMPLEMENT_PROJECTOR_SCAFFOLD"
    assert report.theorem_complete is False
    assert any("Exclude opposite-chirality mirror" in item for item in report.open_obligations)


def test_no_forbidden_empirical_modules_are_imported_by_zero_mode_scaffold():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("zero_mode_index.py", "complement_projector.py", "index_theorem_scaffold.py")
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


def test_zero_mode_scaffold_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_index_theorem_scaffold_report()

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


def test_zero_mode_exports_generate_cleanly(tmp_path):
    zero_md = tmp_path / "zero.md"
    zero_json = tmp_path / "zero.json"
    projector_md = tmp_path / "projector.md"
    projector_json = tmp_path / "projector.json"
    scaffold_md = tmp_path / "scaffold.md"
    scaffold_json = tmp_path / "scaffold.json"

    export_zero_mode_index_markdown(zero_md)
    export_zero_mode_index_json(zero_json)
    export_complement_projector_markdown(projector_md)
    export_complement_projector_json(projector_json)
    export_index_theorem_scaffold_markdown(scaffold_md)
    export_index_theorem_scaffold_json(scaffold_json)

    assert "INDEX_SCAFFOLD" in zero_md.read_text()
    assert json.loads(zero_json.read_text())["theorem_complete"] is False
    assert "COMPLEMENT_PROJECTOR_SCAFFOLD" in projector_md.read_text()
    assert json.loads(projector_json.read_text())["zero_mode_count"] == 3
    assert "INDEX_AND_COMPLEMENT_SCAFFOLD" in scaffold_md.read_text()
    assert json.loads(scaffold_json.read_text())["theorem_complete"] is False


def test_generated_zero_mode_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "zero_mode_index_scaffold.md",
        root / "theory" / "zero_mode_index_scaffold.json",
        root / "theory" / "complement_projector_report.md",
        root / "theory" / "complement_projector_report.json",
        root / "theory" / "index_theorem_scaffold_report.md",
        root / "theory" / "index_theorem_scaffold_report.json",
        root / "manuscript" / "v1_3g_zero_mode_complement_note.md",
        root / "notebooks" / "29_zero_mode_complement_split.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    zero_text = artifact_paths[0].read_text()
    projector_text = artifact_paths[2].read_text()
    scaffold_data = json.loads(artifact_paths[5].read_text())
    note_text = artifact_paths[6].read_text()

    assert "INDEX_SCAFFOLD" in zero_text
    assert "COMPLEMENT_PROJECTOR_SCAFFOLD" in projector_text
    assert scaffold_data["target_kernel_dimension"] == 3
    assert scaffold_data["theorem_complete"] is False
    assert "does not prove the full index theorem" in note_text
    assert "not `INDEX_THEOREM_PROVEN`" in zero_text
    assert "fully proven" not in note_text.lower()
