# Left-family specialization: retained endpoint 13 and positive HS input chain.
# The original right-family proof sources remain immutable.
"""Benchmark local state compression on left unnormalized velocity components.

The retained scalar descriptor cancellation is extended to the 61 velocity
components before normalization and endpoint transport. This is a local
vector refinement, not a global Gate-7 certificate.
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


def evaluate(root, family, adjoint_path, refined_path, out, components, reference=None):
    reuse=None
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
        R = saved.read_matrix(e, 'preconditioner', center=True)
        defect = saved.read_matrix(e, 'center_defect')
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
    import bhsm.interface.input_linear_anchor_jet as anchor_implementation
    import bhsm.interface.local_input_anchor_action as local_anchor
    import bhsm.interface.velocity_residual_adjoint as vector_adjoint
    sources = {**verified['paired_source_hashes'], relative:saved.sha(fullfile),
               'anchor_arithmetic':saved.sha(Path(anchor_implementation.__file__)),
               'local_anchor':saved.sha(Path(local_anchor.__file__)),
               'vector_adjoint':saved.sha(Path(vector_adjoint.__file__)),
               'adjoint':saved.sha(adjoint_path),'refined_base_radii':saved.sha(refined_path),
               'implementation':saved.sha(Path(implementation.__file__)),
               'exact_ball_restoration':saved.sha(Path(exact_balls.__file__)),
               'evaluator':saved.sha(Path(__file__))}
    reference_binding=None
    reference_dir=None
    if reference is not None:
        reference_dir=reference.with_suffix('.terms')
        reference_sources=json.loads((reference_dir/'sources.json').read_bytes())
        full_producer=ROOT/'scripts/certify_n12_gate7_coupled_numerator_vector.py'
        directional_producer=ROOT/'scripts/certify_n12_gate7_directional_numerator_vector.py'
        allowed_sources={saved.sha(full_producer),saved.sha(directional_producer),saved.sha(Path(__file__))}
        if reference_sources.get('evaluator') not in allowed_sources:
            raise ValueError('unchanged reviewed numerator producer required')
        import bhsm.interface.local_input_taylor_action as previous_implementation
        if reference_sources.get('implementation') not in {saved.sha(Path(previous_implementation.__file__)),saved.sha(Path(implementation.__file__))}:
            raise ValueError('reviewed equivalent local arithmetic required')
        if any(reference_sources.get(k)!=v for k,v in sources.items() if k not in ('evaluator','implementation')):
            raise ValueError('same original inputs, correction boxes, arithmetic and covector construction required')
        reference_binding=saved.sha(reference_dir/'sources.json')
        sources['reference_evaluator']=reference_sources['evaluator']
        sources['reference_implementation']=reference_sources['implementation']
        sources['reference_source_manifest']=reference_binding
    import bhsm.interface.shared_action_taylor as state_arithmetic
    import bhsm.interface.shared_parameter_residual as support_arithmetic
    sources['shared_action_taylor']=saved.sha(Path(state_arithmetic.__file__))
    sources['shared_parameter_residual']=saved.sha(Path(support_arithmetic.__file__))
    sources['source_verifier']=saved.sha(Path(saved.__file__))
    if reference is not None:
        for key in ('shared_action_taylor','shared_parameter_residual','source_verifier'):
            if reference_sources.get(key)!=sources[key]:
                raise ValueError('unchanged arithmetic and verifier required for checkpoint reuse')
    binding = hashlib.sha256(saved.encoded(sources)).hexdigest().upper()
    termdir = out.with_suffix('.terms')
    termdir.mkdir(parents=True, exist_ok=True)
    manifest_path=termdir/'sources.json'
    source_bytes=saved.encoded(sources)
    if manifest_path.exists() and manifest_path.read_bytes()!=source_bytes:
        raise ValueError('checkpoint source manifest must be immutable')
    if not manifest_path.exists(): manifest_path.write_bytes(source_bytes)
    active_component=None
    def action(name, legs):
        if active_component is not None: name=f"component_{active_component:02d}_{name}"
        # A completed record is retained immediately; no partial result is
        # silently consumed by a later run.
        path=termdir/(name+'.json.gz')
        reference_term=(reference_dir/(name+'.json.gz')) if reference_dir is not None else None
        # Reuse only after the referenced producer has stopped. Full gzip
        # integrity, source binding, matrix shape, and dyadic restoration
        # are checked below; a partial/interrupted checkpoint fails closed.
        origin=None
        if path.exists() or (reference_term is not None and reference_term.exists()):
            selected=path if path.exists() else reference_term
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
    configuration = [qw[i]*state[37+i] for i in range(37)]
    configuration_u = [qw[i]*u[37+i] for i in range(37)]
    d = [configuration[i]/weights[i] for i in range(37)]+[arb(0)]*61
    du = [configuration_u[i]/weights[i] for i in range(37)]+[arb(0)]*61
    slope = action('slope',[pad(psi),pad(psi),u])
    K = R.solve(arb_mat(np.eye(62,dtype=int).tolist())-defect)
    H = arb_mat(61,61,[K[i,j]+(ep[61,0] if i==j else 0) for i in range(61) for j in range(61)])
    # The eigenpair equation has -psi in its last column. Directional
    # residuals use +psi, consistently with the retained variation records.
    Kplus = arb_mat(62,62)
    for i in range(61):
        for j in range(61): Kplus[i,j]=H[i,j]-(ep[61,0] if i==j else 0)
        Kplus[i,61]=ep[i,0];Kplus[61,i]=ep[i,0]
    out.mkdir(parents=True,exist_ok=False)
    records=[]
    for component in components:
        active_component=component
        v2,v3,defect2,defect3=vector_adjoint.directional_covectors(Kplus,
            centers[0].entries()[:61],centers[0][61,0],raw[98,0].mid(),[arb(i==component) for i in range(61)])
        axis_defect=max(abs(v).upper() for v in defect2.entries()+defect3.entries())
        print(json.dumps(dict(component=component,stage='anchor_covectors')),flush=True)
        def source_legs(v):
            return ([v[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[arb(0)]*61,
                    [arb(0)]*37+[v[i]*rw[i]/weights[37+i] for i in range(61)])
        g3,c3=source_legs(v3)
        fu=action('axis_gradient',[g3,u])-action('axis_hessian',[c3,d,u])-action('axis_configuration',[c3,du])
        G2=(action('axis_line',[pad(v2),pad(psi_u)])-lam*dot(v2[:61],psi_u[:61])+psi_u[61]*dot(v2[:61],psi)
            +action('axis_line_source',[pad(v2),pad(psi),u])-slope*dot(v2[:61],psi)+v2[61]*dot(psi,psi_u[:61]))
        G3=(action('axis_response',[pad(v3),pad(hard_u)])-lam*dot(v3[:61],hard_u[:61])+hard_u[61]*dot(v3[:61],psi)
            +action('axis_response_source',[pad(v3),pad(hard),u])-slope*dot(v3[:61],hard[:61])
            +hard[61]*dot(v3[:61],psi_u[:61])-fu+v3[61]*(dot(psi,hard_u[:61])+dot(psi_u[:61],hard[:61])))
        Y=hard_u[61]*psi[component]+hard[61]*psi_u[component]+su*hard[component]+s*hard_u[component]
        W=Y-G2-G3
        payload=dict(component=component,coefficients=encode(W),
            axis_covectors=[[str(v.fmpq()) for v in block] for block in (v2,v3)],
            source_binding=binding)
        archive=out/f'component_{component:02d}.json.gz'
        archive.write_bytes(gzip.compress(saved.encoded(payload),mtime=0))
        record=dict(component=component,raw_support=upper(Y.support()),cancelled_support=upper(W.support()),
            constant_correction_support=upper(sum((abs(W.c[0,j]).upper() for j in range(74,198)),arb(0))),
            linear=upper(W.linear_bound()),nonlinear=upper(W.r),base_residuals_subtracted=False,
            axis_adjoint_defect=upper(axis_defect),models_SHA256=saved.sha(archive),terms=dict(terms))
        (out/f'component_{component:02d}.json').write_bytes(saved.encoded(record))
        records.append(record)
        print(json.dumps(dict(component=component,constant_error=float(arb(record['constant_correction_support']['exact'])),
                              linear=float(W.linear_bound()),remainder=float(W.r))),flush=True)
    result=dict(side='left',algorithm='FULL_INPUT_DIRECTIONAL_NUMERATOR_SHARED_RESIDUAL_V1',family=family,components=list(components),
        all_61_velocity_components_certified=set(components)==set(range(61)),
        original_state_groups=groups,input_groups=input_groups,input_map=adjoint['input_map'],
        axis_correction_radii=[str(v.fmpq()) for v in axis_radii],source_hashes=sources,
        records=records,base_residuals_subtracted=False,
        physical_input_columns=74,full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'record.json').write_bytes(saved.encoded(result))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--family',choices=('midpoint','endpoint'),required=True)
    parser.add_argument('--adjoint',type=Path,required=True)
    parser.add_argument('--refined',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--reference',type=Path,help='completed terms from the source-bound full numerator producer')
    parser.add_argument('--components',default='0:61',help='half-open component range, e.g. 0:61')
    args=parser.parse_args();ctx.prec=512
    start,stop=map(int,args.components.split(':'))
    if not 0<=start<stop<=61: raise ValueError('nonempty physical velocity component range required')
    if args.out.exists(): raise FileExistsError('fresh output required')
    global input_linear_taylor_action,implementation
    import bhsm.interface.local_state_input_taylor_action as implementation
    input_linear_taylor_action=implementation.input_linear_taylor_action
    evaluate(args.evidence_root.resolve(),args.family,args.adjoint.resolve(),args.refined.resolve(),args.out.resolve(),range(start,stop),args.reference.resolve() if args.reference is not None else None)


if __name__=='__main__': main()
