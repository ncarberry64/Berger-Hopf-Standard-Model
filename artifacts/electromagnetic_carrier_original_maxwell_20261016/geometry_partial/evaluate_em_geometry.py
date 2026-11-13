"""Isolated actual Maxwell geometry/source cross application; no physical gate.

The independent gauge, inherited remainder, EM frame and frozen material test
basis are held fixed.  The owned material geometry/density/mechanical family
varies through all original100 raw geometry coordinates.  There is no new
history, incoming state, force, or matching correction in this calculation.
"""
from __future__ import annotations

import argparse
import gc
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

REPO = Path(r"C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001")
sys.path[:0] = [str(REPO / "src"), str(REPO / "scripts")]
import evaluate_em_carrier_original_maxwell_20261016 as retained
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_baton_zoo_original_validation import independent_original_maxwell_weak
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows
from bhsm.interface.muon_parent_maxwell_full_weak import (
    M, background_subtracted_maxwell_action_jet, full_maxwell_weak_geometric_jets,
)
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation

GEOMETRY_KEYS = (
    "electric", "radial", "angular", "electric_radial", "shift",
    "connection_lambda", "lambda_tau", "lambda_rho",
)
DENSITY_KEYS = GEOMETRY_KEYS[:5]
FIELD_KEYS = ("gauge", "gauge_tau", "gauge_rho", "gauge_angular")
TEST_KEYS = ("tests", "tests_tau", "tests_rho", "tests_angular")


def real(a):
    x = np.asarray(a)
    if not np.isfinite(x).all() or np.any(x.imag != 0):
        raise ValueError("exactly real actual branch required; no imaginary projection")
    return x.real.copy()


def sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def norm(a):
    return float(np.max(np.abs(a))) if np.size(a) else 0.0


def difference(actual, expected):
    absolute = norm(np.asarray(actual) - np.asarray(expected))
    denominator = max(norm(actual), norm(expected), 1e-300)
    return dict(absolute=absolute, relative=absolute / denominator,
                scaled=absolute / max(1.0, denominator), denominator=denominator)


def real_geometry(raw, rho, *, differentiate):
    geo = holomorphic_geometry_rows(raw, rho, differentiate=differentiate)
    rows = []
    for row in geo["rows"]:
        rows.append({key: Jet(float(real(row[key].value)), real(row[key].gradient),
                              real(row[key].hessian)) for key in GEOMETRY_KEYS})
    return dict(rows=rows, coordinate_count=100 if differentiate else 0,
                clock="coordinate_time", response_chart=geo["response_chart"])


def mechanical(rows, nh):
    nr = len(rows)
    fields = [np.zeros((nr, nh, 5, 4)) for _ in range(3)]
    for placement, key, offset in ((0, "connection_lambda", 1),
                                   (1, "lambda_tau", 0), (2, "lambda_rho", 0)):
        values = np.array([r[key].value for r in rows]) - offset
        fields[placement][:, :, 2:] = values[:, None, None, None] * M[None, None]
    fields.append(np.zeros((nr, nh, 3, 5, 4)))
    return fields


def test_arrays(snap):
    directions = [retained.direction(snap, radial, mode)
                  for radial in range(4) for mode in range(4)]
    # Original weak indexed layout is (radial,test,Haar,field,internal).
    return [np.stack([d[i] for d in directions], axis=1) for i in range(4)]


def literal(raw, snap, independent, tests):
    """Fresh literal F polynomial at perturbed geometry, no AD weak call."""
    geo = real_geometry(raw, snap["rho"], differentiate=False)
    mech = mechanical(geo["rows"], len(snap["space"]["weights"]))
    total = [a + b for a, b in zip(independent, mech)]
    density = np.array([[r[key].value for key in DENSITY_KEYS] for r in geo["rows"]])
    nr, nh = total[0].shape[:2]
    density = np.broadcast_to(density[:, None], (nr, nh, 5)).reshape(-1, 5)
    nt = tests[0].shape[1]
    tf = [x.transpose(0, 2, 1, *range(3, x.ndim)).reshape(
        (nr * nh, nt) + x.shape[3:]) for x in tests]
    quadrature = (MAXWELL_TO_CAP * snap["wr"][:, None]
                  * snap["space"]["weights"][None]).ravel()

    def application(fields, test_fields):
        return independent_original_maxwell_weak(
            **dict(zip(("connection", "time_derivative", "radial_derivative",
                        "angular_derivative"),
                       [x.reshape((nr * nh,) + x.shape[2:]) for x in fields])),
            **dict(zip(("tests", "tests_time", "tests_radial", "tests_angular"), test_fields)),
            metric_densities=density, quadrature=quadrature)

    full = application(total, tf)
    zeros = [np.zeros((nr * nh, 1, 5, 4)) for _ in range(3)]
    zeros.append(np.zeros((nr * nh, 1, 3, 5, 4)))
    reference = application(mech, zeros)
    momentum = full["temporal_momentum"].reshape(nr, nh, 5, 4)
    ptest = np.einsum("rp,rjpic,rpic->j", quadrature.reshape(nr, nh),
                     tests[0], momentum)
    return dict(action=complex(full["original_action_value"] - reference["original_action_value"]),
                weak=full["original_weak_rows"], momentum=ptest,
                total_action=complex(full["original_action_value"]),
                mechanical_action=complex(reference["original_action_value"]))


def json_real(a):
    return real(a).tolist()


def execute(output, orders, steps):
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError("preserve prior evidence; choose an unused output folder")
    out.mkdir(parents=True)
    space = retained.even_angular_space()
    arrays, records, pins = {}, [], {}
    for side, path in retained.PHASES.items():
        phase = load_profile_preserving_phase(path, repository=REPO)
        pins.update(phase["input_hashes"])
        t = phase["receipt"]["span"] / 2
        previous = None
        for order in orders:
            print(f"{side} radial{order}: original real coefficient snapshot", flush=True)
            snap = retained.snapshot(phase, t, order, space)
            sample = retained.sample_coefficients(phase, t,
                retained.radial_representation(phase["representation"], snap["rho"]))[1]
            raw = real(sample["raw_fields"][:100])
            geo = real_geometry(raw, snap["rho"], differentiate=True)
            own = mechanical(geo["rows"], len(space["weights"]))
            independent = [a - b for a, b in zip(snap["fields"], own)]
            reconstructed = [a + b for a, b in zip(independent, own)]
            reconstruction = max(norm(a - b) for a, b in zip(reconstructed, snap["fields"]))
            if reconstruction > 1e-12:
                raise ValueError("mechanical recenter/reconstruction failed")
            tests = test_arrays(snap)
            H = real(snap["c"]["intrinsic_H_realified"])
            Hdot = real(snap["c"]["intrinsic_H_realified_first"][0])
            generators = higgs_u2_real_representation()["real_generators"]
            qH = np.einsum("c,cij->ij", snap["charge"], generators)
            qHdot = np.einsum("c,cij->ij", snap["charge_rate"], generators)
            neutral = qH @ H
            moving_neutral = qHdot @ H + qH @ Hdot
            higgs_identity = dict(
                neutral_norm=norm(neutral), total_clock_neutral_norm=norm(moving_neutral),
                held_axis_partial_clock_norm=norm(qH @ Hdot),
                axis_motion_term_norm=norm(qHdot @ H),
                full_H_norm=norm(H), full_Hdot_norm=norm(Hdot),
                scope="direct original Higgs representation identities; not an independent full mixed Higgs-action application")
            print(f"{side} radial{order}: full geometry100 action and EM16 weak jets", flush=True)
            action = background_subtracted_maxwell_action_jet(
                geo, MAXWELL_TO_CAP * snap["wr"], space["weights"],
                **dict(zip(FIELD_KEYS, independent)))
            weak = full_maxwell_weak_geometric_jets(
                geo, MAXWELL_TO_CAP * snap["wr"], space["weights"],
                **dict(zip(FIELD_KEYS, independent)), **dict(zip(TEST_KEYS, tests)))
            baseline = literal(raw, snap, independent, tests)
            controls = dict(
                action=difference(action["value"], baseline["action"]),
                weak=difference(weak["weak"]["values"], baseline["weak"]),
                momentum=difference(weak["temporal_momentum_test"]["values"], baseline["momentum"]))
            if max(v["scaled"] for v in controls.values()) > 2e-10:
                raise ValueError("independent same-operand literal baseline comparison failed")
            fd = []
            for label, axis in (("normal98", 98), ("rate99", 99), ("log_radius_q0", 0)):
                target = np.r_[action["gradient"][axis],
                    weak["weak"]["geometric_jacobian"][:, axis],
                    weak["temporal_momentum_test"]["geometric_jacobian"][:, axis]]
                table = []
                for h in steps:
                    values = {}
                    for multiplier in (-2, -1, 1, 2):
                        x = raw.copy(); x[axis] += multiplier * h
                        evaluated = literal(x, snap, independent, tests)
                        values[multiplier] = np.r_[evaluated["action"], evaluated["weak"], evaluated["momentum"]]
                    fd2 = (values[1] - values[-1]) / (2 * h)
                    fd4 = (-values[2] + 8 * values[1] - 8 * values[-1] + values[-2]) / (12 * h)
                    row = dict(h=h, centered2=difference(fd2, target), centered4=difference(fd4, target),
                        action4=difference(fd4[:1], target[:1]),
                        weak4=difference(fd4[1:17], target[1:17]),
                        momentum4=difference(fd4[17:], target[17:]),
                        all_ad_norm=norm(target), all_fd4_norm=norm(fd4))
                    table.append(row)
                fd.append(dict(direction=label, raw_index=axis, steps=table))
                print(f"{side} radial{order}: literal {label} sweep retained", flush=True)
            prefix = f"{side}_q{order}_"
            arrays.update({prefix + "geometry100": raw,
                prefix + "radial_nodes": snap["rho"], prefix + "radial_weights": snap["wr"],
                prefix + "density_and_mechanical_values": np.array([[r[k].value for k in GEOMETRY_KEYS] for r in geo["rows"]]),
                prefix + "density_and_mechanical_jacobian": np.array([[r[k].gradient for k in GEOMETRY_KEYS] for r in geo["rows"]]),
                prefix + "background_subtracted_action_value": np.array(action["value"]),
                prefix + "background_subtracted_action_gradient": action["gradient"],
                prefix + "background_subtracted_action_hessian": action["hessian"],
                prefix + "weak16": weak["weak"]["values"],
                prefix + "weak16_geometry_jacobian": weak["weak"]["geometric_jacobian"],
                prefix + "weak16_geometry_hessian": weak["weak"]["geometric_hessians"],
                prefix + "momentum16": weak["temporal_momentum_test"]["values"],
                prefix + "momentum16_geometry_jacobian": weak["temporal_momentum_test"]["geometric_jacobian"],
                prefix + "momentum16_geometry_hessian": weak["temporal_momentum_test"]["geometric_hessians"],
                prefix + "EM_inclusion": snap["s"], prefix + "EM_inclusion_clock": snap["sd"]})
            arrays.update({prefix + "intrinsic_H": H, prefix + "intrinsic_H_clock": Hdot,
                prefix + "charge_Higgs_representation": qH,
                prefix + "charge_clock_Higgs_representation": qHdot,
                prefix + "neutral_Higgs_identity": neutral,
                prefix + "moving_neutral_Higgs_identity": moving_neutral})
            record = dict(side=side, time=t, radial_order=order, angular_rule="24-cell degree5",
                recenter_reconstruction_max=reconstruction, literal_baseline_controls=controls,
                background_subtracted_action=float(action["value"]),
                full_action=float(action["full_action_value"]),
                mechanical_reference_action=float(action["mechanical_reference_value"]),
                geometry_covector100_norm=norm(action["gradient"]),
                EM_weak_geometry16x100_norm=norm(weak["weak"]["geometric_jacobian"]),
                EM_momentum_geometry16x100_norm=norm(weak["temporal_momentum_test"]["geometric_jacobian"]),
                direct_Higgs_alignment=higgs_identity,
                literal_fd_sweep=fd)
            current = dict(action_gradient=action["gradient"],
                weak_jacobian=weak["weak"]["geometric_jacobian"],
                momentum_jacobian=weak["temporal_momentum_test"]["geometric_jacobian"])
            if previous is not None:
                record["radial_difference_to_previous"] = {k: difference(current[k], previous[k]) for k in current}
            previous = current
            records.append(record)
            _compressed_npz(out / "geometry_application.npz", arrays)
            (out / "partial_result.json").write_text(json.dumps(records, indent=2, sort_keys=True, allow_nan=False) + "\n")
            del geo, weak, action, snap
            gc.collect()
    for name, module in list(sys.modules.items()):
        source = getattr(module, "__file__", None)
        if source and Path(source).is_relative_to(REPO) and (name.startswith("bhsm.") or name.startswith("bhsm_real") or name == retained.__name__):
            pins[Path(source).relative_to(REPO).as_posix()] = sha(source)
    pins[str(Path(__file__).resolve())] = sha(__file__)
    prep = REPO / "artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json"
    pins[prep.relative_to(REPO).as_posix()] = sha(prep)
    archive = out / "geometry_application.npz"
    result = dict(classification="ACTUAL_RETAINED_REAL_MAXWELL_FIXED_FIELD_GEOMETRY_PARTIAL",
        records=records, coordinate_count=100, EM_amplitude_tests=16,
        tests="all four owned frozen radial profiles and four Maxwell seed forms; actual s(H),sdot(H,Hdot)",
        numerical_sha256=sha(archive), source_and_input_sha256=dict(sorted(pins.items())),
        action="S_Maxwell(Abar(q)+a_fixed)-S_Maxwell(Abar(q)); MAXWELL_TO_CAP once",
        geometry_scope="original100 real material coefficients; density, wall chart, normal/rate and own mechanical connection two-jets",
        held_fixed="independent gauge/inherited remainder, raw Higgs/Hdot, photon H-axis, frozen radial/angular tests and source-extra maps",
        derivative_scope="partial geometry derivative at fixed independent fields/tests; not the full physical or outgoing derivative",
        stress_scope="finite geometry100 action covector; not a reconstructed full pointwise stress tensor",
        mechanical_energy_double_counted=False, independent_extra_source_recomputed=False,
        unreported_zero_sources_inserted=False, coupled_corrections=0,
        full_collider_preparation_realized=False, physical_radial_convergence_admitted=False,
        physical_derivative_admitted=False, physical_terminal_return=None,
        fresh_adopted_Maxwell_or_226_validation=None, muon_moment=None,
        fd_gate="all fixed steps retained; FD accuracy is a local partial control only, not physical2e-10 admission",
        matching_guard=2e-10)
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("complete", sha(archive), sha(out / "result.json"), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--radial-orders", nargs="+", type=int, default=[24, 48])
    parser.add_argument("--fd-steps", nargs="+", type=float, default=[1e-4, 3e-5, 1e-5, 3e-6, 1e-6])
    args = parser.parse_args()
    execute(args.output, args.radial_orders, args.fd_steps)
