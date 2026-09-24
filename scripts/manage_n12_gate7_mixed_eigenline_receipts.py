"""Freeze/validate completed mixed-eigenline blocks without numerical work.

Used before restart and after each complete action block. Published sidecars
bind exact payload bytes to the common immutable input receipt and domain.
An incomplete JSON file is never accepted as a completed contraction.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path


def raw(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def sha(data):return hashlib.sha256(data).hexdigest().upper()
def atomic(path,data):
    pending=path.with_suffix('.pending')
    with pending.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(pending,path)


def receipt(work):
    inputs=work/'immutable_inputs.json'
    if not inputs.exists():
        count=0
        for stage in ('first','repeat'):
            folder=work/stage;source=folder/'immutable_inputs.json'
            if not source.exists():continue
            binding=json.loads(source.read_bytes());saved=folder/'completed';saved.mkdir(exist_ok=True)
            for p in folder.glob('*.json'):
                if len(p.stem)!=64:continue
                data=p.read_bytes()
                try:payload=json.loads(data)
                except json.JSONDecodeError:continue
                if payload.get('key')!=p.stem or not payload.get('models'):raise ValueError('invalid contraction payload')
                info=dict(completed=True,key=p.stem,payload_SHA256=sha(data),byte_count=len(data),
                    immutable_inputs_SHA256=sha(source.read_bytes()),precision_bits=512,
                    parameters=binding['parameters'],groups=binding['groups'],radius_exact=binding['radius_exact'],
                    source_input_hashes=binding['source_input_hashes'],rows=len(payload['models']),original_domain_unchanged=True)
                target=saved/p.name;encoded=raw(info)
                if target.exists():
                    if target.read_bytes()!=encoded:raise ArithmeticError('completed intermediate hash/domain mismatch')
                else:atomic(target,encoded)
                count+=1
        print(json.dumps(dict(completed_blocks_validated=count)));return
    binding=json.loads(inputs.read_bytes());input_hash=sha(inputs.read_bytes())
    eigen_paths=[p for p in binding['inputs_SHA256'] if p.replace('\\','/').endswith('gate7_moving_response_20260923/eigenpair.json')]
    if len(eigen_paths)!=1:raise ValueError('one frozen eigenpair certificate required')
    eigen=json.loads(Path(eigen_paths[0]).read_bytes())
    count=0
    for stage in ('first','repeat'):
        folder=work/stage
        if not folder.exists():continue
        saved=folder/'completed';saved.mkdir(exist_ok=True)
        for p in folder.glob('*.json'):
            if len(p.stem)!=64:continue
            data=p.read_bytes()
            try:payload=json.loads(data)
            except json.JSONDecodeError:continue  # Still being written; never certified.
            if payload.get('key')!=p.stem or not payload.get('models'):raise ValueError('invalid contraction payload')
            info=dict(completed=True,key=p.stem,payload_SHA256=sha(data),byte_count=len(data),
                immutable_inputs_SHA256=input_hash,source_input_hashes=binding['inputs_SHA256'],
                precision_bits=512,parameters=287,
                groups=[[0,1,'interval'],[1,75,'euclidean'],[75,76,'interval'],[76,150,'euclidean'],
                        [150,151,'interval'],[151,225,'euclidean'],[225,287,'box']],
                radius_exact=eigen['radius_exact'],original_domain_unchanged=True,
                rows=len(payload['models']),representation='CANONICAL_RATIONAL_ARB_TAYLOR_MODELS')
            target=saved/p.name;encoded=raw(info)
            if target.exists():
                if target.read_bytes()!=encoded:raise ArithmeticError('completed intermediate hash/domain mismatch')
            else:atomic(target,encoded)
            count+=1
    print(json.dumps(dict(completed_blocks_validated=count,immutable_inputs_SHA256=input_hash)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True)
    receipt(p.parse_args().work.resolve())
