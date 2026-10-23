#!/usr/bin/env python
"""Execute paired finite retarded/advanced tests on actual central matrices."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_parent_hypercharge_advanced_probe import boundary_probe_on_support
from bhsm.interface.muon_parent_retarded_hypercharge import _deterministic_npz


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    source=ROOT/'artifacts/muon_parent_retarded_hypercharge_20261010/canonical_run_2/run_2.npz'
    receipt=ROOT/'artifacts/muon_parent_retarded_hypercharge_20261010/canonical_run_2/result.json'
    duration=json.loads(receipt.read_text())['runs'][2]['source_duration']
    with np.load(source,allow_pickle=False) as z:
        matrices={k:np.array(z[k]) for k in ('M','N','K')}
    args.output.mkdir(parents=True,exist_ok=True)
    rows={}
    for reverse,label in ((False,'retarded'),(True,'advanced')):
        result=boundary_probe_on_support(**matrices,source_duration=duration,reversed_time=reverse)
        target=args.output/(label+'.npz')
        _deterministic_npz(target,{k:v for k,v in result.items() if isinstance(v,np.ndarray)})
        rows[label]={k:v for k,v in result.items() if not isinstance(v,np.ndarray)}
        rows[label]['npz_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
    paths=[source,receipt,ROOT/'src/bhsm/interface/muon_parent_hypercharge_advanced_probe.py',Path(__file__)]
    packet=dict(scope='FINITE_RETAINED_CENTRAL_BOUNDARY_ADJOINT_ON_SOURCE_SUPPORT',runs=rows,
        original_time_interval=[0,duration],radial_order=len(matrices['M'])-1,
        reciprocal_pairing_defect=abs(rows['retarded']['boundary_trace_contraction']-rows['advanced']['boundary_trace_contraction']),
        hashes=[dict(path=x.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(x.read_bytes()).hexdigest(),bytes=x.stat().st_size) for x in paths],
        continuum_error_evaluated=False,complete_native=False)
    target=args.output/'result.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        reciprocal_pairing_defect=packet['reciprocal_pairing_defect']),sort_keys=True))


if __name__=='__main__':main()
