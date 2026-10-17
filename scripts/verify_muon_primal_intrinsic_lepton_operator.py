"""Verify actual primal lepton applications without rerunning their action solves."""
from __future__ import annotations
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_primal_intrinsic_lepton_operator_20261010'


def identity(path):
    data=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest())


def main():
    pairs=[]
    for name in ('application.npz','result.json'):
        first,second=(FOLDER/f'run_{i}'/name for i in (1,2))
        if first.read_bytes()!=second.read_bytes():raise ValueError('independent replay differs: '+name)
        pairs.append(dict(first=identity(first),second=identity(second),byte_identical=True))
    result=json.loads((FOLDER/'run_1/result.json').read_text(encoding='utf8'))
    consumed=[]
    for path,expected in result['input_hashes'].items():
        actual=identity(ROOT/path)
        if actual['sha256']!=expected:raise ValueError('consumed owner changed: '+path)
        consumed.append(actual)
    with np.load(FOLDER/'run_1/application.npz',allow_pickle=False) as arrays:
        if any(not np.isfinite(arrays[k]).all() for k in arrays.files):raise ValueError('nonfinite action application')
        for side in ('incoming','outgoing'):
            for position in ('birth','midpoint'):
                key=f'{side}_{position}'
                if arrays[key+'_raw_fields'].shape!=(228,):raise ValueError('incomplete raw fields')
                if arrays[key+'_W_raw_first_jet'].shape!=(228,18,18):raise ValueError('incomplete first action jet')
                if not np.array_equal(arrays[key+'_current_Gram'],np.eye(18)):raise ValueError('current pairing changed')
    stdout=ROOT/'artifacts/muon_primal_intrinsic_lepton_operator_tests.stdout.txt'
    stderr=ROOT/'artifacts/muon_primal_intrinsic_lepton_operator_tests.stderr.txt'
    test_output=stdout.read_text(encoding='utf8')
    if '10 passed' not in test_output or stderr.read_bytes():raise ValueError('focused tests did not pass')
    commands=[]
    for i in (1,2):
        out=ROOT/f'artifacts/muon_primal_intrinsic_lepton_operator_run{i}.stdout.txt'
        err=ROOT/f'artifacts/muon_primal_intrinsic_lepton_operator_run{i}.stderr.txt'
        if err.read_bytes():raise ValueError('production stderr is nonempty')
        commands.append(dict(argv=[sys.executable,'scripts/evaluate_muon_primal_intrinsic_lepton_operator.py',
            '--output',f'artifacts/muon_primal_intrinsic_lepton_operator_20261010/run_{i}'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),
            python_exit_code=0,stdout=identity(out),stderr=identity(err)))
    verification=dict(classification='VERIFIED_ALL_FAMILY_OPERATOR_ON_ACTUAL_PRIMAL_FIELDS',
        commands=commands,independent_process_replays=pairs,consumed_owner_identities=consumed,
        focused_tests=dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_primal_intrinsic_lepton_operator.py'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),exit_code=0,
            stdout=test_output,stderr='',stdout_file=identity(stdout),stderr_file=identity(stderr),
            source=identity(ROOT/'src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py'),
            test=identity(ROOT/'tests/test_muon_primal_intrinsic_lepton_operator.py')),
        runtime=dict(executable=sys.executable,python=sys.version,
            packages={p:version(p) for p in ('numpy','scipy','pytest','python-flint')}),
        common_birth_comparison=result['common_birth_comparison'],
        scientific_classification=dict(
            DERIVED='literal all-family first-order Dirac action, independent material gauge traces and actual H; analytic geometry/gauge/H first jets and proper-time measure jets',
            EVALUATED='both actual nonlinear incoming/outgoing birth fields at common t0 and midpoint fields; complete C18 operator, canonical current Gram and raw228 first jets',
            CONTROL_ONLY='assigned nu-squared4/gamma-null parameter member and finite midpoint action domain; no covariance or physical carrier selected',
            UNEVALUATED='physical scale and area matching, formation and cutoff, complete native relative domain, LSZ and renormalized soft-transfer Pauli contraction',
            OWNER_DEFINITION_GAP='none established'),
        error_scope=result['error_scope'],same_birth_W_is_complete_relative_heat_cancellation=False,
        preserved_flags=dict(action_selected=False,Gate7_closed=False),complete_observable=False,
        continued_production_required=True)
    target=FOLDER/'verification.json'
    if target.exists():raise FileExistsError('preserve verification; choose a new version')
    target.write_text(json.dumps(verification,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(target),all_replays_byte_identical=True),sort_keys=True))


if __name__=='__main__':main()
