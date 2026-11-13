"""Consume the cached tail component in an open-port parent-bulk model solve.

Unknown owned seams/constraints/completion are not set to zero. This solves
only the explicitly stored known parent-bulk component and leaves its incoming
port as an affine argument. It is not a full owned exterior source solution.
"""
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
    if out.exists():raise FileExistsError('new output required')
    out.mkdir(parents=True)
    a=read(source/'partial_system_with_tail_core.npz')
    prefix=root/'artifacts/muon_prefix_time_element_20261004/run_1/prefix_time_element.npz'
    p=read(prefix);H=a['H'];f=a['rhs'];C=a['trace_continuity'];n=len(H);dim=24
    L=np.zeros((dim,n),complex);L[:,:48]=p['hierarchical_to_endpoint_coefficients'][:dim]
    A=np.vstack((C,L));m=len(A)
    # A congruence, not a diagonal penalty. All forms, loads, dual reactions
    # and trace rows are transformed together; original coordinates persist.
    diag=abs(np.diag(H))
    if np.any(diag==0):raise ValueError('zero diagonal chart; retain full relation instead of regularizing')
    D=1/np.sqrt(diag);AD=A*D[None,:];R=1/np.linalg.norm(AD,axis=1)
    Ah=R[:,None]*AD;Hh=D[:,None]*H*D[None,:]
    KKT=np.block([[Hh,Ah.conj().T],[Ah,np.zeros((m,m),complex)]])
    rhs=np.zeros((n+m,dim+1),complex);rhs[:n,0]=D*f
    rhs[n+len(C):,1:]=np.diag(R[len(C):])
    condition=float(np.linalg.cond(KKT))
    np.savez_compressed(out/'compatible_KKT_relation.npz',original_H=H,original_rhs=f,
        original_trace_operator=A,incoming_port=L,joining=C,field_congruence=D,
        reaction_congruence=R,scaled_KKT=KKT,scaled_rhs=rhs)
    factor=lu_factor(KKT);x=lu_solve(factor,rhs)
    U=D[:,None]*x[:n];reactions=R[:,None]*x[n:]
    g=p['left_source_trace'];u=U[:,0]+U[:,1:]@g;lam=reactions[:,0]+reactions[:,1:]@g
    eq=H@u+A.conj().T@lam-f;tr=A@u-np.r_[np.zeros(len(C)),g]
    scaled=np.r_[u/D,lam/R];srhs=rhs[:,0]+rhs[:,1:]@g
    scaled_res=KKT@scaled-srhs
    backward=float(np.linalg.norm(scaled_res)/(np.linalg.norm(KKT)*np.linalg.norm(scaled)+np.linalg.norm(srhs)))
    # Natural outward weak-model traction is minus the boundary multiplier.
    conormal=-lam[len(C):];Mtrace=p['left_trace_Cauchy_Gram']
    conormal_Riesz=np.linalg.solve(Mtrace,conormal)
    tail_trace=a['tail_trace_injection']@u
    tail=read(source/'tail_response.npz')
    tail_dual=tail['S']@tail_trace-tail['r']
    np.savez_compressed(out/'coupled_core_source_solution.npz',solution=u,source_particular=U[:,0],
        incoming_trace_solution_map=U[:,1:],reaction=lam,source_reaction=reactions[:,0],
        incoming_trace_reaction_map=reactions[:,1:],incoming_source_trace=g,
        equation_residual=eq,trace_residual=tr,stationary_model_conormal_dual=conormal,
        stationary_model_conormal_Riesz=conormal_Riesz,incoming_Cauchy_pairing=Mtrace,
        solved_node2_trace=tail_trace,node2_stationary_tail_dual=tail_dual,
        left_source_trace=L@u,joining_dual_reactions=lam[:len(C)])
    result=dict(classification='open-port parent-bulk plus temporal minimal-core tail numerical model',
        model_solution=True,full_owned_exterior_source_solution=False,incoming_port_selected_physically=False,
        source_application='u(g)=u_source+U_trace g evaluated at saved ORIGINAL source trace; incoming physical port remains an argument',
        KKT_condition_after_congruence=condition,equation_absolute_residual=float(np.linalg.norm(eq)),
        trace_absolute_residual=float(np.linalg.norm(tr)),equation_scaled_backward_residual=backward,
        graph_numerically_resolved=bool(condition*np.finfo(float).eps<1e-6),
        stationary_model_conormal_dual_norm=float(np.linalg.norm(conormal)),
        stationary_model_conormal_Riesz_norm=float(np.linalg.norm(conormal_Riesz)),
        incoming_port_output_contraction=cj(np.vdot(g,conormal)),
        solved_node2_output_contraction=cj(np.vdot(tail_trace,tail_dual)),
        known_component_source_pairing=cj(np.vdot(u,f)),
        unknown_owned_blocks=dict(wall_reset_seam=None,constraint_complex_pullback=None,relative_completion=None),
        no_diagonal_regularizer=True,source_load_reused=True,earlier_element_replays=0,
        scope='stationary model residuals only; no continuum or Pauli error bound; no new terminal/incoming physical boundary law',
        physical_a_mu=None,physical_g_mu=None)
    save(out/'result.json',result)
    save(out/'input_hashes.json',{name:dict(path=str(pth),sha256=sha(pth)) for name,pth in
        dict(attachment=source/'partial_system_with_tail_core.npz',tail=source/'tail_response.npz',prefix=prefix,script=Path(__file__)).items()})
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.source,a.output)
