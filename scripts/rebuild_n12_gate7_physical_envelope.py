"""Recompose a physical aggregate using unchanged producers and locked inputs."""
import argparse
import importlib
import inspect
import json
from pathlib import Path
import sys


def main(stage, out):
    root=Path(__file__).resolve().parents[1]
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    names={'first':'certify_n12_gate7_physical_first_causal_envelope',
           'incidence':'certify_n12_gate7_physical_incidence_causal_envelope'}
    producer=importlib.import_module(names[stage])
    import bhsm_immutable_input_hash_cache as cache
    targets=[]
    for module in tuple(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if not path or not Path(path).resolve().is_relative_to(root):continue
        for name in ('sha','_sha','file_sha'):
            value=getattr(module,name,None)
            if callable(value) and len(inspect.signature(value).parameters)==1:
                targets.append((module,name))
    with cache.cache_hashes(targets,excluded_roots=[out.parent]) as stats:
        payload=producer.build_payload()
        if not payload['validation_passed'] or not payload['coverage']['complete']:
            raise ValueError('Complete validated composition required')
        if payload['claim_boundary']['Gate7_closed']:
            raise ValueError('This scoped aggregate cannot close Gate 7')
        with out.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(json.dumps(payload,sort_keys=True,indent=2)+'\n')
        print(json.dumps({'stage':stage,'complete':True,'coverage':payload['coverage'],'hash_cache':stats}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=('first','incidence'),required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();main(args.stage,args.out.resolve())
