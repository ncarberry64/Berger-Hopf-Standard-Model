"""Compute pending independent scalar terms for the active base producer.

The exact original producer manifest and arithmetic are retained. A separate
receipt records this execution backend and each completed term's digest.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def prefetch(root,operands,predictors,out,start,workers):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(Path(__file__).resolve().parents[1]/'src/bhsm/interface'))
    from bhsm.interface.shared_action_taylor import TaylorDomain
    import n12_gate7_parallel_scalar_taylor as parallel
    ctx.prec=512;p=engine.p;cert=p.values.cert
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    sources=json.loads((out/'sources.json').read_bytes())
    if any(sha(Path(path))!=digest for path,digest in sources.items()):raise ValueError('Active producer source changed')
    binding=hashlib.sha256(p.geometry.encoded(sources)).hexdigest().upper()
    def load(folder,name):
        record=json.loads((folder/'record.json').read_bytes())
        if sha(folder/name)!=record['data_SHA256']:raise ValueError('Verified operand bytes required')
        for path in (folder/'record.json',folder/name):
            if sources.get(str(path.resolve()))!=sha(path):raise ValueError('Same active producer inputs required')
        with np.load(folder/name,allow_pickle=False) as z:
            return record,{k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
    ore,a=load(operands,'operands.npz');pre,s=load(predictors,'predictors.npz')
    if pre['interval']!=14:raise ValueError('Interval 14 only')
    n=s['weighted_tube_directions'].shape[1];domain=TaylorDomain(pre['parameter_groups'],n)
    _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
    weights,qw,rw=[[arb(float(v)) for v in values] for values in (weights,qw,rw)]
    state=[domain.affine(s['center_state'][i],[s['weighted_tube_directions'][i,j]/weights[i] for j in range(n)]) for i in range(98)]
    hard=[domain.affine(s['point_solve_0'][i,0].mid(),[s['point_solve_4'][i,j].mid() for j in range(n)]) for i in range(62)]
    pad=lambda v:[arb(0)]*37+list(v[:61])
    configuration=[qw[i]*state[37+i] for i in range(37)]
    legs=dict(hard=pad(hard),d=[configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61)
    tasks=[]
    for i in range(start,62):
        v=list(a['paired_rm'][i,:61]);legs[f'v{i}']=pad(v)
        legs[f'g{i}']=[v[j]*rw[j]*qw[j]/weights[j] for j in range(37)]+[arb(0)]*61
        legs[f'c{i}']=[arb(0)]*37+[v[j]*rw[j]/weights[37+j] for j in range(61)]
        tasks.extend([(f'response_{i:02d}_gradient',[f'g{i}']),
            (f'response_{i:02d}_source',[f'c{i}','d']),
            (f'response_{i:02d}_action',[f'v{i}','hard'])])
    backend={str(path.resolve()):sha(path) for path in (Path(__file__),Path(parallel.__file__))}
    parallel.precompute(root,domain,state,legs,tasks,binding,out,workers)
    if any(sha(Path(path))!=digest for path,digest in {**sources,**backend}.items()):raise ValueError('Source changed')
    receipt=dict(original_producer_binding=binding,backend_source_SHA256=backend,
        parameter_groups=domain.groups,original_domain_unchanged=True,interval13_recomputed=False,
        scalar_term_SHA256={name:sha(out/(name+'.json')) for name,_ in tasks},physical_entry_certified=False)
    with (out/'parallel_response_receipt.json').open('xb') as stream:stream.write(p.geometry.encoded(receipt))
    print(json.dumps(dict(prefetched_terms=len(tasks),complete=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','operands','predictors','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--start-row',type=int,required=True);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    prefetch(args.evidence_root.resolve(),args.operands.resolve(),args.predictors.resolve(),args.out.resolve(),args.start_row,args.workers)
