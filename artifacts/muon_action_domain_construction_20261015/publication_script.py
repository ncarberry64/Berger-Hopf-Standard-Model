"""Publish finite action checks and the precise unresolved domain variation."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

REPO=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
OUT=REPO/'artifacts/muon_action_domain_construction_20261015'


def digest(path):return sha256(path.read_bytes()).hexdigest()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def check(spec):
    name,args=spec;command=[sys.executable,str(REPO/'tools'/name),*args]
    done=subprocess.run(command,cwd=REPO,env=dict(os.environ,PYTHONPATH=str(REPO/'src')),capture_output=True)
    folder=OUT/'publication_checks';folder.mkdir(exist_ok=True)
    for label,data in (('stdout',done.stdout),('stderr',done.stderr)):
        (folder/(name+'.'+label+'.txt')).write_bytes(data)
    print(json.dumps(dict(audit=name,exit_code=done.returncode)),flush=True)
    return name,dict(command=command,exit_code=done.returncode,stdout_sha256=sha256(done.stdout).hexdigest(),stderr_sha256=sha256(done.stderr).hexdigest())


def main():
    assert (OUT/'binding_run_1.json').read_bytes()==(OUT/'binding_run_2.json').read_bytes()
    binding=json.loads((OUT/'binding_run_1.json').read_bytes())
    for name,value in binding['actual_output_sha256'].items():
        a,b=(OUT/run/name for run in binding['actual_numerical_repeat_pair'])
        assert a.read_bytes()==b.read_bytes()and digest(a)==value
    for path,value in binding['physical_definition_source_sha256'].items():assert digest(REPO/path)==value
    assert digest(REPO/'audits/bhsm_two_arm_directional_action_check_20261015.py')==binding['producer_sha256']
    assert not binding['full_physical_derivative_passed']
    assert binding['physical_magnetic_moment']is None and binding['coupled_matching_corrections_applied']==0
    specs=[('audit_bhsm_status.py',[]),('audit_forbidden_claims.py',[]),
        ('audit_frozen_prediction_integrity.py',[]),('verify_precision.py',[]),
        ('audit_public_readiness.py',['--format','json'])]
    with ThreadPoolExecutor(max_workers=5)as pool:checks=dict(pool.map(check,specs))
    (OUT/'publication_checks/result.json').write_bytes(encoded(checks))
    original=REPO/'artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
    expected='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    assert digest(original)==expected
    (OUT/'publication_script.py').write_bytes(Path(__file__).read_bytes())
    report=dict(classification=binding['classification'],binding_sha256=digest(OUT/'binding_run_1.json'),
        publication_checks=checks,original_common_cut_unchanged_sha256=expected,
        actual_finite_directional_action_diagnostic_runs=2,physical_exterior_solutions=0,
        full_physical_derivative_passed=False,physical_two_spin_normalization=None,
        physical_magnetic_moment=None,coupled_matching_corrections_applied=0,
        packet_sha256={p.relative_to(OUT).as_posix():digest(p)for p in sorted(OUT.rglob('*'))
            if p.is_file()and p.name not in ('publication_manifest_run_1.json','publication_manifest_run_2.json')},
        publication_serialization_is_not_a_physics_evaluation=True)
    payload=encoded(report)
    for i in (1,2):(OUT/f'publication_manifest_run_{i}.json').write_bytes(payload)
    print(json.dumps(dict(manifest_sha256=sha256(payload).hexdigest(),all_five_publication_audits_passed=all(v['exit_code']==0 for v in checks.values()))),flush=True)
    if any(v['exit_code']for v in checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
