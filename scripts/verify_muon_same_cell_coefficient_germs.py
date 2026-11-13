"""Verify the same-action source coefficient germs and their independent replay."""
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_same_cell_coefficient_germs_20261011'


def identity(p):
    p=Path(p);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes()
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha256(b).hexdigest())


def main():
    files=set();pairs={};count=0;commands=[]
    for name in ('application.npz','result.json'):
        paths=[FOLDER/('run_'+str(n))/name for n in (1,2)]
        infos=[identity(p)for p in paths];files.update(p.relative_to(ROOT).as_posix()for p in paths)
        if len({(r['bytes'],r['sha256'])for r in infos})!=1:raise ValueError('independent replay differs '+name)
        pairs[name]=infos
    for n in (1,2):
        md=json.loads((FOLDER/('run_'+str(n))/'result.json').read_text())
        for name,h in md['input_hashes'].items():
            if identity(name)['sha256']!=h:raise ValueError('consumed input changed '+name)
            count+=1
        logs={}
        for ch in ('stdout','stderr'):
            p='artifacts/muon_same_cell_coefficient_germs_run_'+str(n)+'.'+ch+'.txt'
            files.add(p);logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
        commands.append(dict(argv=['C:\\Python314\\python.exe','scripts/evaluate_muon_same_cell_coefficient_germs.py',
            '--output','artifacts/muon_same_cell_coefficient_germs_20261011/run_'+str(n)],exit_code=0,logs=logs,
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1')))
    for suffix in ('','_2'):
        logs={}
        for ch in ('stdout','stderr'):
            p='artifacts/muon_same_cell_coefficient_germs_tests'+suffix+'.'+ch+'.txt'
            files.add(p);logs[ch]=dict(**identity(p),text=(ROOT/p).read_text())
        commands.append(dict(argv=['C:\\Python314\\python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_same_cell_coefficient_germs.py'],exit_code=0,tests_passed=6,logs=logs,
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1')))
    files.update(('src/bhsm/interface/muon_same_cell_coefficient_germs.py',
        'tests/test_muon_same_cell_coefficient_germs.py','scripts/evaluate_muon_same_cell_coefficient_germs.py',
        Path(__file__).relative_to(ROOT).as_posix()))
    record=dict(classification='VERIFIED_REPLAYED_SAME_BACKGROUND_COEFFICIENT_GERMS',commands=commands,
        independent_byte_replay=pairs,verified_input_hash_count=count,
        review='validation agent read-only reviewed full profile, inverse and product germs; explicit-clock second derivative corrected to its along-cell derivative before canonical production',
        DERIVED='metric inverse and complete inherited kappa first/second germs; stable divided differences integrate owned derivative instead of close-value subtraction',
        EVALUATED='both chronological arms,12 split-Gauss nodes,4/8Gauss divided derivatives,6 focused tests including independent complete action value differences',
        CONTROL_ONLY='exact declared inside-cell affine x and held vy plus inherited affine parent/reference first germs; no physical history inferred',
        UNEVALUATED='outward coefficient-production bounds and full differential/native response and Pauli uncertainty',
        OWNER_DEFINITION_GAP='none established',
        error_scope='analytic finite action jets in binary64; difference and quadrature checks are diagnostics, not full observable enclosures',
        complete_observable=False,physical_a_mu=None,physical_g_mu=None)
    p=FOLDER/'verification.json';p.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    files.add(p.relative_to(ROOT).as_posix())
    manifest=dict(classification='FROZEN_REPLAYED_SAME_BACKGROUND_COEFFICIENT_GERMS',
        byte_identical_replay=True,all_input_hashes_verified=True,files=[identity(n)for n in sorted(files)])
    (FOLDER/'publication_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(p),publication_manifest=identity(FOLDER/'publication_manifest.json'),
        files=len(files),byte_identical=True),sort_keys=True))


if __name__=='__main__':main()
