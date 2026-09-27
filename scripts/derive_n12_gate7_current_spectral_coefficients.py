"""Current-node spectral coefficient first jets; no action/history producers.

The old finite-core coefficient enclosure is tested for base compatibility,
not silently transported. No second operator jet or heat eigensolve is run.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from checkpoint_n12_gate7_66d_tangent_binding import FIXED, digest, encoded, bound
from bhsm.interface.aether_forward_boundary_radius import RADIUS0

BASE=ROOT/'artifacts/flagship_integration'
LAUNCH=BASE/'gate7_launch_response_20260927'
CORE=BASE/'BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz'


def interval(v):
    return dict(lower=str(v.lower().fmpq()),upper=str(v.upper().fmpq()),
                midpoint=float(v.mid()),radius_upper=float(v.rad()))


def calculate(out):
    ctx.prec=512
    a=load(LAUNCH/'arrays.npz')
    if digest(LAUNCH/'arrays.npz')!=json.loads((LAUNCH/'report.json').read_bytes())['arrays_SHA256']:
        raise ValueError('frozen launch packet changed')
    with np.load(ROOT/FIXED) as z:weights=z['state_weights'].copy()
    with np.load(CORE) as z:
        if not np.array_equal(weights,z['state_weights']):raise ValueError('action frames differ')
        old_x=z['node_log_R4_interval'].copy()
    Y=[a['corrected_state_action'][i,0]/arb(float(weights[i])) for i in range(98)]
    T=arb_mat([[a['launch_action'][i,j]/arb(float(weights[i])) for j in range(73)] for i in range(98)])
    row=lambda i:arb_mat([[T[i,j] for j in range(73)]])
    sk=[(-1)**(j+1) for j in range(12)];sj=[(-1)**j for j in range(12)]
    v=sum((Y[25+j]*sj[j] for j in range(12)),arb(0));t=(2*v).tanh()
    x=(arb(float(RADIUS0))/2).log()+Y[0]+sum((Y[1+j]*sk[j] for j in range(12)),arb(0))-(2*v).cosh().log()/2
    logN=sum((Y[74+j]*sk[j] for j in range(12)),arb(0));N=logN.exp()
    dv=sum((row(25+j)*sj[j] for j in range(12)),arb_mat(1,73))
    dx=row(0)+sum((row(1+j)*sk[j] for j in range(12)),arb_mat(1,73))-dv*t
    dlogN=sum((row(74+j)*sk[j] for j in range(12)),arb_mat(1,73))
    vdot=sum((Y[62+j]*sj[j] for j in range(12)),arb(0))
    numerator=Y[37]+sum((Y[38+j]*sk[j] for j in range(12)),arb(0))-t*vdot
    dnum=row(37)+sum((row(38+j)*sk[j] for j in range(12)),arb_mat(1,73))
    dnum-=sum((row(62+j)*sj[j] for j in range(12)),arb_mat(1,73))*t+dv*(2*(1-t*t)*vdot)
    rate=numerator/N;drate=(dnum-dlogN*numerator)/N
    w=(-x).exp();V=(-2*x).exp();c=arb(59)/30
    values=dict(log_R4=x,log_lapse=logN,lapse=N,inverse_radius=w,inverse_radius_squared=V,
                proper_log_radius_rate=rate,zeta_proper_density=-c*w,zeta_coordinate_density=-c*N*w)
    jets=dict(log_R4=dx,log_lapse=dlogN,lapse=dlogN*N,inverse_radius=-dx*w,
              inverse_radius_squared=-dx*(2*V),proper_log_radius_rate=drate,
              zeta_proper_density=dx*(c*w),zeta_coordinate_density=(dlogN-dx)*(-c*N*w))
    R=arb_mat(a['response_7x73'].tolist())
    native_dx=arb_mat([[(1-t)*R[1,j]/2+(1+t)*R[2,j]/2 for j in range(73)]])
    replay=dx-native_dx
    if not all(v.contains(0) for v in replay.entries()):raise ArithmeticError('current chart/native trace binding failed')
    old_lo=arb(float(old_x[:,0].min()));old_hi=arb(float(old_x[:,1].max()))
    separation=x-old_hi
    if not separation>0:raise ArithmeticError('base comparison changed; review before labeling incompatible')
    paths=[Path(__file__),ROOT/FIXED,CORE,LAUNCH/'arrays.npz',LAUNCH/'report.json',
        ROOT/'src/bhsm/interface/aether_forward_boundary_radius.py',
        ROOT/'src/bhsm/interface/aether_ae2_one_seam_descriptor.py',
        ROOT/'src/bhsm/interface/aether_forward_c2_finite_core_descriptor.py',
        ROOT/'src/bhsm/interface/forward_finite_endpoint_heat_force.py',
        ROOT/'artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json']
    names=['BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE',
           'BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE',
           'BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR',
           'BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT',
           'BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND',
           'BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN']
    paths.extend(BASE/(n+'.json') for n in names)
    ledger=json.loads(paths[9].read_bytes())['graded_operator_ledger']
    out.mkdir(parents=True,exist_ok=False)
    arrays={name+'_value':arb_mat([[value]]) for name,value in values.items()}
    arrays.update({name+'_first_73':jet for name,jet in jets.items()})
    arrays['native_trace_log_radius_replay']=replay
    save_arrays(out/'arrays.npz',arrays)
    report=dict(status='CURRENT_SPECTRAL_COEFFICIENT_FIRST_JETS_CLOSED_HISTORY_BASE_TRANSPORT_REQUIRED',
        branch_of_decision='B: owned finite-N law; current joint-history numerical realization incomplete, not absent physics',
        coefficient_values={k:interval(v) for k,v in values.items()},
        first_jet_norms={k:bound(v) for k,v in jets.items()},
        trace_binding_replay=bound(replay),
        old_family_log_R4=dict(lower=float(old_lo),upper=float(old_hi)),
        current_minus_old_global_upper=interval(separation),
        old_family_contains_current_point=False,
        operator_law=dict(
            element='K=S/h + mu^2*exp(-2*xmid)*h*A/6 [+ epsilon*mu*exp(-xmid)*C for product Dirac]; M=h*A/6',
            scalar='mu=m; HS m>=1 and transverse gauge m>=2',
            Weyl='mu=n+3/2; preserve owned chirality decomposition without doubling multiplicity',
            form_jet='dK=K_xmid*(dx_left+dx_right)/2+K_h*dh; dM=A*dh/6; add owned seam-contact jet once',
            self_adjointness='Real symmetric K,M with positive durations; both exterior Dirichlet nodes removed; one internal seam',
            spectral_operator='Generalized pencil K-lambda*M, not K alone',
            heat='-1/2 STr E1(ell_kappa^2 P); ell_kappa=1 in retained units',
            reference='Retained E0 Dirichlet source/domain, fixed reference derivative; subtract existing Gamma_SM_zeta once',
            second_operator_jet_computed=False),
        grading=ledger,
        dependencies=[
            dict(ingredient='Current node13 state and 73D chart',status='OWNED_NUMERICALLY'),
            dict(ingredient='Current spectral coefficients and first 73D jets',status='OWNED_NUMERICALLY'),
            dict(ingredient='Retained finite-element joint law, grading, regulator and zero-mode quotient',status='OWNED_SYMBOLICALLY'),
            dict(ingredient='Old 1222 path, first element jets and transposed-duration actions',status='BOUND_AVAILABLE',scope='Historical family, disjoint coefficient base'),
            dict(ingredient='Current incoming/C2 coefficient histories and their launch pullback',status='OWNED_SYMBOLICALLY',scope='Require current-base propagation/binding; old enclosures cannot be transplanted'),
            dict(ingredient='Gauge/scalar contact law and covariant reset transport',status='OWNED_SYMBOLICALLY'),
            dict(ingredient='Historical full graded heat and direct zeta covectors',status='BOUND_AVAILABLE',scope='Do not transfer historical heat suppression to current node13'),
        ],
        physical_owner_absence_claimed=False,
        complete_joint_operator_instantiated=False,complete_seven_response=None,
        seven_adjoint_residuals=None,rank_complete=None,history_correction_norm=None,
        second_jet_scope='First force Tr(Q dP) uses only dP. Differentiating a force requires DQ[P_b]P_a+Q P_ab unless an owned cancellation eliminates it; no second jet computed here.',
        current_history_needed='Bind/propagate incoming and child coefficient paths and first pullbacks at current node13, with positive owned durations and seam contact values; retain historical 1222 enclosures in their original base.',
        action_producers_run=False,local_native_derivative_recomputed=False,historical_test_covectors_run=False,
        expensive_1222_rows_recomputed=False,heat_seed_set_to_zero=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','coefficient_values','trace_binding_replay','current_minus_old_global_upper')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);calculate(p.parse_args().out)
