"""Audit physical-tail operands and both characteristics of actual finite poles.

Only frozen saved coefficient/mode applications are executed.  Neither a
physical exterior nor its E/B jet is created by this diagnostic.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from flint import acb, acb_mat, arb, ctx


def run(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 256
    pins = {}

    def read(relative):
        path = root / relative
        data = path.read_bytes()
        pins[relative.replace('\\', '/')] = sha256(data).hexdigest()
        if path.suffix == '.json':
            return json.loads(data)
        with np.load(path, allow_pickle=False) as archive:
            return {key: archive[key].copy() for key in archive.files}

    def matrix(value):
        value = np.asarray(value, complex)
        if value.ndim != 2 or not np.isfinite(value).all():
            raise ValueError('Complete finite original matrix required')
        return acb_mat([[acb(arb(float(z.real)), arb(float(z.imag)))
                         for z in row] for row in value])

    def norm_interval(value):
        square = sum((abs(value[i, j]) ** 2
                      for i in range(value.nrows())
                      for j in range(value.ncols())), arb(0)).sqrt()
        return [float(np.nextafter(float(square.lower()), -np.inf)),
                float(np.nextafter(float(square.upper()), np.inf))]

    def max_upper(value):
        return max(float(np.nextafter(float(abs(value[i, j]).upper()), np.inf))
                   for i in range(value.nrows()) for j in range(value.ncols()))

    def anchor(relative, needles):
        path = root / relative
        data = path.read_bytes()
        pins[relative] = sha256(data).hexdigest()
        lines = data.decode('utf8').splitlines()
        matches = []
        for needle in needles:
            matched = [(i + 1, line.strip()) for i, line in enumerate(lines)
                       if needle in line]
            if len(matched) != 1:
                raise ValueError('Source contract anchor is missing or ambiguous: ' + needle)
            matches.append(dict(line=matched[0][0], text=matched[0][1]))
        return dict(path=relative, sha256=pins[relative], anchors=matches)

    source_evidence = [
        anchor('src/bhsm/interface/muon_sigma_normal_collar_transport.py', [
            "raise ValueError('outside actual canonical history, original callback continuation required')",
            'No partial integral is substituted for the unknown full normalization.',
            'history_outside_supplied_cells_not_extrapolated=True']),
        anchor('src/bhsm/interface/muon_holomorphic_d5_trace_action.py', [
            'This first-order form does not select an exterior at the material wall;',
            'global_stationary_frequency_or_pole_not_inferred=True']),
        anchor('src/bhsm/interface/muon_retarded_spinor_tail_jet.py', [
            'The caller supplies the child block on the AE4 retarded domain of the SAME',
            'Every E/B/EB coefficient is',
            'future_support_or_first_hit_not_selected_by_matrix_elimination=True']),
        anchor('src/bhsm/interface/ae4_current_c2_canonical_stop_domain_bridge.py', [
            'selected = all(conditions.values())',
            'physical_stop_matched_operator_path_evaluated',
            'AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED']),
        anchor('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py', [
            'global self-adjoint stratified operator/domain has been constructed.',
            '"numerical_ell_star_evaluated_on_current_C2": False,']),
        anchor('src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py', [
            '"AE4_CURRENT_C2_FUTURE_CHILD_BLOCK_EVALUATED": False,',
            '"AE4_COMPLETE_BRST_CALDERON_PROJECTOR_EVALUATED": False,',
            '"CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,']),
        anchor('src/bhsm/interface/muon_coupled_lorentz_radial_green.py', [
            'the frozen-frequency polynomial with the full causal quantum propagator.',
            'physical_frequency_or_pole_selected=False,physical_overlap_subtracted=False,']),
    ]
    prior = read('artifacts/muon_physical_outgoing_energy_20261015/outgoing_domain/run_1/result.json')
    indices = np.array([2, 3, 8, 9, 14, 15])
    ambient = np.arange(128, 256)
    I = acb_mat(np.eye(128).tolist())
    records = []
    for stage in range(2):
        coefficient = read(f'artifacts/muon_physical_outgoing_energy_20261015/retained_inputs/d5_coefficients/stage_{stage:04d}_current_geometry_normal_and_material_trace.npz')
        for branch in range(2):
            pole = read(f'artifacts/muon_physical_outgoing_energy_20261015/split_poles/run_1/stage_{stage:04d}_branch_{branch}_actual_finite_simple_pole.npz')
            r = matrix(pole['normalized_right6'])
            if r.nrows() != 6 or r.ncols() != 1:
                raise ValueError('Complete original C6 finite pole trace required')
            for sheet in ('plus', 'minus'):
                T = matrix(coefficient[f'eta_{sheet}_original_principal_time_Clifford128'])
                N = matrix(coefficient[f'eta_{sheet}_original_principal_normal_Clifford128'])
                V = matrix(coefficient[f'eta_{sheet}_normal_mode_right_point_lift'][np.ix_(ambient, indices)])
                y = V * r
                A = T * N
                positive = (I + A) * y / 2
                negative = (I - A) * y / 2
                bounds = [norm_interval(positive), norm_interval(negative)]
                if not all(bound[0] > 0 for bound in bounds):
                    raise ArithmeticError('Characteristic-image nonvanishing not certified')
                energy = complex(pole['energy'].item())
                records.append(dict(stage=stage, branch=branch, sheet=sheet,
                    finite_energy=[energy.real, energy.imag],
                    original_localized_complex_components=6,
                    original_carrier_complex_components=128,
                    right_C6_norm_interval=norm_interval(r),
                    full_lifted_trace_norm_interval=norm_interval(y),
                    plus_characteristic_image_norm_interval=bounds[0],
                    minus_characteristic_image_norm_interval=bounds[1],
                    both_actual_characteristic_images_nonzero=True,
                    reconstruction_rows_upper=max_upper(positive + negative - y),
                    analytic_characteristic_involution_rows_upper=max_upper(A*A-I),
                    interpretation='These are analytic point-characteristic images of an actual saved finite pole trace. Their Euclidean sizes certify nonvanishing of frozen complex vectors only; they are not physical positive-flux projectors, normalized resonance states, or an exterior selection.'))
    result = dict(
        classification='ACTUAL_FINITE_POLE_CHARACTERISTIC_NONVANISHING_AND_PHYSICAL_TAIL_OPERAND_EVIDENCE',
        arithmetic='MP256 complex balls on exact stored B64 inputs; upstream geometry, radial and physical exterior errors are not included',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_evidence=source_evidence, input_sha256=pins,
        actual_finite_pole_characteristic_images=records,
        preserved_nonzero_finite_causal_remainder_norm=prior['actual_existing_tail_limit']['actual_finite_causal_final_field_remainder_norm'],
        actual_normal_flow_termination=prior['actual_existing_tail_limit']['normal_flow_prefixes'],
        first_missing_equation_application=dict(
            original_unsquared_normal_equation='D(E,B)=A_n(s,E,B) partial_s+A_parallel(s,E,B); in the transported full frame Q_ext=-A_n^-1 A_parallel plus the owned frame-derivative contact',
            smallest_unavailable_application='Q_ext,-+(s,E,B) Y_+(s,E,B) beyond the supplied canonical history/collar',
            energy_first='Q_ext,-+,E Y_+ + Q_ext,-+ Y_+,E, including actual E-dependent domain and frame contacts',
            magnetic_first='Q_ext,-+,B Y_+ + Q_ext,-+ Y_+,B, including actual B-dependent field, source, domain and frame contacts',
            required_field='Action-produced exterior coframe/lapse/shift/spin connection, gauge field, sigma/eta density/inclusion, same-action radiation or certified stop/transmission germ; intrinsic Higgs remains its once-only seam term',
            nonzero_characteristic_images_do_not_prove_mixing_nonzero=True,
            mixing_cancellation_proved=False,
            reason_cancellation_not_evaluated='Q_ext and the continued Y_+ are not bound. The new nonvanishing check only excludes obtaining cancellation by deleting the entire reached point-characteristic image. No physical nonzero mixing value or alternative exterior is asserted.'),
        physical_outgoing_trace=None, physical_outgoing_energy_jet=None,
        physical_outgoing_magnetic_jet=None, physical_full_derivative_pass=False,
        physical_radial_convergence_established=False,
        physical_two_spin_state_normalized=False, physical_muon_magnetic_moment=None,
        new_physical_exterior_integrations=0, coupled_matching_corrections_applied=0,
        completed_source_D5_profile_history_canonical_campaigns_restarted=False)
    path = out / 'result.json'
    path.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps(dict(result=str(path), sha256=sha256(path.read_bytes()).hexdigest(),
        minimum_actual_characteristic_image_norm_lower=min(record[key][0] for record in records
            for key in ('plus_characteristic_image_norm_interval', 'minus_characteristic_image_norm_interval')))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    arguments = parser.parse_args()
    run(arguments.repository, arguments.output)
