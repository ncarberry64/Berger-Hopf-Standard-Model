"""Restrict the proved first-exit model in time without changing its domain."""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, packet, restore, digest, encoded, save_arrays,
    scalar, arb, arb_mat, ctx, np, Path, argparse, json,
)


def restricted_ratios(ratios, fraction):
    """The source bound is h(A+B/2), A,B>=0; at t=f*h it is
    h(f*A+f^2*B/2) <= f*h(A+B/2), for 0<f<=1.

    Unknown material parameters are in A and are not assumed constant in
    time. The state/normal domain is unchanged. This is not a domain-radius
    rescaling or a relaxed acceptance threshold.
    """
    f = arb(fraction)
    if not f.rad().is_zero() or not 0<f<=1:
        raise ValueError('exact fraction in (0,1] required')
    if any(not v.is_finite() or not v>=0 for v in ratios):
        raise ValueError('nonnegative finite source first-exit bounds required')
    return [(f*v).upper() for v in ratios]


def calculate(source, out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    sr, data = packet(source)
    if not sr['descriptor_positive'] or not sr['source_normal_graph_reused']:
        raise ValueError('source must prove the normal graph and positive descriptor')
    for path, expected in sr['source_SHA256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError('current source changed: '+path)
    lift_path = next((ROOT/p).parent for p in sr['source_SHA256']
                     if p.endswith('/arrays.npz') and '/flow55_curve_normal1/' in p)
    lr, lift = packet(lift_path)
    jr, jet = packet(JET)
    old_step = restore(lift, 'step')[0, 0]
    rho = restore(lift, 'curve_action_radii').entries()
    ratio = restore(data, 'flow_first_exit_ratios').entries()
    f = arb(15)/16
    reduced = restricted_ratios(ratio, f)
    if not all(v<1 for v in reduced):
        raise ArithmeticError('partial first-exit step still fails')
    step = f*old_step
    U = restore(jet, 'fixed_s_direction')
    s0 = restore(jet, 'current_descriptor')[0, 0]
    with np.load(CANDIDATE) as z:
        initial = [arb(float(v))*arb(float(w)) for v, w in zip(z['joint_state_raw'][:98], z['state_weights'])]
    endpoint = [initial[i]+step*U[i, 0]+arb(0, (rho[i]*reduced[i]).upper()) for i in range(98)]+[s0+step]
    target_path = ROOT/'artifacts/flagship_integration/gate7_current_history_20260927/flow_box'
    target_record, target = packet(target_path)
    domain = restore(target, 'domain')
    failures = [i for i in range(99) if not domain[i, 0].contains(endpoint[i])]
    arrays = dict(step=arb_mat([[step]]), old_step=arb_mat([[old_step]]),
        fraction=arb_mat([[f]]), initial_action=arb_mat(99, 1, initial+[s0]),
        endpoint_action=arb_mat(99, 1, endpoint),
        first_exit_ratios=arb_mat(98, 1, reduced), curve_action_radii=arb_mat(98, 1, rho))
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    report = dict(status='FIRST_CURRENT_RESET_COLLAR_FLOW_SEGMENT_CERTIFIED',
        actual_flow_tube_included=True, step=scalar(step), fraction=scalar(f),
        maximum_first_exit_ratio=scalar(max(reduced)),
        normal_graph_and_positive_descriptor_reused=True,
        endpoint_target_domain_failures=failures, endpoint_in_target_domain=not failures,
        first_variation_transported=False, prefix_overlap_certified=False,
        positive_operator_history_certified=False,
        negative_initial_selected_descriptor_preserved=True,
        scope='Same-action fixed-s state flow on the first local segment only',
        prefix_cells_rebuilt=0, tolerances_changed=False, physical_radii_changed=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    files = [Path(__file__), source/'arrays.npz', source/'report.json',
        lift_path/'arrays.npz', lift_path/'report.json', JET/'arrays.npz', JET/'report.json',
        CANDIDATE, target_path/'arrays.npz', target_path/'report.json']
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    print(report['status'], 'step=', float(step), 'first_exit=', float(max(reduced)),
          'prefix_overlap=', not failures, flush=True)
    data.close(); lift.close(); jet.close(); target.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=BASE/'flow55_composed1')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    calculate(args.source, args.out)
