"""Compute the input-independent output adjoint on its actual endpoint.

Only three contracted third derivatives are needed for the last two implicit
blocks. This is a point proposal, not a uniform nonlinear certificate.
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
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import evaluate_n12_gate7_coupled_residual_saved as saved


def dot(a, b):
    return sum((x*y for x,y in zip(a,b,strict=True)), arb(0))


def evaluate(root, side):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    if side == 'left':
        import n12_gate7_left_saved_family as verifier
    else:
        verifier = saved
    verified = verifier.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    from bhsm.interface import prescribed_arb_action_jet as prescribed
    from bhsm.interface import sparse_arb_mixed_jets as sparse
    from bhsm.interface import ball_factored_arb_integrand as factored
    p, cert = base.p, base.p.values.cert
    index = 13 if side == 'left' else 14
    pair = root/f'tmp/bhsm_endpoint_trial_mean_value_bootstrap_{side}_pair_20260913/value/first/column.npz'
    eigen = root/f'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_{index:03d}/eigenpair.npz'
    with np.load(pair, allow_pickle=False) as z, np.load(eigen, allow_pickle=False) as e:
        state = saved.read_matrix(e, 'center_state', center=True)
        ep = saved.read_matrix(e, 'eigenpair_center', center=True)
        R = saved.read_matrix(e, 'preconditioner', center=True)
        defect = saved.read_matrix(e, 'center_defect')
        hard = saved.read_matrix(z, 'point_center_0', center=True).entries()
        s = saved.read_matrix(z, 'raw_domain')[98,0].mid()
    psi, border = ep.entries()[:61], hard[61]
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights, qw, rw = [[arb(float(v)) for v in vv] for vv in (weights, qw, rw)]
    scale = [rw[i]/weights[37+i] for i in range(61)]
    configuration = [qw[i]*state[37+i,0] for i in range(37)]
    pp = np.array([arb(0)]*37+psi, dtype=object)
    aa = np.array([arb(0)]*37+[scale[i]*psi[i] for i in range(61)], dtype=object)
    dd = np.array([configuration[i]/weights[i] for i in range(37)]
                  +[scale[i]*hard[i] for i in range(61)], dtype=object)
    x = np.array(state.entries(), dtype=object)
    basis = np.array([[arb(int(i == 37+j)) for j in range(61)] for i in range(98)], dtype=object)
    maps = [cert._dense_mapping(cert._integrand(x, node, 0).maps) for node in range(cert.POINTS)]
    vectors = []
    for name, a, b in [('eigenline_pair', pp, pp), ('scaled_line', pp, aa), ('response', pp, dd)]:
        with sparse.use_optimized_mixed(cert), factored.use_ball_factored_integrand(cert, x):
            value = prescribed.affine_action_contraction(cert, x, maps, basis, a, b)
        vectors.append(list(value.reshape(61)))
        print(json.dumps(dict(contracted_third_derivative=name)), flush=True)
    g, q, t = vectors
    c, remainder = dot(psi, q), dot(psi, t)
    N = [s*v for v in configuration]+[rw[i]*(border*psi[i]+s*hard[i]) for i in range(61)]
    delta = border*c+s*remainder
    norm = dot(N,N).sqrt()
    residual = p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'), (residual.center,'_sha'),
                                 (residual.foundation.coordinate.center,'_sha')]):
        local = base.reader.load_inputs(13)
    P = base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axisfile = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axisfile, allow_pickle=False) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:,None]
    axes[0] = 0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper() != local['binding']['axes_SHA256']:
        raise ValueError('unchanged physical output axis required')
    axis = [arb(float(v)) for v in axes[14]]
    zrow = (arb_mat(1,74,[arb(int(i == 73))-axis[73]*axis[i] for i in range(74)])
            *P*(2*arb(float(local['step']))/3)).entries()
    alpha = (dot(zrow[:98],N)+zrow[98]*delta)/(norm**3)
    v = [zrow[i]/norm-alpha*N[i] for i in range(98)]
    gamma = zrow[98]/norm
    line_gradient = [rw[i]*border*v[37+i]+gamma*(border*(2*q[i]+scale[i]*g[i])+2*s*t[i])
                     for i in range(61)]+[arb(0)]
    response_gradient = [rw[i]*s*v[37+i]+gamma*s*scale[i]*g[i] for i in range(61)]
    response_gradient.append(dot(v[37:], [rw[i]*psi[i] for i in range(61)])+gamma*c)
    K = R.solve(arb_mat(62,62,[int(i == j) for i in range(62) for j in range(62)])-defect)
    for i in range(61):
        K[i,61] = ep[i,0]
    v3 = K.transpose().solve(arb_mat(62,1,response_gradient)).mid()
    reduced = [line_gradient[i]-border*v3[i,0]-hard[i]*v3[61,0] for i in range(61)]+[line_gradient[61]]
    v2 = K.transpose().solve(arb_mat(62,1,reduced)).mid()
    defects = ((arb_mat(62,1,response_gradient)-K.transpose()*v3).entries()
               +(arb_mat(62,1,reduced)-K.transpose()*v2).entries())
    return dict(algorithm='THREE_D3_DIRECTIONAL_OUTPUT_ADJOINT_POINT_PROPOSAL_V1',
        family='endpoint', side=side, unknowns=248,
        exact_covectors=dict(eigenline=['0']*62,response=['0']*62,
            axis_line=[str(v.fmpq()) for v in v2.entries()],
            axis_response=[str(v.fmpq()) for v in v3.entries()]),
        only_directional_blocks_optimized=True, base_covectors_are_zero_placeholders=True,
        maximum_directional_adjoint_defect=float(max(abs(v).upper() for v in defects)),
        physical_input_map_required=False, uniform_error_certified=False,
        source_hashes={**verified['paired_source_hashes'],
            **{Path(m.__file__).name:saved.sha(Path(m.__file__)) for m in (cert,prescribed,sparse,factored)},
            'evaluator':saved.sha(Path(__file__)), 'source_verifier':saved.sha(Path(verifier.__file__))},
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--side', choices=('left','right'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    result = evaluate(args.evidence_root.resolve(), args.side)
    with args.out.open('xb') as f:
        f.write(saved.encoded(result))
    print(json.dumps(dict(side=args.side, defect=result['maximum_directional_adjoint_defect'])), flush=True)


if __name__ == '__main__':
    main()
