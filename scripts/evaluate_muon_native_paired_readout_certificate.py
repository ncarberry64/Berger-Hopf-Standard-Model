"""Pair actual exported finite phases with the certified reached heat target."""
from __future__ import annotations
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_native_paired_readout_certificate import retained_paired_readout,retained_legacy_mesh_diagnostics
from evaluate_muon_native_product_factor_graph import serial


def main():
    p=argparse.ArgumentParser();p.add_argument('--phase-directory',type=Path,nargs='+',required=True)
    p.add_argument('--legacy-mesh-diagnostics',action='store_true')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision-bits',type=int,default=192);args=p.parse_args()
    out=args.output if args.output.is_absolute() else ROOT/args.output
    if out.exists():raise FileExistsError('preserve earlier finite readout certificates')
    names=('src/bhsm/interface/muon_native_paired_readout_certificate.py',
        'scripts/evaluate_muon_native_paired_readout_certificate.py',
        'src/bhsm/interface/muon_parent_mean_causal_descriptor.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py')
    refs=[]
    for name in names:
        raw=(ROOT/name).read_bytes();refs.append(dict(path=name,bytes=len(raw),sha256=sha256(raw).hexdigest(),
            symbols={n.name:dict(line=n.lineno,end_line=n.end_lineno) for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}))
    packet=retained_paired_readout(args.phase_directory,repository=ROOT,precision_bits=args.precision_bits)
    if args.legacy_mesh_diagnostics:packet['legacy_numeric_mesh_diagnostics']=retained_legacy_mesh_diagnostics(ROOT)
    for row in refs:
        if sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('readout source changed during replay')
    packet['source_records']=refs;raw=(json.dumps(serial(packet),indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    out.mkdir(parents=True);(out/'paired_readout.json').write_bytes(raw)
    print(json.dumps(dict(receipt_bytes=len(raw),receipt_sha256=sha256(raw).hexdigest(),
        finite_traces=[dict(steps=r['time_steps'],lower=r['paired_readout']['channel_trace_lower'],upper=r['paired_readout']['channel_trace_upper'])
            for r in packet['finite_applications']]),sort_keys=True))


if __name__=='__main__':main()
