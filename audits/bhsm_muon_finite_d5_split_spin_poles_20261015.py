"""New split simple-pole work on frozen finite D5 affine field matrices.

The original D5 coefficients, normal trace, source and history are read only.
Gamma(E) is rational after its original Schur reductions; it is evaluated
without linearizing the energy-dependent inverse or imposing degeneracy.
No physical retarded boundary, external scale or magnetic probe is supplied.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["OMP_NUM_THREADS"] = "2"
import numpy as np
from scipy.linalg import eig

REPO = Path(r"C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001")
WORK = Path(r"C:/Users/carbe/OneDrive/Documents/CODEX")
BASE = WORK / "outputs/bhsm_finite_d5_split_spin_poles_20261015"
OLD = "artifacts/muon_d5_finite_trace_pole_match_20261012/trial_0000_stage_pair_run_3"
GUARD = 2e-10
sys.path.insert(0, str(REPO / "src"))
from bhsm.interface.muon_holomorphic_d5_trace_action import normalized_two_sheet_point_action
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def maxabs(a):
    return float(np.max(np.abs(a)))


def clean(v):
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [clean(x) for x in v]
    if isinstance(v, np.ndarray):
        return clean(v.tolist())
    if isinstance(v, (complex, np.complexfloating)):
        return [float(v.real), float(v.imag)]
    if isinstance(v, np.generic):
        return v.item()
    return v


def trace_section(G, GE):
    X = np.linalg.solve(G[:4, :4], G[:4, 4:])
    Y = np.linalg.solve(G[:4, :4].T, G[4:, :4].T).T
    R, L = np.r_[-X, np.eye(2)], np.c_[-Y, np.eye(2)]
    return G[4:, 4:]-G[4:, :4]@X, L@GE@R, R, L


class Inputs:
    def __init__(self):
        self.pins = {}

    def read(self, relative, expected=None):
        p = REPO / relative
        raw = p.read_bytes()
        digest = sha256(raw).hexdigest()
        if expected is not None and expected != digest:
            raise ValueError("Frozen coefficient binding differs: " + relative)
        self.pins[relative] = digest
        if p.suffix == ".npz":
            with np.load(p, allow_pickle=False) as a:
                return {k: a[k].copy() for k in a.files}
        return json.loads(raw) if p.suffix == ".json" else raw.decode("utf-8-sig")


class FrozenStage:
    def __init__(self, inputs, source, source_md, stage, gamma0):
        self.stage = stage
        name = f"stage_{stage:04d}_current_geometry_normal_and_material_trace.npz"
        self.c = inputs.read(source + "/" + name, source_md["archives"][name]["sha256"])
        self.blocks = {}
        for eps in (1, -1):
            for branch in ("particle", "conjugate"):
                name = f"stage_{stage:04d}_eta_{eps:+d}_{branch}_original_radial_field_action.npz"
                a = inputs.read(source + "/" + name, source_md["archives"][name]["sha256"])
                self.blocks[eps, branch] = (a["original_unsquared_radial_action"],
                                           a["original_unsquared_radial_action_energy"])
        ids = np.array([2, 3, 8, 9, 14, 15])
        amb = np.arange(128, 256)
        self.M = self.c["fixedY_Higgs_intrinsic_seam_matrix"][np.ix_(ids, ids)]
        self.traces = []
        for label in ("plus", "minus"):
            tr = {}
            for key in ("normalized_right_Gamma0", "normal_mode_Dirac_bar_left_point_lift"):
                tr[key] = self.c[f"eta_{label}_" + key][np.ix_(ids, amb)]
            for key in ("normalized_Dirac_bar_left_Gamma0", "normal_mode_right_point_lift"):
                tr[key] = self.c[f"eta_{label}_" + key][np.ix_(amb, ids)]
            self.traces.append(tr)
        self.gamma0 = gamma0
        self.calls = 0

    def evaluate(self, E):
        sheet, sheetE = [], []
        radial_rows = 0.
        for eps in (1, -1):
            vals, first = [], []
            for branch in ("particle", "conjugate"):
                K0, KE = self.blocks[eps, branch]
                K = K0 + E*KE
                A, B, C, D = K[:192, :192], K[:192, 192:], K[192:, :192], K[192:, 192:]
                X = np.linalg.solve(A, B)
                rhsE = KE[:192, 192:]-KE[:192, :192]@X
                XE = np.linalg.solve(A, rhsE)
                vals.append(D-C@X)
                first.append(KE[192:, 192:]-KE[192:, :192]@X-C@XE)
                radial_rows = max(radial_rows, maxabs(A@X-B), maxabs(A@XE-rhsE))
            z = np.zeros((64, 64), complex)
            uv = self.c["actual_normalized_Gamma0_multiplier"].item()
            sheet.append(np.block([[vals[0], z], [z, vals[1]]])/(uv*uv))
            sheetE.append(np.block([[first[0], z], [z, first[1]]])/(uv*uv))
        app = normalized_two_sheet_point_action(
            np.array(sheet), np.array(sheetE), self.traces, self.M,
            self.c["actual_intrinsic_surface_density"].item(), self.gamma0,
            left_trace_count=4)
        self.calls += 1
        G, GE = app["finite_normalized_field_Gamma"], app["finite_normalized_field_Gamma_energy"]
        return G, GE, {"radial_interior_rows_max": radial_rows,
                       "full_field_and_trace_rows_max": maxabs(app["original_full_field_and_trace_rows"]),
                       "full_field_and_trace_energy_rows_max": maxabs(app["original_full_field_and_trace_energy_rows"])}


def simple_root(stage, seed, limit=8):
    E = complex(seed)
    history = []
    for iteration in range(limit):
        G, GE, checks = stage.evaluate(E)
        K, Z, R, L = trace_section(G, GE)
        w, vl, vr = eig(K, left=True, right=True)
        j = int(np.argmin(np.abs(w)))
        q, ell = vr[:, j], vl[:, j].conj()
        denominator = ell@Z@q
        if abs(denominator) < 1e-14:
            raise ArithmeticError("Unresolved simple-pole kinetic pairing")
        r = R@q
        l = (ell@L)/denominator
        residue = np.outer(r, l)
        rows = max(maxabs(G@r), maxabs(l@G), maxabs(G@residue), maxabs(residue@G))
        step = -(ell@K@q)/denominator
        history.append({"iteration": iteration, "energy": E,
                        "all_null_and_residue_rows_max": rows, "proposed_step": step})
        if rows <= GUARD:
            break
        E += step
    else:
        raise ArithmeticError("Bounded split-pole solve did not pass original rows")
    pairing = l@GE@r
    assert abs(pairing-1) <= GUARD
    return dict(energy=np.array(E), gamma6=G, gamma_energy6=GE,
                normalized_right6=r[:, None], normalized_literal_left6=l[None, :],
                residue6=residue, raw_kinetic_denominator=np.array(denominator),
                residue_pairing=np.array(pairing), full_null_right=G@r,
                full_null_left=l@G, residue_null_right=G@residue, residue_null_left=residue@G,
                charged_trace_K2=K, charged_trace_energy2=Z,
                four_complement_right_lift=R, four_complement_literal_left_lift=L,
                other_spin_trace_eigenvalue=np.array(w[1-j]),
                full_gamma_singular_values=np.linalg.svd(G, compute_uv=False),
                history=history, checks=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=int, required=True)
    args = parser.parse_args()
    out = BASE / f"run_{args.run}"
    out.mkdir(parents=True, exist_ok=False)
    inp = Inputs()
    inp.read("AGENTS.md")
    md = inp.read(OLD + "/result.json")
    source = md["source"]
    source_md = inp.read(source + "/result.json")
    for rel in ["src/bhsm/interface/muon_holomorphic_d5_trace_action.py",
                "src/bhsm/interface/muon_full_d5_localized_lepton_trace.py",
                "src/bhsm/interface/muon_coupled_phase_trace_projection.py",
                "src/bhsm/interface/muon_d5_finite_trace_pole_match.py"]:
        inp.read(rel)
    G0 = full_d5_localized_lepton_trace()["gamma5D_self_dual128"][0]
    records, archives = [], {}
    with nullcontext():
        for j in range(2):
            name = f"stage_{j:04d}_finite_trace_pole_and_clock_rows.npz"
            old = inp.read(OLD+"/"+name, md["archives"][name]["sha256"])
            stage = FrozenStage(inp, source, source_md, j, G0)
            E0 = old["energy_candidate"].item()
            G, GE, _ = stage.evaluate(E0)
            reproduction = max(maxabs(G-old["full_gamma"]), maxabs(GE-old["full_gamma_energy"]))
            if reproduction > GUARD:
                raise ArithmeticError("Same frozen rational Gamma failed center reproduction")
            K, Z, _, _ = trace_section(G, GE)
            shifts = eig(-K, Z, right=False)
            order = np.lexsort((shifts.imag, shifts.real))
            roots = [simple_root(stage, E0+shifts[k]) for k in order]
            if abs(roots[0]["energy"].item()-roots[1]["energy"].item()) < 1e-10:
                raise ArithmeticError("Two selected simple roots were not resolved")
            for branch, root in enumerate(roots):
                arrays = {k: v for k, v in root.items() if isinstance(v, np.ndarray)}
                for key in ("intrinsic_H_realified", "lapse", "radius", "gauge_connection_material",
                            "actual_intrinsic_surface_density", "actual_normalized_Gamma0_multiplier"):
                    arrays["same_stage_"+key] = stage.c[key]
                filename = f"stage_{j:04d}_branch_{branch}_actual_finite_simple_pole.npz"
                np.savez_compressed(out/filename, **arrays)
                archives[filename] = sha256((out/filename).read_bytes()).hexdigest()
                record = {"stage": j, "branch": branch, "energy": root["energy"].item(),
                          "offset_from_stored_center": root["energy"].item()-E0,
                          "center_Gamma_reproduction_max": reproduction,
                          "normalized_pairing": root["residue_pairing"].item(),
                          "raw_kinetic_denominator": root["raw_kinetic_denominator"].item(),
                          "null_right_max": maxabs(root["full_null_right"]),
                          "null_left_max": maxabs(root["full_null_left"]),
                          "residue_null_right_max": maxabs(root["residue_null_right"]),
                          "residue_null_left_max": maxabs(root["residue_null_left"]),
                          "other_spin_trace_eigenvalue": root["other_spin_trace_eigenvalue"].item(),
                          "history": root["history"], "original_rows": root["checks"]}
                records.append(record)
                print(json.dumps(clean(record), sort_keys=True), flush=True)
            print(json.dumps({"stage_complete": j, "Gamma_evaluations": stage.calls}), flush=True)
    for rel, digest in inp.pins.items():
        assert sha256((REPO/rel).read_bytes()).hexdigest() == digest, rel
    result = {
        "classification": "EVALUATED_TWO_DISTINCT_SIMPLE_POLES_OF_FROZEN_FINITE_D5_RATIONAL_TRACE_ACTION",
        "records": records, "archives": archives, "input_hashes": inp.pins,
        "energy_law": "Original stored K0+E KE, with differentiated radial and two-sheet inverses; Gamma(E) is rational, not an affine fit at the old center.",
        "branch_rule": "Both generalized charged-trace shifts from the stored center are retained and independently solved. Labels0/1 order initial complex shifts only, not physical spin orientation or measured mass.",
        "two_spin_degeneracy_assessment": "A shared-energy semisimple rank2 pole was an extra degeneracy assumption and is not justified on this nonzero/time-dependent finite background. The old failed rank2 candidate does not rule out two individually normalized simple poles. Physical spin-state and rest-frame assignments remain unproved.",
        "residue_law": "Gamma(E_s)r_s=0; l_s Gamma(E_s)=0; l_s Gamma_E(E_s)r_s=1; Res_s=r_s l_s, separately at each E_s. No extra conjugation of the analytic left row.",
        "normalized_TWO_SPIN_physical_state": None,
        "physical_exterior_selected": False, "physical_muon_poles_selected": False,
        "physical_mass_or_width_scale": None, "Gamma_B": None, "physical_magnetic_moment": None,
        "physical_a_mu": None, "measured_mass_or_anomaly_consumed": False,
        "nonzero_magnetic_or_charge_terms_set_zero": False,
        "action_coefficients_or_completed_D5_campaign_recomputed": False,
        "physical_corrections_applied": 0,
        "error_scope": "Binary64 new spectral algebra on frozen finite coefficients; original rows checked at2e-10. No upstream formation, normal-flow, physical retarded exterior or continuum error enclosure.",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "repeat_scope": "Run new split-pole spectral work twice byte-identically; original completed D5 coefficients, source and history are not replayed.",
    }
    rp = out/"result.json"
    rp.write_text(json.dumps(clean(result), sort_keys=True, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"result_sha256": sha256(rp.read_bytes()).hexdigest(), "out": str(out)}), flush=True)


if __name__ == "__main__":
    main()
