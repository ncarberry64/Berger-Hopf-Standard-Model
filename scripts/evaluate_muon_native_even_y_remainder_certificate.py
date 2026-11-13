"""Replay the actual finite FE even-Y tail certificate; no field producer."""
from __future__ import annotations
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.muon_native_even_y_remainder_certificate import retained_certificate
from evaluate_muon_native_product_factor_graph import deterministic_npz, array_record


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--precision-bits', type=int, default=192); args = p.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists(): raise FileExistsError('preserve previous certificates; choose a new output')
    paths = ('src/bhsm/interface/muon_native_even_y_remainder_certificate.py',
        'scripts/evaluate_muon_native_even_y_remainder_certificate.py')
    records = []
    for name in paths:
        raw = (ROOT / name).read_bytes()
        records.append(dict(path=name, bytes=len(raw), sha256=sha256(raw).hexdigest(),
            symbols={n.name: dict(line=n.lineno, end_line=n.end_lineno) for n in ast.parse(raw).body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}))
    packet, arrays = retained_certificate(repository=ROOT, precision_bits=args.precision_bits)
    for item in records:
        if sha256((ROOT / item['path']).read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('certificate source changed during replay')
    archive = deterministic_npz(arrays)
    packet.update(source_records=records, array_records={k: array_record(a) for k, a in arrays.items()},
        bound_archive=dict(path='remainder_bounds.npz', bytes=len(archive), sha256=sha256(archive).hexdigest()))
    raw = (json.dumps(packet, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
    output.mkdir(parents=True)
    (output / 'remainder_bounds.npz').write_bytes(archive)
    (output / 'remainder_certificate.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(), archive_sha256=sha256(archive).hexdigest(),
        value_tail_upper=packet['tail_certificate']['value_tail_upper']['upper_binary64'],
        constant_directional_tail_max=float(max(arrays['constant_directional_tail_upper']))), sort_keys=True))


if __name__ == '__main__': main()
