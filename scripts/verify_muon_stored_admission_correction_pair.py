"""Verify the one bounded fixed stored148 admission-correction replay pair."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def main():
    base=ROOT/'artifacts/muon_stored_admission_correction_20261012';out=base/'pair_verification'
    if out.exists():raise FileExistsError('preserve bounded correction verification')
    files={}; pins={}; reports=[]
    for number in (1,2):
        folder=base/f'run_{number}'; p=folder/'result.json'; b=p.read_bytes(); md=json.loads(b);reports.append(md)
        if number==2 and b!=(base/'run_1/result.json').read_bytes():raise ValueError('replay correction receipt differs')
        files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        for name,record in md['archives'].items():
            p=folder/name;b=p.read_bytes()
            if sha256(b).hexdigest()!=record['sha256']:raise ValueError('correction archive digest changed')
            if number==2 and b!=(base/'run_1'/name).read_bytes():raise ValueError('replay correction arrays differ')
            files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        for rel,h in md['input_hashes'].items():
            if rel in pins and pins[rel]!=h:raise ValueError('unchanged system pin conflict')
            pins[rel]=h
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('fixed stored source pin changed')
    for name in ('artifacts/muon_stored_admission_correction_20261012_run_1.stdout.txt',
        'artifacts/muon_stored_admission_correction_20261012_run_2.stdout.txt',
        'artifacts/muon_stored_admission_correction_tests_20261012.stdout.txt',
        'artifacts/muon_stored_admission_transpose_tests_20261012.stdout.txt',
        'tests/test_muon_stored_admission_transpose.py'):
        p=ROOT/name;files[name]=sha256(p.read_bytes()).hexdigest()
    p=Path(__file__);files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    record=dict(classification='VERIFIED_ONE_BOUNDED_EXACT_STORED148_ADMISSION_CORRECTION_PAIR',
        all_output_bytes_equal=True,input_hashes=pins,files=files,
        commands=[f'C:/Python314/python.exe scripts/evaluate_muon_stored_admission_correction.py --output artifacts/muon_stored_admission_correction_20261012/run_{i} --precision-bits 192 --corrections 3' for i in(1,2)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        precision_bits=192,correction_budget=3,original_guard=2e-10,
        focused_tests=[dict(command='C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_stored_admission_correction.py',observed_result='2 passed in 0.94s'),
            dict(command='C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_stored_admission_transpose.py',observed_result='1 passed; exact timing retained in stdout')],
        applications=reports[0]['applications'],
        matrix_solution_high_low_representation_distinct_from_rounded_state=True,
        no_original_action_accuracy_or_physical_admission_bound=True,
        no_canonical_changing_background_or_unsquared_source_integration_executed=True,
        scope='one bounded correction of unchanged stored K/rhs/targets/sources; all146 and namedframe rows/reactions remain independent audits')
    out.mkdir(parents=True);p=out/'publication_manifest.json'
    p.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
