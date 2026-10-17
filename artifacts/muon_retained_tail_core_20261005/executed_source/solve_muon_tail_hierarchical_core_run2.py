"""Exact joining-constraint chart of the cached open-port parent-core model."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
from scipy.linalg import lu_factor,lu_solve


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cj(z):return dict(real=float(z.real),imag=float(z.imag))


def run(root,source,out):
    if out.exists():raise FileExistsError('fresh output required')
    out.mkdir(parents=True)
    a=read(source/'partial_system_with_tail_core.npz');base=root/'artifacts/muon_prefix_time_element_20261004'
    pre=read(base/'run_1/prefix_time_element.npz');br=read(base/'assembly_run_1/cut_to_future1_element.npz')
    fut=read(base/'future_run_2/retained_arc_time_element.npz')
    H=a['H'];f=a['rhs'];C=a['trace_continuity'];d=24;n=len(H);I=np.eye(d)
    sp=float(pre['temporal_basis_scale']);sb=float(br['temporal_basis_scale']);sf=float(fut['temporal_basis_scale'])
    # Free coordinates: prefix physical-time slope v, node1 g1, node2 g2.
    # Port g is free, not a selected physical incoming boundary condition.
    O=np.vstack((I,np.zeros((d,d)),I/2,-I/sb,np.zeros((2*d,d))))
    Z=np.zeros((n,3*d),complex)
    Z[:d,:d]=sp*I/2;Z[d:2*d,:d]=I
    Z[2*d:3*d,:d]=sp*I/2;Z[3*d:4*d,:d]=-sp*I/sb
    Z[2*d:3*d,d:2*d]=I/2;Z[3*d:4*d,d:2*d]=I/sb
    Z[4*d:5*d,d:2*d]=I/2;Z[5*d:,d:2*d]=-I/sf
    Z[4*d:5*d,2*d:]=I/2;Z[5*d:,2*d:]=I/sf
    L=np.zeros((d,n),complex);L[:,:2*d]=pre['hierarchical_to_endpoint_coefficients'][:d]
    # Neither a tolerance-based kernel nor a dropped tiny trace coefficient.
    Hz=Z.conj().T@H@Z;diag=abs(np.diag(Hz))
    if np.any(diag==0):raise ValueError('singular independent chart; compatible relation retained')
    D=1/np.sqrt(diag);Zd=Z*D[None,:];Hr=Zd.conj().T@H@Zd
    rhs=np.column_stack((Zd.conj().T@f,Zd.conj().T@H@O))
    cond=float(np.linalg.cond(Hr));sol=lu_solve(lu_factor(Hr),rhs)
    force=Zd@sol[:,0];U=O-Zd@sol[:,1:];g=pre['left_source_trace'];u=force+U@g
    residual=H@u-f;conormal=O.conj().T@residual
    A=np.vstack((C,L));lam=np.linalg.solve(A@A.conj().T,-A@residual)
    eq=residual+A.conj().T@lam;tr=A@u-np.r_[np.zeros(len(C)),g]
    reduced_res=Zd.conj().T@residual
    reduced_x=sol[:,0]-sol[:,1:]@g
    reduced_rhs=rhs[:,0]-rhs[:,1:]@g
    backward=float(np.linalg.norm(Hr@reduced_x-reduced_rhs)/
        (np.linalg.norm(Hr)*np.linalg.norm(reduced_x)+np.linalg.norm(reduced_rhs)))
    Riesz=np.linalg.solve(pre['left_trace_Cauchy_Gram'],conormal)
    tail=read(source/'tail_response.npz');tg=a['tail_trace_injection']@u;td=tail['S']@tg-tail['r']
    # Preserves S(s), r(s) and source/port solutions without imposing symmetry.
    S=O.conj().T@H@U;r=O.conj().T@(f-H@force)
    np.savez_compressed(out/'hierarchical_core_solution.npz',solution=u,source_particular=force,
        incoming_trace_solution_map=U,incoming_source_trace=g,original_equation_residual=eq,
        original_trace_residual=tr,reduced_equation_residual=reduced_res,reaction=lam,
        stationary_model_conormal_dual=conormal,stationary_model_conormal_Riesz=Riesz,
        incoming_response_S=S,incoming_affine_r=r,solved_node2_trace=tg,node2_stationary_tail_dual=td,
        independent_chart=Z,scaled_independent_chart=Zd,port_injection=O,field_congruence=D,
        joining=C,incoming_trace_operator=L,reduced_H=Hr,reduced_rhs=rhs,
        node2_Cauchy_pairing=tail['node2_Cauchy_pairing'])
    result=dict(classification='open-port parent-bulk plus temporal minimal-core tail numerical model',
        chart='exact analytic joining elimination: prefix slope, node1 trace, node2 trace; no nullspace threshold',
        reduced_dimension=3*d,reduced_condition_after_congruence=cond,
        graph_numerically_resolved=bool(cond*np.finfo(float).eps<1e-6),
        joining_chart_residual=float(np.linalg.norm(C@Zd)),port_chart_residual=float(np.linalg.norm(L@Zd)),
        source_solution=True,full_owned_source_solution=False,incoming_physical_port_unselected=True,
        equation_absolute_residual=float(np.linalg.norm(eq)),trace_absolute_residual=float(np.linalg.norm(tr)),
        reduced_equation_absolute_residual=float(np.linalg.norm(reduced_res)),
        reduced_backward_residual=backward,conormal_reaction_identity_residual=float(np.linalg.norm(conormal+lam[-d:])),
        stationary_model_conormal_dual_norm=float(np.linalg.norm(conormal)),
        incoming_port_output_contraction=cj(np.vdot(g,conormal)),
        solved_node2_output_contraction=cj(np.vdot(tg,td)),
        unknown_owned_blocks=dict(wall_reset_seam=None,constraint_complex_pullback=None,relative_completion=None),
        source_and_duals_congruently_transformed=True,no_diagonal_regularizer=True,
        tail_cached=True,new_point_evaluations=0,earlier_element_replays=0,
        error_scope='binary64 model diagnostics; no uniform forward/continuum bound; original physical graph and owned seams not promoted',
        physical_a_mu=None,physical_g_mu=None)
    save(out/'result.json',result)
    save(out/'input_hashes.json',{name:dict(path=str(pth),sha256=sha(pth)) for name,pth in
        dict(attachment=source/'partial_system_with_tail_core.npz',tail=source/'tail_response.npz',
             prefix=base/'run_1/prefix_time_element.npz',bridge=base/'assembly_run_1/cut_to_future1_element.npz',
             future=base/'future_run_2/retained_arc_time_element.npz',script=Path(__file__)).items()})
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.source,a.output)
