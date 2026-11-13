"""Freeze completed canonical residual probes and their execution evidence."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def freeze():
    base=ROOT/'artifacts/muon_safeguarded_complex_constitutive_20261011'
    output=base/'finite_solver_verification.json'
    if output.exists():raise FileExistsError('immutable completed verification')
    component={};checked={}
    for name in('direct_run_1','resumed_run_1'):
        folder=base/name;receipt=json.loads((folder/'result.json').read_bytes())
        for path,digest in receipt['input_hashes'].items():
            if sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('source changed: '+path)
            checked[path]=digest
        p=folder/'application.npz';digest=sha256(p.read_bytes()).hexdigest()
        if digest!=receipt['archives']['application.npz']['sha256']:raise ValueError('final rows changed')
        component[name]=dict(result_sha256=sha256((folder/'result.json').read_bytes()).hexdigest(),
            application_sha256=digest,exit_code=0,status=receipt['status'],
            original_rows_max=receipt['original_rows_max'],
            original_momentum_residual_max=receipt['original_momentum_residual_max'],
            original_algebraic_residual_max=receipt['original_algebraic_residual_max'],
            accepted_checkpoint_count=len(receipt['history']),
            independent_replay_executed=False)
    stdout=Path('C:/Users/carbe/Downloads/BHSM_complex_constitutive_resumed_run_1.stdout.txt').read_bytes()
    (base/'resumed_run_1.stdout.txt').write_bytes(stdout)
    environment=dict(PYTHONPATH='src;.',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    records=[dict(argv=['C:/Python314/python.exe','scripts/evaluate_muon_safeguarded_complex_constitutive.py',
        '--output','artifacts/muon_safeguarded_complex_constitutive_20261011/direct_run_1',
        '--max-evaluations','80'],environment=environment,exit_code=0,
        stdout_capture='Tool returned streamed stdout; complete accepted history is in result.json. No raw shell capture was requested.'),
        dict(argv=['C:/Python314/python.exe','scripts/continue_muon_safeguarded_complex_constitutive.py',
        '--previous','artifacts/muon_safeguarded_complex_constitutive_20261011/direct_run_1',
        '--output','artifacts/muon_safeguarded_complex_constitutive_20261011/resumed_run_1',
        '--max-evaluations','200'],environment=environment,exit_code=0,
        stdout_capture='Actual complete PowerShell Tee-Object bytes copied without transformation.',
        stdout_sha256=sha256(stdout).hexdigest()),
        dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
        'tests/test_muon_safeguarded_complex_constitutive.py'],environment=environment,exit_code=0,
        passed=2,reported_seconds=.81,
        stdout_capture='Actual tool-returned test summary; no raw shell capture requested.',
        warning_scope='Two SciPy zero-gradient division warnings in deliberately incompatible toy control; its original source remained unsolved.')]
    paths=['src/bhsm/interface/muon_safeguarded_complex_constitutive.py',
        'scripts/evaluate_muon_safeguarded_complex_constitutive.py',
        'scripts/continue_muon_safeguarded_complex_constitutive.py',
        'tests/test_muon_safeguarded_complex_constitutive.py',
        Path(__file__).relative_to(ROOT).as_posix()]
    md=dict(classification='IMMUTABLE_COMPLETED_ALL148_CANONICAL_RESIDUAL_EXECUTION_EVIDENCE',
        components=component,executions=records,
        own_source_hashes={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in paths},
        consumed_source_pin_count=len(checked),consumed_sources_current=True,
        original_action_source_position_momentum_and_named_frame_preserved=True,
        optimizer_success_promoted_to_stationarity=False,
        physical_compatibility_or_Pauli_claim=False,
        checkpoint_role='Accepted checkpoints retained locally; compact final action and complete histories selected for publication.',
        coframe_prototype_consumed_by_these_runs=False)
    output.write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=output.relative_to(ROOT).as_posix(),
        sha256=sha256(output.read_bytes()).hexdigest(),components=component),sort_keys=True))


if __name__=='__main__':freeze()
