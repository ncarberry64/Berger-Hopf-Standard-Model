"""Verify interacting paired-endpoint operator applications and exact trace reduction."""
from __future__ import annotations
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/muon_primal_trace_enriched_lepton_operator_20261010'


def identity(path):
    data=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest())


def main():
    pairs=[]
    for name in ('application.npz','result.json'):
        a,b=(FOLDER/f'run_{i}'/name for i in (1,2))
        if a.read_bytes()!=b.read_bytes():raise ValueError('independent replay differs: '+name)
        pairs.append(dict(first=identity(a),second=identity(b),byte_identical=True))
    result=json.loads((FOLDER/'run_1/result.json').read_text(encoding='utf8'))
    consumed=[]
    for path,expected in result['input_hashes'].items():
        actual=identity(ROOT/path)
        if actual['sha256']!=expected:raise ValueError('consumed owner changed: '+path)
        consumed.append(actual)
    with np.load(FOLDER/'run_1/application.npz',allow_pickle=False) as f:
        if any(not np.isfinite(f[k]).all() for k in f.files):raise ValueError('nonfinite result')
        for side in ('incoming','outgoing'):
            if f[side+'_raw_fields'].shape!=(268,) or f[side+'_W_raw_first_jet'].shape!=(268,18,18):
                raise ValueError('incomplete actual enriched fields or first jets')
            if not np.array_equal(f[side+'_current_Gram'],np.eye(18)):raise ValueError('current pairing changed')
    test_out=ROOT/'artifacts/muon_primal_trace_enriched_lepton_operator_tests.stdout.txt'
    test_err=ROOT/'artifacts/muon_primal_trace_enriched_lepton_operator_tests.stderr.txt'
    text=test_out.read_text(encoding='utf8')
    if '10 passed' not in text or test_err.read_bytes():raise ValueError('focused tests did not pass')
    endpoint='artifacts/muon_parent_gauge_geometry_correction_20261010/paired_field_endpoint_enriched_run_1'
    commands=[]
    for run in (1,2):
        out=ROOT/f'artifacts/muon_primal_trace_enriched_lepton_operator_run{run}.stdout.txt'
        err=ROOT/f'artifacts/muon_primal_trace_enriched_lepton_operator_run{run}.stderr.txt'
        if err.read_bytes():raise ValueError('production stderr is nonempty')
        commands.append(dict(argv=[sys.executable,'scripts/evaluate_muon_primal_trace_enriched_lepton_operator.py',
            '--endpoint',endpoint,'--output',f'artifacts/muon_primal_trace_enriched_lepton_operator_20261010/run_{run}'],
            cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1'),python_exit_code=0,
            stdout=identity(out),stderr=identity(err)))
    record=dict(classification='VERIFIED_ACTUAL_INTERACTING_PAIRED_ENDPOINT_LEPTON_ACTION',
        commands=commands,independent_process_replays=pairs,consumed_owner_identities=consumed,
        focused_tests=dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_primal_trace_enriched_lepton_operator.py'],
            exit_code=0,stdout=text,stderr='',stdout_file=identity(test_out),stderr_file=identity(test_err),
            source=identity(ROOT/'src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py'),
            test=identity(ROOT/'tests/test_muon_primal_trace_enriched_lepton_operator.py')),
        runtime=dict(executable=sys.executable,python=sys.version,packages={p:version(p) for p in ('numpy','scipy','pytest','python-flint')}),
        scientific_classification=dict(
            DERIVED='exact action reduction through all20 wall components; full raw268 analytic first jets via fixed-frame trace map; no bulk radial action projection',
            EVALUATED='complete C18 all-family lepton operator and first jets on both nonzero interacting gauge/H paired endpoint fields',
            CONTROL_ONLY='finite assigned nu-squared4/gamma-null action member, fixed q endpoint and numerical radial frame',
            UNEVALUATED='physical matching/cutoff and complete relative domain/LSZ/soft Pauli observable',
            OWNER_DEFINITION_GAP='none established'),
        common_birth_comparison=result['common_birth_comparison'],error_scope=result['error_scope'],
        no_covariance_or_carrier_member_selected=True,complete_observable=False,
        action_selected=False,Gate7_closed=False,continued_production_required=True)
    target=FOLDER/'verification.json'
    if target.exists():raise FileExistsError('preserve verification; choose a new version')
    target.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=identity(target),all_replays_byte_identical=True),sort_keys=True))


if __name__=='__main__':main()
