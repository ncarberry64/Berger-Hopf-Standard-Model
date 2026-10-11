"""Materialize and consume the actual normal-frame external-test maps."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from bhsm.interface.muon_normal_current_contraction_maps import normal_current_contraction_maps
from bhsm.interface.muon_normal_current_compressed_maps import compress_normal_current_maps
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_lepton_sample
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_wall_reference
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out = Path(output)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        raise FileExistsError('preserve earlier external-test applications')
    arrays, records, refs = {}, {}, {}
    inputs_path = 'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    inputs = json.loads((ROOT / inputs_path).read_bytes())
    refs[inputs_path] = sha256((ROOT / inputs_path).read_bytes()).hexdigest()
    charge = float(np.sqrt(4 * np.pi * inputs['alpha_consumer']['value']))
    source_receipt = 'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/result.json'
    source = json.loads((ROOT / source_receipt).read_bytes())
    if source['electric_charge'] != charge:
        raise ValueError('the same independently matched source charge is required')
    refs[source_receipt] = sha256((ROOT / source_receipt).read_bytes()).hexdigest()

    def pack(value, key):
        if isinstance(value, np.ndarray):
            arrays[key] = value
            return dict(array_key=key, shape=list(value.shape))
        if isinstance(value, dict):
            return {k: pack(v, key + '_' + k) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [pack(v, key + '_' + str(i)) for i, v in enumerate(value)]
        if isinstance(value, np.generic):
            return pack(value.item(), key)
        if isinstance(value, complex):
            return dict(real=value.real, imag=value.imag)
        return value

    names = ('right_mass_C', 'right_FW_C', 'Weyl_mass_C',
        'Weyl_mass_T', 'Weyl_FW_C', 'Weyl_FW_T')
    for side, folder in (
            ('incoming', 'artifacts/muon_finite_normal_phase_20261011/incoming_run_1'),
            ('outgoing', 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')):
        phase = load_profile_preserving_phase(folder)
        refs.update(phase['input_hashes'])
        sample = profile_preserving_lepton_sample(phase, 0.)
        raw, operator = sample['sample']['raw_fields'], sample['operator']
        wall = corrected_wall_reference(raw, phase['representation'], coordinate_time=0.)['background_values'][0]
        for family in (1, 2):
            ids = np.array([2*family, 2*family+1, 6+2*family,
                7+2*family, 12+2*family, 13+2*family])
            arguments = dict(family_indices=ids, family=family,
                radius=operator['R4'], wall_connection=wall, H=operator['H'], electric_charge=charge)
            maps = normal_current_contraction_maps(**arguments)
            compact = compress_normal_current_maps(maps, radius=operator['R4'])
            key = side + '_family_' + str(family)
            records[key] = pack(dict(arguments=arguments, maps=compact,
                energy_residue_weight=maps['kinetic_residue_energy_weight']), key)
            print(json.dumps(dict(stage='actual_normal_maps', side=side, family=family,
                maximum_reconstruction_residual=max(row['reconstruction_residual_norm']
                    for name in names for row in compact[name]),
                FW_charged_only_relative_residual=compact['right_FW_C'][0]['charged_only_projection_relative_residual']),
                sort_keys=True), flush=True)
            if side == 'incoming' and family == 1:
                path = 'artifacts/muon_paired_changing_magnetic_columns_20261011/constant_run_1/incoming_family_1_forward.npz'
                reverse_path = path.replace('_forward', '_reverse')
                refs[path] = sha256((ROOT / path).read_bytes()).hexdigest()
                refs[reverse_path] = sha256((ROOT / reverse_path).read_bytes()).hexdigest()
                with np.load(ROOT / path, allow_pickle=False) as a:
                    values = {k: a[k].copy() for k in a.files}
                with np.load(ROOT / reverse_path, allow_pickle=False) as a:
                    for k in a.files:
                        arrays['incoming_family_1_literal_reverse_' + k] = a[k]
                contributions = {}
                for term, C in values.items():
                    if C.shape != (3, 24, 6):
                        raise ValueError('the completed actual constant placement requires all C6 entries')
                    rows = {name: np.array([np.einsum('oi,Aoi->A', row['tensor_weight'], C)
                        for row in compact[name]]).T for name in names if name.endswith('_C')}
                    contributions[term] = rows
                for name in names:
                    if not name.endswith('_C'):
                        continue
                    total = contributions['total'][name]
                    total -= sum(row[name] for term, row in contributions.items() if term != 'total')
                    arrays['incoming_family_1_' + name + '_placement_sum_difference'] = total
                    # Recompute the total rather than modifying the consumed center.
                    contributions['total'][name] = np.array([np.einsum('oi,Aoi->A', row['tensor_weight'], values['total'])
                        for row in compact[name]]).T
                records['completed_constant_application'] = pack(contributions, 'incoming_family_1_constant')
    modules = ('muon_normal_current_contraction_maps', 'muon_normal_current_compressed_maps',
        'muon_changing_normal_current_readout', 'muon_intrinsic_normal_coordinate_readout',
        'muon_intrinsic_covariant_open_current_jet', 'muon_profile_preserving_phase_sample',
        'muon_corrected_profile_magnetic_response', 'muon_magnetic_open_lepton_vertex',
        'muon_native_product_factor_graph', 'muon_native_dirac_hamiltonian')
    for module in modules:
        path = 'src/bhsm/interface/' + module + '.py'
        refs[path] = sha256((ROOT / path).read_bytes()).hexdigest()
    for path in ('tests/test_muon_normal_current_contraction_maps.py',
            'tests/test_muon_normal_current_compressed_maps.py',
            Path(__file__).relative_to(ROOT).as_posix()):
        refs[path] = sha256((ROOT / path).read_bytes()).hexdigest()
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise RuntimeError('a consumed completed source or frame changed')
    out.mkdir(parents=True)
    deterministic_archive(out / 'application.npz', arrays)
    archive = out / 'application.npz'
    result = dict(classification='EVALUATED_STRUCTURAL_NORMAL_TEST_REDUCTION_WITH_COMPLETE_CONSTANT_FAMILY_APPLICATION',
        input_hashes=refs, records=records,
        archive=dict(path='application.npz', bytes=archive.stat().st_size,
            sha256=sha256(archive.read_bytes()).hexdigest()),
        completed_loop_scope='all seven placements and nine field blocks of incoming middle constant family; remaining families/arms/momentum are not filled zero',
        normal_reference='same actual common birth for each arm; computational normal test with its actual complete C6 spin/gauge connection',
        full_first_Weyl_symbol_evaluated=False,
        source_charge_reinserted=False, neutral_complement_removed=False,
        physical_pole_mass_or_unit_selected=False,
        overlap_subtraction_or_sectorial_Lorentz_identification_performed=False,
        physical_F2=None, physical_a_mu=None, physical_g_mu=None,
        error_scope='Binary64 exact structural-map and actual constant-placement applications; reconstruction and placement-sum residuals reported, not outward enclosures. Missing tangent, relative domain and on-shell loop identification remain explicit.')
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2,
        allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return dict(classification=result['classification'], archive_sha256=result['archive']['sha256'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize(args.output), sort_keys=True))
