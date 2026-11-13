"""Apply the canonical conormal graph to frozen reflected-native operands.

No field history, source, inverse, spectral selection or terminal load is
recomputed. The spectral jet holds the represented coefficients fixed; it
is not the physical outgoing unsquared-energy or magnetic derivative.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_reflected_native_conormal_graph import (
    reflected_native_conormal_graph_jets,
)


def _relative(actual, expected):
    return float(np.max(abs(actual-expected)))/max(
        float(np.max(abs(actual))), float(np.max(abs(expected))), 1e-300)


def materialize(output):
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = ROOT/'artifacts/muon_transported_native_pairing_20261011/run_1'
    pins = {}

    def pin(path, expected=None):
        digest = sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError(f'Frozen operand changed: {path.name}')
        pins[path.relative_to(ROOT).as_posix()] = digest
        return digest

    pin(base/'result.json')
    original = json.loads((base/'result.json').read_bytes())
    if original['complete_physical_OS_contour_reset_exterior_or_relative_domain_proved']:
        raise ValueError('This application is scoped to the retained finite core')
    names = sorted((name for name in original['archives']
                    if name.startswith('native_coframe_nodes_')),
                   key=lambda name: int(Path(name).stem.rsplit('_', 1)[1]))
    n, count = 18, 0
    identity = np.eye(n, dtype=complex)
    zero = np.zeros_like(identity)
    S = np.block([[zero, identity], [-identity, zero]])
    digest = sha256()
    maxima = dict(independent_body_adjoint=0., reflected_clock=0.,
                  geometric_density=0., literal_generator_relative=0.,
                  spectral_generator_coefficient_relative=0.,
                  real_axis_Green_identity_relative=0.,
                  conormal_definition_relative=0.,
                  retained_body_norm=0., non_Hermitian_body_norm=0.)
    for name in names:
        path = base/name
        pin(path, original['archives'][name]['sha256'])
        with np.load(path, allow_pickle=False) as data:
            arrays = {key: data[key] for key in data.files}
        for index, C in enumerate(arrays['H18']):
            Cs = arrays['Hsharp18'][index]
            w = complex(arrays['right_clock'][index])
            ws = complex(arrays['reflected_clock'][index])
            m = complex(arrays['original_holomorphic_measure'][index])
            mu = float(arrays['measure'][index])
            # Strip the original reference quadrature weight. A quadrature
            # weight must not become a pointwise momentum density.
            reference_weight = m/w
            if (abs(reference_weight.imag) > 1e-12*abs(reference_weight)
                    or reference_weight.real <= 0):
                raise ValueError('Original positive reference quadrature required')
            density = mu/reference_weight.real
            G = density*identity
            b = 1/w
            result = reflected_native_conormal_graph_jets(
                b_jet=np.array([b, 0, 0, 0]),
                density_jet=np.array([G, zero, zero, zero]),
                body_jet=np.array([C, zero, zero, zero]),
                spectral_parameter_jet=np.array([0, 1, 0, 0], complex))
            J, Jz, Jy, Jzy = result['canonical_generator_jet']
            # Independently reconstruct from the SAVED reflected branch,
            # rather than calling the implementation's derivative helper.
            literal = np.block([[-w*C, abs(w)**2/density*identity],
                                [zero, ws*Cs]])
            literal_z = np.block([[zero, zero], [-G, zero]])
            maxima['independent_body_adjoint'] = max(
                maxima['independent_body_adjoint'], float(np.max(abs(Cs-C.conj().T))))
            maxima['reflected_clock'] = max(maxima['reflected_clock'], abs(ws-w.conjugate()))
            maxima['geometric_density'] = max(maxima['geometric_density'], abs(density-abs(w)))
            for key, actual, expected in (
                    ('literal_generator_relative', J, literal),
                    ('spectral_generator_coefficient_relative', Jz, literal_z),
                    ('real_axis_Green_identity_relative', J.conj().T@S+S@J, np.zeros_like(J))):
                # The identity's scale is the original generator, not its
                # cancellation remainder.
                error = (float(np.max(abs(actual)))/max(float(np.max(abs(J))), 1e-300)
                         if key == 'real_axis_Green_identity_relative'
                         else _relative(actual, expected))
                maxima[key] = max(maxima[key], error)
            if np.any(Jy) or np.any(Jzy):
                raise ArithmeticError('A fixed-background spectral path gained another direction')
            u = (np.arange(n)+1j*np.arange(n, 0, -1))/n
            du = (np.arange(n, 0, -1)-1j*np.arange(n))/(n+1)
            p = b.conjugate()*G@(b*du+C@u)
            maxima['conormal_definition_relative'] = max(
                maxima['conormal_definition_relative'],
                _relative((J@np.r_[u, p])[:n], du))
            maxima['retained_body_norm'] = max(maxima['retained_body_norm'], float(np.linalg.norm(C)))
            maxima['non_Hermitian_body_norm'] = max(maxima['non_Hermitian_body_norm'], float(np.linalg.norm(C-C.conj().T)))
            digest.update(np.ascontiguousarray(result['canonical_generator_jet']).tobytes())
            count += 1
    if count != 3832 or n != 18:
        raise ValueError('All original full-family coefficient nodes required')

    # Inspect the ORIGINAL independent-dual corner transport. This is not
    # an assertion that those analytic domains ought to be Hilbert domains.
    corner_base = ROOT/'artifacts/muon_native_dual_density_graph_20261011/run_1'
    pin(corner_base/'result.json')
    corner_report = json.loads((corner_base/'result.json').read_bytes())
    name = 'actual_dual_corner_maps.npz'
    pin(corner_base/name, corner_report['archives'][name]['sha256'])
    with np.load(corner_base/name, allow_pickle=False) as data:
        t = data['internal_native_conormal_return'].copy()
        ell = data['internal_left_trace_transfer'].copy()
    corner = dict(
        original_internal_corners=len(t),
        independent_dual_pairing_product_error=float(np.max(abs(t*ell-1))),
        unchanged_primal_Hilbert_Green_defect_max=float(np.max(abs(t-1))),
        unchanged_primal_Hilbert_Green_defect_nonzero_count=int(np.count_nonzero(abs(t-1) > 1e-12)),
        diagnostic_equation='For M=diag(I,t I), M_dagger S M-S has blocks (0,(t-1)I;-(conj(t)-1)I,0)',
        original_analytic_independent_dual_domain_is_a_failed_physical_equation=False,
        original_domain_replaced_or_corner_phase_chosen=False,
        joint_primal_and_dual_native_domain_identified=False,
    )
    for name in ('muon_owned_native_product_connection',
                 'muon_primal_intrinsic_lepton_operator',
                 'muon_reflected_native_conormal_graph',
                 'muon_transported_native_pairing', 'muon_native_dual_density_graph',
                 'muon_chronological_clifford_graph'):
        pin(ROOT/'src/bhsm/interface'/(name+'.py'))
    pin(Path(__file__).resolve())
    cut = ROOT/('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
                'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
                'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    pin(cut, 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b')
    result = dict(
        classification='EVALUATED_EXACT_CANONICAL_CONORMAL_GRAPH_OF_SAVED_REFLECTED_NATIVE_POSITIVE_FORM',
        coefficient_nodes=count, point_fiber_components=n, closed_lepton_families=3,
        starting_angular_space='normalized constant scalar; original full C18 body',
        nonzero_spin_gauge_and_Higgs_bodies_retained=True,
        complex_base_projected_to_real=False,
        graph_jet_stream_sha256=digest.hexdigest(), maxima=maxima,
        original_corner_domain_diagnostic=corner,
        derived_real_common_A_native_temporal_binding_already_available=True,
        canonical_generic_unbound_slot_proves_absence_of_component=False,
        temporal_connection_or_contour_owner_changed=False,
        spectral_jet_scope='partial in z at fixed saved coefficients and pairing; x=z, y absent; not unsquared physical E or magnetic field',
        real_two_parameter_Hilbert_jets_conjugate_coefficients=True,
        independent_complex_analytic_source_tangents_conjugated=False,
        new_field_or_history_integrations=0, old_campaign_replays=0,
        physical_full_angular_or_radial_convergence=False,
        full_physical_outgoing_derivative_at_2e_minus_10_passed=False,
        physical_outgoing_domain_evaluated=False, full_native_P_strat_realized=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None, original226_after_correction=None,
        input_hashes=dict(sorted(pins.items())),
    )
    if any(sha256((ROOT/path).read_bytes()).hexdigest() != value for path, value in pins.items()):
        raise RuntimeError('Consumed operands changed during application')
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True,
        allow_nan=False)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(coefficient_nodes=count, maxima=maxima, corner=corner,
                         result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    materialize(args.output)
