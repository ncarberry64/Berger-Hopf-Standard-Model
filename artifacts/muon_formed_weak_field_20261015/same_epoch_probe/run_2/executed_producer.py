"""New local B/e source operand on the two exact retained finite pole stages.

Only source/curvature/canonical-vertex algebra is evaluated. No history, D5
action, induced field response, retarded boundary, or physical Gamma_B is
solved. Unit e=1 means a coefficient PER UNIT canonical EM coupling; it does
not assign an empirical or native coupling to the formed muon benchmark.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import zipfile

import numpy as np


D5 = 'artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2'
TRIAL = 'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000'
D5_RESULT_SHA = '3647c939e8ee150d79483f1e32066e08cee261cac82ef0ef29eecf009a5f75f2'


def _max(a): return float(np.max(abs(a)))


def _relative(rows, *operands):
    scale = max((_max(a) for a in operands), default=0.)
    return _max(rows)/(scale or 1.)


def _npz(path, arrays):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in sorted(arrays.items()):
            b = BytesIO(); np.lib.format.write_array(b, np.asarray(value), allow_pickle=False)
            info = zipfile.ZipInfo(name+'.npy', (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, b.getvalue())


def _clean(v):
    if isinstance(v, dict): return {k:_clean(a) for k,a in v.items()}
    if isinstance(v, (list, tuple)): return [_clean(a) for a in v]
    if isinstance(v, np.ndarray): return _clean(v.tolist())
    if isinstance(v, (complex, np.complexfloating)): return dict(real=float(v.real), imag=float(v.imag))
    if isinstance(v, np.generic): return v.item()
    return v


class Inputs:
    def __init__(self, root): self.root, self.hashes = root, {}
    def read(self, relative, expected=None):
        path = self.root/relative; raw = path.read_bytes(); digest = sha256(raw).hexdigest()
        if expected is not None and digest != expected: raise ValueError('source binding changed: '+relative)
        self.hashes[relative] = digest
        if path.suffix == '.json': return json.loads(raw)
        if path.suffix == '.npz':
            with np.load(BytesIO(raw), allow_pickle=False) as a: return {k:a[k].copy() for k in a.files}
        return raw.decode('utf8')


def _affine_clock(raw):
    # Original inherited parent/reference law, as in the pinned D5 producer.
    return np.r_[raw[37:74], np.zeros(61), raw[99], np.zeros(169)]


def _wall_background(raw, raw_time, parent, refs, wall_map, *, WALL, M, profile):
    actual = np.einsum('fcj,j->fc', wall_map, raw[100:180])
    actual_time = np.einsum('fcj,j->fc', wall_map, raw_time[100:180])
    own = []
    for a in (parent, refs[0], refs[1]):
        v, d = profile(a, _affine_clock(a)[:, None], np.array([WALL]))
        own.append((v[0, 0], d[0, 0, 0]))
    mech = own[0][0]-own[1][0]+own[2][0]
    mech_time = own[0][1]-own[1][1]+own[2][1]
    actual[2:] += M*(mech-1)
    actual_time[2:] += M*mech_time
    return actual, actual_time, mech, mech_time


def point_curvature(Q, derivative_matrices, point_values, background, epsilon):
    """Analytic complex continuation of the existing local magnetic point jet.

    Keep derivative, right-coframe structure and ACTUAL-background commutator
    separately. No background coefficient is conjugated or set to zero.
    """
    f = np.asarray(Q, complex)[2:]
    value = np.einsum('ichA,h->icA', f, point_values)
    derivative = np.einsum('h,jhk,ickA->jicA', point_values, derivative_matrices, f)
    structure = 2*np.einsum('ijk,kcA->ijcA', epsilon, value)
    comm = np.zeros((3, 3, 4, 3), complex)
    for i in range(3):
        for j in range(3):
            comm[i, j, :3] = (np.cross(background[i, :3], value[j, :3].T).T
                              -np.cross(background[j, :3], value[i, :3].T).T)/np.sqrt(2)
    curvature = derivative-derivative.swapaxes(0, 1)+structure+comm
    return dict(potential=value, coframe_derivative=derivative,
                coframe_structure_contact=structure,
                actual_background_commutator_contact=comm, curvature=curvature)


def run(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists(): raise FileExistsError('preserve each independent source application')
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_holomorphic_n1_magnetic_action import holomorphic_local_B_trace, magnetic_angular_trace
    from bhsm.interface.muon_holomorphic_current_source import _wall_coframe, _profile
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_intrinsic_scalar_discretization import (
        scalar_basis_values, real_scalar_basis_transform, real_scalar_basis_labels)
    from bhsm.interface.muon_matched_mechanical_source import epsilon
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    inp = Inputs(root)
    inp.read('AGENTS.md')
    md = inp.read(D5+'/result.json', D5_RESULT_SHA)
    for module in ('muon_holomorphic_n1_magnetic_action', 'muon_holomorphic_current_source',
                   'muon_holomorphic_em_current', 'muon_electromagnetic_soft_magnetic_source',
                   'muon_native_dirac_hamiltonian', 'muon_native_product_factor_graph',
                   'muon_intrinsic_scalar_discretization', 'muon_matched_mechanical_source',
                   'muon_parent_maxwell_full_weak'):
        inp.read('src/bhsm/interface/'+module+'.py')
    wall_path = next(p for p in md['input_hashes'] if p.endswith('/finite_moving_trace_run_1/application.npz'))
    wall_packet = inp.read(wall_path, md['input_hashes'][wall_path])
    wall_map = wall_packet['wall_trace_map']
    if wall_map.shape != (5, 4, 80): raise ValueError('same original full wall map required')
    angular = magnetic_angular_trace(); eps = epsilon()
    labels = real_scalar_basis_labels(3)
    n1 = np.flatnonzero([l[0] == 1 for l in labels])
    n0 = np.flatnonzero([l[0] == 0 for l in labels])
    all_point = (scalar_basis_values(np.eye(2, dtype=complex)[None], 3) @ real_scalar_basis_transform(3))[0]
    if _max(all_point.imag) > 2e-14: raise ValueError('real observation harmonic frame required')
    point_values = all_point[n1].real
    if len(n0) != 1 or abs(all_point[n0[0]]-1) > 2e-14:
        raise ValueError('unit-Haar constant harmonic required for the literal n0/n1 placements')
    if not np.array_equal(angular['harmonic_labels'], np.array([labels[j] for j in n1])):
        raise ValueError('same exact n1 coordinate frame required')
    alpha = lepton_current_hilbert_representation()['alpha']
    generators = lepton_unit_trace_gauge_representation()['generators']
    out.mkdir(parents=True)
    records, archives = [], {}
    for j in range(2):
        stage_path = f'{TRIAL}/stage_{j:04d}.npz'
        stage = inp.read(stage_path, md['input_hashes'][stage_path])
        cname = f'stage_{j:04d}_current_geometry_normal_and_material_trace.npz'
        saved = inp.read(D5+'/'+cname, md['archives'][cname]['sha256'])
        x = stage['stage_raw']; dx = saved['canonical_raw_coordinate_time_direction']
        if x.shape != (268,) or dx.shape != (268,) or not np.array_equal(x[260:264], saved['intrinsic_H_realified']):
            raise ValueError('same full raw/clock/H epoch required')
        def source_at(raw):
            R, N, _ = _wall_coframe(raw)
            a = holomorphic_local_B_trace(raw, dx[:, None],
                dict(induced_lapse_first=N.gradient @ dx[:100, None]), electric_charge=1., angular=angular)
            return a, R, N
        source, R, N = source_at(x)
        background, background_time, mechanical, mechanical_time = _wall_background(
            x, dx, stage['parent_source_raw'], stage['reference_stage_pair'], wall_map,
            WALL=WALL, M=M, profile=_profile)
        Q, Qt = source['Q'], source['Q_coordinate_time']
        value = point_curvature(Q, angular['derivative_matrices'], point_values, background[2:], eps)
        time = point_curvature(Qt, angular['derivative_matrices'], point_values, background[2:], eps)
        # d_t [A,deltaA] includes the independent [A_t,deltaA] contact too.
        extra_clock_contact = point_curvature(Q, angular['derivative_matrices'], point_values,
                                             background_time[2:], eps)['actual_background_commutator_contact']
        time['curvature'] += extra_clock_contact
        s, st = source['unit_charge_coefficients'], source['unit_charge_coefficient_time']
        target = R.value**2*np.einsum('ijA,c->ijcA', eps, s)
        target_time = (2*R.value*source['R4_coordinate_time']*np.einsum('ijA,c->ijcA', eps, s)
                       +R.value**2*np.einsum('ijA,c->ijcA', eps, st))
        # Direct canonical local vertex, all18 fibers. Independent route first
        # forms the gauge connection and then applies the canonical alpha.
        HB = -1j*np.einsum('aij,cjk,achA->Ahik', alpha, generators, Q[2:])/R.value
        HQt = -1j*np.einsum('aij,cjk,achA->Ahik', alpha, generators, Qt[2:])/R.value
        Rt = source['R4_coordinate_time'].item()
        HB_time = HQt-HB*Rt/R.value
        omega = np.einsum('cij,achA->Ahaij', generators, Q[2:])
        independent_HB = -1j*sum(alpha[a] @ omega[:, :, a] for a in range(3))/R.value
        # These are both literal multiplication placements, not adjoint copies.
        lower = HB.transpose(0, 1, 2, 3).reshape(3, 72, 18)
        upper = HB.transpose(0, 2, 1, 3).reshape(3, 18, 72)
        lower_time = HB_time.reshape(3, 72, 18)
        upper_time = HB_time.transpose(0, 2, 1, 3).reshape(3, 18, 72)
        # A bounded derivative check on this coefficient germ only. The
        # fixed direction is archived; no new clock/history is integrated.
        # Q is nonlinear only in position geometry/normal and the normalized
        # Higgs axis. Qtime is additionally LINEAR in their coordinate rates.
        # Source-inactive gauge/multiplier accelerations must not choose an
        # almost machine-zero difference step for this separate expression.
        nonlinear_geometry = np.r_[np.arange(37), 98]
        rate = max(float(np.max(abs(dx[nonlinear_geometry])/(1+abs(x[nonlinear_geometry])))),
                   _max(dx[260:264])/(_max(x[260:264]) or 1.))
        h = 3e-4/(rate or 1.)
        samples = {k:source_at(x+k*h*dx)[0] for k in (-2, -1, 1, 2)}
        fd = {key:(-samples[2][key]+8*samples[1][key]-8*samples[-1][key]+samples[-2][key])/(12*h)
              for key in ('Q', 'Q_coordinate_time')}
        checks = dict(
            coordinate_position_clock_rows=_max(dx[:37]-x[37:74]),
            coordinate_normal_clock_rows=float(abs(dx[98]-x[99])),
            coordinate_H_clock_rows=_max(dx[260:264]-x[264:268]),
            source_clock_first_minus_time_relative=_relative(source['Q_first'][0]-Qt, source['Q_first'][0], Qt),
            potential_zero_relative=_relative(value['potential'], Q),
            local_curvature_identity_relative=_relative(value['curvature']-target, target),
            local_curvature_clock_identity_relative=_relative(time['curvature']-target_time, target_time),
            local_canonical_vertex_convention_relative=_relative(HB-independent_HB, HB),
            Q_first_five_point_difference_relative=_relative(fd['Q']-source['Q_first'][0], fd['Q'], source['Q_first'][0]),
            Q_time_first_five_point_difference_relative=_relative(fd['Q_coordinate_time']-source['Q_coordinate_time_first'][0],
                                                                  fd['Q_coordinate_time'], source['Q_coordinate_time_first'][0]),
            direct_n0_to_n1_insertion_norm=float(np.linalg.norm(lower)),
            direct_n1_to_n0_insertion_norm=float(np.linalg.norm(upper)),
            direct_insertion_clock_norm=float(np.linalg.norm(HB_time)),
            nonzero_actual_background_spatial_norm=float(np.linalg.norm(background[2:])),
            analytic_complex_background_preserved=bool(np.any(x.imag != 0)))
        exact_checks = [checks[n] for n in ('source_clock_first_minus_time_relative', 'potential_zero_relative',
            'local_curvature_identity_relative', 'local_curvature_clock_identity_relative', 'local_canonical_vertex_convention_relative')]
        finite_difference_checks = [checks[n] for n in ('Q_first_five_point_difference_relative',
                                                         'Q_time_first_five_point_difference_relative')]
        if max(exact_checks) > 2e-10: raise ArithmeticError('same-stage exact source identity failed: '+str(checks))
        if max(finite_difference_checks) > 2e-7: raise ArithmeticError('bounded source coefficient derivative check failed: '+str(checks))
        arrays = {k:v for k,v in source.items() if isinstance(v, np.ndarray)}
        arrays.update(raw268=x, archived_canonical_raw_coordinate_time=dx,
            actual_background_wall_connection=background, actual_background_wall_connection_coordinate_time=background_time,
            actual_background_mechanical_profile=np.array(mechanical), actual_background_mechanical_profile_coordinate_time=np.array(mechanical_time),
            wall_radius=np.array(R.value), wall_induced_lapse=np.array(N.value),
            point_values=point_values, magnetic_angular_derivatives=angular['derivative_matrices'],
            expected_local_curvature_per_unit_e=target, expected_local_curvature_coordinate_time_per_unit_e=target_time,
            clock_background_commutator_contact=extra_clock_contact,
            canonical_H_B_coefficients_per_unit_e=HB, canonical_Qtime_H_insertion_per_unit_e=HQt,
            canonical_H_B_coordinate_time_per_unit_e=HB_time,
            direct_n0_to_n1_per_unit_e=lower, direct_n1_to_n0_per_unit_e=upper,
            direct_n0_to_n1_literal_transpose=lower.transpose(0, 2, 1),
            direct_n1_to_n0_literal_transpose=upper.transpose(0, 2, 1),
            direct_n0_to_n1_coordinate_time_per_unit_e=lower_time,
            direct_n1_to_n0_coordinate_time_per_unit_e=upper_time,
            finite_difference_Q_first=fd['Q'], finite_difference_Qtime_first=fd['Q_coordinate_time'],
            finite_difference_coordinate_step=np.array(h))
        arrays.update({'point_'+k:v for k,v in value.items()})
        arrays.update({'point_coordinate_time_'+k:v for k,v in time.items()})
        name = f'stage_{j:04d}_actual_unit_magnetic_source_and_direct_insertion.npz'
        _npz(out/name, arrays); archives[name] = sha256((out/name).read_bytes()).hexdigest()
        records.append(dict(stage=j, coordinate_time=stage['coordinate_time'].item(), wall_radius=R.value,
                            wall_induced_lapse=N.value, source_norm=float(np.linalg.norm(Q)),
                            source_coordinate_time_norm=float(np.linalg.norm(Qt)),
                            finite_difference_coordinate_step=h,
                            finite_difference_step_scope='3e-4/max nonlinear-source position/normal rate and normalized Higgs-axis rate; Qtime rate variables enter linearly',
                            checks=checks))
    result = dict(
        classification='EVALUATED_SAME_STAGE_UNIT_COUPLING_LOCAL_B_SOURCE_CURVATURE_AND_DIRECT_CANONICAL_INSERTION',
        original_stage_parent=TRIAL, original_clock_parent=D5,
        records=records, archives=archives, input_hashes=inp.hashes,
        unit_charge_convention='e=1 evaluates Q_B/e and H_B/e, coefficients per unit canonical EM coupling; no native or empirical charge value is inferred.',
        axes='All three Cartesian local magnetic directions, fixed retained right-coframe at g=I.',
        source_scope='Original local n1 wall trace and clock/H-axis motion, around the complete actual complex finite-stage background.',
        current_convention='H_B=(-i/R4) sum_a,c alpha18[a] G18[c] Q_B[2+a,c,h,axis]; chi_hat current Gram identity; no second e or Haar factor.',
        literal_angular_placements='Both n0->n1 and n1->n0 multiplication blocks evaluated with unit-Haar real harmonics. Reverse operator is not manufactured by Hilbert adjoint; literal transpose duals exported separately.',
        direct_vertex_is_nonzero=True,
        n0_only_restriction_not_used_to_infer_zero=True,
        n1_input_to_n2_image_or_full_angular_closure_not_computed=True,
        complex_Higgs_branches_conjugated=False,
        self_field_spin_mechanical_and_clock_background_set_zero=False,
        source_At_Ar_zero_only_by_explicit_prescribed_magnetic_trace=True,
        field_response_initial_or_terminal_data_not_selected=True,
        no_induced_geometry_Higgs_gauge_response_or_quantum_contact_assigned_zero=True,
        physical_retarded_Gamma_B=None, physical_muon_moment=None, physical_g_mu=None, physical_a_mu=None,
        integration_performed=False, prior_source_D5_history_campaign_restarted=False,
        exact_source_identity_relative_guard=2e-10,
        coefficient_five_point_derivative_guard=2e-7,
        error_scope='Binary64 source and direct vertex coefficient algebra on the archived complex germ; derivative check is finite-difference sanity only, not an outward physical or continuum bound.',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    encoded = json.dumps(_clean(result), sort_keys=True, indent=2, allow_nan=False)+'\n'
    (out/'result.json').write_text(encoded, encoding='utf8', newline='\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(result=str(out/'result.json'), sha256=sha256(encoded.encode()).hexdigest(),
                          source_stages=len(records), integration_performed=False)))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', required=True); p.add_argument('--output', required=True)
    a = p.parse_args(); run(a.repository, a.output)
