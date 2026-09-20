"""Evaluate the left input operator, deferring base cancellation to transport.

The physical input occupies one 74-dimensional Euclidean ball. Two sets of
62 directional solve errors occupy additional shared scalar slots. Their
dependence on the physical input is relaxed only after Y-beta G is formed.
Every original state parameter and every base-solve correction is retained.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain, Taylor
from bhsm.interface.input_linear_taylor import InputLinearTaylor, vector_norm, input_linear_taylor_action
import bhsm.interface.input_linear_taylor as implementation
import n12_gate7_left_saved_family as saved
import certify_n12_gate7_endpoint_vector_transport as exact_balls


def dot(a, b):
    return sum((x*y for x, y in zip(a, b, strict=True)), arb(0))


def upper(v):
    return dict(exact=str(v.upper().fmpq()), approximate=float(v.upper()))


def encode(value):
    return [[str(v.mid().fmpq()), str(v.rad().fmpq())]
            for v in value.c.entries()+value.a.entries()+[value.r]]


def write_models_archive(path,values):
    """Keep the canonical JSON array while encoding one complete row at a time."""
    with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as stream:
        stream.write(b'[\n')
        for i,value in enumerate(values):
            if i: stream.write(b',\n')
            row=json.dumps(encode(value),sort_keys=True,indent=2)
            stream.write(('  '+row.replace('\n','\n  ')).encode())
        stream.write(b'\n]\n')
    digest=hashlib.sha256()
    with path.open('rb') as raw:
        for block in iter(lambda:raw.read(1024*1024),b''): digest.update(block)
    return digest.hexdigest().upper()


def evaluate(root, family, adjoint_path, refined_path, out, directional_path=None, unchanged_terms=None):
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
    adjoint = json.loads(adjoint_path.read_bytes())
    refined = json.loads(refined_path.read_bytes())
    directional = json.loads(directional_path.read_bytes()) if directional_path is not None else adjoint
    if directional_path is not None:
        if (directional.get('algorithm') != 'THREE_D3_DIRECTIONAL_OUTPUT_ADJOINT_POINT_PROPOSAL_V1'
                or directional.get('side') != 'left' or directional.get('family') != family
                or directional.get('unknowns') != 248
                or any(directional['source_hashes'].get(k) != v for k,v in verified['paired_source_hashes'].items())):
            raise ValueError('source-bound actual-left-point directional proposal required')
        covectors = directional['exact_covectors']
    else:
        covectors = adjoint['fixed_axis_covectors']
    for key in ('axis_line', 'axis_response'):
        if len(covectors[key]) != 62 or any(not arb(v).is_finite() for v in covectors[key]):
            raise ValueError('two finite complete directional covectors required')
    if adjoint.get('family') != family or adjoint.get('input_dimension') != 74 or adjoint.get('side') != 'left':
        raise ValueError('matching complete input adjoint required')
    for record in (adjoint, refined):
        if any(record['source_hashes'].get(k) != v for k, v in verified['paired_source_hashes'].items()):
            raise ValueError('unchanged original physical source family required')
    with np.load(data, allow_pickle=False) as z, np.load(eigenfile, allow_pickle=False) as e:
        centers = [saved.read_matrix(z, f'point_center_{i}', center=True) for i in range(7)]
        center = saved.read_matrix(e, 'center_state', center=True)
        ep = saved.read_matrix(e, 'eigenpair_center', center=True)
        eigenbox = saved.read_matrix(e, 'eigenpair_box')
        directions = saved.read_matrix(z, 'weighted_tube_directions')
        raw = saved.read_matrix(z, 'raw_domain')
    nstate = directions.ncols()
    groups = verified['families'][family]['groups']+[(nstate, nstate+124, 'box')]
    domain = TaylorDomain(groups, nstate+124)
    input_groups = [(0, 74, 'euclidean'), (74, 198, 'box')]
    U = arb_mat([[arb(v) for v in row] for row in adjoint['input_map']])
    line_point = arb_mat([[arb(v) for v in row] for row in adjoint['point_line_map']])
    response_point = arb_mat([[arb(v) for v in row] for row in adjoint['point_response_map']])
    kind, index = ('interval',13) if middle else ('endpoint',13)
    fullfile = root/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{family}_uniform_df_work/{kind}_{index:03d}/derivative.npz'
    relative = fullfile.relative_to(root).as_posix()
    if adjoint['source_hashes'].get(relative) != saved.sha(fullfile):
        raise ValueError('verified complete derivative source required')
    with np.load(fullfile, allow_pickle=False) as z:
        full_line = saved.read_matrix(z, 'selected_line_variation')*U
        full_response = saved.read_matrix(z, 'response_variation')*U
        point_rate = saved.read_matrix(z, 'point_derivative')*U
    axis_radii = []
    for uniform, point in ((full_line, line_point), (full_response, response_point)):
        axis_radii.extend(vector_norm([uniform[i,j]-point[i,j] for j in range(74)]) for i in range(62))
    base_radii = [arb(v) for v in refined['correction_radii_exact'][:124]]
    def model(c, derivative, rows, offset):
        values = []
        for i in range(rows):
            a = [derivative[i,j] for j in range(nstate)]+[arb(0)]*124
            a[nstate+offset+i] = base_radii[offset+i]
            values.append(domain.affine(c[i,0], a))
        return values
    def linear(c):
        value = InputLinearTaylor(domain, arb_mat(1,198,c), arb_mat(domain.dimension,198), input_groups=input_groups)
        value._linear = arb(0)
        return value
    def direction_models(point, offset):
        values = []
        for i in range(62):
            c = [point[i,j] for j in range(74)]+[arb(0)]*124
            c[74+offset+i] = axis_radii[offset+i]
            values.append(linear(c))
        return values
    psi = model(ep, centers[3], 61, 0)
    hard = model(centers[0], centers[4], 62, 62)
    psi_u, hard_u = direction_models(line_point,0), direction_models(response_point,62)
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights, qw, rw = [[arb(float(v)) for v in vv] for vv in (weights,qw,rw)]
    state = [domain.affine(center[i,0], [directions[i,j]/weights[i] for j in range(nstate)]+[arb(0)]*124)
             for i in range(98)]
    if any(not raw[i,0].contains(v.enclosure()) for i,v in enumerate(state)):
        raise ValueError('shared states must remain within original certified outer domain')
    u = [linear([U[i,j]/weights[i] for j in range(74)]+[arb(0)]*124) for i in range(98)]
    su = linear([U[98,j] for j in range(74)]+[arb(0)]*124)
    s = domain.affine(raw[98,0].mid(), [directions[98,j] for j in range(nstate)]+[arb(0)]*124)
    pad = lambda v: [domain.affine(0)]*37+list(v[:61])
    maps = [cert._dense_mapping(cert._integrand(center.entries(), node, 0).maps) for node in range(cert.POINTS)]
    terms = {}
    sources = {**verified['paired_source_hashes'], relative:saved.sha(fullfile),
               'adjoint':saved.sha(adjoint_path),'refined_base_radii':saved.sha(refined_path),
               'implementation':saved.sha(Path(implementation.__file__)),
               'exact_ball_restoration':saved.sha(Path(exact_balls.__file__)),
               'evaluator':saved.sha(Path(__file__)),
               'left_source_verifier':saved.sha(Path(saved.__file__))}
    if directional_path is not None:
        sources['directional_cancellation_proposal'] = saved.sha(directional_path)
    # Base coefficients are zero here. All 124 base equations will be
    # subtracted before endpoint transport in the final certified block.
    sources['base_cancellation_policy'] = 'DEFER_ALL_124_BASE_EQUATIONS_TO_PRETRANSPORT'
    reference_binding = None
    unchanged_names = {'rayleigh','slope','descriptor_c','descriptor_r',
        'descriptor_cu4','descriptor_cu3a','descriptor_cu3b',
        'descriptor_ru4','descriptor_ru3a','descriptor_ru3b'}
    if directional_path is None:
        # The same input-adjoint file supplies exactly the original v2,v3.
        unchanged_names |= {'axis_gradient','axis_hessian','axis_configuration',
            'axis_line','axis_line_source','axis_response','axis_response_source'}
    import bhsm.interface.shared_action_taylor as state_arithmetic
    import bhsm.interface.shared_parameter_residual as support_arithmetic
    sources['shared_action_taylor']=saved.sha(Path(state_arithmetic.__file__))
    sources['shared_parameter_residual']=saved.sha(Path(support_arithmetic.__file__))
    sources['source_verifier']=saved.sha(Path(saved.__file__))
    guarded_paths = {'adjoint':adjoint_path,'refined_base_radii':refined_path,
        'implementation':Path(implementation.__file__),'evaluator':Path(__file__),
        'exact_ball_restoration':Path(exact_balls.__file__),
        'shared_action_taylor':Path(state_arithmetic.__file__),
        'shared_parameter_residual':Path(support_arithmetic.__file__),
        'source_verifier':Path(saved.__file__)}
    if directional_path is not None:
        guarded_paths['directional_cancellation_proposal'] = directional_path
    if unchanged_terms is not None:
        reference_sources = json.loads((unchanged_terms/'sources.json').read_bytes())
        original_producer = ROOT/'scripts/certify_n12_gate7_left_input_output.py'
        if (reference_sources.get('evaluator') != saved.sha(original_producer)
                or any(reference_sources.get(k) != v for k,v in sources.items()
                    if k not in ('evaluator','directional_cancellation_proposal','base_cancellation_policy'))
                or set(reference_sources) != set(sources)-{'directional_cancellation_proposal','base_cancellation_policy'}):
            raise ValueError('identical original input maps, state operands and arithmetic required')
        reference_binding = saved.sha(unchanged_terms/'sources.json')
        sources['unchanged_checkpoint_producer'] = saved.sha(original_producer)
        sources['unchanged_checkpoint_source_manifest'] = reference_binding
        guarded_paths['unchanged_checkpoint_producer'] = original_producer
        guarded_paths['unchanged_checkpoint_source_manifest'] = unchanged_terms/'sources.json'
    binding = hashlib.sha256(saved.encoded(sources)).hexdigest().upper()
    termdir = out.with_suffix('.terms')
    termdir.mkdir(parents=True, exist_ok=True)
    manifest_path=termdir/'sources.json'
    source_bytes=saved.encoded(sources)
    if manifest_path.exists() and manifest_path.read_bytes()!=source_bytes:
        raise ValueError('checkpoint source manifest must be immutable')
    if not manifest_path.exists(): manifest_path.write_bytes(source_bytes)
    def action(name, legs):
        # A completed record is retained immediately; no partial result is
        # silently consumed by a later run.
        path=termdir/(name+'.json.gz')
        reference=(unchanged_terms/(name+'.json.gz')) if unchanged_terms is not None and name in unchanged_names else None
        origin=None
        if path.exists() or (reference is not None and reference.exists()):
            selected=path if path.exists() else reference
            stored=json.loads(gzip.decompress(selected.read_bytes()))
            expected=binding if selected==path else reference_binding
            if stored['binding'] != expected:
                raise ValueError('action checkpoint source mismatch; preserve it and use a fresh output path')
            origin=stored.get('origin') if selected==path else dict(binding=expected,SHA256=saved.sha(selected))
            v=[exact_balls.restore(pair) for pair in stored['values']]
            if stored['kind']=='InputLinearTaylor':
                if len(v)!=198+domain.dimension*198+1:
                    raise ValueError('complete input-linear checkpoint coefficients required')
                value=InputLinearTaylor(domain,arb_mat(1,198,v[:198]),
                    arb_mat(domain.dimension,198,v[198:-1]),v[-1],input_groups)
            elif stored['kind']=='Taylor':
                if len(v)!=domain.dimension+2:
                    raise ValueError('complete state checkpoint coefficients required')
                value=Taylor(domain,v[0],arb_mat(1,domain.dimension,v[1:-1]),v[-1])
            else:
                raise ValueError('known action checkpoint type required')
        else:
            with input_linear_taylor_action(cert):
                value = cert._contracted_action(np.array(state,dtype=object),
                             [np.array(v,dtype=object) for v in legs], maps)
        terms[name] = dict(kind=type(value).__name__,remainder=upper(value.r))
        if origin is not None:
            terms[name]['reused_checkpoint']=origin
        payload = dict(binding=binding,kind=type(value).__name__,values=encode(value)
                       if isinstance(value,InputLinearTaylor) else [[str(v.mid().fmpq()),str(v.rad().fmpq())]
                       for v in [value.c,*value.a.entries(),value.r]])
        if origin is not None: payload['origin']=origin
        encoded = gzip.compress(saved.encoded(payload),mtime=0)
        if not path.exists():
            with path.open('xb') as f:
                f.write(encoded)
        print(json.dumps(dict(term=name,**terms[name])),flush=True)
        return value
    # Reproduce the exact predictor eigenvalue from the uncorrected affine p.
    predicted_psi = [domain.affine(ep[i,0], [centers[3][i,j] for j in range(nstate)]+[arb(0)]*124) for i in range(61)]
    rayleigh = action('rayleigh',[pad(predicted_psi),pad(predicted_psi)])/dot(predicted_psi,predicted_psi)
    la = [v.mid() for v in rayleigh.a.entries()]
    lambda_predictor = domain.affine(ep[61,0],la)
    # Recompute the lambda correction if coefficient rounding differs from
    # the old predictor; this preserves the original eigenvalue inclusion.
    la[nstate+61] = (abs(eigenbox[61,0]-ep[61,0]).upper()+lambda_predictor.linear_bound()).upper()
    lam = domain.affine(ep[61,0],la)
    v2,v3 = [[arb(v) for v in covectors[key]] for key in ('axis_line','axis_response')]
    def source_legs(v):
        return ([v[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[arb(0)]*61,
                [arb(0)]*37+[v[i]*rw[i]/weights[37+i] for i in range(61)])
    g3,c3 = source_legs(v3)
    configuration = [qw[i]*state[37+i] for i in range(37)]
    configuration_u = [qw[i]*u[37+i] for i in range(37)]
    d = [configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61
    du = [configuration_u[i]/weights[i] for i in range(37)]+[arb(0)]*61
    fu = action('axis_gradient',[g3,u])-action('axis_hessian',[c3,d,u])-action('axis_configuration',[c3,du])
    slope = action('slope',[pad(psi),pad(psi),u])
    G2 = (action('axis_line',[pad(v2),pad(psi_u)])-lam*dot(v2[:61],psi_u[:61])+psi_u[61]*dot(v2[:61],psi)
          +action('axis_line_source',[pad(v2),pad(psi),u])-slope*dot(v2[:61],psi)+v2[61]*dot(psi,psi_u[:61]))
    G3 = (action('axis_response',[pad(v3),pad(hard_u)])-lam*dot(v3[:61],hard_u[:61])+hard_u[61]*dot(v3[:61],psi)
          +action('axis_response_source',[pad(v3),pad(hard),u])-slope*dot(v3[:61],hard[:61])
          +hard[61]*dot(v3[:61],psi_u[:61])-fu+v3[61]*(dot(psi,hard_u[:61])+dot(psi_u[:61],hard[:61])))
    scale = lambda v:[rw[i]/weights[37+i]*v[i] for i in range(61)]
    pp,pu = pad(psi),pad(psi_u)
    aa,au = pad(scale(psi)),pad(scale(psi_u))
    dd = d[:37]+scale(hard)
    ddu = du[:37]+scale(hard_u)
    cpsi = action('descriptor_c',[pp,pp,aa])
    rem = action('descriptor_r',[pp,pp,dd])
    cu = action('descriptor_cu4',[pp,pp,aa,u])+2*action('descriptor_cu3a',[pp,pu,aa])+action('descriptor_cu3b',[pp,pp,au])
    ru = action('descriptor_ru4',[pp,pp,dd,u])+2*action('descriptor_ru3a',[pp,pu,dd])+action('descriptor_ru3b',[pp,pp,ddu])
    N = [s*v for v in configuration]+[rw[i]*(hard[61]*psi[i]+s*hard[i]) for i in range(61)]
    Nu = [su*x+s*y for x,y in zip(configuration,configuration_u)]
    Nu += [rw[i]*(hard_u[61]*psi[i]+hard[61]*psi_u[i]+su*hard[i]+s*hard_u[i]) for i in range(61)]
    delta,deltau = hard[61]*cpsi+s*rem,hard_u[61]*cpsi+hard[61]*cu+su*rem+s*ru
    norm = (dot(N,N).log()/2).exp()
    residual = p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]):
        local = base.reader.load_inputs(13)
    P = base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axesfile = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axesfile,allow_pickle=False) as z:
        axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:],axis=1)[:,None]
    axes[0]=0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper()!=local['binding']['axes_SHA256']:
        raise ValueError('original projection required')
    axis=[arb(float(x)) for x in axes[14]]
    Q=arb_mat(74,74,[arb(i==j)-axis[i]*axis[j] for i in range(74) for j in range(74)])
    L=Q*P*(2*arb(float(local['step']))/3)
    Y=dot([L[73,j] for j in range(99)],Nu+[deltau])/norm-dot([L[73,j] for j in range(99)],N+[delta])*dot(N,Nu)/(norm**3)
    W=Y-G2-G3
    cancellation=dict(raw_output_support=upper(Y.support()),cancelled_support=upper(W.support()),
        directional_correction_constant_support=upper(sum((abs(W.c[0,j]).upper() for j in range(74,198)),arb(0))),
        cancelled_linear_support=upper(W.linear_bound()),cancelled_remainder=upper(W.r))
    print(json.dumps(dict(scalar_operator_cancellation=cancellation)),flush=True)
    if L[73,98].contains(0):
        raise ArithmeticError('nonzero descriptor pivot required')
    # The final reconstructor combines this pivot with all 61 separately
    # certified velocity numerators. Do not materialize 73 unused raw rows.
    out.mkdir(parents=True,exist_ok=False)
    scalar_data=gzip.compress(saved.encoded(encode(W)),mtime=0)
    (out/'scalar_model.json.gz').write_bytes(scalar_data)
    result=dict(algorithm='LEFT_DEFERRED_BASE_SHARED_SCALAR_PIVOT_V1',family=family,side='left',
        original_state_groups=groups,input_groups=input_groups,physical_input_columns=74,
        projected_output_rows=74,saved_scalar_rows=1,scalar_row=73,
        all_projected_rows_require_complete_velocity_reconstruction=True,
        input_correction_symbols=124,base_correction_symbols=124,
        input_map=adjoint['input_map'],axis_correction_radii=[str(v.fmpq()) for v in axis_radii],
        scalar_row_bound=dict(component=73,support=upper(W.support()),linear=upper(W.linear_bound()),nonlinear=upper(W.r)),
        terms=terms,base_cancellation_deferred=True,base_equations_deferred=124,
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        scope='all-input scalar pivot; all 61 velocity numerators and endpoint transport required for full vector',
        scalar_operator_cancellation=cancellation,source_hashes=sources,
        scalar_model_SHA256=hashlib.sha256(scalar_data).hexdigest().upper())
    if any(saved.sha(path) != sources[key] for key,path in guarded_paths.items()):
        raise ValueError('source changed during deferred-cancellation arithmetic')
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(scalar_pivot_support=upper(W.support()),complete_vector_certified=False)),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--family',choices=('midpoint','endpoint'),required=True)
    parser.add_argument('--adjoint',type=Path,required=True)
    parser.add_argument('--refined',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--local-inputs',action='store_true')
    parser.add_argument('--directional-adjoint',type=Path)
    parser.add_argument('--unchanged-terms',type=Path)
    args=parser.parse_args()
    ctx.prec=512
    if args.local_inputs:
        global input_linear_taylor_action,implementation
        import bhsm.interface.local_input_taylor_action_fast as implementation
        input_linear_taylor_action=implementation.input_linear_taylor_action
    if args.out.exists():
        raise FileExistsError('fresh output required')
    evaluate(args.evidence_root.resolve(),args.family,args.adjoint.resolve(),args.refined.resolve(),args.out,args.directional_adjoint,args.unchanged_terms)


if __name__=='__main__':
    main()
