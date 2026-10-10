"""Apply the charged current to unchanged actual coupled midpoint cells."""
from __future__ import annotations
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_primal_charged_current_response import retained_current_response
from evaluate_muon_reached_trace_action import deterministic_archive


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output if a.output.is_absolute() else ROOT/a.output
    if out.exists():raise FileExistsError('preserve earlier current applications')
    names=['src/bhsm/interface/muon_primal_charged_current_response.py','scripts/evaluate_muon_primal_charged_current_response.py',
        'src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py','src/bhsm/interface/muon_native_dirac_hamiltonian.py',
        'src/bhsm/interface/muon_pointwise_full_field_action.py','src/bhsm/interface/muon_birth_coupled_primal_midpoint.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py','src/bhsm/interface/muon_parent_gauge_geometry_correction.py',
        'src/bhsm/interface/ae31_c2_coexact_su2l_charged_current.py']
    refs=[]
    for name in names:
        data=(ROOT/name).read_bytes();refs.append(dict(path=name,bytes=len(data),sha256=sha256(data).hexdigest(),
            symbols={n.name:dict(line=n.lineno,end_line=n.end_lineno) for n in ast.parse(data).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}))
    packet=retained_current_response(ROOT);arrays={}
    def extract(value,key):
        if isinstance(value,np.ndarray):arrays[key]=value;return dict(array_key=key)
        if isinstance(value,dict):return {k:extract(v,key+'_'+k) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [extract(v,key+'_'+str(i)) for i,v in enumerate(value)]
        if isinstance(value,np.generic):return value.item()
        return value
    result=extract(packet,'current');result['source_records']=refs
    for row in refs:
        if sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('current action changed during replay')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    archive=(out/'application.npz').read_bytes();result['array_sha256']=sha256(archive).hexdigest()
    result['array_records']={k:dict(shape=list(v.shape),dtype=str(v.dtype),raw_sha256=sha256(np.ascontiguousarray(v).tobytes()).hexdigest()) for k,v in arrays.items()}
    raw=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(out/'result.json').write_bytes(raw)
    print(json.dumps(dict(receipt_bytes=len(raw),receipt_sha256=sha256(raw).hexdigest(),archive_bytes=len(archive),archive_sha256=result['array_sha256'],
        arms=[dict(side=v['side'],frame_difference=v['named_frame_pairing_absolute_difference'],
            exact_stored_adjoint_identity=[r['exact_stored_certificate']['source_adjoint_intervals_overlap'] for r in v['applications']]) for v in packet['arms']]),sort_keys=True))


if __name__=='__main__':main()
