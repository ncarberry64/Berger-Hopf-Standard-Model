"""New fifth-action contraction on the frozen endpoint-19 original domain.

No point Hessian, eigenpair or physical first variation is recomputed.
Only the listed boundary operands are hashed, once per independent run.
"""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, fmpq, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_accepted_replay_center_outward_74d as action
from bhsm.interface import uniform_action_contraction as producer
from bhsm.interface.shared_action_taylor import TaylorDomain


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pair(value):
    return [str(value.mid().fmpq()), str(value.rad().fmpq())]


def number(value):
    return dict(exact=str(value.fmpq()), approximate=float(value))


def run(evidence, out):
    ctx.prec = 512
    package = ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923'
    record_path = package/'certificate_headers/.affine_eigenpair_pilot_work/endpoint_019/record.json'
    data_path = evidence/'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_019/eigenpair.npz'
    ledger_path = package/'current_history_budget.json'
    weights_path = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
    record = json.loads(record_path.read_bytes())
    ledger = json.loads(ledger_path.read_bytes())
    paths = [record_path, data_path, ledger_path, weights_path, Path(__file__),
             Path(action.__file__), Path(producer.__file__),
             ROOT/'src/bhsm/interface/factored_arb_integrand.py',
             ROOT/'src/bhsm/interface/shared_action_taylor.py',
             ROOT/'src/bhsm/interface/shared_parameter_residual.py',
             Path(sys.modules[action.metric_data.__module__].__file__),
             Path(sys.modules[action.standard_model_casimir_coefficient.__module__].__file__)]
    hashes = {str(p.resolve()): sha(p) for p in paths}
    if hashes[str(data_path.resolve())] != record['data_SHA256']:
        raise ValueError('imported scientific operand differs from frozen header')
    radii = [r['radius']['exact'] for r in ledger['rows']]
    if radii != [record['radius_longitudinal_rational'], record['radius_transverse_rational']]:
        raise ValueError('original current radii required')
    rL, rT = [arb(fmpq(v)) for v in radii]
    with np.load(data_path, allow_pickle=False) as z:
        def read(name):
            mids, rads = z[name+'_mid_q'], z[name+'_rad_q']
            values = [arb(fmpq(str(m)))+arb(0, arb(fmpq(str(r))))
                      for m, r in zip(mids.flat, rads.flat, strict=True)]
            return np.asarray(values, dtype=object).reshape(mids.shape)
        center, directions, eigen = read('center_state'), read('affine_directions'), read('eigenpair_center')
    if center.shape != (98,) or directions.shape != (98, 75) or eigen.shape != (62,):
        raise ValueError('complete frozen affine state and selected line required')
    with np.load(weights_path, allow_pickle=False) as z:
        weights = [arb(float(v)) for v in z['state_weights']]
    domain = TaylorDomain([(0, 1, 'interval'), (1, 75, 'euclidean')], 75)
    state = [domain.affine(center[i], [directions[i,j]*(rL if j == 0 else rT)
                                     for j in range(75)]) for i in range(98)]
    p = [arb(0)]*37+list(eigen[:61])
    rw = action.metric_data()[1]
    a = [arb(0)]*37+[arb(float(rw[i]))*p[37+i]/weights[37+i] for i in range(61)]
    u = [directions[i,0]*rL for i in range(98)]
    value, inertia_lower = producer.contract(action, state, [p,p,a,u,u],
        lambda done, total: print(json.dumps(dict(phase='NEW_D5_ACTION', completed=done,total=total)), flush=True))
    payload = dict(algorithm='SHARED_ORIGINAL_DOMAIN_FIFTH_ACTION_CONTRACTION_V1',
        endpoint=19, derivative='D5 S(x(theta))[p0,p0,a0,rL*dL,rL*dL]',
        definition='p0=(0,psi_center); a0=(0,W_reduced*psi_center/W_state); dL=frozen raw longitudinal direction',
        radius_exact=radii, parameters=75, groups=domain.groups,
        domain='x=x0+rL*dL*theta0+rT*D_T*thetaT; abs(theta0)<=1, norm2(thetaT)<=1',
        center_ball=pair(value.c), signed_linear_coefficients=[pair(v) for v in value.a.entries()],
        signed_linear_support_upper=number(value.linear_bound()),
        nonlinear_model_remainder_upper=number(value.r),
        uniform_absolute_upper=number(value.support()),
        variation_from_center_upper=number((value.linear_bound()+value.r).upper()),
        inertia_lower=number(inertia_lower), source_SHA256=hashes,
        raw_legs=[[pair(v) for v in leg] for leg in (p,p,a,u,u)],
        frozen_calculations_recomputed=False, current_domain_shrunk=False,
        global_inertia_and_boundary_included=True, shared_parameters_preserved=True,
        physical_eigenvector_leg_variation_included=False,
        complete_physical_Hessian_enclosed=False, all_direction_pairs_enclosed=False,
        kappa_L=None, kappa_T=None, full_history_campaign_authorized_by_probe=False,
        classification='ACTION_DERIVATIVE_LEAF_ONLY_NOT_GLOBAL_FEASIBILITY',
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:payload[k] for k in ('center_ball','uniform_absolute_upper',
        'variation_from_center_upper','nonlinear_model_remainder_upper','inertia_lower')}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.evidence_root.resolve(), args.out.resolve())
