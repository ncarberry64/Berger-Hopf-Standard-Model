"""Replay the corrected action charged-current contraction and scale row."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_corrected_charged_current_cell import corrected_charged_current_cell
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out = Path(output)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        raise FileExistsError('preserve earlier corrected current applications')
    refs, arrays, rows = {}, {}, []
    def pack(value, key):
        if isinstance(value, np.ndarray):
            arrays[key] = value
            return dict(array_key=key, shape=list(value.shape))
        if isinstance(value, dict):
            return {k: pack(v, key + '_' + k) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [pack(v, key + '_' + str(j)) for j, v in enumerate(value)]
        if isinstance(value, np.generic):
            return pack(value.item(), key)
        if isinstance(value, complex):
            return dict(real=value.real, imag=value.imag)
        return value
    folders = dict(incoming='artifacts/muon_finite_normal_phase_20261011/incoming_run_1',
        outgoing='artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    for side, folder in folders.items():
        phase = load_profile_preserving_phase(folder)
        refs.update(phase['input_hashes'])
        if phase['receipt']['steps'] != 1:
            raise ValueError('this materializer binds the actual same one-cell current')
        app = corrected_charged_current_cell(phase)
        rows.append(pack(app, side))
        print(json.dumps(dict(stage='corrected_same_action_charged_current', side=side,
            frame_difference=app['named_frame_electron_muon_difference'],
            fits=[row['local_Fermi_template_fit'] for row in app['applications']]), sort_keys=True), flush=True)
    for name in ('muon_corrected_charged_current_cell', 'muon_profile_preserving_phase_sample',
        'muon_charged_current_cell_amputation', 'muon_charged_current_fermi_reduction',
        'muon_primal_native_phase_adjoint', 'muon_trace_enriched_charged_current_response',
        'muon_primal_charged_current_response', 'muon_inherited_intrinsic_lepton_operator',
        'muon_primal_trace_enriched_lepton_operator', 'muon_inherited_wall_lepton_application',
        'muon_primal_intrinsic_lepton_operator'):
        path = 'src/bhsm/interface/' + name + '.py'
        refs[path] = sha256((ROOT / path).read_bytes()).hexdigest()
    own = Path(__file__).relative_to(ROOT).as_posix()
    refs[own] = sha256((ROOT / own).read_bytes()).hexdigest()
    if any(sha256((ROOT / path).read_bytes()).hexdigest() != digest for path, digest in refs.items()):
        raise RuntimeError('same corrected action owner changed during current contraction')
    out.mkdir(parents=True)
    deterministic_archive(out / 'application.npz', arrays)
    packet = dict(classification='EVALUATED_CORRECTED_INHERITED_CHRONOLOGICAL_CURRENT_AND_FERMI_TEMPLATE',
        input_hashes=refs, arms=rows,
        archive=dict(path='application.npz', bytes=(out / 'application.npz').stat().st_size,
            sha256=sha256((out / 'application.npz').read_bytes()).hexdigest()),
        scale_owner='universal_gf_scale.UniversalGFScaleMap',
        scale_equation='G_F_measured=c_F[matched corrected common-action charged-current contraction]/E_kappa^2',
        measured_mass_or_anomaly_used_in_action=False,
        physical_low_energy_Fermi_coefficient=None, physical_E_kappa=None,
        tree_Y_H_mass_assigned_interacting_pole=False, physical_Pauli_or_anomaly_completed=False)
    (out / 'result.json').write_text(json.dumps(packet, sort_keys=True, indent=2,
        allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return dict(classification=packet['classification'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize(args.output), sort_keys=True))
