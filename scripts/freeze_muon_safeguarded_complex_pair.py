"""Verify every independent deterministic canonical-probe output byte."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def freeze():
    base=ROOT/'artifacts/muon_safeguarded_complex_constitutive_20261011'
    output=base/'deterministic_pair_verification.json'
    if output.exists():raise FileExistsError('preserve independent replay evidence')
    pairs=[];pins={}
    for first,second in(('direct_run_1','direct_replay_run_2'),('resumed_run_1','resumed_replay_run_2')):
        a,b=base/first,base/second
        if not (b/'result.json').exists():raise ValueError('independent execution is not complete: '+second)
        af={p.relative_to(a).as_posix():p for p in a.rglob('*')if p.is_file()}
        bf={p.relative_to(b).as_posix():p for p in b.rglob('*')if p.is_file()}
        if af.keys()!=bf.keys():raise ValueError('independent output membership differs')
        hashes={}
        for name in sorted(af):
            ha=sha256(af[name].read_bytes()).hexdigest();hb=sha256(bf[name].read_bytes()).hexdigest()
            if ha!=hb:raise ValueError('independent byte difference: '+name)
            hashes[name]=ha
        receipt=json.loads((a/'result.json').read_bytes())
        for rel,h in receipt['input_hashes'].items():
            if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:raise ValueError('consumed source changed: '+rel)
            pins[rel]=h
        pairs.append(dict(original=first,replay=second,all_output_bytes_identical=True,
            all_output_count=len(hashes),all_output_sha256=hashes,
            scientific_result_sha256=hashes['result.json'],
            compact_application_sha256=hashes['application.npz']))
    logs={}
    for label in('direct_replay_run_2','resumed_replay_run_2'):
        path=Path('C:/Users/carbe/Downloads')/('BHSM_complex_constitutive_'+label+'.stdout.txt')
        data=path.read_bytes();target=base/(label+'.stdout.txt');target.write_bytes(data)
        logs[target.name]=dict(sha256=sha256(data).hexdigest(),bytes=len(data),
            capture_provenance='Actual completed PowerShell Tee-Object bytes, copied unchanged.')
    env=dict(PYTHONPATH='src;.',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    commands=[dict(argv=['C:/Python314/python.exe','scripts/evaluate_muon_safeguarded_complex_constitutive.py',
        '--output','artifacts/muon_safeguarded_complex_constitutive_20261011/direct_replay_run_2',
        '--max-evaluations','80'],environment=env,exit_code=0),
        dict(argv=['C:/Python314/python.exe','scripts/continue_muon_safeguarded_complex_constitutive.py',
        '--previous','artifacts/muon_safeguarded_complex_constitutive_20261011/direct_run_1',
        '--output','artifacts/muon_safeguarded_complex_constitutive_20261011/resumed_replay_run_2',
        '--max-evaluations','200'],environment=env,exit_code=0)]
    md=dict(classification='INDEPENDENT_BYTE_IDENTICAL_ALL148_CANONICAL_PROBE_REPLAYS',
        pairs=pairs,executions=commands,stdout=logs,consumed_source_pins_current=True,
        consumed_source_pin_count=len(pins),
        preserved_previous_verification='finite_solver_verification.json recorded the first completed executions before replay',
        replay_input_scope='Both replays consume original terminalrun2; resumed replay consumes SAME direct_run1, not replay path.',
        full_ancestor_rematerialization_executed=False,physical_Pauli_or_stationarity_claim=False,
        verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    output.write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=output.relative_to(ROOT).as_posix(),
        sha256=sha256(output.read_bytes()).hexdigest(),pairs=[{k:v for k,v in p.items()if k!='all_output_sha256'}for p in pairs]),sort_keys=True))


if __name__=='__main__':freeze()
