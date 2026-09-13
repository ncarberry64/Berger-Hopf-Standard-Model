"""Independently reproduce a fixed, single-direction signed Hessian pilot."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',type=Path,required=True)
    parser.add_argument('--repeat-out',type=Path,required=True);args=parser.parse_args()
    record=json.loads((args.pilot/'direct/record.json').read_bytes())
    if record['report'].get('complete_signed_mixed_line_and_response_residuals_used') is not True:
        raise ValueError('complete signed mixed physical Hessian diagnostic required')
    args.repeat_out.mkdir(parents=True,exist_ok=False)
    producer=ROOT/'scripts/diagnose_n12_gate7_signed_mixed_uniform_hessian.py'
    normalizer=ROOT/'scripts/diagnose_n12_gate7_saved_coupled_hessian_normalization_v2.py'
    binding={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (Path(__file__),producer,normalizer)}
    try:
        subprocess.run([sys.executable,str(producer),'--endpoint',str(record['endpoint']),
            '--column',str(record['column']),'--out',str(args.repeat_out/'direct')],cwd=ROOT,check=True)
        # Both normalizations use the identical original saved source. Its
        # independent direct recomputation is separately compared below.
        subprocess.run([sys.executable,str(normalizer),'--source',str(args.pilot/'direct'),
            '--out',str(args.repeat_out/'normalized')],cwd=ROOT,check=True)
        files={}
        for rel in ('direct/record.json','direct/hessian.npz',
                    'normalized/record.json','normalized/normalized_hessian.npz'):
            first=args.pilot/rel;repeat=args.repeat_out/rel
            if first.read_bytes()!=repeat.read_bytes():raise ArithmeticError('independent reproduction differs: '+rel)
            files[rel]=sha(first)
        for rel,expected in binding.items():
            if sha(ROOT/rel)!=expected:raise ArithmeticError('reproduction driver source changed')
        receipt=dict(independent_recomputation=True,byte_identical=True,files_SHA256=files,
            driver_sources_SHA256=binding,endpoint=record['endpoint'],column=record['column'],
            scope='ONE_SCALED_LONGITUDINAL_DIRECTION_AND_ONE_TRANSVERSE_COLUMN_ON_ENDPOINT_TUBE',
            full_affine_direction_coverage=False,full_path_uniform_contraction=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
        with (args.pilot/'reproduction.json').open('xb') as stream:
            stream.write((json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode())
        print(json.dumps(receipt),flush=True)
    except BaseException as error:
        (args.repeat_out/'failure.json').write_text(json.dumps(dict(error=repr(error),
            evidence_preserved=True,FULL_BHSM_COMPLETE=False),indent=2)+'\n',encoding='utf-8')
        raise


if __name__=='__main__':main()
