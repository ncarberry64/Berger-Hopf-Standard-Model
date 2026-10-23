"""Freeze the unchanged ONE exact-stored302 attribution replay pair."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def main():
    base=ROOT/'artifacts/muon_exact_stored_reset_projection_20261012';out=base/'pair_verification'
    if out.exists():raise FileExistsError('preserve attribution verification')
    reports=[];files={};pins={}
    for number in (1,2):
        folder=base/f'run_{number}';report=json.loads((folder/'result.json').read_text());reports.append(report)
        for name,record in report['archives'].items():
            p=folder/name;b=p.read_bytes()
            if sha256(b).hexdigest()!=record['sha256']:raise ValueError('attribution archive changed')
            if number==2 and b!=(base/'run_1'/name).read_bytes():raise ValueError('attribution replay differs')
            files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        p=folder/'result.json';b=p.read_bytes()
        if number==2 and b!=(base/'run_1/result.json').read_bytes():raise ValueError('attribution receipts differ')
        files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        for p,h in report['input_hashes'].items():
            if p in pins and pins[p]!=h:raise ValueError('attribution input conflict')
            pins[p]=h
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('attribution source changed')
    for number in (1,2):
        p=ROOT/f'artifacts/muon_exact_stored_reset_projection_20261012_run_{number}.stdout.txt'
        files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    p=Path(__file__);files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    record=dict(classification='VERIFIED_ONE_STORED302_ATTRIBUTION_PAIR_NOT_A_PRECISION_CAMPAIGN',
        all_output_bytes_equal=True,input_pin_count=len(pins),files=files,input_hashes=pins,
        commands=[f'C:/Python314/python.exe scripts/evaluate_muon_exact_stored_reset_projection.py --output artifacts/muon_exact_stored_reset_projection_20261012/run_{number} --precision-bits 192'for number in(1,2)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        binary_original226_max=reports[0]['binary_original226_rows_max'],
        stored302_port_original226_max=reports[0]['exact_stored_port_original226_rows_max'],
        original_reset_tolerance_not_passed=True,physical_formation_or_cutoff_selected=False,
        scope='Only arithmetic of the same exact stored binary302 saddle/rhs/dual; source, action evaluation, reset base and physical domain excluded')
    out.mkdir();p=out/'verification.json';p.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),verification_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
