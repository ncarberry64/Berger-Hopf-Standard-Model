"""Apply corrected two-term sources to the actual full302/original226 birth.

This reads a completed changing-stage receipt, but consumes its BIRTH child
reconstitution only. It does not turn the reset candidate into a solution.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src')); sys.path.insert(0, str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_coupled_reset_continuation import (
    coupled_reset_application, central_reset_Ward_rows,
)
from bhsm.interface.muon_corrected_birth_source_endpoint import (
    corrected_birth_endpoint_source, endpoint_formal_area_offset,
)
from bhsm.interface.muon_complex_paired_normal_action import complex_proper_normal_trace
from bhsm.interface.muon_holomorphic_current_source import holomorphic_current_stage
from bhsm.interface.muon_reset_trial_role_application import reset_role_indices
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(x):
    if isinstance(x, dict): return {k:clean(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)): return [clean(v) for v in x]
    if isinstance(x, np.ndarray): return clean(x.tolist())
    if isinstance(x, (complex, np.complexfloating)): return [float(x.real), float(x.imag)]
    if isinstance(x, np.generic): return x.item()
    return x


def materialize(stage_folder, output):
    out = ROOT/output
    if out.exists(): raise FileExistsError('preserve every endpoint source application')
    pins = {}; archives = {}
    def read(folder, name, md=None):
        p = ROOT/folder/name; b = p.read_bytes(); h = sha256(b).hexdigest()
        pins[p.relative_to(ROOT).as_posix()] = h
        if md is not None and h != md['archives'][name]['sha256']:
            raise ValueError('same admitted birth source archive required')
        if p.suffix == '.json': return json.loads(b)
        with np.load(p, allow_pickle=False) as z:
            return {k:z[k].copy() for k in z.files}
    tf = Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1')
    rf = Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1')
    tm, rm, sm = [read(p, 'result.json') for p in (tf, rf, stage_folder)]
    trace = read(tf, 'application.npz', tm); saved = read(rf, 'application.npz', rm)
    raw, ref = trace['raw_pair'], trace['reference_pair']
    if (not np.array_equal(raw, saved['raw_pair'])
            or not np.array_equal(ref, saved['reference_pair'])
            or tm['action_parameters'] != rm['action_parameters']
            or sm['action_parameters'] != rm['action_parameters']):
        raise ValueError('same final reset raw/reference/parameter graph required')
    weights_path = next(Path(p) for p in tm['input_hashes']
                        if p.endswith('true_phase_projection_inputs.npz'))
    wp = ROOT/weights_path; wb = wp.read_bytes()
    if sha256(wb).hexdigest() != tm['input_hashes'][weights_path.as_posix()]:
        raise ValueError('same fixed action weights required')
    pins[weights_path.as_posix()] = sha256(wb).hexdigest()
    with np.load(wp, allow_pickle=False) as z:
        weights = z['state_weights'].copy(); normalization = z['normalization_coordinates'].copy()
    phase, _ = retained_input('outgoing', pins); rep = phase['representation']
    params = rm['action_parameters']; R = trace['master_lift']; P = R[:268, :252]
    print(json.dumps(dict(stage='fresh_original302_endpoint_started')), flush=True)
    base = coupled_reset_application(raw, ref, rep, weights, normalization,
        action_parameters=params, compute_jacobian=False)
    if base['groups'] != rm['groups']: raise ValueError('all original226 row roles must agree')
    ward = central_reset_Ward_rows(base, raw, rep)
    roles = reset_role_indices(base['groups']); J = saved['original226_Jacobian']
    T = np.zeros((6, 504), complex)
    for arm in range(2):
        T[arm*3:(arm+1)*3, arm*252:arm*252+106] = complex_proper_normal_trace(raw[arm], P)['trace']
    mw = abs(R.T)@np.tile(np.r_[weights, np.ones(170)], 2)
    out.mkdir(parents=True)
    def save(name, arrays):
        p = out/name; _compressed_npz(p, arrays)
        if p.stat().st_size > 10*1024**2: raise ValueError('split all original endpoint arrays')
        archives[name] = dict(bytes=p.stat().st_size, sha256=sha256(p.read_bytes()).hexdigest())
    save('same_birth_full302_and_original226.npz', dict(raw_pair=raw, reference_pair=ref,
        master_lift=R, fresh_joint_Hessian=base['action']['hessian'],
        fresh_parent_own_Hessian=base['action']['parent']['hessian'],
        fresh_original226_rows=base['residual'], saved_original226_rows=saved['original226_rows'],
        supplied_same_point_original226_Jacobian=J,
        fresh_area_parameter_source=base['area_parameter_source'],
        fresh_full302_saddle=base['projection']['saddle'],
        fresh_full302_original_phase_rows=base['projection']['original_phase_rows'],
        fresh_full302_transpose_rows=base['projection']['analytic_adjoint_rows'],
        fresh_joint_temporal_dual=base['action']['temporal_cotangent'],
        fresh_parent_own_Pi=base['action']['parent']['gradient'][106:212],
        fresh_joint_Pi=base['action']['gradient'][base['action']['velocity_indices']],
        original_Ward_rows=ward['rows'], original_nonlinear_Ward_identity=ward['original_nonlinear_identity'],
        actual_position_trace_map=T, master_direction_weights=mw))
    results = {}
    for case, gamma_direction in (('normal_basis', 0), ('area_source', 1)):
        parent = read(stage_folder, case+'_consumed_birth_parent_source.npz', sm)
        child = read(stage_folder, case+'_consumed_birth_child_source.npz', sm)
        dh = np.r_[parent['direction_high'], child['direction_high']]
        dl = np.r_[parent['direction_low'], child['direction_low']]
        app = corrected_birth_endpoint_source(base, J, dh, dl, T,
            parameter_amplitude=gamma_direction)
        arrays = app.pop('arrays')
        arrays.update(raw_pair=raw, reference_pair=ref,
            raw_direction_high=(R@dh).reshape(2,268), raw_direction_low=(R@dl).reshape(2,268),
            direct_reference_direction=np.zeros((2,268), complex))
        # Keep both coefficient terms as separate analytic directions in the
        # full18 current image. No rounded source combination or dagger.
        raw_dirs = np.stack((arrays['raw_direction_high'], arrays['raw_direction_low']), axis=-1)
        for arm, side in ((0, 'parent'), (1, 'child')):
            current = holomorphic_current_stage(raw[arm], raw_dirs[arm], raw[0], raw_dirs[0],
                ref, np.zeros((2,268,2), complex), rep, side=side)
            save(case+'_'+side+'_full18_current_and_trace_source.npz',
                 {k:v for k,v in current.items() if isinstance(v,np.ndarray)})
        rounded = dh+dl
        mag = max(float(np.max(abs(mw*rounded))), abs(gamma_direction), 1.)
        controls = {}; fd = []
        eta = R.T@raw.reshape(-1)
        for label, step in (('primary', 2e-5), ('half_step', 1e-5)):
            epsilon = step/mag
            sides = []
            for sign in (1, -1):
                trial = (R@(eta+sign*epsilon*rounded)).reshape(2,268)
                trial_app = coupled_reset_application(trial, ref, rep, weights, normalization,
                    action_parameters=params, compute_jacobian=False)
                # Tension is an analytic coefficient-direction control,
                # not a physical positive-gamma assignment or fit.
                actual = endpoint_formal_area_offset(trial_app,
                    sign*epsilon*gamma_direction, normalization)
                sides.append(actual['residual'])
                prefix = label+('_positive' if sign == 1 else '_negative')
                arrays[prefix+'_full302_original_phase_rows'] = actual['projection']['original_phase_rows']
                arrays[prefix+'_full302_transpose_rows'] = actual['projection']['analytic_adjoint_rows']
                arrays[prefix+'_full302_trace_rows'] = actual['projection']['trace_rows']
                arrays[prefix+'_full302_named_frame_rows'] = actual['projection']['named_frame_rows']
                print(json.dumps(dict(stage='endpoint_directional_application', case=case,
                    step_label=label, sign=sign,
                    original302_phase_rows_max=float(np.max(abs(actual['projection']['original_phase_rows']))),
                    original226_max=float(np.max(abs(actual['residual']))))), flush=True)
            derivative = (sides[0]-sides[1])/(2*epsilon)
            fd.append(derivative)
            expected = arrays['original226_response_high']+arrays['original226_response_low']
            differences = {name:dict(max_abs=float(np.max(abs((derivative-expected)[ids]))),
                response_norm=float(np.linalg.norm(derivative[ids]))) for name,ids in roles.items()}
            controls[label] = dict(weighted_step=step, coefficient_step=epsilon,
                magnitude=mag, all_rows_difference_max=float(np.max(abs(derivative-expected))),
                all_rows_difference_norm=float(np.linalg.norm(derivative-expected)), role_differences=differences)
            arrays[label+'_full_endpoint_source_FD'] = derivative
            arrays[label+'_positive_endpoint_rows'] = sides[0]
            arrays[label+'_negative_endpoint_rows'] = sides[1]
        controls['step_halving'] = dict(all_rows_difference_norm=float(np.linalg.norm(fd[1]-fd[0])),
            all_rows_relative_difference=float(np.linalg.norm(fd[1]-fd[0])/max(np.linalg.norm(fd[1]), np.finfo(float).tiny)),
            role_difference_max={name:float(np.max(abs((fd[1]-fd[0])[ids]))) for name,ids in roles.items()})
        app['directional_original_action_controls'] = controls
        app['role_groups'] = {name:ids.tolist() for name,ids in roles.items()}
        app['group_source_readouts'] = {name:dict(max_abs=float(np.max(abs(
            (arrays['original226_response_high']+arrays['original226_response_low'])[ids]))),
            norm=float(np.linalg.norm((arrays['original226_response_high']+arrays['original226_response_low'])[ids])))
            for name,ids in base['groups'].items()}
        save(case+'_full_endpoint_source_response.npz', arrays)
        results[case] = app
    for name,module in sorted(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if name.startswith('bhsm.') and path:
            try: rel = Path(path).relative_to(ROOT).as_posix()
            except ValueError: continue
            pins[rel] = sha256((ROOT/rel).read_bytes()).hexdigest()
    for path in ('scripts/evaluate_muon_corrected_birth_source_endpoint.py',
                 'tests/test_muon_corrected_birth_source_endpoint.py'):
        pins[path] = sha256((ROOT/path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):
        raise ValueError('endpoint source producer input changed')
    result = dict(classification='EVALUATED_CORRECTED_TWO_TERM_BIRTH_SOURCE_FULL302_AND_ORIGINAL226_ENDPOINT_RESPONSE',
        archives=archives, input_hashes=pins, action_parameters=params, applications=results,
        fresh_base_original226_max=float(np.max(abs(base['residual']))),
        pinned_base_original226_max=float(np.max(abs(saved['original226_rows']))),
        fresh_minus_pinned_base_rows_max=float(np.max(abs(base['residual']-saved['original226_rows']))),
        fresh_minus_pinned_Hessian_max=float(np.max(abs(base['action']['hessian']-trace['full_joint_Hessian']))),
        original302_phase_rows_max=float(np.max(abs(base['projection']['original_phase_rows']))),
        original302_transpose_rows_max=float(np.max(abs(base['projection']['analytic_adjoint_rows']))),
        baseline_absolute_reset_guard_passed=False, reset_tolerance=2e-10,
        endpoint_natural_response_not_forced_zero=True, corrected_child_inherited_source_count=1,
        parent_and_child_both_from_fresh_same_action_birth_reconstitution=True,
        source_seed_reference_held_only_for_declared_normal_and_area_partials=True,
        full18_current_trace_source_exported_before_projection=True,
        original_common_normal_port_uses_retained_normal_amplitude_coordinate=True,
        proper_normal_displacement_is_separate_first_variation_not_force_calibration=True,
        physical_formation_first_hit_gamma_or_pole_selected=False,
        error_scope='exact stored J/H/two-term arithmetic plus limited binary full-action directional/halving controls; endpoint third-action production, finite stage/source quality, physical domain and Pauli errors not enclosed')
    p=out/'result.json'; p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='corrected_birth_endpoint_source_complete',
        result_sha256=sha256(p.read_bytes()).hexdigest())), flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage-folder',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); materialize(args.stage_folder,args.output)
