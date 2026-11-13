"""Verify the original three-step constitutive replay and thread diagnostic."""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/muon_complex_canonical_compatibility_20261011'


def materialize():
    out = BASE/'replay_verification.json'
    if out.exists():
        raise FileExistsError('preserve the existing replay verification')
    original = json.loads((BASE/'run_1/result.json').read_bytes())
    pairs = []
    for name in ['result.json', *sorted(original['archives'])]:
        left, right = (BASE/f'run_{k}'/name for k in (1, 3))
        a, b = left.read_bytes(), right.read_bytes()
        if a != b:
            raise ValueError('original-environment replay differs: '+name)
        pairs.append(dict(name=name, bytes=len(a), sha256=sha256(a).hexdigest()))
    for name, digest in original['input_hashes'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise ValueError('consumed action/source pin changed: '+name)
    threaded = json.loads((BASE/'run_2/result.json').read_bytes())
    with np.load(BASE/'run_1/application.npz', allow_pickle=False) as a:
        original_arrays = {k:a[k].copy() for k in a.files}
    with np.load(BASE/'run_2/application.npz', allow_pickle=False) as a:
        single_arrays = {k:a[k].copy() for k in a.files}
    differences = {k:float(np.max(abs(original_arrays[k]-single_arrays[k])))
        for k in original_arrays if np.issubdtype(original_arrays[k].dtype, np.number)}
    commands = []
    for run, threads, log, launch, completion in (
        (2, 1, 'artifacts/muon_complex_canonical_compatibility_replay_20261012.log', 'db32be', 'a1504f'),
        (3, 4, 'artifacts/muon_complex_canonical_compatibility_original_env_replay_20261012.log', '21ee3c', '3aace9')):
        raw = (ROOT/log).read_bytes()
        commands.append(dict(argv=['C:/Python314/python.exe',
            'scripts/evaluate_muon_complex_canonical_compatibility.py', '--output',
            f'artifacts/muon_complex_canonical_compatibility_20261011/run_{run}', '--max-iterations', '3'],
            environment=dict(PYTHONPATH='src;scripts', OPENBLAS_NUM_THREADS=str(threads), OMP_NUM_THREADS=str(threads)),
            exit_code=0, stdout_path=log, stdout_sha256=sha256(raw).hexdigest(),
            launch_tool_chunk=launch, completion_tool_chunk=completion))
    receipt = dict(classification='VERIFIED_ORIGINAL_CONSTITUTIVE_REPLAY_WITH_THREAD_DIFFERENCE_RETAINED',
        byte_identical_original_environment=True, file_pairs=pairs,
        consumed_source_pin_count=len(original['input_hashes']), consumed_source_pins_current=True,
        original_and_same_environment_replay=['run_1', 'run_3'], commands=commands,
        single_thread_result_sha256=sha256((BASE/'run_2/result.json').read_bytes()).hexdigest(),
        single_thread_original_rows_max=threaded['original_rows_max'],
        original_environment_original_rows_max=original['original_rows_max'],
        single_thread_absolute_array_differences=differences,
        rejected_overflow_line_search_trials_remain_in_actual_logs=True,
        input_hashes={'scripts/verify_muon_complex_canonical_replay.py':sha256(Path(__file__).read_bytes()).hexdigest()},
        error_scope='deterministic original finite three-step application; thread sensitivity is diagnostic, not a continuum, physical matching or anomaly error enclosure')
    out.write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(file_pairs=len(pairs), byte_identical_original_environment=True,
        verification_sha256=sha256(out.read_bytes()).hexdigest(),
        single_thread_original_rows_max=threaded['original_rows_max'])))


if __name__ == '__main__':
    materialize()
