"""Continue one new retarded compatible368 cell on its actual nonlinear epoch.

The direct CHILD scalar is applied to every candidate column. A saved true
nearby Hessian only preconditions the solve. Full252 inherited source and
affine primal contacts are retained; this is no physical exterior/lineage.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'


def run(repository,cauchy,operator,midpoint,clock,birth,mp_tables,output,*,maximum_iterations=12):
    root,qpath,apath,mpath,tpath,bpath,lpath,out=map(lambda p:Path(p).resolve(),(repository,cauchy,operator,midpoint,clock,birth,mp_tables,output))
    out.mkdir(parents=True,exist_ok=False);producer=Path(__file__).read_bytes();(out/'initial_producer.py').write_bytes(producer)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    import numpy as np
    from flint import ctx,acb_mat
    from bhsm_baton_zoo_compatible_mp_current_flow import _snapshot_module
    from bhsm_baton_zoo_matrix_free_canonical_cell import canonical_cell
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_holomorphic_child_action import _affine_geometry
    from bhsm.interface.muon_changing_weak_birth_action import affine_parent_master_map
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=192;pins={}
    def read(p):
        pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def exact(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def split(vals):
        arrays={}
        for k,v in vals.items():arrays[k+'_high'],arrays[k+'_low']=_split(v)
        return arrays
    q,a,m,c,b,l=map(read,(qpath,apath,mpath,tpath,bpath,lpath))
    snapshot=mpath.parent/'bhsm_baton_zoo_phase_clock_analytic_jet_imported_runtime.py'
    binary_snapshot=mpath.parent/'bhsm_baton_zoo_augmented_source_domain_derivative_imported_runtime.py'
    binary,binarypin=_snapshot_module('bhsm_baton_zoo_augmented_source_domain_derivative',binary_snapshot,out)
    packed,packedpin=_snapshot_module('bhsm_baton_zoo_phase_clock_analytic_jet',snapshot,out)
    phase,_=retained_input('outgoing',pins);rep,P=phase['representation'],phase['coordinates']['lift']
    params=read(root/'artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    born=read(root/'artifacts/muon_birth_full_proper_port_saddle_20261013/run_1/birth_fixed_germ_and_source_compatibility.npz')
    n,dim,nc=158,368,7;original=np.asarray(a['original252_to_augmented368'],int);extra=np.asarray(a['extra116_to_full'],int)
    maps=dict(old504_to_full=np.r_[np.arange(252),252+original],extra_coordinates_to_full=extra,full_dimension=620,child_original252_to_augmented=original)
    for k in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        for part in('high','low'):maps[k+'_'+part]=l[k+'_'+part]
    for key,owner in[('extra_point_lift','compatible_extra_point_lift'),('extra_wall_lift','compatible_extra_wall_lift')]:
        for part in('high','low'):maps[key+'_'+part]=l[owner+'_'+part]
    maps['extra_point_lift']=maps['extra_point_lift_high']+maps['extra_point_lift_low']
    eta=m['midpoint_master368'];time=m['coordinate_time'].item();step=m['step'].item()
    start=q['authoritative_node_time'].item();tag_delta=_matrix([[time-step/2]])[0,0]-_matrix([[start]])[0,0]
    if abs(complex(tag_delta))>1e-18:raise ValueError('current response cell must begin at the identified accepted Cauchy node')
    if not np.array_equal(eta,c['master368']):raise ValueError('complete current midpoint and continuous clock state must be identical')
    raw=np.array([_affine_geometry(born['raw_pair'][0],time),P@eta[original]])
    refs=np.array([_affine_geometry(x,time)for x in born['reference_pair']]);zero=np.zeros((620,1),complex)
    selected=np.asarray(a['all_selected_full_action_indices'],int);active=np.asarray(a['action_active_parent_source_indices100'],int)
    if not np.array_equal(selected,np.r_[active,252+np.arange(dim)]):raise ValueError('explicit direct CHILD source/current selector required')
    Q=exact(q,'retarded_and_homogeneous_separate316');Up=exact(b,'fixed_position_parent_phase');J=_matrix(affine_parent_master_map(time));parent=acb_mat(252,nc);pu=J*Up
    for i in range(252):
        for j in range(3):parent[i,1+j]=pu[i,j]
    g=exact(m,'phase_gradient');totalclock=exact(c,'phase_gradient_first');force=acb_mat(dim,nc)
    for i in range(n):force[i,0]=g[i,0]-totalclock[i,0]
    for i in range(2*n,dim):force[i,0]=g[i,0]
    max_gradient_difference=0.;calls=0
    def apply(child,source):
        nonlocal calls,max_gradient_difference
        R=_cat(source,child);rh,rl=_split(R)
        z=packed.phase_action_contractions(raw,refs,rep,P,maps,selected,zero,zero,rh,rl,extra_base=eta[extra-252],
            include_directional_first=False,include_parent_action=False,nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'],precision_bits=192)
        value=exact(z,'phase_Hessian_on_actual_right');gradient=exact(z,'phase_gradient');sourcecot=acb_mat(252,nc);sourceg=acb_mat(252,1)
        for i,slot in enumerate(active):
            sourceg[int(slot),0]=gradient[i,0]
            for j in range(nc):sourcecot[int(slot),j]=value[i,j]
        max_gradient_difference=max(max_gradient_difference,_upper(_rows(gradient,100,468)-g));calls+=1
        print(json.dumps(dict(stage='same_current_direct_CHILD_action_vector_applied',call=calls,gradient_difference_upper=max_gradient_difference)),flush=True)
        return dict(child_cotangent=_rows(value,100,468),parent_cotangent252=sourcecot,direct_child_source_gradient252=sourceg)
    H=exact(a,'true_child_Hessian368');F=a['completed_frames']
    app=canonical_cell(H,step,F,Q,parent,apply,force,guard=2e-10,max_iterations=maximum_iterations,precision_bits=192,
        checkpoint=lambda r:print(json.dumps(dict(stage='actual_matrixfree_original526_response_rows',**r)),flush=True))
    passing=app['status']=='ALL_ACTUAL_MATRIX_FREE_ORIGINAL_CANONICAL_ROWS_PASS'and max_gradient_difference<=2e-10
    oldreturn=exact(q,'existing_full252_source_return');source7=app['values']['parent_source_cotangent'];source4=acb_mat(252,4)
    for i in range(252):
        source4[i,0]=source7[i,0]+app['values']['actual_affine_primal_source_gradient252'][i,0]
        for j in range(3):source4[i,1+j]=source7[i,1+j]+source7[i,4+j]
    increment=_matrix([[step]])[0,0]*J.transpose()*source4;returned=oldreturn+increment
    finalQ=app['values']['final_canonical'];combined=acb_mat(316,4)
    for i in range(316):
        combined[i,0]=finalQ[i,0]
        for j in range(3):combined[i,1+j]=finalQ[i,1+j]+finalQ[i,4+j]
    packet=dict(app['arrays'],coordinate_time=np.asarray(time),step=np.asarray(step),authoritative_node_time=np.asarray(time+step/2),completed_frames=F,
        original252_to_augmented368=original,extra116_to_full=extra,actual_midpoint_master368=eta,actual_midpoint_packet=np.asarray(str(mpath)),
        **split(dict(retarded_and_homogeneous_separate316=finalQ,combined_four_Cauchy316=combined,actual_parent_source252=parent,
            baseline_Euler_force368x7=force,existing_full252_source_return=returned,full252_inherited_source_return_increment=increment,all_four_source_cotangent252=source4)))
    p=out/'actual_new_only_compatible316_response_and_full252_source_return.npz';_compressed_npz(p,packet)
    result=dict(classification='ACTUAL_CURRENT_NONZERO_COMPATIBLE368_MATRIX_FREE_RETARDED_CELL_AND_FULL252_SOURCE_RETURN',status=app['status'],admitted_finite_cell=passing,
        original526_rows_upper=app['original_rows_upper'],framed_rows_upper=app['framed_rows_upper'],records=app['records'],same_scalar_gradient_reproduction_upper=max_gradient_difference,
        source_full252_retained=True,source_parent_profile_and_both_reference_clocks_once=True,primal_affine_Gp_source_offset_retained=True,
        baseline_force_upper=_upper(force),source_return_increment_upper=_upper(increment),preconditioner_substituted_as_operator=False,
        source_midpoint_clock_tag_delta_upper=float(tag_delta.abs_upper()),continuous_clock_time_tag=[c['coordinate_time'].item().real,c['coordinate_time'].item().imag],
        current_midpoint_time_tag=[time.real,time.imag],old_integrations_repeated=False,physical_outgoing_or_reset_or_lineage_or_original226_admitted=False,
        inputs=pins,imported_runtime_dependencies=[binarypin,packedpin],producer_sha256=sha256(producer).hexdigest(),packet_sha256=sha256(p.read_bytes()).hexdigest())
    f=out/'result.json';f.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');(out/'executed_producer.py').write_bytes(producer)
    print(json.dumps(dict(stage='actual_new_only_retarded_cell_checkpoint',status=app['status'],admitted_finite_cell=passing,original526_rows_upper=app['original_rows_upper'],result_sha256=sha256(f.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in('repository','cauchy','operator','midpoint','clock','birth','mp-tables','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--maximum-iterations',type=int,default=12)
    a=p.parse_args();run(a.repository,a.cauchy,a.operator,a.midpoint,a.clock,a.birth,a.mp_tables,a.output,maximum_iterations=a.maximum_iterations)
