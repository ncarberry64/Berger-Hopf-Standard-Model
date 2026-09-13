"""Fresh-process reproduction of the complete 75-direction diagnostic."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', type=Path, required=True)
    parser.add_argument('--repeat-out', type=Path, required=True)
    args = parser.parse_args()
    record_path = args.pilot / 'record.json'
    record = json.loads(record_path.read_bytes())
    if (record['report'].get('all_75_scaled_affine_tube_directions_enclosed') is not True
            or record['report'].get('all_75_point_columns_contained') is not True
            or record['data_SHA256'] != sha(args.pilot / 'hessian.npz')):
        raise ValueError('complete intact 75-direction pilot required')
    if args.repeat_out.exists() or (args.pilot / 'reproduction.json').exists():
        raise FileExistsError('preserve previous attempt and receipt')
    producer = ROOT / 'scripts/diagnose_n12_gate7_affine_basis_uniform_hessian.py'
    binding = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
               for p in (Path(__file__), producer)}
    original = {name: sha(args.pilot / name) for name in ('record.json', 'hessian.npz')}
    try:
        subprocess.run([sys.executable, str(producer), '--endpoint', str(record['endpoint']),
                        '--column', str(record['column']), '--out', str(args.repeat_out)],
                       cwd=ROOT, check=True)
        for name, expected in original.items():
            if sha(args.pilot / name) != expected or sha(args.repeat_out / name) != expected:
                raise ArithmeticError('independent reproduction differs: ' + name)
            if (args.pilot / name).read_bytes() != (args.repeat_out / name).read_bytes():
                raise ArithmeticError('independent bytes differ: ' + name)
        for rel, expected in binding.items():
            if sha(ROOT / rel) != expected:
                raise ArithmeticError('reproduction driver source changed')
        receipt = dict(independent_recomputation=True, fresh_process=True, byte_identical=True,
                       files_SHA256=original, driver_sources_SHA256=binding,
                       endpoint=record['endpoint'], column=record['column'],
                       full_affine_direction_coverage=True, full_physical_input_basis=False,
                       same_family_segment_smoothness_consumer_completed=False,
                       candidates_consumed_by_production=False,
                       full_path_uniform_contraction=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
        with (args.pilot / 'reproduction.json').open('xb') as stream:
            stream.write((json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode())
        print(json.dumps(receipt), flush=True)
    except BaseException as error:
        args.repeat_out.mkdir(parents=True, exist_ok=True)
        with (args.repeat_out / 'reproduction_failure.json').open('x', encoding='utf-8') as stream:
            json.dump(dict(error=repr(error), evidence_preserved=True, FULL_BHSM_COMPLETE=False), stream, indent=2)
        raise


if __name__ == '__main__':
    main()
