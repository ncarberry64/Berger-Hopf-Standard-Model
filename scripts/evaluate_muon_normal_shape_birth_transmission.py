"""Source-completed field/trace birth transmission and actual born-child IVP.

The remaining geometric/energy natural rows are exported, not suppressed.
Held geometry coordinates complete this declared computational response;
they do not select the physical exterior, formation mode or environment.
"""
from pathlib import Path
from hashlib import sha256
import argparse,itertools,json,sys
import numpy as np
from flint import acb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_normal_shape_birth_transmission import canonical_source_transmission
from bhsm.interface.muon_normal_shape_induced_canonical_response import forced_original_canonical_jacobi,source_complete_true_face
from bhsm.interface.muon_fixed_parent_finite_shooting import ward_canonical_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_stored_admission_correction import _matrix,_mid
from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(incoming,child,rate_source,weak_source,history,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every transmitted source application')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    im=read(incoming,'result.json');cm=read(child,'result.json');hm=read(history,'result.json')
    resetfolder=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1')
    rm=read(resetfolder,'result.json');reset=read(resetfolder,'application.npz');J=reset['original226_Jacobian'];groups=rm['groups']
    fiber=read(Path('artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000'),'action_and_shooting_rows.npz')
    trace=read(Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1'),'application.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    pair,ref=reset['raw_pair'],reset['reference_pair'];eta=P.T@pair[1];F=canonical_central_frame(pair[1],rep)['named_frame_covectors']
    pi=trace['joint_canonical_Pi'][106:]
    wardmap=canonical_central_frame(pair[1],rep)['literal_generators'][:106].T
    piv=max(itertools.combinations(np.flatnonzero(np.max(abs(wardmap),axis=0)>0).tolist(),2),key=lambda p:abs(np.linalg.det(wardmap[:,p])))
    keep=np.array([i for i in range(106)if i not in piv])
    packet=ward_canonical_input(pair[1],rep,pi[keep],pivot_columns=piv)
    E=packet['canonical_embedding'];keep_pi=packet['independent_momentum_columns']
    coords=generic=rep['gauge_labels'];coordinates=phase['coordinates']
    # The two excluded field-dual rows are the fixed rank2 central minor.
    dyn=coordinates['dynamic_gauge_indices'];Ar=[j for j,i in enumerate(dyn)if coords[i]['field']=='A_rho'and coords[i]['internal']==3]
    candidates=np.array(groups['gauge_temporal_dual'])[Ar]
    dependent=max(itertools.combinations(candidates.tolist(),2),key=lambda p:abs(np.linalg.det(reset['Ward_rows'][:,p])))
    traces=np.array(groups['gauge_trace']+groups['Higgs_trace']+groups['moving_geometric_trace']+groups['normal_position_trace'])
    fields=np.array([i for i in groups['gauge_temporal_dual']+groups['Higgs_temporal_dual']if i not in dependent])
    selected=np.r_[traces,fields]
    if len(traces)!=73 or len(fields)!=66:raise ValueError('original73 trace and66 Ward-independent field-dual rows required')
    C=np.zeros((71,210),complex);C[:33]=fiber['fiber_coordinate_map'][:33]
    geom_pi=np.array([np.flatnonzero(keep_pi==j)[0]for j in range(38)])
    C[33+np.arange(38),106+geom_pi]=1
    scales=np.r_[1/read(Path('artifacts/muon_coupled_birth_full_application_20261012/run_1'),'actual_full_birth_action.npz')['weights'][74:98],np.ones(16)]
    names=('initial','cell_0000','corner_0000','cell_0001','final');points={}
    print(json.dumps(dict(stage='fresh_actual_child_source_blocks_started')),flush=True)
    for name in names:
        w=read(weak_source,name+'_shape_weak_application.npz');r=read(rate_source,name+'_bounded_rate_and_shape.npz')
        a=holomorphic_two_arm_action(w['raw_pair'],w['reference_pair'],rep,**hm['action_parameters'])
        points[name]=dict(w=w,r=r,H=a['hessian'][252:,252:],Hcp=a['hessian'][252:,:252],
            H_difference=float(np.max(abs(a['hessian'][252:,252:]-r['literal_child_Hessian']))))
        print(json.dumps(dict(stage='actual_source_block',point=name,H_difference=points[name]['H_difference'])),flush=True)
    if not np.array_equal(points['initial']['w']['raw_pair'],pair)or not np.array_equal(points['initial']['w']['reference_pair'],ref):
        raise ValueError('exact COMMON birth pair/reference required before transmission')
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split source/transmission arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def split_sum(*pairs):
        old=ctx.prec;ctx.prec=192
        try:
            q=acb_mat(pairs[0][0].shape[0],pairs[0][0].shape[1])
            for h,l in pairs:q+=_matrix(h)+_matrix(l)
            return _split(q)
        finally:ctx.prec=old
    def product(A,h,l):
        old=ctx.prec;ctx.prec=192
        try:return _split(_matrix(A)*(_matrix(h)+_matrix(l)))
        finally:ctx.prec=old
    def sum_app(a,b,keys):
        data={}
        for key in keys:
            data[key+'_high'],data[key+'_low']=split_sum((a[key+'_high'],a[key+'_low']),(b[key+'_high'],b[key+'_low']))
        return data
    def row_groups(rows):
        return{name:dict(maximum=float(np.max(abs(rows[ids]))),worst_original_row=ids[int(np.argmax(abs(rows[ids])))])for name,ids in groups.items()}
    records=[];sectors=[];guard=2e-10
    for sector in('base','area'):
        p=read(incoming,sector+'_birth_induced_and_total.npz');oldchild=read(child,sector+'_initial_induced_and_total.npz')
        dp=(p['total_phase_high'],p['total_phase_low']);H0=points['initial']['H']
        if not np.array_equal(p['actual_raw'],pair[0]):raise ValueError('OWN parent birth target changed')
        direct=(oldchild['direct_phase_high'],oldchild['direct_phase_low'])if sector=='base'else(np.zeros((252,1),complex),np.zeros((252,1),complex))
        old_g=points['initial']['r']['literal_two_term_rhs_'+sector+'_bulk_source'][252:]
        source_pair=split_sum((old_g[:,None],np.zeros((252,1),complex)),product(points['initial']['Hcp'],*dp))
        bparent=p['direct_phase_high']+p['direct_phase_low']if sector=='base'else np.zeros((252,1),complex)
        qp=p['effective_source'][:,None]-p['original_own_Hessian']@bparent
        qc=old_g[:,None]-H0@(direct[0]+direct[1])
        extra=np.zeros((226,1),complex);extra[groups['incoming_constraints']]=scales[:,None]*qp[212:]
        extra[groups['child_constraints']]=scales[:,None]*qc[212:]
        extra[groups['gauge_temporal_dual']+groups['Higgs_temporal_dual']]=qp[144:212]-qc[144:212]
        oldq=oldchild['effective_canonical_high']+oldchild['effective_canonical_low']
        controls=np.r_[oldq[:106,0],oldq[106+keep_pi,0]]
        a=canonical_source_transmission(H0,F,E,J[:,:252],J[:,252:],*dp,*source_pair,*direct,extra,selected,C,(C@controls)[:,None])
        aa=a['arrays'];qh,ql=aa['effective_canonical_high'],aa['effective_canonical_low']
        ih,il=aa['induced_phase_high'],aa['induced_phase_low'];th,tl=aa['total_phase_high'],aa['total_phase_low']
        state_parts={}
        for name,d in(('parent_direct',(p['direct_phase_high'],p['direct_phase_low'])if sector=='base'else(np.zeros_like(dp[0]),np.zeros_like(dp[1]))),
            ('parent_induced',(p['induced_phase_high'],p['induced_phase_low'])),('child_direct',direct),('child_induced',(ih,il))):
            block=J[:,:252]if name.startswith('parent')else J[:,252:]
            h,l=product(block,*d);state_parts[name+'_image_high']=h;state_parts[name+'_image_low']=l
        image=aa['all_original_state_and_known_source_rows_high']+aa['all_original_state_and_known_source_rows_low']
        rawstate=split_sum(product(J[:,:252],*dp),product(J[:,252:],th,tl))
        base_plus=reset['original226_rows'][:,None]+image
        rcoef=points['initial']['r']['literal_two_term_rhs_'+sector+'_boundary_source']
        full_boundary=np.r_[p['full_rate_conormal']-rcoef[:252],-rcoef[252:]]
        data=dict(**aa,**state_parts,raw_pair=pair,reference_pair=ref,original226_BASE=reset['original226_rows'],
            original226_Jacobian=J,known_extra_action_source_rows=extra,unknown_natural_source_rows=np.array(groups['incoming_energy']+groups['child_energy']+groups['common_attachment_temporal_dual']+groups['common_normal_temporal_dual']),
            state_image_high=rawstate[0],state_image_low=rawstate[1],BASE_plus_state_and_known_source_rows=base_plus,
            named_Ward_rows=reset['Ward_rows'],Ward_completed_source_image=reset['Ward_rows']@image,
            selected_original_rows=selected,named_dependent_field_dual_rows=np.array(dependent),held_coordinate_map=C,held_coordinate_target=(C@controls)[:,None],
            full_incoming_plus_child_initial_rate_boundary_covector=full_boundary,
            parent_extra_mixed_source=qp,child_extra_mixed_source=qc,actual_parent_total_phase_high=dp[0],actual_parent_total_phase_low=dp[1],
            actual_parent_total_raw_high=p['total_raw_high'],actual_parent_total_raw_low=p['total_raw_low'],
            actual_child_total_raw_high=product(P,th,tl)[0],actual_child_total_raw_low=product(P,th,tl)[1],named_frame_covectors=F)
        save(sector+'_birth_transmission_and_all226.npz',data)
        admitted=a['selected_rows_upper']<=guard and a['original_constitutive_upper']<=guard and a['frame_reaction_upper']<=guard
        rec=dict(sector=sector,conditional_field_trace_transmission_passed=admitted,selected139_upper=a['selected_rows_upper'],
            original146_upper=a['original_constitutive_upper'],frame_reaction_upper=a['frame_reaction_upper'],square_upper=a['square_residual_upper'],
            ALL226_state_and_known_source_groups=row_groups(image[:,0]),BASE_plus_state_and_known_source_groups=row_groups(base_plus[:,0]),
            extra_geometric_natural_source_Hessian_not_supplied_as_zero=True,
            full_rate_boundary_covector_norm=float(np.linalg.norm(full_boundary)),total_parent_phase_norm=float(np.linalg.norm(dp[0]+dp[1])),
            total_child_phase_norm=float(np.linalg.norm(th+tl)))
        print(json.dumps(clean(dict(stage='conditional_birth_transmission',**rec)),sort_keys=True),flush=True)
        outputs={};propagation=[]
        if admitted:
            for name in names:
                pp=points[name];H=pp['H'];t=pp['w']['coordinate_time'].item();Jaff=np.eye(252,dtype=complex)
                Jaff[np.arange(37),106+np.arange(37)]+=t;Jaff[37,143]+=t
                inherited=product(pp['Hcp']@Jaff,*dp)
                old=pp['r']['literal_two_term_rhs_'+sector+'_bulk_source'][252:]
                gh,gl=split_sum((old[:,None],np.zeros((252,1),complex)),inherited)
                B=pp['r']['literal_two_term_rhs_'+sector+'_boundary_source'][252:]
                zq=np.zeros_like(qh)
                if name.startswith('cell_'):
                    k=int(name[5:]);stage=read(history,f'step_{k:04d}_stage.npz');h=stage['coordinate_step'].item()
                    ah=forced_original_canonical_jacobi(H,h,F,qh,ql,gh[:,0]);al=forced_original_canonical_jacobi(H,h,F,zq,zq,gl[:,0])
                    comb=sum_app(ah,al,('effective_canonical_final','induced_stage_direction','original_action_cotangent_first','solution'))
                    qh,ql=comb['effective_canonical_final_high'],comb['effective_canonical_final_low'];ci=(comb['induced_stage_direction_high'],comb['induced_stage_direction_low'])
                    pr=dict(point=name,original358_upper=ah['original_forced_rows_upper']+al['original_forced_rows_upper'],
                        frame_reaction_upper=ah['frame_reaction_rows_upper']+al['frame_reaction_rows_upper'],framed_upper=ah['framed_rows_upper']+al['framed_rows_upper'])
                else:
                    ah=source_complete_true_face(H,F,qh,ql,gh[:,0],B);al=source_complete_true_face(H,F,zq,zq,gl[:,0],B)
                    comb=sum_app(ah,al,('induced_phase','original_Pi_first','effective_p_minus_g_v'))
                    ci=(comb['induced_phase_high'],comb['induced_phase_low'])
                    pr=dict(point=name,original146_upper=ah['original_forced_rows_upper']+al['original_forced_rows_upper'],
                        frame_reaction_upper=ah['frame_reaction_rows_upper']+al['frame_reaction_rows_upper'],framed_upper=ah['framed_rows_upper']+al['framed_rows_upper'],
                        complete_rate_work=(ah['complete_rate_work']+al['complete_rate_work']).item())
                prior=read(child,sector+'_'+name+'_induced_and_total.npz')
                db=(prior['direct_phase_high'],prior['direct_phase_low'])if sector=='base'else(np.zeros_like(ci[0]),np.zeros_like(ci[1]))
                ct=split_sum(ci,db);additional=split_sum(ci,(-prior['induced_phase_high'],-prior['induced_phase_low']))
                point_arrays=dict(comb)
                point_arrays.update(
                    induced_phase_high=ci[0],induced_phase_low=ci[1],total_phase_high=ct[0],total_phase_low=ct[1],
                    additional_born_induced_phase_high=additional[0],additional_born_induced_phase_low=additional[1],
                    total_raw_high=product(P,*ct)[0],total_raw_low=product(P,*ct)[1],additional_born_induced_raw_high=product(P,*additional)[0],additional_born_induced_raw_low=product(P,*additional)[1],
                    parent_born_total_phase_high=dp[0],parent_born_total_phase_low=dp[1],parent_affine_phase_high=product(Jaff,*dp)[0],parent_affine_phase_low=product(Jaff,*dp)[1],
                    parent_affine_raw_high=product(P@Jaff,*dp)[0],parent_affine_raw_low=product(P@Jaff,*dp)[1],
                    inherited_parent_source_high=inherited[0],inherited_parent_source_low=inherited[1],source_high=gh,source_low=gl,
                    effective_canonical_high=qh,effective_canonical_low=ql,actual_raw_pair=pp['w']['raw_pair'],actual_reference_pair=pp['w']['reference_pair'],
                    actual_coordinate_time=np.array(t),full_rate_conormal=B,
                    high_source_original_rows=ah.get('original_forced_rows',ah.get('original_forced146_rows')),
                    low_source_original_rows=al.get('original_forced_rows',al.get('original_forced146_rows')),
                    high_source_frame_reaction_rows=ah['frame_reaction_rows'],low_source_frame_reaction_rows=al['frame_reaction_rows'],
                    named_frame_covectors=F)
                save(sector+'_'+name+'_linked_response.npz',point_arrays)
                propagation.append(pr);print(json.dumps(clean(dict(stage='linked_original_child_response',sector=sector,**pr)),sort_keys=True),flush=True)
        rec['propagation']=propagation;records.append(rec)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_normal_shape_birth_transmission.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same birth/source/domain changed')
    result=dict(classification='EXECUTED_SOURCE_COMPLETED_CONDITIONAL_BIRTH_FIELD_TRANSMISSION_AND_BORN_CHILD_RESPONSE',
        input_hashes=pins,archives=archives,records=records,action_parameters=hm['action_parameters'],
        original_BASE226_groups=row_groups(reset['original226_rows']),
        selected_rows='73 original endpoint traces plus66 field natural duals; two exact Ward-dependent field rows audited',
        held_coordinates='33 free geometry positions and38 geometry momenta at supplied previous conditional source values; not a physical outgoing selector',
        source_law='child g=old mixed shape Euler source+Hcp J_affine(t) totalbornparent; high/low retained, reference source held',
        BASE_not_solved_by_setting_source_image_zero=True,
        complete_natural_source_projection_not_claimed=True,
        required_natural_source_action='Same chronological domain weak Fshape Hessian including state/rate and boundary/source pullback, six full phase port/adjoint lifts; no deltaD=0 substitution',
        common_gamma_coefficient_not_assigned_or_child_only=True,
        physical_environment_formation_energy_gamma_c_retarded_pole_or_LSZ_matching_admitted=False,
        scope='Executed finite same action stored-source response and all226 state/known-source images; natural geometric/energy source completion and BASE matching remain explicit. No error enclosure.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='linked_birth_response_complete',result_sha256=sha256(p.read_bytes()).hexdigest()),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--incoming',type=Path,default=Path('artifacts/muon_incoming_shape_induced_response_20261013/run_1'))
    p.add_argument('--child',type=Path,default=Path('artifacts/muon_normal_shape_induced_canonical_response_20261013/run_1'))
    p.add_argument('--rate-source',type=Path,default=Path('artifacts/muon_normal_shape_rate_attribution_20261012/run_1'))
    p.add_argument('--weak-source',type=Path,default=Path('artifacts/muon_normal_shape_weak_consumption_20261012/run_1'))
    p.add_argument('--history',type=Path,default=Path('artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.incoming,a.child,a.rate_source,a.weak_source,a.history,a.output)
