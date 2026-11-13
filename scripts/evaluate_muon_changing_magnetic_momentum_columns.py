"""Apply the changing magnetic graph to its complete input-momentum image."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from bhsm.interface.muon_changing_magnetic_momentum_columns import changing_magnetic_momentum_columns
from bhsm.interface.muon_magnetic_n6_return_fermion import n6_return_angular_blocks
from evaluate_muon_changing_magnetic_open_exchange import retained_inputs
from evaluate_muon_reached_trace_action import deterministic_archive


def retained_momentum_inputs(side, refs, *, repository=ROOT):
    """Bind every return block to the unchanged source/field quadrature."""
    phase, sampler, fermions, fields, direction, sample = retained_inputs(side, refs, repository=repository)
    folder = repository / 'artifacts/muon_magnetic_n6_return_fermion_20261011/run_1'
    receipt_path = folder / 'result.json'
    raw = receipt_path.read_bytes()
    receipt = json.loads(raw)
    if receipt['classification'] != 'EVALUATED_SAME_PHASE_MAGNETIC_N6_FERMION_RETURN_FORM':
        raise ValueError('same complete n6 return application required')
    refs[receipt_path.relative_to(repository).as_posix()] = sha256(raw).hexdigest()
    for path, digest in receipt['input_hashes'].items():
        if path in refs and refs[path] != digest:
            raise ValueError('n6 return binds a different source or action')
        refs[path] = digest

    def load(name):
        path = folder / name
        data = path.read_bytes()
        record = receipt['numerical_files'][name]
        if sha256(data).hexdigest() != record['sha256'] or len(data) != record['bytes']:
            raise ValueError('retained n6 return array changed: ' + str(path))
        refs[path.relative_to(repository).as_posix()] = record['sha256']
        with np.load(path, allow_pickle=False) as archive:
            return {key: archive[key].copy() for key in archive.files}

    n6_sample = load(side + '_samples.npz')
    for key in ('source_temporal_congruence', 'temporal_basis_values', 'temporal_basis_coordinate_rates',
                'chronological_quadrature_times', 'chronological_quadrature_weights',
                'coefficient_N_R', 'coefficient_W', 'coefficient_Omega'):
        if not np.array_equal(n6_sample[key], sample[key]):
            raise ValueError('n6 return must use the same chronological coefficient and temporal family: ' + key)
    # This is the literal direct sum of complete even shells, not a new
    # field loop or an insertion of padded zero operator modes.
    for fermion in fermions:
        if fermion['parity'] == 'even':
            transform = np.zeros((len(fermion['harmonic_indices']), 84), complex)
            transform[:, :35] = fermion['real_to_complex']
            fermion['real_to_complex'] = transform
    angular = n6_return_angular_blocks()
    for family, family_indices in enumerate(angular['family_indices']):
        for index, block in enumerate(angular['angular_blocks']):
            data = load(side + '_block_' + str(7 * family + index) + '.npz')
            harmonic_indices = block['harmonic_indices']
            if (not np.array_equal(data['harmonic_indices'], harmonic_indices)
                    or not np.array_equal(data['family_indices'], family_indices)):
                raise ValueError('n6 family or orbital coefficient ordering changed')
            transform = np.zeros((len(harmonic_indices), 84), complex)
            transform[:, 35:] = angular['real_to_complex'][harmonic_indices]
            fermions.append(dict(name='n6_' + str(7 * family + index), family=family,
                family_indices=family_indices, parity='even', level=6,
                spectator=block['spectator'], harmonic_indices=35 + harmonic_indices,
                derivatives=angular['complex_derivatives'][:, harmonic_indices][:, :, harmonic_indices],
                real_to_complex=transform, eigenvalues=data['generalized_eigenvalues'],
                eigenvectors=data['eigenvectors']))
    if any(sha256((repository / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise ValueError('same coefficient/source dependency changed before momentum application')
    return phase, sampler, fermions, fields, direction, sample


def materialize(output, *, cutoff=1e-11):
    out = Path(output)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        raise FileExistsError('preserve previous momentum applications')
    out.mkdir(parents=True)
    own_paths = (
        'src/bhsm/interface/muon_changing_magnetic_momentum_columns.py',
        'tests/test_muon_changing_magnetic_momentum_columns.py',
        Path(__file__).relative_to(ROOT).as_posix(),
        'scripts/evaluate_muon_changing_magnetic_open_exchange.py',
        'src/bhsm/interface/muon_changing_magnetic_open_exchange.py',
        'src/bhsm/interface/muon_changing_magnetic_current_jets.py')
    refs = {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in own_paths}
    files, records = {}, []
    for side in ('incoming', 'outgoing'):
        phase, sampler, fermions, fields, direction, sample = retained_momentum_inputs(side, refs)
        app = changing_magnetic_momentum_columns(phase, sampler, fermions, fields, direction,
            times=sample['chronological_quadrature_times'], weights=sample['chronological_quadrature_weights'],
            temporal_values=sample['temporal_basis_values'], temporal_rates=sample['temporal_basis_coordinate_rates'],
            cutoff=cutoff, progress=lambda row: print(json.dumps(dict(
                stage='actual_changing_magnetic_momentum_graph', side=side, **row), sort_keys=True), flush=True))
        for placement in ('forward', 'reverse'):
            path = out / (side + '_' + placement + '.npz')
            deterministic_archive(path, app[placement])
            if path.stat().st_size > 10 * 1024**2:
                raise ValueError('complete momentum columns exceed artifact publication size')
            files[path.name] = dict(bytes=path.stat().st_size, sha256=sha256(path.read_bytes()).hexdigest())
        records.append(dict(side=side, block_records=app['block_records'],
            external_tent_Gram=app['external_tent_Gram'], ordering=app['ordering'],
            forward_norm=float(np.linalg.norm(app['forward']['total'])),
            reverse_norm=float(np.linalg.norm(app['reverse']['total'])),
            parts_forward={key: float(np.linalg.norm(value)) for key, value in app['forward'].items()},
            parts_reverse={key: float(np.linalg.norm(value)) for key, value in app['reverse'].items()},
            maximum_scalar_kernel_approximation_upper=app['maximum_scalar_kernel_approximation_upper']))
        del app, fermions, fields
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise RuntimeError('same source/phase changed during momentum application')
    result = dict(classification='EVALUATED_CHANGING_COMPLETE_FIELD_LOOP_MAGNETIC_INPUT_MOMENTUM_COLUMNS',
        input_hashes=refs, numerical_files=files, records=records, action_parameters=phase['receipt']['action_parameters'],
        common_probe_cutoff=float(cutoff), Gaussian_statistics_sign=-1,
        external_columns='forward outputspin18*10+realharmonic(n0/n2), inputspin18*4+realharmonic(n1); literal reverse',
        all_starting_field_coordinates_retained=[1200, 2100],
        source_directed_fermion_return_harmonics='complete n0/n2/n4/n6 and n1/n3/n5; all8 same independent temporal functions',
        input_momentum_columns_evaluated=True, starting_field_loop_domain_enlarged=False,
        both_fermion_square_placements=True, acted_trial_numerator_contact=True,
        field_Gram_and_both_current_normalization_contacts=True, actual_field_current_chart_motion=True,
        independent_sector_inverses=False, angular_starting_loop_complement_bound=False,
        variable_coefficient_differential_closure_claimed=False,
        physical_P_strat_Wick_LSZ_Pauli_completed=False, physical_a_mu=None, physical_g_mu=None,
        error_scope='binary64 same-phase source/coefficient Gaussian graph application. Scalar kernel series/Hermite allowance is separate; no total contraction/eigen/continuum or physical soft-matching enclosure.')
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n',
        encoding='utf8', newline='\n')
    return dict(classification=result['classification'], records=records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cutoff', type=float, default=1e-11)
    args = parser.parse_args()
    print(json.dumps(materialize(args.output, cutoff=args.cutoff), sort_keys=True))
