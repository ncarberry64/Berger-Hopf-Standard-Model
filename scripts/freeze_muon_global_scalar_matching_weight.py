"""Freeze actual global scalar matching and same-clock endpoint comparisons."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/muon_global_scalar_matching_weight_20261011'


def freeze(output):
    out = ROOT/output
    if out.exists():
        raise FileExistsError('preserve every immutable scalar matching verification')
    folders = [BASE/f'run_{k}' for k in (3, 4)]
    names = [sorted(p.name for p in f.iterdir() if p.is_file()) for f in folders]
    if names[0] != names[1] or any((folders[0]/n).read_bytes() != (folders[1]/n).read_bytes() for n in names[0]):
        raise ArithmeticError('independent scalar matching replays differ')
    if any(p.is_file() for p in (BASE/'run_1').rglob('*')):
        raise ArithmeticError('failed pre-export probe must not supply numerical arrays')
    selected = {}

    def pin(path):
        path = Path(path)
        selected[path.relative_to(ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()

    def snapshot(name, original):
        path = out/name
        path.write_text(original.read_text(encoding='utf8'), encoding='utf8', newline='\n')
        pin(path)
        return dict(stdout_stderr=path.relative_to(ROOT).as_posix(), original_log_path=str(original),
                    original_log_sha256=sha256(original.read_bytes()).hexdigest())

    out.mkdir(parents=True)
    runs = []
    for k, folder in zip((3, 4), folders):
        result = json.loads((folder/'result.json').read_bytes())
        for name in names[0]:
            path = folder/name
            if path.stat().st_size >= 10*1024**2:
                raise ArithmeticError('publication archive exceeds the retained cap')
            pin(path)
        for path, digest in result['input_hashes'].items():
            if sha256((ROOT/path).read_bytes()).hexdigest() != digest:
                raise RuntimeError('same matching/source/comparison changed: '+path)
            selected[path] = digest
        log = Path('C:/Users/carbe/Downloads')/f'BHSM_global_scalar_matching_weight_run_{k}.stdout.txt'
        argv = ['C:\\Python314\\python.exe', 'scripts/evaluate_muon_global_scalar_matching_weight.py',
                '--output', folder.relative_to(ROOT).as_posix()]
        runs.append(dict(argv=argv, completed_exit_code=0, working_directory=str(ROOT),
            environment={'PYTHONPATH': 'src;.', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'},
            **snapshot(f'run_{k}.stdout.txt', log),
            executed_powershell_command="$env:PYTHONPATH='src;.'; $env:OPENBLAS_NUM_THREADS='1'; "
                "$env:OMP_NUM_THREADS='1'; "+' '.join(argv)+
                ' 2>&1 | Tee-Object -FilePath '+str(log)+'; exit $LASTEXITCODE'))
    test_log = Path('C:/Users/carbe/Downloads/BHSM_global_scalar_matching_weight_tests.stdout.txt')
    test = dict(argv=['C:\\Python314\\python.exe', '-m', 'pytest', '--noconftest', '-q',
                     'tests/test_muon_global_scalar_matching_weight.py'], completed_exit_code=0,
                **snapshot('focused_tests.stdout.txt', test_log))
    failed = dict(completed_exit_code=1, scientific_arrays_written=False,
        consumed_as_scientific_application=False,
        failure='pre-export reader requested an excluded complex scalar key; corrected by the exact saved proper-clock node difference',
        **snapshot('failed_run_1.stdout.txt', Path('C:/Users/carbe/Downloads/BHSM_global_scalar_matching_weight_run_1.stdout.txt')))
    diagnostic = json.loads((BASE/'run_2/result.json').read_bytes())
    preserved_probe = dict(completed_exit_code=0, result_sha256=sha256((BASE/'run_2/result.json').read_bytes()).hexdigest(),
        archive_hashes=diagnostic['archives'],
        preserved_output_directory=(BASE/'run_2').relative_to(ROOT).as_posix(),
        consumed_as_canonical_application=False,
        correction='phase maximum mislabeled future although evaluated over all original points; numerical arrays unchanged, fixed canonical run3/run4 label')
    verification = dict(classification='VERIFIED_GLOBAL_SCALAR_SAME_CLOCK_MATCHING_AND_REFERENCE_PAIR',
        runs=runs, focused_tests=test, identical_files_per_run=len(names[0]),
        result_sha256=sha256((folders[0]/'result.json').read_bytes()).hexdigest(),
        preserved_failed_pre_export_probe=failed, preserved_metadata_probe=preserved_probe,
        original_complex_clock_and_diagonal_spectator_trace_retained=True,
        reference_from_literal_signed_action_with_same_initial_Cauchy_domain=True,
        impulse_and_both_nonzero_final_conormal_contacts_retained=True,
        no_static_meromorphic_reference_or_old_high_frequency_tail_graft=True,
        q6_q8_difference_is_outward_error_enclosure=False,
        omitted_y_above_32_or_physical_Pauli_selected=False)
    path = out/'verification.json'
    path.write_text(json.dumps(verification, indent=2, sort_keys=True)+'\n', encoding='utf8', newline='\n')
    pin(path)
    pin(Path(__file__))
    path = out/'publication_manifest.json'
    path.write_text(json.dumps(dict(classification='FROZEN_GLOBAL_SAME_CLOCK_SCALAR_MATCHING_MANIFEST',
        files=dict(sorted(selected.items())), file_count=len(selected)), indent=2, sort_keys=True)+'\n',
        encoding='utf8', newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(path.read_bytes()).hexdigest(),
        verification_sha256=sha256((out/'verification.json').read_bytes()).hexdigest(),
        result_sha256=verification['result_sha256'], files=len(selected), identical_files_per_run=len(names[0]))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    freeze(parser.parse_args().output)
