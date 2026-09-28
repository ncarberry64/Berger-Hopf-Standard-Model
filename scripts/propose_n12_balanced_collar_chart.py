"""Choose a coupled curve corridor from the frozen signed rate first jet.

The point resolvent only proposes a domain. New uniform normal and flow
inequalities must validate that domain before it is a trajectory enclosure.
"""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, BASE, packet, restore, digest, encoded, save_arrays, scalar,
    arb, arb_mat, ctx, Path, argparse, json,
)
from bind_n12_collar_curve_normal_response import box_image_bound


def calculate(out, exponent):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    paths = dict(endpoint=BASE/'flow55_endpoint1', lift=BASE/'flow55_curve_normal1', jet=JET)
    records, packs = {}, {}
    for key, path in paths.items():
        records[key], packs[key] = packet(path)
        for source, expected in records[key]['source_SHA256'].items():
            if digest(ROOT/source) != expected:
                raise ValueError('current source changed: '+source)
    endpoint, lift, jet = [packs[k] for k in ('endpoint', 'lift', 'jet')]
    affine = restore(endpoint, 'endpoint_affine')
    oldT = restore(endpoint, 'step')[0, 0]
    oldrho = restore(lift, 'curve_action_radii').entries()
    J = arb_mat(98, 98, [affine[i, j]/oldT/oldrho[j] for i in range(98) for j in range(98)])
    A = arb_mat(98, 98, [abs(v).upper() for v in J.entries()])
    h = arb(2)**(-exponent)
    curvature = restore(jet, 'fixed_s_curve_second')
    forcing = arb_mat(98, 1, [h*h*(abs(curvature[i, 0]).upper()/2+1) for i in range(98)])
    I = arb_mat([[arb(i == j) for j in range(98)] for i in range(98)])
    solution = (I-4*h*A).solve(4*forcing)
    rho = [v.upper() for v in solution.entries()]
    if not all(v>0 for v in rho):
        raise ArithmeticError('point majorant does not give a positive curve proposal')
    ratio = [(forcing[i, 0]+h*sum((A[i, j]*rho[j] for j in range(98)), arb(0)))/rho[i] for i in range(98)]
    oldnormal = restore(lift, 'old_normal_radii').entries()
    T = restore(lift, 'curve_normal_response_scaled')
    response = arb_mat(124, 98,
        [oldnormal[i]*T[i, j]*rho[j]/oldrho[j] for i in range(124) for j in range(98)])
    blocks = {}
    for name, start, stop in (('psi', 0, 61), ('lambda', 61, 62), ('hard', 62, 123), ('b', 123, 124)):
        block = arb_mat(stop-start, 98, [response[i, j] for i in range(start, stop) for j in range(98)])
        blocks[name] = scalar(box_image_bound(block))
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', dict(step=arb_mat([[h]]), point_rate_jacobian=J,
        point_absolute_majorant=A, point_curvature_forcing=forcing,
        curve_action_radii=arb_mat(98, 1, rho), curve_normal_response=response,
        point_majorant_ratios=arb_mat(98, 1, ratio)))
    report = dict(status='COUPLED_CURVE_CORRIDOR_PROPOSED_FROM_FROZEN_RATE_JET', exponent=exponent,
        step=scalar(h), maximum_point_majorant_ratio=scalar(max(v.upper() for v in ratio)),
        induced_normal_curve_variation=blocks,
        new_scientific_action_evaluations=0, uniform_domain_certified=False,
        actual_flow_tube_included=False, prefix_overlap_certified=False,
        physical_direction_columns_generated=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    files = [Path(__file__), ROOT/'scripts/bind_n12_collar_curve_normal_response.py']
    for path in paths.values():
        files.extend([path/'arrays.npz', path/'report.json'])
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps(dict(exponent=exponent, point_ratio=float(max(ratio)), normal_blocks={k:v['midpoint'] for k,v in blocks.items()})), flush=True)
    for p in packs.values():
        p.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--exponent', type=int, default=45)
    args = parser.parse_args()
    calculate(args.out, args.exponent)
