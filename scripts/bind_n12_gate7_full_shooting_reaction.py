"""Replay the full frozen interval-13 first derivative; no scientific producers."""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, FIXED, PHYSICAL, CAUSAL, amat, mid, frob, bound, digest, encoded, frame
from diagnose_n12_gate7_eight_reaction_center import block, identity

C = ROOT/BASE/'gate7_66d_checkpoint_20260926'
D = ROOT/BASE/'gate7_8reaction_center_20260926'
PRED = ROOT/BASE/'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz'
MID = ROOT/BASE/'BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.npz'
PROVENANCE = {
    'scripts/audit_n12_gate7_correlated_descriptor_newton_midpoint_replay.py': [(49,78)],
    'scripts/audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate.py': [(67,77)],
    'src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py': [(167,217)],
    'scripts/materialize_n12_gate7_correlated_descriptor_augmented_jacobians.py': [(61,84)],
    'scripts/materialize_n12_gate7_augmented_fixed_descriptor_block_newton_predictor.py': [(67,87)],
    'scripts/audit_n12_gate7_current_green_componentwise_two_radius.py': [(102,115)],
    'scripts/certify_n12_gate7_current_green_signed_transverse_causal_center.py': [(683,689),(740,745)],
    'scripts/checkpoint_n12_gate7_66d_tangent_binding.py': [(51,56),(79,96)],
    'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py': [(3199,3228),(3257,3282)],
}


def hs_residual(left, right, left_rate, right_rate, midpoint_rate, h):
    """Exact signed formula of the frozen assembler, valid for arrays or Arb."""
    return right-left-h*(left_rate+4*midpoint_rate+right_rate)/6


def hs_derivative_parts(jl, jr, jm, left_direction, right_direction, h):
    """Separate direct endpoint terms from midpoint chain-rule incidence."""
    left = -left_direction-(jl*left_direction)*(h/6)
    right = right_direction-(jr*right_direction)*(h/6)
    midpoint_direction = (left_direction+right_direction)/2+(jl*left_direction-jr*right_direction)*(h/8)
    midpoint = -(jm*midpoint_direction)*(2*h/3)
    return {'right':right, 'left':left, 'midpoint':midpoint}


def calculate():
    ctx.prec=512
    sources={}
    def verify(path, expected=None):
        actual=digest(path)
        if expected is not None and actual!=expected:
            raise ValueError('frozen source hash mismatch: '+str(path))
        sources[str(path.relative_to(ROOT))]=actual
    old=json.loads((D/'report.json').read_bytes())
    binding=json.loads((C/'binding/report.json').read_bytes())
    for path,expected in old['source_SHA256'].items(): verify(ROOT/path,expected)
    verify(D/'arrays.npz',old['arrays_SHA256'])
    verify(D/'report.json')
    for name in (FIXED,PHYSICAL,CAUSAL): verify(ROOT/name,binding['source_SHA256'][str(ROOT/name)])
    meta=json.loads(MID.with_suffix('.json').read_bytes())
    verify(MID,meta['data_SHA256']);verify(MID.with_suffix('.json'))
    provenance={}
    for path,ranges in PROVENANCE.items():
        verify(ROOT/path)
        lines=(ROOT/path).read_text().splitlines()
        provenance[path]=[dict(start=a,end=b,text='\n'.join(lines[a-1:b])) for a,b in ranges]
    verify(Path(__file__))
    with np.load(D/'arrays.npz') as z: frozen={k:z[k] for k in z.files}
    P,Pi,Q,Qinv=map(amat,(frozen['trial_transform'],frozen['trial_transform_inverse'],frozen['M_qq'],frozen['M_qq_inverse']))
    with np.load(C/'binding/arrays.npz') as z: b={k:z[k] for k in z.files}
    with np.load(ROOT/PHYSICAL) as z:
        tangents=z['endpoint_physical_tangent_action'][13:15]
        jl,jr=map(amat,z['endpoint_augmented_Jacobian_action'][13:15])
        jm=amat(z['midpoint_augmented_Jacobian_action'][13])
    with np.load(ROOT/FIXED) as z: rates=z['exact_endpoint_augmented_rates'][13:15]
    with np.load(PRED) as z:
        left_block=amat(z['left_Newton_blocks'][13]);right_block=amat(z['right_Newton_blocks'][13])
    with np.load(C/'newton/M_13.npz') as z: M=amat(z['M_13'])
    with np.load(ROOT/CAUSAL) as z: causal=amat(z['causal_maps_center'][13])
    with np.load(MID) as z:
        h=arb(float(z['action_times'][14]-z['action_times'][13]))
        endpoints=z['augmented_endpoints'][13:15]; erates=z['exact_endpoint_rates'][13:15]
        mrates=z['exact_midpoint_rates'][13]; stored_residual=z['Hermite_Simpson_shooting_residual'][13]
        midpoint=z['midpoint_augmented_action_values'][13]
    residual_replay=hs_residual(endpoints[0],endpoints[1],erates[0],erates[1],mrates,float(h))
    # The max(s,0) branch in the producer is inactive at these stored centers.
    if not np.all(endpoints[:,98]>0) or not midpoint[98]>0:
        raise ValueError('descriptor clamp branch requires separate derivative ownership')
    E0,E1=[amat(frame(t,1e-7)) for t in tangents]
    test=amat(frame(tangents[1],1e6)).transpose()
    W=block(Pi,range(66,74),range(74))*test
    N=test*left_block*E0
    launch=amat(b['node_014_launch_coordinates'])
    families=[amat(b[f'node_{k:03d}_family']) for k in (13,14)]
    flows=[]; histories=[]
    for i in range(2):
        v=np.r_[np.linalg.lstsq(tangents[i],rates[i,:98],rcond=None)[0],rates[i,98]/1e-7]
        flows.append(amat(v[:,None]))
        F=arb_mat([[families[i][r,c] if c<72 else flows[i][r,0] for c in range(73)] for r in range(74)])
        histories.append(F*launch)
    V0,V1=histories
    Pp=block(P,range(74),range(66))
    parts=hs_derivative_parts(jl,jr,jm,E0*V0,E1*Pp,h)
    parts['history_external']=arb_mat(99,66)
    forcing={k:W*v for k,v in parts.items()}
    total=sum(forcing.values(),arb_mat(8,66))
    reactions={k:-Qinv*v for k,v in forcing.items()}
    reaction=sum(reactions.values(),arb_mat(8,66))
    truth=amat(np.vstack((np.zeros((7,66)),b['node_014_child_augmented'][73])))
    delta=reaction-truth
    descriptor_error=bound(block(delta,[7],range(66)))
    descriptor_allowance=arb(old['descriptor_reprojection_allowance_upper'])
    X=amat(b['node_014_fixed_into_physical'])
    Aphys=amat(frozen['interface_normalized'])*X.inv()
    child_error=arb(binding['nodes'][1]['child_reprojection_error']['exact_upper'])
    coeff_allowance=child_error/(1-arb(binding['nodes'][1]['gram_error_upper_physical'])).sqrt()
    boundary_rows=[]
    for i in range(7):
        allowance=frob(block(Aphys,[i],range(73)))*coeff_allowance
        error=frob(block(delta,[i],range(66)))
        boundary_rows.append(dict(channel=old['interface_order'][i],error_upper=str(error.fmpq()),
            error_diagnostic=float(error),allowance_upper=str(allowance.upper().fmpq()),
            allowance_diagnostic=float(allowance.upper()),passes=bool(error<=allowance)))
    # Independently owned first-order physical rows: fixed interface and causal descriptor graph.
    family_s=np.r_[b['node_014_family'][73],rates[1,98]/1e-7]
    graph=amat(b['node_014_launch_state']).transpose().solve(amat(family_s[:,None])).transpose()
    G=arb_mat(8,74)
    for i in range(7):
        for j in range(73): G[i,j]=Aphys[i,j]
    for j in range(73): G[7,j]=-graph[0,j]
    G[7,73]=1
    GP=G*P; Gp=block(GP,range(8),range(66));Gq=block(GP,range(8),range(66,74))
    bridge=Q*Gq.inv()
    defect=total-bridge*Gp
    # Exact affine-jet bridge, with signed source defect retained, never fitted away.
    bridge_residual=bound(total-bridge*Gp-defect)
    # Independent right/left chain-rule blocks for ownership replay.
    zl=arb_mat(99,74)
    dl=hs_derivative_parts(jl,jr,jm,E0,zl,h)
    dr=hs_derivative_parts(jl,jr,jm,zl,E1,h)
    left_chain=sum(dl.values(),arb_mat(99,74));right_chain=sum(dr.values(),arb_mat(99,74))
    # Preserve the saved 8x8 block; carry its rounding difference from the chain.
    delta_q=W*right_chain*block(P,range(74),range(66,74))-Q
    recurrence=families[1]-causal*families[0]
    flow_defect=M*flows[1]+N*flows[0]
    alpha=block(launch,[72],range(66))
    history_defect=M*V1+N*V0
    family_part=(M*families[1]+N*families[0])*block(launch,range(72),range(66))
    projection=amat(np.eye(8)[7:8]);expected_s=block(truth,[7],range(66))
    denom=sum((v*v for v in expected_s.entries()),arb(0))
    contribution_report={}
    for name,value in {**reactions,'signed_sum':reaction}.items():
        row=projection*value
        signed=sum((row[0,i]*expected_s[0,i] for i in range(66)),arb(0))/denom
        contribution_report[name]=dict(descriptor_row_norm=bound(row),signed_projection_on_expected_descriptor=float(signed.mid()))
    arrays={**{f'forcing_{k}':mid(v) for k,v in forcing.items()},
        **{f'reaction_{k}':mid(v) for k,v in reactions.items()},
        'forcing_total':mid(total),'Dphi_total':mid(reaction),'Dphi_truth':mid(truth),
        'left_child_history':mid(V0),'right_child_history':mid(V1),'left_reduced_block':mid(N),
        'physical_rows':mid(G),'physical_rows_in_split':mid(GP),'row_bridge':mid(bridge),
        'signed_row_bridge_defect':mid(defect),'signed_frozen_Q_defect':mid(delta_q),
        'flow_defect':mid(flow_defect),'history_defect':mid(history_defect)}
    passed=all(r['passes'] for r in boundary_rows) and frob(block(delta,[7],range(66)))<=descriptor_allowance
    report=dict(status='CENTER_REPLAY_WITHIN_FROZEN_REPROJECTION_ALLOWANCES' if passed else 'STOP_FULL_CENTER_REPLAY_FAILED',
        source_SHA256=sources,source_line_provenance=provenance,interval=13,node=14,
        authority='FROZEN_FIRST_ORDER_JET_WITH_EXPLICIT_DEFECT_NOT_NONLINEAR_EQUATION_EQUIVALENCE',
        residual_formula='R=y14-y13-h/6*(f13+4*f(mid)+f14); mid=(y13+y14)/2+h/8*(f13-f14); external_history=0',
        total_derivative_formula='Etest14^T*(Rright*Etrial14*dy14 + Lleft*Etrial13*dy13); history enters dy13, not an extra additive residual',
        reaction_formula='Q*dq + W*(right_direct + left_direct + midpoint_chain)=0',
        row_identity='[Ftotal,Q_actual] = B*[Gp,Gq] + [E,deltaQ], B=Q*Gq^-1, E=Ftotal-B*Gp, deltaQ=Q_actual-Q; signed defects retained',
        actual_chain_reaction_block_defect=bound(delta_q),
        row_identity_residual=bridge_residual,row_identity_defect=bound(defect),
        computed_reaction_equation_residual=bound(Q*reaction+total),
        nonlinear_row_identity_proved=False,center_replay_passes=bool(passed),
        stored_residual_replay_max_abs=float(np.max(np.abs(residual_replay-stored_residual))),
        midpoint_replay_max_abs=float(np.max(np.abs((endpoints[0]+endpoints[1])/2+float(h)*(erates[0]-erates[1])/8-midpoint))),
        descriptor_clamp_inactive=True,descriptor_trial_scale=1e-7,descriptor_test_scale=1e6,
        derivative_left_block_replay=bound(left_chain-left_block*E0),derivative_right_block_replay=bound(right_chain-right_block*E1),
        forcing_block_replay=bound(total-block(Pi,range(66,74),range(74))*(M*Pp+N*V0)),
        frozen_reaction_block_replay=bound(block(Pi,range(66,74),range(74))*M*block(P,range(74),range(66,74))-Q),
        saved_causal_map_identity=bound(M*causal+N),causal_family_recurrence=bound(recurrence),
        causal72_history_contribution=bound(family_part),flow_history_contribution=bound(flow_defect*alpha),
        history_defect_decomposition=bound(history_defect-family_part-flow_defect*alpha),
        full_history_defect=bound(history_defect),right_history_binding_replay=bound(V1-amat(b['node_014_child_augmented'])),
        descriptor_error=descriptor_error,descriptor_frozen_allowance=old['descriptor_reprojection_allowance_upper'],
        boundary_rows=boundary_rows,contributions=contribution_report,
        original_descriptor_error=old['descriptor_replay_difference_diagnostic'],
        reduction_factor_diagnostic=old['descriptor_replay_difference_diagnostic']/descriptor_error['approximate_upper'],
        no_separate_current_green_forcing=True,history_dependence_retained_in_left_endpoint=True,
        frozen_Mqq_reextracted=False,tolerances_changed=False,scientific_producers_run=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,nonlinear_work_performed=False)
    return report,arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    report,arrays=calculate();a.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (a.out/'arrays.npz').write_bytes(buffer.getvalue());report['arrays_SHA256']=digest(a.out/'arrays.npz')
    (a.out/'report.json').write_bytes(encoded(report))
    print(json.dumps({'status':report['status'],'descriptor_error':report['descriptor_error']['approximate_upper'],'boundary_rows':report['boundary_rows'],'contributions':report['contributions']},indent=2))


if __name__=='__main__':main()
