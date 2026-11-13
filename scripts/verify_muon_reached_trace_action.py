"""Verify executed reached-source action, replay, commands and error scope."""
from __future__ import annotations
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/muon_reached_trace_action_20261010/verification.json'


def identity(path):
    data=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest())


def main():
    folder=OUT.parent;pairs=[];receipts=[]
    for name in sorted(p.name for p in (folder/'run_2').iterdir() if p.is_file()):
        a,b=folder/'run_2'/name,folder/'run_3'/name
        if a.read_bytes()!=b.read_bytes():raise ValueError('independent replay differs: '+name)
        pairs.append(dict(first=identity(a),second=identity(b),byte_identical=True))
    packet=json.loads((folder/'run_2/result.json').read_text(encoding='utf8'))
    for path,expected in packet['input_hashes'].items():
        actual=identity(ROOT/path)
        if actual['sha256']!=expected:raise ValueError('changed consumed action owner: '+path)
        receipts.append(actual)
    for run in (2,3):
        for name,expected in packet['array_archives'].items():
            path=folder/f'run_{run}'/name
            if identity(path)['sha256']!=expected['sha256']:raise ValueError('numerical archive hash mismatch')
            with np.load(path,allow_pickle=False) as f:
                if sorted(f.files)!=expected['arrays']:raise ValueError('incomplete action archive')
                if any(not np.isfinite(f[k]).all() for k in f.files):raise ValueError('nonfinite action output')
    stdout=(ROOT/'artifacts/muon_reached_trace_action_tests.stdout.txt').read_text(encoding='utf8')
    stderr=(ROOT/'artifacts/muon_reached_trace_action_tests.stderr.txt').read_text(encoding='utf8')
    if '4 passed' not in stdout or stderr:raise ValueError('actual focused verification did not pass')
    commands=[]
    for run,exit_code in ((1,1),(2,0),(3,0)):
        log=ROOT/f'artifacts/muon_reached_trace_action_run{run}.stdout.txt'
        err=ROOT/f'artifacts/muon_reached_trace_action_run{run}.stderr.txt'
        commands.append(dict(argv=[sys.executable,'scripts/evaluate_muon_reached_trace_action.py',
            '--output',f'artifacts/muon_reached_trace_action_20261010/run_{run}',
            '--time-nodes','17','--time-steps','64'],cwd=str(ROOT),
            environment_overrides=dict(PYTHONPATH='src',**({'OPENBLAS_NUM_THREADS':'1'} if run>1 else {})),
            python_exit_code=exit_code,stdout=identity(log),stderr=identity(err),
            outcome=('PACKAGING_FAILURE_AFTER_NUMERICAL_APPLICATION' if run==1 else 'PASSED'),
            error=(err.read_text(encoding='utf8') if exit_code else None)))
    result=dict(classification='VERIFIED_EXECUTED_REACHED_SOURCE_ACTION_COMPONENT',
        commands=commands,focused_tests=dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_reached_trace_action.py'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
            exit_code=0,stdout=stdout,stderr=stderr,
            source=identity(ROOT/'src/bhsm/interface/muon_reached_trace_action.py'),
            test=identity(ROOT/'tests/test_muon_reached_trace_action.py')),
        independent_process_replays=pairs,consumed_owner_identities=receipts,
        runtime=dict(executable=sys.executable,python=sys.version,
            packages={p:version(p) for p in ('numpy','scipy','pytest','python-flint')}),
        numerical_results={k:packet[k] for k in ('Gauss_relative_maximum',
            'action_boundary_relative_defect','adjoint_pairing_maximum_defect',
            'intrinsic_H_response_norm','intrinsic_H_canonical_norm',
            'scalar_wall_current_norm','gauge_Euler_reaction_norm')},
        scientific_classification=dict(
            DERIVED='literal moving full400 trace pullback and Qdot*b electric contact; source motion differentiated before same-action Gauss; intrinsic material H80 seagull and mixed rows',
            EVALUATED='fresh current angular response outside old Q8, coupled full5 Maxwell/H retarded and advanced action on those reached columns; actual nonzero H response and wall currents',
            CONTROL_ONLY='finite outgoing24 backward core, compact Green pulse, conditioning shift and nu-squared4 parameter member',
            UNEVALUATED='physical birth/cutoff and current selection; physical unit matching; complete return/relative completion and renormalized soft Pauli readout',
            OWNER_DEFINITION_GAP='none established'),
        error_scope=dict(forward_adjoint_and_Gauss_are_finite_application_checks=True,
            action_boundary_residual_is_not_continuum_error=True,
            inherited_backward_core_is_not_incoming_history=True,
            conditioned_shift_is_not_physical_soft_momentum=True,
            current_frame_motion_count=1,old_Q8_response_substitution=False,
            full_native_or_anomaly_enclosure=False),
        retained_failures=[dict(scope='test fixture only',command='C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_reached_trace_action.py',
            output='3 setup errors in 2.04s: KeyError incoming_raw_coefficients',
            repair='bind actual raw_endpoint_coefficients[0] archive key; production operator unchanged'),
            dict(scope='archive serialization only',run=1,
                repair='fixed-metadata lossless compression and complete separate action/phase/contact archives; no numerical rows or arrays removed')],
        action_selected=False,Gate7_closed=False,complete_observable=False,
        continued_production_required=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(OUT),all_replays_byte_identical=True),sort_keys=True))


if __name__=='__main__':main()
