"""Execute only the exact middle/light external family restrictions."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from bhsm.interface.muon_changing_magnetic_open_exchange import changing_magnetic_constant_columns
from bhsm.interface.muon_changing_magnetic_momentum_columns import changing_magnetic_momentum_columns
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from evaluate_muon_changing_magnetic_momentum_columns import retained_momentum_inputs
from evaluate_muon_reached_trace_action import deterministic_archive


def family_restriction(fermions, sample):
    """Verify literal family invariance, preserving each neutral/charged fiber."""
    families = {family: next(f['family_indices'] for f in fermions if f['family'] == family)
        for family in range(3)}
    keep = np.zeros((18, 18), bool)
    for indices in families.values():
        keep[np.ix_(indices, indices)] = True
    alpha = lepton_current_hilbert_representation()['alpha']
    if (np.any(sample['coefficient_W'][:, ~keep])
            or np.any(sample['coefficient_Omega'][:, ~keep]) or np.any(alpha[:, ~keep])):
        raise ValueError('actual operator does not preserve the fixed-Y family restrictions')
    return families


def materialize(output, *, kind, cutoff=1e-11):
    if kind not in ('constant', 'momentum'):
        raise ValueError('a concrete constant or input-momentum application is required')
    out = Path(output)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        raise FileExistsError('preserve earlier paired family applications')
    out.mkdir(parents=True)
    own_paths = (
        'src/bhsm/interface/muon_changing_magnetic_open_exchange.py',
        'src/bhsm/interface/muon_changing_magnetic_current_jets.py',
        'src/bhsm/interface/muon_changing_magnetic_momentum_columns.py',
        'scripts/evaluate_muon_changing_magnetic_open_exchange.py',
        'scripts/evaluate_muon_changing_magnetic_momentum_columns.py',
        Path(__file__).relative_to(ROOT).as_posix())
    refs = {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in own_paths}
    files, records = {}, []
    for side in ('incoming', 'outgoing'):
        phase, sampler, all_fermions, fields, direction, sample = retained_momentum_inputs(side, refs)
        family_indices = family_restriction(all_fermions, sample)
        for family in (1, 2):
            selected = [dict(f) for f in all_fermions if f['family'] == family]
            if kind == 'constant':
                selected = [f for f in selected if f['level'] != 6]
                for fermion in selected:
                    if fermion['parity'] == 'even':
                        fermion['real_to_complex'] = fermion['real_to_complex'][:, :35]
                consume = changing_magnetic_constant_columns
            else:
                consume = changing_magnetic_momentum_columns
            app = consume(phase, sampler, selected, fields, direction,
                times=sample['chronological_quadrature_times'], weights=sample['chronological_quadrature_weights'],
                temporal_values=sample['temporal_basis_values'], temporal_rates=sample['temporal_basis_coordinate_rates'],
                cutoff=cutoff, progress=lambda row: print(json.dumps(dict(
                    stage='actual_paired_changing_magnetic_' + kind, side=side, **row), sort_keys=True), flush=True))
            indices = family_indices[family]
            output_indices = (indices[:, None] * (4 if kind == 'constant' else 10)
                + np.arange(4 if kind == 'constant' else 10)).ravel()
            input_indices = indices if kind == 'constant' else (indices[:, None] * 4 + np.arange(4)).ravel()
            norms = {}
            for placement in ('forward', 'reverse'):
                rows, columns = (output_indices, input_indices) if placement == 'forward' else (input_indices, output_indices)
                arrays = {key: value[:, rows][:, :, columns].copy() for key, value in app[placement].items()}
                path = out / (side + '_family_' + str(family) + '_' + placement + '.npz')
                deterministic_archive(path, arrays)
                files[path.name] = dict(bytes=path.stat().st_size, sha256=sha256(path.read_bytes()).hexdigest())
                norms[placement] = {key: float(np.linalg.norm(value)) for key, value in arrays.items()}
            records.append(dict(side=side, family=family, family_indices=indices.tolist(),
                block_records=app['block_records'], external_tent_Gram=app['external_tent_Gram'],
                norms=norms, maximum_scalar_kernel_approximation_upper=app['maximum_scalar_kernel_approximation_upper']))
            del app, selected
        del all_fermions, fields
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise RuntimeError('same source/phase changed during paired family application')
    result = dict(classification='EVALUATED_EXACT_MIDDLE_LIGHT_CHANGING_MAGNETIC_' + kind.upper() + '_COLUMNS',
        input_hashes=refs, numerical_files=files, records=records,
        action_parameters=phase['receipt']['action_parameters'], common_probe_cutoff=float(cutoff),
        evaluated_external_families=[1, 2], unevaluated_external_family=0,
        family_reduction='literal fixed diagonal Y, W, Omega, alpha and source/current generators preserve all three family subspaces; each retained C6 includes both neutral and charged fibers',
        omitted_family_output_filled_zero=False, closed_tau_photon_terms_unchanged=True,
        placement_shapes=([3, 24, 6] if kind == 'constant' else [3, 60, 24]),
        ordering='family spin-major angular; family_indices explicitly embed the six fibers in the full18 current Hilbert space',
        all_starting_field_coordinates_retained=[1200, 2100], starting_field_loop_domain_enlarged=False,
        both_fermion_square_placements=True, acted_trial_numerator_contact=True,
        field_operator_and_Gram_and_both_current_contacts=True, Gaussian_statistics_sign=-1,
        independent_sector_inverses=False, input_momentum_columns_evaluated=(kind == 'momentum'),
        angular_starting_loop_complement_bound=False, variable_coefficient_differential_closure_claimed=False,
        physical_P_strat_Wick_LSZ_Pauli_completed=False, physical_a_mu=None, physical_g_mu=None,
        error_scope='binary64 same-phase Gaussian component; scalar kernel approximation allowance alone is not a contraction/eigen/continuum or physical matching bound.')
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n',
        encoding='utf8', newline='\n')
    return dict(classification=result['classification'], records=records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=('constant', 'momentum'), required=True)
    parser.add_argument('--cutoff', type=float, default=1e-11)
    args = parser.parse_args()
    print(json.dumps(materialize(args.output, kind=args.kind, cutoff=args.cutoff), sort_keys=True))
