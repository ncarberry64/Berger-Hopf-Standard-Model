"""Compute the complete four-block anchor adjoint for a physical output row.

Only contracted third/fourth action data absent from the saved inverse are
evaluated. This is an anchor adjoint with an explicit defect, not a uniform
physical error certificate.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface import coupled_action_output_adjoint as adjoint
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(root, family):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    from bhsm.interface import prescribed_arb_action_jet as prescribed
    from bhsm.interface import sparse_arb_mixed_jets as sparse
    from bhsm.interface import ball_factored_arb_integrand as factored
    from bhsm.interface import factored_arb_integrand as algebra
    p, cert = base.p, base.p.values.cert
    pair = ('bhsm_midpoint_center_mean_value_right_pair_20260913' if family == 'midpoint'
            else 'bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913')
    eigen_name = ('.coupled_midpoint_eigenpair_pilot_work/interval_013' if family == 'midpoint'
                  else '.affine_eigenpair_pilot_work/endpoint_014')
    data = root/'tmp'/pair/'value/first/column.npz'
    eigenfile = root/'artifacts/flagship_integration'/eigen_name/'eigenpair.npz'
    with np.load(data, allow_pickle=False) as z, np.load(eigenfile, allow_pickle=False) as e:
        read = lambda name: saved.read_matrix(z, name, center=True)
        state = saved.read_matrix(e, 'center_state', center=True)
        ep = saved.read_matrix(e, 'eigenpair_center', center=True)
        R = saved.read_matrix(e, 'preconditioner', center=True)
        defect = saved.read_matrix(e, 'center_defect')
        domain = saved.read_matrix(z, 'raw_domain')
        axis = read('weighted_input_axis')
        centers = ep.entries()+sum([read(f'point_center_{i}').entries() for i in range(3)], [])
        boxes = saved.read_matrix(e, 'eigenpair_box').entries()
        boxes += sum([saved.read_matrix(z, f'uniform_solve_{i}').entries() for i in range(3)], [])
        saved_rate = saved.read_matrix(z, 'point_derivative')
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights, qw, rw = [[arb(float(x)) for x in v] for v in (weights, qw, rw)]
    raw_axis = np.array([axis[i, 0]/weights[i] for i in range(98)], dtype=object)
    x = np.array(state.entries(), dtype=object)
    # Recover the saved action Hessian from D=I-R*J, without reevaluating it.
    K = R.solve(arb_mat(np.eye(62, dtype=int).tolist())-defect)
    H = arb_mat(61, 61, [K[i, j]+(ep[61, 0] if i == j else 0) for i in range(61) for j in range(61)])
    maps = [cert._dense_mapping(cert._integrand(x, node, 0).maps) for node in range(cert.POINTS)]
    basis = np.array([[arb(i == 37+j) for j in range(61)] for i in range(98)], dtype=object)
    cache, calls = {}, []
    def contraction(*legs):
        keys = []
        for leg in legs:
            arr = np.asarray(leg, dtype=object)
            keys.append(hashlib.sha256(saved.encoded(dict(shape=arr.shape,
                values=[[str(v.mid().fmpq()), str(v.rad().fmpq())] for v in arr.flat]))).hexdigest())
        key = tuple(keys)
        if key not in cache:
            with sparse.use_optimized_mixed(cert), factored.use_ball_factored_integrand(cert, x):
                cache[key] = prescribed.affine_action_contraction(cert, x, maps, *legs)
            calls.append(dict(order=len(legs), shape=list(cache[key].shape)))
            print(json.dumps(dict(completed_anchor_contraction=len(calls), **calls[-1])), flush=True)
        return cache[key]
    Hu = base.matrix(contraction(basis, basis, raw_axis).reshape(61, 61))
    residual = p.geometry.residual
    with base.cache.cache_hashes([(p.values, 'sha'), (residual.center, '_sha'),
                                 (residual.foundation.coordinate.center, '_sha')]):
        local = base.reader.load_inputs(13)
    P = base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axisfile = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axisfile, allow_pickle=False) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:, None]
    axes[0] = 0
    if hashlib.sha256(np.asarray(axes, dtype='<f8').tobytes()).hexdigest().upper() != local['binding']['axes_SHA256']:
        raise ValueError('same frozen physical output required')
    a = [arb(float(v)) for v in axes[14]]
    zrow = arb_mat(1, 74, [arb(i == 73)-a[73]*a[i] for i in range(74)])*P*(2*arb(float(local['step']))/3)
    configuration = [qw[i]*x[37+i] for i in range(37)]
    configuration_u = [qw[i]*raw_axis[37+i] for i in range(37)]
    constant = lambda v: adjoint.FirstJet(arb(v), arb_mat(1, 248))
    def action_jet(*legs):
        values = [np.array([v.c for v in leg], dtype=object) for leg in legs]
        value = contraction(*values).reshape(-1)[0]
        derivative = arb_mat(1, 248)
        for i, leg in enumerate(legs):
            if any(not v.a[0, j].is_zero() for v in leg[:37] for j in range(248)):
                raise ValueError('fixed input configuration required for the U adjoint')
            variation = arb_mat(61, 248, [v for entry in leg[37:] for v in entry.a.entries()])
            if all(v.is_zero() for v in variation.entries()):
                continue
            other = values[:i]+values[i+1:]
            # Put the single free reduced leg first; fixed legs commute by
            # symmetry of this smooth retained-action derivative.
            other.sort(key=lambda arr: hashlib.sha256(saved.encoded(
                [[str(v.mid().fmpq()), str(v.rad().fmpq())] for v in arr])).hexdigest())
            free = contraction(basis, *other).reshape(61)
            derivative += arb_mat(1, 61, list(free))*variation
        return adjoint.FirstJet(value, derivative)
    def descriptors(pj, hj, puj, huj):
        pad = lambda v: [constant(0)]*37+v
        scale = lambda v: [rw[i]/weights[37+i]*v[i] for i in range(61)]
        pp, pu = pad(pj), pad(puj)
        aa, au = pad(scale(pj)), pad(scale(puj))
        dd = [constant(configuration[i]/weights[i]) for i in range(37)]+scale(hj)
        du = [constant(configuration_u[i]/weights[i]) for i in range(37)]+scale(huj)
        uu = [constant(v) for v in raw_axis]
        # These are the THIRD/Fourth descriptor contractions in _batch_scalar,
        # including both occurrences of the selected eigenvector.
        c = action_jet(pp, pp, aa)
        rem = action_jet(pp, pp, dd)
        cu = action_jet(pp, pp, aa, uu)+2*action_jet(pp, pu, aa)+action_jet(pp, pp, au)
        ru = action_jet(pp, pp, dd, uu)+2*action_jet(pp, pu, dd)+action_jet(pp, pp, du)
        return c, rem, cu, ru
    J, gradient, value = adjoint.linearize(H, Hu, configuration, configuration_u, rw,
        domain[98, 0].mid(), axis[98, 0], zrow.entries(), centers, descriptors)
    beta, error = adjoint.adjoint_proposal(J, gradient)
    widths = [abs(box-center).upper() for box, center in zip(boxes, centers, strict=True)]
    weighted_defect = sum((abs(error[0, i]).upper()*widths[i] for i in range(248)), arb(0)).upper()
    result = dict(algorithm='COMPLETE_COUPLED_ANCHOR_OUTPUT_ADJOINT_ARB512_V1', family=family,
        unknowns=248, residual_block_order=['eigenline','response','axis_line','axis_response'],
        output='row73 of (2*dt/3)*Q*P*DF(anchor)*saved_axis',
        exact_covectors={name:[str(beta[0, 62*k+j].fmpq()) for j in range(62)]
            for k, name in enumerate(['eigenline','response','axis_line','axis_response'])},
        maximum_anchor_adjoint_defect_exact=str(max(abs(v).upper() for v in error.entries()).fmpq()),
        weighted_anchor_defect_exact=str(weighted_defect.fmpq()),
        weighted_anchor_defect_approximate=float(weighted_defect),
        anchor_output=dict(mid=str(value.mid().fmpq()), rad=str(value.rad().fmpq())),
        saved_point_output=dict(mid=str((zrow*saved_rate)[0,0].mid().fmpq()), rad=str((zrow*saved_rate)[0,0].rad().fmpq())),
        action_contractions=calls, original_action_Hessian_reused=True,
        third_and_fourth_descriptor_derivatives_included=True,
        full_anchor_output_gradient_included=True, uniform_adjoint_defect_enclosed=False,
        correction_box_used_only_for_anchor_defect_scaling=True,
        complete_projected_physical_error=None, physical_global_margin=None,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_hashes={**verified['paired_source_hashes'],
            **{Path(m.__file__).name:saved.sha(Path(m.__file__)) for m in (cert, prescribed, sparse, factored, algebra, adjoint)},
            'evaluator':saved.sha(Path(__file__))})
    p.verify_sources(json.loads((data.parent/'record.json').read_bytes())['binding'])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--family', choices=['midpoint','endpoint'], default='midpoint')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    if args.out.exists():
        raise FileExistsError('use a new output path')
    result = evaluate(args.evidence_root.resolve(), args.family)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as target:
        target.write(saved.encoded(result))
    print(json.dumps(dict(family=args.family, weighted_anchor_defect=result['weighted_anchor_defect_approximate'],
                         uniform_adjoint_defect_enclosed=False)), flush=True)


if __name__ == '__main__':
    main()
