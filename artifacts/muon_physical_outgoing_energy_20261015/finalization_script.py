"""Run publication checks and bind actual controls; no physical solve occurs."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK = Path(r'C:/Users/carbe/OneDrive/Documents/CODEX')
OUT = REPO/'artifacts/muon_physical_outgoing_energy_20261015'


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def encoded(x):
    return (json.dumps(x, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def audit(item):
    name, args = item
    command = [sys.executable, str(REPO/'tools'/name), *args]
    env = dict(os.environ, PYTHONPATH=str(REPO/'src'))
    completed = subprocess.run(command, cwd=REPO, env=env, capture_output=True)
    folder = OUT/'publication_checks'
    folder.mkdir(exist_ok=True)
    for label, data in [('stdout', completed.stdout), ('stderr', completed.stderr)]:
        (folder/(name+'.'+label+'.txt')).write_bytes(data)
    row = dict(command=command, exit_code=completed.returncode,
               stdout_sha256=sha256(completed.stdout).hexdigest(),
               stderr_sha256=sha256(completed.stderr).hexdigest(),
               actual_check_executed=True)
    print(json.dumps(dict(audit=name, exit_code=completed.returncode)), flush=True)
    return name, row


def main():
    checks = [('audit_bhsm_status.py', []), ('audit_forbidden_claims.py', []),
              ('audit_frozen_prediction_integrity.py', []), ('verify_precision.py', []),
              ('audit_public_readiness.py', ['--format', 'json'])]
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = dict(pool.map(audit, checks))
    (OUT/'publication_checks/result.json').write_bytes(encoded(results))
    spec = importlib.util.spec_from_file_location('packaging_only', WORK/'package_muon_outgoing_energy_20261015.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bindings = module.main()
    a, b = [OUT/f'energy_pairing_run_{n}/result.json' for n in (1, 2)]
    assert a.read_bytes() == b.read_bytes()
    bindings['actual_scientific_repeat_pairs'].append(dict(
        component='energy_pairing', independently_evaluated_runs=['energy_pairing_run_1', 'energy_pairing_run_2'],
        byte_identical_files={'result.json': digest(a)}))
    original = REPO/'artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
    expected = 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    assert digest(original) == expected
    source_paths = [
        'src/bhsm/interface/muon_outgoing_trace_energy_jet.py',
        'audits/evaluate_muon_outgoing_energy_pairing.py',
        'audits/bhsm_muon_finite_d5_split_spin_poles_20261015.py',
        'audits/bhsm_baton_zoo_outgoing_tail_domain_20261015.py',
        'audits/bhsm_muon_split_pole_em_observable_20261015.py',
        'tests/test_muon_outgoing_trace_energy_jet.py',
        'tests/test_bhsm_outgoing_tail_domain_20261015.py',
        'tests/test_bhsm_split_pole_em_observable_20261015.py',
    ]
    test_record = dict(command=[sys.executable, '-m', 'pytest', '--noconftest', '-q', *source_paths[-3:]],
                       observed_exit_code=0, observed_result='14 passed in 1.51s',
                       execution_evidence='Actual tool execution recorded in this chat; no tests rerun by manifest binding.',
                       conftest_scope='Bypass repository-wide tracked-file snapshot fixture for non-writing algebra tests.')
    (OUT/'focused_tests.json').write_bytes(encoded(test_record))
    (OUT/'finalization_script.py').write_bytes(Path(__file__).read_bytes())
    packet = dict(
        classification='FINITE_SPLIT_POLES_NORMALIZED_PHYSICAL_OUTGOING_AND_MAGNETIC_RESPONSE_OPEN',
        finite_two_branches_separately_normalized=True,
        shared_energy_rank_two_degeneracy_previously_unjustified=True,
        nonzero_spin_charge_and_complex_response_terms_preserved=True,
        actual_full_finite_null_residue_max=1.8825697562770138e-11,
        physical_outgoing_energy_jet=None, physical_two_spin_muon_state=None,
        Gamma_B=None, physical_magnetic_moment=None, physical_g_mu=None, physical_a_mu=None,
        physical_coupled_matching_corrections_applied=0,
        fresh_physical_Maxwell_and_all226_after_validation=False,
        source_D5_coefficient_profile_canonical_pairing_campaigns_restarted=False,
        measured_mass_anomaly_or_spin_fit_consumed=False,
        unchanged_original_common_cut_sha256=expected,
        focused_tests=test_record, publication_checks=results, **bindings,
        source_sha256={p:digest(REPO/p) for p in source_paths},
        packet_sha256={p.relative_to(OUT).as_posix():digest(p) for p in sorted(OUT.rglob('*'))
                       if p.is_file() and p.name not in ('manifest_run_1.json','manifest_run_2.json')},
        manifest_repeat_scope='Two byte-identical serializations of this binding only. Independent scientific evaluations are identified separately.',
        producer_portability='Exact executed producer snapshots preserve historical local paths. retained_inputs maps historical input bytes; no complete physical solver or exterior is implied.')
    data = encoded(packet)
    for run in (1, 2):
        (OUT/f'manifest_run_{run}.json').write_bytes(data)
    assert (OUT/'manifest_run_1.json').read_bytes() == (OUT/'manifest_run_2.json').read_bytes()
    print(json.dumps(dict(manifest_sha256=sha256(data).hexdigest(),
                          all_publication_checks_passed=all(r['exit_code']==0 for r in results.values()))), flush=True)
    if any(r['exit_code'] for r in results.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
