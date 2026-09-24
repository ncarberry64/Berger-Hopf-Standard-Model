"""Read-only frozen-operand attribution and linear correlation recovery.

No action contraction, eigenline solve, response solve or cover calculation
is called. The output explicitly does not certify a full shared Layer-C jet.
"""
import argparse,ast,hashlib,json,sys
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface import shared_hs_output_operator as composition


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def encode(z):return (json.dumps(z,sort_keys=True,indent=2)+'\n').encode()
def ball(v):return arb(fmpq(v[0]))+arb(0,arb(fmpq(v[1])))
def number(x):return dict(exact=str(x.upper().fmpq()),approximate=float(x.upper()))
def norm(v):return sum((abs(x).upper()**2 for x in v),arb(0)).sqrt().upper()
def matrix(a):return arb_mat(a.shape[0],a.shape[1],[arb(float(x)) for x in a.flat])
def rational_array(z,name):
    m,r=z[name+'_mid_q'],z[name+'_rad_q']
    return np.array([ball((str(a),str(b))) for a,b in zip(m.flat,r.flat,strict=True)],dtype=object).reshape(m.shape)


def run(evidence,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512;sources={}
    package=ROOT/'artifacts/flagship_integration/gate7_physical_tube_20260924'
    def read(p):sources[str(p.resolve())]=sha(p);return json.loads(p.read_bytes())
    atlas=read(package/'interval_013/certificate.json');receipt=read(package/'interval_013/reproduction.json')
    if not atlas['complete_physical_tube_cover_certified'] or receipt['certificate_SHA256']!=sha(package/'interval_013/certificate.json'):
        raise ValueError('frozen complete Layer-B atlas required')
    old=read(package/'rate_and_remainder/interval13_inherited_remainder_first.json')
    oldrepeat=package/'rate_and_remainder/interval13_inherited_remainder_repeat.json'
    if oldrepeat.read_bytes()!=(package/'rate_and_remainder/interval13_inherited_remainder_first.json').read_bytes():
        raise ValueError('frozen remainder reproduction failed')
    sources[str(oldrepeat.resolve())]=sha(oldrepeat)
    sites=[];leaves=[]
    for site in ('left','middle','right'):
        p=package/f'rate_and_remainder/interval13_inherited2rate_{site}_first.json'
        z=read(p);r=p.with_name(p.name.replace('_first','_repeat'))
        if z['interval']!=13 or z['site']!=site or z['radius_exact']!=old['radius_exact']:
            raise ValueError('same site and unchanged interval-13 radii required')
        if p.read_bytes()!=r.read_bytes():raise ValueError('frozen rate reproduction failed')
        sources[str(r.resolve())]=sha(r)
        for k,h in z['source_SHA256'].items():
            if sha(Path(k))!=h:raise ValueError('frozen rate input changed: '+k)
        H=[ball(v) for v in z['rate_jets']['uv']];leaves.append(arb_mat(99,1,H))
        sites.append(dict(site=site,actual_normalization_lower_exact=z['descriptor_norm_lower_exact'],
            state98_mixed_upper=number(norm(H[:98])),descriptor_mixed_upper=number(abs(H[98])),
            saved_representation='99 component interval balls for each jet; no shared coefficients',
            unavailable=['unnormalized jets','norm jets','mixed eigenline models','mixed response models','C/J mixed models','shared parameter/monomial map']))
    for k,h in old['source_SHA256'].items():
        if sha(Path(k))!=h:raise ValueError('frozen transport input changed: '+k)
    base=evidence/'artifacts/flagship_integration'
    def operand(name):
        p=base/name;sources[str(p.resolve())]=sha(p)
        if str(p.resolve()) in old['source_SHA256'] and old['source_SHA256'][str(p.resolve())]!=sha(p):raise ValueError('wrong frozen operand')
        return p
    dp=operand('.coupled_midpoint_uniform_df_work/interval_013/derivative.npz')
    with np.load(dp,allow_pickle=False) as z:a=rational_array(z,'derivative');A=arb_mat(99,99,list(a.flat))
    with np.load(operand('BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'),allow_pickle=False) as z:
        h=arb(float(z['collocation_arc_parameters'][14]-z['collocation_arc_parameters'][13]))
    with np.load(operand('BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz'),allow_pickle=False) as z:tangent=z['endpoint_physical_tangent_action'][14]
    with np.load(operand('BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz'),allow_pickle=False) as z:right=matrix(z['reduced_right_Newton_blocks'][13])
    action_path=ROOT/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
    tree=ast.parse(action_path.read_text());scale=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TEST_DESCRIPTOR_SCALE' for t in n.targets))
    test=np.zeros((74,99));test[:73,:98]=tangent.T;test[73,98]=scale;B=right.solve(matrix(test))
    with np.load(operand('BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz'),allow_pickle=False) as z:maps=z['causal_maps_center']
    ap=evidence/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz';sources[str(ap.resolve())]=sha(ap)
    with np.load(ap,allow_pickle=False) as z:axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    foundation=read(operand('BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE.json'))
    if not foundation['validation_passed'] or foundation['coverage']!=dict(intervals=370,nodes=371,complete=True):
        raise ValueError('complete causal arithmetic authority required')
    for name in ('BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz',
                 'BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz',
                 'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz',
                 'BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz'):
        p=base/name
        if sha(p)!=foundation['inputs'][p.relative_to(evidence).as_posix()]:
            raise ValueError('operand not bound to frozen causal lemma')
    ah=lambda a:hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest().upper()
    if ah(axes)!=foundation['axes_SHA256'] or ah(maps)!=foundation['causal_maps_SHA256']:raise ValueError('map/axis identity mismatch')
    quadratics=[]
    for family in ('LL','LT'):
        blocks=[]
        for pair in ('00','01','10','11'):
            p=operand(f'.direct_physical_quadratic_source_work/interval_013/{family}_{pair}.npz')
            with np.load(p,allow_pickle=False) as z:Q=rational_array(z,'Q');blocks.append(arb_mat(*Q.shape,list(Q.flat)))
        quadratics.append(blocks)
    rL,rT=[arb(fmpq(v)) for v in old['radius_exact']]
    G=arb_mat(74,74,[arb(i==j) for i in range(74) for j in range(74)])
    best=[arb(0),arb(0)];dominance={k:[arb(0),arb(0)] for k in ('endpoint_direct','midpoint_state98','midpoint_descriptor','second_incidence','booked_LL_LT')}
    old_dominance={k:[arb(0),arb(0)] for k in dominance}
    midstate=arb_mat(99,1,leaves[1].entries()[:98]+[arb(0)])
    middesc=arb_mat(99,1,[arb(0)]*98+[leaves[1][98,0]])
    old_classes=dict(endpoint_direct=B*(h*(leaves[0]+leaves[2])/6),
        midpoint_state98=B*(2*h*midstate/3),midpoint_descriptor=B*(2*h*middesc/3),
        second_incidence=B*(2*h*(A*(h*(leaves[0]-leaves[2])/8))/3))
    booked_rows=[arb(0)]*74
    for family,blocks in enumerate(quadratics):
        for Q in blocks:
            for i in range(74):
                amount=2*rL*rL*abs(Q[i,0]).upper() if family==0 else 4*rL*rT*norm([Q[i,j] for j in range(Q.ncols())])
                booked_rows[i]+=arb(0,amount.upper())
    old_classes['booked_LL_LT']=arb_mat(74,1,booked_rows)
    for node in range(14,371):
        if node>14:G=matrix(maps[node-1])*G
        e=arb_mat(74,1,[arb(float(v)) for v in axes[node]])
        for key,local in old_classes.items():
            value=G*local;longitudinal=e.transpose()*value
            bounds=(norm(longitudinal.entries()),norm((value-e*longitudinal).entries()))
            old_dominance[key]=[max(a,b) for a,b in zip(old_dominance[key],bounds)]
        for beta,(P,PG) in enumerate(zip(composition.projected_operator(G*B,e),composition.projected_operator(G,e))):
            H=composition.evaluate_same_leaves(composition.composed_operators(P,A,h),leaves)
            booked=arb(0)
            LL,LT=quadratics
            for Q in (2*LL[0],LL[1]+LL[2],LL[1]+LL[2],2*LL[3]):booked+=rL*rL*norm((PG*Q).entries())
            for Q in LT:booked+=4*rL*rT*norm((PG*Q).entries())
            best[beta]=max(best[beta],(norm(H.entries())+booked).upper())
            classes=dict(endpoint_direct=h*P*(leaves[0]+leaves[2])/6,
                midpoint_state98=2*h*P*midstate/3,midpoint_descriptor=2*h*P*middesc/3,
                second_incidence=h*h*P*A*(leaves[0]-leaves[2])/12)
            for key,value in classes.items():dominance[key][beta]=max(dominance[key][beta],norm(value.entries()))
            dominance['booked_LL_LT'][beta]=max(dominance['booked_LL_LT'][beta],booked)
    al,at=[arb(float(v)) for v in foundation['fixed_axis_projection_norms_upper']];gain=arb(float(foundation['frozen_map_perturbation_gain_upper']))
    error=(gain*(al*best[0]+best[1])/(1-gain)).upper()
    kappas=[(best[0]+al*error)/rL,(best[1]+at*error)/rT]
    oldk=[arb(fmpq(v['exact'])) for v in old['isolated_interval_kappa_upper']]
    for p in (action_path,Path(__file__),Path(composition.__file__)):
        sources[str(p.resolve())]=sha(p)
    result=dict(algorithm='FROZEN_INTERVAL13_LINEAR_CORRELATION_RECOVERY_AND_AUDIT_V1',
        frozen_checkpoint='baf41b96',interval=13,Layer_B_cover_reused=True,new_action_evaluations=0,
        eigenline_or_response_solves_rerun=False,cover_rerun=False,physical_budget_debit=False,
        first_explicit_direction_loss='derive_n12_gate7_inherited_site_rate_jet.py: direction=[arb(0,direction_support(...)) ...]',
        earlier_inherited_state_loss='Uniform endpoint value/DF and raw_domain are balls without a common physical theta model.',
        sites=sites,old_isolated_kappa_upper=old['isolated_interval_kappa_upper'],
        recovered_linear_only_isolated_kappa_upper=[number(v) for v in kappas],
        improvement_factor_lower_exact=[str((a/b).lower().fmpq()) for a,b in zip(oldk,kappas)],
        improvement_compares_upper_enclosures_not_physical_magnitudes=True,
        old_class_normalized_bounds_before_map_error={k:[number(v/r) for v,r in zip(values,(rL,rT))] for k,values in old_dominance.items()},
        class_normalized_bounds_before_map_error={k:[number(v/r) for v,r in zip(values,(rL,rT))] for k,values in dominance.items()},
        class_bounds_are_not_a_disjoint_decomposition_of_kappa=True,
        frozen_map_error_normalized=[number(al*error/rL),number(at*error/rT)],
        normalization_mixed_eigenline_mixed_response_internal_attribution='Unavailable: intermediate graphs/models were not serialized in baf41b96.',
        cellwise_absolute_sum_present_in_old_code=False,coverage_cells_are_not_additive_HS_residuals=True,
        same_Hessian_leaf_in_direct_and_incidence_terms_combined_before_support=True,
        output_projection_and_causal_matrices_composed_before_leaf_support=True,
        full_shared_state_direction_normalization_model_available=False,
        full_Layer_C_certificate_produced=False,classification='SIGNED_CORRELATION_LOST_IN_LAYER_C_REMAINDER_ASSEMBLY',
        surviving_bounds_are_not_irreducible_action_term_lower_bounds=True,global_kappa_L=None,global_kappa_T=None,
        intervals14_to18_evaluated=False,Gate7_closed=False,source_SHA256=sources)
    if any(sha(Path(p))!=digest for p,digest in sources.items()):raise ValueError('consumed source changed')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(encode(result))
    print(json.dumps(dict(old=[float(v) for v in oldk],linear_recovery=[float(v) for v in kappas],dominance={k:[float(v/r) for v,r in zip(vs,(rL,rT))] for k,vs in dominance.items()})))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.out.resolve())
