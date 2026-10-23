"""Verification of evaluated action applications, with their limited scope."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'artifacts/muon_coupled_action_application_20261010/verification.json'
MODULES=('muon_intrinsic_higgs_gauge_action','muon_parent_maxwell_full_weak',
    'muon_parent_maxwell_full_q_application','muon_calibrated_bosonic_weak_log')
PAIRS=(('muon_parent_maxwell_full_weak_20261010','run_5','run_6'),
       ('muon_parent_maxwell_full_q_20261010','run_1','run_2'),
       ('muon_calibrated_bosonic_weak_log_20261010','run_1','run_2'),
       ('muon_calibrated_extended_ledger_20261010','run_1','run_2'))


def identity(p):
    b=p.read_bytes()
    return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def execute(argv):
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1')
    result=subprocess.run(argv,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return dict(argv=argv,cwd=str(ROOT),environment_overrides={
        'PYTHONPATH':str(ROOT/'src'),'OPENBLAS_NUM_THREADS':'1'},
        exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)


def evidence():
    replays=[]
    for directory,a,b in PAIRS:
        left,right=(ROOT/'artifacts'/directory/x for x in (a,b))
        names=sorted(p.relative_to(left).as_posix() for p in left.rglob('*') if p.is_file())
        if not names or names!=sorted(p.relative_to(right).as_posix() for p in right.rglob('*') if p.is_file()):
            raise ValueError('incomplete replay pair '+directory)
        files=[]
        for name in names:
            if (left/name).read_bytes()!=(right/name).read_bytes():
                raise ValueError('replay mismatch '+directory+'/'+name)
            files.append(dict(first=identity(left/name),second=identity(right/name)))
        replays.append(dict(directory=directory,byte_identical=True,files=files))
    sources=[ROOT/f'src/bhsm/interface/{m}.py' for m in MODULES]
    sources+=[ROOT/f'tests/test_{m}.py' for m in MODULES]
    sources+=[Path(__file__),ROOT/'scripts/evaluate_muon_calibrated_extended_ledger.py',
        ROOT/'scripts/evaluate_muon_calibrated_bosonic_weak_log.py']
    return dict(replays=replays,source_hashes=[identity(p) for p in sources],
        previous_verification=identity(ROOT/'artifacts/muon_calibrated_current_response_20261010/verification.json'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tests',action='store_true')
    parser.add_argument('--audits',action='store_true');args=parser.parse_args()
    record=json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    record.update(evidence())
    record.update(action_selected=False,Gate7_closed=False,complete_observable=False,
        scientific_classification=dict(
            DERIVED='joint intrinsic Higgs/gauge/geometry real action two-jet; full five-component Maxwell Ward and angular closure',
            EVALUATED='actual E1+ full400 source images, mixed geometric derivatives, calibrated bosonic weak logarithm and common-input subtotal',
            CONTROL_ONLY='finite trial maps and off-shell gauge test jets; covariance independence illustration',
            UNEVALUATED='full physical native Pauli response after overlap; finite weak completion; interacting stationary base and branch cutoff',
            OWNER_DEFINITION_GAP='none established'),
        error_scope=dict(
            arithmetic_and_finite_action_tests_are_not_anomaly_bounds=True,
            offshell_Ward_does_not_establish_stationarity=True,
            eight_source_compression_not_invariant=True,
            Lorentz_Hessian_not_native_heat_operator=True,
            bosonic_log_endpoint_diagnostic_not_finite_remainder_bound=True,
            full_observable_error_enclosure=False),
        corrected_failures=[
            'Higgs scale derivative finite-difference test initially sat at an exact zero; changed control premise to nonzero derivative.',
            'FullQ first smoke expected a normalized Gram; restored the literal raw unitTr16 Gram16/3.',
            'Fullweak deterministic uncompressed packet exceeded additive artifact size threshold; final lossless compressed packet preserves every array.',
            'PowerShell rg literal wildcard filenames rejected; repeated with directory and -g patterns.'])
    code=0
    if args.tests:
        record['focused_tests']=execute([sys.executable,'-m','pytest','--noconftest','-q']+
            [f'tests/test_{m}.py' for m in MODULES])
        print(json.dumps(record['focused_tests'],indent=2));code=record['focused_tests']['exit_code']
    if args.audits:
        audits=dict(status=['tools/audit_bhsm_status.py','--format','json'],
            claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],
            precision=['tools/verify_precision.py'],public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5) as pool:
            results=list(pool.map(execute,([sys.executable]+a for a in audits.values())))
        record['publication_audits']=dict(zip(audits,results))
        print(json.dumps(record['publication_audits'],indent=2));code=max(code,max(r['exit_code'] for r in results))
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return code


if __name__=='__main__':raise SystemExit(main())
