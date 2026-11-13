"""Checkpoint a source-restricted affine current derivative, preserving nonpasses."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from bhsm.interface.muon_causal_operator_current_derivative import affine_current_derivative
from bhsm.interface.retained_response.field_spin_connection import (
    OpenFieldPath,field_vertices,verify_inputs,verify_application_result,
)
from bhsm.interface.retained_response.finite_time_response import evolve,interpolate,write_npz

ROOT=Path(__file__).resolve().parents[1]
FIELD=ROOT/'artifacts/muon_retained_response_20261018'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path,value):
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    tmp.replace(path)


def load_arrays(path):
    with np.load(path,allow_pickle=False) as f:
        return {k:f[k].copy() for k in f.files}


def main(out,resume):
    verify_inputs();verify_application_result(FIELD/'run_A')
    identities={name:digest(ROOT/name) for name in (
        'src/bhsm/interface/muon_causal_operator_wall_current.py',
        'src/bhsm/interface/muon_causal_operator_current_derivative.py',
        'scripts/evaluate_muon_causal_operator_current_derivative.py',
        'artifacts/muon_retained_response_20261018/inputs/PROVENANCE.json')}
    if out.exists() and not resume:
        raise FileExistsError('completed/interrupted output exists; use --resume')
    out.mkdir(parents=True,exist_ok=resume)
    checkpoint=out/'CHECKPOINT.json'
    if resume:
        state=json.loads(checkpoint.read_text())
        if state['input_code_sha256']!=identities:
            raise ValueError('input/code identity changed; review only affected applications')
    else:
        state=dict(input_code_sha256=identities,sides={},
            physical_total_derivative_admitted=False,
            NEXT_OPERAND='Complete this declared finite affine response check; physical source/domain/reference/interface derivative remains separate.')
        json_write(checkpoint,state)
    for side in ('incoming','outgoing'):
        record=state['sides'].setdefault(side,dict(events={}))
        for event,item in record['events'].items():
            if digest(out/item['path'])!=item['sha256']:
                raise ValueError('saved event changed: '+side+'/'+event)
        if record.get('completed'):
            report_path=out/record['report_path']
            if digest(report_path)!=record['report_sha256']:
                raise ValueError('completed report changed: '+side)
            print(side+' reused completed derivative applications',flush=True)
            continue
        folder=out/side;folder.mkdir(exist_ok=True)
        def save(event,arrays,metadata):
            file=folder/(event+'.npz')
            write_npz(file,arrays)
            record['events'][event]=dict(path=file.relative_to(out).as_posix(),
                sha256=digest(file),metadata=metadata)
            json_write(checkpoint,state)
            print(side+' saved '+event,flush=True)
        cache={}
        for event,item in record['events'].items():
            if event.startswith('finite_affine_'):
                cache[event.removeprefix('finite_affine_')]=dict(
                    arrays=load_arrays(out/item['path']),metadata=item['metadata'])
        analytic=None
        key='analytic_affine_current_derivative'
        if key in record['events']:
            item=record['events'][key]
            analytic=dict(arrays=load_arrays(out/item['path']),metadata=item['metadata'])
        path=OpenFieldPath(side);U=evolve(path.history)
        arrays,report,_=affine_current_derivative(path,U,field_vertices()['V'],interpolate,
            checkpoint=save,finite_cache=cache,analytic_cache=analytic)
        target=folder/'result.json';json_write(target,report)
        record.update(completed=True,report_path=target.relative_to(out).as_posix(),report_sha256=digest(target))
        json_write(checkpoint,state)
        print(side+' completed affine current derivative; physical total derivative remains unadmitted',flush=True)
    json_write(out/'result.json',state)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args();main(a.output.resolve(),a.resume)
