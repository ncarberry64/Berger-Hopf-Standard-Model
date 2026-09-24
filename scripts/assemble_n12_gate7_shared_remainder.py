"""Signed interval-13 operator recipe and explicitly relaxed support screen.

The immutable parents preserve the complete expressions that are available.
This numerical backend imports their affine enclosures, so it deliberately
does not claim that all higher-order or inherited theta correlations have
been recovered. The diagnostic cannot establish a physical failure.
"""
import argparse,ast,hashlib,json,sys
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_expression_graph import restore,pair
from bhsm.interface.sparse_affine_enclosure import SparseDomain,SparseAffine
from bhsm.interface.projected_affine_enclosures import ProjectedAffineModels,booked_affine_relaxation
from bhsm.interface.adaptive_expression_reader import read_graph
from bhsm.interface.shared_hs_output_operator import composed_operators,projected_operator
from audit_n12_gate7_layer_c_correlation import sha,encode,number,norm,matrix,rational_array


def operands(evidence):
    sources={};base=evidence/'artifacts/flagship_integration'
    package=ROOT/'artifacts/flagship_integration/gate7_physical_tube_20260924'
    def read(p):
        sources[str(p.resolve())]=sha(p)
        return json.loads(p.read_bytes())
    atlas=read(package/'interval_013/certificate.json')
    receipt=read(package/'interval_013/reproduction.json')
    if not atlas['complete_physical_tube_cover_certified'] or receipt['certificate_SHA256']!=sha(package/'interval_013/certificate.json'):
        raise ValueError('frozen complete interval-13 physical cover required')
    old=read(package/'rate_and_remainder/interval13_inherited_remainder_first.json')
    def operand(name):
        p=base/name;h=sha(p);sources[str(p.resolve())]=h
        if str(p.resolve()) in old['source_SHA256'] and old['source_SHA256'][str(p.resolve())]!=h:
            raise ValueError('changed frozen operand: '+name)
        return p
    with np.load(operand('.coupled_midpoint_uniform_df_work/interval_013/derivative.npz'),allow_pickle=False) as z:
        a=rational_array(z,'derivative');A=arb_mat(99,99,list(a.flat))
    endpoint=operand('BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz')
    jacobian=operand('BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz')
    inverse=operand('BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz')
    causal=operand('BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz')
    with np.load(endpoint,allow_pickle=False) as z:h=arb(float(z['collocation_arc_parameters'][14]-z['collocation_arc_parameters'][13]))
    with np.load(jacobian,allow_pickle=False) as z:tangent=z['endpoint_physical_tangent_action'][14]
    with np.load(inverse,allow_pickle=False) as z:right=matrix(z['reduced_right_Newton_blocks'][13])
    action=ROOT/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
    tree=ast.parse(action.read_text())
    scale=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TEST_DESCRIPTOR_SCALE' for t in n.targets))
    test=np.zeros((74,99));test[:73,:98]=tangent.T;test[73,98]=scale;B=right.solve(matrix(test))
    with np.load(causal,allow_pickle=False) as z:maps=z['causal_maps_center'].copy()
    axes_path=evidence/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    sources[str(axes_path.resolve())]=sha(axes_path)
    with np.load(axes_path,allow_pickle=False) as z:axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    foundation=read(operand('BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE.json'))
    if not foundation['validation_passed'] or foundation['coverage']!=dict(intervals=370,nodes=371,complete=True):
        raise ValueError('complete frozen causal arithmetic authority required')
    for p in (endpoint,jacobian,inverse,causal):
        if sha(p)!=foundation['inputs'][p.relative_to(evidence).as_posix()]:raise ValueError('frozen causal input changed')
    ah=lambda a:hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest().upper()
    if ah(axes)!=foundation['axes_SHA256'] or ah(maps)!=foundation['causal_maps_SHA256']:raise ValueError('frozen axes/maps changed')
    folder=base/'.direct_physical_quadratic_source_work/interval_013'
    manifest=read(folder/'manifest.json');repro=read(folder/'reproduction.json')
    if repro['manifest_SHA256']!=sha(folder/'manifest.json') or not repro['byte_identical'] or not repro['independent_recomputation']:
        raise ValueError('reproduced frozen signed booking required')
    quadratics={}
    for family in ('LL','LT'):
        quadratics[family]={}
        for pair in ('00','01','10','11'):
            p=folder/f'{family}_{pair}.npz';record=read(p.with_suffix('.json'))
            if record['data_SHA256']!=sha(p) or record['interval']!=13 or record['family']!=family or record['endpoint_pair']!=pair or not record['taylor_half_included']:
                raise ValueError('same booked half-Hessian required')
            if record['axes_SHA256']!=foundation['axes_SHA256'] or record['causal_maps_SHA256']!=foundation['causal_maps_SHA256']:
                raise ValueError('booking axis/map binding mismatch')
            for path in (p,p.with_suffix('.json')):
                expected=manifest['files'][path.relative_to(evidence).as_posix()]
                if expected not in (sha(path),hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest().upper()):
                    raise ValueError('booking manifest mismatch')
                sources[str(path.resolve())]=sha(path)
            with np.load(p,allow_pickle=False) as z:Q=rational_array(z,'Q')
            quadratics[family][pair]=arb_mat(*Q.shape,list(Q.flat))
    sources[str(action.resolve())]=sha(action)
    return atlas,A,h,B,maps,axes,foundation,quadratics,sources


def run(args):
    ctx.prec=512
    if args.out.exists():raise FileExistsError('fresh derived diagnostic required')
    modules=[Path(__file__),ROOT/'src/bhsm/interface/shared_projected_rate.py',ROOT/'src/bhsm/interface/projected_affine_enclosures.py',ROOT/'src/bhsm/interface/shared_expression_graph.py',ROOT/'src/bhsm/interface/sparse_affine_enclosure.py',ROOT/'src/bhsm/interface/streamed_expression_artifact.py',ROOT/'src/bhsm/interface/adaptive_expression_reader.py',ROOT/'src/bhsm/interface/shared_hs_output_operator.py',ROOT/'scripts/audit_n12_gate7_layer_c_correlation.py']
    code_sources={str(p.resolve()):sha(p) for p in modules}
    atlas,A,h,B,maps,axes,foundation,quadratics,sources=operands(args.evidence_root)
    sources.update(code_sources)
    paths=[args.left,args.middle,args.right]
    metadata=[read_graph(p) for p in paths];hashes=[sha(p) for p in paths]
    for site,z,p,digest in zip(('left','middle','right'),metadata,paths,hashes):
        if z['site']!=site or z['interval']!=13 or z['radius_exact']!=atlas['radius_exact']:raise ValueError('same interval and unchanged radii required')
        for name,value in z['source_SHA256'].items():
            if sha(Path(name))!=value:raise ValueError('parent input changed: '+name)
        sources[str(p.resolve())]=digest
    if any(z['parameter_order']!=metadata[0]['parameter_order'] or z['groups']!=metadata[0]['groups'] for z in metadata):
        raise ValueError('one shared theta/u/v namespace required')
    cell_hashes=[]
    parents=dict(zip(('left','middle','right'),hashes))
    for i,cover_cell in enumerate(atlas['cells']):
        path=args.cells/f'cell_{i:02d}.json';cell=json.loads(path.read_bytes())
        if (cell['cell']!=i or cell['interval']!=13 or cell['radius_exact']!=atlas['radius_exact']
                or cell['common_parent_graphs_SHA256']!=parents or cell['frozen_cover_cell']!=cover_cell
                or cell['local_model']['parameter_order'][:450]!=metadata[0]['parameter_order']):
            raise ValueError('all eight restrictions must share the same physical family and frozen cover')
        sources[str(path.resolve())]=sha(path);cell_hashes.append(sha(path))
    internal={}
    for site,z in zip(('left','middle','right'),metadata):
        backend=SparseDomain([tuple(g) for g in z['groups']],len(z['parameter_order']))
        def root_support(name):
            m=z['affine_enclosures'][name]
            return SparseAffine(backend,restore(m['c']),{i:restore(v) for i,v in m['a']},arb(fmpq(m['r']))).support()
        row={}
        row['mixed_rate_roots_with_zero_affine_part']=sum(
            restore(z['affine_enclosures'][f'rate/uv/{i}']['c']).is_zero()
            and not z['affine_enclosures'][f'rate/uv/{i}']['a'] for i in range(99))
        for quantity,count in (('eigenline',61),('response',62),('factored_numerator',99)):
            row[quantity+'_mixed_vector_upper']=number(norm([root_support(f'{quantity}/uv/{i}') for i in range(count)]))
        row['normalization_mixed_upper']=number(root_support('normalization/norm_uv'))
        for quantity in ('C','J'):
            values=[root_support(f'descriptor/{quantity}/uv/term{i}') for i in range(16)]
            row[quantity+'_mixed_action_terms']=[number(x) for x in values]
            row[quantity+'_largest_enclosure_term_index']=max(range(16),key=lambda i:values[i])
            row[quantity+'_mixed_sum_upper']=number(root_support(f'descriptor/{quantity}/uv'))
        internal[site]=row
    rL,rT=[arb(fmpq(v)) for v in atlas['radius_exact']]
    backend=SparseDomain([tuple(g) for g in metadata[0]['groups']],len(metadata[0]['parameter_order']))
    models=[ProjectedAffineModels(backend,z) for z in metadata]
    def combine(vectors):return [sum(xs,backend.affine(0)) for xs in zip(*vectors)]
    def subtract(a,b):return [x-y for x,y in zip(a,b)]
    local=subtract(combine([m.mixed(P) for m,P in zip(models,composed_operators(B,A,h))]),
        booked_affine_relaxation(backend,quadratics,rL,rT))
    local_models=[{'c':pair(x.c),'a':[[j,pair(v)] for j,v in sorted(x.coefficients.items())],'r':str(x.r.fmpq())} for x in local]
    maximum=[arb(0),arb(0)];classes={k:[arb(0),arb(0)] for k in ('endpoint_direct','midpoint_state98','midpoint_descriptor','second_incidence','booked_LL_LT')}
    G=arb_mat(74,74,[arb(i==j) for i in range(74) for j in range(74)])
    node_bounds=[]
    for node in range(14,371):
        if node>14:G=matrix(maps[node-1])*G
        e=arb_mat(74,1,[arb(float(x)) for x in axes[node]])
        bounds=[]
        for beta,(P,PG) in enumerate(zip(projected_operator(G*B,e),projected_operator(G,e))):
            operators=composed_operators(P,A,h)
            projected_Q={family:{pair:PG*Q for pair,Q in blocks.items()} for family,blocks in quadratics.items()}
            physical=combine([m.mixed(O) for m,O in zip(models,operators)])
            booking=booked_affine_relaxation(backend,projected_Q,rL,rT)
            output=subtract(physical,booking)
            PA=P*A
            mid=2*h*P/3
            midstate=arb_mat(P.nrows(),99,[mid[i,j] if j<98 else arb(0) for i in range(P.nrows()) for j in range(99)])
            middesc=arb_mat(P.nrows(),99,[mid[i,j] if j==98 else arb(0) for i in range(P.nrows()) for j in range(99)])
            attributed={'endpoint_direct':combine([models[0].mixed(h*P/6),models[2].mixed(h*P/6)]),
                'second_incidence':combine([models[0].mixed(h*h*PA/12),models[2].mixed(-h*h*PA/12)]),
                'midpoint_state98':models[1].mixed(midstate),'midpoint_descriptor':models[1].mixed(middesc),
                'booked_LL_LT':booking}
            value=norm([x.support() for x in output])
            if not value.is_finite():raise ArithmeticError('nonfinite composed output bound')
            bounds.append(value);maximum[beta]=max(maximum[beta],value)
            for key,vector in attributed.items():classes[key][beta]=max(classes[key][beta],norm([x.support() for x in vector]))
        node_bounds.append({'node':node,'projected_bounds':[number(x) for x in bounds]})
        print(json.dumps({'phase':'SIGNED_PROJECTED_CAUSAL_SUPPORT','node':node,'upper':[float(x) for x in bounds]}),flush=True)
    al,at=[arb(float(v)) for v in foundation['fixed_axis_projection_norms_upper']]
    gain=arb(float(foundation['frozen_map_perturbation_gain_upper']))
    error=(gain*(al*maximum[0]+maximum[1])/(1-gain)).upper()
    kappas=[(maximum[0]+al*error)/rL,(maximum[1]+at*error)/rT]
    audit_path=ROOT/'artifacts/flagship_integration/gate7_layer_c_correlation_20260924/first.json'
    audit=json.loads(audit_path.read_bytes());sources[str(audit_path.resolve())]=sha(audit_path)
    baseline=[arb(fmpq(x['exact'])) for x in audit['recovered_linear_only_isolated_kappa_upper']]
    ledger_path=ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json'
    ledger=json.loads(ledger_path.read_bytes());sources[str(ledger_path.resolve())]=sha(ledger_path)
    targets=[min(2*arb(fmpq(row['remaining_normalized_self_map_allowance']['exact'])),arb(fmpq(row['remaining_derivative_row_allowance']['exact']))).lower() for row in ledger['rows']]
    result=dict(algorithm='INTERVAL13_SHARED_EXPRESSION_SIGNED_OUTPUT_RECIPE_WITH_AFFINE_RELAXATION_V1',
        frozen_checkpoint='baf41b96',correlation_audit='f5b6b4b6',interval=13,radius_exact=atlas['radius_exact'],
        expression_recipe={'parents_SHA256':dict(zip(('left','middle','right'),hashes)),
            'eight_history_restriction_SHA256':cell_hashes,
            'parameter_order':metadata[0]['parameter_order'],'groups':metadata[0]['groups'],
            'mixed_rate':'(P*N_uv - nu_uv*(P*N/nu) - nu_u*((P*N_v-nu_v*P*N/nu)/nu) - nu_v*((P*N_u-nu_u*P*N/nu)/nu))/nu',
            'nu_lower_exact':'1','site_operators':['h*P/6+h^2*P*A/12','2*h*P/3','h*P/6-h^2*P*A/12'],
            'P':'e^T*G*B for L, (I-e*e^T)*G*B for T; frozen operand hashes bind G, B and e',
            'signed_booking':'subtract differentiated frozen LL + doubled LT polynomial on the SAME endpoint u/v symbols',
            'aggregation':'one HS residual restricted by eight covering cells; no independent sum of eight copies'},
        isolated_interval_kappa_upper=[number(x) for x in kappas],
        signed_local_remainder_affine_enclosure=local_models,
        numerical_backend='signed matrix projection of numerator c/a/r, shared implicit normalization, explicit affine-tail relaxation',
        previous_audit_kappa_approximate=[float(x) for x in baseline],
        reduction_factor_lower=[{'exact':str((a/b).lower().fmpq()),'approximate':float((a/b).lower())} for a,b in zip(baseline,kappas)],
        class_normalized_bounds_before_map_error={k:[number(x/r) for x,r in zip(v,(rL,rT))] for k,v in classes.items()},
        dominant_source_class_by_output=[max(classes,key=lambda k:classes[k][beta]) for beta in range(2)],
        class_bounds_are_not_a_disjoint_decomposition=True,
        saved_internal_model_diagnostics=internal,
        internal_model_bounds_have_different_units_and_are_not_an_additive_output_decomposition=True,
        frozen_map_error_normalized=[number(al*error/rL),number(at*error/rT)],node_bounds=node_bounds,
        all_357_causal_destination_nodes_included=True,sufficient_framework_targets_lower_exact=[str(x.fmpq()) for x in targets],
        numerical_upper_enclosure_viable=all(k<t for k,t in zip(kappas,targets)),
        exact_operator_recipe_preserves_shared_parent_identity=True,
        full_correlation_preservation_in_numerical_support=False,
        remaining_losses=['imported primal and DF coefficient theta dependence','q-based implicit correction tail dependence','parent nonlinear/bilinear expressions replaced by outward affine tails in this support compiler'],
        classification='REPRESENTATION_LOSS_REMAINS; NO_PHYSICAL_FAILURE_ESTABLISHED',
        full_correlated_Layer_C_certified=False,physical_budget_debit=False,Gate7_closed=False,
        intervals14_to18_evaluated=False,global_kappa_L=None,global_kappa_T=None,source_SHA256=sources)
    if any(sha(Path(p))!=s for p,s in sources.items()):raise ValueError('consumed source changed')
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_bytes(encode(result))
    print(json.dumps({'kappa_upper':[float(x) for x in kappas],'viable':result['numerical_upper_enclosure_viable']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('evidence-root','left','middle','right','cells','out'):p.add_argument('--'+name,type=Path,required=True)
    run(p.parse_args())
