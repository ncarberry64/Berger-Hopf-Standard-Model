"""Evaluate action-owned mixed child form vertices on the current N12 path.

The output contains full tridiagonal K/M/V/Q and their elementwise mixed
geometry/source operators for both inherited product-Dirac chiralities.
Optional coefficient jets must occupy this same node and element mesh.
For the48-macro-node backreaction jets, explicitly use the matching48-node
coefficient_path.npz; no interpolation onto the default371-node path occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_lepton_composite_mixing_structure import shared_charged_lepton_vertex_jet
from bhsm.interface.n12_current_mixed_child_forms import (
    mixed_form_directional_check,
    normalized_source_mixed_form_jets,
)

DEFAULT_PATH = ROOT / "artifacts/current_runtime/dop853_system_integration_current_finer/coefficient_path.npz"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_mixed_child_operators"


def _load_path(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as source:
        arrays = {key: np.asarray(source[key], dtype=float)
                  for key in ("arc_nodes", "log_radius", "proper_times", "proper_durations")}
    x, h, tau = (arrays[key] for key in ("log_radius", "proper_durations", "proper_times"))
    if (x.ndim != 1 or h.ndim != 1 or x.shape != tau.shape or x.size != h.size + 1
            or arrays["arc_nodes"].shape != x.shape or not np.all(np.diff(arrays["arc_nodes"]) > 0)
            or not all(np.all(np.isfinite(value)) for value in arrays.values())
            or np.any(h <= 0) or not np.allclose(np.diff(tau), h, rtol=1e-12, atol=0.0)):
        raise ValueError("aligned actual coefficient-path arrays required")
    return arrays


def _load_jets(path: Path | None, coefficients: dict[str, np.ndarray]) -> tuple[np.ndarray | None, np.ndarray | None]:
    if path is None:
        return None, None
    with np.load(path, allow_pickle=False) as source:
        dx = np.asarray(source["log_radius_first_jet"], dtype=float)
        h = coefficients["proper_durations"]
        if "proper_durations_first_jet" in source:
            dh = np.asarray(source["proper_durations_first_jet"], dtype=float)
        elif "proper_duration_first_jet" in source:
            dT = np.asarray(source["proper_duration_first_jet"], dtype=float)
            dh = (h / h.sum())[:, None] * dT[None, :]
        else:
            raise ValueError("mode jets need element-duration jets or a fixed-normalized-time total-duration jet")
        arc_key = "arc_nodes" if "arc_nodes" in source else "action_lengths"
        if arc_key not in source:
            raise ValueError("mode jet node ownership requires arc_nodes or action_lengths")
        arc = np.asarray(source[arc_key], dtype=float)
        expected = coefficients["arc_nodes"]
        if arc.shape != expected.shape or not np.allclose(arc, expected, rtol=0, atol=1e-12):
            raise ValueError("mode jets and coefficient path occupy different action nodes; supply their matching coefficient path")
        if (dx.ndim != 2 or dx.shape[0] != expected.size or dh.shape != (h.size, dx.shape[1])
                or not np.all(np.isfinite(dx)) or not np.all(np.isfinite(dh))):
            raise ValueError("finite aligned node-radius and element-duration jets required")
        for key in ("log_radius", "proper_durations"):
            if key in source:
                base = np.asarray(source[key], dtype=float)
                if base.shape != coefficients[key].shape or not np.allclose(base, coefficients[key], rtol=1e-12, atol=1e-14):
                    raise ValueError(f"mode jet base {key} differs from this coefficient path")
    return dx, dh


def run(args: argparse.Namespace) -> dict[str, Any]:
    coefficients = _load_path(args.coefficient_path)
    dx, dh = _load_jets(args.mode_jets, coefficients)
    x, h = coefficients["log_radius"], coefficients["proper_durations"]
    saved = dict(coefficients)
    if dx is not None:
        saved["log_radius_first_jet"] = dx
        saved["proper_durations_first_jet"] = dh
    summaries = {}
    for chi, name in ((1, "plus"), (-1, "minus")):
        block = normalized_source_mixed_form_jets(
            log_radii=x, proper_durations=h, chirality=chi,
            log_radius_first_jet=dx, proper_durations_first_jet=dh,
        )
        saved.update({f"{name}_{key}": value for key, value in block["arrays"].items()})
        summaries[name] = block["summary"]
    lepton = shared_charged_lepton_vertex_jet()
    lepton_array_keys = ("intrinsic_vertex_matrix", "auxiliary_vertex_matrix", "squared_pencil_mixed_contact")
    for key in lepton_array_keys:
        saved[f"lepton_{key}"] = np.asarray(lepton[key], dtype=float)
    lepton_summary = {key: value for key, value in lepton.items() if key not in lepton_array_keys}
    lepton_summary["array_keys"] = [f"lepton_{key}" for key in lepton_array_keys]
    lepton_summary["vertex_dimensions"] = [6, 6]
    lepton_summary["intrinsic_vertex_frobenius_norm"] = float(np.linalg.norm(saved["lepton_intrinsic_vertex_matrix"]))
    lepton_summary["auxiliary_vertex_frobenius_norm"] = float(np.linalg.norm(saved["lepton_auxiliary_vertex_matrix"]))
    check = mixed_form_directional_check(x, h)
    if not check["passed"]:
        raise ArithmeticError("actual-path mixed form derivative check failed: " + json.dumps(check))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output / "arrays.npz", **saved)
    report = {
        "status": "CURRENT_N12_MIXED_GEOMETRY_SOURCE_CHILD_OPERATORS_EVALUATED",
        "coefficient_path": str(args.coefficient_path.resolve()),
        "coefficient_path_SHA256": hashlib.sha256(args.coefficient_path.read_bytes()).hexdigest(),
        "mode_jets": str(args.mode_jets.resolve()) if args.mode_jets else None,
        "mode_jet_node_alignment_checked": args.mode_jets is not None,
        "node_count": x.size, "element_count": h.size,
        "proper_duration": float(h.sum()),
        "stop_action_length": float(coefficients["arc_nodes"][-1]),
        "form_conventions": {
            "K": "S/h+W^2*M+W*C", "M": "h*A/6", "W": "chi*1.5*exp(-x_mid)",
            "source_center": 0.0, "source_profile": "p=1/sqrt(T)",
            "V": "2*W*p*M+p*C", "Q": "2*p^2*M",
            "D_x_mid_V_at_fixed_source": "-2*W*p*M",
            "D_h_V_at_fixed_source": "2*W*p*A/6",
            "D_source_profile": "-p*D_T/(2*T)",
            "source_kind": "INHERITED_UNIT_COMMUTING_REDUCED_LR_HS_PROBE",
            "coefficient_jets": "FIXED_NODE_INDEX_WITH_SUPPLIED_RADIUS_AND_DURATION_MOTION",
            "far_node": "EXISTING_FRIEDRICHS_FORM_CORE_DIRICHLET_TRUNCATION",
        },
        "chirality_blocks": summaries,
        "lepton_intrinsic_auxiliary": lepton_summary,
        "actual_path_derivative_check": check,
        "execution": {"trajectory_reintegrated": False, "new_exact_action_evaluations": 0,
                      "retarded_child_packet_invented": False, "fermion_background_selected": False},
        "scope": "ACTUAL_FINITE_CORE_OPERATOR_VERTICES_AND_MIXED_FORM_JETS;_CHILD_STRESS_EXPECTATION_NOT_SELECTED",
        "arrays": str(output / "arrays.npz"),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coefficient-path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--mode-jets", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    report = run(parser.parse_args())
    print(json.dumps({key: report[key] for key in ("status", "node_count", "element_count", "proper_duration", "arrays")}, indent=2))
    print(json.dumps({"derivative_check_passed": report["actual_path_derivative_check"]["passed"],
                      "mode_jet_direction_count": report["chirality_blocks"]["plus"]["coefficient_jet_direction_count"],
                      "lepton_cross_contact_residual": report["lepton_intrinsic_auxiliary"]["squared_pencil_cross_contact_residual"]}))


if __name__ == "__main__":
    main()
