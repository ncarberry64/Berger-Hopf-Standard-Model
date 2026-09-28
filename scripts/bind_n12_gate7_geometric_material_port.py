"""Source-bind the 3+4 split and replay current trace/material local blocks.

Only frozen inputs and inexpensive explicit geometric formulas are consumed.
No local action jet, Stage-B calculation, or history prefix is regenerated.
"""
import argparse
import ast
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import amat,bound,digest,encoded,FIXED
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from diagnose_n12_gate7_eight_reaction_center import block,identity
from derive_n12_gate7_slaved_interface import A
from bhsm.interface.geometric_material_port import geometric_trace_jet,required_material_jet,TRACE_OBJECT,MATERIAL_OBJECT

BASE=ROOT/'artifacts/flagship_integration'
OWNER=ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'


def source_functions():
    source=OWNER.read_text(encoding='utf-8')
    tree=ast.parse(source)
    names={'_trace_jacobian_at_order','_attachment_jacobian_at_order','_boundary_lift',
           '_canonical_pair_at_order','_metric_radial_flux_covector_at_order','_child_rows_at_order'}
    definitions={node.name:node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names}
    # Execute the actual trace owner, without importing/running its action code.
    namespace={'np':np,'dimensions':lambda order:{'coordinates':1+3*order}}
    exec(compile(ast.Module(body=[definitions['_trace_jacobian_at_order']],type_ignores=[]),str(OWNER),'exec'),namespace)
    return namespace['_trace_jacobian_at_order'],{
        name:dict(first_line=f.lineno,last_line=f.end_lineno,
                  text='\n'.join(source.splitlines()[f.lineno-1:f.end_lineno]))
        for name,f in definitions.items()}


def radial_from_current_state(Y):
    """The frozen raw radial owner, with identical binary64 constants."""
    sk=[(-1)**(j+1) for j in range(12)];sj=[(-1)**j for j in range(12)]
    u=sum((Y[1+j]*sk[j] for j in range(12)),arb(0))
    w=sum((Y[13+j]*sj[j] for j in range(12)),arb(0))
    v=sum((Y[25+j]*sj[j] for j in range(12)),arb(0))
    N=sum((Y[74+j]*sk[j] for j in range(12)),arb(0)).exp()
    radius=arb(float(A.RADIUS0))*Y[0].exp();root2=arb(math.sqrt(2.0))
    aa=radius*(u+v).exp()/root2;bb=radius*(u-v).exp()/root2;cc=radius*(u+w).exp()
    pref=3*N*aa**3*bb**3/cc
    raw=arb_mat(37,1)
    for j in range(12):raw[25+j,0]=2*pref*sj[j]
    return raw


def calculate(out):
    ctx.prec=512
    inputs={};sources=[Path(__file__),OWNER,ROOT/FIXED,
        ROOT/'src/bhsm/interface/geometric_material_port.py',
        ROOT/'src/bhsm/interface/heat_zeta_mixed_boundary_launch.py',
        ROOT/'src/bhsm/interface/aether_n3_required_child_cauchy_flux_v17_93.py',
        ROOT/'scripts/derive_n12_gate7_slaved_interface.py']
    for key,name in [('launch','gate7_launch_response_20260927'),
                     ('child','gate7_comoving_interface_20260927/node13'),
                     ('seeds','gate7_material_seeds_20260927'),
                     ('spectral','gate7_current_spectral_20260927')]:
        directory=BASE/name
        report=json.loads((directory/'report.json').read_bytes())
        if digest(directory/'arrays.npz')!=report['arrays_SHA256']:
            raise ValueError('frozen input changed: '+name)
        inputs[key]=load(directory/'arrays.npz')
        sources.extend([directory/'arrays.npz',directory/'report.json'])
    current=BASE/'gate7_coupled_fiber_center_20260927/neighborhood/arrays.npz'
    history=BASE/'gate7_current_history_20260927/core'
    hreport=json.loads((history/'report.json').read_bytes())
    if digest(history/'arrays.npz')!=hreport['arrays_SHA256']:
        raise ValueError('frozen C2 prefix changed')
    sources.extend([current,history/'report.json',history/'arrays.npz'])
    launch,child=inputs['launch'],inputs['child']
    node=load(current)
    state=arb_mat(launch['corrected_state_action'].tolist())
    center_replay=state-arb_mat(node['left_state_domain'][:98,None].tolist())
    if not all(x.contains(0) for x in center_replay.entries()):raise ValueError('center mismatch')
    child_report=json.loads((BASE/'gate7_comoving_interface_20260927/node13/report.json').read_bytes())
    if digest(current) not in child_report['source_SHA256'].values():raise ValueError('canonical center unbound')
    with np.load(ROOT/FIXED) as z:weights=[arb(float(x)) for x in z['state_weights']]
    Y=[state[i,0]/weights[i] for i in range(98)]
    T=arb_mat(launch['launch_action'].tolist())
    trace_owner,spans=source_functions()
    trace_raw=amat(trace_owner(12));trace=arb_mat(3,98)
    for i in range(3):
        for k in range(37):trace[i,k]=trace_raw[i,k]/weights[k]
    zero=arb_mat(3,73)
    geometric=geometric_trace_jet(trace,T,zero)
    frozen=arb_mat(launch['response_trace'].tolist())
    trace_replay=geometric-frozen
    if not all(x.contains(0) for x in trace_replay.entries()):raise ArithmeticError('native trace replay fails')
    gm=arb_mat(3,73,[x.mid() for x in geometric.entries()])
    right_inverse=gm.transpose()*(gm*gm.transpose()).inv()
    trace_rank_replay=geometric*right_inverse-identity(3)
    if bound(trace_rank_replay)['approximate_upper']>=1:raise ArithmeticError('trace rank not certified')
    # Current trace map is constant; all three scalar outputs are explicit here.
    trace_value=trace*state
    v=sum((Y[25+j]*((-1)**j) for j in range(12)),arb(0));t=(2*v).tanh()
    radius_trace=arb_mat([[(1-t)*geometric[1,j]/2+(1+t)*geometric[2,j]/2 for j in range(73)]])
    radius_replay=radius_trace-arb_mat(inputs['spectral']['log_R4_first_73'].tolist())

    # Reuse canonical/frozen dynamic jets, recombining signed terms only.
    qlift=arb_mat(child['canonical_lift_q'][:37].tolist())
    conormal=qlift.transpose()*radial_from_current_state(Y)
    momentum=arb_mat(child['reactions'][3:5].tolist())
    target_flux=arb_mat(child['reactions'][5:7].tolist())
    rate=arb_mat(child['momentum_time_derivative'].tolist())
    force=target_flux+conormal+rate
    dc=arb_mat(child['derivative_action'].tolist())
    event=arb_mat(launch['native_event_7x98'].tolist())
    dP=block(dc,[3,4],range(98))*T
    dG=block(event,[5,6],range(98))*T
    mixed=arb_mat(child['momentum_mixed_derivative'].tolist())*T
    direction=arb_mat(child['momentum_dynamic_direction_derivative'].tolist())*T
    native_flux=block(dc,[5,6],range(98))*T
    # Force jet reconstructed from the already-owned dynamic identity. It is
    # not a fresh independent action calculation or a heat/history correction.
    dF=native_flux+dG+mixed+direction
    material=required_material_jet(dP,dF,dG,mixed,direction)
    frozen_material=block(dc,range(3,7),range(98))*T
    material_replay=material-frozen_material
    if not all(x.contains(0) for x in material_replay.entries()):raise ArithmeticError('dynamic decomposition replay fails')
    order=arb_mat([[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]])
    E=arb_mat(inputs['seeds']['canonical_four_seed_action_98x4'].tolist())
    reordered=E*order
    offset=arb_mat([[arb(0)],[arb(0)]]+(-conormal-rate).tolist())
    native_value=arb_mat(momentum.tolist()+target_flux.tolist())
    canonical_value=arb_mat(momentum.tolist()+force.tolist())
    rows=[]
    for i in range(7):
        rows.append(dict(row=i+1,type='GEOMETRIC_COMPATIBILITY' if i<3 else 'MATERIAL_ACTION_REACTION',
            channel=('trace '+str(i+1)) if i<3 else ('momentum '+str(i-2)) if i<5 else ('dynamic flux '+str(i-4)),
            owner='_trace_jacobian_at_order + _child_rows_at_order' if i<3 else '_canonical_pair_at_order + _child_rows_at_order' if i<5 else '_canonical_pair_at_order + _metric_radial_flux_covector_at_order + _child_rows_at_order',
            state_dependence='q only; constant trace map at chi=pi/4' if i<3 else 'q,v,m through complete-action gradient/Hessian and moving Lv' if i<5 else 'q,v,m; Lq, radial, DP[X] and action-owned rate X',
            explicit_joint_heat_zeta_history_call=False,
            local_action_sector_dependence=False if i<3 else True,
            history_route='geometric chain rule through the state/reset/history jet; no trace action seed' if i<3 else 'mixed action contraction plus moving Lv and full internal adjoint' if i<5 else 'mixed configuration-force contraction, conormal variation, and D2P[X,Pj]+DP[DX Pj]; no static basis substitution',
            history_direct_scope='No explicit heat/zeta call in this local producer; full nonlocal action corrections must be composed through its owned variational/dynamic route.',
            child_sign=1 if i<5 else -1,event_sign=-1 if i<5 else 1))
    out.mkdir(parents=True,exist_ok=False)
    save_arrays(out/'arrays.npz',dict(
        trace_raw_3x37=trace_raw,trace_action_3x98=trace,trace_value_3x1=trace_value,
        geometric_trace_3x73=geometric,trace_overlap_replay=trace_replay,
        signed_event_trace_3x73=-geometric,trace_rank_replay=trace_rank_replay,
        trace_fixed_section_explicit_shape_3x73=zero,trace_explicit_attachment_3x73=zero,
        trace_direct_action_increment_3x73=zero,trace_radius_replay=radius_replay,
        canonical_order_change_4x4=order,canonical_ordered_material_directions_98x4=reordered,
        canonical_momentum_value=momentum,canonical_force_value_recovered=force,
        conormal_value=conormal,momentum_rate_value=rate,
        canonical_pair_value_4x1=canonical_value,required_native_material_value_4x1=native_value,
        force_to_flux_offset_4x1=offset,value_decomposition_replay=native_value-canonical_value-offset,
        canonical_momentum_jet=dP,canonical_force_jet_recovered=dF,conormal_jet=dG,
        momentum_mixed_jet=mixed,momentum_rate_direction_jet=direction,
        local_required_material_4x73=material,material_overlap_replay=material_replay,
        dynamic_force_to_flux_jet=-dG-mixed-direction))
    report=dict(status='THREE_GEOMETRIC_FOUR_MATERIAL_SPLIT_SOURCE_BOUND',
        classification_dimensions=[3,4],seven_action_seed_requirement_retired=True,
        trace_target=TRACE_OBJECT,material_target=MATERIAL_OBJECT,
        geometric_trace_materialized=True,trace_scope='Current frozen node13 chart; complete three-row geometry, not a new complete joint-history normal graph.',
        trace_shape=[3,73],trace_rank=3,trace_rank_inverse_defect=bound(trace_rank_replay),
        trace_overlap_replay=bound(trace_replay),trace_row_norms=[bound(block(geometric,[i],range(73))) for i in range(3)],
        radius_trace_crosscheck=bound(radius_replay),
        trace_contributions=[
            dict(name='fixed material section chain rule',status='ALREADY_INCLUDED',expression='T W^-1 launch_action',numeric_array='geometric_trace_3x73'),
            dict(name='explicit section/frame motion',status='IDENTICALLY_ZERO',reason='Owner evaluates constant T at fixed material chi=pi/4; physical seam/state motion stays in launch_action'),
            dict(name='explicit attachment-map derivative',status='IDENTICALLY_ZERO',reason='A2 and DA2 do not occur in the three trace equations'),
            dict(name='state/formation/history transport',status='ALREADY_INCLUDED_IN_SUPPLIED_CHART',reason='Current 72-label-plus-flow launch jet consumed once; no separately instantiated current formation history inferred'),
            dict(name='reset pullback',status='ALREADY_INCLUDED_IN_SUPPLIED_CHART',reason='Inherited reset-family labels are in the frozen launch chart; a new complete joint reset/normal correction remains uncomputed')],
        no_double_counting='geometric_trace_3x73 equals the existing local top block. It is NOT an additive R_trace_history. Direct action correction at fixed state is zero; any new full-system state response contributes T W^-1 Delta_J_joint.',
        R_trace_history_3x73=None,trace_explicit_action_correction_zero=True,
        canonical_order_old=['Bq1','Bq2','Bv1','Bv2'],canonical_order_new=['Bv1','Bv2','Bq1','Bq2'],
        canonical_order_inverse_defect=bound(order*order-identity(4)),
        material_correspondence='Bv1/2 give canonical momentum; Bq1/2 give configuration force. Required dynamic flux is F-G-DP[X], not F.',
        force_to_flux_is_static_basis_change=False,
        actual_map='[P,F] -> [P,F-G-DP[X]]; derivative [DP,DF] -> [DP,DF-DG-D2P[X,Pj]-DP[DX Pj]]',
        force_to_flux_offset=bound(offset),force_to_flux_nonzero_entry_lower=max(float(abs(x).lower()) for x in offset.entries()),
        local_material_overlap_replay=bound(material_replay),
        local_material_row_norms=[bound(block(material,[i],range(73))) for i in range(4)],
        local_dynamic_correction_row_norms=[bound(block(-dG-mixed-direction,[i],range(73))) for i in range(2)],
        material_decomposition_scope='Recombination of frozen local jets; recovered DF is not an independent replay or a history heat/zeta response.',
        current_material_history_4x73_materialized=False,
        remaining_inputs=[
            'Owner-composed four material history incidences in the current joint formation/reset/C2 realization, with canonical seed motion and full internal adjoint',
            'Native flux correction includes conormal and time derivative of the history momentum response; retain rate/normal dependence before support',
            'Current formation history and reset/contact numerical jets are not supplied by the frozen C2-only prefix'],
        retained_sectors=[
            dict(name='formation',state='REQUIRED_NOT_NUMERICALLY_INSTANTIATED'),
            dict(name='reset/U_R',state='REQUIRED_COVARIANT_PULLBACK_NOT_AN_INDEPENDENT_SOURCE'),
            dict(name='C2',state='FROZEN_1222_PREFIX_REUSED_NOT_REBUILT'),
            dict(name='moving duration',state='SIGNED_TERMS_REQUIRED_NOT_ZEROED'),
            dict(name='gauge Wentzell contact',state='ACTIVE'),
            dict(name='scalar/topographic and AE2 pair/contact',state='ACTIVE_COUNT_ONCE'),
            dict(name='independent fermion delta contact',state='ZERO_BY_FROZEN_AE2_OWNER'),
            dict(name='constraint/descriptor/history normal response',state='FULL_INTERNAL_ADJOINT_REQUIRED')],
        R_history_7x73=None,R_complete_7x73=None,material_response_promoted=False,
        rows=rows,source_definitions=spans,source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        arrays_SHA256=digest(out/'arrays.npz'),prefix_rebuilt=False,Stage_B_rerun=False,action_producers_run=0,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','trace_rank','trace_overlap_replay','trace_row_norms',
        'force_to_flux_offset','force_to_flux_nonzero_entry_lower','local_material_overlap_replay')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    calculate(parser.parse_args().out)
