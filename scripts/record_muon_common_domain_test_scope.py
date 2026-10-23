"""Record executed primary and seed-only checks without promoting fixtures."""
from pathlib import Path
from hashlib import sha256
import json
ROOT = Path(__file__).resolve().parents[1]


def materialize():
    plan = ROOT/'artifacts/muon_common_domain_publication_plan_20261011'
    tests = (plan/'selected_test_paths.txt').read_text().splitlines()
    logs = [
        ('primary_reached_regression', 'artifacts/muon_common_domain_publication_selected_tests_20261011.log',
         '152 passed in 45.08s', 0, dict(passed=152, failed=0, errors=0)),
        ('seed_only_correct_local_package', 'artifacts/muon_common_domain_seed_only_tests_0455_20261011.log',
         '26 failed, 124 passed, 2 errors in 24.78s', 1, dict(passed=124, failed=26, errors=2)),
        ('seed_only_missing_package_initializers', 'artifacts/muon_common_domain_seed_only_tests_0435_20261011.log',
         '57 errors in 1.28s', 2, dict(passed=0, collection_errors=57))]
    rows = []
    for name, path, marker, exit_code, counts in logs:
        raw = (ROOT/path).read_bytes()
        text = raw.decode('utf8')
        if marker not in text:
            raise ValueError('recorded executed output differs: '+path)
        rows.append(dict(check=name, path=path, sha256=sha256(raw).hexdigest(), bytes=len(raw),
            argv=['C:\\Python314\\python.exe', '-m', 'pytest', '--noconftest', '-q', *tests],
            exit_code=exit_code, actual_output_summary=marker, counts=counts,
            environment=dict(PYTHONPATH='src;scripts', OPENBLAS_NUM_THREADS='1')))
    scratch = Path('C:/Users/carbe/Downloads/BHSM_common_domain_regeneration_smoke_20261012_0455')
    setup = (scratch/'regeneration_setup.json').read_bytes()
    result = dict(classification='EXECUTED_REGRESSION_AND_SEED_ONLY_TEST_SCOPE_WITH_FAILURES_RETAINED',
        checks=rows, package_initializer_fix_executed=True,
        seed_only_directory=str(scratch), seed_only_setup_sha256=sha256(setup).hexdigest(),
        setup_receipt=json.loads(setup), selected_test_file_count=len(tests),
        primary_worktree=str(ROOT),
        seed_only_failure_scope='26 failures and2 fixture setup errors: generated predecessor artifacts were absent; the corrected copy resolves local imports and124 checks pass',
        earlier_collection_error_scope='copied source lacked regular-package initializers, so an installed editable bhsm package won import resolution; fixed in setup helper',
        generated_predecessor_producers_executed_in_scratch=False,
        clean_numerical_regeneration_proved=False,
        physical_matching_or_anomaly_error_enclosed=False)
    out = ROOT/'artifacts/muon_common_domain_test_scope_20261012'
    out.mkdir(parents=True, exist_ok=True)
    receipt = out/'verification.json'
    receipt.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(verification_sha256=sha256(receipt.read_bytes()).hexdigest(),
        primary_passed=152, seed_only_passed=124, seed_only_fixture_failures=26,
        seed_only_fixture_errors=2, clean_numerical_regeneration_proved=False)))


if __name__ == '__main__':
    materialize()
