"""First-order 72+flow launch chart and native event response at node 13.

The historical event derivative is not transported across a disjoint center.
Reuses the certified center, constraint/fiber jets and native momentum jet.
Only the new configuration-conormal first derivative is evaluated there.
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from flint import arb, arb_mat, ctx
import derive_n12_gate7_event_conormal_jet as e
from checkpoint_n12_gate7_66d_tangent_binding import amat, bound, digest, encoded, FIXED, PHYSICAL, PARENT, CAUSAL, RESET
from diagnose_n12_gate7_eight_reaction_center import block, identity
from bhsm.interface.complete_child_flux_response import pullback_sector_five

r=e.r; A=r.A; ROOT=r.ROOT; BASE=r.center.BASE
CENTER=BASE/'gate7_coupled_fiber_center_20260927'
CHILD=BASE/'gate7_comoving_interface_20260927/node13'
OLD=BASE/'gate7_66d_checkpoint_20260926/binding'
LAUNCH_OWNER=Path('C:/Users/carbe/Downloads/bhsm_gate7_layerC_launch_to_child_binding.py')


def conormal(state, weights):
    """Outward D(Lq.T radial) at the supplied current state box, in W^-1 columns."""
    U=arb_mat(98,98)
    for i in range(98):U[i,i]=1/weights[i]
    with r.center.sparse.use_optimized_mixed(A),r.center.factored.use_ball_factored_integrand(A,state):
        jets=A._arb_action_jets(state);H=r.mat(jets.hessian_arb)
        B,signs,t,sech=r.attachment(state[:37]);dB=r.attachment_variation(r.arr(U),signs,t,sech)
        K,L,target=r.kkt(H,B,0)
        eye=r.zeros((98,98))
        for i in range(98):eye[i,i]=1
        lq,lm=r.components(L,0);legs=np.concatenate((lq+lm,lq),axis=1)
        third=np.asarray(A._contracted_action(state,[eye[:,:,None,None],legs[:,None,:,None],
            r.arr(U)[:,None,None,:]],jets.dense_maps),dtype=object)
    KL=r.zeros((63,2,98))
    for k in range(98):
        KL[:37,:,k]=third[:37,:2,k];KL[39:,:,k]=third[74:,2:,k]
        db=r.mat(dB[:,:,k])
        KL[:37,:,k]+=r.arr(db.transpose()*block(L,[37,38],range(2)))
        KL[37:39,:,k]=r.arr(db*block(L,range(37),range(2)))
    DL=-K.solve(r.mat(KL.reshape(63,196)))
    sk=[arb((-1)**(j+1)) for j in range(12)]
    uq=sum((state[1+j]*sk[j] for j in range(12)),arb(0))
    wq=sum((state[13+j]*signs[j] for j in range(12)),arb(0))
    vq=sum((state[25+j]*signs[j] for j in range(12)),arb(0))
    lapse=sum((state[74+j]*sk[j] for j in range(12)),arb(0)).exp()
    radius=arb(float(A.RADIUS0))*state[0].exp();rt=arb(math.sqrt(2.0))
    aa=radius*(uq+vq).exp()/rt;bb=radius*(uq-vq).exp()/rt;cc=radius*(uq+wq).exp()
    pref=3*lapse*aa**3*bb**3/cc
    raw=arb_mat(63,1);log=arb_mat(1,98);log[0,0]=5
    for j in range(12):
        raw[25+j,0]=2*pref*signs[j];log[0,1+j]=5*sk[j]
        log[0,13+j]=-signs[j];log[0,74+j]=sk[j]
    draw=raw*log*U;direct=L.transpose()*draw;adjoint=L.transpose()*draw;eta=K.solve(raw)
    for k in range(98):
        dl=arb_mat([[DL[i,j*98+k] for j in range(2)] for i in range(63)])
        dx=dl.transpose()*raw;corr=eta.transpose()*r.mat(KL[:,:,k])
        for j in range(2):direct[j,k]+=dx[j,0];adjoint[j,k]-=corr[0,j]
    return dict(value=L.transpose()*raw,jet=direct,lift=L,
        replay=direct-adjoint,inverse_defect=identity(63)-K*K.inv(),
        lift_replay=K*L-target,dl_replay=K*DL+r.mat(KL.reshape(63,196)))


def calculate(out):
    ctx.prec=512
    paths=[ROOT/FIXED,ROOT/PHYSICAL,ROOT/PARENT,ROOT/CAUSAL,ROOT/RESET,
        OLD/'arrays.npz',OLD/'report.json',CENTER/'neighborhood/arrays.npz',
        CENTER/'neighborhood/report.json',CENTER/'uniform_inputs/left.npz',
        CENTER/'uniform_inputs/report.json',CHILD/'arrays.npz',CHILD/'report.json',
        e.BASE/'arrays.npz',LAUNCH_OWNER,Path(__file__),Path(A.__file__),Path(r.__file__)]
    inputs={str(p):digest(p) for p in paths}
    cert=json.loads((CENTER/'uniform_inputs/report.json').read_bytes())
    child_report=json.loads((CHILD/'report.json').read_bytes())
    if cert['status']!='LOCAL_COUPLED_CENTER_NEIGHBORHOOD_CERTIFIED':raise ValueError('current center not certified')
    if digest(CENTER/'uniform_inputs/left.npz')!=cert['local_derivative_SHA256']['left']:raise ValueError('left jet changed')
    if digest(CHILD/'arrays.npz')!=child_report['arrays_SHA256']:raise ValueError('native first five changed')
    if digest(CENTER/'neighborhood/arrays.npz') not in child_report['source_SHA256'].values():raise ValueError('child jet center mismatch')
    geom=r.load(CENTER/'neighborhood/arrays.npz');local=r.load(CENTER/'uniform_inputs/left.npz')
    child=r.load(CHILD/'arrays.npz');parent=r.load(e.BASE/'arrays.npz')
    with np.load(ROOT/FIXED) as z:
        weights=np.array([arb(float(x)) for x in z['state_weights']],dtype=object)
        old13=amat(z['projected_states'][13][:,None]);flow_old=z['exact_endpoint_augmented_rates'][13]
    with np.load(ROOT/PARENT) as z:basis_center=amat(z['projected_states'][13][:,None])
    with np.load(ROOT/PHYSICAL) as z:T73=z['endpoint_physical_tangent_action'][13];T0=z['endpoint_physical_tangent_action'][0]
    with np.load(ROOT/RESET) as z:seed=z['projected_C2_parameter_lift']
    family=np.vstack((np.linalg.lstsq(T0,seed,rcond=None)[0],np.zeros((1,72))))
    with np.load(ROOT/CAUSAL) as z:
        for i in range(13):family=z['causal_maps_center'][i]@family
    qflow=np.linalg.lstsq(T73,flow_old[:98],rcond=None)[0]
    launch_state=np.column_stack((family[:73],qflow))
    with np.load(OLD/'arrays.npz') as z:
        if not np.array_equal(launch_state,z['node_013_launch_state']):raise ValueError('launch reconstruction differs from frozen checkpoint')
    initial=amat(T73)*amat(launch_state)
    current=r.mat(geom['left_state_domain'][:98,None]);W=arb_mat(98,98)
    for i in range(98):W[i,i]=weights[i]
    old_event=W*r.mat(parent['parent_center'][:,None])
    delta=old_event-current
    if not any(not v.contains(0) for v in delta.entries()):raise ValueError('unexpected coincident centers; review binding branch')
    # Fixed-normal implicit chart, using the existing center's normal coordinates.
    # This is a chart change, not a physical boundary condition on seven reactions.
    DC=r.mat(local['DC']);N=r.mat(geom['left_phase_chart'][:98,:25]);C=DC*N
    project=lambda V:V-N*C.solve(DC*V)
    first72=project(block(initial,range(98),range(72)))
    flow=project(r.mat(local['rate'][:98,None]))
    T=arb_mat([first72.tolist()[i]+[flow[i,0]] for i in range(98)])
    g=r.mat(local['covector'][None,:]);ds=g*T
    # Fixed midpoint left inverse avoids squaring interval dependencies in
    # the ill-conditioned launch Gram inverse. ||I-R0 T||<1 certifies rank.
    Tmid=arb_mat(98,73,[v.mid() for v in T.entries()])
    R0=(Tmid.transpose()*Tmid).solve(Tmid.transpose())
    rankdef=identity(73)-R0*T
    if bound(rankdef)['approximate_upper']>=1:raise ArithmeticError('launch rank not certified')
    print('launch reconstructed, centers disjoint, current chart rank certified',flush=True)
    flux=conormal(geom['left_state_domain'][:98]/weights,weights)
    native5=block(r.mat(child['derivative_action']),range(5),range(98))
    native7=arb_mat(native5.tolist()+flux['jet'].tolist())
    # Native retained owner has only q,v,m arguments and fixed material section.
    # Its direct seam geometry and moving canonical lift are already in J.
    explicit_native_shape=arb_mat(7,73)
    response=native7*T+explicit_native_shape
    sectors={n:arb_mat(2,98) for n in e.s.NAMES}
    sectors['adm_kinetic']=block(native5,[3,4],range(98))
    five,pieces=pullback_sector_five(block(native5,range(3),range(98)),sectors,T,arb_mat(5,73))
    data=dict(historical_launch_state=amat(launch_state),historical_launch_action=initial,
        launch_action=T,launch_descriptor=ds,launch_augmented=arb_mat(T.tolist()+ds.tolist()),
        constraint_derivative=DC,constraint_normal=N,constraint_normal_inverse=C.inv(),
        chart_left_inverse_proposal=R0,corrected_state_action=current,historical_event_state_action=old_event,
        center_difference_action=delta,native_event_7x98=native7,response_7x73=response,
        native_explicit_shape_7x73=explicit_native_shape,
        response_trace=block(response,range(3),range(73)),
        response_momentum=block(response,[3,4],range(73)),response_flux=block(response,[5,6],range(73)),
        flux_replay=flux['replay'],chart_constraint_replay=DC*T,
        chart_rank_inverse_replay=rankdef,sector_five_replay=five-block(response,range(5),range(73)))
    for n,piece in pieces.items():data[n+'_pulled_momentum']=piece
    r.save_arrays(out/'arrays.npz',data)
    report=dict(status='RECENTERED_LAUNCH_CHART_AND_NATIVE_SEVEN_ROW_COMPOSITION',
        node=13,historical_event_center_agrees=False,
        historical_event_to_current=bound(delta),old_node13_to_current=bound(W*old13-current),
        physical_basis_center_to_current=bound(W*basis_center-current),
        disjoint_coordinate_lower=max(float(abs(v).lower()) for v in delta.entries()),
        launch_reconstruction_byte_equal_to_frozen=True,
        original_launch_condition=float(np.linalg.cond(launch_state)),
        chart_transport='T72_new=(I-N(DC N)^-1 DC) T72_old; last column is the similarly projected current certified flow',
        chart_parameter_order='72 inherited reset-family labels, then one current forward-flow phase; NOT 66+7',
        descriptor_relation='ds=Dlambda_event*T_new in physical units; independent descriptor input absent',
        chart_rank_certified=73,chart_rank_inverse_defect=bound(rankdef),
        chart_constraint_replay=bound(DC*T),chart_change=bound(T-initial),
        current_flow_normal_correction=bound(flow-r.mat(local['rate'][:98,None])),
        first_five_reused_at_identical_certified_domain=True,
        conormal_replay={k:bound(flux[k]) for k in ('replay','inverse_defect','lift_replay','dl_replay')},
        conormal_lift_vs_frozen_child=bound(flux['lift']-r.mat(child['canonical_lift_q'])),
        response_shape=[7,73],row_order=['trace1','trace2','trace3','momentum1','momentum2','event_conormal1','event_conormal2'],
        response_norm=bound(response),sector_sum_replay=bound(five-block(response,range(5),range(73))),
        native_direct_shape_term='Zero: native owner has only retained q,v,m arguments at fixed material chi=pi/4; DLq and state geometry included before composition.',
        general_environment_frame_shape_jet_inferred=False,
        material_environment_identity_proved=False,
        scope='Certified local constraint/fiber chart and native event-functional composition at the corrected node13 box. Recentring does not prove this is a fixed external environment material solution or transport the old parent point to node13.',
        historical_72_family_uniform_transport_proved=False,
        boundary_reactions_solved=False,Layer_C_rebound=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        frozen_tolerances_changed=False,source_SHA256=inputs,arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','historical_event_to_current','chart_rank_inverse_defect','chart_constraint_replay','conormal_replay')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);calculate(args.out)
