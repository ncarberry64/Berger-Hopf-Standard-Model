"""Capture an independent original temporal action continuation process."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
LOG = Path(__file__).resolve().parent


def main():
    name = 'run_'+sys.argv[1]
    argv = [sys.executable, 'scripts/evaluate_muon_wick_temporal_action.py', '--output',
        'artifacts/muon_wick_temporal_action_20261011/'+name]
    proc = subprocess.run(argv, cwd=ROOT, env=dict(os.environ, PYTHONPATH='src'), capture_output=True)
    for label, data in (('stdout', proc.stdout), ('stderr', proc.stderr)):
        (LOG/f'{name}.{label}.txt').write_bytes(data.replace(b'\r\n', b'\n'))
    command = dict(argv=argv, cwd=str(ROOT), environment_overrides={'PYTHONPATH': 'src'},
        exit_code=proc.returncode, stdout_path=f'{name}.stdout.txt', stderr_path=f'{name}.stderr.txt',
        captured_text_newline_policy='CRLF normalized to LF; stdout/stderr content unchanged')
    (LOG/f'{name}.command.json').write_text(json.dumps(command, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    if proc.returncode:
        print(proc.stderr.decode('utf8', errors='replace'))
    else:
        lines = proc.stdout.decode('utf8').splitlines()
        result = json.loads(lines[-1]); print(json.dumps(dict(records=result['records'],
            numerical_sha256=result['numerical_sha256']), sort_keys=True))
    raise SystemExit(proc.returncode)


if __name__ == '__main__':
    main()
