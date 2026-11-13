"""Freeze the exact original-reset normal trial domain application replay."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    base=ROOT/'artifacts/muon_reset_normal_trial_domain_20261012'
    out=base/'independent_pair_verification.json'
    if out.exists():raise FileExistsError('preserve every normal-domain receipt')
    a,b=(base/f'run_{i}'for i in(1,2))
    af={p.name:p for p in a.iterdir()if p.is_file()};bf={p.name:p for p in b.iterdir()if p.is_file()}
    if af.keys()!=bf.keys():raise ValueError('all outputs must have identical membership')
    hashes={}
    for name in sorted(af):
        h=sha256(af[name].read_bytes()).hexdigest()
        if h!=sha256(bf[name].read_bytes()).hexdigest():raise ValueError('output replay differs '+name)
        hashes[name]=h
    md=json.loads((a/'result.json').read_bytes())
    for p,h in md['input_hashes'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('same supplied trial or storedJ changed '+p)
    logs={}
    for name,source in[(f'run_{i}.stdout.txt',f'artifacts/muon_reset_normal_trial_domain_run_{i}.stdout.txt')for i in(1,2)]+[
        ('focused_review.stdout.txt','artifacts/muon_reset_normal_trial_domain_review.stdout.txt')]:
        data=(ROOT/source).read_bytes();p=base/name;p.write_bytes(data)
        logs[name]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
    result=dict(classification='INDEPENDENT_REPLAY_ORIGINAL_RESET_DOMAIN_TEST_OF_SUPPLIED_NORMAL_TRIALS',
        all_output_bytes_identical=True,all_output_count=len(hashes),all_output_sha256=hashes,input_pins_current=True,
        executions=[dict(argv=['C:/Python314/python.exe','scripts/evaluate_muon_reset_normal_trial_domain.py',
            '--output',f'artifacts/muon_reset_normal_trial_domain_20261012/run_{i}'],exit_code=0)for i in(1,2)],
        focused_review=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_reset_normal_trial_domain.py'],exit_code=0,passed=1,duration_seconds=1.74),
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),cwd=str(ROOT),
        stdout=logs,capture_provenance='complete actual PowerShell Tee-Object bytes',
        independent_math_review='Validation reviewed module, evaluator and full504 analytic-bilinear/sign test without edits or duplicate tests',
        finite_normal_owner_review='FullLyy, commonattachment/propernormal gluing, independent analytic left/right, 8 staticAr frames, heldstate area derivative and one child-plus properclock; complete Jacobi time contacts −dotLvx,−dotLvv,−dotLvy plus reference-only clock reviewed',
        full_domain_caveat='80 reset algebraic/Gauss rows repeat bulk algebraic Jacobi equations; two central Ward identities remain. Do not append all226 as independent borders or call the local3-row trace space the fullreset domain',
        coefficient_units='frequency orders0..2 are Taylor coefficients with different frequency powers; their maxima are domain images, not a Pauli uncertainty',
        normal_trial_domain_violation_excludes_all_physical_normal_modes=False,
        physical_firsthit_i_over_r_gamma_or_Pauli_completed=False,
        verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    files=['src/bhsm/interface/muon_reset_normal_trial_domain.py','scripts/evaluate_muon_reset_normal_trial_domain.py',
        'tests/test_muon_reset_normal_trial_domain.py',Path(__file__).relative_to(ROOT).as_posix(),out.relative_to(ROOT).as_posix()]
    files+=sorted((base/name).relative_to(ROOT).as_posix()for name in logs)
    files+=sorted(p.relative_to(ROOT).as_posix()for d in(a,b)for p in d.iterdir()if p.is_file())
    manifest=base/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification=result['classification'],
        files={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in files},
        dependencies=['artifacts/muon_complex_paired_normal_action_20261012/run_1/result.json',
                      'artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1/result.json'],
        physical_Pauli_completed=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=hashes['result.json'],all_output_count=len(hashes),
        verification=out.relative_to(ROOT).as_posix(),verification_sha256=sha256(out.read_bytes()).hexdigest(),
        manifest=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha256(manifest.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':verify()
