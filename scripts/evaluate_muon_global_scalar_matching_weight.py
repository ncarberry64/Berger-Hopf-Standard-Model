"""Apply the recorded fixed-Y weight and same-clock scalar comparator globally."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from bhsm.interface.muon_global_scalar_matching_weight import (
    global_scalar_matching_weight, high_frequency_clock_amplification,
    same_clock_scalar_reference_impulse)
from bhsm.interface.muon_global_causal_laplace_response import global_laplace_weak_boundary_identity
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out = ROOT/output
    if out.exists():
        raise FileExistsError('preserve all original global matching applications')
    pins, receipts, archives = {}, {}, {}

    def read(folder, name):
        path = folder/name
        digest = sha256(path.read_bytes()).hexdigest()
        if name != 'result.json' and digest != receipts[folder]['archives'][name]['sha256']:
            raise RuntimeError('same coupled source or comparison changed: '+str(path))
        pins[path.relative_to(ROOT).as_posix()] = digest
        if name == 'result.json':
            data = json.loads(path.read_bytes())
            pins.update(data['input_hashes'])
            receipts[folder] = data
            return data
        with np.load(path, allow_pickle=False) as z:
            return {k: z[k].copy() for k in z.files}

    global_folder = ROOT/'artifacts/muon_global_causal_laplace_response_20261011/run_2'
    source_folder = ROOT/'artifacts/muon_initial_canonical_radial_return_20261011/run_1'
    matching_folder = ROOT/'artifacts/muon_native_local_overlap_matching_20261011/run_3'
    gm, sm, mm = [read(f, 'result.json') for f in (global_folder, source_folder, matching_folder)]
    base = read(global_folder, 'complete_global_scalar_Laplace_action.npz')
    names = sorted((k for k in gm['archives'] if k.startswith('actual_Laplace_field_pairing_points_')),
                   key=lambda s: int(Path(s).stem.rsplit('_', 1)[1]))
    points = [read(global_folder, k) for k in names]
    pairing = np.concatenate([a['same_angular_direct_sum_radial_pairing_at_quadrature'] for a in points])
    measure = np.concatenate([a['original_holomorphic_measure'] for a in points])
    tau = base['relative_proper_clock_points']
    future = base['future_source_domain_mask']
    source = read(source_folder, 'actual_birth_final_and_source_pairings.npz')
    endpoint = read(source_folder, 'initial_and_final_canonical_boundary.npz')
    names = sorted((k for k in sm['archives'] if k.startswith('original_canonical_response_nodes_')),
                   key=lambda s: int(Path(s).stem.rsplit('_', 1)[1]))
    action = np.concatenate([read(source_folder, k)['original_action_rows'] for k in names])
    b = np.zeros_like(action)
    b[574] = source['actual_right_birth_sources']
    left = source['literal_left_birth_sources']
    initial = np.r_[endpoint['initial_complete_action_cotangent'], np.zeros((8, 8), complex)]
    direct_sum = lambda z: z[..., :4, :4]+z[..., 4:, 4:]
    for rel in (Path(__file__).relative_to(ROOT).as_posix(),
                'src/bhsm/interface/muon_global_scalar_matching_weight.py',
                'tests/test_muon_global_scalar_matching_weight.py',
                'src/bhsm/interface/muon_global_causal_laplace_response.py',
                'src/bhsm/interface/muon_native_local_overlap_matching.py',
                'src/bhsm/interface/muon_literal_euclidean_wall_action.py',
                'scripts/evaluate_muon_reached_trace_action.py'):
        pins[rel] = sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)

    def save(name, arrays):
        path = out/name
        deterministic_archive(path, arrays)
        if path.stat().st_size >= 10*1024**2:
            raise ArithmeticError('split numerical arrays before publication')
        archives[name] = dict(bytes=path.stat().st_size, sha256=sha256(path.read_bytes()).hexdigest())

    records = []
    for side in ('incoming', 'outgoing'):
        matched = next(r for r in mm['records'] if r['kind'] == 'coupled_radial_matching' and r['side'] == side)['record']
        args = matched['calibrated_external_covector_probes'][1]
        parameters = dict(matched_mass_action=args['matched_internal_and_external_fermion_mass_action'],
            fixed_Y=args['fixed_Y'], kinetic_residue=matched['coupled_matching']['actual_scalar_kinetic_residue'])
        comparison = read(matching_folder, f'{side}_coupled_scalar_matching.npz')
        Cref = comparison['data_coupled_matching_same_coordinate_reference_coefficients']
        prior = []
        for order in (6, 8):
            a = global_scalar_matching_weight(pairing, measure, tau, future, **parameters, quadrature_order=order)
            rates = a['proper_Laplace_rates']
            r = same_clock_scalar_reference_impulse(Cref, tau,
                (base['proper_clock_nodes'][-1]-base['proper_clock_nodes'][575]).item(), rates)
            # The analytic after-impulse germ has support only on the
            # recorded chronological future, even on a complex contour.
            r['reference_driven_point_pairing'][~future] = 0
            reference = global_scalar_matching_weight(r['reference_driven_point_pairing'], measure, tau,
                future, **parameters, quadrature_order=order)
            weak = global_laplace_weak_boundary_identity(action, b, left, base['proper_clock_nodes'],
                rates, initial, endpoint['final_dynamic_force'], birth_node=575)
            weak = {k: direct_sum(v) for k, v in weak.items() if isinstance(v, np.ndarray)}
            ref_inv = reference['finite_radial_inverse_action_Green']
            ref_driven = -ref_inv
            D = r['proper_reference_inverse_action_coefficients'][0]+rates**2*r['proper_reference_inverse_action_coefficients'][2]
            ref_identity = D[:, None, None]*ref_driven-np.eye(4)[None]-r['reference_Laplace_differential_endpoint_contact']
            difference = a['finite_global_scalar_covector_samples']-reference['finite_global_scalar_covector_samples']
            fields = {k: v for k, v in a.items() if isinstance(v, np.ndarray)}
            fields.update({'reference_'+k: v for k, v in reference.items() if isinstance(v, np.ndarray)})
            fields.update({k: v for k, v in r.items() if isinstance(v, np.ndarray)})
            fields.update(weak)
            fields.update(same_coordinate_subtracted_covector_samples=difference,
                same_coordinate_subtracted_covector=np.array(a['quadrature_weights']@difference),
                actual_minus_reference_final_weak_conormal=weak['final_canonical_endpoint_contact']-r['reference_final_weak_conormal_contact'],
                reference_Laplace_differential_boundary_identity=ref_identity,
                comparison_original_Lorentz_coefficients=Cref)
            diagnostic = high_frequency_clock_amplification(tau[future], matched_mass_action=parameters['matched_mass_action'])
            fields.update({'high_frequency_'+k: v for k, v in diagnostic.items() if isinstance(v, np.ndarray)})
            name = f'{side}_global_same_clock_matching_q{order}.npz'
            save(name, fields)
            complex_record = lambda v: dict(real=float(np.real(v)), imag=float(np.imag(v)))
            rec = dict(side_parameter_trial=side, same_global_trajectory=True, quadrature_order=order,
                parameters=parameters, archive=name,
                reached_covector=complex_record(a['finite_global_scalar_covector']),
                same_clock_reference_covector=complex_record(reference['finite_global_scalar_covector']),
                reached_minus_same_clock_reference_covector=complex_record(fields['same_coordinate_subtracted_covector']),
                future_exponential_modulus_max=a['future_clock_exponential_modulus_max'],
                all_original_clock_exponential_argument_max=a['original_clock_exponential_argument_max'],
                integrated_absolute_reached_sample_value=a['integrated_absolute_sample_value'],
                original_weak_endpoint_identity_max=float(np.max(abs(weak['global_weak_source_endpoint_identity']))),
                reference_differential_boundary_identity_max=float(np.max(abs(ref_identity))),
                actual_final_weak_conormal_norm=float(np.linalg.norm(weak['final_canonical_endpoint_contact'])),
                actual_minus_reference_final_weak_conormal_norm=float(np.linalg.norm(fields['actual_minus_reference_final_weak_conormal'])),
                before_source_integral_norm=float(np.linalg.norm(a['finite_before_source_pairing'])),
                high_frequency_log_modulus_max=diagnostic['future_exponential_log_modulus_max'].tolist(),
                high_frequency_log_coordinates=diagnostic['log_coordinates'].tolist())
            prior.append(fields['same_coordinate_subtracted_covector'].item())
            records.append(rec)
            print(json.dumps(rec, sort_keys=True), flush=True)
        records[-1]['same_coordinate_subtraction_q6_q8_difference'] = float(abs(prior[1]-prior[0]))
    if any(sha256((ROOT/p).read_bytes()).hexdigest() != h for p, h in pins.items()):
        raise RuntimeError('consumed trajectory/action/comparator changed during matching')
    result = dict(classification='EVALUATED_GLOBAL_SCALAR_FIXED_Y_MATCHING_WEIGHT_AND_SAME_CLOCK_REFERENCE_0_TO_32',
        input_hashes=pins, archives=archives, records=records,
        original_nodes=1151, all_source_and_corner_edges=1150,
        source_section='recorded birth2r radial source and independent literal target, two diagonal4 spectator sums',
        reference_action='C_L=-Za+Zz^2; literal L_E=-L_L(v_L=i v_E) gives -Z d_tau^2+Za with the SAME complex clock/initial Cauchy/free-final canonical action',
        reference_current_kernel='-sinh(sqrt(a)*tau)/(Z sqrt(a)), zero coordinate and canonical trace before source; projected raw2r weak row has impulse2I',
        reference_canonical_endpoint_return_dropped=False,
        reached_gauge_H_Gauss_frame_or_clock_contacts_dropped=False,
        original_complex_measure_replaced_by_absolute_measure=False,
        quantum_covariance_or_continuum_overlap_subtraction_proven=False,
        integral_for_y_above_32_evaluated_or_enclosed=False,
        old_static_meromorphic_tail_grafted=False,
        actual_growth_on_log64_identified_as_physical_divergence=False,
        physical_a_mu=None, physical_g_mu=None,
        error_scope='binary64 executed full impulse/source/clock and numerical q6/q8 scalar weight; endpoint/source and reference differential identities evaluated. Time/quadrature/clock-polynomial/physical-domain errors and omitted high-s integral remain separate, not certified.')
    path = out/'result.json'
    path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(result_sha256=sha256(path.read_bytes()).hexdigest(), archives=len(archives))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    materialize(parser.parse_args().output)
