"""Run the selected unchanged tests, preserving each new result and log."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(cwd: Path, label: str, focused_paths: list[str] | None = None) -> None:
    log, receipt = HERE/(label+'.log'), HERE/(label+'.json')
    if log.exists() or receipt.exists():
        raise FileExistsError('preserve previous regression evidence: '+label)
    plan_path = HERE/'publication_plan.json'
    plan = json.loads(plan_path.read_bytes())
    paths = focused_paths or plan['selected_test_paths']
    if not set(paths) <= set(plan['selected_test_paths']):
        raise ValueError('focused tests must belong to the publication selection')
    tests = {}
    for name in paths:
        source, copied = ROOT/name, cwd/name
        digest = sha256(source.read_bytes()).hexdigest()
        if sha256(copied.read_bytes()).hexdigest() != digest:
            raise ValueError('test copy differs: '+name)
        tests[name] = digest
    argv = ['C:/Python314/python.exe', '-m', 'pytest', '--noconftest', '-q', *paths]
    environment = dict(PYTHONPATH='src;scripts', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    start = time.time()
    process = subprocess.run(argv, cwd=cwd, env=dict(os.environ, **environment),
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    elapsed = time.time()-start
    log.write_bytes(process.stdout)
    summary = process.stdout.decode('utf8', errors='replace')
    result = dict(classification='EXECUTED_SELECTED_REGRESSION_WITH_EXACT_TEST_BYTES',
        argv=argv, working_directory=str(cwd), environment=environment,
        elapsed_seconds=elapsed, exit_code=process.returncode, selected_test_files=len(paths),
        selected_test_sha256=tests, selection_plan_sha256=sha256(plan_path.read_bytes()).hexdigest(),
        stdout_log=log.relative_to(ROOT).as_posix(), stdout_sha256=sha256(process.stdout).hexdigest(),
        passed=int(re.search(r'(\d+) passed', summary).group(1)) if re.search(r'(\d+) passed', summary) else None,
        complete_selected_suite_executed=set(paths)==set(plan['selected_test_paths']),
        fixtures_and_imports_are_computational_regression_inputs=True,
        full_numerical_producer_regeneration_proved=False, physical_matching_proved=False,
        previous_logs_overwritten=False)
    receipt.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({k:result[k] for k in ('selected_test_files', 'passed', 'exit_code', 'elapsed_seconds', 'stdout_sha256')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--test-path', action='append')
    args = parser.parse_args()
    if re.fullmatch(r'[a-z0-9_]+', args.label) is None:
        raise ValueError('use a simple new evidence label')
    run(args.cwd.resolve(), args.label, args.test_path)
