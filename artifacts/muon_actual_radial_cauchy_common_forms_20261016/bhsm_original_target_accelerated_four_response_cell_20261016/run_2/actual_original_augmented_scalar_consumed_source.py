"""Literal augmented scalar-action source/domain directional applications.

S_aug is the original full two-arm action plus the Maxwell bulk difference
L(A+Tz,d)-L(A,d). The fixed-material-rho phi/Legendre profiles vanish with
their radial first derivatives at both spatial faces. The entire original
scalar/Higgs/metric action and inherited parent profile remain present.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys
import time

os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'


def augmented_maps(current, completion):
    """Return explicit old504 and profile-coordinate injections."""
    import numpy as np
    oldchild=completion['current288_to_augmented'][current['original_order_to_augmented'][:252]]
    profiles=[]
    old=completion['current288_to_augmented']
    profiles.extend(old[np.r_[current['complement_position_indices'],
        current['complement_rate_indices'],current['complement_Gauss_indices']]])
    degrees=len(completion['profile_degrees'])
    for k in range(degrees):
        profiles.extend(np.r_[completion['added_position_indices'][16*k:16*(k+1)],
            completion['added_rate_indices'][16*k:16*(k+1)],
            completion['added_Gauss_indices'][4*k:4*(k+1)]])
    extra=np.asarray(profiles,int)
    if sorted(np.r_[oldchild,extra].tolist())!=list(range(len(completion['Hessian']))):
        raise ValueError('complete explicit original/profile coordinate direct sum required')
    point=np.concatenate((current['profile_lift'],completion['added_point_lift']),axis=2)
    return dict(old504_to_full=np.r_[np.arange(252),252+oldchild],
        extra_coordinates_to_full=252+extra,extra_point_lift=point,
        full_dimension=252+len(completion['Hessian']),child_original252_to_augmented=oldchild)


def _density_jets(A,At,Ar,density):
    """Independent literal density/shift partials of the original Maxwell scalar."""
    import numpy as np
    from bhsm.interface.muon_baton_zoo_original_validation import _commutator
    n=len(A);e,r,d,k,beta=density.T
    X=At[:,1]-Ar[:,0]+_commutator(A[:,0],A[:,1])
    T=At[:,2:]+_commutator(A[:,0,None],A[:,2:])
    R=Ar[:,2:]+_commutator(A[:,1,None],A[:,2:])
    B=2*A[:,2:].copy()
    for i,j,l in ((0,1,2),(1,2,0),(2,0,1)):
        B[:,i]+=_commutator(A[:,j+2],A[:,l+2])
    Y=T-beta[:,None,None]*R
    norm=lambda x:np.sum(x*x,axis=tuple(range(1,x.ndim)))
    yr=np.sum(Y*R,axis=(1,2));rr=norm(R)
    g=np.c_[norm(Y)/2,-rr/2,-norm(B)/2,norm(X)/2,-e*yr]
    H=np.zeros((n,5,5),complex)
    H[:,0,4]=H[:,4,0]=-yr;H[:,4,4]=e*rr
    return g,H


def _field_density_cross(A,At,Ar,density):
    import numpy as np
    from bhsm.interface.muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
    result=np.empty((len(A),60,5),complex)
    for k in range(4):
        unit=np.zeros_like(density);unit[:,k]=1;unit[:,4]=density[:,4]
        result[:,:,k]=analytic_constant_maxwell_batch(A,At,Ar,unit)['gradient']
    p,m=density.copy(),density.copy();p[:,4]+=1;m[:,4]-=1
    result[:,:,4]=(analytic_constant_maxwell_batch(A,At,Ar,p)['gradient']-
        analytic_constant_maxwell_batch(A,At,Ar,m)['gradient'])/2
    return result


def augmented_scalar_action(raw_pair, reference_pair, extra_coefficients,
        representation, maps, *, action_parameters):
    """Evaluate SAME action value/gradient/Hessian on all augmented variables.

    Full profile J/J2 and metric density D/D2 contacts are retained before
    any contraction. There is no scalar wall increment because the added
    fields have exact zero wall trace in the supplied material-rho chart.
    """
    import numpy as np
    from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
    from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows
    from bhsm.interface.muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    raw,ref=np.asarray(raw_pair,complex),np.asarray(reference_pair,complex)
    z=np.asarray(extra_coefficients,complex)
    rep=representation;oldmap=maps['old504_to_full'];extra=maps['extra_coordinates_to_full']
    T=maps['extra_point_lift'];dim=int(maps['full_dimension'])
    if raw.shape!=(2,268)or ref.shape!=raw.shape or z.shape!=(len(extra),):
        raise ValueError('actual same-domain raw pair and complete augmented field coefficients required')
    original=holomorphic_two_arm_action(raw,ref,rep,**action_parameters)
    P=original['one_lift'];Pgeo=P[:100]
    H=np.zeros((dim,dim),complex);G=np.zeros(dim,complex)
    H[np.ix_(oldmap,oldmap)]=original['hessian'];G[oldmap]=original['gradient']
    old_fields=original['branch_fields'][1]
    packed=np.concatenate([old_fields[k].reshape(len(T),20)for k in ('A','At','Ar')],axis=1)
    changed=packed+np.einsum('rai,i->ra',T,z)
    A,At,Ar=(changed[:,20*k:20*(k+1)].reshape(-1,5,4)for k in range(3))
    oldA,oldAt,oldAr=(old_fields[k]for k in ('A','At','Ar'))
    geo=holomorphic_geometry_rows(raw[1,:100],rep['rho'])
    parent=holomorphic_geometry_rows(raw[0,:100],rep['rho'],connection_only=True)
    names=('electric','radial','angular','electric_radial','shift')
    density=np.asarray([[row[k].value for k in names]for row in geo['rows']])
    oldlocal=analytic_constant_maxwell_batch(oldA,oldAt,oldAr,density)
    local=analytic_constant_maxwell_batch(A,At,Ar,density)
    ld0,dd0=_density_jets(oldA,oldAt,oldAr,density)
    ld,dd=_density_jets(A,At,Ar,density)
    gd0=_field_density_cross(oldA,oldAt,oldAr,density)
    gd=_field_density_cross(A,At,Ar,density)
    nr=len(T);gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(nr,80,20)
    gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(nr,80,20)
    Eraw=np.zeros((nr,60,268),complex)
    Eraw[:,:20,100:180]=gb.transpose(0,2,1)
    Eraw[:,20:40,180:260]=gb.transpose(0,2,1)
    Eraw[:,40:,100:180]=gr.transpose(0,2,1)
    E=Eraw@P
    value=original['value']
    point_first=np.zeros((nr,60,dim),complex)
    density_first=np.zeros((nr,5,dim),complex)
    for i,(row,prow,w0)in enumerate(zip(geo['rows'],parent['rows'],rep['radial_quadrature'])):
        w=MAXWELL_TO_CAP*w0
        Jp=np.zeros((60,252),complex)
        for k,key in enumerate(('connection_lambda','lambda_tau','lambda_rho')):
            Jp[k*20+8:(k+1)*20]=M.reshape(12,1)*(prow[key].gradient@Pgeo)[None,:]
        J=np.c_[Jp,E[i]]
        D=np.zeros((5,504),complex)
        D[:,252:]=np.asarray([row[k].gradient@Pgeo for k in names])
        point_first[i,:,oldmap]=J.T
        point_first[i,:,extra]=T[i].T
        density_first[i,:,oldmap]=D.T
        df=local['gradient'][i]-oldlocal['gradient'][i]
        dl=ld[i]-ld0[i]
        dH=local['hessian'][i]-oldlocal['hessian'][i]
        dgd=gd[i]-gd0[i]
        ddd=dd[i]-dd0[i]
        go=w*(J.T@df+D.T@dl)
        ho=w*(J.T@dH@J+J.T@dgd@D+D.T@dgd.T@J+D.T@ddd@D)
        # Curvature of the nonlinear parent source profile is NOT zero and
        # is never inferred by subtracting OWN and joint Hessians.
        p2=np.zeros((100,100),complex)
        for k,key in enumerate(('connection_lambda','lambda_tau','lambda_rho')):
            p2+=np.sum(M.reshape(12)*df[k*20+8:(k+1)*20])*prow[key].hessian
        ho[:252,:252]+=w*Pgeo.T@p2@Pgeo
        d2=sum((dl[k]*row[name].hessian for k,name in enumerate(names)),np.zeros((100,100),complex))
        ho[252:,252:]+=w*Pgeo.T@d2@Pgeo
        G[oldmap]+=go;H[np.ix_(oldmap,oldmap)]+=ho
        cross=w*(J.T@local['hessian'][i]@T[i]+D.T@gd[i].T@T[i])
        H[np.ix_(oldmap,extra)]+=cross
        H[np.ix_(extra,oldmap)]+=cross.T
        H[np.ix_(extra,extra)]+=w*T[i].T@local['hessian'][i]@T[i]
        G[extra]+=w*T[i].T@local['gradient'][i]
        value+=w*(local['value'][i]-oldlocal['value'][i])
    return dict(value=value,gradient=G,Hessian=H,old_full504_Hessian=original['hessian'],
        old_full504_gradient=original['gradient'],one_lift=P,point_connection=A,
        point_time=At,point_radial=Ar,density=density,
        point_first=point_first,density_first=density_first,
        inherited_profile_J2_and_density_D2_retained=True,
        scalar_Higgs_wall_increment_zero_by_fixed_material_zero_trace=True,
        independent_source_motion_inserted_once=True,analytic_transpose_not_Hilbert_adjoint=True)


def contracted_directional_application(evaluator, base_master, directions_high,
        directions_low, right_high, right_low, *, radii=(.032,.016,.008),
        save_branch=None,base_evaluation=None):
    """Evaluate D_h H applied only to supplied actual augmented right vectors."""
    import numpy as np
    from flint import ctx
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    ctx.prec=192
    q=np.asarray(base_master,complex);dh=np.asarray(directions_high,complex);dl=np.asarray(directions_low,complex)
    if dh.shape!=dl.shape or dh.ndim!=2 or dh.shape[0]!=len(q):
        raise ValueError('actual complete same-augmented source/domain direction high/low pairs required')
    rh,rl=np.asarray(right_high,complex),np.asarray(right_low,complex)
    if rh.shape!=rl.shape or rh.ndim!=2 or rh.shape[0]!=len(q):
        raise ValueError('mandatory same-augmented right-vector high/low pairs required')
    right=_matrix(rh)+_matrix(rl)
    records=[];applications=[]
    if base_evaluation is None:base_evaluation=evaluator(q)
    baseH=_matrix(base_evaluation['Hessian'])
    for j in range(dh.shape[1]):
        direction=dh[:,j]+dl[:,j]
        scale=max(float(np.max(abs(direction))),np.finfo(float).tiny)
        unit=direction/scale
        old=None
        for radius in radii:
            Hs=[];Gs=[];Vs=[]
            for k,axis in enumerate((1,1j,-1,-1j)):
                branch=evaluator(q+axis*radius*unit)
                Hs.append(_matrix(branch['Hessian']));Gs.append(_matrix(branch['gradient'][:,None]));Vs.append(branch['value'])
                if save_branch is not None:save_branch(j,radius,k,branch)
                print(json.dumps(dict(stage='actual_augmented_original_action_branch',direction=j,radius=radius,axis=k)),flush=True)
            weights=(1,-1j,-1,1j)
            combine=lambda a:scale*sum((w*x for w,x in zip(weights,a)),a[0]*0)/(4*radius)
            first=combine(Hs)*right
            gradient_first=combine(Gs)
            gradient_expected=baseH*(_matrix(dh[:,j,None])+_matrix(dl[:,j,None]))
            values=dict(contracted_Hessian_first_on_actual_right=first,
                fresh_original_gradient_first=gradient_first,
                original_Hessian_direction_gradient_first=gradient_expected,
                independent_original_gradient_difference=gradient_first-gradient_expected)
            arrays={}
            for name,value in values.items():arrays[name+'_high'],arrays[name+'_low']=_split(value)
            mid=_mid(first);gd=_mid(gradient_first);ge=_mid(gradient_expected)
            rec=dict(direction=j,radius=radius,direction_normalization=scale,
                independent_original_gradient_absolute_upper=_upper(gradient_first-gradient_expected),
                independent_original_gradient_relative_norm=float(np.linalg.norm(gd-ge)/max(np.linalg.norm(gd),1e-300)),
                contracted_Hessian_first_norm=float(np.linalg.norm(mid)),
                contracted_step_difference_norm=None if old is None else float(np.linalg.norm(mid-old)))
            old=mid;records.append(rec);applications.append((j,radius,arrays))
            print(json.dumps(dict(stage='augmented_contracted_derivative_control',**rec)),flush=True)
    return dict(records=records,applications=applications,full_third_tensor_materialized=False,
        fixed_source_adjoint_moved=False,source_or_domain_operand_defaulted_to_zero=False)


def run_birth(repository,birth_folder,output,*,columns=(0,1,2)):
    """First actual augmented application at the gauge-completed birth."""
    import numpy as np
    root,birth,out=map(Path,(repository,birth_folder,output))
    if out.exists():raise FileExistsError('preserve each original augmented derivative application')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pins,archives={},{}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        p=out/name;_compressed_npz(p,data)
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    c=read(birth/'birth_current288_connected_action_and_rate_operands.npz')
    r=read(birth/'enlarged_birth_radial_action.npz')
    b=read(birth/'enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    params=read(root/'artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    phase,_=retained_input('outgoing',pins);rep=phase['representation']
    P=phase['coordinates']['lift'];maps=augmented_maps(c,r)
    dim=maps['full_dimension'];oldmap=maps['old504_to_full'];extra=maps['extra_coordinates_to_full']
    raw,ref=b['raw_pair'],b['reference_pair']
    oldmaster=np.r_[P.T@raw[0],P.T@raw[1]]
    master=np.zeros(dim,complex);master[oldmap]=oldmaster
    def evaluate(q):
        delta=q[oldmap]-oldmaster
        xx=raw+np.stack((P@delta[:252],P@delta[252:]))
        return augmented_scalar_action(xx,ref,q[extra],rep,maps,action_parameters=params)
    print(json.dumps(dict(stage='actual_gauge_augmented_birth_base_started',dimension=dim)),flush=True)
    base=evaluate(master)
    difference=base['Hessian']-b['full_two_arm_Hessian']
    save('same_augmented_birth_original_action_base.npz',dict(Hessian=base['Hessian'],gradient=base['gradient'],
        saved_full_two_arm_Hessian=b['full_two_arm_Hessian'],coefficient_Hessian_difference=difference,
        raw_pair=raw,reference_pair=ref,old504_to_full=oldmap,extra_coordinates_to_full=extra,
        extra_point_lift=maps['extra_point_lift'],base_master=master))
    print(json.dumps(dict(stage='actual_augmented_scalar_base_comparison',
        maximum=float(np.max(abs(difference))),relative=float(np.linalg.norm(difference)/max(np.linalg.norm(base['Hessian']),1e-300)))),flush=True)
    if np.max(abs(difference))>2e-8:
        raise ValueError('augmented original scalar action differs from saved same-epoch completed coefficients')
    Uhigh=b['full_two_arm_fixed_position_phase_high'][:,columns]
    Ulow=b['full_two_arm_fixed_position_phase_low'][:,columns]
    def branch_save(j,h,k,a):
        save(f'direction_{columns[j]}_radius_{h:.0e}_axis_{k}_original_augmented_action.npz',
            dict(Hessian=a['Hessian'],gradient=a['gradient'],value=np.asarray(a['value'])))
    result=contracted_directional_application(evaluate,master,Uhigh,Ulow,
        b['full_two_arm_fixed_position_phase_high'],b['full_two_arm_fixed_position_phase_low'],
        save_branch=branch_save,base_evaluation=base)
    for j,h,data in result['applications']:
        save(f'direction_{columns[j]}_radius_{h:.0e}_contracted_source_domain_action.npz',data)
    pins[str(Path(__file__))]=sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(classification='EVALUATED_ACTUAL_AUGMENTED_BIRTH_SOURCE_DOMAIN_ACTION_DIRECTIONS',
        input_hashes=pins,archives=archives,records=result['records'],augmented_dimension=dim,
        old504_basis_substituted_for_augmented_directions=False,
        base_full_Hessian_difference_max=float(np.max(abs(difference))),
        fixed_material_rho_gauge_frame_first_zero_by_explicit_literal_coefficient_law=True,
        full_original_scalar_Higgs_metric_inherited_action_retained=True,
        profile_second_and_density_second_contacts_retained=True,
        fixed_adjoint_source_preserved=True,full_third_tensor_materialized=False,
        actual_retarded_history_derivative_solved=False,physical_terminal_derivative_admitted=False,
        source_D5_profile_canonical_pairing_integrations_repeated=0,
        scope='Actual NEW gauge-completed proper birth directions, complete phi/P1/P2 added fields and their rates/Gauss components. Original scalar-action Hessian directional applications evaluated on all supplied right columns. This is an operand of the chronological source/domain derivative; it does not substitute for that history solve or terminal conversion.',
        error_scope='Three analytic polarization radii; fresh original scalar-gradient derivatives and contracted Hessian step changes. Binary coefficient evaluation plus retained192 contractions; no physical/truncation/outward enclosure.')
    p=out/'result.json';p.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='augmented_birth_directional_application_finished',path=str(p))),flush=True)
    return report


def run_first_cell(repository,birth_folder,output,*,columns=(0,1,2),rank=7):
    """Actual new proper stage action derivatives with the two source placements."""
    import numpy as np
    from flint import ctx
    root,birth,out=map(Path,(repository,birth_folder,output))
    if out.exists():raise FileExistsError('preserve every actual augmented cell derivative')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_changing_weak_birth_action import affine_parent_master_map
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    ctx.prec=192
    pins,archives={},{}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        p=out/name;_compressed_npz(p,data)
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    a=root/'artifacts'
    c=read(a/'muon_baton_zoo_saved_rate_operands_20261013/joint_run_1/cell_0000_independent_rate_and_source_operands.npz')
    r=read(a/'muon_baton_zoo_radial_completion_20261013/assembly_run_1/cell_0000_degree_02_connected_radial_action.npz')
    b=read(birth/'enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    f=read(a/'muon_baton_zoo_radial_completion_20261013/action_gauge_all_cells_run_1/cell_0000_degree_02_literal_temporal_gauge_frames.npz')
    proper=read(a/f'muon_baton_zoo_gauge_proper_history_20261013/rank{rank}_run_1/cell_0000_retarded_and_homogeneous_proper_columns.npz')
    baseline=read(a/f'muon_baton_zoo_gauge_completed_history_20261013/rank{rank}_run_1/cell_0000_joint_baseline_and_three_columns.npz')
    params=read(a/'muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    maps=augmented_maps(c,r);dim=maps['full_dimension'];oldmap=maps['old504_to_full'];extra=maps['extra_coordinates_to_full']
    raw,ref=c['raw_pair'],c['reference_pair'];oldmaster=np.r_[P.T@raw[0],P.T@raw[1]]
    master=np.zeros(dim,complex);master[oldmap]=oldmaster
    def evaluate(q):
        delta=q[oldmap]-oldmaster
        xx=raw+np.stack((P@delta[:252],P@delta[252:]))
        return augmented_scalar_action(xx,ref,q[extra],rep,maps,action_parameters=params)
    print(json.dumps(dict(stage='actual_new_proper_first_cell_augmented_action_base_started',dimension=dim)),flush=True)
    base=evaluate(master)
    blocks=dict(child_Hessian_difference=base['Hessian'][252:,252:]-r['Hessian'],
        inherited_Hcp_difference=base['Hessian'][252:,:252]-r['inherited_source_Hcp'],
        inherited_Hpc_difference=base['Hessian'][:252,252:]-r['inherited_source_Hpc'],
        original504_Hessian_difference=base['old_full504_Hessian']-c['original_full_Hessian'])
    maxima={k:float(np.max(abs(v)))for k,v in blocks.items()}
    save('same_augmented_first_cell_original_action_base.npz',dict(Hessian=base['Hessian'],gradient=base['gradient'],
        point_first=base['point_first'],density_first=base['density_first'],point_connection=base['point_connection'],
        point_time=base['point_time'],point_radial=base['point_radial'],density=base['density'],
        original_point_rate=c['point_rate'],original_density_rate=c['density_rate'],
        baseline_Euler_force=r['baseline_Euler_force'],frames=f['frames_completed'],
        raw_pair=raw,reference_pair=ref,old504_to_full=oldmap,extra_coordinates_to_full=extra,
        extra_point_lift=maps['extra_point_lift'],base_master=master,**blocks))
    print(json.dumps(dict(stage='actual_augmented_first_cell_coefficient_equality',**maxima)),flush=True)
    if max(maxima.values())>2e-8:raise ValueError('same current original augmented coefficient epoch required')
    tm=proper['coordinate_time'].item()
    if tm!=baseline['coordinate_time'].item() or tm!=r['coordinate_time'].item():
        raise ValueError('same original/proper/baseline first-cell coordinate time required')
    J=_matrix(affine_parent_master_map(tm))
    Up=_matrix(b['fixed_position_parent_phase_high'])+_matrix(b['fixed_position_parent_phase_low'])
    parent=J*Up;ph,pl=_split(parent)
    childh=proper['total_proper_stage_high'];childl=proper['total_proper_stage_low']
    directions_h=np.r_[ph,childh][:,columns];directions_l=np.r_[pl,childl][:,columns]
    # Baseline inherited parent source response is exactly zero by its
    # definition. The three other parents and every child are evaluated.
    rh=np.zeros((dim,8),complex);rl=np.zeros_like(rh)
    rh[252:,0]=baseline['stage_high'][:,0];rl[252:,0]=baseline['stage_low'][:,0]
    rh[252:,1:4]=childh;rl[252:,1:4]=childl
    rh[:252,5:8]=ph;rl[:252,5:8]=pl
    save('actual_new_proper_first_cell_direction_and_separated_rights.npz',dict(
        complete_augmented_direction_high=directions_h,complete_augmented_direction_low=directions_l,
        child_and_parent_separated_right_high=rh,child_and_parent_separated_right_low=rl,
        actual_new_parent_proper_high=ph,actual_new_parent_proper_low=pl,
        actual_new_child_proper_high=childh,actual_new_child_proper_low=childl,
        coordinate_time=np.asarray(tm),columns=np.asarray(columns),
        named_frame_first_by_fixed_material_coefficient_law=np.zeros((len(columns),)+f['frames_completed'].shape,complex)))
    def branch_save(j,h,k,v):
        save(f'direction_{columns[j]}_radius_{h:.0e}_axis_{k}_original_augmented_action.npz',
             dict(Hessian=v['Hessian'],gradient=v['gradient'],value=np.asarray(v['value'])))
    result=contracted_directional_application(evaluate,master,directions_h,directions_l,rh,rl,
        save_branch=branch_save,base_evaluation=base)
    for j,h,data in result['applications']:
        for suffix in ('high','low'):
            C=data['contracted_Hessian_first_on_actual_right_'+suffix]
            data['daughter_bulk_DhHzz_on_actual_child4_'+suffix]=C[252:,:4]
            data['inherited_source_DhHzp_on_actual_parent4_'+suffix]=C[252:,4:]
            data['inherited_return_DhHpz_on_actual_child4_'+suffix]=C[:252,:4]
            data['inherited_direct_return_DhHpp_on_actual_parent4_'+suffix]=C[:252,4:]
            data['coupled_child_operator_DhH_on_actual_four_'+suffix]=C[252:,:4]+C[252:,4:]
        save(f'direction_{columns[j]}_radius_{h:.0e}_separated_contracted_source_domain_action.npz',data)
    pins[str(Path(__file__))]=sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(classification='EVALUATED_NEW_PROPER_FIRST_CELL_SEPARATED_AUGMENTED_ACTION_CONTRACTIONS',
        input_hashes=pins,archives=archives,records=result['records'],coefficient_difference_maxima=maxima,
        baseline_plus_three_actual_child_stage_rights=True,new_proper_parent_J_Up=True,
        child_bulk_and_both_inherited_source_return_placements_separate=True,
        fixed_material_rho_named_frame_first_zero_by_literal_coefficients=True,
        baseline_Euler_force_first_evaluated=False,mandatory_missing_operands=['actual new proper point/density rate first for baseline Euler force derivative','birth-section jet of nonzero homogeneous canonical seed'],
        chronological_retarded_derivative_solved=False,physical_terminal_derivative_admitted=False,
        old504_directions_substituted=False,full_third_tensor_materialized=False,moving_adjoint_reinserted=False,
        scope='Original complete augmented scalar/Higgs/metric/inherited Maxwell action at actual first cell; three NEW proper source/domain directions, contracted separately on actual baseline+three daughter stages and inherited parent directions. Mandatory Euler-force time-rate and birth-section operands are explicit and unevaluated.')
    p=out/'result.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='actual_new_proper_first_cell_contractions_finished',path=str(p))),flush=True)
    return report


def independent_complement_Euler_force(point,point_rate,density,density_rate,
        profile_lift,quadrature,extra_coordinates_to_child,child_dimension):
    """Evaluate original component g_x-d_t g_v and all added temporal Gauss rows.

    The old original rows have a separate saved canonical owner; this force
    is the independent phi/Legendre complement's original Euler defect.
    Actual point/density rates are mandatory, including reference clock.
    """
    import numpy as np
    from bhsm.interface.muon_baton_zoo_original_validation import (
        independent_original_maxwell_weak,independent_original_maxwell_momentum_rate)
    p,pt,d,dt,T,w=map(lambda a:np.asarray(a,complex),(
        point,point_rate,density,density_rate,profile_lift,quadrature))
    nr,nt=len(p),T.shape[2]
    if p.shape!=(nr,60)or pt.shape!=p.shape or d.shape!=(nr,5)or dt.shape!=d.shape:
        raise ValueError('complete evaluated same-epoch field/density and rate operands required')
    if T.shape!=(nr,60,nt)or nt%36 or len(extra_coordinates_to_child)!=nt:
        raise ValueError('all profile value/rate/Gauss coordinates and explicit child injection required')
    A,At,Ar=(p[:,20*k:20*(k+1)].reshape(nr,5,4)for k in range(3))
    Atau,Att,Art=(pt[:,20*k:20*(k+1)].reshape(nr,5,4)for k in range(3))
    angular=np.zeros((nr,3,5,4),complex)
    tests=dict(tests=T[:,:20].transpose(0,2,1).reshape(nr,nt,5,4),
        tests_time=T[:,20:40].transpose(0,2,1).reshape(nr,nt,5,4),
        tests_radial=T[:,40:].transpose(0,2,1).reshape(nr,nt,5,4),
        tests_angular=np.zeros((nr,nt,3,5,4),complex))
    weak=independent_original_maxwell_weak(connection=A,time_derivative=At,
        radial_derivative=Ar,angular_derivative=angular,metric_densities=d,
        quadrature=w,**tests)['original_weak_rows']
    momentum_rate=independent_original_maxwell_momentum_rate(connection=A,
        time_derivative=At,radial_derivative=Ar,angular_derivative=angular,
        connection_rate=Atau,time_derivative_rate=Att,radial_derivative_rate=Art,
        angular_derivative_rate=angular,metric_densities=d,metric_density_rates=dt)
    pos=np.r_[tuple(np.arange(36*k,36*k+16)for k in range(nt//36))]
    gauss=np.r_[tuple(np.arange(36*k+32,36*k+36)for k in range(nt//36))]
    m=np.einsum('rjfc,rfc,r->j',tests['tests'][:,pos],momentum_rate,w,optimize=True)
    full=np.zeros(int(child_dimension),complex)
    ids=np.asarray(extra_coordinates_to_child,int)
    full[ids[pos]]=weak[pos]-m;full[ids[gauss]]=weak[gauss]
    return dict(baseline_Euler_force=full,independent_original_profile_gradient=weak,
        independent_original_profile_momentum_time_first=m,
        old_original_rows_owned_by_separate_saved_canonical_application=True,
        rate_force_slots_zero_by_Euler_source_placement=True)


def independent_complement_Euler_force_first(base,first,*,radii=(.032,.016,.008)):
    """Fresh original component derivatives; no absent rate may default to zero."""
    import numpy as np
    mandatory=('point','point_rate','density','density_rate')
    for k in mandatory:
        if k not in base or k not in first:raise ValueError('mandatory actual '+k+' and first operand missing')
    # The Euler force is affine in the point/density rates. Normalizing
    # by a large acceleration first would needlessly suppress the field
    # perturbation; finite analytic branches require only field/density
    # control. The supplied rate perturbations remain complete.
    # The first four metric densities enter affinely, so only the shift
    # density needs nonlinear amplitude control together with the fields.
    scale=max(float(np.max(abs(first['point']))),float(np.max(abs(first['density'][:,4]))))
    scale=max(scale,np.finfo(float).tiny)
    exact=independent_complement_Euler_force_first_product(base,first)
    records=[];applications=[]
    for radius in radii:
        rows=[]
        for axis in (1,1j,-1,-1j):
            operands={k:base[k]+axis*radius/scale*first[k]for k in mandatory}
            rows.append(independent_complement_Euler_force(**operands,
                profile_lift=base['profile_lift'],quadrature=base['quadrature'],
                extra_coordinates_to_child=base['extra_coordinates_to_child'],
                child_dimension=base['child_dimension'])['baseline_Euler_force'])
        value=scale*(rows[0]-1j*rows[1]-rows[2]+1j*rows[3])/(4*radius)
        records.append(dict(radius=radius,normalization=scale,norm=float(np.linalg.norm(value)),
            fresh_original_component_difference_max=float(np.max(abs(value-exact))),
            fresh_original_component_difference_relative=float(np.linalg.norm(value-exact)/max(np.linalg.norm(exact),1e-300))))
        applications.append(value)
    return dict(records=records,force_first=applications,independent_product_rule_force_first=exact,
        independent_original_component_product_rule=True,mandatory_rate_operand_missing=False)


def independent_complement_Euler_force_first_product(base,first):
    """Literal component product rule for D_h(g_x-d_tg_v,g_At).

    It differentiates the original Maxwell curvature/brackets and every
    density and momentum-rate factor. No scalar-action Hessian is used.
    """
    import numpy as np
    from bhsm.interface.muon_baton_zoo_original_validation import _commutator as c
    p,pt,d,dd=(np.asarray(base[k],complex)for k in ('point','point_rate','density','density_rate'))
    hp,hpt,hd,hdd=(np.asarray(first[k],complex)for k in ('point','point_rate','density','density_rate'))
    T=np.asarray(base['profile_lift'],complex);w=np.asarray(base['quadrature'],complex)
    nr,nt=len(p),T.shape[2]
    split=lambda q:[q[:,20*k:20*(k+1)].reshape(nr,5,4)for k in range(3)]
    a,at,ar=split(p);ad,atd,ard=split(pt)
    ha,hat,har=split(hp);had,hatd,hard=split(hpt)
    v,vt,vr=[T[:,20*k:20*(k+1)].transpose(0,2,1).reshape(nr,nt,5,4)for k in range(3)]
    e,r,ang,k,beta=d.T;he,hr,hang,hk,hbeta=hd.T
    ed,_,_,kd,bd=dd.T;hed,_,_,hkd,hbd=hdd.T
    x=at[:,1]-ar[:,0]+c(a[:,0],a[:,1])
    hx=hat[:,1]-har[:,0]+c(ha[:,0],a[:,1])+c(a[:,0],ha[:,1])
    t=at[:,2:]+c(a[:,0,None],a[:,2:])
    ht=hat[:,2:]+c(ha[:,0,None],a[:,2:])+c(a[:,0,None],ha[:,2:])
    z=ar[:,2:]+c(a[:,1,None],a[:,2:])
    hz=har[:,2:]+c(ha[:,1,None],a[:,2:])+c(a[:,1,None],ha[:,2:])
    b=2*a[:,2:].copy();hb=2*ha[:,2:].copy()
    dx=vt[:,:,1]-vr[:,:,0]+c(v[:,:,0],a[:,None,1])+c(a[:,None,0],v[:,:,1])
    hdx=c(v[:,:,0],ha[:,None,1])+c(ha[:,None,0],v[:,:,1])
    dt=vt[:,:,2:]+c(v[:,:,0,None],a[:,None,2:])+c(a[:,None,0,None],v[:,:,2:])
    hdt=c(v[:,:,0,None],ha[:,None,2:])+c(ha[:,None,0,None],v[:,:,2:])
    dz=vr[:,:,2:]+c(v[:,:,1,None],a[:,None,2:])+c(a[:,None,1,None],v[:,:,2:])
    hdz=c(v[:,:,1,None],ha[:,None,2:])+c(ha[:,None,1,None],v[:,:,2:])
    db=2*v[:,:,2:].copy();hdb=np.zeros_like(db)
    for i,j,l in ((0,1,2),(1,2,0),(2,0,1)):
        b[:,i]+=c(a[:,j+2],a[:,l+2]);hb[:,i]+=c(ha[:,j+2],a[:,l+2])+c(a[:,j+2],ha[:,l+2])
        db[:,:,i]+=c(v[:,:,j+2],a[:,None,l+2])+c(a[:,None,j+2],v[:,:,l+2])
        hdb[:,:,i]+=c(v[:,:,j+2],ha[:,None,l+2])+c(ha[:,None,j+2],v[:,:,l+2])
    y=t-beta[:,None,None]*z
    hy=ht-hbeta[:,None,None]*z-beta[:,None,None]*hz
    dy=dt-beta[:,None,None,None]*dz
    hdy=hdt-hbeta[:,None,None,None]*dz-beta[:,None,None,None]*hdz
    inner=lambda aa,bb:np.sum(aa[:,None]*bb,axis=tuple(range(2,bb.ndim)))
    weak=(hk[:,None]*inner(x,dx)+k[:,None]*(inner(hx,dx)+inner(x,hdx))+
        he[:,None]*inner(y,dy)+e[:,None]*(inner(hy,dy)+inner(y,hdy))-
        hr[:,None]*inner(z,dz)-r[:,None]*(inner(hz,dz)+inner(z,hdz))-
        hang[:,None]*inner(b,db)-ang[:,None]*(inner(hb,db)+inner(b,hdb)))
    weak=np.sum(w[:,None]*weak,axis=0)
    xd=atd[:,1]-ard[:,0]+c(ad[:,0],a[:,1])+c(a[:,0],ad[:,1])
    hxd=hatd[:,1]-hard[:,0]+c(had[:,0],a[:,1])+c(ad[:,0],ha[:,1])+c(ha[:,0],ad[:,1])+c(a[:,0],had[:,1])
    td=atd[:,2:]+c(ad[:,0,None],a[:,2:])+c(a[:,0,None],ad[:,2:])
    htd=hatd[:,2:]+c(had[:,0,None],a[:,2:])+c(ad[:,0,None],ha[:,2:])+c(ha[:,0,None],ad[:,2:])+c(a[:,0,None],had[:,2:])
    zd=ard[:,2:]+c(ad[:,1,None],a[:,2:])+c(a[:,1,None],ad[:,2:])
    hzd=hard[:,2:]+c(had[:,1,None],a[:,2:])+c(ad[:,1,None],ha[:,2:])+c(ha[:,1,None],ad[:,2:])+c(a[:,1,None],had[:,2:])
    yd=td-bd[:,None,None]*z-beta[:,None,None]*zd
    hyd=htd-hbd[:,None,None]*z-bd[:,None,None]*hz-hbeta[:,None,None]*zd-beta[:,None,None]*hzd
    mp=np.zeros((nr,5,4),complex)
    mp[:,1]=hkd[:,None]*x+kd[:,None]*hx+hk[:,None]*xd+k[:,None]*hxd
    mp[:,2:]=hed[:,None,None]*y+ed[:,None,None]*hy+he[:,None,None]*yd+e[:,None,None]*hyd
    pos=np.r_[tuple(np.arange(36*j,36*j+16)for j in range(nt//36))]
    gauss=np.r_[tuple(np.arange(36*j+32,36*j+36)for j in range(nt//36))]
    rate=np.einsum('rjfc,rfc,r->j',v[:,pos],mp,w,optimize=True)
    result=np.zeros(int(base['child_dimension']),complex);ids=np.asarray(base['extra_coordinates_to_child'],int)
    result[ids[pos]]=weak[pos]-rate;result[ids[gauss]]=weak[gauss]
    return result


def actual_point_density_rate_first(raw_pair,one_lift,maps,representation,
        full_direction,full_direction_time_rate,base_child_original_rate,
        base_parent_rate):
    """Contract owned source J2/density D2 once with actual stage/time directions.

    The anchored references are held in this supplied original direction
    application. Their affine clock is retained in the baseline point rate;
    no unknown reference/domain direction is silently inferred as zero.
    """
    import numpy as np
    from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    raw=np.asarray(raw_pair,complex);Pgeo=np.asarray(one_lift)[:100]
    h,ht=np.asarray(full_direction,complex),np.asarray(full_direction_time_rate,complex)
    if h.shape!=ht.shape or h.shape!=(maps['full_dimension'],):
        raise ValueError('mandatory complete actual augmented stage/time directions required')
    oldmap=np.asarray(maps['old504_to_full'],int)
    parenth=Pgeo@h[:252];parentrate=Pgeo@np.asarray(base_parent_rate,complex)
    childh=Pgeo@h[oldmap[252:]];childrate=Pgeo@np.asarray(base_child_original_rate,complex)
    p=np.zeros((len(representation['rho']),60),complex)
    d=np.zeros((len(p),5),complex)
    parent=holomorphic_geometry_rows(raw[0,:100],representation['rho'],connection_only=True)['rows']
    child=holomorphic_geometry_rows(raw[1,:100],representation['rho'])['rows']
    keys=('connection_lambda','lambda_tau','lambda_rho')
    names=('electric','radial','angular','electric_radial','shift')
    for i,(pr,cr)in enumerate(zip(parent,child)):
        for k,name in enumerate(keys):
            p[i,20*k+8:20*(k+1)]=M.reshape(12)*(parenth@pr[name].hessian@parentrate)
        for k,name in enumerate(names):d[i,k]=childh@cr[name].hessian@childrate
    return dict(point_rate_curvature_first=p,density_rate_curvature_first=d,
        no_extra_material_profile_first_by_literal_fixed_rho_coefficients=True,
        fixed_anchored_reference_direction_scope=True)


def materialize_first_cell_Euler_force_first(repository,application_folder,
        clock_folder,actual_stage_rate_high,actual_stage_rate_low,
        actual_parent_stage_rate_high,actual_parent_stage_rate_low,output):
    """Mandatory actual h-rate inputs plus fresh original component force controls."""
    import numpy as np
    root,folder,clock,out=map(Path,(repository,application_folder,clock_folder,output))
    if out.exists():raise FileExistsError('preserve original component Euler-force first')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pins,archives={},{}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        p=out/name;_compressed_npz(p,data);archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    base=read(folder/'same_augmented_first_cell_original_action_base.npz')
    packet=read(folder/'actual_new_proper_first_cell_direction_and_separated_rights.npz')
    ratebase=read(clock/'same_epoch_full_clock_point_density_canonical_and_Euler_comparison.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    h=packet['complete_augmented_direction_high']+packet['complete_augmented_direction_low']
    ch=np.asarray(actual_stage_rate_high,complex)+np.asarray(actual_stage_rate_low,complex)
    ph=np.asarray(actual_parent_stage_rate_high,complex)+np.asarray(actual_parent_stage_rate_low,complex)
    if ch.shape!=(360,h.shape[1])or ph.shape!=(252,h.shape[1]):
        raise ValueError('actual same-new-proper-column child360 and parent252 rate high/low required')
    ht=np.r_[ph,ch];oldmap=base['old504_to_full'];extra=base['extra_coordinates_to_full']
    maps=dict(full_dimension=612,old504_to_full=oldmap)
    baserate=ratebase['full_augmented_base_master_rate']
    oldchildrate=baserate[oldmap[252:]];parentrate=baserate[:252]
    point=np.concatenate((base['point_connection'].reshape(-1,20),base['point_time'].reshape(-1,20),base['point_radial'].reshape(-1,20)),axis=1)
    b=dict(point=point,point_rate=ratebase['actual_point_rate'],density=base['density'],
        density_rate=ratebase['actual_density_rate'],profile_lift=base['extra_point_lift'],
        quadrature=np.asarray(rep['radial_quadrature'])*__import__('bhsm.interface.muon_parent_mean_causal_action',fromlist=['MAXWELL_TO_CAP']).MAXWELL_TO_CAP,
        extra_coordinates_to_child=extra-252,child_dimension=360)
    report=[]
    for j,column in enumerate(packet['columns']):
        curvature=actual_point_density_rate_first(base['raw_pair'],P,maps,rep,h[:,j],ht[:,j],oldchildrate,parentrate)
        first=dict(point=base['point_first']@h[:,j],density=base['density_first']@h[:,j],
            point_rate=base['point_first']@ht[:,j]+curvature['point_rate_curvature_first'],
            density_rate=base['density_first']@ht[:,j]+curvature['density_rate_curvature_first'])
        save(f'direction_{column}_actual_point_density_and_rate_first.npz',dict(**first,
            actual_complete_stage_direction=h[:,j],actual_complete_stage_time_rate=ht[:,j],
            actual_child_stage_rate_high=np.asarray(actual_stage_rate_high)[:,j],
            actual_child_stage_rate_low=np.asarray(actual_stage_rate_low)[:,j],
            actual_parent_stage_rate_high=np.asarray(actual_parent_stage_rate_high)[:,j],
            actual_parent_stage_rate_low=np.asarray(actual_parent_stage_rate_low)[:,j],
            **{k:v for k,v in curvature.items()if isinstance(v,np.ndarray)}))
        result=independent_complement_Euler_force_first(b,first)
        save(f'direction_{column}_independent_original_product_rule_Euler_force_first.npz',dict(
            baseline_Euler_force_first=result['independent_product_rule_force_first'],
            actual_complete_stage_time_rate=ht[:,j]))
        for rec,value in zip(result['records'],result['force_first']):
            save(f'direction_{column}_radius_{rec["radius"]:.0e}_independent_original_Euler_force_first.npz',dict(
                baseline_Euler_force_first=value,actual_complete_stage_time_rate=ht[:,j]))
            report.append(dict(direction=int(column),**rec))
    result=dict(classification='EVALUATED_ACTUAL_NEW_PROPER_ORIGINAL_COMPONENT_COMPLEMENT_EULER_FORCE_FIRST',
        input_hashes=pins,archives=archives,records=report,
        actual_stage_time_rate_supplied=True,source_J2_and_density_D2_applied_once=True,
        fixed_material_profile_first_zero_by_literal_coefficients=True,
        fixed_anchored_reference_direction_scope=True,
        moving_adjoint_reinserted=False,physical_terminal_derivative_admitted=False)
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return result


def original_canonical_rate_from_same_action(action,raw_pair,coordinate_time,
        born_pair,born_reference,representation,original_frames,*,action_parameters,clock_only=False):
    """Original canonical rate using the SAME action epoch and exact source clock."""
    import numpy as np
    from flint import acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _cat,_rows,_split
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    import bhsm.interface.muon_holomorphic_child_clock_application as clock
    raw=np.asarray(raw_pair,complex);P=action['one_lift'];H=action['old_full504_Hessian'][252:,252:]
    G=action['old_full504_gradient'][252:];eta=P.T@raw[1]
    owner=clock.holomorphic_inherited_child_action
    cached=dict(gradient=G,hessian=H,coordinates=dict(x_count=106,lift=P),
        Lvx=H[106:212,:106],Lyx=H[212:,:106])
    def supplied(*args,**kwargs):return cached
    clock.holomorphic_inherited_child_action=supplied
    try:
        gt=clock.holomorphic_child_explicit_clock_application(raw[1],coordinate_time,
            born_pair,born_reference,representation,**action_parameters)['gradient_clock_first']
    finally:clock.holomorphic_inherited_child_action=owner
    if clock_only:return dict(gradient_clock_first=gt)
    F=np.asarray(original_frames,complex)
    K=np.block([[H[106:,106:],F.T],[F,np.zeros((len(F),len(F)),complex)]])
    rhs=_cat(_matrix(G[:106])-_matrix(H[106:212,:106])*_matrix(eta[106:212])-_matrix(gt[106:212]),
        -_matrix(H[212:,:106])*_matrix(eta[106:212])-_matrix(gt[212:]),acb_mat(len(F),1))
    v=_matrix(K).solve(rhs);erate=_cat(_matrix(eta[106:212]),_rows(v,0,146))
    rate=_mid(erate)[:,0]
    eff,efft=clock.inherited_connection_clock_jet(born_pair,born_reference,
        coordinate_time,representation['rho'])
    source=np.zeros((len(eff),60),complex)
    for k in range(3):source[:,20*k+8:20*(k+1)]=M.reshape(1,12)*efft[:,k,None]
    return dict(original_child_master_rate=rate,original_child_master_rate_high=_split(erate)[0],
        original_child_master_rate_low=_split(erate)[1],actual_inherited_clock_point_rate=source,
        original_phase_rate_rows_upper=_upper(_matrix(K)*v-rhs),gradient_clock_first=gt)


def augmented_direct_child_parent_source(raw_pair,reference_pair,extra_coefficients,
        representation,maps,one_lift,*,nu_squared_action=4):
    """Independent CHILD Hpp leaf with exact inherited profile J/J2 and wall Higgs."""
    import numpy as np
    from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    from bhsm.interface.muon_common_port_chronological_lifts_source import direct_child_parent_profile_source
    raw,ref=np.asarray(raw_pair,complex),np.asarray(reference_pair,complex);rep=representation
    keys=('connection_lambda','lambda_tau','lambda_rho')
    vals=lambda r,rr:np.array([[q[k].value for k in keys]for q in
        holomorphic_geometry_rows(r[:100],rr,connection_only=True)['rows']])
    eff=vals(raw[0],rep['rho'])-vals(ref[0],rep['rho'])+vals(ref[1],rep['rho'])
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(eff),80,20)
    gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(eff),80,20)
    A=(gb.transpose(0,2,1)@raw[1,100:180]).reshape(-1,5,4)
    At=(gb.transpose(0,2,1)@raw[1,180:260]).reshape(-1,5,4)
    Ar=(gr.transpose(0,2,1)@raw[1,100:180]).reshape(-1,5,4)
    A[:,2:]+=M[None]*(eff[:,0]-1)[:,None,None]
    At[:,2:]+=M[None]*eff[:,1,None,None];Ar[:,2:]+=M[None]*eff[:,2,None,None]
    point=np.concatenate((A.reshape(-1,20),At.reshape(-1,20),Ar.reshape(-1,20)),axis=1)
    point+=maps['extra_point_lift']@np.asarray(extra_coefficients,complex)
    A,At,Ar=(point[:,20*k:20*(k+1)].reshape(-1,5,4)for k in range(3))
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[1,100:180])
    wall_eff=vals(raw[0],[WALL])-vals(ref[0],[WALL])+vals(ref[1],[WALL])
    wall[2:]+=M*(wall_eff[0,0]-1)
    operands=dict(one_lift=one_lift,branch_fields=[None,dict(A=A,At=At,Ar=Ar,wall=wall)])
    return direct_child_parent_profile_source(operands,raw,rep,nu_squared_action=nu_squared_action)


def materialize_direct_source_placement(repository,birth_folder,application_folder,output):
    """Read completed branch states and evaluate direct CHILD parent-return placements."""
    import numpy as np
    from flint import ctx
    root,birth,folder,out=map(Path,(repository,birth_folder,application_folder,output))
    if out.exists():raise FileExistsError('preserve every independent child source application')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    ctx.prec=192
    pins,archives={},{}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        p=out/name;_compressed_npz(p,data);archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    b=read(birth/'enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    base=read(folder/'same_augmented_first_cell_original_action_base.npz')
    packet=read(folder/'actual_new_proper_first_cell_direction_and_separated_rights.npz')
    maps=dict(extra_point_lift=base['extra_point_lift'])
    dh=packet['complete_augmented_direction_high']+packet['complete_augmented_direction_low']
    rh=packet['child_and_parent_separated_right_high'][:252,4:]
    rl=packet['child_and_parent_separated_right_low'][:252,4:];right=_matrix(rh)+_matrix(rl)
    raw,ref=base['raw_pair'],base['reference_pair'];oldmap=base['old504_to_full'];extra=base['extra_coordinates_to_full']
    records=[]
    for j,column in enumerate(packet['columns']):
        scale=max(float(np.max(abs(dh[:,j]))),np.finfo(float).tiny)
        for h in (.032,.016,.008):
            H=[]
            for k,axis in enumerate((1,1j,-1,-1j)):
                d=axis*h/scale*dh[:,j]
                xx=raw+np.stack((P@d[oldmap[:252]],P@d[oldmap[252:]]))
                result=augmented_direct_child_parent_source(xx,ref,d[extra],rep,maps,P)
                H.append(_matrix(result['hessian']))
                save(f'direction_{column}_radius_{h:.0e}_axis_{k}_direct_child_source.npz',result)
                print(json.dumps(dict(stage='direct_augmented_child_source_branch',direction=int(column),radius=h,axis=k)),flush=True)
            first=scale*(H[0]-1j*H[1]-H[2]+1j*H[3])/(4*h)*right
            hi,lo=_split(first)
            save(f'direction_{column}_radius_{h:.0e}_direct_child_DhHpp_on_actual_parent4.npz',dict(
                direct_child_source_DhHpp_on_actual_parent4_high=hi,
                direct_child_source_DhHpp_on_actual_parent4_low=lo,
                actual_parent_right_high=rh,actual_parent_right_low=rl))
            records.append(dict(direction=int(column),radius=h,norm=float(np.linalg.norm(_mid(first)))))
    report=dict(classification='EVALUATED_DIRECT_CHILD_AUGMENTED_PARENT_SOURCE_DERIVATIVE_PLACEMENT',
        input_hashes=pins,archives=archives,records=records,parent_own_subtraction_used=False,
        profile_J2_and_child_wall_Higgs_retained=True,physical_derivative_admitted=False,
        prior_joint_parent_Hpp_key_is_joint_action_not_direct_child=True)
    p=out/'result.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return report


def run_clock_first_cell(repository,birth_folder,output,*,rank=7,radii=(.032,.016,.008)):
    """Full coefficient time derivative with parent and BOTH reference germs."""
    import numpy as np
    from flint import ctx
    root,birth,out=map(Path,(repository,birth_folder,output))
    if out.exists():raise FileExistsError('preserve each evaluated full clock derivative')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_changing_weak_birth_action import affine_parent_master_map
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    ctx.prec=192
    pins,archives={},{}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays);archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    a=root/'artifacts'
    c=read(a/'muon_baton_zoo_saved_rate_operands_20261013/joint_run_1/cell_0000_independent_rate_and_source_operands.npz')
    r=read(a/'muon_baton_zoo_radial_completion_20261013/assembly_run_1/cell_0000_degree_02_connected_radial_action.npz')
    b=read(birth/'enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    proper=read(a/f'muon_baton_zoo_gauge_proper_history_20261013/rank{rank}_run_1/cell_0000_retarded_and_homogeneous_proper_columns.npz')
    baseline=read(a/f'muon_baton_zoo_gauge_completed_history_20261013/rank{rank}_run_1/cell_0000_joint_baseline_and_three_columns.npz')
    params=read(a/'muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    maps=augmented_maps(c,r);dim=maps['full_dimension'];oldmap=maps['old504_to_full'];extra=maps['extra_coordinates_to_full']
    raw,ref=c['raw_pair'],c['reference_pair'];oldmaster=np.r_[P.T@raw[0],P.T@raw[1]]
    master=np.zeros(dim,complex);master[oldmap]=oldmaster
    parent_rate=np.zeros(252,complex);parent_rate[:38]=(P.T@b['raw_pair'][0])[106:144]
    fullrate=np.zeros(dim,complex);fullrate[:252]=parent_rate
    fullrate[oldmap[252:]]=(c['original_phase_rate_high']+c['original_phase_rate_low'])[:,0]
    refrate=np.zeros((2,268),complex)
    for arm in range(2):
        refrate[arm,:37]=b['reference_pair'][arm,37:74];refrate[arm,98]=b['reference_pair'][arm,99]
    tm=proper['coordinate_time'].item()
    # Fresh old canonical owner and point rates are checked before any
    # temporal contraction. Reference germs follow their recorded affine law.
    original_frames=c['frames'][:,c['original_order_to_augmented'][106:252]-122]
    def evaluate(offset):
        delta=offset*fullrate[oldmap]
        xx=raw+np.stack((P@delta[:252],P@delta[252:]))
        rr=ref+offset*refrate
        v=augmented_scalar_action(xx,rr,np.zeros(len(extra),complex),rep,maps,action_parameters=params)
        canonical=original_canonical_rate_from_same_action(v,xx,tm+offset,
            b['raw_pair'],b['reference_pair'],rep,original_frames,action_parameters=params)
        erate=np.zeros(dim,complex);erate[oldmap[252:]]=canonical['original_child_master_rate']
        point_rate=v['point_first']@erate+canonical['actual_inherited_clock_point_rate']
        density_rate=v['density_first']@erate
        point=np.concatenate((v['point_connection'].reshape(-1,20),v['point_time'].reshape(-1,20),v['point_radial'].reshape(-1,20)),axis=1)
        force=independent_complement_Euler_force(point,point_rate,v['density'],density_rate,
            maps['extra_point_lift'],c['quadrature'],extra-252,dim-252)
        v.update(actual_point_rate=point_rate,actual_density_rate=density_rate,
            baseline_Euler_force=force['baseline_Euler_force'],canonical_rate=canonical)
        return v
    print(json.dumps(dict(stage='actual_parent_and_two_reference_clock_base_started')),flush=True)
    base=evaluate(0)
    checks=dict(point_rate_difference_max=float(np.max(abs(base['actual_point_rate']-c['point_rate']))),
        density_rate_difference_max=float(np.max(abs(base['actual_density_rate']-c['density_rate']))),
        baseline_Euler_force_difference_max=float(np.max(abs(base['baseline_Euler_force']-r['baseline_Euler_force']))),
        original_child_rate_difference_max=float(np.max(abs(base['canonical_rate']['original_child_master_rate']-(c['original_phase_rate_high']+c['original_phase_rate_low'])[:,0]))))
    save('same_epoch_full_clock_point_density_canonical_and_Euler_comparison.npz',dict(
        actual_point_rate=base['actual_point_rate'],saved_point_rate=c['point_rate'],
        actual_density_rate=base['actual_density_rate'],saved_density_rate=c['density_rate'],
        actual_baseline_Euler_force=base['baseline_Euler_force'],saved_baseline_Euler_force=r['baseline_Euler_force'],
        full_augmented_base_master_rate=fullrate,reference_pair_rate=refrate,raw_pair=raw,reference_pair=ref))
    print(json.dumps(dict(stage='actual_full_clock_saved_rate_comparison',**checks)),flush=True)
    if checks['point_rate_difference_max']>2e-8 or checks['density_rate_difference_max']>2e-8 or checks['baseline_Euler_force_difference_max']>2e-8:
        raise ValueError('full same-clock point/density/Euler operands differ; preserve failed application')
    J=_matrix(affine_parent_master_map(tm));Up=_matrix(b['fixed_position_parent_phase_high'])+_matrix(b['fixed_position_parent_phase_low'])
    ph,pl=_split(J*Up)
    rh=np.zeros((dim,8),complex);rl=np.zeros_like(rh)
    rh[252:,0]=baseline['stage_high'][:,0];rl[252:,0]=baseline['stage_low'][:,0]
    rh[252:,1:4]=proper['total_proper_stage_high'];rl[252:,1:4]=proper['total_proper_stage_low']
    rh[:252,5:8]=ph;rl[:252,5:8]=pl;right=_matrix(rh)+_matrix(rl)
    save('actual_clock_direction_and_separate_rights.npz',dict(right_high=rh,right_low=rl,
        full_augmented_base_master_rate=fullrate,reference_pair_rate=refrate))
    scale=max(float(np.max(abs(fullrate))),float(np.max(abs(refrate))),1.)
    records=[];previous=None
    for radius in radii:
        hs=[];gs=[];fs=[]
        for k,axis in enumerate((1,1j,-1,-1j)):
            v=evaluate(axis*radius/scale)
            hs.append(_matrix(v['Hessian']));gs.append(_matrix(v['gradient'][:,None]));fs.append(_matrix(v['baseline_Euler_force'][:,None]))
            save(f'radius_{radius:.0e}_axis_{k}_same_clock_original_action.npz',dict(
                Hessian=v['Hessian'],gradient=v['gradient'],baseline_Euler_force=v['baseline_Euler_force'],
                point_rate=v['actual_point_rate'],density_rate=v['actual_density_rate']))
            print(json.dumps(dict(stage='actual_full_clock_action_branch',radius=radius,axis=k)),flush=True)
        weights=(1,-1j,-1,1j)
        first=lambda vv:scale*sum((w*x for w,x in zip(weights,vv)),vv[0]*0)/(4*radius)
        ht=first(hs)*right;gt=first(gs);ft=first(fs)
        arrays={}
        for key,v in dict(full_coefficient_time_Hessian_on_actual_separate_right=ht,
                full_scalar_gradient_time_first=gt,baseline_Euler_force_time_first=ft).items():
            arrays[key+'_high'],arrays[key+'_low']=_split(v)
        for suffix in ('high','low'):
            C=arrays['full_coefficient_time_Hessian_on_actual_separate_right_'+suffix]
            arrays['daughter_Hzz_time_on_actual_child4_'+suffix]=C[252:,:4]
            arrays['inherited_Hzp_time_on_actual_parent4_'+suffix]=C[252:,4:]
            arrays['inherited_Hpz_time_on_actual_child4_'+suffix]=C[:252,:4]
            arrays['inherited_Hpp_time_on_actual_parent4_'+suffix]=C[:252,4:]
        save(f'radius_{radius:.0e}_full_clock_contracted_time_action_and_Euler_force.npz',arrays)
        mid=_mid(ht);rec=dict(radius=radius,clock_direction_normalization=scale,Hessian_time_contracted_norm=float(np.linalg.norm(mid)),
            baseline_Euler_force_time_norm=float(np.linalg.norm(_mid(ft))),
            clock_step_difference_norm=None if previous is None else float(np.linalg.norm(mid-previous)))
        records.append(rec);previous=mid
        print(json.dumps(dict(stage='actual_full_clock_contraction_control',**rec)),flush=True)
    report=dict(classification='EVALUATED_FULL_PARENT_MINUS_REFERENCE_PARENT_PLUS_REFERENCE_CHILD_CLOCK_CONTRACTIONS',
        input_hashes=pins,archives=archives,records=records,same_epoch_rate_checks=checks,
        both_reference_clock_germs_retained_once=True,reference_clock_held_to_zero=False,
        original_canonical_rate_recomputed_from_fresh_same_action=True,
        actual_baseline_Euler_force_time_first_evaluated=True,
        new_proper_stage_time_rate_solved=False,physical_terminal_derivative_admitted=False)
    p=out/'result.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='full_original_clock_contractions_finished',path=str(p))),flush=True)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,required=True)
    p.add_argument('--birth',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--columns',type=int,nargs='+',default=[0,1,2])
    p.add_argument('--first-cell',action='store_true')
    p.add_argument('--clock-first-cell',action='store_true')
    p.add_argument('--rank',type=int,default=7)
    a=p.parse_args()
    if a.clock_first_cell:run_clock_first_cell(a.repository,a.birth,a.output,rank=a.rank)
    elif a.first_cell:run_first_cell(a.repository,a.birth,a.output,columns=tuple(a.columns),rank=a.rank)
    else:run_birth(a.repository,a.birth,a.output,columns=tuple(a.columns))
