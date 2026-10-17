"""Apply the normal covector to the actual joined canonical current jets.

This consumes the full common-Y coefficients and both angular directions.
It does not replace a Gaussian loop with a current inverse or invent a
nonmagnetic self-energy residue for that current component.
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
from bhsm.interface.muon_changing_normal_current_readout import changing_family_current_inverse_covectors
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_lepton_sample
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_wall_reference
from bhsm.interface.muon_common_y_current_response import paired_fixed_y_polynomial
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output, *, input_folder=Path('artifacts/muon_joined_common_y_current_20261011/run_1')):
    out, folder = Path(output), Path(input_folder)
    out = out if out.is_absolute() else ROOT / out
    folder = folder if folder.is_absolute() else ROOT / folder
    if out.exists():
        raise FileExistsError('preserve earlier joined normal applications')
    receipt_bytes = (folder / 'result.json').read_bytes()
    packet = json.loads(receipt_bytes)
    if packet['classification'] != 'EVALUATED_JOINED_CANONICAL_COMMON_Y_CURRENT_WITH_BOTH_ANGULAR_SOURCE_DIRECTIONS':
        raise ValueError('the actual joined current and both angular source directions are required')
    refs = dict(packet['input_hashes'])
    refs[(folder / 'result.json').relative_to(ROOT).as_posix()] = sha256(receipt_bytes).hexdigest()
    for path, digest in refs.items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError('consumed joined current owner changed: ' + path)
    phase = load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    for path, digest in phase['input_hashes'].items():
        if path in refs and refs[path] != digest:
            raise ValueError('normal reference and current use different primal fields')
        refs[path] = digest
    reference = profile_preserving_lepton_sample(phase, 0.)
    raw, operator = reference['sample']['raw_fields'], reference['operator']
    wall = corrected_wall_reference(raw, phase['representation'], coordinate_time=0.)['background_values'][0]
    input_path = ROOT / 'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    inputs = json.loads(input_path.read_bytes())
    refs[input_path.relative_to(ROOT).as_posix()] = sha256(input_path.read_bytes()).hexdigest()
    charge = float(np.sqrt(4 * np.pi * inputs['alpha_consumer']['value']))
    source_path = 'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/result.json'
    if source_path not in refs or json.loads((ROOT / source_path).read_bytes())['electric_charge'] != charge:
        raise ValueError('the current and normal covector must use the same actual source charge')
    arguments = dict(family_indices=np.array([2, 3, 8, 9, 14, 15]), family=1,
        radius=operator['R4'], wall_connection=wall, H=operator['H'], electric_charge=charge)
    arrays, records, previous = {}, [], {}

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

    for steps in (16, 32, 64):
        name = 'joined_' + str(steps) + '.npz'
        path = folder / name
        raw_archive = path.read_bytes()
        digest = sha256(raw_archive).hexdigest()
        if digest != packet['array_archives'][name]['sha256']:
            raise ValueError('actual joined common-Y arrays changed')
        refs[path.relative_to(ROOT).as_posix()] = digest
        with np.load(path, allow_pickle=False) as archive:
            a = {key: archive[key].copy() for key in archive.files}
        paired = changing_family_current_inverse_covectors(a['paired_constant_forward'],
            a['paired_momentum_forward'], a['paired_constant_reverse'],
            a['paired_momentum_reverse'], **arguments)
        order = a['constant_forward_coefficients'].shape[1]
        coefficients = [changing_family_current_inverse_covectors(
            a['constant_forward_coefficients'][:, k], a['momentum_forward_coefficients'][:, k],
            a['constant_reverse_coefficients'][:, k], a['momentum_reverse_coefficients'][:, k],
            **arguments)['mass_affine_signed_soft_covectors'] for k in range(order)]
        Y = a['fixed_middle_light_Y']
        comparisons = {}
        for symbol, row in paired['mass_affine_signed_soft_covectors'].items():
            for key in ('mass_coefficient', 'FW_constant_coefficient'):
                values = np.array([coefficient[symbol][key] for coefficient in coefficients])
                projected_pair = paired_fixed_y_polynomial(values, *Y)
                row[key + '_common_Y_coefficients'] = values
                row[key + '_linearity_difference'] = row[key] - projected_pair
                comparisons[symbol + '_' + key + '_norm'] = float(np.linalg.norm(row[key]))
                comparisons[symbol + '_' + key + '_refinement_difference'] = (
                    None if (symbol, key) not in previous else
                    float(np.linalg.norm(row[key] - previous[symbol, key])))
                previous[symbol, key] = row[key]
                isotropic = np.trace(row[key]) / 3
                row[key + '_isotropic'] = isotropic
                row[key + '_nonisotropic'] = row[key] - isotropic * np.eye(3)
        records.append(pack(dict(steps_per_arm=steps, paired_application=paired,
            comparisons=comparisons, fixed_middle_light_Y=Y), 'steps_' + str(steps)))
        print(json.dumps(dict(stage='joined_canonical_normal_covector', steps_per_arm=steps,
            **comparisons), sort_keys=True), flush=True)
    for module in ('muon_changing_normal_current_readout', 'muon_intrinsic_normal_coordinate_readout',
        'muon_intrinsic_covariant_open_current_jet', 'muon_magnetic_open_lepton_vertex',
        'muon_profile_preserving_phase_sample', 'muon_corrected_profile_magnetic_response',
        'muon_common_y_current_response'):
        path = 'src/bhsm/interface/' + module + '.py'
        refs[path] = sha256((ROOT / path).read_bytes()).hexdigest()
    for path in ('tests/test_muon_changing_normal_current_readout.py',
            Path(__file__).relative_to(ROOT).as_posix()):
        refs[path] = sha256((ROOT / path).read_bytes()).hexdigest()
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise RuntimeError('same joined source/frame changed during the normal readout')
    out.mkdir(parents=True)
    deterministic_archive(out / 'application.npz', arrays)
    result = dict(classification='EVALUATED_JOINED_CANONICAL_CURRENT_MASS_AFFINE_NORMAL_COVECTORS',
        input_hashes=refs, records=records, actual_normal_reference_time=0.,
        normal_reference='incoming common-birth normal point and actual full mechanical/gauge connection; fixed temporal extension of these computational normal inputs',
        archive=dict(path='application.npz', bytes=(out / 'application.npz').stat().st_size,
            sha256=sha256((out / 'application.npz').read_bytes()).hexdigest()),
        external_pole_mass_or_action_unit_selected=False,
        nonmagnetic_self_energy_residue_filled_zero=False,
        self_energy_or_Gaussian_loop_identification=False,
        positive_factor_current_substituted=False,
        local_overlap_or_finite_c_native_completion_performed=False,
        physical_F2=None, physical_a_mu=None, physical_g_mu=None,
        error_scope='Binary64 actual joined canonical coefficients, first normal Weyl/FW application, literal reverse and common-Y linearity. Temporal refinement is diagnostic; full bilocal symbol, quantum loop/domain, finite-c and physical Pauli error are not enclosed.')
    (out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2,
        allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return dict(classification=result['classification'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--input-folder', type=Path,
        default=Path('artifacts/muon_joined_common_y_current_20261011/run_1'))
    args = parser.parse_args()
    print(json.dumps(materialize(args.output, input_folder=args.input_folder), sort_keys=True))
