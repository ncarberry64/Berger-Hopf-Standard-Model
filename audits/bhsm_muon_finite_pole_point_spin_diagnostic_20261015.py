"""Conditional point-coefficient spin diagnostic on four saved finite poles.

The dagger below is ONLY the explicit canonical point coefficient Gram.
Independent pole left covectors remain analytic; no Hilbert adjoint replaces
them.  No spatial/normal state norm, applied field, or physical axis is made.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

sys.dont_write_bytecode = True
REPO = Path(r"C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001")
WORK = Path(r"C:/Users/carbe/OneDrive/Documents/CODEX")
SOURCE = WORK/"outputs/bhsm_finite_d5_split_spin_poles_20261015/run_1"
BASE = WORK/"outputs/bhsm_finite_pole_point_spin_diagnostic_20261015"
sys.path.insert(0, str(REPO/"src"))
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return clean(x.tolist())
    if isinstance(x, (complex, np.complexfloating)):
        return [float(x.real), float(x.imag)]
    if isinstance(x, np.generic):
        return x.item()
    return x


def maxabs(x):
    return float(np.max(abs(x)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=int, required=True)
    args = p.parse_args()
    out = BASE/f"run_{args.run}"
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def read(path, expected=None):
        path = Path(path)
        payload = path.read_bytes()
        digest = sha256(payload).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError("Actual saved pole or geometry changed: "+str(path))
        pins[str(path)] = digest
        if path.suffix == ".json":
            return json.loads(payload)
        if path.suffix == ".npz":
            with np.load(path, allow_pickle=False) as a:
                return {k: a[k].copy() for k in a.files}
        return payload.decode("utf-8-sig")

    for rel in ("AGENTS.md", "src/bhsm/interface/muon_native_dirac_hamiltonian.py",
                "src/bhsm/interface/muon_full_d5_localized_lepton_trace.py"):
        read(REPO/rel)
    md = read(SOURCE/"result.json")
    current = lepton_current_hilbert_representation()
    alpha = current["alpha"]
    spin18 = np.array([-.5j*alpha[b]@alpha[c] for b,c in ((1,2),(2,0),(0,1))])
    full = full_d5_localized_lepton_trace()
    gamma = full["gamma5D_self_dual128"]
    spin128 = np.array([.25j*(gamma[b]@gamma[c]-gamma[c]@gamma[b])
                        for b,c in ((2,3),(3,1),(1,2))])
    W, D = full["localized_lepton18_trace_lift"], full["localized_lepton18_literal_dual"]
    pulled = np.array([D@np.kron(np.eye(3),S)@W for S in spin128])
    ids = np.array([2,3,8,9,14,15])
    spin6 = spin18[:,ids][:,:,ids]
    gram6 = current["Gram"][np.ix_(ids,ids)]
    controls = {
        "full_D5_to_intrinsic_spin_max": maxabs(pulled-spin18),
        "spin6_Hermitian_max": maxabs(spin6-spin6.conj().transpose(0,2,1)),
        "spin6_Casimir_max": maxabs(sum(S@S for S in spin6)-.75*np.eye(6)),
        "spin6_lie_algebra_max": max(maxabs(spin6[b]@spin6[c]-spin6[c]@spin6[b]-1j*spin6[a])
                                     for a,b,c in ((0,1,2),(1,2,0),(2,0,1))),
        "point_Gram_minus_I6_max": maxabs(gram6-np.eye(6)),
    }
    assert max(controls.values()) < 2e-10
    geometry_controls = {}
    geometry = {}
    oldmd = read(REPO/"artifacts/muon_d5_finite_trace_pole_match_20261012/trial_0000_stage_pair_run_3/result.json")
    for stage in range(2):
        rel = oldmd["source"]+f"/stage_{stage:04d}_current_geometry_normal_and_material_trace.npz"
        c = read(REPO/rel, md["input_hashes"][rel])
        geometry[stage] = c
        amb = np.arange(128,256)
        checks = {}
        for sheet in ("plus", "minus"):
            ER = c[f"eta_{sheet}_normal_mode_right_point_lift"][np.ix_(amb,ids)]
            BR = c[f"eta_{sheet}_normalized_right_Gamma0"][np.ix_(ids,amb)]
            EL = c[f"eta_{sheet}_normal_mode_Dirac_bar_left_point_lift"][np.ix_(ids,amb)]
            BL = c[f"eta_{sheet}_normalized_Dirac_bar_left_Gamma0"][np.ix_(amb,ids)]
            checks[sheet] = {
                "right_point_intertwiner_max": max(maxabs(S@ER-ER@s) for S,s in zip(spin128,spin6)),
                "right_trace_intertwiner_max": max(maxabs(BR@S-s@BR) for S,s in zip(spin128,spin6)),
                "left_Dirac_bar_point_intertwiner_max": max(maxabs(EL@S-s@EL) for S,s in zip(spin128,spin6)),
                "left_Dirac_bar_trace_intertwiner_max": max(maxabs(S@BL-BL@s) for S,s in zip(spin128,spin6)),
            }
        geometry_controls[stage] = checks
    records, states, archives = [], {}, {}
    for name, digest in sorted(md["archives"].items()):
        a = read(SOURCE/name, digest)
        stage = int(name.split("_")[1]); branch = int(name.split("_")[3])
        r, l = a["normalized_right6"][:,0], a["normalized_literal_left6"][0]
        norm2 = np.vdot(r,gram6@r)
        assert abs(norm2.imag) < 1e-14 and norm2.real > 0
        norm = np.sqrt(norm2.real)
        u, ell = r/norm, l*norm
        G, GE = a["gamma6"], a["gamma_energy6"]
        means = np.array([np.vdot(u,gram6@S@u) for S in spin6])
        assert maxabs(means.imag) < 1e-13
        vector = means.real
        length = float(np.linalg.norm(vector))
        axis = vector/length
        Sn = sum(v*S for v,S in zip(axis,spin6))
        variance = np.array([np.vdot(u,gram6@S@S@u)-m*m for S,m in zip(spin6,means)])
        axis_residual = Sn@u-.5*u
        normalized_kinetic = ell@GE@u
        residue_retention = maxabs(np.outer(u,ell)-a["residue6"])
        assert abs(np.vdot(u,gram6@u)-1) < 2e-10
        assert abs(normalized_kinetic-1) < 2e-10
        assert residue_retention < 2e-10
        comm = np.array([G@S-S@G for S in spin6])
        point_uncertainty = {
            "component_variances_raw": variance,
            "axis_variance_via_norm_squared": float(np.linalg.norm((Sn-length*np.eye(6))@u)**2),
            "axis_eigenvalue_half_residual_norm": float(np.linalg.norm(axis_residual)),
            "polarization_half_deficit": .5-length,
            "scope": "Point coefficient Gram only; neither physical state uncertainty nor upstream numerical error enclosure. Nonzero impurity is retained.",
        }
        record = {"stage":stage,"branch":branch,"energy":a["energy"].item(),
                  "point_current_norm":np.vdot(u,gram6@u),
                  "pole_kinetic_pairing_after_reciprocal_left_rescale":normalized_kinetic,
                  "residue_retention_max":residue_retention,
                  "coefficient_spin_vector":means,"polarization_length":length,
                  "inferred_body_frame_axis":axis,"point_uncertainty":point_uncertainty,
                  "Gamma_spin_commutator_max_per_axis":np.array([maxabs(x)for x in comm]),
                  "Gamma_spin_commutator_Frobenius_per_axis":np.array([np.linalg.norm(x)for x in comm]),
                  "analytic_left_kinetic_right_spin_placement":np.array([ell@GE@S@u for S in spin6]),
                  "analytic_left_spin_left_kinetic_placement":np.array([ell@S@GE@u for S in spin6])}
        states[stage,branch] = u
        records.append(record)
        output_name = name.replace("actual_finite_simple_pole", "unit_point_coefficient_spin")
        np.savez_compressed(out/output_name,
            energy=a["energy"], gamma6=G,gamma_energy6=GE,
            unit_point_right6=u[:,None],reciprocally_rescaled_literal_left6=ell[None,:],
            unit_point_current_Gram6=gram6,spin_generators6=spin6,
            residue6=np.outer(u,ell),coefficient_spin_vector=means,
            inferred_body_frame_axis=axis,point_spin_variance=variance,
            axis_spin_eigen_residual=axis_residual,Gamma_spin_commutators=comm)
        archives[output_name] = sha256((out/output_name).read_bytes()).hexdigest()
    overlaps = []
    for stage in range(2):
        u,v = states[stage,0],states[stage,1]
        overlap = np.vdot(u,gram6@v)
        overlaps.append({"stage":stage,"coefficient_Gram_overlap":overlap,
                         "coefficient_overlap_abs_squared":float(abs(overlap)**2),
                         "interpretation":"Different-energy resonance coefficient modes need not be orthogonal. This is not a CAR density matrix or physical preparation probability."})
    for path,digest in pins.items():
        assert sha256(Path(path).read_bytes()).hexdigest() == digest
    result = {
        "classification":"EVALUATED_CONDITIONAL_POINT_COEFFICIENT_SPIN_ON_FOUR_DISTINCT_FINITE_POLES",
        "generator_law":"S_a=-i alpha_b alpha_c/2, verified against i[Gamma_b,Gamma_c]/4 through full D5 W/dual; C6 is selected by original family incidence, not assumed I3 tensor Pauli.",
        "operator_controls":controls,"saved_normal_point_intertwiners":geometry_controls,
        "records":records,"branch_overlaps":overlaps,"archives":archives,"input_hashes":pins,
        "state_normalization":"r_unit=r/sqrt(r_dagger I6 r); independent analytic l_unit=l*sqrt(r_dagger I6 r), preserving l Gamma_E r and residue. Dagger appears only in declared point coefficient Gram.",
        "physical_axis_selected":False,"physical_spin_state_selected":False,
        "global_positive_current_or_normal_mode_norm_evaluated":False,
        "applied_measuring_field_or_B0_limit_evaluated":False,"magnetic_moment":None,
        "missing_for_physical_axis":["Physical outgoing domain and same-mode global current/normal-state normalization", "Map from inherited body spatial frame to the actual measuring-field/rest frame", "Same-owner infinitesimal electromagnetic probe and its source/domain/response jets", "A controlled applied-B to zero family holding the formed background/preparation as declared; existing background splitting is not equated to Zeeman response"],
        "no_source_history_action_or_root_rebuild":True,"physical_corrections_applied":0,
        "repeat_scope":"New tiny coefficient-spin contractions repeated twice; no completed action/source/D5/history campaign repeated.",
        "producer_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    rp=out/"result.json"
    rp.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"output":str(out),"result_sha256":sha256(rp.read_bytes()).hexdigest(),"records":len(records)}))


if __name__ == "__main__":
    main()
