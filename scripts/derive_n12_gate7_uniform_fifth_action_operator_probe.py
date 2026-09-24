"""Uniform bilinear fixed-eigenvector action leaf on the endpoint-19 tube.

The state and both input directions use their complete original product balls.
This supplies all input pairs for ONE action leaf, not the physical Hessian.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, fmpq, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_uniform_fifth_action_prototype as first
from bhsm.interface.shared_action_taylor import TaylorDomain


def run(seed_path, out):
    ctx.prec=512
    seed=json.loads(seed_path.read_bytes())
    if seed['algorithm']!='SHARED_ORIGINAL_DOMAIN_FIFTH_ACTION_CONTRACTION_V1' or seed['endpoint']!=19:
        raise ValueError('matching endpoint-19 action seed required')
    sources=[Path(p) for p in seed['source_SHA256'] if p.endswith('endpoint_019\\eigenpair.npz')
             or p.endswith('endpoint_019/eigenpair.npz')]
    if len(sources)!=1:
        raise ValueError('one original frozen state operand required')
    data=sources[0]
    # This newly composed producer consumes the seed boundary receipt and its
    # frozen operand binding; it does not traverse or rehash the input tree.
    with np.load(data,allow_pickle=False) as z:
        def read(name):
            m,r=z[name+'_mid_q'],z[name+'_rad_q']
            return np.array([arb(fmpq(str(a)))+arb(0,arb(fmpq(str(b))))
                for a,b in zip(m.flat,r.flat,strict=True)],dtype=object).reshape(m.shape)
        center,directions=read('center_state'),read('affine_directions')
    rL,rT=[arb(fmpq(v)) for v in seed['radius_exact']]
    groups=[(s,s+1,'interval') for s in ()]
    groups=[g for s in (0,75,150) for g in ((s,s+1,'interval'),(s+1,s+75,'euclidean'))]
    domain=TaylorDomain(groups,225)
    scaled=[[directions[i,j]*(rL if j==0 else rT) for j in range(75)] for i in range(98)]
    state=[domain.affine(center[i],scaled[i]+[arb(0)]*150) for i in range(98)]
    u=[domain.affine(0,[arb(0)]*75+scaled[i]+[arb(0)]*75) for i in range(98)]
    v=[domain.affine(0,[arb(0)]*150+scaled[i]) for i in range(98)]
    def restore(pair):return arb(fmpq(pair[0]))+arb(0,arb(fmpq(pair[1])))
    p,p2,a=[[restore(pair) for pair in leg] for leg in seed['raw_legs'][:3]]
    value,inertia=first.producer.contract(first.action,state,[p,p2,a,u,v],
        lambda done,total:print(json.dumps(dict(phase='NEW_D5_BILINEAR',completed=done,total=total)),flush=True))
    if not value.c.is_zero() or any(not a.is_zero() for a in value.a.entries()):
        raise ArithmeticError('bilinear direction origin must have zero constant and first jet')
    # This condition only checks that the fixed LL leaf is not contradicted;
    # it is not an independent reproduction of this new operator computation.
    if not value.support() >= arb(fmpq(seed['uniform_absolute_upper']['exact'])):
        raise ArithmeticError('unexpectedly smaller generic operator enclosure; inspect decomposition')
    payload=dict(algorithm='SHARED_FIFTH_ACTION_FIXED_LEG_BILINEAR_PROBE_V1',endpoint=19,
        derivative='D5 S(x(theta))[p0,p0,a0,D_r*u,D_r*v]',parameters=225,groups=groups,
        radius_exact=seed['radius_exact'],all_original_L_T_input_pairs_enclosed=True,
        independent_state_and_test_directions=True,shared_state_parameters_preserved=True,
        uniform_absolute_upper=first.number(value.support()),inertia_lower=first.number(inertia),
        representation='SIGNED_AFFINE_MODELS_WITH_CERTIFIED_NONLINEAR_TAILS',
        limitation='Bilinear test-direction terms enter the nonlinear tail; cancellation may be lost there.',
        seed_SHA256=first.sha(seed_path),original_operand_boundary_receipt=seed['source_SHA256'],
        producer_SHA256={str(p.resolve()):first.sha(p) for p in (Path(__file__),Path(first.__file__),Path(first.producer.__file__))},
        moving_eigenvector_legs_enclosed=False,implicit_second_variations_enclosed=False,
        complete_physical_Hessian_enclosed=False,global_feasibility_established=False,
        kappa_L=None,kappa_T=None,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    with out.open('x',encoding='utf8',newline='\n') as stream:
        stream.write(json.dumps(payload,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(uniform_action_leaf=payload['uniform_absolute_upper'],global_feasibility_established=False)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();run(args.seed.resolve(),args.out.resolve())
