"""Freeze additive charge-clock replays while preserving the legacy application."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'artifacts/muon_common_domain_charge_source_clock_20261011'


def freeze(output, *, run_chunks, test_chunks):
    out = ROOT/output
    if out.exists():
        raise FileExistsError('preserve each immutable corrected charge verification')
    folders = [BASE/f'run_{k}' for k in (1, 2)]
    names = [sorted(p.name for p in f.iterdir() if p.is_file()) for f in folders]
    if names[0] != names[1] or any((folders[0]/n).read_bytes() != (folders[1]/n).read_bytes()
                                  for n in names[0]):
        raise ArithmeticError('independent corrected charge replays differ')
    selected = {}
    def pin(path, expected=None):
        path = Path(path)
        digest = sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError('corrected/legacy source or archive changed: '+str(path))
        selected[path.relative_to(ROOT).as_posix()] = digest
        return digest
    result = json.loads((folders[0]/'result.json').read_bytes())
    if (result['classification'] != 'EVALUATED_CORRECTED_SOURCE_CELL_CLOCK_COMMON_DOMAIN_HOLOMORPHIC_CHARGE_WEAK_ACTION'
            or sum(result['source_clock_part_counts'].values()) != 3832
            or result['diagnostics']['connector_charge_first_change_max'] != 0
            or result['diagnostics']['legacy_H_first_reconstruction_max'] != 0
            or result['diagnostics']['legacy_charge_first_reconstruction_max'] != 0):
        raise ValueError('actual complete clock correction or frozen connector scope changed')
    for folder in folders:
        for name in names[0]:
            path = folder/name
            if path.stat().st_size >= 10*1024**2:
                raise ArithmeticError('split each original point archive under the cap')
            expected = result['archives'].get(name, {}).get('sha256')
            pin(path, expected)
        for name, digest in result['input_hashes'].items():
            pin(ROOT/name, digest)
    legacy_folders = [ROOT/'artifacts/muon_common_domain_charge_transport_20261011'/f'run_{k}'
                      for k in (3, 4)]
    legacy_names = [sorted(p.name for p in f.iterdir() if p.is_file()) for f in legacy_folders]
    if legacy_names[0] != legacy_names[1] or any((legacy_folders[0]/n).read_bytes() !=
            (legacy_folders[1]/n).read_bytes() for n in legacy_names[0]):
        raise ValueError('preserved frozen legacy charge replay differs')
    for folder in legacy_folders:
        for name in legacy_names[0]:
            pin(folder/name)
    pin(Path(__file__))
    out.mkdir(parents=True)
    commands = [dict(argv=['C:/Python314/python.exe',
                          'scripts/evaluate_muon_common_domain_charge_source_clock.py',
                          '--output', folder.relative_to(ROOT).as_posix()],
                     working_directory=str(ROOT),
                     environment={'PYTHONPATH':'src', 'OPENBLAS_NUM_THREADS':'4'},
                     completed_exit_code=0, completion_chunk=chunk)
                for folder, chunk in zip(folders, run_chunks)]
    verification = dict(classification='VERIFIED_CORRECTED_COMMON_DOMAIN_CHARGE_SOURCE_CLOCK_PAIR',
        runs=commands, identical_files_per_run=len(names[0]),
        result_sha256=sha256((folders[0]/'result.json').read_bytes()).hexdigest(),
        focused_tests=dict(argv=['C:/Python314/python.exe','-m','pytest','-q',
                                'tests/test_muon_common_domain_charge_source_clock.py'],
                           passed=3, completed_exit_code=0, tool_output_chunks=test_chunks),
        old_frozen_charge_sources_and_outputs_preserved=True,
        old_frozen_files_per_run=len(legacy_names[0]),
        source_cells_use_owned_minus_i_over_N=True,
        both_connector_legs_are_bit_exact_unchanged=True,
        all_six_source_directions_and_both_charge_neutral_returns_retained=True,
        independently_transposed_analytic_dual_not_Hilbert_replacement=True,
        source_clock_correction_integral_norm=result['correction_integral_norms']['total_source_direction_clock_correction'],
        active_charge_exchange_not_removed=True,
        mathematical_outward_or_physical_error_enclosure=False,
        physical_pole_charge_or_LSZ_or_Pauli_assigned=False,
        publication_plan_or_legacy_predictions_modified=False)
    vp = out/'verification.json'
    vp.write_text(json.dumps(verification, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    pin(vp)
    mp = out/'publication_manifest.json'
    mp.write_text(json.dumps(dict(classification='FROZEN_ADDITIVE_CORRECTED_CHARGE_CLOCK_MANIFEST',
        files=dict(sorted(selected.items())), file_count=len(selected),
        scope='local full-stream byte replay and input identity; selective publication/regeneration is separate'),
        sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(mp.read_bytes()).hexdigest(),
                         verification_sha256=sha256(vp.read_bytes()).hexdigest(),
                         result_sha256=verification['result_sha256'],
                         files=len(selected), identical_files_per_run=len(names[0]))), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--run-chunks', nargs=2, required=True)
    p.add_argument('--test-chunks', nargs='+', required=True)
    a = p.parse_args()
    freeze(a.output, run_chunks=a.run_chunks, test_chunks=a.test_chunks)
