#!/usr/bin/env python
"""Verify independent endpoint applications and record their actual scope."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

import flint
import numpy as np
import scipy

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_pointwise_full_field_action_20261010'


def record(path):
    p=Path(path)
    if not p.is_absolute(): p=ROOT/p
    raw=p.read_bytes()
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=sha256(raw).hexdigest())


def main():
    pairs=[]
    for name in ('application.npz','result.json'):
        left,right=BASE/'run_2'/name,BASE/'run_3'/name
        if left.read_bytes()!=right.read_bytes():raise RuntimeError(f'replay mismatch: {name}')
        pairs.append(dict(left=record(left),right=record(right),byte_identical=True))
    result=json.loads((BASE/'run_2/result.json').read_bytes())
    for p,h in result['input_hashes'].items():
        if record(p)['sha256']!=h:raise RuntimeError(f'owner changed: {p}')
    with np.load(BASE/'run_2/application.npz',allow_pickle=False) as a:
        if any(not np.isfinite(a[k]).all() for k in a.files):raise RuntimeError('nonfinite action application')
        if a['raw_hessian'].shape!=(2,228,228):raise RuntimeError('incomplete fullfield Hessian')
    test_out=ROOT/'artifacts/muon_pointwise_full_field_action_tests.stdout.txt'
    if '5 passed' not in test_out.read_text():raise RuntimeError('focused test completion not recorded')
    logs={name:record('artifacts/'+name) for name in (
        'muon_pointwise_full_field_action_run1.stdout.txt','muon_pointwise_full_field_action_run1.stderr.txt',
        'muon_pointwise_full_field_action_run2.stdout.txt','muon_pointwise_full_field_action_run2.stderr.txt',
        'muon_pointwise_full_field_action_run3.stdout.txt','muon_pointwise_full_field_action_run3.stderr.txt',
        'muon_pointwise_full_field_action_tests.stdout.txt','muon_pointwise_full_field_action_tests.stderr.txt')}
    commands=[]
    for run,exit_code in ((1,1),(2,0),(3,0)):
        commands.append(dict(argv=[sys.executable,'scripts/evaluate_muon_pointwise_full_field_action.py',
            '--output',f'artifacts/muon_pointwise_full_field_action_20261010/run_{run}'],
            shell='PowerShell',cwd=str(ROOT),exit_code=exit_code,
            stdout=logs[f'muon_pointwise_full_field_action_run{run}.stdout.txt'],
            stderr=logs[f'muon_pointwise_full_field_action_run{run}.stderr.txt']))
    commands.append(dict(argv=[sys.executable,'-m','pytest','--noconftest',
        'tests/test_muon_pointwise_full_field_action.py','-q'],cwd=str(ROOT),exit_code=0,
        stdout=logs['muon_pointwise_full_field_action_tests.stdout.txt'],
        stderr=logs['muon_pointwise_full_field_action_tests.stderr.txt']))
    payload=dict(scope='VERIFIED_REPLAY_OF_EXECUTED_POINTWISE_TWO_ARM_FULLFIELD_ACTION',
        commands=commands,
        failure_scope='run1 rejected a40 interior-only representation; no output application was written. Producer corrected to inherited a60 including20 independent wall lifts; run2/3 succeeded unchanged.',
        tests=dict(final_count=5,final_stdout=test_out.read_text(),
            earlier_results=['4 passed in 11.58s','5 passed in 11.43s'],
            covered='all228 first/second derivatives against unchanged literal mean backend; active zero-gauge first/mixed rows; supplied acceleration/multiplier motion; natural wall trace contact; absent-input rejection'),
        runtime=dict(executable=record(sys.executable) if str(ROOT).lower() in sys.executable.lower() else
            dict(path=sys.executable,sha256=sha256(Path(sys.executable).read_bytes()).hexdigest()),
            python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__,python_flint=flint.__version__),
        replay_pairs=pairs,input_hashes=result['input_hashes'],
        changed_source_records=[record(p) for p in (
            'src/bhsm/interface/muon_pointwise_full_field_action.py',
            'scripts/evaluate_muon_pointwise_full_field_action.py',
            'scripts/verify_muon_pointwise_full_field_action.py',
            'tests/test_muon_pointwise_full_field_action.py')],
        classifications=dict(DERIVED='same normalized common-action x/v/y and Euler derivative bindings; material wall conormal orientation',
            EVALUATED='both corrected endpoints: full228 weak-action gradients/Hessians and actual wall conormals',
            CONTROL_ONLY='finite radial/homogeneous basis and action-unit nu_squared=4; corrected assigned56 initialization',
            UNEVALUATED='coupled full Euler continuation, paired physical field/boundary realization, formation, scale/cutoff, completed native Pauli',
            OWNER_DEFINITION_GAP='none established'),
        error_scope=result['error_scope'],
        software_replay_is_anomaly_enclosure=False,action_selected=False,Gate7_closed=False,
        complete_observable=False,publication_audits='recorded separately by the next reviewed aggregate milestone')
    (BASE/'verification.json').write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+'\n',
                                        encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=record(BASE/'verification.json'),replay_verified=True,focused_tests=5),sort_keys=True))


if __name__=='__main__':main()
