"""Consume corrected two-term birth sources on actual changing arm stages."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action,_affine_geometry
from bhsm.interface.muon_holomorphic_joint_reference_clock import joint_reference_explicit_clock
from bhsm.interface.muon_complex_canonical_midpoint import solve_complex_canonical_midpoint
from bhsm.interface.muon_warm_complex_canonical_compatibility import warm_complex_constitutive_compatibility
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_complex_paired_normal_action import complex_proper_normal_trace
from bhsm.interface.muon_changing_canonical_source import changing_stage_source,constitutive_source_two_term,split_action
from bhsm.interface.muon_moving_reference_trace_source import moving_reference_profile_source,fixed_radial_coefficient_test_restriction
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_full_profile_source_weak_application import full_profile_source_weak_application


def clean(v):
    if isinstance(v,dict):return{k:clean(x)for k,x in v.items()}
    if isinstance(v,(list,tuple)):return[clean(x)for x in v]
    if isinstance(v,np.ndarray):return clean(v.tolist())
    if isinstance(v,(complex,np.complexfloating)):return[float(v.real),float(v.imag)]
    if isinstance(v,np.generic):return v.item()
    return v


def materialize(output,step,steps,max_iterations):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve changing action applications')
    pins={};archives={}
    def read(folder,name,md=None):
        p=ROOT/folder/name;b=p.read_bytes();h=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=h
        if md is not None and h!=md['archives'][name]['sha256']:raise ValueError('same source/action archive changed')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    tf=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1')
    cf=Path('artifacts/muon_stored_admission_correction_20261012/run_1')
    sf=Path('artifacts/muon_per_arm_canonical_source_20261012/run_1')
    tm,cm,sm=[read(f,'result.json')for f in(tf,cf,sf)]
    trace=read(tf,'application.npz',tm);phase,_=retained_input('outgoing',pins);rep=phase['representation']
    P=phase['coordinates']['lift'];raw0=trace['raw_pair'];ref0=trace['reference_pair'];eta0=(P.T@raw0.T).T
    params=tm['action_parameters'];n=106;h=complex(step);guard=2e-10
    out.mkdir(parents=True)
    def save(name,obj):
        p=out/name;_compressed_npz(p,{k:v for k,v in obj.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>10*1024**2:raise ValueError('split full action/source output')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def own_parent(e):
        r=P@e;pair=np.stack((r,r))
        return holomorphic_two_arm_action(pair,pair,rep,**params)['parent']
    def child(e,t):return holomorphic_inherited_child_action(P@e,t,raw0,ref0,rep,**params)
    def graph(e,t):
        pp=_affine_geometry(raw0[0],t);rr=np.array([_affine_geometry(r,t)for r in ref0])
        return np.array([pp,P@e]),rr,holomorphic_two_arm_action(np.array([pp,P@e]),rr,rep,**params)
    initial_actions=[own_parent(eta0[0]),child(eta0[1],0)]
    initial_H_difference=float(np.max(abs(initial_actions[0]['hessian']-trace['parent_standalone_Hessian'])))
    if initial_H_difference>1e-13:raise ValueError('same complete standalone parent action required')
    initial_Pi=[trace['parent_standalone_Pi'],trace['joint_canonical_Pi'][n:]]
    base_rows=[float(np.max(abs(np.r_[a['gradient'][n:2*n]-Pi,a['gradient'][2*n:]])))for a,Pi in zip(initial_actions,initial_Pi)]
    if max(base_rows)>guard:raise ValueError('actual initial original Gauss rows must pass unchanged guard')
    frames=[canonical_central_frame(r,rep)for r in raw0]
    births={};admissions={}
    for case in('normal_basis','area_source'):
        corrected=read(cf,case+'_parent_stored_correction.npz',cm)
        ph,pl=corrected['corrected_direction_high'],corrected['corrected_direction_low']
        parent_saved=read(sf,case+'_parent_original146.npz',sm);child_saved=read(sf,case+'_child_original146.npz',sm)
        pa=constitutive_source_two_term(initial_actions[0]['hessian'],parent_saved['delta_x'],parent_saved['canonical_momentum_target'],
            parent_saved['source_gradient'],np.zeros(252),frames[0]['named_frame_covectors'],parent_saved['original_rhs'][-2:],
            dx_low=np.zeros(n),dp_low=np.zeros(n),frame_value_low=np.zeros(2))
        parent_fresh_change=float(np.linalg.norm(pa['direction_high']-ph));ph,pl=pa['direction_high'],pa['direction_low']
        save(case+'_consumed_birth_parent_source.npz',pa)
        # Consume the corrected parent rather than the old rounded source.
        inherited_h,inherited_l=split_action(trace['full_joint_Hessian'][252:,:252],ph,pl)
        original=read(sf,case+'_coupled_source_effects.npz',sm)
        gh=original['source'][252:]+inherited_h;gl=inherited_l
        fv=child_saved['original_rhs'][-2:]
        ca=constitutive_source_two_term(initial_actions[1]['hessian'],child_saved['delta_x'],child_saved['canonical_momentum_target'],gh,gl,
            frames[1]['named_frame_covectors'],fv,dx_low=np.zeros(n),dp_low=np.zeros(n),frame_value_low=np.zeros(2))
        births[case]=[(ph,pl,parent_saved['canonical_momentum_target'],np.zeros(n)),
            (ca['direction_high'],ca['direction_low'],child_saved['canonical_momentum_target'],np.zeros(n))]
        admissions[case]=dict(parent_corrected_stored_upper=cm['applications'][case+'_parent']['high_low_state']['original_action_rows_residual_upper'],
            fresh_parent_original_upper=pa['original_rows_upper'],parent_fresh_direction_change_norm=parent_fresh_change,
            child_reassembled_original_upper=ca['original_rows_upper'],child_frame_reaction_upper=ca['frame_reaction_rows_upper'],
            corrected_parent_inherited_source_change_norm=float(np.linalg.norm(gh-child_saved['source_gradient'])),
            momentum_targets_preserved=True,old_source_not_silently_reused=True,
            admitted=max(pa['original_rows_upper'],ca['original_rows_upper'])<=guard)
        save(case+'_consumed_birth_child_source.npz',ca)
        print(json.dumps(clean(dict(stage='reassembled_child_source_admission',case=case,**admissions[case])),sort_keys=True),flush=True)
    stages=[];trajectories={};base_history=[]
    for side,arm,sign in(('incoming',0,-1),('outgoing',1,1)):
        eta=eta0[arm].copy();p=initial_Pi[arm].copy();time=0j;C=frames[arm]['named_frame_covectors']
        fv0=C@eta[n:];current={}
        for case in births:
            bh,bl,dp,dpl=births[case][arm]
            fh,fl=split_action(C,bh[n:],bl[n:])
            current[case]=dict(dx=bh[:n],dxl=bl[:n],dp=dp,dpl=dpl,frameh=fh,framel=fl,active=admissions[case]['admitted'])
        trajectory=[]
        for k in range(steps):
            hs=sign*h;t=time+hs/2
            callback=(lambda e:own_parent(e)) if arm==0 else (lambda e:child(e,t))
            guess=eta.copy();guess[:n]=eta[:n]
            def checkpoint(i,z,rho,a,f,K,scale,history):
                print(json.dumps(dict(stage='changing_actual_arm_base',side=side,cell=k,**history[-1]),sort_keys=True),flush=True)
            b=solve_complex_canonical_midpoint(eta[:n],p,guess,hs,callback,frames[arm],frame_reference=eta0[arm,n:],
                tolerance=guard,max_iterations=max_iterations,checkpoint=checkpoint)
            a=b['application'];base_history.append(dict(side=side,cell=k,status=b['status'],history=b['history']))
            save(f'{side}_{k:04d}_actual_base.npz',dict(initial_master=eta,initial_Pi=p,stage_master=a['midpoint_coefficients'],stage_raw=P@a['midpoint_coefficients'],
                x_final=a['x_new'],Pi_final=a['p_new'],stage_Hessian=a['action']['hessian'],stage_gradient=a['action']['gradient'],original358_rows=a['residual'],
                original_Jacobian=a['jacobian'],frame_reactions=b['frame_reactions'],time=np.array(t),step=np.array(hs),
                initial_action_dual=a['initial_action_cotangent'],final_action_dual=a['final_action_cotangent']))
            if b['status']!='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE':
                stages.append(dict(side=side,cell=k,base_admitted=False,original_base358_max=float(np.max(abs(a['residual'])))));break
            rawstage=P@a['midpoint_coefficients'];fr=canonical_central_frame(rawstage,rep)
            if not np.array_equal(fr['named_frame_covectors'],C):raise ValueError('actual frame variation must be explicitly included if C changes')
            normal=complex_proper_normal_trace(rawstage,P)['proper_normal']
            stage_record=dict(side=side,cell=k,base_admitted=True,original_base358_max=float(np.max(abs(a['residual']))),
                actual_Hessian_change_norm=float(np.linalg.norm(a['action']['hessian']-initial_actions[arm]['hessian'])),sources={})
            if arm==1:
                pair,rr,ga=graph(a['midpoint_coefficients'],t)
                if np.max(abs(ga['hessian'][252:,252:]-a['action']['hessian']))!=0:raise ValueError('same restricted child stage Hessian required')
                clock=joint_reference_explicit_clock(pair,rr,rep,ga,nu_squared_action=params['nu_squared_action'])
                full=moving_reference_profile_source(rr,rep['rho']);coord=phase['coordinates']['dynamic_gauge_indices']
                gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(rep['rho']),80,20)
                B=gb[:,coord].transpose(0,2,1).reshape(-1,64)
                restriction=fixed_radial_coefficient_test_restriction(B,rep['radial_quadrature'],full['full_material_field_source'])
                represented=restriction['represented_source_image'].T.reshape(3,len(rep['rho']),5,4)
                complement=restriction['full_source_image_complement'].T.reshape(3,len(rep['rho']),5,4)
                wallmap=rep['wall_trace_map'].reshape(20,80)[:,coord]
                represented_wall=(wallmap@restriction['represented_source_test_coefficients']).T.reshape(3,5,4)
                complement_wall=full['full_material_wall_source']-represented_wall
                acted={name:full_profile_source_weak_application(pair,rep,ga,field,wall,nu_squared_action=params['nu_squared_action'])
                    for name,field,wall in(('full',full['full_material_field_source'],full['full_material_wall_source']),
                        ('represented',represented,represented_wall),('complement',complement,complement_wall))}
                weak_difference=acted['full']['gradient_clock_first']-clock['gradient_clock_first']
                weak_additivity=acted['full']['gradient_clock_first']-acted['represented']['gradient_clock_first']-acted['complement']['gradient_clock_first']
                save(f'{side}_{k:04d}_full_reference_source.npz',dict(**{q:v for q,v in full.items()if isinstance(v,np.ndarray)},
                    **{q:v for q,v in restriction.items()if isinstance(v,np.ndarray)},exact_clock_gradient504=clock['gradient_clock_first'],
                    parent_source_stage_raw=pair[0],reference_stage_pair=rr,
                    full_source_weak_gradient504=acted['full']['gradient_clock_first'],
                    represented_source_weak_gradient504=acted['represented']['gradient_clock_first'],
                    complementary_source_weak_gradient504=acted['complement']['gradient_clock_first'],
                    full_source_minus_exact_clock_gradient=weak_difference,
                    full_minus_represented_minus_complement_weak_gradient=weak_additivity))
                stage_record['full_reference_source_norm']=float(np.linalg.norm(full['full_material_field_source']))
                stage_record['full_reference_clock_gradient_norm']=float(np.linalg.norm(clock['gradient_clock_first']))
                stage_record['weighted_reference_complement_norms']=restriction['weighted_complement_norms']
                stage_record['weak_full_source_minus_owned_clock_max']=float(np.max(abs(weak_difference)))
                stage_record['weak_full_source_additivity_max']=float(np.max(abs(weak_additivity)))
                stage_record['weak_complement_gradient_norm']=float(np.linalg.norm(acted['complement']['gradient_clock_first']))
            else:ga=holomorphic_two_arm_action(np.stack((rawstage,rawstage)),np.stack((rawstage,rawstage)),rep,**params)
            # Reconstruct the ACTUAL endpoint v/y at the carried x/Pi before
            # evaluating its coframe or returning its fields to another domain.
            endpoint_time=time+hs;endpoint_guess=np.r_[a['x_new'],a['v_mid'],a['y_mid']]
            endpoint_callback=(lambda e:own_parent(e))if arm==0 else(lambda e:child(e,endpoint_time))
            endpoint=warm_complex_constitutive_compatibility(endpoint_guess,a['p_new'],endpoint_callback,
                canonical_central_frame(P@endpoint_guess,rep),frame_reference=eta0[arm,n:],max_iterations=max_iterations,tolerance=guard)
            stage_record['endpoint_status']=endpoint['status'];stage_record['endpoint_original146_max']=float(np.max(abs(endpoint['original_constitutive_rows'])))
            save(f'{side}_{k:04d}_actual_endpoint.npz',dict(endpoint_master=endpoint['coefficients'],endpoint_raw=P@endpoint['coefficients'],
                endpoint_Pi=a['p_new'],endpoint_gradient=endpoint['action']['gradient'],endpoint_Hessian=endpoint['action']['hessian'],
                endpoint_original146_rows=endpoint['original_constitutive_rows'],endpoint_frame_reactions=endpoint['frame_reactions'],
                endpoint_time=np.array(endpoint_time),literal_stage_generators=fr['literal_generators'],
                literal_stage_generator_image=a['action']['hessian'][n:,n:]@fr['literal_generators']))
            endpoint_normal=complex_proper_normal_trace(P@endpoint['coefficients'],P)['proper_normal']
            for case in births:
                if not current[case]['active']:continue
                q=current[case];sh=np.zeros(252,complex);sl=np.zeros(252,complex)
                if arm==1:
                    ph,pl=births[case][0][:2]
                    iph=P.T@_affine_geometry(P@ph,t);ipl=P.T@_affine_geometry(P@pl,t)
                    sh,sl=split_action(ga['hessian'][252:,:252],iph,ipl)
                if case=='area_source':sh=sh+ga['area_gradient_per_gamma'][arm*252:(arm+1)*252]
                v=changing_stage_source(b,q['dx'],q['dp'],sh,sl,C,q['frameh'],q['framel'],normal,delta_x_low=q['dxl'],delta_p_low=q['dpl'])
                va=v.pop('arrays');va.update(stage_raw=rawstage,stage_raw_direction_high=P@va['stage_direction_high'],stage_raw_direction_low=P@va['stage_direction_low'],
                    parent_source_stage_raw=(pair[0]if arm else rawstage),reference_stage_pair=(rr if arm else ref0),
                    coordinate_time=np.array(t),coordinate_time_step=np.array(hs))
                if arm:
                    va.update(parent_source_stage_raw_direction_high=P@iph,parent_source_stage_raw_direction_low=P@ipl)
                else:va.update(parent_source_stage_raw_direction_high=va['stage_raw_direction_high'],parent_source_stage_raw_direction_low=va['stage_raw_direction_low'])
                # Sources have held reference seed; its nonzero clock motion is in stage reevaluation, once.
                va['reference_stage_direction_high']=np.zeros((2,268),complex);va['reference_stage_direction_low']=np.zeros((2,268),complex)
                save(f'{side}_{k:04d}_{case}_source_response.npz',va)
                v['all_original_source_rows_admitted']=v['original_rows_upper']<=guard
                stage_record['sources'][case]=v
                v['normal_pairing_scope']='midpoint coframe applied to final displacement; actual endpoint coframe separately reconstructed'
                q['dx']=va['stage_solution_high'][:n];q['dxl']=va['stage_solution_low'][:n]
                q['dp']=va['stage_solution_high'][n:2*n];q['dpl']=va['stage_solution_low'][n:2*n]
                if endpoint['status']=='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':
                    eg=np.zeros(252,complex);egl=np.zeros(252,complex)
                    if arm:
                        epair,eref,ea=graph(endpoint['coefficients'],endpoint_time)
                        ph,pl=births[case][0][:2]
                        eph=P.T@_affine_geometry(P@ph,endpoint_time);epl=P.T@_affine_geometry(P@pl,endpoint_time)
                        eg,egl=split_action(ea['hessian'][252:,:252],eph,epl)
                    else:
                        eraw=P@endpoint['coefficients'];ea=holomorphic_two_arm_action(np.stack((eraw,eraw)),np.stack((eraw,eraw)),rep,**params)
                    if case=='area_source':eg+=ea['area_gradient_per_gamma'][arm*252:(arm+1)*252]
                    ev=constitutive_source_two_term(endpoint['action']['hessian'],q['dx'],q['dp'],eg,egl,C,q['frameh'],
                        dx_low=q['dxl'],dp_low=q['dpl'],frame_value_low=q['framel'])
                    ev.update(endpoint_raw=P@endpoint['coefficients'],endpoint_raw_direction_high=P@ev['direction_high'],
                        endpoint_raw_direction_low=P@ev['direction_low'],endpoint_normal_covector=endpoint_normal,
                        endpoint_Pi=a['p_new'],endpoint_time=np.array(endpoint_time))
                    save(f'{side}_{k:04d}_{case}_endpoint_source_response.npz',ev)
                    nh,nl=split_action(endpoint_normal[None,:],q['dx'],q['dxl'])
                    v['actual_endpoint_normal_pairing_high']=complex(nh[0]);v['actual_endpoint_normal_pairing_low']=complex(nl[0])
                    v['actual_endpoint_original_source146_upper']=ev['original_rows_upper']
                if not v['all_original_source_rows_admitted']:
                    # Preserve failed application; it cannot become a subsequent admitted stage.
                    q['active']=False
            stages.append(stage_record);trajectory.append(a['midpoint_coefficients'])
            print(json.dumps(clean(dict(stage='changing_actual_arm_source_complete',**stage_record)),sort_keys=True),flush=True)
            if endpoint['status']!='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':break
            eta=endpoint['coefficients'];p=a['p_new'];time+=hs
        trajectories[side]=trajectory
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:r=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            pins[r]=sha256((ROOT/r).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same source action changed during execution')
    result=dict(classification='EVALUATED_CHANGING_NONLINEAR_CANONICAL_ARM_SOURCE_APPLICATION',archives=archives,input_hashes=pins,
        action_parameters=params,tolerance=guard,step=[h.real,h.imag],requested_steps=steps,initial_base_Gauss_max=base_rows,
        admissions=admissions,stages=stages,base_history=base_history,
        reevaluated_initial_parent_Hessian_minus_pinned_max=initial_H_difference,
        original_base_momentum_targets_preserved=True,
        inherited_child_source='owned affine parent first germ at child positive coordinate-time increment; actual incoming solve is separately negative oriented and is not grafted as an incoming future',
        full_moving_profile_and_complement_retained_before_action_restriction=True,
        base_and_source_coefficients_recomputed_at_actual_stages=True,
        birth_reset73_never_continuous_bulk_constraints=True,named_frame_fixed_by_retained_representation=True,
        literal_gauge_generator_recomputed_on_changing_stage=True,
        physical_formation_or_first_hit_or_pole_or_native_Pauli_selected=False,
        error_scope='binary actual finite nonlinear action/stage coefficients; two-term 192-bit arithmetic source application with literal original358 residuals; no stage truncation, continuum, source-domain or anomaly enclosure')
    p=out/'result.json';p.write_text(json.dumps(clean(result),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='changing_canonical_source_application_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--step',type=complex,default=1e-8);p.add_argument('--steps',type=int,default=2);p.add_argument('--max-iterations',type=int,default=6)
    a=p.parse_args();materialize(a.output,a.step,a.steps,a.max_iterations)
