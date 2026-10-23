"""Complete same-epoch MP D_A chi maps with actual inherited total clocks.

The supplied accepted background selects an external numerical chart.
Phase test/right variations hold it; time/parameter contacts are explicit.
This is not a nonlinear reselected K(A) chart and assigns no new momentum.
"""
from pathlib import Path
import argparse
import numpy as np


def complete_product_lifts(point, total_clock, wall, wall_clock,
                           profiles, wall_profiles, *, wall_radial=None):
    from flint import acb, acb_mat
    if point.ncols() != 60 or total_clock.nrows() != point.nrows() or total_clock.ncols() != 60:
        raise ValueError('same-owner full60 point and complete source/reference/child clock required')
    if wall.nrows() != 1 or wall.ncols() != 20 or wall_clock.nrows() != 1 or wall_clock.ncols() != 20:
        raise ValueError('same-epoch full20 wall and complete wall clock required')
    chi, cr, crr = [profiles[k] for k in ('values', 'first', 'second')]
    cw, cwr, cwrr = [wall_profiles[k] for k in ('values', 'first', 'second')]
    if chi.nrows() != point.nrows():
        raise ValueError('literal radial profiles on the actual point grid required')
    factor = 1 / acb(2).sqrt()
    labels = [(p, c) for p in range(chi.ncols()) for c in range(3)]
    N = len(labels)
    def comm(v, c, z):
        result = [acb(0) for _ in range(4)]
        for i, j, k in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            if c == k:
                result[i] += v[j] * z * factor
            if c == j:
                result[i] -= v[k] * z * factor
        return result
    T, Tt = [], []
    for r in range(point.nrows()):
        value, clock = acb_mat(60, 2*N), acb_mat(60, 2*N)
        for j, (p, c) in enumerate(labels):
            for f in range(1, 5):
                K = comm([point[r, 4*f+i] for i in range(4)], c, chi[r, p])
                Kr = comm([point[r, 40+4*f+i] for i in range(4)], c, chi[r, p])
                extra_r = comm([point[r, 4*f+i] for i in range(4)], c, cr[r, p])
                Kt = comm([total_clock[r, 4*f+i] for i in range(4)], c, chi[r, p])
                Ktt = comm([total_clock[r, 20+4*f+i] for i in range(4)], c, chi[r, p])
                Krt = comm([total_clock[r, 40+4*f+i] for i in range(4)], c, chi[r, p])
                extra_rt = comm([total_clock[r, 4*f+i] for i in range(4)], c, cr[r, p])
                if f == 1:
                    K[c] += cr[r, p]
                    Kr[c] += crr[r, p]
                for i in range(4):
                    value[4*f+i, j] = K[i]
                    value[20+4*f+i, j] = Kt[i]
                    value[40+4*f+i, j] = Kr[i] + extra_r[i]
                    value[20+4*f+i, N+j] = K[i]
                    clock[4*f+i, j] = Kt[i]
                    clock[20+4*f+i, j] = Ktt[i]
                    clock[40+4*f+i, j] = Krt[i] + extra_rt[i]
                    clock[20+4*f+i, N+j] = Kt[i]
        T.append(value)
        Tt.append(clock)
    W, Wt, Wr = acb_mat(20, 2*N), acb_mat(20, 2*N), None
    if wall_radial is not None:
        if wall_radial.nrows() != 1 or wall_radial.ncols() != 20:
            raise ValueError('same actual full20 wall radial connection required')
        Wr = acb_mat(20, 2*N)
    for j, (p, c) in enumerate(labels):
        for f in range(1, 5):
            K = comm([wall[0, 4*f+i] for i in range(4)], c, cw[0, p])
            Kt = comm([wall_clock[0, 4*f+i] for i in range(4)], c, cw[0, p])
            if f == 1:
                K[c] += cwr[0, p]
            if Wr is not None:
                Kr = comm([wall_radial[0, 4*f+i] for i in range(4)], c, cw[0, p])
                more = comm([wall[0, 4*f+i] for i in range(4)], c, cwr[0, p])
                if f == 1:
                    Kr[c] += cwrr[0, p]
            for i in range(4):
                W[4*f+i, j], Wt[4*f+i, j] = K[i], Kt[i]
                if Wr is not None:
                    Wr[4*f+i, j] = Kr[i] + more[i]
    return dict(point_lift=T, point_lift_total_clock=Tt, wall_lift=W,
                wall_lift_total_clock=Wt, wall_lift_radial=Wr,
                generator_profile_internal_labels=np.asarray(labels, int))


def run(repository, clock_packet, current_operator, output, *, degree=2, wall_radial_packet=None):
    from bhsm_baton_zoo_radial_convergence import environment
    root, out, read, save, finish = environment(repository, output)
    from bhsm.interface.muon_stored_admission_correction import _matrix, _upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm_baton_zoo_literal_radial_profile_precision import literal_profiles
    from evaluate_muon_continued_current_factor import retained_input
    clock, actual = read(Path(clock_packet)), read(Path(current_operator))
    if clock['coordinate_time'].item() != actual['coordinate_time'].item():
        raise ValueError('same actual cut clock and current scalar operator required; no nearby midpoint substitution')
    if not np.array_equal(clock['master368'], actual['master368']):
        raise ValueError('same accepted nonzero compatible368 state required')
    if 'reference_affine_clock_once' not in clock:
        raise ValueError('both actual affine references must be explicit in the total-clock owner')
    phase, _ = retained_input('outgoing', {})
    rep = phase['representation']
    base = root / 'artifacts/muon_baton_zoo_radial_convergence_20261014'
    template = read(base / f'covariant_degree{degree}_normalized_MP_birth_run_{2 if degree == 2 else 1}/actual_product_domain_lifts_and_normalization.npz')
    lt = read(base / f'literal_MP_point_wall_tables_run_1/degree_{degree:02d}_literal_MP_original_and_extra_point_wall_tables.npz')
    exact = lambda z, k: _matrix(z[k + '_high']) + _matrix(z[k + '_low'])
    profiles, wp = literal_profiles(rep, rep['rho'], degree), literal_profiles(rep, [np.pi/2], degree)
    radial = None
    if wall_radial_packet is not None:
        wall_data = read(Path(wall_radial_packet))
        if wall_data['coordinate_time'].item() != actual['coordinate_time'].item():
            raise ValueError('same actual wall radial epoch required')
        radial = exact(wall_data, 'wall_radial_connection')
    product = complete_product_lifts(exact(clock, 'child_point_coefficients'),
        exact(clock, 'child_point_coefficients_directional_first'),
        exact(clock, 'child_wall_connection'), exact(clock, 'child_wall_connection_directional_first'),
        profiles, wp, wall_radial=radial)
    N = len(product['generator_profile_internal_labels'])
    stack = lambda matrices: tuple(np.asarray([_split(m)[part] for m in matrices]) for part in (0, 1))
    th, tl = stack(product['point_lift'])
    tth, ttl = stack(product['point_lift_total_clock'])
    wh, wl = _split(product['wall_lift'])
    wth, wtl = _split(product['wall_lift_total_clock'])
    arrays = {k: v.copy() for k, v in template.items() if k not in
              ('extra_point_lift_high', 'extra_point_lift_low', 'extra_wall_lift_high', 'extra_wall_lift_low',
               'product_point_lift_time_first_high', 'product_point_lift_time_first_low')}
    for half, T, Tt, W, Wt in (('high', th, tth, wh, wth), ('low', tl, ttl, wl, wtl)):
        arrays['extra_point_lift_' + half] = np.concatenate((lt['compatible_extra_point_lift_' + half], T), axis=2)
        arrays['extra_point_lift_total_clock_' + half] = np.concatenate((np.zeros_like(lt['compatible_extra_point_lift_' + half]), Tt), axis=2)
        arrays['extra_wall_lift_' + half] = np.concatenate((lt['compatible_extra_wall_lift_' + half].reshape(20, -1), W), axis=1).reshape(5, 4, -1)
        arrays['extra_wall_lift_total_clock_' + half] = np.concatenate((np.zeros_like(lt['compatible_extra_wall_lift_' + half].reshape(20, -1)), Wt), axis=1).reshape(5, 4, -1)
    arrays.update(coordinate_time=actual['coordinate_time'], generator_profile_internal_labels=product['generator_profile_internal_labels'],
        actual_nonzero_current_master368=actual['master368'], original252_to_current368=actual['original252_to_augmented368'],
        actual_current368_extra116_to_full=actual['extra116_to_full'],
        complete_source_and_both_reference_clock_retained_once=np.asarray(True),
        numerical_chart_ownership=np.asarray('External same accepted background selects K(t); J/R held, actual total-clock and family h contacts explicit once. No nonlinear reselected K(A) chart.'),
        normalization_ownership=np.asarray('Saved invertible physical-coordinate normalization held as computational preconditioner; no mode/row dropped.'))
    if product['wall_lift_radial'] is not None:
        rh, rl = _split(product['wall_lift_radial'])
        arrays['product_wall_radial_lift_high'], arrays['product_wall_radial_lift_low'] = rh.reshape(5, 4, 2*N), rl.reshape(5, 4, 2*N)
    save(f'actual_degree_{degree:02d}_complete_clock_covariant_product_epoch_maps.npz', arrays)
    finish(dict(classification='ACTUAL_CURRENT_COMPLETE_TOTAL_CLOCK_COVARIANT_PRODUCT_EPOCH_MAPS', degree=degree,
        actual_time=[actual['coordinate_time'].item().real, actual['coordinate_time'].item().imag],
        product_position_count=N, full_action_dimension=int(arrays['full_dimension']),
        point_time_contact_upper=max(_upper(x) for x in product['point_lift_total_clock']),
        wall_time_contact_upper=_upper(product['wall_lift_total_clock']),
        actual_nonzero_primal_fields_preserved=True,
        both_affine_reference_clocks_held_in_old_birth_map=False,
        wall_radial_reset_trace_supplied=radial is not None,
        new_Cauchy_momenta_or_source_domain_or_field_convergence_or_outgoing_load_assigned=False,
        failed_old316_seed_consumed=False), producer_paths=(Path(__file__),))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'clock-packet', 'current-operator', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--degree', type=int, choices=(2, 4, 6, 8), default=2)
    p.add_argument('--wall-radial-packet', type=Path)
    a = p.parse_args()
    run(a.repository, a.clock_packet, a.current_operator, a.output, degree=a.degree, wall_radial_packet=a.wall_radial_packet)
