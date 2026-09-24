"""Reuse supported descriptor forms only after exact numerical circuit proof."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.quadratic_circuit_identity import verify_identity


def main():
    p=argparse.ArgumentParser()
    for name in ('descriptor-checkpoint','target-checkpoint','descriptor-report','out'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    a=json.loads(args.descriptor_checkpoint.read_bytes());b=json.loads(args.target_checkpoint.read_bytes())
    for key in ('graph_SHA256','parameter_order','groups','radius_exact'):
        if a[key]!=b[key]:raise ValueError('same frozen physical parameter domain required')
    names=[f'descriptor/J/uv/term{i}' for i in (13,3,8)]
    for name in names:
        for key in ('c','a','qb','tails'):
            if a['models'][name][key]!=b['models'][name][key]:raise ValueError('forward model mismatch: '+name+'/'+key)
    paths=[(p.parent/'quadratics.sqlite').resolve() for p in (args.descriptor_checkpoint,args.target_checkpoint)]
    dbs=[sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) for path in paths]
    proof=verify_identity(*dbs,[(a['models'][n]['q'],b['models'][n]['q']) for n in names],
                          progress=lambda s:print(s,flush=True))
    proof.update(descriptor_checkpoint_SHA256=hashlib.sha256(args.descriptor_checkpoint.read_bytes()).hexdigest().upper(),
                 target_checkpoint_SHA256=hashlib.sha256(args.target_checkpoint.read_bytes()).hexdigest().upper())
    proof_path=args.out.with_name(args.out.stem+'_reuse_proof.json')
    proof_path.write_text(json.dumps(proof,indent=2,sort_keys=True)+'\n')
    result=json.loads(args.descriptor_report.read_bytes())
    if result['checkpoint_SHA256']!=proof['descriptor_checkpoint_SHA256']:raise ValueError('supported descriptor source mismatch')
    result.update(scope='targets',stats=b['stats'],target_circuit_models=b['models'],
                  quadratic_circuit_file=str(paths[1]),
                  descriptor_support_reused_after_exact_circuit_identity=True,
                  reuse_proof_SHA256=hashlib.sha256(proof_path.read_bytes()).hexdigest().upper())
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(reused_after_exact_identity=True,verified_nodes=proof['reachable_nodes'])),flush=True)


if __name__=='__main__':main()
