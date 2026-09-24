"""Derive an affine eigenpair enclosure from frozen Banach/mean-value data.

No action, branch, point Hessian or fixed fifth-action probe is recomputed.
The affine value enclosure is explicitly NOT an eigenpair derivative jet.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,fmpq,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.shared_parameter_residual import linear_support


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def pair(v):return [str(v.mid().fmpq()),str(v.rad().fmpq())]
def bound(v):return dict(exact=str(v.upper().fmpq()),approximate=float(v.upper()))


def run(evidence,out):
    ctx.prec=512
    package=ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923'
    path=package/'certificate_headers/.affine_eigenpair_pilot_work/endpoint_019/record.json'
    frozen=json.loads(path.read_bytes())
    seed=ROOT/'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed_record=json.loads(seed.read_bytes())
    data=evidence/'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_019/eigenpair.npz'
    # The existing scalar boundary receipt already imports this exact operand.
    if seed_record['source_SHA256'][str(data.resolve())]!=frozen['data_SHA256']:
        raise ValueError('frozen operand receipts must agree')
    with np.load(data,allow_pickle=False) as z:
        def read(name):
            m,r=z[name+'_mid_q'],z[name+'_rad_q']
            return np.array([arb(fmpq(str(a)))+arb(0,arb(fmpq(str(b)))) for a,b in zip(m.flat,r.flat,strict=True)],dtype=object).reshape(m.shape)
        y0,R,D,A=[read(n) for n in ('eigenpair_center','preconditioner','center_defect','signed_residual_derivatives')]
        selected=[i for i,t in enumerate(frozen['report']['trials']) if t['validation_passed']]
        if len(selected)!=1:raise ValueError('one frozen successful contraction required')
        w=read(f'trial_{selected[0]}_radii');V=read(f'trial_{selected[0]}_variation_bounds')
    proof=frozen['report']['point_eigenpair_proof']
    witness=[arb(fmpq(m))+arb(0,arb(fmpq(r))) for m,r in zip(proof['target_midpoints_rational'],proof['target_radii_rational'],strict=True)]
    eps=[abs(a-b).upper() for a,b in zip(witness,y0,strict=True)]
    # 0=RF(y0)+(I-D)e+R*(-e_lambda*e_psi, ||e_psi||^2/2).
    nonlinear=[eps[-1]*e for e in eps[:-1]]+[sum((e*e for e in eps[:-1]),arb(0))/2]
    residual0=[sum((abs(arb(i==j)-D[i,j]).upper()*eps[j]+abs(R[i,j]).upper()*nonlinear[j]
                   for j in range(62)),arb(0)).upper() for i in range(62)]
    radii=seed_record['radius_exact'];rL,rT=[arb(fmpq(v)) for v in radii]
    groups=[(0,1,'interval'),(1,75,'euclidean')]
    coefficients=[];tails=[]
    for i in range(62):
        scaled=[A[i,j]*(rL if j==0 else rT) for j in range(75)]
        coefficients.append([-a.mid() for a in scaled])
        tails.append((residual0[i]+linear_support([a.rad() for a in scaled],groups)+V[i]).upper())
    q=max((a/b).upper() for a,b in zip(V,w,strict=True))
    if not q<1:raise ArithmeticError('frozen joint inverse defect does not close')
    result=dict(algorithm='SHARED_AFFINE_EIGENPAIR_FROM_FROZEN_CONTRACTION_V1',endpoint=19,
        radius_exact=radii,groups=groups,parameters=75,center=[pair(v) for v in y0],
        coefficients=[[pair(v) for v in row] for row in coefficients],
        remainder_upper=[bound(v) for v in tails],center_equation_residual_upper=[bound(v) for v in residual0],
        weighted_inverse_defect_upper=bound(q),frozen_inverse_weights=[pair(v) for v in w],
        maximum_eigenvector_remainder_upper=bound(max(tails[:-1])),
        eigenvalue_remainder_upper=bound(tails[-1]),
        proof_identity='y(theta)=y0-RF(y0,theta)+Ebar(theta)*(y(theta)-y0); abs(Ebar)*w<=V',
        common_parameters_preserved=True,point_witness_reused=True,branch_recomputed=False,
        derivative_jet_certified=False,mixed_eigenvector_variation_enclosed=False,
        source_SHA256={str(p.resolve()):sha(p) for p in (path,seed,Path(__file__),Path(sys.modules[linear_support.__module__].__file__))},
        inherited_operand_receipt=seed_record['source_SHA256'],Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('maximum_eigenvector_remainder_upper','eigenvalue_remainder_upper','weighted_inverse_defect_upper')}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.out.resolve())
