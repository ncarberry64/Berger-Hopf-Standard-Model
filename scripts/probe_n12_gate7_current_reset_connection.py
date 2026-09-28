"""Numerical initial guess for the current-node13 to reset connection.

This is NOT a certified flow or formation history. It uses the owned fixed-s
field as a numerical predictor, retaining the supplied signed descriptor.
No binary64 eigenvalue is promoted to a signed-descriptor certificate.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import DOP853

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import FIXED,digest,encoded
from certify_n12_gate7_coupled_center_neighborhood import load
from bhsm.interface.aether_forward_c2_exact_fixed_s_field import exact_fixed_s_field_action

BASE=ROOT/'artifacts/flagship_integration'


def calculate(out,max_evaluations):
    center=BASE/'gate7_coupled_fiber_center_20260927/neighborhood/arrays.npz'
    field=BASE/'gate7_coupled_fiber_center_20260927/uniform_inputs/left.npz'
    g=load(center);r=load(field)
    y0=np.array([float(x.mid()) for x in g['left_state_domain'][:98]])
    s0=float(g['left_state_domain'][98].mid())
    f=np.array([float(x.mid()) for x in r['rate']])
    fs0=f[:98]/f[98]
    with np.load(ROOT/FIXED) as z:
        weights=z['state_weights'];reference=z['branch_reference']
    records=[];states=[y0.copy()];times=[1.];evaluations=0
    def rhs(t,y):
        nonlocal evaluations
        if t==1. and np.array_equal(y,y0):return s0*fs0
        if evaluations>=max_evaluations:raise RuntimeError('NUMERICAL_GUESS_EVALUATION_LIMIT')
        evaluations+=1
        a=exact_fixed_s_field_action(state=y/weights,weights=weights,reference=reference,
            signed_descriptor=max(0.,t*s0))
        if a['selected_branch']!=24:raise ArithmeticError('NUMERICAL_SELECTED_LINE_CHANGED')
        records.append([t,a['Delta'],a['selected_eigenvalue'],np.linalg.norm(a['field_action'])])
        if evaluations%10==0:print('new predictor evaluations',evaluations,'remaining descriptor fraction',t,flush=True)
        return s0*a['field_action']
    failure=None
    solver=DOP853(rhs,1.,y0,0.,rtol=1e-9,atol=1e-10,first_step=1/32,max_step=1/8)
    try:
        while solver.status=='running':
            message=solver.step()
            if solver.status=='failed':failure=message;break
            times.append(solver.t);states.append(solver.y.copy())
    except (RuntimeError,ArithmeticError,ValueError) as error:
        failure=str(error)
    complete=solver.status=='finished'
    with np.load(BASE/'BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz') as z:
        old=z['proof_center'][:98]*weights
        lift=z['projected_C2_parameter_lift'];radius=float(z['parameter_radius'])
    endpoint=states[-1]
    delta=endpoint-old
    xi=np.linalg.lstsq(lift,delta,rcond=None)[0]
    out.mkdir(parents=True,exist_ok=False)
    np.savez_compressed(out/'candidate.npz',descriptor_fraction=np.array(times),
        state_action=np.array(states),rhs_diagnostics=np.array(records),weights=weights,
        historical_reset_displacement_action=delta,reset_linear_coordinate_guess=xi,
        reset_linear_fit_residual=delta-lift@xi)
    report=dict(status='CURRENT_RESET_CONNECTION_NUMERICAL_GUESS_ONLY',
        reached_descriptor_zero=complete,completed_steps=len(times)-1,new_field_evaluations=evaluations,
        last_descriptor_fraction=times[-1],failure=failure,
        predictor_solver=dict(method='DOP853',rtol=1e-9,atol=1e-10,
            scope='New numerical guess tolerances, not certificate allowances'),
        current_signed_descriptor=s0,branch_required=24,
        reset_action_displacement_norm=float(np.linalg.norm(delta)),
        linear_reset_parameter_norm=float(np.linalg.norm(xi)),
        historical_parameter_radius=radius,
        linear_reset_fit_residual_norm=float(np.linalg.norm(delta-lift@xi)),
        no_reset_membership_inferred_from_linear_fit=True,
        current_reset_member_certified=False,incoming_parent_history_certified=False,
        first_73_jet_constructed=False,frozen_prefix_rebuilt=False,frozen_interval_actions_run=False,
        scientific_scope='Current outgoing connection guess only; not the incoming parent arm. The nonlinear reset and branch-23 orientation must be bound before incoming integration.',
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in [center,field,ROOT/FIXED,
            BASE/'BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz',Path(__file__),
            ROOT/'src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py']},
        candidate_SHA256=digest(out/'candidate.npz'),Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('reached_descriptor_zero','completed_steps','new_field_evaluations',
        'failure','reset_action_displacement_norm','linear_reset_parameter_norm','linear_reset_fit_residual_norm')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--max-evaluations',type=int,default=160)
    a=p.parse_args();calculate(a.out,a.max_evaluations)
