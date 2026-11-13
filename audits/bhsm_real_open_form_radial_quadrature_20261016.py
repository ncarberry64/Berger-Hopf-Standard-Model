"""Fixed-trial radial integration sensitivity, never a physical convergence gate.

Read independent applications of the canonical real full-D5 open-form producer.
Time quadrature, PW band, all fiber rows, density, and trial columns stay fixed.
No new history, background, normal-mode normalization, or exterior is supplied.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from scipy import sparse

REPO = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def artifact_path(value):
    path = Path(value)
    path = (REPO / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(REPO):
        raise ValueError("Published inputs and outputs must stay within the repository")
    return path


def matrix(archive, name):
    return sparse.csr_matrix(
        (archive[name + "_data"], archive[name + "_indices"], archive[name + "_indptr"]),
        shape=tuple(archive[name + "_shape"]),
    )


def difference(left, right):
    a, b = float(sparse.linalg.norm(left)), float(sparse.linalg.norm(right))
    residual = (left - right).tocoo()
    delta = float(sparse.linalg.norm(residual))
    if residual.nnz:
        lv = np.asarray(left[residual.row, residual.col]).reshape(-1)
        rv = np.asarray(right[residual.row, residual.col]).reshape(-1)
        absolute_entry = float(np.max(abs(residual.data)))
        scaled_entry = float(np.max(abs(residual.data)/np.maximum(1.,np.maximum(abs(lv),abs(rv)))))
    else:
        absolute_entry = scaled_entry = 0.
    return dict(left_Frobenius_norm=a, right_Frobenius_norm=b,
                difference_Frobenius_norm=delta,
                symmetric_relative_difference=delta / max(a, b, np.finfo(float).tiny),
                absolute_or_relative_difference=delta / max(1.0, a, b),
                maximum_absolute_entry_difference=absolute_entry,
                maximum_entrywise_absolute_or_relative_difference=scaled_entry)


def matrix_kind(name):
    if name.endswith("_K"):
        return "K"
    if name.endswith("_M"):
        return "M"
    return "wall_conormal" if "_wall_" in name else "temporal_conormal"


def execute(output, *, input_pairs, streaming_controls, repeat):
    out = artifact_path(output)
    if out.exists():
        raise FileExistsError(out)
    orders = tuple(sorted(input_pairs))
    if orders[0] != 4 or sorted(set(orders)) != list(orders):
        raise ValueError("Use ascending distinct rules starting with retained rule4")
    archives, applications, provenance = {}, {}, {}
    for order in orders:
        paths = [artifact_path(path) for path in input_pairs[order]]
        if len(paths) != 2:
            raise ValueError("Each rule requires two independent directories")
        for name in ("application.npz", "result.json"):
            if (paths[0] / name).read_bytes() != (paths[1] / name).read_bytes():
                raise ArithmeticError(f"Independent rule{order} pair differs: {name}")
        application = json.loads((paths[repeat - 1] / "result.json").read_text())
        if application["radial_order"] != order:
            raise ValueError("The labeled radial rule does not match the application")
        if application["angular_level"] != 1 or application["time_order"] != 2:
            raise ValueError("The held angular or temporal rule changed")
        applications[order] = application
        archives[order] = np.load(paths[repeat - 1] / "application.npz")
        provenance[str(order)] = dict(
            independent_repeat_paths=[p.relative_to(REPO).as_posix() for p in paths],
            application_sha256=digest(paths[0] / "application.npz"),
            result_sha256=digest(paths[0] / "result.json"),
            application_bytes=(paths[0] / "application.npz").stat().st_size,
            canonical_producer_and_input_sha256=application.get("input_and_source_sha256",
                application.get("source_and_input_sha256")),
            canonical_matrix_relative_controls=application.get("canonical_matrix_relative_controls"),
            reference_application_sha256=application.get("reference_application_sha256"),
            pair_application_bytes_identical=True,
            pair_result_bytes_identical=True,
        )
    first = archives[orders[0]]
    names = sorted(key[:-6] for key in first.files if key.endswith("_shape"))
    matrices = {order: {name: matrix(archives[order], name) for name in names}
                for order in orders}
    invariant_names = [key for key in first.files if
                       key.endswith("_intrinsic_normalized_q_SH_form") or
                       key.endswith("_raw") or key.endswith("_rawtime") or
                       key == "angular_derivatives" or key == "angular_labels"]
    invariant = {
        key: all(np.array_equal(first[key], archives[order][key]) for order in orders)
        for key in invariant_names
    }
    if not all(invariant.values()):
        raise ArithmeticError("A held field/trial/seam/angular operand changed")
    transitions = []
    finest = orders[-1]
    for a, b in zip(orders[:-1], orders[1:]):
        table = {name: difference(matrices[a][name], matrices[b][name]) for name in names}
        maximum = max(table, key=lambda name: table[name]["symmetric_relative_difference"])
        transitions.append(dict(
            left_rule=a, right_rule=b, matrices=table,
            category_maxima={kind:{metric:max(row[metric] for name,row in table.items()
                if matrix_kind(name)==kind) for metric in (
                    "symmetric_relative_difference", "maximum_absolute_entry_difference",
                    "maximum_entrywise_absolute_or_relative_difference")}
                for kind in ("K","M","temporal_conormal","wall_conormal")},
            maximum_symmetric_relative_difference=table[maximum]["symmetric_relative_difference"],
            maximum_matrix=maximum,
        ))
    to_finest = {
        str(order): {name: difference(matrices[order][name], matrices[finest][name])
                     for name in names}
        for order in orders[:-1]
    }
    control_receipts = {}
    for path in streaming_controls:
        path = artifact_path(path)
        receipt = json.loads(path.read_text())
        order = int(receipt["radial_order"])
        if order not in (4, 8) or str(order) in control_receipts:
            raise ValueError("Exactly one original streaming control for each of rule4 and rule8 is required")
        errors = receipt["canonical_matrix_relative_controls"]
        if len(errors) != len(names) or max(errors.values()) > 2e-12:
            raise ArithmeticError("Original streaming/full-batch control is incomplete or failed")
        if receipt["reference_application_sha256"] != provenance[str(order)]["application_sha256"]:
            raise ArithmeticError("Streaming control references a different canonical rule archive")
        control_receipts[str(order)] = dict(path=path.relative_to(REPO).as_posix(),
            result_sha256=digest(path), receipt=receipt)
    if set(control_receipts) != {"4", "8"}:
        raise ValueError("Both original streaming controls are required")
    result = dict(
        classification="FIXED_P1_OPEN_FORM_RADIAL_QUADRATURE_SENSITIVITY_ONLY",
        radial_orders=list(orders), angular_level=1, angular_count=5, time_order=2,
        bulk_fiber_dimension=384, matrix_count=len(names),
        trial="Fixed P1-time x P1-material-rho x full retained PW band; all endpoints free",
        density_and_Haar="Actual real mu=N C R^3 and unit Haar Gram times2pi^2, unchanged",
        eta="Primary combined f-contact retained; no global sigma normal or sin(f) rescaling",
        comparison="Exact same matrix columns; Frobenius norms, symmetric relative difference, max(1,norm) scaling, and max entrywise absolute/scaled changes",
        held_operands_exactly_equal=invariant, transitions=transitions,
        differences_to_finest_retained_rule=to_finest, provenance=provenance,
        streaming_controls=control_receipts,
        comparison_source_sha256=digest(Path(__file__)),
        new_history_or_source_campaigns=0, physical_mean_solved=False,
        full_native_domain_selected=False, physical_radial_convergence_passed=False,
        physical_derivative_at_2e_minus10_passed=False, coupled_corrections=0,
        physical_muon_magnetic_moment=None,
    )
    out.mkdir(parents=True)
    (out / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2,
        allow_nan=False) + "\n", encoding="utf8", newline="\n")
    for archive in archives.values():
        archive.close()
    print(json.dumps(dict(result_sha256=digest(out / "result.json"),
        transitions=[{key: row[key] for key in ("left_rule", "right_rule",
        "maximum_symmetric_relative_difference", "maximum_matrix")} for row in transitions])))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--input", nargs=3, action="append", required=True,
        metavar=("ORDER", "DIR1", "DIR2"))
    p.add_argument("--streaming-control", action="append", required=True)
    p.add_argument("--repeat", type=int, choices=(1, 2), required=True)
    args = p.parse_args()
    pairs = {}
    for order, first, second in args.input:
        order = int(order)
        if order in pairs:
            raise ValueError("Repeated radial input order")
        pairs[order] = (first, second)
    execute(args.output, input_pairs=pairs, streaming_controls=args.streaming_control,
        repeat=args.repeat)
