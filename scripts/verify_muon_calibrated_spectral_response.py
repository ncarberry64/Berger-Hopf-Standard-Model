"""Record focused checks and immutable replay evidence for evaluated components.

This is verification of the declared partial applications, not an uncertainty
enclosure or a complete native Pauli calculation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'artifacts/muon_calibrated_current_response_20261010/verification.json'
MODULES = (
    'muon_calibrated_higher_qed', 'muon_calibrated_hvp_spectral',
    'muon_calibrated_hvp_higher', 'muon_calibrated_hvp_nnlo',
    'muon_calibrated_hadronic_ledger', 'muon_calibrated_weak_decay',
    'muon_calibrated_current_response', 'muon_calibrated_component_ledger',
    'muon_intrinsic_scalar_birth_rows', 'muon_parent_retarded_hypercharge',
    'muon_parent_maxwell_background_euler', 'muon_parent_maxwell_geometry_weak',
    'muon_parent_hypercharge_advanced_probe', 'muon_parent_hypercharge_energy_residual',
)
PAIRS = (
    ('muon_calibrated_higher_qed_20261010', 'run_1', 'run_2'),
    ('muon_calibrated_weak_decay_20261010', 'run_1', 'run_2'),
    ('muon_calibrated_hvp_spectral_20261010', 'run_3', 'run_4'),
    ('muon_calibrated_hvp_higher_20261010', 'run_3', 'run_4'),
    ('muon_calibrated_hvp_nnlo_20261010', 'run_3', 'run_4'),
    ('muon_calibrated_hvp_spectral_20261010', 'hadronic_ledger_run_1', 'hadronic_ledger_run_2'),
    ('muon_calibrated_current_response_20261010', 'run_1', 'run_2'),
    ('muon_calibrated_component_ledger_20261010', 'run_5', 'run_6'),
    ('muon_parent_retarded_hypercharge_20261010', 'canonical_run_1', 'canonical_run_2'),
    ('muon_parent_retarded_hypercharge_20261010', 'background_canonical_run_1', 'background_canonical_run_2'),
    ('muon_parent_retarded_hypercharge_20261010', 'mixed_run_1', 'mixed_run_2'),
    ('muon_parent_hypercharge_advanced_probe_20261010', 'run_3', 'run_4'),
    ('muon_parent_hypercharge_energy_residual_20261010', 'run_1', 'run_2'),
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command):
    env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), OPENBLAS_NUM_THREADS='1')
    process = subprocess.run(command, cwd=ROOT, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return dict(argv=command, cwd=str(ROOT), environment_overrides={
        'PYTHONPATH': str(ROOT/'src'), 'OPENBLAS_NUM_THREADS':'1'},
        exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr)

def evidence():
    pairs = []
    for directory, first, second in PAIRS:
        left, right = (ROOT/'artifacts'/directory/name for name in (first,second))
        names = sorted(p.relative_to(left).as_posix() for p in left.rglob('*') if p.is_file())
        other = sorted(p.relative_to(right).as_posix() for p in right.rglob('*') if p.is_file())
        if not names or names != other:
            raise ValueError(f'incomplete replay pair {directory}/{first},{second}')
        files = []
        for name in names:
            a,b=left/name,right/name
            if a.read_bytes() != b.read_bytes():
                raise ValueError(f'replay differs: {directory}/{name}')
            files.append(dict(first=a.relative_to(ROOT).as_posix(),
                              second=b.relative_to(ROOT).as_posix(),
                              sha256=digest(a),bytes=a.stat().st_size))
        pairs.append(dict(byte_identical=True,files=files))
    sources = [ROOT/f'src/bhsm/interface/{m}.py' for m in MODULES]
    sources += [ROOT/f'tests/test_{m}.py' for m in MODULES]
    sources += [ROOT/'scripts/verify_muon_calibrated_spectral_response.py']
    sources += sorted(ROOT.glob('scripts/evaluate_muon_calibrated*.py'))
    sources += [ROOT/'scripts/evaluate_muon_parent_hypercharge_advanced_probe.py']
    inputs = [ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json',
              ROOT/'artifacts/muon_calibrated_pauli_20261009/run_1/calibrated_pauli.json']
    for directory in ('muon_calibrated_hvp_spectral_20261010',
                      'muon_calibrated_hvp_higher_20261010',
                      'muon_calibrated_hvp_nnlo_20261010',
                      'muon_calibrated_hlbl_projection_20261010'):
        inputs += sorted((ROOT/'artifacts'/directory/'input').rglob('*'))
    return dict(replays=pairs, source_hashes={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
                input_hashes={p.relative_to(ROOT).as_posix():digest(p) for p in inputs if p.is_file()})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests',action='store_true')
    parser.add_argument('--audit',choices=('status','claims','frozen','precision','public'))
    parser.add_argument('--audits',action='store_true')
    parser.add_argument('--replay-root',action='store_true')
    args=parser.parse_args()
    record=json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    record.update(evidence())
    record.update(scope='EVALUATED_CALIBRATED_COMPONENTS_AND_ACTION_APPLICATIONS; native remainder incomplete',
        action_selected=False, Gate7_closed=False,
        scientific_classification=dict(
            DERIVED='normalized spectral/Pauli kernel, constrained source/adjoint identities, common input tangent, Maxwell weak/chart identities',
            EVALUATED='QED3-5, current HVP LO/NLO/NNLO, independently published HLbL projection, rematched weak subset, top one-loop VP, retained parent weak applications',
            CONTROL_ONLY='compact temporal/radial parent probes and finite test representation; not a formation section',
            UNEVALUATED='full native Pauli remainder after common-action overlap; physical background and source/heat completion; remaining weak terms',
            OWNER_DEFINITION_GAP='none established'),
        error_scope=dict(
            native_unknown_not_truncation=True, full_observable_enclosure=False,
            parent_probe_continuum_estimate_not_enclosure=True,
            calibrated_subtotal_not_complete_prediction=True,
            historical_corrected_failures=[
                'Uniform-Gauss spacelike endpoint layer; replaced by endpoint partition before final replay.',
                'Incorrect test SI magneton range; corrected unit expectation.',
                'Component driver expected primitive_order; corrected to owned gradient_order.',
                'Scalar-array shape in energy residual coefficient derivative; corrected before final tests.',
                'Stale parent source hash rejected during LF normalization; final consumers use canonical replay.',
                'Birth velocity-Hessian inversion generated order1e12 accelerations; rejected, not used.',
                'Strong conormal difference remains unconverged; goal estimate is loose and uncertified.']))
    command=None
    if args.replay_root:
        jobs=(('muon_calibrated_current_response_20261010','evaluate_muon_calibrated_current_response.py','run_1'),
              ('muon_calibrated_component_ledger_20261010','evaluate_muon_calibrated_component_ledger.py','run_5'),
              ('muon_parent_hypercharge_advanced_probe_20261010','evaluate_muon_parent_hypercharge_advanced_probe.py','run_3'))
        commands=[[sys.executable,'scripts/'+script,'--output','artifacts/'+directory+'/verification_replay']
                  for directory,script,_ in jobs]
        if any((ROOT/c[-1]).exists() for c in commands):
            raise FileExistsError('preserve previous replay; root replay has already been run')
        with ThreadPoolExecutor(max_workers=3) as executor:
            completed=list(executor.map(run,commands))
        for job,result in zip(jobs,completed):
            directory,_,reference=job
            if result['exit_code']!=0:
                continue
            expected=ROOT/'artifacts'/directory/reference
            actual=ROOT/'artifacts'/directory/'verification_replay'
            names=sorted(p.relative_to(expected).as_posix() for p in expected.rglob('*') if p.is_file())
            result['byte_identical_to_reference']=all((expected/p).read_bytes()==(actual/p).read_bytes() for p in names)
            result['reference']=expected.relative_to(ROOT).as_posix()
            if not result['byte_identical_to_reference']:
                result['exit_code']=1
        record['root_producer_replay_commands']=completed
    elif args.tests:
        command=[sys.executable,'-m','pytest','-q']+[f'tests/test_{m}.py' for m in MODULES]
        key='focused_tests'
    elif args.audit or args.audits:
        audit=dict(status=['tools/audit_bhsm_status.py','--format','json'],
                   claims=['tools/audit_forbidden_claims.py','--format','json'],
                   frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],
                   precision=['tools/verify_precision.py'],
                   public=['tools/audit_public_readiness.py','--format','json'])
        if args.audits:
            with ThreadPoolExecutor(max_workers=5) as executor:
                completed=list(executor.map(run,([sys.executable]+v for v in audit.values())))
            for name,result in zip(audit,completed):
                record['audit_'+name]=result
        else:
            command=[sys.executable]+audit[args.audit]; key='audit_'+args.audit
    if command:
        result=run(command)
        # Audit calls can be run independently; merge their results at write time.
        if OUTPUT.exists():
            latest=json.loads(OUTPUT.read_text())
            latest.update(record); record=latest
        record[key]=result
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if command:
        print(json.dumps(record[key],indent=2)); return record[key]['exit_code']
    if args.replay_root:
        print(json.dumps(record['root_producer_replay_commands'],indent=2))
        return max(row['exit_code'] for row in record['root_producer_replay_commands'])
    if args.audits:
        print(json.dumps({name:dict(exit_code=record['audit_'+name]['exit_code'],
                                   stdout=record['audit_'+name]['stdout'],
                                   stderr=record['audit_'+name]['stderr']) for name in audit},indent=2))
        return max(record['audit_'+name]['exit_code'] for name in audit)
    print(json.dumps(dict(replay_pairs=len(record['replays']),byte_identical=True,
                         output=OUTPUT.relative_to(ROOT).as_posix()),indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
