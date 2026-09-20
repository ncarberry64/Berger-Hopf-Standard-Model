"""Compare isolated-process contractions with an existing serial Taylor term."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def check(root,operands,predictors,serial,out):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(Path(__file__).resolve().parents[1]/'src/bhsm/interface'))
    from bhsm.interface.shared_action_taylor import TaylorDomain
    import n12_gate7_parallel_scalar_taylor as parallel
    ctx.prec=512;p=engine.p
    def load(folder,name):
        record=json.loads((folder/'record.json').read_bytes())
        if hashlib.sha256((folder/name).read_bytes()).hexdigest().upper()!=record['data_SHA256']:
            raise ValueError('Verified operand bytes required')
        with np.load(folder/name,allow_pickle=False) as z:
            return record,{k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
    ore,a=load(operands,'operands.npz');pre,s=load(predictors,'predictors.npz')
    if ore['report']['index']!=15 or pre['stage']!='endpoint':raise ValueError('Only endpoint 15')
    n=75;domain=TaylorDomain(pre['parameter_groups'],n)
    weights=p.values.operands()[1]
    state=[domain.affine(s['center_state'][i],[s['weighted_tube_directions'][i,j]/arb(float(weights[i])) for j in range(n)]) for i in range(98)]
    ep=[arb(v) for v in pre['point_checks'][0]['target_midpoints_rational']]
    psi=[domain.affine(ep[i].mid(),[s['point_solve_3'][i,j].mid() for j in range(n)]) for i in range(61)]
    legs={'v':[arb(0)]*37+list(a['paired_rm'][18,:61]),'psi':[arb(0)]*37+psi}
    old=json.loads(serial.read_bytes())
    out.mkdir(parents=True,exist_ok=False)
    parallel.precompute(root,domain,state,legs,[('replica_a',['v','psi']),('replica_b',['v','psi'])],old['binding'],out,2)
    copies=[json.loads((out/(name+'.json')).read_bytes()) for name in ('replica_a','replica_b')]
    if any(copy!=old for copy in copies):raise ArithmeticError('Worker/serial contraction differs')
    result=dict(serial_and_two_process_results_byte_identical=all((out/(name+'.json')).read_bytes()==serial.read_bytes()
        for name in ('replica_a','replica_b')),interval13_recomputed=False,physical_entry_certified=False)
    (out/'record.json').write_bytes(p.geometry.encoded(result));print(json.dumps(result),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','operands','predictors','serial','out'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    check(args.evidence_root.resolve(),args.operands.resolve(),args.predictors.resolve(),args.serial.resolve(),args.out.resolve())
