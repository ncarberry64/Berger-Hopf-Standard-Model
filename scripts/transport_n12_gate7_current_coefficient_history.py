"""New current-centered finite proof-core coefficient history and first jet.

Only the relative mesh weights are reused. No historical duration, coefficient
enclosure or interval action is asserted to be a current-center certificate.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,FIXED,bound
from derive_n12_gate7_current_spectral_coefficients import interval,CORE,LAUNCH
from bhsm.interface.arb_current_history_transport import flow_certificate,flow_at,flow_span,proper_clock
from bhsm.interface.arb_weyl_first_pullback import first_pullback
from bhsm.interface.aether_forward_boundary_radius import RADIUS0

BASE=ROOT/'artifacts/flagship_integration'
PACKET=BASE/'gate7_current_history_20260927'


def radius_jet(state, J, weights):
    y=[state[i]/weights[i] for i in range(98)]
    v=sum(((-1)**j*y[25+j] for j in range(12)),arb(0));t=(2*v).tanh()
    x=(arb(float(RADIUS0))/2).log()+y[0]+sum(((-1)**(j+1)*y[1+j] for j in range(12)),arb(0))-(2*v).cosh().log()/2
    g=arb_mat(1,99);g[0,0]=1/weights[0]
    for j in range(12):
        g[0,1+j]=(-1)**(j+1)/weights[1+j]
        g[0,25+j]=-((-1)**j)*t/weights[25+j]
    return x,g*J


def calculate(out, box):
    ctx.prec=512
    metadata=json.loads((box/'report.json').read_bytes())
    if metadata['status']!='NEW_CURRENT_HISTORY_FLOW_BOX_EVALUATED' or digest(box/'arrays.npz')!=metadata['arrays_SHA256']:
        raise ValueError('verified current flow box required')
    a=load(box/'arrays.npz');launch=load(LAUNCH/'arrays.npz')
    with np.load(ROOT/FIXED) as z:w=[arb(float(v)) for v in z['state_weights']]
    with np.load(CORE) as z:
        old_h=[arb(float(v)) for v in z['segment_proper_duration_proof_center']]
        old_x=arb(float(z['node_log_R4_center'][0]))
        old_h_total=np.sum(z['segment_proper_duration_interval'],axis=0).tolist()
    initial=a['center'];r=[arb(metadata['state_radius'])]*98+[arb(metadata['descriptor_radius'])]
    if any(not launch['corrected_state_action'][i,0].overlaps(initial[i]) for i in range(98)):
        raise ValueError('launch and flow-box centers differ')
    # A dyadic arc horizon inside the new certified box; the far endpoint is
    # a Friedrichs proof-core choice, not a physical endpoint/descriptor hit.
    horizon=arb(2)**-69
    c=flow_certificate(initial,launch['launch_augmented'],a['rate'],a['derivative'],r,horizon)
    # Use the saved evaluated outer box for coefficient bounds only. The flow
    # inclusion uses the exact smaller radii above, not inflated reload radii.
    q,dq=proper_clock(a['domain'],w,a['rate'],a['derivative'])
    _,Jtube=flow_span(c,0,horizon)
    qfirst=dq*Jtube
    total=sum(old_h,arb(0));arc=[horizon*v/total for v in old_h]
    times=[arb(0)];running=arb(0)
    for h in arc:running+=h;times.append(running)
    times[-1]=horizon
    xs=[];dx=[]
    for i,time in enumerate(times):
        # Enclose rounding of the fixed mesh with the exact flow domain.
        if i==len(times)-1:time=horizon
        y,J=flow_at(c,time)
        x,d=radius_jet(y,J,w);xs.append(x);dx.append(d.entries())
    hproper=[h*q for h in arc]
    dh=arb_mat([[h*v for v in qfirst.entries()] for h in arc]);dx=arb_mat(dx)
    arrays=dict(arc_nodes=np.array(times,dtype=object),arc_widths=np.array(arc,dtype=object),
        log_radius=np.array(xs,dtype=object),log_radius_first_73=dx,
        proper_durations=np.array(hproper,dtype=object),proper_duration_first_73=dh,
        proper_clock=arb_mat([[q]]),proper_clock_first_tube=qfirst,
        initial_augmented_jet=c['initial_jet'],first_variation_linear_coefficient=c['AJ'])
    responses={}
    for name,kind,value,chi in [('HS_m1','scalar',1,1),('gauge_m2','scalar',4,1),
                                ('Weyl_n0_plus','product_Dirac',arb(3)/2,1),('Weyl_n0_minus','product_Dirac',arb(3)/2,-1)]:
        print('current proof-core first pullback',name,flush=True)
        result=first_pullback(xs,hproper,dx,dh,channel=kind,value=value,z=-1,chirality=chi)
        for key,v in result.items():arrays[name+'_'+key]=arb_mat([[v]]) if isinstance(v,arb) else v
        responses[name]=dict(value=interval(result['value']),first_jet_norm=bound(result['first']),
            forward_backward_residual=bound(result['replay']))
    out.mkdir(parents=True,exist_ok=False);save_arrays(out/'arrays.npz',arrays)
    laws=['aether_forward_c2_weyl_riccati.py','aether_forward_c2_finite_core_descriptor.py',
        'aether_cancelled_arc_proper_time_pullback.py','aether_ae2_one_seam_descriptor.py',
        'arb_current_history_transport.py','arb_weyl_first_pullback.py']
    paths=[Path(__file__),box/'arrays.npz',box/'report.json',LAUNCH/'arrays.npz',CORE,ROOT/FIXED]
    paths += [ROOT/'src/bhsm/interface'/p for p in laws]
    paths += [BASE/(n+'.json') for n in ['BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT',
        'BHSM_N12_INCOMING_MF_COMPACT_MATCH','BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE',
        'BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR']]
    report=dict(status='CURRENT_CENTER_C2_FINITE_PROOF_CORE_AND_FIRST_PULLBACK_ENCLOSED',
        base='certified node13 neighborhood; 72 reset labels plus current flow',
        scope='New finite C2 prefix, not old descriptor-endpoint history or full incoming+C2 joint operator',
        core_choice='r in [0,2^-69]; old 1222 relative duration weights are proof mesh only',
        physical_endpoint_condition_added=False,old_descriptor_increments_preserved=False,
        proper_duration=interval(horizon*q),historical_total_proper_duration=old_h_total,
        proper_clock=interval(q),descriptor_speed=interval(a['rate'][98]),
        picard=dict(excursion_upper=str(c['excursion_upper']),weighted_L=interval(c['L']),
            weighted_L_times_horizon=interval(c['L']*horizon)),
        first_variation='J(t) in J0+t*DF(B)*J0 + E; |E_ij| <= r_i ||J0_j/r|| (Lt)^2 exp(Lt)/2',
        duration_first_jet='D h_i = integral_{arc_i} Dq(y(t))*J(t) dt; enclosed jointly, not zeroed',
        coefficient_difference=dict(log_radius=interval(xs[0]-old_x),classification='BASE_POINT_SHIFT; same physical coefficient law'),
        historical_certificates_inherited=0,new_flow_boxes=1,current_core_mesh_segments=len(arc),
        historical_actions_recomputed=0,first_variation_columns=73,independent_history_solves=0,
        negative_axis_checks=responses,negative_axis_checks_are_graded_heat_outputs=False,
        recurrence_scope='Certified values/first jets of the owned piecewise-midpoint Riccati model. A continuum-history interpolation remainder is not promoted from this model.',
        proper_clock_first_jet_max_radius=max(float(v.rad()) for v in qfirst.entries()),
        proper_clock_first_jet_max_midpoint=max(float(abs(v.mid())) for v in qfirst.entries()),
        duration_first_jet_signs_resolved=any(not v.contains(0) for v in dh.entries()),
        current_incoming_parent_required='Formation-side state/history and its 73D pullback in the common reset frame at this child realization; a C2-forward prefix cannot substitute for it.',
        incoming_parent_history_instantiated=False,UR_current_jet_instantiated=False,active_contact_jet_instantiated=False,
        R_history_7x73=None,R_complete_7x73=None,complete_rank=None,
        history_row_norms=None,largest_seven_row_correction=None,
        material_response_promoted=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','proper_duration','proper_clock','picard')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--box',type=Path,default=PACKET/'flow_box');a=p.parse_args();calculate(a.out,a.box)
