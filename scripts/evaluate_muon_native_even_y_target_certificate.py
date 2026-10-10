"""Replay the actual reached finite-core Y² heat and raw228 target enclosure."""
from __future__ import annotations
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_native_even_y_target_certificate import retained_target_certificate
from evaluate_muon_native_product_factor_graph import deterministic_npz,array_record


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--precision-bits',type=int,default=192);args=p.parse_args()
    output=args.output if args.output.is_absolute() else ROOT/args.output
    if output.exists():raise FileExistsError('preserve previous target certificates; choose a new output')
    names=('src/bhsm/interface/muon_native_even_y_target_certificate.py',
        'scripts/evaluate_muon_native_even_y_target_certificate.py',
        'src/bhsm/interface/muon_native_even_y_remainder_certificate.py',
        'src/bhsm/interface/muon_native_coupled_source_heat.py',
        'src/bhsm/interface/muon_native_product_factor_graph.py',
        'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
        'src/bhsm/interface/muon_native_mean_core_heat_target.py',
        'scripts/evaluate_muon_native_product_factor_graph.py')
    records=[]
    for name in names:
        raw=(ROOT/name).read_bytes();records.append(dict(path=name,bytes=len(raw),sha256=sha256(raw).hexdigest(),
            symbols={n.name:dict(line=n.lineno,end_line=n.end_lineno) for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}))
    packet,arrays=retained_target_certificate(repository=ROOT,precision_bits=args.precision_bits)
    for row in records:
        if sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('target source changed during replay')
    archive=deterministic_npz(arrays);packet.update(source_records=records,array_records={k:array_record(v) for k,v in arrays.items()},
        bound_archive=dict(path='target_bounds.npz',bytes=len(archive),sha256=sha256(archive).hexdigest()))
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();output.mkdir(parents=True)
    (output/'target_certificate.json').write_bytes(raw);(output/'target_bounds.npz').write_bytes(archive)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive_sha256=sha256(archive).hexdigest(),
        paired_value_interval=[packet['actual_FE_paired_Y2_value_lower'],packet['actual_FE_paired_Y2_value_upper']],
        maximum_target_reference_mismatch_upper=float(arrays['actual_FE_Y2_target_reference_difference_upper'].max())),sort_keys=True))


if __name__=='__main__':main()
