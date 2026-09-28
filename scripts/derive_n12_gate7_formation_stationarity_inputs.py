"""Current terminal-reset derivatives and local material values, not a history saddle.

Evaluate only the two saved candidate points. No connection/prefix is rerun.
The scalar-history stationarity covector is deliberately not replaced by
the local Lagrangian gradient or by seven output coordinates.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_slaved_interface as r
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,bound,amat
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from diagnose_n12_gate7_eight_reaction_center import block,identity
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal
from bhsm.interface.physical_hs_value import verified_eigenline
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bind_n12_gate7_geometric_material_port import radial_from_current_state,source_functions
from audit_n12_finite_terminal_directed_center import _normalization_coordinates
from bhsm.interface.aether_full_reset_action_jacobian import _symmetric_power
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import _attachment_jacobian_at_order

BASE=ROOT/'artifacts/flagship_integration'
INPUT=BASE/'gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz'


def point(raw_float,weights,reference,index):
    state=np.array([arb(float(v)) for v in raw_float],dtype=object)
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    U=r.zeros((98,98))
    for i in range(98):U[i,i]=1/w[i]
    checks=[];selected={};original=r.A._eigenline
    def proposal(h,mid,ref):return indexed_proposal(h[37:,37:],index,ref)
    r.A._eigenline=recentered_eigenline(proposal)
    try:
        with r.center.sparse.use_optimized_mixed(r.A),r.center.factored.use_ball_factored_integrand(r.A,state):
            with verified_eigenline(r.A,checks,expected_index=index,normalize_proposal_center=True):
                verified=r.A._eigenline
                def retain(*args):
                    result=verified(*args);selected['psi']=result[0];selected['lambda']=result[1];return result
                r.A._eigenline=retain
                try:rate=r.A._rate_enclosure(state,arb(0),weights,reference,None)
                finally:r.A._eigenline=verified
            jets=rate.action_jets;H=r.mat(jets.hessian_arb);g=r.mat(jets.gradient_arb[:,None])
            value=r.center.action_value(state)
            velocity=arb_mat(37,1,list(state[37:74]))
            energy=(velocity.transpose()*block(g,range(37,74),[0]))[0,0]-value
            constraints=np.r_[jets.gradient_arb[74:]/w[74:],energy]
            DC=block(H*r.mat(U),range(74,98),range(98))
            for i in range(24):
                for j in range(98):DC[i,j]/=w[74+i]
            energy_row=velocity.transpose()*block(H,range(37,74),range(98))
            for j in list(range(37))+list(range(74,98)):energy_row[0,j]-=g[j,0]
            energy_row=energy_row*r.mat(U)
            DC=arb_mat(DC.tolist()+energy_row.tolist())
            B,signs,t,sech=r.attachment(state[:37]);dB=r.attachment_variation(U,signs,t,sech)
            K,L,target=r.kkt(H,B,37)
            gv=arb_mat(63,1,g.entries()[37:74]+[arb(0)]*26)
            eta=K.solve(gv);momentum=L.transpose()*gv
            Pj=L.transpose()*arb_mat(block(H*r.mat(U),range(37,74),range(98)).tolist()+[[arb(0)]*98]*26)
            ls,lm=r.components(eta,37);rs,rm=r.components(L,37)
            for a,b in ((ls,rs),(lm,rs),(ls,rm)):
                term=r.A._contracted_action(state,[a[:,0,None,None],b[:,:,None],U[:,None,:]],jets.dense_maps)
                Pj-=r.mat(np.asarray(term,dtype=object).reshape(2,98))
            Pj-=r.mat(r.boundary_pair(eta,L,dB))
            psi=np.r_[np.full(37,arb(0),dtype=object),selected['psi']]
            slope=r.A._contracted_action(state,[psi[:,None],psi[:,None],U],jets.dense_maps)
            slope=r.mat(np.asarray(slope,dtype=object).reshape(1,98))
            Kq,Lq,tq=r.kkt(H,B,0)
            force=block(Lq,range(37),range(2)).transpose()*block(g,range(37),[0])
            conormal=block(Lq,range(37),range(2)).transpose()*radial_from_current_state(state)
    finally:r.A._eigenline=original
    trace=amat(source_functions()[0](12));q=arb_mat(37,1,list(state[:37]))
    v=sum((state[25+j]*(-1)**j for j in range(12)),arb(0))
    u=sum((state[1+j]*(-1)**(j+1) for j in range(12)),arb(0))
    attachment=-u+(2*v).cosh().log()/2
    geometry=arb_mat((trace*q).tolist()+[[attachment]])
    GJ=arb_mat((trace*r.mat(U[:37])).tolist()+(block(B,[1],range(37))*r.mat(U[:37])).tolist())
    arc_momentum=Pj*arb_mat(98,1,list(rate.value[:98]))
    return dict(constraints=arb_mat(25,1,list(constraints)),constraint_J=DC,
        geometry=geometry,geometry_J=GJ,momentum=momentum,momentum_J=Pj,
        eigenvalue=arb_mat([[selected['lambda']]]),eigenvalue_J=slope,
        force=force,conormal=conormal,momentum_arc_derivative=arc_momentum,
        rate=arb_mat(99,1,list(rate.value)),
        proof=dict(eigenpair=checks[0],canonical_velocity_lift_replay=bound(K*L-target),
            canonical_configuration_lift_replay=bound(Kq*Lq-tq),
            canonical_inverse_defect=bound(identity(63)-K*K.inv())))


def rank_record(J):
    mid=r.center.mid(r.arr(J));norms=np.linalg.norm(mid,axis=1)
    scale=amat(np.diag(1/norms));M=scale*J
    right=M.transpose()*(M*M.transpose()).inv()
    defect=bound(M*right-identity(M.nrows()))
    singular=np.linalg.svd(r.center.mid(r.arr(M)),compute_uv=False)
    if defect['approximate_upper']>=1:raise ArithmeticError('row-rank replay failed')
    projector=identity(J.ncols())-right*M
    return dict(row_rank=J.nrows(),nullity=J.ncols()-J.nrows(),
        row_scaled_condition_diagnostic=float(singular[0]/singular[-1]),
        raw_condition_diagnostic=float(np.linalg.cond(mid)),
        right_inverse_defect=defect,annihilator_replay=bound(M*projector)),projector


def calculate(out):
    ctx.prec=512
    record=json.loads(INPUT.with_name('report.json').read_bytes())
    if digest(INPUT)!=record['candidate_SHA256']:raise ValueError('candidate changed')
    with np.load(INPUT) as z:state=z['joint_state_raw'];weights=z['state_weights'];ref=z['branch_reference']
    data={}
    for name,offset,index in [('C2',0,24),('E1',98,23)]:
        print('Evaluating new stationary-input point',name,flush=True)
        data[name]=point(state[offset:offset+98],weights,ref,index)
        print('Current constraints, momentum and selected-descriptor first jets ready',name,flush=True)
    C,E=data['C2'],data['E1']
    normq=_normalization_coordinates();trace=source_functions()[0](12)
    attach=_attachment_jacobian_at_order(12,normq)
    geom=np.vstack((trace,attach[1]));N=amat(_symmetric_power((geom/weights[:37])@(geom/weights[:37]).T,-.5))
    P=amat(_symmetric_power(attach@attach.T,.5))
    ordered=json.loads((ROOT/'artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json').read_bytes())['ordered_scale']
    with np.load(BASE/'BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz') as z:incoming_scale=float(z['child_gradient_scale'])
    zero=arb_mat(25,98)
    pair=lambda a,b:arb_mat([x+y for x,y in zip(a.tolist(),b.tolist())])
    blocks=[pair(C['constraint_J'],zero),pair(C['eigenvalue_J']/arb(float(ordered)),arb_mat(1,98)),
        pair(-N*C['geometry_J'],N*E['geometry_J']),pair(zero,E['constraint_J']),
        pair(-P*C['momentum_J'],P*E['momentum_J']),pair(arb_mat(1,98),E['eigenvalue_J']/arb(incoming_scale))]
    J=arb_mat([row for b in blocks for row in b.tolist()])
    residual=arb_mat(C['constraints'].tolist()+(C['eigenvalue']/arb(float(ordered))).tolist()
        +(N*(E['geometry']-C['geometry'])).tolist()+E['constraints'].tolist()
        +(P*(E['momentum']-C['momentum'])).tolist()+(E['eigenvalue']/arb(incoming_scale)).tolist())
    incoming=block(J,range(26,58),range(98,196))
    ranks,projector=rank_record(incoming);joint_rank,_=rank_record(J)
    _,_,vh=np.linalg.svd(r.center.mid(r.arr(incoming)),full_matrices=True)
    null_basis=vh[32:].T
    arrays=dict(terminal_reset_J=J,terminal_reset_residual=residual,incoming_constraint_J=incoming,
        incoming_kernel_projector=projector,incoming_kernel_basis_numerical=amat(null_basis))
    for name,d in data.items():
        arrays.update({name+'_'+k:v for k,v in d.items() if k!='proof'})
    out=Path(out);out.mkdir(parents=True,exist_ok=False);save_arrays(out/'arrays.npz',arrays)
    paths=[Path(__file__),INPUT,INPUT.with_name('report.json'),Path(r.__file__),Path(r.A.__file__),
        ROOT/'src/bhsm/interface/indexed_eigenpair_proposal.py',
        ROOT/'src/bhsm/interface/aether_full_reset_action_jacobian.py',
        BASE/'BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json',
        BASE/'BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json']
    report=dict(status='CURRENT_RESET_COMPATIBILITY_AND_LOCAL_MATERIAL_STATIONARITY_INPUTS',
        scope='Pointwise current numerical candidate; not a stationary history or root certificate',
        residual_groups={name:bound(block(residual,rows,[0])) for name,rows in {
            'outgoing_constraints':range(25),'outgoing_descriptor':[25],
            'geometry':range(26,30),'incoming_constraints':range(30,55),
            'momentum_matching':range(55,57),'incoming_descriptor':[57]}.items()},
        full_reset_residual=bound(residual),incoming_rank=ranks,full_reset_rank=joint_rank,
        local_values={name:{k:bound(d[k]) for k in ('momentum','force','conormal','momentum_arc_derivative')}
            for name,d in data.items()},
        point_proofs={name:d['proof'] for name,d in data.items()},
        full_action_stationarity_residual=None,full_dynamic_flux_balance_residual=None,
        full_stationarity_rank=None,formation_history_certified=False,formation_73_jet_certified=False,
        missing_current_action_object='Reduced incoming formation/contact stationarity covector and its normal/launch derivative on the current seed-invisible reset directions',
        null_classification='66 incoming reset-compatible directions; not classified as gauge, time, or stationary physical moduli without the current history action',
        no_arbitrary_kernel_selector=True,independent_environment_inputs=0,
        no_frozen_connection_or_C2_producer_rerun=True,
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in paths},arrays_SHA256=digest(out/'arrays.npz'),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('full_reset_residual','incoming_rank','full_reset_rank')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();calculate(a.out)
