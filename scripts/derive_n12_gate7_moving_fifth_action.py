"""Enclose the fifth-action leaf with the certified moving eigenpair.

This changes the operands of the frozen fixed-leg probe. It does not supply
the separate derivatives of the moving legs in the complete physical jet.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,fmpq,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_uniform_fifth_action_prototype as first
from bhsm.interface.shared_action_taylor import TaylorDomain


def run(eigen_path,out):
    ctx.prec=512
    eigen=json.loads(eigen_path.read_bytes())
    if eigen['algorithm']!='SHARED_AFFINE_EIGENPAIR_FROM_FROZEN_CONTRACTION_V1' or eigen['endpoint']!=19:
        raise ValueError('certified shared endpoint-19 eigenpair required')
    seed_path=ROOT/'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed=json.loads(seed_path.read_bytes())
    if eigen['radius_exact']!=seed['radius_exact']:
        raise ValueError('unchanged original state radii required')
    sources=[Path(p) for p in seed['source_SHA256'] if p.replace('\\','/').endswith('endpoint_019/eigenpair.npz')]
    if len(sources)!=1:raise ValueError('one reconciled original state operand required')
    with np.load(sources[0],allow_pickle=False) as z:
        def read(name):
            m,r=z[name+'_mid_q'],z[name+'_rad_q']
            return np.array([arb(fmpq(str(a)))+arb(0,arb(fmpq(str(b))))
                for a,b in zip(m.flat,r.flat,strict=True)],dtype=object).reshape(m.shape)
        center,directions=read('center_state'),read('affine_directions')
    weights_path=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
    with np.load(weights_path,allow_pickle=False) as z:
        weights=[arb(float(v)) for v in z['state_weights']]
    rL,rT=[arb(fmpq(v)) for v in seed['radius_exact']]
    groups=[g for s in (0,75,150) for g in ((s,s+1,'interval'),(s+1,s+75,'euclidean'))]
    groups.append((225,287,'box'))
    domain=TaylorDomain(groups,287)
    scaled=[[directions[i,j]*(rL if j==0 else rT) for j in range(75)] for i in range(98)]
    state=[domain.affine(center[i],scaled[i]+[arb(0)]*212) for i in range(98)]
    u=[domain.affine(0,[arb(0)]*75+scaled[i]+[arb(0)]*137) for i in range(98)]
    v=[domain.affine(0,[arb(0)]*150+scaled[i]+[arb(0)]*62) for i in range(98)]
    def restore(pair):return arb(fmpq(pair[0]))+arb(0,arb(fmpq(pair[1])))
    moving=[]
    for i in range(62):
        coefficients=[restore(pair) for pair in eigen['coefficients'][i]]+[arb(0)]*212
        coefficients[225+i]=arb(fmpq(eigen['remainder_upper'][i]['exact']))
        moving.append(domain.affine(restore(eigen['center'][i]),coefficients))
    p=[domain.affine(0)]*37+moving[:61]
    rw=first.action.metric_data()[1]
    a=[domain.affine(0)]*37+[moving[i]*arb(float(rw[i]))/weights[37+i] for i in range(61)]
    value,inertia=first.producer.contract(first.action,state,[p,p,a,u,v],
        lambda done,total:print(json.dumps(dict(phase='NEW_MOVING_D5',completed=done,total=total)),flush=True))
    if not value.c.is_zero() or any(not a.is_zero() for a in value.a.entries()):
        raise ArithmeticError('bilinear direction origin must have zero constant/first jet')
    payload=dict(algorithm='SHARED_FIFTH_ACTION_MOVING_EIGENPAIR_V1',endpoint=19,
        derivative='D5 S(x(theta))[p(theta),p(theta),a(theta),D_r*u,D_r*v]',
        parameters=287,groups=groups,radius_exact=seed['radius_exact'],
        uniform_absolute_upper=first.number(value.support()),inertia_lower=first.number(inertia),
        same_eigenpair_error_parameters_reused_in_all_legs=True,
        all_original_L_T_input_pairs_enclosed=True,moving_eigenvector_values_enclosed=True,
        moving_eigenvector_derivatives_enclosed=False,complete_physical_Hessian_enclosed=False,
        limitation='Only the highest-action leaf; mixed moving-leg derivatives and physical composition are not enclosed.',
        source_SHA256={str(p.resolve()):first.sha(p) for p in (eigen_path,seed_path,Path(__file__),Path(first.producer.__file__))},
        inherited_operand_receipt=seed['source_SHA256'],global_feasibility_established=False,
        kappa_L=None,kappa_T=None,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(payload,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(moving_action_leaf=payload['uniform_absolute_upper'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--eigenpair',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.eigenpair.resolve(),a.out.resolve())
