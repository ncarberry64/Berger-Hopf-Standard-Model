"""New high-precision outgoing connection guess; NOT a validated trajectory.

Integrate displacements from the exact stored center, avoiding binary64
rounding of the large base coordinates. Every new RHS is evaluated by the
owned Arb action/selected-line machinery. Global flow and reset-membership
certification are separate requirements, never inferred from solver success.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx
from scipy.integrate import DOP853

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import solve_n12_gate7_fiber_constrained_center as c
from checkpoint_n12_gate7_66d_tangent_binding import FIXED,digest,encoded
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bhsm.interface.physical_hs_value import verified_eigenline

BASE=ROOT/'artifacts/flagship_integration'


def calculate(out,max_evaluations):
    ctx.prec=512
    cp=BASE/'gate7_coupled_fiber_center_20260927/neighborhood/arrays.npz'
    fp=BASE/'gate7_coupled_fiber_center_20260927/uniform_inputs/left.npz'
    center=load(cp)['left_state_domain'];initial=load(fp)['rate']
    base=np.array([v.mid() for v in center[:98]],dtype=object);s0=center[98].mid()
    with np.load(ROOT/FIXED) as z:
        wf=z['state_weights'];w=np.array([arb(float(v)) for v in wf],dtype=object);reference=z['branch_reference']
    initial_fs=np.array([float((s0*v/initial[98]).mid()) for v in initial[:98]])
    evaluations=0;diagnostics=[];times=[1.];displacements=[np.zeros(98)]
    old=c.action._eigenline;c.action._eigenline=recentered_eigenline(old)
    def rhs(t,dy):
        nonlocal evaluations
        if t==1. and not np.any(dy):return initial_fs
        if evaluations>=max_evaluations:raise RuntimeError('NUMERICAL_GUESS_EVALUATION_LIMIT')
        evaluations+=1
        state=(base+np.array([arb(float(v)) for v in dy],dtype=object))/w
        descriptor=s0*arb(float(t));checks=[]
        with c.sparse.use_optimized_mixed(c.action),c.factored.use_ball_factored_integrand(c.action,state):
            with verified_eigenline(c.action,checks,expected_index=24,normalize_proposal_center=True):
                rate=c.action._rate_enclosure(state,descriptor,wf,reference,None)
        ds=rate.value[98]
        if not ds>0:raise ArithmeticError('POSITIVE_FIXED_S_CHART_NOT_VERIFIED_AT_NEW_PREDICTOR_POINT')
        value=np.array([float((s0*v/ds).mid()) for v in rate.value[:98]])
        diagnostics.append([t,float(ds.mid()),float(ds.rad()),max(float(v.rad()) for v in rate.value)])
        if evaluations%5==0:print('Arb predictor evaluations',evaluations,'remaining descriptor fraction',t,flush=True)
        return value
    failure=None;solver=None
    try:
        solver=DOP853(rhs,1.,np.zeros(98),0.,rtol=1e-9,atol=1e-10,first_step=1/32,max_step=1/8)
        while solver.status=='running':
            message=solver.step()
            if solver.status=='failed':failure=message;break
            times.append(solver.t);displacements.append(solver.y.copy())
    except (RuntimeError,ArithmeticError,ValueError) as error:failure=str(error)
    finally:c.action._eigenline=old
    endpoint=base+np.array([arb(float(v)) for v in displacements[-1]],dtype=object)
    with np.load(BASE/'BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz') as z:
        historical=np.array([arb(float(v)) for v in z['proof_center'][:98]],dtype=object)*w
        lift=z['projected_C2_parameter_lift'];rho=float(z['parameter_radius'])
    delta=np.array([float(v.mid()) for v in endpoint-historical]);xi=np.linalg.lstsq(lift,delta,rcond=None)[0]
    out.mkdir(parents=True,exist_ok=False)
    # These are numerical predictor point values, not interval flow tubes.
    save_arrays(out/'endpoint.npz',dict(current_midpoint_action=base,
        endpoint_action=endpoint,endpoint_signed_descriptor=np.array([s0*arb(times[-1])],dtype=object)))
    np.savez_compressed(out/'path.npz',descriptor_fraction=np.array(times),
        action_displacement=np.array(displacements),rhs_diagnostics=np.array(diagnostics),
        reset_linear_coordinate_guess=xi,reset_linear_fit_residual=delta-lift@xi)
    report=dict(status='ARB_EVALUATED_CURRENT_RESET_CONNECTION_PREDICTOR',
        reached_descriptor_zero=bool(solver is not None and solver.status=='finished'),failure=failure,
        new_point_evaluations=evaluations,completed_steps=len(times)-1,last_descriptor_fraction=times[-1],
        exact_stored_center_midpoint_retained=True,coordinate_integrator='DOP853 on action displacements',
        predictor_rtol=1e-9,predictor_atol=1e-10,certificate_tolerances_changed=False,
        rhs_precision_bits=512,pointwise_branch_index=24,
        full_trajectory_certified=False,current_reset_member_certified=False,
        incoming_parent_history_certified=False,current_first_73_jet_certified=False,
        reset_action_displacement_norm=float(np.linalg.norm(delta)),
        linear_reset_parameter_norm=float(np.linalg.norm(xi)),historical_parameter_radius=rho,
        linear_reset_fit_residual_norm=float(np.linalg.norm(delta-lift@xi)),
        linear_guess_is_not_reset_membership=True,
        frozen_prefix_rebuilt=False,frozen_interval_actions_run=False,
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in [cp,fp,ROOT/FIXED,
            BASE/'BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz',Path(__file__),
            Path(c.action.__file__),ROOT/'scripts/recenter_n12_gate7_current_history_box.py']},
        endpoint_SHA256=digest(out/'endpoint.npz'),path_SHA256=digest(out/'path.npz'),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('reached_descriptor_zero','failure','new_point_evaluations',
        'reset_action_displacement_norm','linear_reset_parameter_norm','linear_reset_fit_residual_norm')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--max-evaluations',type=int,default=160)
    a=p.parse_args();calculate(a.out,a.max_evaluations)
