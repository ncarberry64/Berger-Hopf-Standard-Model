import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from formal_kernel_convergence import (
    build_formal_kernel_convergence_report,
    export_formal_kernel_convergence_json,
    export_formal_kernel_convergence_markdown,
    scan_formal_kernel_convergence,
)
from formal_kernel_operator import (
    DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
    DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
)
from formal_kernel_regression import (
    build_formal_kernel_regression_report,
    export_formal_kernel_regression_json,
    export_formal_kernel_regression_markdown,
    formal_kernel_lower_bound_row,
    old_coordinate_first_lower_bound_row,
)


def test_regression_compares_old_coordinate_first_to_corrected_formal_kernel():
    report = build_formal_kernel_regression_report()
    old, corrected = report.lower_bound_rows

    assert old.variant == DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST
    assert corrected.variant == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert old.protected_coordinates == (0, 1, 2)
    assert corrected.protected_coordinates == (0, 18, 36)
    assert corrected.protected_sectors == ("lepton", "up", "down")
    assert corrected.direct_finite_spectrum_lower_bound > old.direct_finite_spectrum_lower_bound
    assert corrected.ht_gap > old.ht_gap
    assert report.corrected_gap_stable is True
    assert report.theorem_complete is False


def test_corrected_lower_bound_reports_use_formal_complement():
    corrected = formal_kernel_lower_bound_row()

    assert corrected.variant == DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
    assert corrected.protected_coordinates == (0, 18, 36)
    assert corrected.direct_finite_spectrum_lower_bound == corrected.minmax_complement_lower_bound
    assert corrected.direct_finite_spectrum_lower_bound > corrected.required_dirac_lower_bound
    assert corrected.gershgorin_lower_bound > corrected.required_dirac_lower_bound
    assert corrected.passes_mu_h is True


def test_old_coordinate_first_row_is_retained_only_for_comparison():
    old = old_coordinate_first_lower_bound_row()

    assert old.variant == DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST
    assert old.protected_coordinates == (0, 1, 2)
    assert old.protected_sectors == ("lepton", "lepton", "lepton")


def test_corrected_convergence_scan_covers_requested_k_values_and_anisotropies():
    rows = scan_formal_kernel_convergence()
    k_values = {row.k_max for row in rows}
    a_values = {row.a for row in rows}

    assert k_values == {4, 6, 8, 10, 12, 16, 20, 24, 32}
    assert len(a_values) == 3
    assert len(rows) == 27
    assert all(row.protected_sectors == ("lepton", "up", "down") for row in rows)
    assert all(row.passes is True for row in rows)
    assert all(row.theorem_complete is False for row in rows)


def test_corrected_convergence_report_flags_failures_if_any_and_keeps_theorem_open():
    report = build_formal_kernel_convergence_report()

    assert report.classification == "FORMAL_KERNEL_CONVERGENCE_SUPPORTED"
    assert report.all_rows_pass is True
    assert report.worst_direct_margin > 0.0
    assert report.worst_gershgorin_margin > 0.0
    assert report.min_first_complement_eigenvalue > 0.8038064161349437
    assert report.theorem_complete is False


def test_no_forbidden_empirical_modules_are_imported_by_regression_modules():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in ("formal_kernel_regression.py", "formal_kernel_convergence.py")
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


def test_formal_kernel_regression_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    build_formal_kernel_regression_report()
    build_formal_kernel_convergence_report()

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


def test_formal_kernel_regression_exports_generate_cleanly(tmp_path):
    regression_md = tmp_path / "regression.md"
    regression_json = tmp_path / "regression.json"
    convergence_md = tmp_path / "convergence.md"
    convergence_json = tmp_path / "convergence.json"

    export_formal_kernel_regression_markdown(regression_md)
    export_formal_kernel_regression_json(regression_json)
    export_formal_kernel_convergence_markdown(convergence_md)
    export_formal_kernel_convergence_json(convergence_json)

    assert DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL in regression_md.read_text()
    assert json.loads(regression_json.read_text())["corrected_gap_stable"] is True
    assert "FORMAL_KERNEL_CONVERGENCE_SUPPORTED" in convergence_md.read_text()
    assert json.loads(convergence_json.read_text())["all_rows_pass"] is True


def test_generated_formal_kernel_regression_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "formal_kernel_regression_report.md",
        root / "theory" / "formal_kernel_regression_report.json",
        root / "theory" / "formal_kernel_convergence_report.md",
        root / "theory" / "formal_kernel_convergence_report.json",
        root / "manuscript" / "v1_3m_formal_kernel_regression_note.md",
        root / "notebooks" / "35_formal_kernel_regression.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    regression_text = artifact_paths[0].read_text()
    convergence_text = artifact_paths[2].read_text()
    convergence_data = json.loads(artifact_paths[3].read_text())
    note_text = artifact_paths[4].read_text()

    assert DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL in regression_text
    assert "FORMAL_KERNEL_CONVERGENCE_SUPPORTED" in convergence_text
    assert convergence_data["theorem_complete"] is False
    assert "does not prove" in note_text
    assert "fully proven" not in note_text.lower()
