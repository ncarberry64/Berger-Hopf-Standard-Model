"""Propose all left input covectors with the retained positive HS chain sign.

The last two adjoint blocks are input-independent. Only the first two blocks
need a matrix of covectors. This computes anchor derivatives, not a uniform
certificate. Sources held fixed under U differentiation are omitted only here.
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
from bhsm.interface.input_linear_anchor_jet import ScalarJet, InputLinearJet
from bhsm.interface.local_input_anchor_action import input_linear_anchor_action
import bhsm.interface.local_input_anchor_action as local_action
import bhsm.interface.input_linear_anchor_jet as implementation
import n12_gate7_left_saved_family as saved


def dot(a, b):
    return sum((x*y for x, y in zip(a, b, strict=True)), arb(0))


def evaluate(root, family, adjoint_path, out):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p, cert = base.p, base.p.values.cert
    middle = family == 'midpoint'
    pair = ('bhsm_midpoint_center_mean_value_left_pair_20260913' if middle
            else 'bhsm_endpoint_trial_mean_value_bootstrap_left_pair_20260913')
    eigen_name = ('.coupled_midpoint_eigenpair_pilot_work/interval_013' if middle
                  else '.affine_eigenpair_pilot_work/endpoint_013')
    data = root/'tmp'/pair/'value/first/column.npz'
    eigenfile = root/'artifacts/flagship_integration'/eigen_name/'eigenpair.npz'
    with np.load(data, allow_pickle=False) as z, np.load(eigenfile, allow_pickle=False) as e:
        state = saved.read_matrix(e, 'center_state', center=True)
        ep = saved.read_matrix(e, 'eigenpair_center', center=True)
        response = saved.read_matrix(z, 'point_center_0', center=True)
        R = saved.read_matrix(e, 'preconditioner', center=True)
        defect = saved.read_matrix(e, 'center_defect')
        raw = saved.read_matrix(z, 'raw_domain')
        old_axis = saved.read_matrix(z, 'weighted_input_axis', center=True)
    baseline = json.loads(adjoint_path.read_bytes())
    # These two covectors are freely chosen cancellation coefficients. A
    # retained right-family anchor is a proposal only; no right-family error
    # bound or input map is transferred to the left family.
    if baseline.get('unknowns') != 248:
        raise ValueError('complete retained adjoint proposal required')
    for key in ('axis_line', 'axis_response'):
        values = [arb(v) for v in baseline['exact_covectors'][key]]
        if len(values) != 62 or any(not v.is_finite() or not v.rad().is_zero() for v in values):
            raise ValueError('exact finite 62-component cancellation proposal required')
    residual = p.geometry.residual
    with base.cache.cache_hashes([(p.values, 'sha'), (residual.center, '_sha'),
                                 (residual.foundation.coordinate.center, '_sha')]):
        local = base.reader.load_inputs(13)
    paths = {}
    full = {}
    for stage, name in (('endpoint', 'endpoint_013'), ('midpoint', 'interval_013')):
        path = root/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{stage}_uniform_df_work/{name}/derivative.npz'
        relative = path.relative_to(root).as_posix()
        if local['binding']['files'].get(relative) != saved.sha(path):
            raise ValueError('complete full-input derivative source outside verified binding')
        paths[relative] = saved.sha(path)
        with np.load(path, allow_pickle=False) as z:
            full[stage] = {key:saved.read_matrix(z, key) for key in
                          ('point_derivative','point_line_center','point_response_center')}
    E = base.matrix(local['trial_left'])
    h = arb(float(local['step']))
    U = E if not middle else E/2+full['endpoint']['point_derivative']*E*(h/8)
    # A fixed direction map may be chosen freely. Keep it exact, and retain
    # the earlier fixed column as a consistency check and future transport anchor.
    U = arb_mat(U.nrows(), U.ncols(), [v.mid() for v in U.entries()])
    for i in range(99):
        U[i, 14] = old_axis[i, 0]
    pu_matrix = full[family]['point_line_center']*U
    hu_matrix = full[family]['point_response_center']*U
    pu_matrix = arb_mat(62, 74, [v.mid() for v in pu_matrix.entries()])
    hu_matrix = arb_mat(62, 74, [v.mid() for v in hu_matrix.entries()])
    centers = ep.entries()+response.entries()
    dim, inputs = 124, 74
    variables = [ScalarJet(c, arb_mat(1, dim, [arb(i == j) for j in range(dim)]))
                 for i, c in enumerate(centers)]
    psi, lam, hard, border = variables[:61], variables[61], variables[62:123], variables[123]
    constant = lambda c: ScalarJet(arb(c), arb_mat(1, dim))
    linear = lambda values: InputLinearJet(arb_mat(1, inputs, values), arb_mat(dim, inputs))
    psi_u = [linear([pu_matrix[i, j] for j in range(inputs)]) for i in range(62)]
    hard_u = [linear([hu_matrix[i, j] for j in range(inputs)]) for i in range(62)]
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights, qw, rw = [[arb(float(v)) for v in vv] for vv in (weights, qw, rw)]
    x = [constant(v) for v in state.entries()]
    u = [linear([U[i, j]/weights[i] for j in range(inputs)]) for i in range(98)]
    su = linear([U[98, j] for j in range(inputs)])
    s = raw[98, 0].mid()
    pad = lambda v: [constant(0)]*37+list(v[:61])
    scale = lambda v: [rw[i]/weights[37+i]*v[i] for i in range(61)]
    configuration = [qw[i]*x[37+i] for i in range(37)]
    configuration_u = [qw[i]*u[37+i] for i in range(37)]
    maps = [cert._dense_mapping(cert._integrand(state.entries(), node, 0).maps) for node in range(cert.POINTS)]
    terms = {}
    def action(name, legs):
        with input_linear_anchor_action(cert):
            value = cert._contracted_action(np.array(x, dtype=object),
                        [np.array(v, dtype=object) for v in legs], maps)
        terms[name] = type(value).__name__
        print(json.dumps(dict(anchor_term=name, kind=terms[name])), flush=True)
        return value
    v2, v3 = [[arb(v) for v in baseline['exact_covectors'][key]] for key in ('axis_line','axis_response')]
    K = R.solve(arb_mat(np.eye(62, dtype=int).tolist())-defect)
    H = arb_mat(61, 61, [K[i, j]+(ep[61, 0] if i == j else 0)
                         for i in range(61) for j in range(61)])
    def matvec(matrix, values):
        return [dot([matrix[i, j] for j in range(matrix.ncols())], values) for i in range(matrix.nrows())]
    Hp, Hh = matvec(H, psi), matvec(H, hard)
    base_rows = [Hp[i]-lam*psi[i] for i in range(61)]+[(dot(psi, psi)-1)/2]
    base_rows += [Hh[i]-lam*hard[i]+border*psi[i] for i in range(61)]+[dot(psi, hard)]
    J = arb_mat(dim, dim, [v for row in base_rows for v in row.a.entries()])
    pp, pu = pad(psi), pad(psi_u)
    aa, au = pad(scale(psi)), pad(scale(psi_u))
    dd = [configuration[i]/weights[i] for i in range(37)]+scale(hard)
    du = [configuration_u[i]/weights[i] for i in range(37)]+scale(hard_u)
    cpsi = action('descriptor_c', [pp, pp, aa])
    rem = action('descriptor_r', [pp, pp, dd])
    cu = (action('descriptor_cu4', [pp, pp, aa, u])
          +2*action('descriptor_cu3a', [pp, pu, aa])+action('descriptor_cu3b', [pp, pp, au]))
    ru = (action('descriptor_ru4', [pp, pp, dd, u])
          +2*action('descriptor_ru3a', [pp, pu, dd])+action('descriptor_ru3b', [pp, pp, du]))
    N = [s*v for v in configuration]+[rw[i]*(border*psi[i]+s*hard[i]) for i in range(61)]
    Nu = [su*a+s*b for a, b in zip(configuration, configuration_u)]
    Nu += [rw[i]*(hard_u[61]*psi[i]+border*psi_u[i]+su*hard[i]+s*hard_u[i]) for i in range(61)]
    delta = border*cpsi+s*rem
    delta_u = hard_u[61]*cpsi+border*cu+su*rem+s*ru
    norm = (dot(N, N).log()/2).exp()
    P = base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axisfile = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axisfile, allow_pickle=False) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:, None]
    axes[0] = 0
    if hashlib.sha256(np.asarray(axes, dtype='<f8').tobytes()).hexdigest().upper() != local['binding']['axes_SHA256']:
        raise ValueError('frozen projection mismatch')
    a = [arb(float(v)) for v in axes[14]]
    zrow = arb_mat(1, 74, [arb(i == 73)-a[73]*a[i] for i in range(74)])*P*(2*h/3)
    output = dot(zrow.entries(), Nu+[delta_u])/norm-dot(zrow.entries(), N+[delta])*dot(N, Nu)/(norm**3)
    slope = action('slope', [pp, pp, u])
    # These residual contractions are differentiated in U_base only. Their
    # physical source constants have zero U_base derivative; the uniform
    # residual producer must include them in full.
    G2 = (dot(v2[:61], matvec(H, psi_u[:61]))-lam*dot(v2[:61], psi_u[:61])
          +psi_u[61]*dot(v2[:61], psi)+action('line_source', [pad(v2), pp, u])
          -slope*dot(v2[:61], psi)+v2[61]*dot(psi, psi_u[:61]))
    G3 = (dot(v3[:61], matvec(H, hard_u[:61]))-lam*dot(v3[:61], hard_u[:61])
          +hard_u[61]*dot(v3[:61], psi)+action('response_source', [pad(v3), pad(hard), u])
          -slope*dot(v3[:61], hard)+border*dot(v3[:61], psi_u[:61])
          +v3[61]*(dot(psi, hard_u[:61])+dot(psi_u[:61], hard)))
    reduced = output-G2-G3
    solved = J.transpose().solve(reduced.a).transpose()
    beta = arb_mat(inputs, dim, [v.mid() for v in solved.entries()])
    error = reduced.a.transpose()-beta*J
    result = dict(algorithm='LEFT_FULL_INPUT_ANCHOR_BASE_ADJOINT_V1', family=family, side='left',
        fixed_axis_covectors_are_free_proposals=True,
        input_dimension=inputs, base_unknowns=dim, exact_input_linearity=True,
        full_input_uniform_certificate=False, Gate7_closed=False,
        base_adjoint_rows=[[str(beta[i, j].fmpq()) for j in range(dim)] for i in range(inputs)],
        fixed_axis_covectors={k:baseline['exact_covectors'][k] for k in ('axis_line','axis_response')},
        input_map=[[str(U[i, j].fmpq()) for j in range(inputs)] for i in range(99)],
        point_line_map=[[str(pu_matrix[i, j].fmpq()) for j in range(inputs)] for i in range(62)],
        point_response_map=[[str(hu_matrix[i, j].fmpq()) for j in range(inputs)] for i in range(62)],
        maximum_base_adjoint_defect=str(max(abs(v).upper() for v in error.entries()).fmpq()),
        maximum_base_adjoint_defect_approximate=float(max(abs(v).upper() for v in error.entries())),
        seed_base_covector_difference_diagnostic=max(float(abs(beta[14, j]-arb(baseline['exact_covectors']['eigenline' if j<62 else 'response'][j%62])).upper()) for j in range(dim)),
        evaluated_terms=terms, source_hashes={**verified['paired_source_hashes'], **paths,
            'input_scalar_adjoint':saved.sha(adjoint_path),'implementation':saved.sha(Path(implementation.__file__)),
            'evaluator':saved.sha(Path(__file__)),
            'left_source_verifier':saved.sha(Path(saved.__file__)),
            'local_anchor_action':saved.sha(Path(local_action.__file__))})
    with out.open('xb') as f:
        f.write(saved.encoded(result))
    print(json.dumps({k:result[k] for k in ('maximum_base_adjoint_defect_approximate','seed_base_covector_difference_diagnostic')}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--family', choices=('midpoint','endpoint'), required=True)
    parser.add_argument('--adjoint', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    if args.out.exists():
        raise FileExistsError('fresh output required')
    evaluate(args.evidence_root.resolve(), args.family, args.adjoint.resolve(), args.out)


if __name__ == '__main__':
    main()
