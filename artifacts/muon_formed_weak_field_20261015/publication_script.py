"""Publish reproducibility and conservative scope checks, without a solver run."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
OUT = REPO/'artifacts/muon_formed_weak_field_20261015'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return (json.dumps(data, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def check(spec):
    name, extra = spec
    command = [sys.executable, str(REPO/'tools'/name), *extra]
    done = subprocess.run(command, cwd=REPO, env=dict(os.environ,PYTHONPATH=str(REPO/'src')),
                          capture_output=True)
    folder = OUT/'publication_checks'
    folder.mkdir(exist_ok=True)
    for label, value in [('stdout', done.stdout), ('stderr', done.stderr)]:
        (folder/(name+'.'+label+'.txt')).write_bytes(value)
    print(json.dumps(dict(audit=name, exit_code=done.returncode)), flush=True)
    return name, dict(command=command,exit_code=done.returncode,
                      stdout_sha256=sha256(done.stdout).hexdigest(),
                      stderr_sha256=sha256(done.stderr).hexdigest())


def main():
    specs = [('audit_bhsm_status.py', []), ('audit_forbidden_claims.py', []),
             ('audit_frozen_prediction_integrity.py', []), ('verify_precision.py', []),
             ('audit_public_readiness.py', ['--format','json'])]
    with ThreadPoolExecutor(max_workers=5) as pool:
        checks = dict(pool.map(check, specs))
    (OUT/'publication_checks/result.json').write_bytes(encoded(checks))
    original = REPO/'artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
    original_expected = 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    assert digest(original) == original_expected
    binding = OUT/'binding_run_1/result.json'
    assert binding.read_bytes() == (OUT/'binding_run_2/result.json').read_bytes()
    record = json.loads(binding.read_text(encoding='utf8'))
    assert record['selection']['selection_status'] == 'CONFIRMED_BY_USER'
    assert record['physical_status']['physical_magnetic_moment'] is None
    assert record['physical_status']['physical_coupled_matching_corrections_applied'] == 0
    (OUT/'publication_script.py').write_bytes(Path(__file__).read_bytes())
    manifest = dict(
        classification=record['classification'],
        user_benchmark_confirmed=True,
        actual_scientific_repeat_pairs=record['actual_scientific_repeat_pairs'],
        physical_status=record['physical_status'],
        publication_checks=checks,
        original_common_cut_unchanged_sha256=original_expected,
        packet_sha256={p.relative_to(OUT).as_posix():digest(p) for p in sorted(OUT.rglob('*'))
                       if p.is_file() and p.name not in ('publication_manifest_run_1.json','publication_manifest_run_2.json')},
        source_sha256={str(REPO/'audits'/name):value for name,value in record['producer_sha256'].items()},
        publication_binding_is_not_new_physics_solve=True)
    data = encoded(manifest)
    for run in (1,2):
        (OUT/f'publication_manifest_run_{run}.json').write_bytes(data)
    print(json.dumps(dict(manifest_sha256=sha256(data).hexdigest(),
                          all_audits_passed=all(x['exit_code']==0 for x in checks.values()))),flush=True)
    if any(x['exit_code'] for x in checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
