"""Real full-D5 open forms using the primary combined f_eta contact.

The earlier global sigma-normal attempt is preserved separately. This
coefficient is the covector f-contact, not its sigma-normal projection.
No nonunitary sin(f) rescaling, pole regularization or exterior is chosen.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy import sparse

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/"src"))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_raw_sample
from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_wall_material_eta
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_material_green_trace
from bhsm.interface.muon_combined_f_eta_contact import combined_f_eta_contact
from bhsm.interface.muon_full_d5_differential_form import full_d5_differential_coefficients,apply_full_d5_expression
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace,moving_d5_material_trace_frame
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization,scalar_section_labels
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

PHASES=dict(incoming="artifacts/muon_finite_normal_phase_20261011/incoming_run_1",
            outgoing="artifacts/muon_inherited_finite_normal_phase_20261011/run_1")

def geometry_rate(x):
    a=np.zeros_like(x);a[:37]=x[37:74];a[98]=x[99];return a

def radial_representation(rep,rho):
    """Reevaluate the frozen coordinate basis without renormalization."""
    out=dict(rep);V,D=trace_enriched_radial_basis(rep,rho)
    B=np.zeros((len(rho),80,1,5,4));Br=np.zeros_like(B)
    for k,label in enumerate(rep["gauge_labels"]):
        f,i,j=FIELD_ORDER.index(label["field"]),label["internal"],label["radial"]
        B[:,k,0,f,i]=V[:,j];Br[:,k,0,f,i]=D[:,j]
    out.update(rho=np.array(rho),gauge_basis=B,gauge_radial_basis=Br)
    return out

def sample_coefficients(phase,t,rep):
    s=profile_preserving_raw_sample(phase,t);x,dx=s["raw_fields"],s["raw_coordinate_time_derivative"]
    if not np.isrealobj(x)or not np.isrealobj(dx):raise ValueError("No complex-history projection")
    if phase["receipt"]["side"]=="outgoing":
        pair,ref=phase["arrays"]["initial_pair"],phase["arrays"]["reference_pair"]
        p=affine_geometry_germ(pair[0],t);refs=np.array([affine_geometry_germ(a,t)for a in ref])
        dp=geometry_rate(pair[0])[:,None];dr=np.array([geometry_rate(a)[:,None]for a in ref]);side="child"
    else:
        p,refs=x.copy(),np.array([x,x]);dp,dr=dx[:,None],np.array([dx[:,None],dx[:,None]]);side="parent"
    c=d5_trial_stage_coefficients(x,dx[:,None],p,dp,refs,dr,rep,rep["rho"],side=side)
    for key in ("lapse","radial_coframe","radius","coordinate_shift","volume_density","material_wall_velocity"):
        if np.any(c[key].imag!=0):raise ValueError("Coefficient left real chart: "+key)
    if any(np.any(c[k].real<=0)for k in("lapse","radial_coframe","radius","volume_density")):
        raise ValueError("Regular positive real coframe required")
    return c,s

def trial(t,lo,hi,rho):
    T=np.array([1-(t-lo)/(hi-lo),(t-lo)/(hi-lo)]);Dt=np.array([-1.,1.])/(hi-lo)
    R=np.c_[1-rho/WALL,rho/WALL];Dr=np.broadcast_to(np.array([-1.,1.])/WALL,R.shape)
    return tuple(np.einsum("a,qb->qab",a,b).reshape(len(rho),4)for a,b in((T,R),(Dt,R),(T,Dr)))

def point_maps(block,j,V,Vt,Vr,d):
    T,R,B=(sparse.csr_matrix(block[k][j])for k in("A_time","A_radial","A_body"))
    A=sparse.hstack([Vt[k]*T+Vr[k]*R+V[k]*B for k in range(4)],format="csr")
    v=sparse.hstack([a*sparse.eye(d,format="csr")for a in V],format="csr")
    return A,v

def save_sparse(arrays,name,A):
    A=A.tocsr()
    arrays[name+"_data"],arrays[name+"_indices"],arrays[name+"_indptr"]=A.data,A.indices,A.indptr
    arrays[name+"_shape"]=np.array(A.shape,np.int64)

def trace_numerators(c,f):
    """Known numerators only: actual B=D/uR, Cbar=S Gamma0 W/uL."""
    U=float(c["material_wall_velocity"][-1].real)
    G0=np.kron(np.eye(3),f["gamma5D_self_dual128"][0]);W=f["localized_lepton18_trace_lift"]
    result={}
    for eps in(-1,1):
        a=moving_d5_material_trace_frame(-eps*U,0,full_representation=f)
        S=np.kron(np.eye(3),a["spin_boost128"])
        result[eps]=dict(right_trace_numerator=a["ambient_literal_trace_dual"],
            Dirac_bar_left_trace_numerator=S@G0@W,mode_lift_numerator=a["ambient_trace_lift"],
            spin_boost128=a["spin_boost128"],
            current_isometry_residual=np.array(np.max(abs(a["real_wall_Hilbert_current_isometry_rows"]))))
    return result

def execute(output,*,angular_level=1,time_order=2,radial_order=4):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError("Preserve independently executed applications")
    angular=scalar_s3_discretization(angular_level);E=angular["angular_derivative_matrices"]
    h=E.shape[-1];d=64*h;f=full_d5_localized_lepton_trace()
    q,w=np.polynomial.legendre.leggauss(radial_order);rho,wr=(q+1)*WALL/2,w*WALL/2
    allrho=np.r_[rho,WALL];qt,wt=np.polynomial.legendre.leggauss(time_order)
    arrays,records,pins={},[],{};rng=np.random.default_rng(561614)
    for side,path in PHASES.items():
        phase=load_profile_preserving_phase(path,repository=REPO)
        if phase["receipt"]["steps"]!=1:raise ValueError("This application pins the original one-cell histories")
        pins.update(phase["input_hashes"]);span=float(phase["receipt"]["span"])
        lo,hi=min(0.,span),max(0.,span);ts=lo+(qt+1)*(hi-lo)/2;ws=wt*(hi-lo)/2
        rep=radial_representation(phase["representation"],allrho)
        matrices={(eps,b,n):sparse.csr_matrix((4*d,4*d),dtype=complex)
            for eps in(-1,1)for b in("particle","conjugate")for n in("K","M","wall_conormal")}
        probe={(eps,b):rng.normal(size=(3,4,d))+1j*rng.normal(size=(3,4,d))
            for eps in(-1,1)for b in("particle","conjugate")}
        direct={eps:0. for eps in(-1,1)};seam=np.zeros((36*h,36*h),complex);samples=[]
        for i,(t,ww)in enumerate(zip(ts,ws)):
            c,s=sample_coefficients(phase,float(t),rep);V,Vt,Vr=trial(t,lo,hi,allrho)
            phi=np.array([1-(t-lo)/(hi-lo),(t-lo)/(hi-lo)])
            hr=s["raw_fields"][260:264];H=np.array([hr[:2]+1j*hr[2:]])
            M18=fixed_y_higgs_hamiltonian(H)[0]
            surface=float((c["surface_proper_clock_rate"][-1]*c["radius"][-1]**3).real)
            seam-=ww*surface*2*np.pi**2*np.kron(np.outer(phi,phi),np.kron(M18,np.eye(h)))
            for eps in(-1,1):
                eta={};wall_errors={}
                for b in("particle","conjugate"):
                    e=combined_f_eta_contact(c,gamma=f["gamma5D_"+b],carrier_count=16,angular_count=h,sheet_orientation=eps)
                    eta[b]=e["combined_f_eta_contact"]
                    reference=d5_wall_material_eta(c,gamma=f["gamma5D_"+b],carrier_count=16,angular_count=h,sheet_orientation=eps)
                    wall_errors[b]=float(np.max(abs(eta[b][-1]-reference["actual_wall_material_eta_contact"])))
                    arrays[f"{side}_t{i}_eta{eps}_{b}_combined_f_eta_first"]=e["combined_f_eta_contact_first"]
                    arrays[f"{side}_t{i}_eta{eps}_{b}_Q_f"]=e["f_gradient_spacelike_square"]
                a=full_d5_differential_coefficients(c,E,sheet_orientation=eps,full_representation=f,sigma_eta_contacts=eta)
                u=np.zeros((len(allrho),6*d,1),complex);ut=np.zeros_like(u);ur=np.zeros_like(u)
                for bi,b in enumerate(("particle","conjugate")):
                    block=a["blocks"][b]
                    green=d5_material_green_trace(c,gamma=f["gamma5D_"+b],carrier_count=16,
                        angular_count=h,sheet_orientation=eps,point_index=radial_order)
                    arrays[f"{side}_t{i}_eta{eps}_{b}_original_Dirac_bar_wall_Green"]=green["original_Dirac_bar_Green_matrix"]
                    for j in range(radial_order):
                        A,v=point_maps(block,j,V[j],Vt[j],Vr[j],d)
                        weight=ww*wr[j]*2*np.pi**2*float(c["volume_density"][j].real)
                        matrices[eps,b,"K"]+=weight*(A.conj().T@A)
                        matrices[eps,b,"M"]+=weight*(v.conj().T@v)
                    j=radial_order;A,v=point_maps(block,j,V[j],Vt[j],Vr[j],d)
                    ar=sparse.csr_matrix(block["A_radial"][j])
                    # Fixed MATERIAL rho wall: z already includes wall motion.
                    matrices[eps,b,"wall_conormal"]+=ww*2*np.pi**2*float(c["volume_density"][j].real)*(v.conj().T@ar.conj().T@A)
                    for family in range(3):
                        sl=slice((2*family+bi)*d,(2*family+bi+1)*d)
                        for target,basis in((u,V),(ut,Vt),(ur,Vr)):
                            target[:,sl,0]=np.einsum("qk,kj->qj",basis,probe[eps,b][family])
                    arrays[f"{side}_t{i}_eta{eps}_{b}_combined_f_eta"]=block["sigma_eta_contact"]
                acted=apply_full_d5_expression(a,u,ur,ut,placement="formal_product")
                direct[eps]+=float(np.dot(ww*wr*2*np.pi**2*c["volume_density"][:-1].real,np.sum(abs(acted[:-1,:,0])**2,axis=1)))
                del a
            for eps,z in trace_numerators(c,f).items():
                for name,value in z.items():arrays[f"{side}_t{i}_eta{eps}_"+name]=value
            for name in("lapse","radial_coframe","radius","coordinate_shift","volume_density","geometric_time_contact","geometric_radial_contact","material_wall_velocity"):
                arrays[f"{side}_t{i}_"+name]=c[name]
            arrays[f"{side}_t{i}_raw"]=s["raw_fields"];arrays[f"{side}_t{i}_rawtime"]=s["raw_coordinate_time_derivative"]
            arrays[f"{side}_t{i}_H18"]=M18
            samples.append(dict(time=float(t),surface_density=surface,H18_norm=float(np.linalg.norm(M18)),
                minimum_volume_density=float(np.min(c["volume_density"].real)),
                last_eta_orientation_wall_overlap_errors=wall_errors))
        # Both temporal endpoint conormals are assembled, not prescribed.
        # Coefficients are the one-sided saved-cell interpolation, including
        # midpoint v/y; they are not newly imposed physical Cauchy data.
        for label,t,orientation in(("lo",lo,-1),("hi",hi,1)):
            c,s=sample_coefficients(phase,float(t),rep);V,Vt,Vr=trial(t,lo,hi,allrho)
            arrays[f"{side}_temporal_{label}_raw"]=s["raw_fields"]
            for eps in(-1,1):
                eta={b:combined_f_eta_contact(c,gamma=f["gamma5D_"+b],carrier_count=16,
                    angular_count=h,sheet_orientation=eps)["combined_f_eta_contact"]
                    for b in("particle","conjugate")}
                a=full_d5_differential_coefficients(c,E,sheet_orientation=eps,full_representation=f,sigma_eta_contacts=eta)
                for b in("particle","conjugate"):
                    T=sparse.csr_matrix((4*d,4*d),dtype=complex)
                    for j in range(radial_order):
                        A,v=point_maps(a["blocks"][b],j,V[j],Vt[j],Vr[j],d)
                        weight=orientation*wr[j]*2*np.pi**2*float((c["volume_density"][j]/c["lapse"][j]).real)
                        T+=weight*(v.conj().T@A)
                    save_sparse(arrays,f"{side}_eta{eps}_{b}_temporal_{label}_conormal",T)
                del a
        errors,hermitian={},{}
        for eps in(-1,1):
            value=0j
            for b in("particle","conjugate"):
                K=matrices[eps,b,"K"]
                hermitian[f"eta{eps}_{b}"]=float(sparse.linalg.norm(K-K.conj().T)/max(1.,sparse.linalg.norm(K)))
                for state in probe[eps,b]:
                    x=state.reshape(-1);value+=np.vdot(x,K@x)
                for name in("K","M","wall_conormal"):save_sparse(arrays,f"{side}_eta{eps}_{b}_"+name,matrices[eps,b,name])
            errors[f"eta{eps}"]=float(abs(value-direct[eps])/max(abs(value),abs(direct[eps]),1.))
        arrays[side+"_intrinsic_normalized_q_SH_form"]=seam;arrays[side+"_times"]=ts;arrays[side+"_time_weights"]=ws
        records.append(dict(side=side,span=span,samples=samples,relative_full384_form_probe_errors=errors,
            relative_K_Hermitian_errors=hermitian,dimension_per_family_branch=4*d,
            full_bulk_trial_dimension_per_eta=6*4*d,actual_saved_real_coefficients=True,
            imaginary_projection_performed=False,inherited_profile_composed_once=(side=="outgoing"),
            all_time_and_radial_endpoint_coefficients_free=True))
    arrays.update(radial_quadrature=rho,radial_weights=wr,angular_labels=np.array(scalar_section_labels(angular_level)),angular_derivatives=E)
    for name,module in list(sys.modules.items()):
        p=getattr(module,"__file__",None)
        if name.startswith("bhsm.")and p and Path(p).is_relative_to(REPO):
            pins[Path(p).relative_to(REPO).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).resolve().relative_to(REPO).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    eta_source=REPO/"src/bhsm/interface/muon_combined_f_eta_contact.py"
    pins[eta_source.relative_to(REPO).as_posix()]=sha256(eta_source.read_bytes()).hexdigest()
    result=dict(classification="REAL_SAVED_FULL384_D5_OPEN_TENSOR_PRODUCT_FORMS",records=records,
        angular_level=angular_level,angular_count=h,time_order=time_order,radial_order=radial_order,
        trial_space="P1 time x P1 radial x owned PW band x complete384 fiber; identical family blocks repeated exactly",
        Haar_measure="Unit Haar Gram times2pi² once",real_current_Gram="I384 in owned Eulerian frame",
        eta_source="v14.45 m=-partial_s log sinf plus v15.26 f-normal orientation; normalization sqrt cancels before continuation",
        eta_coefficient_is_old_sigma_normal_projection=False,
        spacelike_unit_normal_or_Gaussian_chart_extended_through_cap=False,
        nonunitary_sin_f_transform_used_to_delete_eta=False,
        polar_sin_f_zero_domain_regularization_proved=False,
        sigma_normal_full_collar_normalization=None,normal_mode_wall_values_uL_uR=None,
        trace_numerators="Known D,S Gamma0 W numerators; actual normalized B=D/uR,Cbar=S Gamma0 W/uL retain unevaluated denominators",
        seam_scope="Actual normalized-q once-only SH form; first-order domain contact, NEVER added as potential to positive K",
        normalized_seam_bound_to_bulk_form=False,physical_outgoing_load=None,physical_incoming_load=None,
        both_one_sided_temporal_conormals_assembled=True,
        wall_conormal_uses_fixed_material_rho_no_second_wall_velocity=True,
        temporal_birth_matter_trace_map=None,all_eta_and_temporal_trace_complements_retained=True,
        pole_scope="No point value fixed at the polar coordinate origin; numerical finite-energy trial space, not a domain/completeness certificate",
        historical_action_nu_squared=4,historical_Higgs_lambda="provisional assigned representation value",
        continuous_Euler_or_physical_mean_solved=False,full_native_domain_selected=False,
        physical_radial_or_angular_convergence_passed=False,physical_derivative_at_2e_minus10_passed=False,
        new_history_or_source_campaigns=0,coupled_corrections=0,normalized_physical_spins=None,
        physical_muon_magnetic_moment=None,input_and_source_sha256=dict(sorted(pins.items())))
    error=max(v for r in records for v in r["relative_full384_form_probe_errors"].values())
    if error>2e-12:raise ArithmeticError("Assembled form disagrees with independent full-carrier application")
    out.mkdir(parents=True);_compressed_npz(out/"application.npz",arrays)
    result["numerical_sha256"]=sha256((out/"application.npz").read_bytes()).hexdigest()
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(dict(samples=sum(len(r["samples"])for r in records),angular_count=h,max_relative_form_error=error,numerical_sha256=result["numerical_sha256"],physical_derivative_pass=False)))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",required=True)
    p.add_argument("--angular-level",type=int,default=1);p.add_argument("--time-order",type=int,default=2);p.add_argument("--radial-order",type=int,default=4)
    a=p.parse_args();execute(a.output,angular_level=a.angular_level,time_order=a.time_order,radial_order=a.radial_order)
