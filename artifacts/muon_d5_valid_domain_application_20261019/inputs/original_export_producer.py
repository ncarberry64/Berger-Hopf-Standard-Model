"""Export existing BHSM retained histories for the next integrated response.

This is an INPUT EXPORT, not a physical solve, a new action, or a milestone
certificate. It calls the repository's own validated sampler. It does not
change repository files or choose fields, magnetic ramps, or a quantum state.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np

ANCHOR = '70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde'
SCHEMA = 'BHSM_RETAINED_HISTORY_RESPONSE_INPUTS_V1'
OWNER_FILES = (
    'scripts/evaluate_em_carrier_original_maxwell_20261016.py',
    'scripts/bhsm_real_full_d5_combined_eta_open_form_20261016.py',
    'src/bhsm/interface/muon_profile_preserving_phase_sample.py',
    'src/bhsm/interface/muon_birth_trace_enriched_action.py',
    'src/bhsm/interface/muon_holomorphic_normal_geometry.py',
    'src/bhsm/interface/muon_holomorphic_d5_trace_action.py',
    'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
    'src/bhsm/interface/muon_electromagnetic_soft_magnetic_source.py',
)
PHYSICAL_FLAGS = {
    'new_physical_collider_state': False,
    'physical_quantum_reference_selected': False,
    'radial_form_domain_complete': False,
    'retarded_response_executed': False,
    'complete_source_domain_derivative_admitted': False,
    'physical_Maxwell_or_226_after_state_evaluated': False,
    'coupled_corrections': 0,
    'a_mu': None, 'g_mu': None, 'total_uncertainty': None,
}


def digest(path: Path) -> str:
    h = sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, complex):
        return {'real': value.real, 'imag': value.imag}
    if isinstance(value, Path):
        return str(value)
    return value


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_bytes(data)
    os.replace(tmp, path)


def npz_bytes(arrays: dict[str, np.ndarray]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, value in sorted(arrays.items()):
            if '/' in name or '\\' in name or not name:
                raise ValueError('simple array names required')
            a = np.asarray(value)
            if a.dtype.hasobject or not np.isfinite(a).all():
                raise ValueError(f'{name}: finite non-object array required')
            b = io.BytesIO()
            np.lib.format.write_array(b, a, allow_pickle=False)
            info = zipfile.ZipInfo(name + '.npy', (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, b.getvalue(), compresslevel=6)
    return buffer.getvalue()


def atomic_npz(path: Path, arrays) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = npz_bytes(arrays)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return sha256(data).hexdigest()


def compact_background(a: np.ndarray, angular_points: int):
    """Lossless removal of a repeated angular axis; never average/project."""
    a = np.asarray(a)
    if a.ndim < 2 or a.shape[1] != angular_points:
        raise ValueError('expected (radial, angular, ...) original snapshot')
    original_shape = list(a.shape)
    if np.array_equal(a, np.broadcast_to(a[:, :1], a.shape)):
        return a[:, 0].copy(), {
            'encoding': 'exact_angular_repeat', 'original_shape': original_shape,
        }
    return a.copy(), {'encoding': 'full', 'original_shape': original_shape}


def reconstruct_background(a, metadata):
    a = np.asarray(a)
    if metadata['encoding'] == 'full':
        return a
    if metadata['encoding'] != 'exact_angular_repeat':
        raise ValueError('unknown array encoding')
    return np.broadcast_to(a[:, None], metadata['original_shape']).copy()


def require_outside_repository(repo: Path, output: Path) -> None:
    if output == repo or output.is_relative_to(repo):
        raise ValueError('output must be outside the repository; use Downloads')


def git_read(repo: Path, *args: str) -> str:
    p = subprocess.run(['git', '-C', str(repo), *args], text=True,
                       capture_output=True, check=False)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or f'git read failed: {args}')
    return p.stdout.strip()


def validated_snapshot(snap, raw_sample, count):
    arrays = {
        'rho': np.asarray(snap['rho']),
        'radial_quadrature': np.asarray(snap['wr']),
        'radial_basis': np.asarray(snap['b']),
        'radial_derivative_basis': np.asarray(snap['br']),
        'raw_fields': np.asarray(raw_sample['raw_fields']),
        'raw_coordinate_time_derivative': np.asarray(raw_sample['raw_coordinate_time_derivative']),
        'H_selected_charge_coefficients': np.asarray(snap['charge']),
        'H_selected_charge_coordinate_rate': np.asarray(snap['charge_rate']),
        'EM_inclusion': np.asarray(snap['s']),
        'EM_inclusion_coordinate_rate': np.asarray(snap['sd']),
        'geometric_reference_gram20': np.asarray(snap['gram']),
        'seed_electric_gram': np.asarray(snap['kinetic']),
    }
    layouts = {}
    names = ('connection_value', 'connection_coordinate_time',
             'connection_radial', 'connection_angular')
    for name, field in zip(names, snap['fields'], strict=True):
        arrays[name], layouts[name] = compact_background(field, count)
        if not np.array_equal(reconstruct_background(arrays[name], layouts[name]), field):
            raise ArithmeticError('lossless snapshot packing failed')
    arrays['metric_densities'], layouts['metric_densities'] = compact_background(snap['densities'], count)
    c = snap['c']
    required = ('lapse', 'radial_coframe', 'radius', 'coordinate_shift', 'volume_density',
                'material_wall_velocity', 'intrinsic_H_realified',
                'intrinsic_H_realified_first', 'mechanical_profile')
    for name in required:
        if name not in c:
            raise ValueError(f'live coefficient contract lacks {name}; do not fabricate it')
        arrays['coefficient_' + name] = np.asarray(c[name])
    for name in ('surface_proper_clock_rate', 'gauge_connection_material',
                 'gauge_connection_material_first'):
        if name in c:
            arrays['coefficient_' + name] = np.asarray(c[name])
    if arrays['rho'].ndim != 1 or arrays['rho'].size == 0:
        raise ValueError('nonempty original radial nodes required')
    if not np.all(arrays['radial_quadrature'] > 0):
        raise ValueError('positive original radial quadrature required')
    if arrays['radial_basis'].shape != arrays['radial_derivative_basis'].shape:
        raise ValueError('radial value/derivative bases differ')
    if arrays['raw_fields'].shape != (268,):
        raise ValueError('this export schema requires the retained raw268 chart')
    for a in arrays.values():
        if a.dtype.hasobject or not np.isfinite(a).all():
            raise ValueError('snapshot contains unavailable/nonfinite coefficients')
    return arrays, layouts


def export(repository: Path, output: Path, radial_order: int, time_order: int) -> Path:
    repo = repository.expanduser().resolve()
    out = output.expanduser().resolve()
    require_outside_repository(repo, out)
    if not (repo / 'src/bhsm/interface').is_dir():
        raise FileNotFoundError('the specified path is not the BHSM worktree')
    if radial_order < 4 or time_order < 2:
        raise ValueError('radial_order>=4 and time_order>=2 required')
    for name in OWNER_FILES:
        if not (repo / name).is_file():
            raise FileNotFoundError(f'required live owner: {name}')
    head = git_read(repo, 'rev-parse', 'HEAD')
    source_hashes = {name: digest(repo / name) for name in OWNER_FILES}
    config = dict(schema=SCHEMA, head=head, source_hashes=source_hashes,
                  radial_order=radial_order, time_order=time_order,
                  exporter_sha256=digest(Path(__file__)),
                  repository=str(repo), historical_anchor=ANCHOR)
    checkpoint_path = out / 'CHECKPOINT.json'
    if out.exists():
        if not checkpoint_path.is_file():
            raise FileExistsError('existing output has no compatible checkpoint; use another path')
        checkpoint = json.loads(checkpoint_path.read_text(encoding='utf-8'))
        if checkpoint['configuration'] != config:
            raise ValueError('resume configuration/source epoch differs; preserve it and use another path')
    else:
        out.mkdir(parents=True)
        checkpoint = {'configuration': config, 'status': 'EXPORTING_INPUTS',
                      'completed_samples': {}, 'physical_flags': PHYSICAL_FLAGS}
        atomic_json(checkpoint_path, checkpoint)
    completed_archive = out.with_suffix('.zip')
    if checkpoint.get('status') == 'RETAINED_INPUT_EXPORT_COMPLETE_NOT_A_SOLVE' and completed_archive.is_file():
        manifest = json.loads((out / 'SHA256SUMS.json').read_text(encoding='utf-8'))
        if not all((out / name).is_file() and digest(out / name) == expected
                   for name, expected in manifest.items()):
            raise ValueError('completed export failed its file integrity checks')
        print(f'EXISTING COMPLETE INPUT EXPORT PRESERVED: {completed_archive}', flush=True)
        return completed_archive
    sys.path[:0] = [str(repo / 'src'), str(repo / 'scripts'), str(repo)]
    original = importlib.import_module('evaluate_em_carrier_original_maxwell_20261016')
    sampling = importlib.import_module('bhsm.interface.muon_profile_preserving_phase_sample')
    space = original.even_angular_space()
    # Only background coefficients are compacted. This does not use the even
    # quadrature to certify new odd-source products or a nonlinear action.
    angular = {k: np.asarray(space[k]) for k in ('quaternions', 'weights', 'values',
                                               'derivatives', 'mode_coefficients')}
    atomic_npz(out / 'reference_angular_frame.npz', angular)
    atomic_json(out / 'reference_angular_frame.json', {
        'labels': space['labels'], 'scope': 'existing frame and background sampling only; not a new quadrature certificate',
    })
    phase_records = {}
    q, w = np.polynomial.legendre.leggauss(time_order)
    try:
        for side, phase_path in original.PHASES.items():
            # The original loader checks the actual archives and source hashes.
            phase = sampling.load_profile_preserving_phase(phase_path, repository=repo)
            receipt = phase['receipt']
            span, cells = float(receipt['span']), int(receipt['steps'])
            if cells != 1:
                raise ValueError('this exporter preserves the specified one-cell scope; newer multi-cell data need explicit one-sided-face support')
            lo, hi = sorted((0., span))
            if hi <= lo:
                raise ValueError('nonzero signed phase required')
            ts = lo + (q + 1.) * (hi - lo) / 2.
            ws = w * (hi - lo) / 2.
            targets = [('lo', lo, 0.), *[(f'q{k:03d}', float(t), float(ww))
                                       for k, (t, ww) in enumerate(zip(ts, ws))],
                       ('hi', hi, 0.)]
            pins = phase['input_hashes']
            old_pins = out / side / 'original_input_hashes.json'
            if old_pins.exists() and json.loads(old_pins.read_text(encoding='utf-8')) != jsonable(pins):
                raise ValueError('retained phase inputs changed across resume; use a new output path')
            atomic_json(out / side / 'original_phase_receipt.json', receipt)
            atomic_json(out / side / 'original_input_hashes.json', pins)
            representation = phase['representation']
            needed_arrays = ('affine_profile_reference_states', 'affine_interior_projection',
                             'affine_difference_coefficients', 'wall_trace_map', 'wall_radial_derivative_map')
            radial_arrays = {k: np.asarray(representation[k]) for k in needed_arrays}
            radial_metadata = {k: representation[k] for k in (
                'affine_wall_coefficient', 'affine_complement_norm', 'gauge_labels', 'gauge_count')}
            atomic_npz(out / side / 'original_radial_frame.npz', radial_arrays)
            atomic_json(out / side / 'original_radial_frame.json', radial_metadata)
            saved = {k: phase['arrays'][k] for k in (
                phase['stage_key'], 'coordinate_lift', 'initial_pair', 'reference_pair',
                'initial_raw', 'initial_master', 'initial_p', 'stage_initial_face', 'stage_final_face')
                     if k in phase['arrays']}
            saved['resolved_phase_coordinate_lift'] = phase['coordinates']['lift']
            atomic_npz(out / side / 'phase_reconstruction_operands.npz', saved)
            for label, t, temporal_weight in targets:
                key = f'{side}/{label}'
                name = f'{key}.npz'
                if key in checkpoint['completed_samples']:
                    record = checkpoint['completed_samples'][key]
                    if digest(out / name) != record['sha256']:
                        raise ValueError(f'saved export changed: {name}')
                    continue
                # Reconstruct once through the existing original source chain.
                # No weak Hessian or known frequency-precision sprint is rerun.
                snap = original.snapshot(phase, t, radial_order, space)
                raw_sample = sampling.profile_preserving_raw_sample(phase, t)
                arrays, layouts = validated_snapshot(snap, raw_sample, len(space['weights']))
                sha = atomic_npz(out / name, arrays)
                record = dict(path=name, sha256=sha, coordinate_time=t,
                              positive_time_quadrature=temporal_weight,
                              source_signed_span=span, side=side, stage=raw_sample['stage'],
                              layout=layouts, one_sided_inside_cell_derivative=True)
                atomic_json(out / f'{key}.json', record)
                checkpoint['completed_samples'][key] = record
                atomic_json(checkpoint_path, checkpoint)
                print(f'SAVED {key}: t={t:.17g}; original radial nodes={radial_order}', flush=True)
            phase_records[side] = dict(path=str(phase_path), signed_span=span, steps=cells,
                                      original_archive_hashes=pins,
                                      x_count=phase['coordinates']['x_count'])
        # Preserve exact owner text for checking the narrow extraction contract.
        for name in OWNER_FILES:
            if digest(repo / name) != source_hashes[name]:
                raise RuntimeError(f'owner changed during export: {name}')
            dest = out / 'source_snapshot' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((repo / name).read_bytes())
        atomic_json(out / 'MANIFEST.json', {
            'schema': SCHEMA, 'configuration': config, 'phases': phase_records,
            'field_order': ['At', 'Ar', 'A1', 'A2', 'A3'],
            'density_order': ['electric', 'radial', 'angular', 'electric_radial', 'shift'],
            'MAXWELL_TO_CAP': original.MAXWELL_TO_CAP, 'WALL': original.WALL,
            'git_status_tracked_only': git_read(repo, 'status', '--short', '--untracked-files=no'),
            'physical_flags': PHYSICAL_FLAGS,
            'scope': 'source-validated retained provisional histories; not adopted-collider initial fields or a quantum reference',
            'source_derivative_scope': 'original inside-cell time jets; no total magnetic/energy/preparation derivative supplied',
            'source_reconstruction': 'original snapshot/sample_coefficients; parent/reference clock motion is not replaced by zero',
            'sampling_scope': 'one temporal quadrature and existing radial sampling; no convergence bound claimed',
            'not_supplied': ['physical particle and daughter sections', 'physical inherited reference',
                             'complete interface/native magnetic jets', 'physical retarded exterior completion'],
        })
        (out / 'export_producer.py').write_bytes(Path(__file__).read_bytes())
        checkpoint['status'] = 'RETAINED_INPUT_EXPORT_COMPLETE_NOT_A_SOLVE'
        atomic_json(checkpoint_path, checkpoint)
        files = [p for p in sorted(out.rglob('*')) if p.is_file() and not p.name.endswith('.tmp')
                 and p.name != 'SHA256SUMS.json']
        atomic_json(out / 'SHA256SUMS.json', {p.relative_to(out).as_posix(): digest(p) for p in files})
        archive = out.with_suffix('.zip')
        if archive.exists():
            raise FileExistsError('completed archive already exists; it is preserved')
        temp_archive = archive.with_name(archive.name + '.tmp')
        with zipfile.ZipFile(temp_archive, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file() and not p.name.endswith('.tmp'):
                    z.write(p, out.name + '/' + p.relative_to(out).as_posix())
        os.replace(temp_archive, archive)
        print(f'EXPORT COMPLETE: {archive}', flush=True)
        print('No physical response, correction, magnetic moment, or Git write was performed.', flush=True)
        return archive
    except Exception as exc:
        checkpoint['status'] = 'INTERRUPTED_INPUT_EXPORT'
        checkpoint['last_error'] = f'{type(exc).__name__}: {exc}'
        atomic_json(checkpoint_path, checkpoint)
        raise


def self_test() -> dict:
    """Storage/transport tests only; NOT a numerical BHSM calculation."""
    import tempfile
    passed = []
    x = np.arange(24.).reshape(3,2,4)
    repeated = np.broadcast_to(x[:, None], (3, 5, 2, 4)).copy()
    a, meta = compact_background(repeated, 5)
    assert np.array_equal(reconstruct_background(a, meta), repeated)
    passed.append('exact_repeated_axis_roundtrip')
    changed = repeated.copy(); changed[1, 2, 0, 0] += 0.25
    a, meta = compact_background(changed, 5)
    assert meta['encoding'] == 'full' and np.array_equal(reconstruct_background(a, meta), changed)
    passed.append('nonhomogeneous_fields_not_projected')
    payload = {'real': x, 'analytic_left': x.astype(complex) + 0.25j}
    one, two = npz_bytes(payload), npz_bytes(payload)
    assert one == two
    with np.load(io.BytesIO(one), allow_pickle=False) as z:
        assert all(np.array_equal(z[k], v) for k, v in payload.items())
    passed.append('deterministic_npz_and_complex_roundtrip')
    try:
        npz_bytes({'bad': np.array([np.nan])})
    except ValueError:
        passed.append('nonfinite_data_rejected')
    else:
        raise AssertionError('NaN was accepted')
    with tempfile.TemporaryDirectory() as temp:
        p = Path(temp)
        try:
            require_outside_repository(p, p/'generated')
        except ValueError:
            passed.append('repository_output_rejected')
        else:
            raise AssertionError('output inside repository was accepted')
        atomic_json(p/'test.json', {'none': None, 'z': 1+2j})
        assert json.loads((p/'test.json').read_text())['z'] == {'real': 1., 'imag': 2.}
        assert not (p/'test.json.tmp').exists()
        passed.append('atomic_json_roundtrip')
    assert PHYSICAL_FLAGS['coupled_corrections'] == 0 and PHYSICAL_FLAGS['a_mu'] is None
    passed.append('physical_flags_remain_unclaimed')
    return {'scope': 'exporter transport and storage tests only', 'checks': passed,
            'passed': len(passed), 'production_sampler_executed': False,
            'physical_flags': PHYSICAL_FLAGS}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--radial-order', type=int, default=192)
    p.add_argument('--time-order', type=int, default=4)
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True, indent=2))
    elif args.repository is None or args.output is None:
        p.error('--repository and --output are required unless --self-test is used')
    else:
        export(args.repository, args.output, args.radial_order, args.time_order)
