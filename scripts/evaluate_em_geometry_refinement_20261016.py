"""Portable compact same-field96/192 geometry refinement and literal complex controls.

The frozen24/48 producer is consumed unchanged.  Full100 and16x100 arrays
are compared; complex-step controls cover declared axes0,98,99, not an
independent admission of the entire physical outgoing derivative.
"""
from __future__ import annotations

import argparse
import gc
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

import ast
import os
from types import SimpleNamespace

REPO = Path(os.environ.get("BHSM_REPOSITORY", Path(__file__).resolve().parents[1])).resolve()
sys.path[:0] = [str(REPO / "src"), str(REPO / "scripts")]
import evaluate_em_carrier_original_maxwell_20261016 as retained
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_baton_zoo_original_validation import independent_original_maxwell_weak
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows
from bhsm.interface.muon_parent_maxwell_full_weak import M, background_subtracted_maxwell_action_jet, full_maxwell_weak_geometric_jets
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase

GEOMETRY_KEYS = ("electric", "radial", "angular", "electric_radial", "shift", "connection_lambda", "lambda_tau", "lambda_rho")
DENSITY_KEYS = GEOMETRY_KEYS[:5]
FIELD_KEYS = ("gauge", "gauge_tau", "gauge_rho", "gauge_angular")
TEST_KEYS = ("tests", "tests_tau", "tests_rho", "tests_angular")
UTILITY_NAMES = ("real", "sha", "norm", "difference", "real_geometry", "mechanical", "test_arrays")


def load_frozen_utilities(path):
    path = Path(path).resolve()
    if sha256(path.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError("frozen24/48 executed source changed")
    if Path(retained.REPO).resolve() != REPO or not Path(retained.__file__).resolve().is_relative_to(REPO):
        raise ValueError("selected repository and canonical field owner differ")
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    selected = {node.name: ast.get_source_segment(text, node) for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name in UTILITY_NAMES}
    if set(selected) != set(UTILITY_NAMES):
        raise ValueError("frozen mathematical utility block missing")
    block = "\n\n".join(selected[name] for name in UTILITY_NAMES) + "\n"
    namespace = dict(globals())
    exec(compile(block, str(path) + "::exact_function_blocks", "exec"), namespace)
    namespace["utility_block_sha256"] = sha256(block.encode()).hexdigest()
    namespace["frozen_source_path"] = path
    return SimpleNamespace(**namespace)

BASE_SHA = "43476aa10597491656098b354e35101ceae46c56e1d046c48beb451a8115a2b6"
BASE_RESULT_SHA = "9e1213886a357c2be27515f6075a70e3f8867c5f5e391ecc1251a42ee1ceb7bd"
BASE_NUMERICAL_SHA = "e352b4859fd10d7c383a4f2014211d4b9ef5c9cf41acce0c3b836e6abd69506a"
CS_STEPS = (1e-16, 1e-20, 1e-24)
AXES = (("normal98", 98), ("rate99", 99), ("log_radius_q0", 0))


def complex_mechanical(rows, nh, base):
    nr = len(rows)
    fields = [np.zeros((nr, nh, 5, 4), complex) for _ in range(3)]
    for placement, key, offset in ((0, "connection_lambda", 1),
                                  (1, "lambda_tau", 0), (2, "lambda_rho", 0)):
        values = np.array([r[key].value for r in rows], complex) - offset
        fields[placement][:, :, 2:] = values[:, None, None, None] * base.M[None, None]
    fields.append(np.zeros((nr, nh, 3, 5, 4), complex))
    return fields


def complex_literal(raw, snap, independent, tests, base):
    """Holomorphic values and literal original F, with NO real clipping."""
    geo = base.holomorphic_geometry_rows(np.asarray(raw, complex), snap["rho"], differentiate=False)
    mech = complex_mechanical(geo["rows"], len(snap["space"]["weights"]), base)
    total = [a + b for a, b in zip(independent, mech)]
    nr, nh = total[0].shape[:2]
    density = np.array([[r[key].value for key in base.DENSITY_KEYS] for r in geo["rows"]], complex)
    density = np.broadcast_to(density[:, None], (nr, nh, 5)).reshape(-1, 5)
    nt = tests[0].shape[1]
    tf = [x.transpose(0, 2, 1, *range(3, x.ndim)).reshape((nr * nh, nt) + x.shape[3:]) for x in tests]
    quadrature = (base.MAXWELL_TO_CAP * snap["wr"][:, None] * snap["space"]["weights"][None]).ravel()

    def application(fields, test_fields):
        return base.independent_original_maxwell_weak(
            **dict(zip(("connection", "time_derivative", "radial_derivative", "angular_derivative"),
                       [x.reshape((nr * nh,) + x.shape[2:]) for x in fields])),
            **dict(zip(("tests", "tests_time", "tests_radial", "tests_angular"), test_fields)),
            metric_densities=density, quadrature=quadrature)

    full = application(total, tf)
    zero = [np.zeros((nr * nh, 1, 5, 4), complex) for _ in range(3)]
    zero.append(np.zeros((nr * nh, 1, 3, 5, 4), complex))
    reference = application(mech, zero)
    momentum = full["temporal_momentum"].reshape(nr, nh, 5, 4)
    ptest = np.einsum("rp,rjpic,rpic->j", quadrature.reshape(nr, nh), tests[0], momentum)
    value = np.r_[full["original_action_value"] - reference["original_action_value"],
                  full["original_weak_rows"], ptest]
    chart = geo["response_chart"]
    return value, float(np.max(np.abs(chart["implicit_residual"])))


def loaded_first(archive, side):
    p = f"{side}_q48_"
    return dict(action_gradient=archive[p + "background_subtracted_action_gradient"].copy(),
                weak_jacobian=archive[p + "weak16_geometry_jacobian"].copy(),
                momentum_jacobian=archive[p + "momentum16_geometry_jacobian"].copy())


def execute(output, baseline_path, frozen_producer):
    base = load_frozen_utilities(frozen_producer)
    baseline = Path(baseline_path).resolve()
    if base.sha(baseline / "result.json") != BASE_RESULT_SHA or base.sha(baseline / "geometry_application.npz") != BASE_NUMERICAL_SHA:
        raise ValueError("frozen actual baseline inputs changed")
    with np.load(baseline / "geometry_application.npz", allow_pickle=False) as archive:
        previous_by_side = {side: loaded_first(archive, side) for side in base.retained.PHASES}
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError("preserve evidence; select a fresh output directory")
    out.mkdir(parents=True)
    arrays, full_hessians, records, pins = {}, {}, {}, {}
    space = base.retained.even_angular_space()
    for side, path in base.retained.PHASES.items():
        phase = base.load_profile_preserving_phase(path, repository=base.REPO)
        pins.update(phase["input_hashes"])
        t = phase["receipt"]["span"] / 2
        previous, previous_order = previous_by_side[side], 48
        for key, value in previous.items():
            arrays[f"{side}_q48_{key}"] = value
        side_records = []
        for order in (96, 192):
            print(f"{side} radial{order}: original100 geometry application", flush=True)
            snap = base.retained.snapshot(phase, t, order, space)
            sample = base.retained.sample_coefficients(phase, t,
                base.retained.radial_representation(phase["representation"], snap["rho"]))[1]
            raw = base.real(sample["raw_fields"][:100])
            geo = base.real_geometry(raw, snap["rho"], differentiate=True)
            own = base.mechanical(geo["rows"], len(space["weights"]))
            independent = [a - b for a, b in zip(snap["fields"], own)]
            tests = base.test_arrays(snap)
            action = base.background_subtracted_maxwell_action_jet(
                geo, base.MAXWELL_TO_CAP * snap["wr"], space["weights"],
                **dict(zip(base.FIELD_KEYS, independent)))
            weak = base.full_maxwell_weak_geometric_jets(
                geo, base.MAXWELL_TO_CAP * snap["wr"], space["weights"],
                **dict(zip(base.FIELD_KEYS, independent)), **dict(zip(base.TEST_KEYS, tests)))
            current = dict(action_gradient=action["gradient"],
                weak_jacobian=weak["weak"]["geometric_jacobian"],
                momentum_jacobian=weak["temporal_momentum_test"]["geometric_jacobian"])
            comparison = {k: base.difference(current[k], previous[k]) for k in current}
            stable_absolute = all(v["absolute"] <= 2e-10 for v in comparison.values())
            actual = np.r_[action["value"], weak["weak"]["values"], weak["temporal_momentum_test"]["values"]]
            literal_base, implicit_base = complex_literal(raw, snap, independent, tests, base)
            baseline_check = base.difference(literal_base, actual)
            if baseline_check["scaled"] > 2e-10 or np.any(literal_base.imag != 0):
                raise ValueError("fresh literal baseline failed")
            cs = []
            for name, axis in AXES:
                target = np.r_[current["action_gradient"][axis], current["weak_jacobian"][:, axis], current["momentum_jacobian"][:, axis]]
                values = []
                for h in CS_STEPS:
                    x = raw.astype(complex); x[axis] += 1j * h
                    literal_value, chart_residual = complex_literal(x, snap, independent, tests, base)
                    derivative = literal_value.imag / h
                    values.append(dict(h=h, all=base.difference(derivative, target),
                        action=base.difference(derivative[:1], target[:1]),
                        weak=base.difference(derivative[1:17], target[1:17]),
                        momentum=base.difference(derivative[17:], target[17:]),
                        implicit_chart_residual=chart_residual))
                    arrays[f"{side}_q{order}_cs_{name}_h{h:g}"] = derivative
                cs.append(dict(direction=name, raw_index=axis, steps=values))
            prefix = f"{side}_q{order}_"
            arrays[prefix + "geometry100"] = raw
            for key, value in current.items():
                arrays[prefix + key] = value
            arrays[prefix + "weak16"] = weak["weak"]["values"]
            arrays[prefix + "momentum16"] = weak["temporal_momentum_test"]["values"]
            full_hessians.update({prefix + "action_hessian": action["hessian"],
                prefix + "weak_hessian": weak["weak"]["geometric_hessians"],
                prefix + "momentum_hessian": weak["temporal_momentum_test"]["geometric_hessians"]})
            record = dict(radial_order=order, previous_order=previous_order,
                full100_and16x100_radial_difference=comparison,
                all_previous_differences_below_absolute_2e_minus10=stable_absolute,
                actual_largest_components={k: base.norm(v) for k, v in current.items()},
                fresh_literal_baseline=baseline_check, implicit_chart_baseline_residual=implicit_base,
                independent_complex_step_axes=cs)
            side_records.append(record)
            records[side] = side_records
            base._compressed_npz(out / "compact_geometry_application.npz", arrays)
            base._compressed_npz(out / "work_only_geometry_hessians.npz", full_hessians)
            (out / "partial_result.json").write_text(json.dumps(records, indent=2, sort_keys=True, allow_nan=False) + "\n")
            print(f"{side} radial{order}: full-array differences " + str({k:v["absolute"] for k,v in comparison.items()}), flush=True)
            previous, previous_order = current, order
            del geo, weak, action, snap
            gc.collect()
            if stable_absolute:
                break
    for name, module in list(sys.modules.items()):
        source = getattr(module, "__file__", None)
        if source and Path(source).is_relative_to(base.REPO) and (name.startswith("bhsm.") or name.startswith("bhsm_real") or name == base.retained.__name__):
            pins[Path(source).relative_to(base.REPO).as_posix()] = base.sha(source)
    pins[str(Path(__file__).resolve())] = base.sha(__file__)
    pins[str(base.frozen_source_path)] = BASE_SHA
    pins[str(baseline / "result.json")] = BASE_RESULT_SHA
    pins[str(baseline / "geometry_application.npz")] = BASE_NUMERICAL_SHA
    result = dict(classification="ACTUAL_FIXED_FIELD_GEOMETRY_REFINEMENT_AND_LITERAL_COMPLEX_STEP",
        records=records, compact_numerical_sha256=base.sha(out / "compact_geometry_application.npz"),
        work_only_hessians_sha256=base.sha(out / "work_only_geometry_hessians.npz"),
        source_and_input_sha256=dict(sorted(pins.items())),
        exact_frozen_function_block_sha256=base.utility_block_sha256,
        frozen_function_names=list(UTILITY_NAMES), repository=str(REPO),
        radial_rule="96 compared against frozen48 full arrays;192 executed if any absolute entry difference exceeds2e-10",
        angular_rule="24cell is exact for homogeneous-background weak and geometry partials; radial/time error separate",
        complex_step_scope="independent original F polynomial, holomorphic value-only density/mechanical fields; no real clipping; axes0,98,99 at all three fixed steps",
        convergence_scope="finite fixed-field geometry100 covector and16x100 weak/momentum partials; numerical differences not a continuum enclosure",
        held_fixed="independent/recentered inherited remainder, raw Higgs/Hdot, EM q/qdot frame, four radial profiles and all source-extra maps",
        full_inherited_source_chain_or_domain_geometry_derivative=False,
        physical_radial_convergence_admitted=False, full_physical_derivative_admitted=False,
        coupled_corrections=0, native_or_interface_forces_added=False,
        Maxwell_or_original226_validation=None, physical_terminal_return=None, muon_moment=None)
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("complete", result["compact_numerical_sha256"], base.sha(out / "result.json"), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--frozen-producer", type=Path, required=True)
    args = parser.parse_args()
    execute(args.output, args.baseline, args.frozen_producer)
