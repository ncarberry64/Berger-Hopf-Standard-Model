"""Bind the exact middle/light current graph at zero external frequency.

These moments share the external frequency of the frozen magnetic
constant/tangent producer.  They do not identify the positive reference
with the Lorentz contour or select a physical interacting pole.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from evaluate_muon_changing_magnetic_open_exchange import retained_inputs
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_changing_current_energy_moments import (
    changing_constant_energy_application, proper_clock_at_nodes,
)
from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_open_current_point
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet


def materialize(output, *, cutoff=1e-11):
    out = Path(output)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        raise FileExistsError('preserve earlier same-frequency applications')
    own = (
        'src/bhsm/interface/muon_changing_current_energy_moments.py',
        'tests/test_muon_changing_current_energy_moments.py',
        'src/bhsm/interface/muon_changing_magnetic_open_exchange.py',
        'src/bhsm/interface/muon_changing_magnetic_current_jets.py',
        'scripts/evaluate_muon_changing_magnetic_open_exchange.py',
        Path(__file__).relative_to(ROOT).as_posix(),
    )
    refs = {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in own}
    arrays, records = {}, []
    for side in ('incoming', 'outgoing'):
        phase, sampler, F, B, _, sample = retained_inputs(side, refs)
        F = [f for f in F if f['family'] in (1, 2)]
        length = abs(phase['receipt']['span'])
        times = sample['chronological_quadrature_times']
        weights = sample['chronological_quadrature_weights']

        def lapse(u):
            time = float(u - length if side == 'incoming' else u)
            raw = profile_preserving_raw_sample(phase, time)['raw_fields']
            return intrinsic_m4_weight_jet(12, raw[:37], raw[37:74], raw[74:98],
                source_value=raw[98], source_rate=raw[99])['induced_lapse'].value

        clock = proper_clock_at_nodes(times, lapse, order=16)
        points = [magnetic_open_current_point(phase, float(u), length=length,
            first_field_sampler=sampler, include_maps=False) for u in times]
        for point in points:
            point['length'] = length
        measure = weights * np.array([point['N'] for point in points])
        app = changing_constant_energy_application(F, B, points,
            sample['temporal_basis_values'], sample['temporal_basis_coordinate_rates'],
            measure, clock['proper_times'], energy=0., variable='proper_clock_frequency',
            cutoff=cutoff, progress=lambda row: print(json.dumps(dict(
                stage='actual_zero_frequency_energy_contacts', side=side, **row),
                sort_keys=True), flush=True))
        # The temporary full representation is never emitted as an
        # assertion that an unevaluated tau-family return vanishes.
        family_records = []
        for family in (1, 2):
            indices = next(f['family_indices'] for f in F if f['family'] == family)
            prefix = side + '_family_' + str(family) + '_'
            arrays[prefix + 'family_indices'] = indices.copy()
            for key in ('value', 'left_energy_contact', 'right_energy_contact', 'energy_first'):
                arrays[prefix + key] = app[key][np.ix_(indices, indices)].copy()
            family_records.append(dict(family=family, family_indices=indices.tolist(),
                value_norm=float(np.linalg.norm(arrays[prefix + 'value'])),
                energy_first_norm=float(np.linalg.norm(arrays[prefix + 'energy_first'])),
                left_contact_norm=float(np.linalg.norm(arrays[prefix + 'left_energy_contact'])),
                right_contact_norm=float(np.linalg.norm(arrays[prefix + 'right_energy_contact']))))
        for key, value in clock.items():
            if isinstance(value, np.ndarray):
                arrays[side + '_' + key] = value
        records.append(dict(side=side, families=family_records,
            block_records=app['block_records'], external_tent_Gram=app['external_tent_Gram'],
            proper_clock_refinement_max=float(np.max(abs(clock['quadrature_refinement_difference'])))))
        del F, B, points, app
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise RuntimeError('same current source or domain changed during zero-frequency application')
    out.mkdir(parents=True)
    deterministic_archive(out / 'application.npz', arrays)
    packet = dict(classification='EVALUATED_EXACT_MIDDLE_LIGHT_ZERO_FREQUENCY_CURRENT_ENERGY_JET',
        input_hashes=refs, records=records, energy_variable='proper_clock_frequency',
        external_energy_action=0., common_probe_cutoff=float(cutoff),
        array_archive=dict(path='application.npz', bytes=(out / 'application.npz').stat().st_size,
            sha256=sha256((out / 'application.npz').read_bytes()).hexdigest()),
        evaluated_external_families=[1, 2], unevaluated_external_family=0,
        unevaluated_family_outputs_assigned_zero=False,
        both_external_energy_contacts=True, Gaussian_sign=-1,
        complete_starting_field_coordinates=[1200, 2100],
        external_frequency_matches_magnetic_columns=True,
        energy_matching_scope='same zero-frequency tent/current application; not an on-shell energy identification',
        internal_operator_or_domain_continued=False,
        physical_pole_LSZ_Pauli_completed=False, physical_a_mu=None, physical_g_mu=None,
        error_scope='Binary64 actual current/eigen/quadrature application. Clock refinement is diagnostic; spectral/continuum, source-complement and Lorentz/native-domain errors are not enclosed.')
    (out / 'result.json').write_text(json.dumps(packet, sort_keys=True, indent=2,
        allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return dict(classification=packet['classification'], records=records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cutoff', type=float, default=1e-11)
    args = parser.parse_args()
    print(json.dumps(materialize(args.output, cutoff=args.cutoff), sort_keys=True))
