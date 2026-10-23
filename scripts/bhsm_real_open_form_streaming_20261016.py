"""Chunked evaluation of the frozen real full-D5 fixed P1 open form.

The only change from the canonical full-cap producer is batching its exact
already-evaluated coefficient arrays. All trial columns, measure, endpoint
conormals, normalized-q seam, families, and spin rows stay unchanged. This is
fixed-form radial quadrature, not physical radial/domain convergence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from scipy import sparse

REPO = Path(__file__).resolve().parents[1]
CANONICAL = REPO / "scripts/bhsm_real_full_d5_combined_eta_open_form_20261016.py"
spec = importlib.util.spec_from_file_location("_canonical_real_open_form", CANONICAL)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def coefficient_digest(c):
    h = sha256()
    for key in sorted(c):
        h.update(key.encode())
        value = np.asarray(c[key])
        if value.dtype.hasobject:
            raise TypeError("Object dtype has no stable byte receipt: " + key)
        h.update(value.dtype.str.encode())
        h.update(str(value.shape).encode())
        h.update(value.tobytes())
    return h.hexdigest()


def select_coefficients(c, indices, count):
    """Slice only the source owner's explicit radial axes, never its H axis."""
    out = {}
    for key, value in c.items():
        if key in ("intrinsic_H_realified", "intrinsic_H_realified_first") or not isinstance(value, np.ndarray):
            out[key] = value
        elif key.endswith("_first"):
            if value.shape[1] != count:
                raise ValueError("Unexpected source radial axis: " + key)
            out[key] = value[:, indices]
        else:
            if value.shape[0] != count:
                raise ValueError("Unexpected value radial axis: " + key)
            out[key] = value[indices]
    return out


def expression(c, E, f, eps, h):
    eta = {branch: owner.combined_f_eta_contact(c,
        gamma=f["gamma5D_" + branch], carrier_count=16, angular_count=h,
        sheet_orientation=eps)["combined_f_eta_contact"]
        for branch in ("particle", "conjugate")}
    return owner.full_d5_differential_coefficients(c, E, sheet_orientation=eps,
        full_representation=f, sigma_eta_contacts=eta)


def load_matrix(archive, name):
    return sparse.csr_matrix((archive[name + "_data"], archive[name + "_indices"],
        archive[name + "_indptr"]), shape=tuple(archive[name + "_shape"]))


def execute(output, *, radial_order, chunk_size=4, reference=None):
    out = Path(output)
    if out.exists():
        raise FileExistsError(out)
    if radial_order < 1 or chunk_size < 1:
        raise ValueError("Positive Gauss order and chunk size required")
    angular = owner.scalar_s3_discretization(1)
    E = angular["angular_derivative_matrices"]
    h, d = E.shape[-1], 64 * E.shape[-1]
    f = owner.full_d5_localized_lepton_trace()
    q, w = np.polynomial.legendre.leggauss(radial_order)
    rho, wr = (q + 1) * owner.WALL / 2, w * owner.WALL / 2
    allrho = np.r_[rho, owner.WALL]
    qt, wt = np.polynomial.legendre.leggauss(2)
    rng = np.random.default_rng(561614)
    arrays, records, pins = {}, [], {}
    for side, path in owner.PHASES.items():
        phase = owner.load_profile_preserving_phase(path, repository=REPO)
        if phase["receipt"]["steps"] != 1:
            raise ValueError("Original one-cell histories required")
        pins.update(phase["input_hashes"])
        span = float(phase["receipt"]["span"])
        lo, hi = min(0., span), max(0., span)
        ts, ws = lo + (qt + 1) * (hi - lo) / 2, wt * (hi - lo) / 2
        rep = owner.radial_representation(phase["representation"], allrho)
        matrices = {(eps, branch, name): sparse.csr_matrix((4*d, 4*d), dtype=complex)
            for eps in (-1, 1) for branch in ("particle", "conjugate")
            for name in ("K", "M", "wall_conormal")}
        probe = {(eps, branch): rng.normal(size=(3, 4, d)) + 1j*rng.normal(size=(3, 4, d))
            for eps in (-1, 1) for branch in ("particle", "conjugate")}
        direct = {eps: 0. for eps in (-1, 1)}
        seam = np.zeros((36*h, 36*h), complex)
        coefficient_hashes = {}
        for i, (t, ww) in enumerate(zip(ts, ws)):
            c, sample = owner.sample_coefficients(phase, float(t), rep)
            coefficient_hashes["t" + str(i)] = coefficient_digest(c)
            V, Vt, Vr = owner.trial(t, lo, hi, allrho)
            phi = np.array([1-(t-lo)/(hi-lo), (t-lo)/(hi-lo)])
            hr = sample["raw_fields"][260:264]
            M18 = owner.fixed_y_higgs_hamiltonian(np.array([hr[:2]+1j*hr[2:]]))[0]
            surface = float((c["surface_proper_clock_rate"][-1]*c["radius"][-1]**3).real)
            seam -= ww*surface*2*np.pi**2*np.kron(np.outer(phi, phi), np.kron(M18, np.eye(h)))
            arrays[f"{side}_t{i}_raw"] = sample["raw_fields"]
            arrays[f"{side}_t{i}_rawtime"] = sample["raw_coordinate_time_derivative"]
            for start in range(0, radial_order, chunk_size):
                indices = np.arange(start, min(start+chunk_size, radial_order))
                cc = select_coefficients(c, indices, len(allrho))
                for eps in (-1, 1):
                    a = expression(cc, E, f, eps, h)
                    u = np.zeros((len(indices), 6*d, 1), complex)
                    ut, ur = np.zeros_like(u), np.zeros_like(u)
                    for bi, branch in enumerate(("particle", "conjugate")):
                        block = a["blocks"][branch]
                        for j, global_j in enumerate(indices):
                            A, v = owner.point_maps(block, j, V[global_j], Vt[global_j], Vr[global_j], d)
                            weight = ww*wr[global_j]*2*np.pi**2*float(c["volume_density"][global_j].real)
                            matrices[eps, branch, "K"] += weight*(A.conj().T@A)
                            matrices[eps, branch, "M"] += weight*(v.conj().T@v)
                        for family in range(3):
                            sl = slice((2*family+bi)*d, (2*family+bi+1)*d)
                            for target, basis in ((u,V), (ut,Vt), (ur,Vr)):
                                target[:,sl,0] = np.einsum("qk,kj->qj", basis[indices], probe[eps,branch][family])
                    acted = owner.apply_full_d5_expression(a,u,ur,ut,placement="formal_product")
                    direct[eps] += float(np.dot(ww*wr[indices]*2*np.pi**2*c["volume_density"][indices].real,
                        np.sum(abs(acted[:,:,0])**2,axis=1)))
                    del a
            wall = select_coefficients(c, np.array([radial_order]), len(allrho))
            for eps in (-1,1):
                a = expression(wall,E,f,eps,h)
                for branch in ("particle","conjugate"):
                    block = a["blocks"][branch]
                    A,v = owner.point_maps(block,0,V[-1],Vt[-1],Vr[-1],d)
                    ar = sparse.csr_matrix(block["A_radial"][0])
                    matrices[eps,branch,"wall_conormal"] += ww*2*np.pi**2*float(c["volume_density"][-1].real)*(v.conj().T@ar.conj().T@A)
                del a
        for label,t,orientation in (("lo",lo,-1),("hi",hi,1)):
            c,sample = owner.sample_coefficients(phase,float(t),rep)
            coefficient_hashes["temporal_"+label] = coefficient_digest(c)
            V,Vt,Vr = owner.trial(t,lo,hi,allrho)
            arrays[f"{side}_temporal_{label}_raw"] = sample["raw_fields"]
            temporal = {(eps,branch):sparse.csr_matrix((4*d,4*d),dtype=complex)
                for eps in (-1,1) for branch in ("particle","conjugate")}
            for start in range(0,radial_order,chunk_size):
                indices = np.arange(start,min(start+chunk_size,radial_order))
                cc = select_coefficients(c,indices,len(allrho))
                for eps in (-1,1):
                    a = expression(cc,E,f,eps,h)
                    for branch in ("particle","conjugate"):
                        for j,global_j in enumerate(indices):
                            A,v = owner.point_maps(a["blocks"][branch],j,V[global_j],Vt[global_j],Vr[global_j],d)
                            weight = orientation*wr[global_j]*2*np.pi**2*float((c["volume_density"][global_j]/c["lapse"][global_j]).real)
                            temporal[eps,branch] += weight*(v.conj().T@A)
                    del a
            for (eps,branch),T in temporal.items():
                owner.save_sparse(arrays,f"{side}_eta{eps}_{branch}_temporal_{label}_conormal",T)
        errors = {}
        for eps in (-1,1):
            value = 0j
            for branch in ("particle","conjugate"):
                K = matrices[eps,branch,"K"]
                for state in probe[eps,branch]:
                    x=state.reshape(-1);value+=np.vdot(x,K@x)
                for name in ("K","M","wall_conormal"):
                    owner.save_sparse(arrays,f"{side}_eta{eps}_{branch}_"+name,matrices[eps,branch,name])
            errors[f"eta{eps}"] = float(abs(value-direct[eps])/max(abs(value),abs(direct[eps]),1.))
        records.append(dict(side=side,coefficient_sha256=coefficient_hashes,
            full384_direct_form_relative_errors=errors,span=span))
        arrays[side+"_intrinsic_normalized_q_SH_form"]=seam
        arrays[side+"_times"],arrays[side+"_time_weights"]=ts,ws
    arrays.update(radial_quadrature=rho,radial_weights=wr,
        angular_labels=np.array(owner.scalar_section_labels(1)),angular_derivatives=E)
    error=max(v for row in records for v in row["full384_direct_form_relative_errors"].values())
    if error>2e-12:
        raise ArithmeticError("Streaming form and full384 differential applications disagree")
    controls={}
    if reference:
        with np.load(Path(reference)/"application.npz") as archive:
            for key in arrays:
                if key.endswith("_shape"):
                    name=key[:-6]
                    left,right=load_matrix(arrays,name),load_matrix(archive,name)
                    delta=float(sparse.linalg.norm(left-right))
                    controls[name]=delta/max(float(sparse.linalg.norm(left)),float(sparse.linalg.norm(right)),np.finfo(float).tiny)
            for key in arrays:
                if not key.endswith(("_data","_indices","_indptr","_shape")):
                    if not np.array_equal(arrays[key],archive[key]):
                        raise ArithmeticError("Held operand differs from canonical reference: "+key)
        if max(controls.values())>2e-12:
            raise ArithmeticError("Chunked matrices differ from canonical producer")
    for name,module in list(sys.modules.items()):
        path=getattr(module,"__file__",None)
        if name.startswith("bhsm.")and path and Path(path).is_relative_to(REPO):
            pins[Path(path).relative_to(REPO).as_posix()]=digest(Path(path))
    pins[CANONICAL.relative_to(REPO).as_posix()]=digest(CANONICAL)
    pins[Path(__file__).resolve().relative_to(REPO).as_posix()]=digest(Path(__file__))
    result=dict(classification="STREAMED_FIXED_P1_REAL_FULL384_OPEN_FORM_QUADRATURE",
        radial_order=radial_order,chunk_size=chunk_size,angular_level=1,angular_count=h,time_order=2,
        records=records,canonical_matrix_relative_controls=controls,
        reference_application_sha256=digest(Path(reference)/"application.npz")if reference else None,
        source_and_input_sha256=dict(sorted(pins.items())),
        coefficients_sliced_from_exact_full_radial_arrays=True,
        full_spin_and_all_three_families_retained=True,all_endpoint_coefficients_free=True,
        normalized_q_seam_separate_from_positive_K=True,
        normal_mode_wall_values_uL_uR=None,physical_outgoing_load=None,
        physical_incoming_load=None,physical_mean_solved=False,full_native_domain_selected=False,
        physical_radial_convergence_passed=False,physical_derivative_at_2e_minus10_passed=False,
        coupled_corrections=0,normalized_physical_spins=None,physical_muon_magnetic_moment=None)
    out.mkdir(parents=True)
    owner._compressed_npz(out/"application.npz",arrays)
    result["numerical_sha256"]=digest(out/"application.npz")
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(dict(radial_order=radial_order,max_full384_form_error=error,
        max_canonical_control=max(controls.values())if controls else None,
        numerical_sha256=result["numerical_sha256"])))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True);p.add_argument("--radial-order",type=int,required=True)
    p.add_argument("--chunk-size",type=int,default=4);p.add_argument("--reference")
    a=p.parse_args();execute(a.output,radial_order=a.radial_order,chunk_size=a.chunk_size,reference=a.reference)
