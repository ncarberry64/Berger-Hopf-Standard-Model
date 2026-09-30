"""Mutation tests for an independent stored-data/provenance audit.

Fixtures are tiny synthetic certificate ledgers, not numerical certificates.
They isolate ways an otherwise plausible JSON chain can be invalid.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_n12_c2_stop_dop853_adaptive_chain as audit  # noqa: E402


def _row(interval: int, subspan: int, subdivisions: int = 4) -> dict:
    return {
        "interval": interval, "subspan": subspan, "subdivisions": subdivisions,
        "dyadic_start": f"{subspan}/{subdivisions}",
        "dyadic_end": f"{subspan + 1}/{subdivisions}",
        "selected_branch": 24, "Bernstein_control_count": 8,
        "maximum_projection_column_norm": 0.1,
        "negative_cluster_shift_upper": 0.02, "selected_line_shift_upper": 0.01,
        "positive_cluster_shift_upper": 0.03, "negative_selected_gap_lower": 2.0,
        "selected_positive_gap_lower": 1.0, "minimum_external_center_gap": 3.0,
        "all_three_quarter_gap_bootstraps_closed": True,
        "boundary_cluster_certificate_closed": True,
    }


def _summaries(rows: list[dict]) -> dict:
    return {
        "minimum_selected_line_boundary_gap_lower": min(min(r["negative_selected_gap_lower"], r["selected_positive_gap_lower"]) for r in rows),
        "minimum_negative_selected_gap_lower": min(r["negative_selected_gap_lower"] for r in rows),
        "minimum_selected_positive_gap_lower": min(r["selected_positive_gap_lower"] for r in rows),
        "maximum_selected_line_shift_upper": max(r["selected_line_shift_upper"] for r in rows),
        "maximum_negative_cluster_shift_upper": max(r["negative_cluster_shift_upper"] for r in rows),
        "maximum_positive_cluster_shift_upper": max(r["positive_cluster_shift_upper"] for r in rows),
        "maximum_Bernstein_projection_column_norm": max(r["maximum_projection_column_norm"] for r in rows),
        "minimum_margin_owner": deepcopy(min(rows, key=lambda r: min(r["negative_selected_gap_lower"], r["selected_positive_gap_lower"]))),
    }


def _payloads() -> tuple[dict, dict, dict]:
    coarse_rows = [_row(0, index) for index in range(4)]
    for row in coarse_rows:
        for field in ("subdivisions", "dyadic_start", "dyadic_end"):
            del row[field]
    coarse_rows[1].update({
        "selected_positive_gap_lower": -0.1,
        "all_three_quarter_gap_bootstraps_closed": False,
        "boundary_cluster_certificate_closed": False,
    })
    coarse = {
        "mesh": {"dense_intervals": 1, "subspans_per_dense_interval": 4, "total_subspans": 4},
        "rows": coarse_rows, "summary": _summaries(coarse_rows),
    }
    rows = [_row(0, 0), _row(0, 2, 8), _row(0, 3, 8), _row(0, 2), _row(0, 3)]
    spectrum = {
        "status": audit.SPECTRUM_STATUS, "validation_passed": True, "unresolved_cells": [],
        "mesh": {
            "dense_intervals": 1, "coarse_subspans_per_interval": 4,
            "maximum_subdivisions_per_interval": 32, "coarse_cells_audited": 4,
            "coarse_cells_replaced": 1, "accepted_cover_cell_count": 5,
            "accepted_cover_cells_by_subdivisions": {"4": 3, "8": 2},
            "refinement_cells_audited_by_subdivisions": {"4": 4, "8": 2},
        },
        "rows": rows, "summary": _summaries(rows),
        "validation": {name: True for name in (
            "coarse_replay_consumed_without_reinterpretation",
            "failed_cells_replaced_only_by_exact_dyadic_de_Casteljau_children",
            "adaptive_cells_partition_every_retained_dense_interval_exactly",
            "every_accepted_cell_closes_all_three_quarter_gap_bootstraps",
            "both_selected_line_boundary_margins_positive_everywhere",
            "selected_branch_24_everywhere", "all_cells_use_eight_degree_seven_Bernstein_controls",
            "no_failed_cell_at_maximum_refinement", "same_stored_DOP853_polynomial_as_defect_and_first_hit",
            "no_cubic_Hermite_surrogate_inserted", "quarter_gap_bootstrap_not_weakened",
        )},
        "claim_boundary": {
            "selected_line_on_stored_DOP853_stop_path": "CERTIFIED_SIMPLE",
            "correlated_shadowing_tube": "OPEN", "Gate7": "ACTIVE", "FULL_BHSM_COMPLETE": False,
        },
        "FULL_BHSM_COMPLETE": False, "FLAGSHIP_READY": False,
    }
    graph_rows = []
    for row in rows:
        graph_rows.append({
            **{name: row[name] for name in ("interval", "subspan", "subdivisions")},
            "selected_branch": 24, "certified_global_gap_lower": 1.0,
            "selected_line_shift_upper": 0.01, "spectral_distance_bands": 1,
            "selected_graph_derivative_l2_upper": 0.2,
            "selected_projector_motion_upper": 0.2, "graph_Neumann_closed": True,
            "groups": [{
                "ordered_Weyl_gap_lower": -0.5, "consumed_gap_lower": 1.0,
                "minimum_center_distance": 2.0, "center_D3_coupling_l2_norm": 0.02,
                "D4_coupling_change_upper": 0.03, "coupling_numerator_upper": 0.05,
                "selected_graph_derivative_upper": 0.1,
            }],
        })
    projector = {
        "status": audit.PROJECTOR_STATUS, "validation_passed": True,
        "mesh": {"adaptive_cover_cells": 5}, "rows": graph_rows,
        "summary": {
            "maximum_selected_graph_derivative_l2_upper": 0.2,
            "maximum_selected_projector_motion_upper": 0.2,
            "minimum_consumed_gap_lower": 1.0, "maximum_spectral_distance_bands": 1,
            "owner": deepcopy(graph_rows[0]), "Neumann_factor": 2.0,
        },
        "validation": {name: True for name in (
            "every_adaptive_spectrum_cell_consumed_once_in_order", "branch_24_selected_everywhere",
            "every_certified_gap_strictly_positive", "all_distance_band_graph_Neumann_bounds_below_one",
            "same_DOP853_Bernstein_cover_as_spectrum", "no_cubic_Hermite_surrogate_inserted",
        )},
        "claim_boundary": {
            "selected_projector_graph_on_stored_DOP853_stop_path": "CERTIFIED",
            "correlated_shadowing_tube": "OPEN", "Gate7": "ACTIVE", "FULL_BHSM_COMPLETE": False,
        },
        "FULL_BHSM_COMPLETE": False, "FLAGSHIP_READY": False,
    }
    return coarse, spectrum, projector


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_center(path: Path, intervals: int = 1) -> None:
    np.savez(path, stop_bracket_fine_grid_index=np.asarray([intervals - 1]),
             stop_dense_fraction=np.asarray([0.75]),
             fine_grid_augmented_action_values=np.zeros((intervals + 1, 2)),
             fine_grid_DOP853_dense_coefficients=np.zeros((intervals, 7, 2)),
             fine_grid_action_lengths=np.arange(intervals + 1, dtype=float))


@pytest.fixture
def chain(tmp_path: Path) -> dict:
    (tmp_path / "scripts").mkdir()
    (tmp_path / audit.PROBE).write_text("# synthetic probe dependency\n", encoding="utf-8")
    _write_center(tmp_path / "center.npz")
    coarse, spectrum, projector = _payloads()
    records = {"coarse": coarse, "spectrum": spectrum, "projector": projector}
    _save_chain(tmp_path, records)
    return {"root": tmp_path, **records}


def _save_chain(root: Path, records: dict) -> None:
    common = {"center.npz": audit.normalized_sha256(root / "center.npz"),
              audit.PROBE.as_posix(): audit.normalized_sha256(root / audit.PROBE)}
    records["coarse"]["inputs"] = dict(common)
    _write_json(root / "coarse.json", records["coarse"])
    records["spectrum"]["inputs"] = {**common, "coarse.json": audit.normalized_sha256(root / "coarse.json")}
    _write_json(root / "spectrum.json", records["spectrum"])
    records["projector"]["inputs"] = {**common, "spectrum.json": audit.normalized_sha256(root / "spectrum.json")}
    _write_json(root / "projector.json", records["projector"])


def _verify(chain: dict, *, projector: bool = False) -> dict:
    return audit.verify_chain(chain["root"], Path("coarse.json"), Path("spectrum.json"),
                              Path("center.npz"), Path("projector.json") if projector else None)


def test_valid_chain_passes_and_limits_claims(chain: dict) -> None:
    report = _verify(chain, projector=True)
    assert report["validation_passed"] is True
    assert report["spectrum"]["accepted_cover_cell_count"] == 5
    assert report["spectrum"]["coarse_cells_replaced"] == 1
    assert report["projector"]["maximum_selected_projector_motion_upper"] == 0.2
    assert report["claim_boundary"]["exact_flow_shadowing_verified"] is False


def test_spectrum_only_does_not_consume_a_stale_projector(chain: dict) -> None:
    (chain["root"] / "projector.json").write_text("not JSON", encoding="utf-8")
    assert _verify(chain)["validation_passed"] is True


@pytest.mark.parametrize("changed", ["center.npz", "coarse.json", "spectrum.json", audit.PROBE.as_posix()])
def test_stale_input_hash_fails_closed(chain: dict, changed: str) -> None:
    path = chain["root"] / changed
    path.write_bytes(path.read_bytes() + b" ")
    report = _verify(chain, projector=True)
    assert report["validation_passed"] is False
    assert "stale input hash" in report["errors"][0]


def test_current_npz_stop_mesh_overrules_consistent_json_metadata(chain: dict) -> None:
    _write_center(chain["root"] / "center.npz", intervals=2)
    _save_chain(chain["root"], chain)
    report = _verify(chain)
    assert report["validation_passed"] is False
    assert "current NPZ stop mesh" in report["errors"][0]


def test_required_dependency_cannot_be_omitted(chain: dict) -> None:
    del chain["coarse"]["inputs"]["center.npz"]
    _write_json(chain["root"] / "coarse.json", chain["coarse"])
    chain["spectrum"]["inputs"]["coarse.json"] = audit.normalized_sha256(chain["root"] / "coarse.json")
    _write_json(chain["root"] / "spectrum.json", chain["spectrum"])
    report = _verify(chain)
    assert report["validation_passed"] is False
    assert "required input hash missing" in report["errors"][0]


@pytest.mark.parametrize("mutation, expected", [
    ("hole", "overlap or a hole"), ("overlap", "overlap or a hole"),
    ("accepted_changed", "accepted coarse row changed"),
    ("failed_reused", "failed coarse parent reused"),
    ("accepted_refined", "accepted coarse parent"),
    ("nondyadic", "dyadic level"), ("summary", "summary mismatch"),
    ("counts", "mesh/count mismatch"), ("unresolved", "unresolved cells"),
    ("nan", "finite value"), ("bootstrap", "closure flag contradicts"),
])
def test_plausible_invalid_spectrum_ledgers_are_rejected(mutation: str, expected: str) -> None:
    coarse, spectrum, _ = _payloads()
    rows = spectrum["rows"]
    if mutation == "hole":
        del rows[2]
    elif mutation == "overlap":
        rows.insert(0, deepcopy(rows[0]))
    elif mutation == "accepted_changed":
        rows[0]["selected_line_shift_upper"] = 0.011
    elif mutation == "failed_reused":
        rows[1:3] = [_row(0, 1)]
    elif mutation == "accepted_refined":
        rows[0:1] = [_row(0, 0, 8), _row(0, 1, 8)]
    elif mutation == "nondyadic":
        rows[1]["subdivisions"] = 6
    elif mutation == "summary":
        spectrum["summary"]["minimum_selected_positive_gap_lower"] = 1.1
    elif mutation == "counts":
        spectrum["mesh"]["refinement_cells_audited_by_subdivisions"]["8"] = 4
    elif mutation == "unresolved":
        spectrum["unresolved_cells"] = [deepcopy(rows[1])]
    elif mutation == "nan":
        rows[1]["selected_positive_gap_lower"] = float("nan")
    elif mutation == "bootstrap":
        rows[1]["all_three_quarter_gap_bootstraps_closed"] = False
    with pytest.raises(audit.AuditError, match=expected):
        audit.audit_spectrum_payloads(coarse, spectrum, 1)


def test_refinement_audit_counts_include_nonleaf_ancestors() -> None:
    coarse, spectrum, _ = _payloads()
    spectrum["rows"][1:2] = [_row(0, 4, 16), _row(0, 5, 16)]
    spectrum["summary"] = _summaries(spectrum["rows"])
    spectrum["mesh"].update({
        "accepted_cover_cell_count": 6, "accepted_cover_cells_by_subdivisions": {"4": 3, "8": 1, "16": 2},
        "refinement_cells_audited_by_subdivisions": {"4": 4, "8": 2, "16": 2},
    })
    result = audit.audit_spectrum_payloads(coarse, spectrum, 1)
    assert result["refinement_cells_audited_by_subdivisions"] == {"4": 4, "8": 2, "16": 2}


@pytest.mark.parametrize("mutation, expected", [
    ("order", "ordered spectrum cover"), ("gap", "consumed spectrum gap"),
    ("shift", "selected shift"), ("band_gap", "distance-band consumed gap"),
    ("neumann", "Neumann verdict"), ("motion", "Neumann verdict"),
    ("summary", "projector summary mismatch"),
])
def test_projector_cannot_reinterpret_spectrum(mutation: str, expected: str) -> None:
    _, spectrum, projector = _payloads()
    rows = projector["rows"]
    if mutation == "order":
        rows[0], rows[1] = rows[1], rows[0]
    elif mutation == "gap":
        rows[0]["certified_global_gap_lower"] = 1.01
    elif mutation == "shift":
        rows[0]["selected_line_shift_upper"] = 0.02
    elif mutation == "band_gap":
        rows[0]["groups"][0]["consumed_gap_lower"] = 1.01
    elif mutation == "neumann":
        rows[0]["graph_Neumann_closed"] = False
    elif mutation == "motion":
        rows[0]["selected_projector_motion_upper"] = 1.01
        rows[0]["selected_graph_derivative_l2_upper"] = 1.01
    elif mutation == "summary":
        projector["summary"]["maximum_selected_projector_motion_upper"] = 0.19
    with pytest.raises(audit.AuditError, match=expected):
        audit.audit_projector_payload(spectrum, projector)


def test_cli_emits_json_and_nonzero_on_failed_chain(chain: dict) -> None:
    path = chain["root"] / "center.npz"
    path.write_bytes(path.read_bytes() + b" ")
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/verify_n12_c2_stop_dop853_adaptive_chain.py"),
        "--root", str(chain["root"]), "--coarse", "coarse.json", "--spectrum", "spectrum.json",
        "--center", "center.npz",
    ], capture_output=True, text=True, check=False)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["status"] == "ADAPTIVE_CHAIN_DATA_AUDIT_FAILED"
    assert report["validation_passed"] is False
