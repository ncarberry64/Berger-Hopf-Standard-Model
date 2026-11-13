"""Second magnetic mean on the evaluated moving226 birth action.

The actual endpoint coefficients reconstitute first velocities and Gauss
variables from the common canonical x/p.  The child inherited connection
is differentiated in both arms before applying the six-port action saddle.
Numerical row quotient and finite-difference diagnostics select no state.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import cho_factor, cho_solve

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_finite_geometric_trace_endpoint import pair_master_chart
from .muon_corrected_profile_magnetic_response import corrected_profile_reached_sample, corrected_wall_reference
from .muon_corrected_profile_mean_load import corrected_profile_mean_load, corrected_background_geometry_jets
from .muon_parent_maxwell_source_mean_forcing import maxwell_mean_cotangents, higgs_mean_cotangents, _second_mean
from .muon_current_source_motion_cubic import maxwell_cross_hessian, higgs_cross_hessian
from .muon_parent_retarded_hypercharge import regular_radial_basis, WALL
from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from .muon_electromagnetic_soft_magnetic_source import uniform_magnetic_source_first_jets
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP, VOLUME
from .muon_parent_maxwell_full_weak import M
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_magnetic_birth_ward_mean import named_ward_mean_application
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order, _symmetric_power
from .muon_birth_phase_continuation import _compressed_npz

BASE = 'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'
RESPONSE = 'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'


def endpoint_first_fields(raw, representation, angular, canonical_state, *,
        electric_charge, nu_squared_action, initial_pair=None, reference_pair=None):
    """Actual endpoint constitutive inverse; canonical x/p are never copied rates."""
    raw=np.asarray(raw,float);state=np.asarray(canonical_state,float)
    if raw.shape!=(268,) or state.shape!=(800,8):
        raise ValueError('actual raw268 and all eight common canonical columns required')
    source=uniform_magnetic_source_first_jets(raw,angular,electric_charge=electric_charge)
    kw=dict(coordinate_time=0.,nu_squared_action=nu_squared_action,
            initial_pair=initial_pair,reference_pair=reference_pair)
    sample=corrected_profile_reached_sample(raw,representation,angular,
        source['connection_source'],source['connection_source_rate'],**kw)
    reduced=sample['reduced'];x=state[:400];p=state[400:];b=np.eye(8)
    z=np.r_[x,b]
    v=cho_solve(cho_factor(reduced['M'][:400,:400]),
        p-reduced['B'][:400,:400].T@x-reduced['B'][400:,:400].T@b)
    zdot=np.r_[v,np.zeros((8,8))]
    at=reduced['At_value_map']@z+reduced['At_velocity_map']@zdot
    fullx=np.r_[at,z];fullv=np.r_[np.zeros_like(at),zdot]
    mass,mixed,stiffness=sample['raw_forms']
    momentum=mass@fullv+mixed.T@fullx
    gauss=(stiffness@fullx+mixed@fullv)[:80]
    interior=np.r_[at,x[:320]].T[:3].reshape(3,5,4,20)
    rate=np.r_[np.zeros_like(at),v[:320]].T[:3].reshape(3,5,4,20)
    wall=source['connection_source'].T[:3].reshape(3,5,4,20)
    wallrate=source['connection_source_rate'].T[:3].reshape(3,5,4,20)
    basis,dr=regular_radial_basis(representation['rho'],1)
    shape=lambda a:a[:,None,None,None,None]
    fields=dict(first_gauge=shape(basis[:,0])*interior+shape(basis[:,1])*wall,
        first_gauge_rate=shape(basis[:,0])*rate+shape(basis[:,1])*wallrate,
        first_gauge_radial=shape(dr[:,0])*interior+shape(dr[:,1])*wall,
        first_wall_gauge=wall,first_H=x[320:].T[:3].reshape(3,4,20),
        first_H_rate=v[320:].T[:3].reshape(3,4,20))
    return dict(fields=fields,source=source,sample=sample,velocity=v,A_tau=at,
        canonical_state=state.copy(),Gauss_residual=gauss,
        Legendre_residual=momentum[80:480]-p,
        algebraic_At_rate_used=False,source_profile=1.,source_profile_rate=0.)


def joint_mean_cotangent(raw_pair, reference_pair, representation, angular, fields, sources,
                         *,nu_squared_action):
    """Both arm partials plus the child's inherited-parent cotangent, once."""
    raw=np.asarray(raw_pair,float);rep=representation;E=angular['derivative_matrices']
    results=[]
    for arm in range(2):
        kw=dict(initial_pair=raw,reference_pair=reference_pair) if arm else {}
        results.append(corrected_profile_mean_load(raw[arm],rep,angular,
            {k:sources[arm][k] for k in ('Q_first_jet','Qdot_first_jet')},1.,0.,
            **fields[arm],coordinate_time=0.,nu_squared_action=nu_squared_action,**kw))
    child=results[1];f=fields[1]
    background=corrected_background_geometry_jets(raw[1],rep,coordinate_time=0.,
        initial_pair=raw,reference_pair=reference_pair)
    ref=background['reference'];extra=np.zeros((268,3,3))
    for j in range(len(rep['rho'])):
        a,at,ar=(ref[k][j]for k in ('background_values','background_time_derivatives','background_radial_derivatives'))
        r=maxwell_mean_cotangents(a,at,ar,f['first_gauge'][j],f['first_gauge_rate'][j],
            f['first_gauge_radial'][j],E,ref['positive_two_form_densities'][j])
        extra[:100]+=MAXWELL_TO_CAP*rep['radial_quadrature'][j]*np.einsum('kc,kab->cab',
            child['inherited_parent_geometry_first_jet'][j],r['mechanical_lambda_cotangents'])
    wallrep=dict(rep,rho=np.array([WALL]),radial_quadrature=np.ones(1),
        gauge_basis=np.moveaxis(rep['wall_trace_map'],-1,0)[None,:,None],
        gauge_radial_basis=np.moveaxis(rep['wall_radial_derivative_map'],-1,0)[None,:,None])
    walljets=corrected_background_geometry_jets(raw[1],wallrep,coordinate_time=0.,
        initial_pair=raw,reference_pair=reference_pair)
    w=intrinsic_m4_weight_jet(12,raw[1,:37],raw[1,37:74],raw[1,74:98],
        source_value=raw[1,98],source_rate=raw[1,99])
    scalar=higgs_mean_cotangents(raw[1,260:264],raw[1,264:],walljets['reference']['background_values'][0],
        f['first_H'],f['first_H_rate'],f['first_wall_gauge'],E,
        np.array([w[k].value for k in ('wT','wS','wV')]),
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
    extra[:100]+=walljets['inherited_parent_geometry_first_jet'][0,0,:,None,None]*scalar['mechanical_lambda_cotangent']/VOLUME**2
    fixed=np.array([r['fixed_field_raw_mean_cotangent']for r in results]);fixed[0]+=extra
    motion=np.array([r['source_motion_cotangent']for r in results])
    return dict(raw_mean=fixed+motion,fixed_raw_mean=fixed,source_motion_raw_mean=motion,
        incoming_only_fixed_raw_mean=results[0]['fixed_field_raw_mean_cotangent'],
        inherited_parent_raw_mean=extra,arm_applications=results)


def action_energy_contacts(raw_pair, reference_pair, representation, angular, fields, joint):
    """Literal coefficient energy, first-rate terms and reference-clock work.

    Fixed-action E_AB=v.g_v+L_AB[uA,V_B]+L_AB[uB,V_A]-L_AB.
    Source-chart velocity work remains separately exported.  The child's
    physical clock subtracts the retained reference electric work once.
    """
    raw=np.asarray(raw_pair);rep=representation;E=angular['derivative_matrices'];S=[];T=[];work=np.zeros((3,3))
    for arm in range(2):
        f=fields[arm];kw=dict(initial_pair=raw,reference_pair=reference_pair)if arm else {}
        bg=corrected_background_geometry_jets(raw[arm],rep,coordinate_time=0.,**kw)['reference']
        paired=np.zeros((3,3));rate=np.zeros((3,3))
        for j in range(len(rep['rho'])):
            a,at,ar=(bg[k][j]for k in ('background_values','background_time_derivatives','background_radial_derivatives'))
            u,ut,ur=(f[k][j]for k in ('first_gauge','first_gauge_rate','first_gauge_radial'))
            d=bg['positive_two_form_densities'][j];fac=MAXWELL_TO_CAP*rep['radial_quadrature'][j];zero=np.zeros_like(u)
            paired+=fac*maxwell_cross_hessian(a,at,ar,u,ut,ur,u,ut,ur,E,d)
            cross=maxwell_cross_hessian(a,at,ar,u,ut,ur,zero,ut,zero,E,d)
            rate+=fac*(cross+cross.T)
            if arm:
                uv=_second_mean(u,u)
                work+=fac*representation['reference_time_profile'][j]*d[0]*np.einsum('fc,abfc->ab',M,uv[1]-d[4]*uv[2])
        wall=corrected_wall_reference(raw[arm],rep,coordinate_time=0.,**kw)['background_values'][0]
        w=intrinsic_m4_weight_jet(12,raw[arm,:37],raw[arm,37:74],raw[arm,74:98],source_value=raw[arm,98],source_rate=raw[arm,99])
        weights=np.array([w[k].value for k in ('wT','wS','wV')]);h,ht,aw=(f[k]for k in ('first_H','first_H_rate','first_wall_gauge'))
        args=dict(lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=rep['endpoint_action_parameters']['nu_squared_action'])
        paired+=higgs_cross_hessian(raw[arm,260:264],raw[arm,264:],wall,h,ht,aw,h,ht,aw,E,weights,**args)/VOLUME**2
        cross=higgs_cross_hessian(raw[arm,260:264],raw[arm,264:],wall,h,ht,aw,np.zeros_like(h),ht,np.zeros_like(aw),E,weights,**args)/VOLUME**2
        rate+=cross+cross.T;S.append(paired);T.append(rate)
    chart=pair_master_chart(rep);R=chart['lift'];P=chart['one_lift'];vi=chart['v_indices'];n=chart['dynamic_count']
    eta=R.T@raw.ravel();g=np.einsum('ij,iab->jab',R,joint['fixed_raw_mean'].reshape(536,3,3))
    gp=np.einsum('ij,iab->jab',P,joint['incoming_only_fixed_raw_mean'])
    Egraph=np.einsum('i,iab->ab',eta[vi],g[vi])+sum(T)-sum(S)
    Ep=np.einsum('i,iab->ab',eta[n:2*n],gp[n:2*n])+T[0]-S[0]
    motion=np.einsum('ij,iab->jab',R,joint['source_motion_raw_mean'].reshape(536,3,3))
    mp=np.einsum('ij,iab->jab',P,joint['source_motion_raw_mean'][0])
    Wgraph=np.einsum('i,iab->ab',eta[vi],motion[vi]);Wp=np.einsum('i,iab->ab',eta[n:2*n],mp[n:2*n])
    return dict(fixed_energy_source=np.array([Ep,Egraph-Ep-work]),
        source_motion_velocity_work=np.array([Wp,Wgraph-Wp]),reference_clock_work_source=work,
        arm_paired_action=np.array(S),arm_first_velocity_contacts=np.array(T))


def six_port_mean_source(base_arrays, chart, paired_gradient, oriented_cotangent, directional_gradient,
                         *,difference_step,coordinate_weights):
    """Dg through the actual zero-Lyy constraint/velocity saddle, not Legendre D."""
    K=base_arrays['saddle'];ell=base_arrays['constrained_trace_lift'];theta=base_arrays['temporal_face_cotangent']
    solution=base_arrays['saddle_solution'];n=len(ell);dim=chart['master_count']*2
    scale=1/np.sqrt(np.max(abs(K),axis=1));rhs=np.r_[theta,np.zeros(len(K)-n)]
    adjoint=scale*np.linalg.solve(scale[:,None]*K*scale[None,:],scale*rhs)
    av=np.zeros(dim);ay=np.zeros(dim);av[chart['v_indices']]=adjoint[:n]
    av[chart['y_indices']]=ay[chart['y_indices']]=adjoint[n+6:]
    b=np.zeros((dim,6));by=np.zeros_like(b);b[chart['v_indices']]=ell
    b[chart['y_indices']]=by[chart['y_indices']]=solution[n+6:]
    def dg(d):
        mag=float(np.max(abs(coordinate_weights*d)))
        return np.zeros_like(paired_gradient)if mag==0 else mag*directional_gradient(d/mag,difference_step)
    gav,gay=dg(av),dg(ay)
    contact=np.einsum('iab,ij->jab',gav,b)-np.einsum('iab,ij->jab',gay,by)
    direct=np.einsum('ij,iab->jab',ell,oriented_cotangent)
    common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    return dict(common_source=np.einsum('ij,iab->jab',common,direct-contact),
        six_source=direct-contact,direct_velocity_contact=direct,saddle_contact=contact,
        adjoint=adjoint,adjoint_residual=K@adjoint-rhs,adjoint_direction=av,
        algebraic_adjoint_direction=ay,directional_gradient_adjoint=gav,
        directional_gradient_algebraic=gay,difference_step=difference_step,
        exact_stored_saddle_Lyy=False)


def moving_birth_ward_relations(raw_pair,base_arrays,representation,chart,groups):
    """Named central relations for the moving226 row order, with off-shell DL.F."""
    raw=np.asarray(raw_pair);rep=representation;c=chart['coordinates'];labels=rep['gauge_labels']
    theta=enriched_central_profiles(rep);L=np.zeros((2,226));contact=np.zeros((2,504))
    ids=lambda k:np.asarray(groups[k]['indices'],int)
    for j,i in enumerate(c['At_indices']):
        label=labels[i]
        if label['internal']==3:
            L[:,ids('incoming_constraints')[24+j]]=theta['theta_coefficients'][label['radial']]
            L[:,ids('child_constraints')[24+j]]=-theta['theta_coefficients'][label['radial']]
    for j,i in enumerate(c['dynamic_gauge_indices']):
        label=labels[i]
        if label['field']=='A_rho'and label['internal']==3:
            L[:,ids('gauge_temporal_dual')[j]]=theta['radial_derivative_coefficients'][label['radial']]
    G=higgs_u2_real_representation()['real_generators'][3];g=base_arrays['graph_raw_gradient'];H=base_arrays['graph_raw_hessian'];R=chart['lift']
    ht=ids('Higgs_trace');hp=ids('Higgs_temporal_dual');pchild=g[532:536]
    L[:,ht]=G.T@pchild;L[:,hp]=-G@raw[0,260:264]
    rawcontact=np.zeros((2,536));res=base_arrays['updated_residual']
    rawcontact[:,260:264]=-G.T@res[hp]
    rawcontact+=(G@res[ht])@H[532:536]
    contact=rawcontact@R
    return dict(row_relations=L,off_shell_coefficient_contact=contact,
        base_relation=L@res,jacobian_relation=L@base_arrays['updated_jacobian']+contact,
        equation='theta.(GaussP-GaussC)+theta_r.jump(pAr)-(G_Y H_P).jump(pH)+(G_Y.T pH_C).trace(H)=0')


def corrected_birth_mean_application(*,repository=ROOT,difference_step=2e-5,certify=True,progress=None):
    root=Path(repository);endpoint=load_finite_normal_endpoint(BASE,side='incoming',repository=root)
    refs=dict(endpoint['input_hashes']);folder=endpoint['source'];md=endpoint['receipt'];rep=endpoint['representation']
    with np.load(folder/'application.npz',allow_pickle=False)as a:base={k:a[k].copy()for k in a.files}
    raw=base['updated_raw_pair'];reference=base['reference_raw_pair'];chart=pair_master_chart(rep);R=chart['lift'];P=chart['one_lift']
    rep['endpoint_action_parameters']=dict(md['action_parameters']);rep['reference_time_profile']=base['reference_time_profile']
    for path in (NORMALIZATION_SOURCE,'artifacts/muon_calibrated_pauli_20261009/inputs.json'):
        refs[path]=sha256((root/path).read_bytes()).hexdigest()
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False)as a:weights=a['state_weights'].copy();normalization=a['normalization_coordinates'].copy()
    config=json.loads((root/'artifacts/muon_calibrated_pauli_20261009/inputs.json').read_bytes());charge=np.sqrt(4*np.pi*config['alpha_consumer']['value'])
    response=root/RESPONSE;rmd=json.loads((response/'result.json').read_bytes());refs.update(rmd['input_hashes'])
    refs[RESPONSE+'/result.json']=sha256((response/'result.json').read_bytes()).hexdigest();states=[]
    for side in ('incoming','outgoing'):
        path=response/(side+'_phase.npz');expected=rmd['array_archives'][path.name]['sha256']
        if sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('common canonical first fields changed')
        refs[path.relative_to(root).as_posix()]=expected
        with np.load(path,allow_pickle=False)as a:states.append(a['state'][-1 if side=='incoming'else 0].copy())
    if not np.array_equal(*states):raise ValueError('first canonical common birth state must be identical')
    angular=retained_full_q_angular_space(root);first=[]
    for arm in range(2):
        kw=dict(initial_pair=raw,reference_pair=reference)if arm else {}
        first.append(endpoint_first_fields(raw[arm],rep,angular,states[arm],electric_charge=charge,
            nu_squared_action=md['action_parameters']['nu_squared_action'],**kw))
        if progress:progress(dict(stage='true_endpoint_constitutive_first',side=arm,
            Gauss_max=float(np.max(abs(first[-1]['Gauss_residual']))),Legendre_max=float(np.max(abs(first[-1]['Legendre_residual'])))))
    fields=[f['fields']for f in first];sources=[f['source']for f in first]
    joint=joint_mean_cotangent(raw,reference,rep,angular,fields,sources,nu_squared_action=md['action_parameters']['nu_squared_action'])
    energies=action_energy_contacts(raw,reference,rep,angular,fields,joint)
    g=np.einsum('ij,iab->jab',R,joint['raw_mean'].reshape(536,3,3));gp=np.einsum('ij,iab->jab',P,
        joint['incoming_only_fixed_raw_mean']+joint['source_motion_raw_mean'][0])
    n=chart['dynamic_count'];theta=-g[chart['v_indices']].copy();theta[:n]+=2*gp[n:2*n]
    basis,dr=regular_radial_basis(rep['rho'],1);shape=lambda a:a[:,None,None,None,None]
    def callback(eta):
        changed=(R@eta).reshape(2,268);fs=[];ss=[]
        for arm in range(2):
            s=uniform_magnetic_source_first_jets(changed[arm],angular,electric_charge=charge);ss.append(s)
            dq=(s['connection_source']-sources[arm]['connection_source']).T[:3].reshape(3,5,4,20)
            dqt=(s['connection_source_rate']-sources[arm]['connection_source_rate']).T[:3].reshape(dq.shape)
            f=fields[arm];fs.append(dict(f,first_gauge=f['first_gauge']+shape(basis[:,1])*dq,
                first_gauge_rate=f['first_gauge_rate']+shape(basis[:,1])*dqt,
                first_gauge_radial=f['first_gauge_radial']+shape(dr[:,1])*dq,
                first_wall_gauge=f['first_wall_gauge']+dq))
        j=joint_mean_cotangent(changed,reference,rep,angular,fs,ss,nu_squared_action=md['action_parameters']['nu_squared_action'])
        return np.einsum('ij,iab->jab',R,j['raw_mean'].reshape(536,3,3))
    eta=R.T@raw.ravel()
    def directional(d,h):return(callback(eta+h*d)-callback(eta-h*d))/(2*h)
    contacts=[]
    for h in (difference_step,difference_step/2):
        contacts.append(six_port_mean_source(base,chart,g,theta,directional,difference_step=h,coordinate_weights=base['coordinate_weights']))
        if progress:progress(dict(stage='moving_six_port_mean',step=h,source_norm=float(np.linalg.norm(contacts[-1]['common_source']))))
    source=np.zeros((226,3,3));ids=lambda k:np.asarray(md['groups'][k]['indices'],int)
    scale=np.r_[1/weights[74:98],np.ones(chart['algebraic_count']-24)]
    for arm,key in enumerate(('incoming_constraints','child_constraints')):
        source[ids(key)]=scale[:,None,None]*g[chart['y_indices'][arm*40:(arm+1)*40]]
    energy=energies['fixed_energy_source']+energies['source_motion_velocity_work']
    source[ids('incoming_energy')]=energy[0];source[ids('child_energy')]=energy[1]
    pos=np.arange(38,n-4);source[ids('gauge_temporal_dual')]=theta[pos]+theta[n+pos]
    pos=np.arange(n-4,n);source[ids('Higgs_temporal_dual')]=theta[pos]+theta[n+pos]
    B=_attachment_jacobian_at_order(12,normalization);norm=_symmetric_power(B@B.T,.5)
    source[ids('common_attachment_temporal_dual')]=np.einsum('ij,jab->iab',norm,contacts[-1]['common_source'][:2])
    source[ids('common_normal_temporal_dual')]=contacts[-1]['common_source'][2]
    ward=moving_birth_ward_relations(raw,base,rep,chart,md['groups'])
    solved=named_ward_mean_application(base['updated_jacobian'],source,base['row_scale'],base['coordinate_weights'],
        ward['row_relations'],certify=certify)
    correction=np.einsum('ij,jab->iab',R,solved['correction']).reshape(2,268,3,3)
    if progress:progress(dict(stage='original_moving226_mean_solve',
        original_residual_max=float(np.max(abs(solved['original_residual']))),
        scaled_residual_max=float(np.max(abs(solved['original_scaled_residual']))),
        source_compatibility_max=float(np.max(abs(solved['named_source_compatibility'])))))
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise RuntimeError('consumed owner changed: '+p)
    return dict(base=base,first=first,joint=joint,energies=energies,contacts=contacts,ward=ward,solve=solved,
        source=source,raw_mean_correction=correction,paired_master_source=g,oriented_canonical_source=theta,
        step_halving_difference=contacts[-1]['common_source']-contacts[0]['common_source'],input_hashes=refs)


def materialize_corrected_birth_mean(output,*,repository=ROOT,difference_step=2e-5,certify=True):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve completed mean applications')
    progress=lambda x:print(json.dumps(x,sort_keys=True),flush=True)
    a=corrected_birth_mean_application(repository=root,difference_step=difference_step,certify=certify,progress=progress)
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
    for key in ('joint','energies','ward','solve','base'):
        arrays.update({key+'_'+k:v for k,v in a[key].items()if isinstance(v,np.ndarray)})
    for i,c in enumerate(a['contacts']):arrays.update({'six_port_'+str(i)+'_'+k:v for k,v in c.items()if isinstance(v,np.ndarray)})
    for arm,side in enumerate(('incoming','outgoing')):
        f=a['first'][arm];arrays.update({side+'_'+k:v for k,v in f.items()if isinstance(v,np.ndarray)})
        arrays.update({side+'_'+k:v for k,v in f['fields'].items()})
    refs=dict(a['input_hashes'])
    for name in ('muon_corrected_birth_mean','muon_corrected_profile_mean_load','muon_corrected_profile_magnetic_response',
        'muon_magnetic_birth_ward_mean','muon_birth_finite_geometric_trace_endpoint','muon_current_source_motion_cubic'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_CORRECTED_TRUE_MOVING226_BIRTH_SECOND_MEAN',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        first_constitutive_checks=[dict(side=s,Gauss_max=float(np.max(abs(f['Gauss_residual']))),
            Legendre_max=float(np.max(abs(f['Legendre_residual']))))for s,f in zip(('incoming','outgoing'),a['first'])],
        source_norm=float(np.linalg.norm(a['source'])),inherited_parent_source_norm=float(np.linalg.norm(a['joint']['inherited_parent_raw_mean'])),
        original_row_residual_max=float(np.max(abs(a['solve']['original_residual']))),
        original_scaled_row_residual_max=float(np.max(abs(a['solve']['original_scaled_residual']))),
        named_source_compatibility_max=float(np.max(abs(a['solve']['named_source_compatibility']))),
        base_Ward_identity_max=float(np.max(abs(a['ward']['base_relation']))),
        differentiated_base_Ward_identity_max=float(np.max(abs(a['ward']['jacobian_relation']))),
        six_port_step_halving_difference_norm=float(np.linalg.norm(a['step_halving_difference'])),
        raw_mean_norm=float(np.linalg.norm(a['raw_mean_correction'])),
        row_factor_condition_number=a['solve']['row_factor_condition_number'],
        stored_action_arithmetic_certificate=a['solve']['stored_action_arithmetic_certificate'],
        active_magnetic_axes=[0,1,2],row_count=226,independent_named_row_count=224,
        inherited_parent_connection_motion_count=1,canonical_g_v_count=1,real_scalar_pairing_count=1,
        source_energy_scope='fixed action plus separate chart velocity work; anchored reference electric work subtracted once',
        saddle_scope='retained zero-Lyy constrained-velocity six-port application; not true-Lyy Legendre quotient',
        numerical_particular_selection='minimum coefficient-weight norm in named row quotient; full null space and original rows exported',
        scope='actual true endpoint constitutive fields and joint moving action; finite angular/radial source restriction, reference chart held fixed',
        physical_E0_or_full_angular_birth_mean_selected=False,physical_formation_or_native_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='stored-row arithmetic certificate excludes action rounding, Dg step-halving error and angular/temporal/physical-domain completion')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md
