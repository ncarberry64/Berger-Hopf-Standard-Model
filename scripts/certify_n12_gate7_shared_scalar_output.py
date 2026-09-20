"""Bound one physical scalar via Y-beta*G on an inherited solution domain.

The full nonlinear action and output are evaluated before support bounds.
G=0 on the inherited physical graph, so Y=Y-beta*G there for ANY fixed beta.
An approximate anchor adjoint improves cancellation but is not an assumption.
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


def evaluate(root, family, adjoint_path, progress, checkpoint):
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
    ninput = verified['families'][family]['parameters']
    nparam = ninput+248
    groups = verified['families'][family]['groups']+[(ninput, nparam, 'box')]
    domain = TaylorDomain(groups, nparam)
    adjoint = json.loads(adjoint_path.read_bytes())
    if (adjoint.get('algorithm') != 'COMPLETE_COUPLED_ANCHOR_OUTPUT_ADJOINT_ARB512_V1'
            or adjoint.get('family') != family or adjoint.get('unknowns') != 248):
        raise ValueError('matching complete anchor adjoint proposal required')
    if any(adjoint['source_hashes'].get(k) != v for k, v in verified['paired_source_hashes'].items()):
        raise ValueError('adjoint belongs to a different physical source family')
    betas = {k:[arb(x) for x in v] for k, v in adjoint['exact_covectors'].items()}
    if (set(betas) != {'eigenline','response','axis_line','axis_response'}
            or any(len(v) != 62 or any(not x.rad().is_zero() or not x.is_finite() for x in v) for v in betas.values())):
        raise ValueError('complete exact fixed residual covectors required')
    with np.load(data, allow_pickle=False) as z, np.load(eigenfile, allow_pickle=False) as eigen:
        read = lambda name: saved_reader.read_matrix(z, name, center=True)
        centers = [read(f'point_center_{i}') for i in range(7)]
        center = saved_reader.read_matrix(eigen, 'center_state', center=True)
        ep = saved_reader.read_matrix(eigen, 'eigenpair_center', center=True)
        inverse = saved_reader.read_matrix(eigen, 'preconditioner', center=True)
        directions = saved_reader.read_matrix(z, 'weighted_tube_directions')
        axis = read('weighted_input_axis')
        raw_domain = saved_reader.read_matrix(z, 'raw_domain')
        descriptor = read('descriptor_base')
        boxes = saved_reader.read_matrix(eigen, 'eigenpair_box').entries()
        boxes += sum([saved_reader.read_matrix(z, f'uniform_solve_{i}').entries() for i in range(3)], [])
        point_derivative = saved_reader.read_matrix(z, 'point_derivative')
    report = json.loads((data.parent/'record.json').read_bytes())['report']
    if not all(report.get(k) is True for k in ('same_family_segment_smoothness_established',
        'complete_original_seven_solve_graph_used','complete_original_scalar_contractions_used')):
        raise ValueError('complete same-family implicit physical graph required')
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights = [arb(float(x)) for x in weights]
    qw, rw = [[arb(float(x)) for x in v] for v in (qw, rw)]
    raw_axis = [axis[i, 0]/weights[i] for i in range(98)]
    state = [domain.affine(center[i, 0], [directions[i, j]/weights[i] for j in range(ninput)]+[arb(0)]*248)
             for i in range(98)]
    # This independently checks the saved affine predictor's original outer
    # domain, not a newly chosen smaller domain.
    if any(not raw_domain[i, 0].contains(x.enclosure()) for i, x in enumerate(state)):
        raise ArithmeticError('common-parameter state not enclosed by original source domain')
    def model(c, deriv, rows):
        return [domain.affine(c[i, 0], [deriv[i, j] for j in range(ninput)]+[arb(0)]*248) for i in range(rows)]
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
    sources['full_output_adjoint'] = saved_reader.sha(adjoint_path)
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

    # The source boxes already contain the true same-family implicit solution.
    # For each theta, U-Uhat lies in this explicit correction box. Parameter
    # dependencies are preserved until after Y-beta*G has been formed.
    predictors = psi+[eigenvalue]+hard+psi_u+hard_u
    correction_radii = []
    corrected = []
    for i, (value, box) in enumerate(zip(predictors, boxes, strict=True)):
        radius = (abs(box-value.c).upper()+value.linear_bound()+value.r).upper()
        coefficients = value.a.entries()
        coefficients[ninput+i] = radius
        corrected.append(domain.affine(value.c, coefficients, value.r))
        correction_radii.append(str(radius.fmpq()))
    psi, eigenvalue = corrected[:61], corrected[61]
    hard, psi_u, hard_u = corrected[62:124], corrected[124:186], corrected[186:248]

    # Reconstruct the unchanged scalar output itself, independently of beta.
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
    v0, v1, v2, v3 = [betas[k][:61] for k in ('eigenline','response','axis_line','axis_response')]
    bottom = {k:v[61] for k,v in betas.items()}
    def source_legs(v):
        return ([v[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[arb(0)]*61,
                [arb(0)]*37+[v[i]*rw[i]/weights[37+i] for i in range(61)])
    g1, c1 = source_legs(v1)
    g3, c3 = source_legs(v3)
    d = [qw[i]*state[37+i]/weights[i] for i in range(37)]+[arb(0)]*61
    du = [qw[i]*raw_axis[37+i]/weights[i] for i in range(37)]+[arb(0)]*61
    f = action('source_gradient', [g1])-action('source_hessian', [c1, d])
    fu = (action('source_axis_gradient', [g3, raw_axis])
          -action('source_axis_hessian', [c3, d, raw_axis])
          -action('source_axis_configuration', [c3, du]))
    slope = action('eigenvalue_axis', [pad(psi), pad(psi), raw_axis])
    residuals = {}
    residuals['eigenline'] = (action('eigenline_action', [pad(v0), pad(psi)])
        -eigenvalue*dot(v0, psi)+bottom['eigenline']*(dot(psi, psi)-1)/2)
    residuals['response'] = (action('response_action', [pad(v1), pad(hard)])-eigenvalue*dot(v1, hard[:61])
        +hard[61]*dot(v1, psi)-f+bottom['response']*dot(psi, hard[:61]))
    residuals['axis_line'] = (action('axis_line_action', [pad(v2), pad(psi_u)])
        -eigenvalue*dot(v2, psi_u[:61])+psi_u[61]*dot(v2, psi)
        +action('axis_line_source', [pad(v2), pad(psi), raw_axis])-slope*dot(v2, psi)
        +bottom['axis_line']*dot(psi, psi_u[:61]))
    residuals['axis_response'] = (action('axis_response_action', [pad(v3), pad(hard_u)])
        -eigenvalue*dot(v3, hard_u[:61])+hard_u[61]*dot(v3, psi)
        +action('axis_response_source', [pad(v3), pad(hard), raw_axis])-slope*dot(v3, hard[:61])
        +hard[61]*dot(v3, psi_u[:61])-fu
        +bottom['axis_response']*(dot(psi, hard_u[:61])+dot(psi_u[:61], hard[:61])))

    s = domain.affine(raw_domain[98, 0].mid(), [directions[98, j] for j in range(ninput)]+[arb(0)]*248)
    su = axis[98, 0]
    configuration = [qw[i]*state[37+i] for i in range(37)]
    configuration_u = [qw[i]*raw_axis[37+i] for i in range(37)]
    scale = lambda vec: [rw[i]/weights[37+i]*vec[i] for i in range(61)]
    aa, au = pad(scale(psi)), pad(scale(psi_u))
    dd = [configuration[i]/weights[i] for i in range(37)]+scale(hard)
    ddu = [configuration_u[i]/weights[i] for i in range(37)]+scale(hard_u)
    pp, pu = pad(psi), pad(psi_u)
    cpsi = action('descriptor_c', [pp, pp, aa])
    rem = action('descriptor_r', [pp, pp, dd])
    cu = (action('descriptor_cu_4', [pp, pp, aa, raw_axis])
        +2*action('descriptor_cu_3a', [pp, pu, aa])+action('descriptor_cu_3b', [pp, pp, au]))
    ru = (action('descriptor_ru_4', [pp, pp, dd, raw_axis])
        +2*action('descriptor_ru_3a', [pp, pu, dd])+action('descriptor_ru_3b', [pp, pp, ddu]))
    N = [s*x for x in configuration]+[rw[i]*(hard[61]*psi[i]+s*hard[i]) for i in range(61)]
    Nu = [su*x+s*y for x,y in zip(configuration, configuration_u)]
    Nu += [rw[i]*(hard_u[61]*psi[i]+hard[61]*psi_u[i]+su*hard[i]+s*hard_u[i]) for i in range(61)]
    delta = hard[61]*cpsi+s*rem
    deltau = hard_u[61]*cpsi+hard[61]*cu+su*rem+s*ru
    norm = (dot(N, N).log()/2).exp()
    Y = dot(zrow.entries(), Nu+[deltau])/norm-dot(zrow.entries(), N+[delta])*dot(N, Nu)/(norm**3)
    W = Y-sum(residuals.values(), domain.affine(0))
    anchor = (zrow*point_derivative)[0, 0]
    deviation = W-anchor
    p.verify_sources(json.loads((data.parent/'record.json').read_bytes())['binding'])
    return dict(algorithm='SHARED_PARAMETER_RESIDUAL_CANCELLED_PHYSICAL_SCALAR_ARB512_V1', family=family,
        parameters=nparam, groups=domain.groups, binding=binding, source_hashes=sources,
        residuals={k: summary(v) for k, v in residuals.items()}, action_terms=terms,
        correction_radii_exact=correction_radii,
        exact_covectors=adjoint['exact_covectors'],
        physical_scalar=summary(W), physical_scalar_anchor_deviation=summary(deviation),
        scalar_remainder_support=summary(W)['nonlinear_remainder'],
        correction_linear_support=summary(domain.affine(0,[arb(0)]*ninput+W.a.entries()[ninput:]))['signed_linear_support'],
        inherited_solution_boxes_enclose_graph=True, residual_identity_used_before_support=True,
        all_seven_predictors_reused=True, action_boundary_and_global_inertia_included=True,
        signed_linear_parameters_retained=True, nonlinear_remainders_included=True,
        physical_domain_shrunk=False, predictor_is_solution_enclosure=False,
        covector_kind='FROZEN_LAST_RESPONSE_OUTPUT_ADJOINT_PROPOSAL',
        full_stacked_adjoint_certified=False, stacked_correction_inclusion='INHERITED_SAME_FAMILY_SOLUTION_BOXES',
        complete_projected_physical_error=None, physical_global_margin=None,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        missing='This is one fixed scalar directional output. Complete vector norm, endpoint chain, full-history physical coefficients and remaining Gate-7 obligations are not certified.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--family', choices=['midpoint', 'endpoint'], default='midpoint')
    parser.add_argument('--adjoint', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    if args.out.exists():
        raise FileExistsError('preserve prior evidence; use a new output path')
    result = evaluate(args.evidence_root.resolve(), args.family, args.adjoint.resolve(),
        lambda name, bound: print(json.dumps(dict(term=name, support=bound['complete_support']['approximate'],
            remainder=bound['nonlinear_remainder']['approximate'])), flush=True), args.out.with_suffix('.terms'))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as output:
        output.write(saved_reader.encoded(result))
    print(json.dumps(dict(family=args.family,
        physical_scalar_anchor_deviation=result['physical_scalar_anchor_deviation']['complete_support']['approximate'],
        nonlinear_remainder=result['physical_scalar']['nonlinear_remainder']['approximate'],
        physical_global_margin=None)), flush=True)


if __name__ == '__main__':
    main()
