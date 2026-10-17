"""Continue actual368 with MP master variables and exact affine clocks.

The same MP scalar gradient controls every original canonical/Gauss row.
Rounded Hessians only precondition Newton. Child master coordinates and
parent/reference affine clock formation preserve their high/low parts.
No checkpoint or numerical stall is interpreted as a physical exit.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,os,sys
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'


def _affine_ball(raw,time):
    from bhsm.interface.muon_stored_admission_correction import _matrix
    x=_matrix(raw)
    for i in range(37):x[i,0]+=time*x[37+i,0]
    x[98,0]+=time*x[99,0]
    return x


def _action(e,time,context):
    import numpy as np
    from flint import acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_split
    rep,P,maps,initial,reference,parameters,packed,binary,chart=context;dim=e.nrows()
    original=np.asarray(maps['child_original252_to_augmented'],int);extra=np.asarray(maps['extra_coordinates_to_full'],int)-252
    original_eta=acb_mat([[e[int(i),0]]for i in original]);child=_matrix(P)*original_eta;parent=_affine_ball(initial[0],time)
    rawh,rawl=_split(acb_mat([[parent[i,0]for i in range(268)],[child[i,0]for i in range(268)]]))
    refs=[_affine_ball(x,time)for x in reference];refh,refl=_split(acb_mat([[x[i,0]for i in range(268)]for x in refs]))
    ex=acb_mat([[e[int(i),0]]for i in extra]);exh,exl=_split(ex);zero=np.zeros((252+dim,1),complex)
    approximate=binary.augmented_scalar_action(rawh+rawl,refh+refl,(exh+exl)[:,0],rep,maps,action_parameters=parameters)
    precise=packed.phase_action_contractions(rawh,refh,rep,P,maps,252+np.arange(dim),zero,zero,zero,zero,
        raw_pair_low=rawl,reference_pair_low=refl,extra_base=exh[:,0],extra_base_low=exl[:,0],include_directional_first=False,
        material_chart_precision=chart,nu_squared_action=parameters['nu_squared_action'],surface_gamma=parameters['surface_gamma'])
    gradient=_matrix(precise['phase_gradient_high'])+_matrix(precise['phase_gradient_low'])
    return dict(gradient=gradient,preconditioner=approximate['Hessian'][252:,252:],precise=precise,
        raw_pair_high=rawh,raw_pair_low=rawl,reference_pair_high=refh,reference_pair_low=refl)


def _warm(e,Pi,evaluate,F,reference,*,guard=2e-10,max_iterations=20,checkpoint=None):
    import numpy as np
    from flint import acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat
    e=acb_mat(e);n=Pi.nrows();dim=e.nrows();C=_matrix(F);nf=C.nrows();rho=acb_mat(nf,1);records=[];status='ITERATION_LIMIT'
    fixed=_rows(e,0,n)
    def apply(x,r):
        a=evaluate(x);g=a['gradient'];raw=_cat(_rows(g,n,2*n)-Pi,_rows(g,2*n,dim));frame=C*(_rows(x,n,dim)-reference)
        rows=_cat(raw+C.transpose()*r,frame);H=a['preconditioner'];K=_matrix(np.block([[H[n:,n:],F.T],[F,np.zeros((nf,nf),complex)]]))
        return a,raw,rows,K
    a,raw,rows,K=apply(e,rho)
    for iteration in range(max_iterations+1):
        rec=dict(iteration=iteration,original_rows_upper=_upper(raw),framed_rows_upper=_upper(rows));records.append(rec)
        if checkpoint:checkpoint(rec)
        if _upper(raw)<=guard and _upper(rows)<=guard:status='ALL_MP_ORIGINAL_CONSTITUTIVE_ROWS_PASS';break
        if iteration==max_iterations:break
        correction=K.solve(-rows);merit=float(np.linalg.norm(_mid(rows)));accepted=False
        for half in range(12):
            fraction=2.**(-half);trial=_cat(fixed,_rows(e,n,dim)+fraction*_rows(correction,0,dim-n));rt=rho+fraction*_rows(correction,dim-n,dim-n+nf)
            try:at,rr,fr,kt=apply(trial,rt);nextmerit=float(np.linalg.norm(_mid(fr)))
            except(ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):continue
            if np.isfinite(nextmerit)and nextmerit<merit:e,rho,a,raw,rows,K=trial,rt,at,rr,fr,kt;rec['accepted_fraction']=fraction;accepted=True;break
        if not accepted:status='MP_GRADIENT_LINE_SEARCH_STALL';break
    return dict(master=e,action=a,original_rows=raw,framed_rows=rows,frame_reactions=rho,status=status,records=records)


def _cell(x0,p0,guess,step,evaluate,F,reference,*,guard=2e-10,max_iterations=20,checkpoint=None):
    import numpy as np
    from flint import acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat
    n=p0.nrows();dim=guess.nrows();d=dim+n;nf=len(F);C=_matrix(F);rho=acb_mat(nf,1);h=_matrix([[step]])[0,0]
    first=evaluate(guess);z=_cat(x0+h*_rows(guess,n,2*n),p0+h*_rows(first['gradient'],0,n),_rows(guess,n,dim))
    E=np.zeros((d,nf),complex);E[2*n:]=F.T;B=np.zeros((nf,d),complex);B[:,2*n:]=F
    Eb=_matrix(E);records=[];status='ITERATION_LIMIT'
    def apply(z,r):
        x,p,phase=_rows(z,0,n),_rows(z,n,2*n),_rows(z,2*n,d);eta=_cat((x0+x)/2,phase);a=evaluate(eta);g=a['gradient']
        raw=_cat(x-x0-h*_rows(phase,0,n),p-p0-h*_rows(g,0,n),_rows(g,n,2*n)-(p0+p)/2,_rows(g,2*n,dim))
        rows=_cat(raw+Eb*r,C*(phase-reference));H=a['preconditioner'];J=np.zeros((d,d),complex)
        J[:n,:n]=np.eye(n);J[:n,2*n:3*n]=-step*np.eye(n)
        J[n:2*n,:n]=-step*H[:n,:n]/2;J[n:2*n,n:2*n]=np.eye(n);J[n:2*n,2*n:]=-step*H[:n,n:]
        J[2*n:3*n,:n]=H[n:2*n,:n]/2;J[2*n:3*n,n:2*n]=-np.eye(n)/2;J[2*n:3*n,2*n:]=H[n:2*n,n:]
        J[3*n:,:n]=H[2*n:,:n]/2;J[3*n:,2*n:]=H[2*n:,n:]
        K=_matrix(np.block([[J,E],[B,np.zeros((nf,nf),complex)]]));return a,raw,rows,K,eta
    a,raw,rows,K,eta=apply(z,rho)
    scale=1/np.maximum(np.max(abs(_mid(K)),axis=1),1.)
    for iteration in range(max_iterations+1):
        merit=float(np.linalg.norm(scale[:,None]*_mid(rows)));rec=dict(iteration=iteration,original_rows_upper=_upper(raw),scaled_framed_merit=merit);records.append(rec)
        if checkpoint:checkpoint(rec)
        if _upper(raw)<=guard and merit<=guard:status='ALL_MP_ORIGINAL_CANONICAL_ROWS_PASS';break
        if iteration==max_iterations:break
        correction=K.solve(-rows);accepted=False
        for half in range(12):
            fraction=2.**(-half);zt=z+fraction*_rows(correction,0,d);rt=rho+fraction*_rows(correction,d,d+nf)
            try:at,rr,fr,kt,et=apply(zt,rt);nextmerit=float(np.linalg.norm(scale[:,None]*_mid(fr)))
            except(ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError):continue
            if np.isfinite(nextmerit)and nextmerit<merit:z,rho,a,raw,rows,K,eta=zt,rt,at,rr,fr,kt,et;rec['accepted_fraction']=fraction;accepted=True;break
        if not accepted:status='MP_GRADIENT_LINE_SEARCH_STALL';break
    return dict(status=status,master_midpoint=eta,final_x=_rows(z,0,n),final_Pi=_rows(z,n,2*n),action=a,original_rows=raw,framed_rows=rows,frame_reactions=rho,records=records)


def run(repository,primal_cut,maps_packet,frames_packet,mp_lifts_packet,output,*,maximum_new_cells=24,first_step=1e-6,material_chart='original_binary'):
    root,cpath,apath,fpath,lpath,out=map(lambda p:Path(p).resolve(),(repository,primal_cut,maps_packet,frames_packet,mp_lifts_packet,output));out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'initial_producer.py').write_bytes(producer)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(Path(__file__).parent)]
    import numpy as np
    from flint import ctx
    from bhsm_baton_zoo_compatible_mp_current_flow import _snapshot_module
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=192;pins={};archives={};records=[];workspace=Path(__file__).parent
    packed,packedpin=_snapshot_module('bhsm_baton_zoo_phase_clock_analytic_jet',workspace/'bhsm_baton_zoo_phase_clock_analytic_jet.py',out)
    binary,binarypin=_snapshot_module('bhsm_baton_zoo_augmented_source_domain_derivative',workspace/'bhsm_baton_zoo_augmented_source_domain_derivative.py',out)
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def split(z):
        arrays={}
        for k,v in z.items():arrays[k+'_high'],arrays[k+'_low']=_split(v)
        return arrays
    def save(name,z):
        p=out/name;_compressed_npz(p,z);archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    cut,a,frames,lifts=read(cpath),read(apath),read(fpath),read(lpath);dim=368;n=158
    born=read(root/'artifacts/muon_birth_full_proper_port_saddle_20261013/run_1/birth_fixed_germ_and_source_compatibility.npz')
    parameters=read(root/'artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    phase,_=retained_input('outgoing',pins);rep=dict(phase['representation']);P=phase['coordinates']['lift'];original=np.asarray(a['child_original252_to_augmented'],int)
    oldrad=root/'artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1'
    oldmaps=binary.augmented_maps(read(oldrad/'birth_current288_connected_action_and_rate_operands.npz'),read(oldrad/'enlarged_birth_radial_action.npz'))
    extra=252+np.r_[a['previous_radial_to_augmented'][np.asarray(oldmaps['extra_coordinates_to_full'],int)-252],a['derivative_compatible_position_indices'],a['derivative_compatible_rate_indices']]
    maps=dict(old504_to_full=a['old504_to_full'],extra_coordinates_to_full=extra,full_dimension=252+dim,child_original252_to_augmented=original)
    for k in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        for part in('high','low'):maps[k+'_'+part]=lifts[k+'_'+part]
    for key,owner in[('extra_point_lift','compatible_extra_point_lift'),('extra_wall_lift','compatible_extra_wall_lift')]:
        for part in('high','low'):maps[key+'_'+part]=lifts[owner+'_'+part]
    maps['extra_point_lift']=maps['extra_point_lift_high']+maps['extra_point_lift_low']
    for key,rkey in[('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')]:
        values=maps[key+'_high']+maps[key+'_low']
        if rkey!='wall_trace_map':values=values.reshape(len(rep['rho']),80,1,5,4)
        if np.max(abs(values.imag))!=0:raise ValueError('physically real rounded preconditioner tables required')
        rep[rkey]=values.real
    F=frames.get('frames_completed',frames.get('frames'))
    if 'master368_high'in cut:e=_matrix(cut['master368_high'])+_matrix(cut['master368_low'])
    else:e=_matrix(cut['master368'])
    Pi=_matrix(cut['Pi158_high'])+_matrix(cut['Pi158_low']);time=_matrix([[cut['coordinate_time'].item()]])[0,0]
    if 'coordinate_time_low'in cut:time+=_matrix([[cut['coordinate_time_low'].item()]])[0,0]
    if e.nrows()!=dim or not np.array_equal(cut['original252_to_augmented368'],original)or not np.array_equal(cut['completed_frames'],F):raise ValueError('exact existing compatible368 coordinate/frame Cauchy domain required')
    reference=_matrix(cut['frame_reference']);context=(rep,P,maps,born['raw_pair'],born['reference_pair'],parameters,packed,binary,material_chart)
    evaluate=lambda e,t:_action(e,t,context)
    warm=_warm(e,Pi,lambda e:evaluate(e,time),F,reference,checkpoint=lambda r:print(json.dumps(dict(stage='full_precision_initial_warm',**r)),flush=True))
    save('full_precision_initial_actual_constitutive_rows.npz',dict(**split(dict(master368=warm['master'],Pi158=Pi,original210_rows=warm['original_rows'],frame_reactions=warm['frame_reactions'])),**warm['action']['precise']))
    if warm['status']!='ALL_MP_ORIGINAL_CONSTITUTIVE_ROWS_PASS':raise ArithmeticError(warm['status']+'; actual precision-refinement cut preserved')
    e=warm['master'];step=first_step;status='FULL_PRECISION_ACTUAL_CONTINUATION_RUNNING'
    for cell in range(maximum_new_cells):
        accepted=False
        for retry in range(8):
            h=_matrix([[step]])[0,0];tm,te=time+h/2,time+h
            mid=_cell(_rows(e,0,n),Pi,e,step,lambda e:evaluate(e,tm),F,reference,checkpoint=lambda r:print(json.dumps(dict(stage='full_precision_original526_midpoint',cell=cell,retry=retry,step=step,**r)),flush=True))
            th,tl=_split(_matrix([[complex(tm)]]));tmh=complex(tm);tml=complex(tm-_matrix([[tmh]])[0,0])
            save(f'cell_{cell:04d}_retry_{retry:02d}_full_precision_original526_midpoint.npz',dict(coordinate_time=np.asarray(tmh),coordinate_time_low=np.asarray(tml),step=np.asarray(step),
                **split(dict(midpoint_master368=mid['master_midpoint'],final_Pi158=mid['final_Pi'],original526_rows=mid['original_rows'],framed_rows=mid['framed_rows'],frame_reactions=mid['frame_reactions'])),**mid['action']['precise']))
            if mid['status']!='ALL_MP_ORIGINAL_CANONICAL_ROWS_PASS':step/=2;continue
            guess=_cat(mid['final_x'],_rows(mid['master_midpoint'],n,dim));end=_warm(guess,mid['final_Pi'],lambda e:evaluate(e,te),F,reference,
                checkpoint=lambda r:print(json.dumps(dict(stage='full_precision_original210_endpoint',cell=cell,retry=retry,**r)),flush=True))
            teh=complex(te);tel=complex(te-_matrix([[teh]])[0,0])
            save(f'cell_{cell:04d}_retry_{retry:02d}_full_precision_original210_endpoint.npz',dict(coordinate_time=np.asarray(teh),coordinate_time_low=np.asarray(tel),
                **split(dict(master368=end['master'],Pi158=mid['final_Pi'],original210_rows=end['original_rows'],framed_rows=end['framed_rows'],frame_reactions=end['frame_reactions'])),**end['action']['precise']))
            if end['status']!='ALL_MP_ORIGINAL_CONSTITUTIVE_ROWS_PASS':step/=2;continue
            e,Pi,time=end['master'],mid['final_Pi'],te;records.append(dict(cell=cell,retry=retry,step=step,time=[teh.real,teh.imag],time_low=[tel.real,tel.imag],original526_upper=_upper(mid['original_rows']),original210_upper=_upper(end['original_rows'])))
            step*=1.5;accepted=True;print(json.dumps(dict(stage='full_precision_actual_cell_accepted',**records[-1])),flush=True);break
        if not accepted:status='FULL_PRECISION_NUMERICAL_CONTINUATION_UNRESOLVED__NOT_PHYSICAL_EXIT';break
    else:status='FULL_PRECISION_ACTUAL_PREFIX_EXTENDED__PHYSICAL_MAXIMAL_END_UNCERTIFIED'
    th=complex(time);tl=complex(time-_matrix([[th]])[0,0])
    save('last_actual_full_precision_compatible368_primal.npz',dict(master368=_mid(e)[:,0],coordinate_time=np.asarray(th),coordinate_time_low=np.asarray(tl),
        **split(dict(master368=e,Pi158=Pi)),original252_to_augmented368=original,completed_frames=F,frame_reference=cut['frame_reference']))
    result=dict(classification='ACTUAL_COMPATIBLE368_MP_MASTER_AND_EXACT_AFFINE_CLOCK_NONLINEAR_CONTINUATION',status=status,input_hashes=pins,archives=archives,
        imported_runtime_dependencies=[packedpin,binarypin],producer_sha256=sha256(producer).hexdigest(),records=records,precision_bits=192,material_chart_owner=material_chart,
        master_coordinates_and_source_affine_clocks_keep_high_low=True,old_positions_and_canonical_momenta_preserved_at_precision_cut=True,
        rounded_Hessian_is_Newton_preconditioner_only=True,completed_integrations_repeated=False,physical_outgoing_end_or_original226_admitted=False)
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');(out/'executed_producer.py').write_bytes(producer)
    print(json.dumps(dict(stage='full_precision_actual_checkpoint',result_sha256=sha256(p.read_bytes()).hexdigest(),status=status)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in('repository','primal-cut','maps-packet','frames-packet','mp-lifts-packet','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--maximum-new-cells',type=int,default=24);p.add_argument('--first-step',type=float,default=1e-6);p.add_argument('--material-chart',choices=('original_binary','native_mp'),default='original_binary')
    a=p.parse_args();run(a.repository,a.primal_cut,a.maps_packet,a.frames_packet,a.mp_lifts_packet,a.output,maximum_new_cells=a.maximum_new_cells,first_step=a.first_step,material_chart=a.material_chart)
