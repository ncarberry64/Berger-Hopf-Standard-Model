"""Analytic Cauchy/Noether reaction map for the retained N12 boundary rows.

External action data are fixed. The three interface traces, two momenta and
two flux targets are solved outputs. The dynamic flux includes the full
derivative of the action-owned canonical momentum lift.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_key]='1'
import argparse
import json
import math
from pathlib import Path
import time
import numpy as np
from flint import arb,arb_mat,ctx

import solve_n12_gate7_fiber_constrained_center as center
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from checkpoint_n12_gate7_66d_tangent_binding import bound,digest,encoded
from diagnose_n12_gate7_eight_reaction_center import block,identity

A=center.action
ROOT=center.ROOT
BASE=center.BASE/'gate7_coupled_fiber_center_20260927'
OWNER=ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'


def zeros(shape):return np.full(shape,arb(0),dtype=object)


def mat(a):return center.matrix(np.asarray(a,dtype=object))


def arr(a):return center.array(a)


def embed(v,offset):
    out=zeros((98,v.ncols()))
    out[offset:offset+v.nrows()]=arr(v)
    return out


def attachment(q):
    signs=[arb((-1)**j) for j in range(12)]
    v=sum((q[25+j]*signs[j] for j in range(12)),arb(0))
    t=(2*v).tanh();sech2=1-t*t
    B=zeros((2,37));B[0,0]=1
    for j in range(12):B[0,1+j]=(-1)**(j+1);B[0,25+j]=-t*signs[j]
    B[1]=-B[0];B[1,0]+=1
    return mat(B),signs,t,sech2


def attachment_variation(raw,signs,t,sech2,other=None):
    """DB[u], or D2B[x,u], for the existing two-coordinate attachment."""
    slope=np.array([sum((raw[25+j,k]*signs[j] for j in range(12)),arb(0))
                    for k in range(raw.shape[1])],dtype=object)
    out=zeros((2,37,raw.shape[1]))
    if other is None:factor=-2*sech2*slope
    else:
        vx=sum((other[25+j]*signs[j] for j in range(12)),arb(0))
        factor=8*t*sech2*vx*slope
    for j in range(12):out[0,25+j]=factor*signs[j];out[1,25+j]=-out[0,25+j]
    return out


def kkt(H,B,offset):
    indices=range(offset,offset+37)
    C=arb_mat(B.tolist()+block(H,range(74,98),indices).tolist())
    K=arb_mat(63,63)
    for i in range(37):
        for j in range(37):K[i,j]=H[offset+i,offset+j]
        for j in range(26):K[i,37+j]=C[j,i];K[37+j,i]=C[j,i]
    target=arb_mat(63,2);target[37,0]=1;target[38,1]=1
    lift=K.solve(target)
    return K,lift,target


def components(v,offset):
    return embed(block(v,range(37),range(v.ncols())),offset),embed(block(v,range(39,63),range(v.ncols())),74)


def boundary_pair(left,right,dB):
    out=zeros((right.ncols(),dB.shape[2]))
    for k in range(dB.shape[2]):
        derivative=mat(dB[:,:,k])
        value=(block(left,[37,38],[0]).transpose()*derivative*block(right,range(37),range(right.ncols()))
               +block(left,range(37),[0]).transpose()*derivative.transpose()*block(right,[37,38],range(right.ncols())))
        out[:,k]=arr(value).ravel()
    return out


def calculate_node(index,out):
    ctx.prec=512;start=time.monotonic();sources={}
    for p in (Path(__file__),OWNER,BASE/'neighborhood/arrays.npz',BASE/'center/arrays.npz',Path(A.__file__)):
        sources[str(p)]=digest(p)
    geometry=load(BASE/'neighborhood/arrays.npz')
    z=geometry['left_state_domain' if index==13 else 'right_state_domain']
    problem=center.load_problem();weights=problem['w'];state=z[:98]/weights
    U=zeros((98,98))
    for i in range(98):U[i,i]=1/weights[i]
    with center.sparse.use_optimized_mixed(A),center.factored.use_ball_factored_integrand(A,state):
        jets=A._arb_action_jets(state);H=mat(jets.hessian_arb);grad=mat(jets.gradient_arb[:,None])
        def contract(legs):return np.asarray(A._contracted_action(state,legs,jets.dense_maps),dtype=object)
        B,signs,t,sech2=attachment(state[:37]);dB=attachment_variation(U,signs,t,sech2)
        Kq,Lq,tq=kkt(H,B,0);Kv,Lv,tv=kkt(H,B,37)
        inverseq=Kq.inv();inversev=Kv.inv()
        gv=arb_mat(63,1,grad.entries()[37:74]+[arb(0)]*26)
        momentum=Lv.transpose()*gv;eta=Kv.solve(gv)
        # Raw Euler--Dirac time derivative, exactly as the boundary owner.
        velocity=arb_mat(37,1,list(state[37:74]));Hzz=block(H,range(37,98),range(37,98))
        H_zq=block(H,range(37,98),range(37))
        rhs=arb_mat(61,1,grad.entries()[:37]+[arb(0)]*24)-H_zq*velocity
        solved=Hzz.solve(rhs);X=np.r_[np.array(velocity.entries()),np.array(solved.entries())]
        # DX[u] is differentiated before any norm/support.
        eye=zeros((98,98))
        for i in range(98):eye[i,i]=1
        TXU=contract([eye[:, :,None],X[:,None,None],U[:,None,:]])
        dgrad=H*mat(U)
        dx_rhs=arb_mat(block(dgrad,range(37),range(98)).tolist()+[[arb(0)]*98 for _ in range(24)])
        dx_rhs-=H_zq*mat(U[37:74]);dx_rhs-=mat(TXU[37:])
        dX=np.vstack((U[37:74],arr(Hzz.solve(dx_rhs))))
        print(index,'action dynamics differentiated',round(time.monotonic()-start,2),flush=True)
        # K_v' in the one time direction. This is a D3 contraction, not a tensor export.
        HX=contract([eye[:,:,None],eye[:,None,:],X[:,None,None]])
        BX=attachment_variation(X[:,None],signs,t,sech2)[:,:,0]
        Kx=arb_mat(63,63)
        for i in range(37):
            for j in range(37):Kx[i,j]=HX[37+i,37+j]
            for j in range(26):
                v=BX[j,i] if j<2 else HX[74+j-2,37+i]
                Kx[i,37+j]=v;Kx[37+j,i]=v
        Lx=-Kv.solve(Kx*Lv)
        # K_v'[u] L_v, retaining all 98 shared directions in one block.
        lv,lv_m=components(Lv,37)
        legs=np.concatenate((lv+lv_m,lv),axis=1)
        T=contract([eye[:,:,None,None],legs[:,None,:,None],U[:,None,None,:]])
        KL=zeros((63,2,98))
        for k in range(98):
            KL[:37,:,k]=T[37:74,:2,k]
            KL[39:,:,k]=T[74:,2:,k]
            db=mat(dB[:,:,k]);KL[:37,:,k]+=arr(db.transpose()*block(Lv,[37,38],range(2)))
            KL[37:39,:,k]=arr(db*block(Lv,range(37),range(2)))
        Lu=-Kv.solve(mat(KL.reshape(63,196)))
        bu=arb_mat(block(dgrad,range(37,74),range(98)).tolist()+[[arb(0)]*98 for _ in range(26)])
        bx=arb_mat(63,1,(H*mat(X[:,None])).entries()[37:74]+[arb(0)]*26)
        P_u=Lv.transpose()*bu-mat(np.array([(eta.transpose()*mat(KL[:,:,k])).entries() for k in range(98)],dtype=object).T)
        P_x=Lv.transpose()*bx-Lv.transpose()*Kx*eta
        P_direct=zeros((2,98));P_mixed=zeros((2,98))
        def pair_variation(left,right,offset,raw,db,x=None):
            ls,lm=components(left,offset);rs,rm=components(right,offset)
            total=zeros((right.ncols(),raw.shape[1]))
            for aa,bb in ((ls,rs),(lm,rs),(ls,rm)):
                if x is None:legs=[aa[:,0,None,None],bb[:,:,None],raw[:,None,:]]
                else:legs=[aa[:,0,None,None,None],bb[:,:,None,None],x[:,None,None,None],raw[:,None,:,None]]
                value=contract(legs).reshape(total.shape)
                total+=value
            return total+boundary_pair(left,right,db)
        mixed_boundary=attachment_variation(U,signs,t,sech2,other=X)
        Kxu_pair=pair_variation(eta,Lv,37,U,mixed_boundary,x=X)
        Ku_Lx_pair=pair_variation(eta,Lx,37,U,dB)
        for k in range(98):
            L_u=arb_mat([[Lu[i,j*98+k] for j in range(2)] for i in range(63)])
            # Direct derivative independently replays the adjoint formula.
            P_direct[:,k]=arr(Lv.transpose()*block(bu,range(63),[k])+L_u.transpose()*gv).ravel()
            first=(block(Lv,range(37),range(2)).transpose()*mat(TXU[37:74,k,None]))
            first+=L_u.transpose()*bx+Lx.transpose()*block(bu,range(63),[k])
            first-=L_u.transpose()*Kx*eta
            P_mixed[:,k]=arr(first).ravel()-Kxu_pair[:,k]-Ku_Lx_pair[:,k]
        dB_dX=attachment_variation(dX,signs,t,sech2)
        DP_dX=arr(Lv.transpose()*arb_mat(block(H*mat(dX),range(37,74),range(98)).tolist()+[[arb(0)]*98 for _ in range(26)]))
        DP_dX-=pair_variation(eta,Lv,37,dX,dB_dX)
        # Radial flux covector in the same retained boundary convention.
        q=state[:37];m=state[74:];sk=[arb((-1)**(j+1)) for j in range(12)]
        uq=sum((q[1+j]*sk[j] for j in range(12)),arb(0))
        wq=sum((q[13+j]*signs[j] for j in range(12)),arb(0))
        vq=sum((q[25+j]*signs[j] for j in range(12)),arb(0))
        radius=arb(float(A.RADIUS0))*q[0].exp();root2=arb(math.sqrt(2.0))
        aa=radius*(uq+vq).exp()/root2;bb=radius*(uq-vq).exp()/root2;cc=radius*(uq+wq).exp()
        lapse=sum((m[j]*sk[j] for j in range(12)),arb(0)).exp()
        pref=3*lapse*aa**3*bb**3/cc
        radial=zeros((37,1));loggrad=zeros((1,98));loggrad[0,0]=5
        for j in range(12):radial[25+j,0]=2*pref*signs[j];loggrad[0,1+j]=5*sk[j];loggrad[0,13+j]=-signs[j];loggrad[0,74+j]=sk[j]
        radial=mat(radial);drad=radial*(mat(loggrad)*mat(U))
        w=arb_mat((radial-block(grad,range(37),[0])).tolist()+[[arb(0)] for _ in range(26)])
        w_u=arb_mat((drad-block(dgrad,range(37),range(98))).tolist()+[[arb(0)]*98 for _ in range(26)])
        eta_q=Kq.solve(w);Qflux=Lq.transpose()*w
        Q_u=arr(Lq.transpose()*w_u)-pair_variation(eta_q,Lq,0,U,dB)
        trace=zeros((3,37));trace[:,0]=1
        for j in range(12):trace[:,1+j]=sk[j];trace[0,13+j]=signs[j];trace[1,25+j]=signs[j];trace[2,25+j]=-signs[j]
        trace=mat(trace)
        b=arb_mat((trace*mat(q[:,None])).tolist()+momentum.tolist()+(-Qflux-P_x).tolist())
        Db=arb_mat((trace*mat(U[:37])).tolist()+P_u.tolist()+(-mat(Q_u+P_mixed+DP_dX)).tolist())
    data=dict(reactions=b,derivative_action=Db,raw_dynamics=mat(X[:,None]),raw_dynamics_derivative=mat(dX),
        canonical_lift_q=Lq,canonical_lift_v=Lv,momentum_time_derivative=P_x,
        momentum_mixed_derivative=mat(P_mixed),momentum_dynamic_direction_derivative=mat(DP_dX))
    save_arrays(out/'arrays.npz',data)
    report=dict(status='ACTION_DERIVED_SLAVED_INTERFACE_VALUE_AND_FIRST_DERIVATIVE',node=index,
        external_environment_variation=0,independent_environment_inputs=0,
        boundary_equation='B=[Tq-b_trace, P-b_momentum, Lq^T radial + DP[X]-Lq^T grad_q+b_flux]=0',
        reaction_formula='b=[Tq,P,Lq^T(grad_q-radial)-DP[X]]',
        reaction_block='diag(-I_5,+I_2)',reaction_block_rank=7,
        derivative_formula='Db_flux[u]=-D(Lq^T(radial-grad_q))[u]-D2P[X,u]-DP[DX u]',
        action_domain='Frozen certified replacement endpoint state box; 98 weighted action directions; external retained action constants and boundary class fixed.',
        canonical_q_KKT_residual=bound(Kq*Lq-tq),canonical_v_KKT_residual=bound(Kv*Lv-tv),
        canonical_q_inverse_defect=bound(identity(63)-Kq*inverseq),canonical_v_inverse_defect=bound(identity(63)-Kv*inversev),
        dynamics_equation_residual=bound(Hzz*solved-rhs),
        momentum_adjoint_direct_replay=bound(P_u-mat(P_direct)),
        reaction_value_norm=bound(b),reaction_derivative_norm=bound(Db),
        finite_difference_used=False,raw_eigensolve_used=False,
        source_SHA256=sources,arrays_SHA256=digest(out/'arrays.npz'),
        scope='Exact retained child matching rows solved for their seven internal target quantities. No additional exterior generating relation is asserted.',
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report));print(index,report['status'],round(time.monotonic()-start,2),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--node',type=int,choices=(13,14),required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);calculate_node(a.node,a.out)


if __name__=='__main__':main()
