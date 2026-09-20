"""Evaluate a signed action residual on the saved common-parameter predictor.

This bounded probe supplies an actual action-owned Taylor enclosure. It does
not infer a physical output error from one residual or an approximate adjoint.
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
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain, scalar_taylor_action
import bhsm.interface.shared_action_taylor as implementation
import evaluate_n12_gate7_coupled_residual_saved as saved_reader


def dot(a, b):
    return sum((x*y for x, y in zip(a, b, strict=True)), arb(0))


def summary(value):
    def bound(v):
        return dict(exact=str(v.upper().fmpq()), approximate=float(v.upper()))
    return dict(constant_absolute=bound(abs(value.c)),
                signed_linear_support=bound(value.linear_bound()),
                nonlinear_remainder=bound(value.r), complete_support=bound(value.support()),
                coefficients_SHA256=hashlib.sha256(saved_reader.encoded(
                    [[str(v.mid().fmpq()), str(v.rad().fmpq())]
                     for v in [value.c, *value.a.entries(), value.r]])).hexdigest().upper())


def evaluate(root, family, progress, checkpoint):
    # Verification owns no action derivative evaluations. All seven predictors,
    # original groups, paired bytes and complete source bindings are checked.
    # The immutable readers bind their own module paths. Keep those imports in
    # the evidence checkout while the two new evaluator modules stay local.
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved_reader.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p, cert = base.p, base.p.values.cert
    middle = family == 'midpoint'
    pair = ('bhsm_midpoint_center_mean_value_right_pair_20260913' if middle
            else 'bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913')
    eigen_name = ('.coupled_midpoint_eigenpair_pilot_work/interval_013' if middle
                  else '.affine_eigenpair_pilot_work/endpoint_014')
    data = root/'tmp'/pair/'value/first/column.npz'
    eigenfile = root/'artifacts/flagship_integration'/eigen_name/'eigenpair.npz'
    nparam = verified['families'][family]['parameters']
    domain = TaylorDomain(verified['families'][family]['groups'], nparam)
    with np.load(data, allow_pickle=False) as z, np.load(eigenfile, allow_pickle=False) as eigen:
        read = lambda name: saved_reader.read_matrix(z, name, center=True)
        centers = [read(f'point_center_{i}') for i in range(7)]
        center = saved_reader.read_matrix(eigen, 'center_state', center=True)
        ep = saved_reader.read_matrix(eigen, 'eigenpair_center', center=True)
        inverse = saved_reader.read_matrix(eigen, 'preconditioner', center=True)
        directions, axis = read('weighted_tube_directions'), read('weighted_input_axis')
        raw_domain = saved_reader.read_matrix(z, 'raw_domain')
        descriptor = read('descriptor_base')
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights = [arb(float(x)) for x in weights]
    qw, rw = [[arb(float(x)) for x in v] for v in (qw, rw)]
    raw_axis = [axis[i, 0]/weights[i] for i in range(98)]
    state = [domain.affine(center[i, 0], [directions[i, j]/weights[i] for j in range(nparam)])
             for i in range(98)]
    # This independently checks the saved affine predictor's original outer
    # domain, not a newly chosen smaller domain.
    if any(not raw_domain[i, 0].contains(x.enclosure()) for i, x in enumerate(state)):
        raise ArithmeticError('common-parameter state not enclosed by original source domain')
    def model(c, deriv, rows):
        return [domain.affine(c[i, 0], [deriv[i, j] for j in range(nparam)]) for i in range(rows)]
    psi = model(ep, centers[3], 61)
    hard = model(centers[0], centers[4], 62)
    psi_u = model(centers[1], centers[5], 62)
    hard_u = model(centers[2], centers[6], 62)
    pad = lambda v: [arb(0)]*37+list(v[:61])
    # Every contraction includes the parent boundary and global inertia inverse.
    maps = [cert._dense_mapping(cert._integrand([x.c for x in state], i, 0).maps)
            for i in range(cert.POINTS)]
    sources = dict(verified['paired_source_hashes'])
    sources['retained_action_parent'] = saved_reader.sha(Path(cert.__file__))
    sources['shared_action_taylor'] = saved_reader.sha(Path(implementation.__file__))
    sources['evaluator'] = saved_reader.sha(Path(__file__))
    binding = hashlib.sha256(saved_reader.encoded(dict(sources=sources, family=family,
                                  precision=ctx.prec))).hexdigest().upper()
    checkpoint.mkdir(parents=True, exist_ok=True)
    terms = {}
    def action(name, legs):
        path = checkpoint/(name+'.json')
        if path.exists():
            record = json.loads(path.read_bytes())
            if record['binding'] != binding:
                raise ValueError('checkpoint source mismatch; use a fresh output directory')
            values = [arb(m)+arb(0, arb(r)) for m, r in record['values']]
            value = Taylor(domain, values[0], arb_mat(1, nparam, values[1:-1]), values[-1])
        else:
            with scalar_taylor_action(cert):
                value = cert._contracted_action(np.asarray(state, dtype=object),
                           [np.asarray(v, dtype=object) for v in legs], maps)
            if not isinstance(value, Taylor):
                value = domain.affine(value)
            # Store an exact upward remainder so recovery never treats an
            # uncertain radius as a proved nonnegative number.
            values = [value.c, *value.a.entries(), value.r]
            payload = dict(binding=binding, values=[
                [str(v.mid().fmpq()), str(v.rad().fmpq())] for v in values])
            with path.open('xb') as output:
                output.write(saved_reader.encoded(payload))
        terms[name] = summary(value)
        progress(name, terms[name])
        return value

    # An arbitrary exact eigenvalue predictor is permitted. Recover its signed
    # affine Rayleigh jet from the same p(theta), then retain the original saved
    # eigenvalue anchor. The omitted Rayleigh remainder is NOT an error bound
    # for the true eigenvalue; the complete eigenline residual still owns it.
    rayleigh = action('rayleigh_action', [pad(psi), pad(psi)])/dot(psi, psi)
    eigenvalue = domain.affine(ep[61, 0], [v.mid() for v in rayleigh.a.entries()])

    # Choose an output-informed exact covector proposal using the frozen QP
    # row. It is NOT asserted to be the exact full stacked output adjoint.
    residual = p.geometry.residual
    with base.cache.cache_hashes([(p.values, 'sha'), (residual.center, '_sha'),
                                 (residual.foundation.coordinate.center, '_sha')]):
        local = base.reader.load_inputs(13)
    P = base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axesfile = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axesfile, allow_pickle=False) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:, None]
    axes[0] = 0
    if hashlib.sha256(np.asarray(axes, dtype='<f8').tobytes()).hexdigest().upper() != local['binding']['axes_SHA256']:
        raise ValueError('frozen physical projector changed')
    a = [arb(float(x)) for x in axes[14]]
    qrow = arb_mat(1, 74, [arb(i == 73)-a[73]*a[i] for i in range(74)])
    zrow = qrow*P*(2*arb(float(local['step']))/3)
    # Use the same documented proposal for both anchor families. It selects
    # an action covector; no endpoint HS chain coefficient is inferred here.
    s = raw_domain[98, 0].mid()
    pc, hc = [v.c for v in psi], [v.c for v in hard]
    configuration = [qw[i]*center[37+i, 0] for i in range(37)]
    N = [s*x for x in configuration]+[rw[i]*(hc[61]*pc[i]+s*hc[i]) for i in range(61)]
    norm = dot(N, N).sqrt()
    delta = descriptor[0, 0]*hc[61]+s*descriptor[1, 0]
    zy = dot(zrow.entries(), N+[delta])
    cN = [zrow[0, i]/norm-zy*N[i]/norm**3 for i in range(98)]
    cd = zrow[0, 98]/norm
    ch = [s*rw[i]*cN[37+i]+cd*s*rw[i]/weights[37+i]*ep[61, 0]*pc[i] for i in range(61)]
    cb = dot(cN[37:], [rw[i]*pc[i] for i in range(61)])+cd*descriptor[0, 0]
    # The saved eigenpair inverse uses -p in its final column. Flip the last
    # solution coordinate to form a proposal for the response's +p border.
    candidate = arb_mat(1, 62, ch+[-cb])*inverse
    beta = [v.mid() for v in candidate.entries()]
    v, bottom = beta[:61], beta[61]
    raw_v = pad(v)
    g = [v[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[arb(0)]*61
    c = [arb(0)]*37+[v[i]*rw[i]/weights[37+i] for i in range(61)]
    d = [qw[i]*state[37+i]/weights[i] for i in range(37)]+[arb(0)]*61
    du = [qw[i]*raw_axis[37+i]/weights[i] for i in range(37)]+[arb(0)]*61
    f = action('source_gradient', [g])-action('source_hessian', [c, d])
    fu = (action('source_axis_gradient', [g, raw_axis])
          -action('source_axis_hessian', [c, d, raw_axis])
          -action('source_axis_configuration', [c, du]))
    slope = action('eigenvalue_axis', [pad(psi), pad(psi), raw_axis])
    residuals = {}
    residuals['eigenline'] = (action('eigenline_action', [raw_v, pad(psi)])
        -eigenvalue*dot(v, psi)+bottom*(dot(psi, psi)-1)/2)
    residuals['response'] = (action('response_action', [raw_v, pad(hard)])-eigenvalue*dot(v, hard[:61])
        +hard[61]*dot(v, psi)-f+bottom*dot(psi, hard[:61]))
    residuals['axis_line'] = (action('axis_line_action', [raw_v, pad(psi_u)])
        -eigenvalue*dot(v, psi_u[:61])+psi_u[61]*dot(v, psi)
        +action('axis_line_source', [raw_v, pad(psi), raw_axis])-slope*dot(v, psi)
        +bottom*dot(psi, psi_u[:61]))
    residuals['axis_response'] = (action('axis_response_action', [raw_v, pad(hard_u)])
        -eigenvalue*dot(v, hard_u[:61])+hard_u[61]*dot(v, psi)
        +action('axis_response_source', [raw_v, pad(hard), raw_axis])-slope*dot(v, hard[:61])
        +hard[61]*dot(v, psi_u[:61])-fu
        +bottom*(dot(psi, hard_u[:61])+dot(psi_u[:61], hard[:61])))
    p.verify_sources(json.loads((data.parent/'record.json').read_bytes())['binding'])
    return dict(algorithm='SHARED_PARAMETER_ACTION_RESIDUAL_TAYLOR_ARB512_V1', family=family,
        parameters=nparam, groups=domain.groups, binding=binding, source_hashes=sources,
        residuals={k: summary(v) for k, v in residuals.items()}, action_terms=terms,
        exact_covector=[str(x.fmpq()) for x in beta],
        all_seven_predictors_reused=True, action_boundary_and_global_inertia_included=True,
        signed_linear_parameters_retained=True, nonlinear_remainders_included=True,
        physical_domain_shrunk=False, predictor_is_solution_enclosure=False,
        covector_kind='FROZEN_LAST_RESPONSE_OUTPUT_ADJOINT_PROPOSAL',
        full_stacked_adjoint_certified=False, stacked_correction_inclusion=False,
        complete_projected_physical_error=None, physical_global_margin=None,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        missing='Full stacked adjoint/secant correction bound, lifted descriptor/output residual and exact endpoint-to-midpoint joint graph.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--family', choices=['midpoint', 'endpoint'], default='midpoint')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    if args.out.exists():
        raise FileExistsError('preserve prior evidence; use a new output path')
    result = evaluate(args.evidence_root.resolve(), args.family,
        lambda name, bound: print(json.dumps(dict(term=name, support=bound['complete_support']['approximate'],
            remainder=bound['nonlinear_remainder']['approximate'])), flush=True), args.out.with_suffix('.terms'))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as output:
        output.write(saved_reader.encoded(result))
    print(json.dumps(dict(family=args.family, residuals={k: v['complete_support']['approximate']
        for k, v in result['residuals'].items()}, physical_global_margin=None)), flush=True)


if __name__ == '__main__':
    main()
