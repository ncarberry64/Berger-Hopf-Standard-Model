"""Evaluate full geometric Clifford contacts on saved coefficient germs.

This reads the preceding scalar application; it runs no background, mode,
history or radial integration and makes no native/physical carrier choice.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.muon_m8_geometric_kk_clifford import (
    JET_ORDER, m8_geometric_kk_clifford_jets,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def encode(a):
    a = np.asarray(a, complex)
    return dict(real=a.real.tolist(), imag=a.imag.tolist())


def decode(a):
    return np.asarray(a['real']) + 1j * np.asarray(a['imag'])


def evaluate(source, output):
    source, out = Path(source).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError('Preserve every independently executed application')
    data = json.loads(source.read_bytes())
    if data['full_physical_derivative_at_2e_minus10_passed'] or data['coupled_corrections']:
        raise ValueError('This coefficient application must not promote physical gates')
    g = full_d5_localized_lepton_trace()['gamma5D_particle'][[0, 4, 1, 2, 3]]
    records = []
    for sample in data['records']:
        c = {name: {k: decode(v[k]) for k in JET_ORDER}
             for name, v in sample['coefficient_jets'].items()}
        c['base_frame_order'] = ('0', 'chi', '1', '2', '3')
        result = m8_geometric_kk_clifford_jets(gamma5_base=g, geometric_coefficients=c)
        records.append(dict(
            stage=sample['stage'], sample_kind=sample['sample_kind'],
            original_radial_node_index=sample['original_radial_node_index'],
            original_material_rho=sample['original_material_rho'],
            KK_full16_jets={k: encode(result['KK'][k]) for k in JET_ORDER},
            component_norms={name: {k: float(np.linalg.norm(v[k])) for k in JET_ORDER}
                for name, v in result.items() if isinstance(v, dict)
                and set(v) == set(JET_ORDER) and all(isinstance(x, np.ndarray) for x in v.values())},
            clifford5_residual=result['clifford5_residual'],
            clifford8_residual=result['clifford8_residual'],
            full_vs_upper_ordered_KK_residual=result['full_vs_upper_ordered_KK_residual'],
            mean_spin_density_cancellation_max={k: float(np.max(abs(v)))
                for k, v in result['mean_spin_density_cancellation'].items()},
            vertical_and_temporal_shift_terms_preserved=True,
            adapted_frame_not_combined_with_untransported_original_u_v_frame=True,
        ))
    pins = {source.relative_to(ROOT).as_posix(): sha256(source.read_bytes()).hexdigest()}
    for rel in ('audits/bhsm_m8_kk_saved_geometry_application_20261016.py',
                'src/bhsm/interface/muon_m8_geometric_kk_clifford.py',
                'tests/test_muon_m8_geometric_kk_clifford.py'):
        pins[rel] = sha256((ROOT / rel).read_bytes()).hexdigest()
    for name, module in sorted(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(ROOT):
            pins[Path(path).relative_to(ROOT).as_posix()] = sha256(Path(path).read_bytes()).hexdigest()
    payload = dict(
        classification='FULL16_GEOMETRIC_KK_CONTACTS_ON_FROZEN_COMPLEX_SOURCE_GERMS',
        records=records, fixed_gamma5_base=encode(g),
        base_frame_order=['0', 'chi', '1', '2', '3'],
        source_axes='same saved coordinate-time / declared partial qb0 affine germ as scalar input',
        input_and_source_sha256=dict(sorted(pins.items())),
        full_ordered_curvature_sum=True, all_six_angular_one_normal_principals_retained=True,
        vertical_spin_and_DF_nonzero=True, temporal_and_shift_principals_retained=True,
        new_native_SM_or_statistics_carrier_selected=False,
        complete_associated_mode_connection_and_native_body_realized=False,
        M8_geometric_spin_block_is_a_new_muon_particle_carrier=False,
        D5_muon_outgoing_assembly_requires_new_M8_particle_carrier=False,
        full_physical_outgoing_derivative_at_2e_minus10_passed=False,
        physical_radial_or_angular_convergence_passed=False,
        new_history_profile_D5_or_radial_integrations=0,
        coupled_corrections=0, normalized_physical_spins=None, physical_muon_magnetic_moment=None,
    )
    for rel, expected in pins.items():
        if sha256((ROOT / rel).read_bytes()).hexdigest() != expected:
            raise ValueError('Input changed during coefficient application: ' + rel)
    out.mkdir(parents=True)
    path = out / 'result.json'
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + '\n',
                    encoding='utf8', newline='\n')
    print(json.dumps(dict(samples=len(records), sha256=sha256(path.read_bytes()).hexdigest(),
        max_Clifford_residual=max(r['clifford8_residual'] for r in records),
        max_KK_ordering_residual=max(v for r in records for v in r['full_vs_upper_ordered_KK_residual'].values()),
        coupled_corrections=0, physical_derivative_pass=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    evaluate(args.source, args.output)
