"""Fixed-exterior weak reaction feedback, affine in the unbound exterior datum.

No exterior datum is fitted to the child center. The two coefficient columns
are a representation of a held-fixed datum, not two physical input directions.
"""
import argparse
import ast
import json
from pathlib import Path
import numpy as np
from flint import arb, arb_mat, ctx
import derive_n12_gate7_slaved_interface as r
from checkpoint_n12_gate7_66d_tangent_binding import digest, encoded, bound
from diagnose_n12_gate7_eight_reaction_center import block, identity


def calculate(node, out):
    ctx.prec=512
    geometry=r.load(r.BASE/'neighborhood/arrays.npz')
    z=geometry['left_state_domain' if node==13 else 'right_state_domain']
    weights=r.center.load_problem()['w'];Y=z[:98]/weights
    U=r.zeros((98,98))
    for j in range(98):U[j,j]=1/weights[j]
    with r.center.sparse.use_optimized_mixed(r.A),r.center.factored.use_ball_factored_integrand(r.A,Y):
        jets=r.A._arb_action_jets(Y);H=r.mat(jets.hessian_arb);g=r.mat(jets.gradient_arb[:,None])
        B,signs,t,sech=r.attachment(Y[:37])
        dB=r.attachment_variation(U,signs,t,sech)
        v=r.mat(Y[37:74,None]);Hzz=block(H,range(37,98),range(37,98))
        H_zq=block(H,range(37,98),range(37))
        sk=[arb((-1)**(j+1)) for j in range(12)]
        uq=sum((Y[1+j]*sk[j] for j in range(12)),arb(0))
        wq=sum((Y[13+j]*signs[j] for j in range(12)),arb(0))
        mq=sum((Y[74+j]*sk[j] for j in range(12)),arb(0))
        # Same binary64 constants as the retained radial owner.
        import math
        radius=arb(float(r.A.RADIUS0))*Y[0].exp();root2=arb(math.sqrt(2.0))
        aa=radius*(uq+sum((Y[25+j]*signs[j] for j in range(12)),arb(0))).exp()/root2
        bb=radius*(uq-sum((Y[25+j]*signs[j] for j in range(12)),arb(0))).exp()/root2
        cc=radius*(uq+wq).exp();pref=3*mq.exp()*aa**3*bb**3/cc
        radial=r.zeros((37,1));lg=r.zeros((1,98));lg[0,0]=5
        for j in range(12):
            radial[25+j,0]=2*pref*signs[j]
            lg[0,1+j]=5*sk[j];lg[0,13+j]=-signs[j];lg[0,74+j]=sk[j]
        radial=r.mat(radial);drad=radial*(r.mat(lg)*r.mat(U))
        # Hzz nu - B^T rho_child = rhs-radial, rho_child=-rho_e.
        rhs=arb_mat((block(g,range(37),[0])-radial).tolist()+[[arb(0)]]*24)-H_zq*v
        inputB=arb_mat(B.transpose().tolist()+[[arb(0)]*2]*24)
        affine_rhs=arb_mat([[rhs[i,0]]+[-inputB[i,j] for j in range(2)] for i in range(61)])
        nu=Hzz.solve(affine_rhs)
        E=r.zeros((98,61));E[37:]=np.eye(61,dtype=int)
        nu_full=r.zeros((98,3));nu_full[37:]=r.arr(nu)
        # Signed D(Hzz)[u] nu contracted without a full D3 tensor export.
        third=np.asarray(r.A._contracted_action(Y,[E[:,:,None,None],nu_full[:,None,:,None],U[:,None,None,:]],jets.dense_maps),dtype=object)
        Xq=r.zeros((98,1));Xq[:37]=Y[37:74,None]
        qthird=np.asarray(r.A._contracted_action(Y,[E[:,:,None],Xq[:,None,:],U[:,None,:]],jets.dense_maps),dtype=object)
        dg=H*r.mat(U)
        rhs_u=arb_mat((block(dg,range(37),range(98))-drad).tolist()+[[arb(0)]*98]*24)-H_zq*r.mat(U[37:74])-r.mat(qthird)
        dnu=r.zeros((61,3,98))
        for j in range(3):
            f=rhs_u if j==0 else arb_mat((-r.mat(dB[j-1,:,:])).tolist()+[[arb(0)]*98]*24)
            dnu[:,j,:]=r.arr(Hzz.solve(f-r.mat(third[:,j,:])))
        vv=sum((Y[37+25+j]*signs[j] for j in range(12)),arb(0))
        curvature=arb_mat([[-2*sech*vv*vv],[2*sech*vv*vv]])
        acc=B*block(nu,range(37),range(3))
        for i in range(2):acc[i,0]+=curvature[i,0]
        dacc=r.zeros((2,3,98))
        for k in range(98):
            du=sum((U[25+j,k]*signs[j] for j in range(12)),arb(0))
            dv=sum((U[37+25+j,k]*signs[j] for j in range(12)),arb(0))
            dc=8*t*sech*du*vv*vv-4*sech*vv*dv
            x=r.mat(dB[:,:,k])*block(nu,range(37),range(3))+B*r.mat(dnu[:37,:,k])
            x[0,0]+=dc;x[1,0]-=dc;dacc[:,:,k]=r.arr(x)
    K=arb_mat(63,63)
    for i in range(61):
        for j in range(61):K[i,j]=Hzz[i,j]
        for j in range(2):K[i,61+j]=-inputB[i,j];K[61+j,i]=inputB[i,j]
    Eacc=arb_mat(63,2);Eacc[61,0]=1;Eacc[62,1]=1
    compliance=block(K.solve(Eacc),[61,62],range(2))
    solved=arb_mat(nu.tolist()+[[arb(0),arb(-1),arb(0)],[arb(0),arb(0),arb(-1)]])
    replay_rhs=arb_mat([[rhs[i,0],arb(0),arb(0)] for i in range(61)]+(acc-arb_mat([[curvature[i,0],arb(0),arb(0)] for i in range(2)])).tolist())
    r.save_arrays(out/'arrays.npz',dict(weak_bordered_operator=K,weak_compliance=compliance,
        rate_acceleration_affine=nu,rate_acceleration_derivative_affine=dnu,
        attachment_acceleration_affine=acc,attachment_acceleration_derivative_affine=dacc,
        weak_border_replay=K*solved-replay_rhs))
    owner=r.OWNER.read_text(encoding='utf-8');lines=owner.splitlines()
    names={'_child_history_boundary_reaction_solve','event_child_two_sided_reaction_match_audit'}
    provenance={f.name:dict(start=f.lineno,end=f.end_lineno,text='\n'.join(lines[f.lineno-1:f.end_lineno])) for f in ast.parse(owner).body if isinstance(f,ast.FunctionDef) and f.name in names}
    report=dict(status='FIXED_EXTERIOR_WEAK_FEEDBACK_DERIVED_CONDITIONALLY',node=node,
        fixed_external_variation=0,independent_environment_inputs=0,
        affine_columns=['constant','held_fixed_rho_e_1_coefficient','held_fixed_rho_e_2_coefficient'],
        owner_equation='Hzz nu - B^T rho_child = [gq-radial;0]-Hzq*v; rho_child=-rho_e; attachment_ddot=B*nu_q+curvature',
        derivative_equation='Hzz Dnu[u]=D(rhs-radial)[u]-DB[u]^T rho_e-DHzz[u]nu; Drho_e=0',
        environment_value_bound_to_gate7=False,complete_66D_tangent_bound=False,
        missing_binding='The fixed-environment weak reaction functional and its evaluation along the moving interface at interval 13, in the same attachment frame. Fixed e does not by itself imply fixed sampled conormal rho_e.',
        weak_bordered_inverse_defect=bound(K*K.inv()-identity(63)),
        weak_compliance_inverse_defect=bound(compliance*compliance.inv()-identity(2)),
        affine_owner_replay=bound(K*solved-replay_rhs),boundary_sources=provenance,
        source_SHA256={str(p):digest(p) for p in (Path(__file__),Path(r.__file__),r.OWNER,r.BASE/'neighborhood/arrays.npz',Path(r.A.__file__))},
        arrays_SHA256=digest(out/'arrays.npz'),Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report));print(report['status'],report['affine_owner_replay']['approximate_upper'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--node',type=int,choices=(13,14),default=13);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);calculate(a.node,a.out)
