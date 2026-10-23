"""Capture each independent local-action producer process without rerunning old controls."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
LOG = Path(__file__).resolve().parent
PHASES = {
    'incoming': 'artifacts/muon_finite_normal_phase_20261011/incoming_run_1',
    'outgoing': 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1',
}


def main():
    side, number = sys.argv[1:]
    name = f'{side}_run_{number}'
    argv = [sys.executable, 'scripts/evaluate_muon_local_wick_action.py',
        '--phase-directory', PHASES[side], '--output',
        f'artifacts/muon_local_wick_action_20261011/{name}']
    env = dict(os.environ, PYTHONPATH='src')
    proc = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True)
    (LOG/f'{name}.stdout.txt').write_bytes(proc.stdout)
    (LOG/f'{name}.stderr.txt').write_bytes(proc.stderr)
    command = dict(argv=argv, cwd=str(ROOT), environment_overrides={'PYTHONPATH': 'src'},
        exit_code=proc.returncode, stdout_path=f'{name}.stdout.txt', stderr_path=f'{name}.stderr.txt')
    (LOG/f'{name}.command.json').write_text(json.dumps(command, indent=2, sort_keys=True)+'\n',
        encoding='utf8', newline='\n')
    if proc.returncode:
        print(proc.stderr.decode('utf8', errors='replace'))
    else:
        result = json.loads(proc.stdout)
        print(json.dumps({k: result[k] for k in ('side', 'radial_points',
            'local_action_and_weak_contact_continuation_residual_max',
            'ghost_continuation_residual_max', 'Euclidean_coefficient_imaginary_norm_max',
            'same_real_ADM_reference_Maxwell_value_difference_norm', 'numerical_sha256')}, sort_keys=True))
    raise SystemExit(proc.returncode)


if __name__ == '__main__':
    main()
