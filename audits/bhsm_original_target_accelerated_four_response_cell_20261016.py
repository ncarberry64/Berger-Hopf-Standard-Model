"""Resume actual original-ea02 clock and seven/four retarded response cell.

Numerical affine-residual acceleration consumes the preserved unsuccessful
clock application; it does not alter the action, primal, source or domain.

No old primal/source/profile integration is repeated. The supplied new
accepted midpoint is bound to its original eight-cell response branch.
This advances a finite causal action application, not physical Y_R/s_R.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
ROOT=Path(__file__).resolve().parents[1]
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'


def affine_residual_combination(history):
    """Numerical least-squares warm vector; fresh original rows admit it.

    Complex conjugation is used only inside this numerical QR. It does not
    identify the independent analytic source dual with a Hilbert adjoint.
    All input vectors/rates stay explicit; no residual component is removed.
    """
    import mpmath as mp
    import numpy as np
    from flint import acb,acb_mat
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_stored_admission_correction import _upper
    with mp.workdps(80):
        def exact_binary(A):
            hi,lo=_split(A)
            return mp.matrix([[mp.mpc(complex(hi[i,j]))+mp.mpc(complex(lo[i,j]))for j in range(A.ncols())]for i in range(A.nrows())])
        residuals=[exact_binary(r)for _,r in history];ref=residuals[0]
        cols=[r-ref for r in residuals[1:]];scale=[max(abs(v)for v in c)for c in cols]
        if any(s==0 for s in scale):raise ValueError('Zero numerical residual difference is not discarded')
        A=mp.matrix([[c[i]/d for c,d in zip(cols,scale)]for i in range(ref.rows)])
        coefficients,qr_residual=mp.qr_solve(A,-ref)
        coefficients=[a/d for a,d in zip(coefficients,scale)]
        text=[(mp.nstr(a.real,82),mp.nstr(a.imag,82))for a in coefficients]
        weights=[acb(re,im)for re,im in text]
        base=history[0][0];candidate=base
        for weight,(u,_)in zip(weights,history[1:]):candidate=candidate+weight*(u-base)
        prediction=ref
        for a,c in zip(coefficients,cols):prediction=prediction+a*c
        return candidate,dict(method='MP80_QR_affine_combination_of_ALL_saved_actual_residual_rate_pairs',
            all_saved_steps_used=len(history),no_old_action_evaluation_replayed=True,coefficient_real_imag=text,
            predicted_residual_from_saved_binary_high_low=mp.nstr(max(abs(v)for v in prediction),25),
            coefficient_precision_decimal=80,numerical_QR_only_not_analytic_adjoint=True,
            fresh_original_equation_admission_required=True)


def execute(repository,tail_folder,output,workspace,clock_attempt):
    root,tail,out,work=map(lambda x:Path(x).resolve(),(repository,tail_folder,output,workspace))
    if out.exists():raise FileExistsError('Preserve previous actual response evidence')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(root/'audits')]
    import numpy as np
    from flint import ctx,acb,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_changing_weak_birth_action import affine_parent_master_map
    from evaluate_muon_continued_current_factor import retained_input
    from evaluate_muon_continued_current_factor import ROOT as retained_root
    if root!=Path(retained_root).resolve():raise ValueError('Repository must equal the retained input owner ROOT; no cross-repository field substitution')
    ctx.prec=256;pins={};archives={}
    def path_name(p):
        p=Path(p).resolve();return p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p)
    def read(p):
        p=Path(p);p=p if p.is_absolute()else root/p;b=p.read_bytes();pins[path_name(p)]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,p):
        p=Path(p);p=p if p.is_absolute()else root/p;b=p.read_bytes();pins[path_name(p)]=sha256(b).hexdigest();(out/(name+'_consumed_source.py')).write_bytes(b)
        spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    def save(name,values):
        arrays={}
        for k,v in values.items():
            if isinstance(v,acb_mat):arrays[k+'_high'],arrays[k+'_low']=_split(v)
            elif isinstance(v,np.ndarray):arrays[k]=v
        p=out/name;_compressed_npz(p,arrays);archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def exact(a,k):return _matrix(a[k+'_high'])+_matrix(a[k+'_low'])
    def gather(a,indices):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in indices])
    def center(a):return acb_mat([[acb(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
    guard=module('actual_original_target_tail_source','audits/bhsm_original_target_new_coupled_tail_cell_20261016.py')
    solver=module('actual_existing_tail_solver',FAMILY+'/actual_compatible368_full_precision_cut_control_run_1/initial_producer.py')
    binary=module('actual_original_augmented_scalar',FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/bhsm_baton_zoo_augmented_source_domain_derivative_imported_runtime.py')
    packed=module('actual_repaired_native_scalar',FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
    chart=module('actual_same_material_chart4',FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1/new620_fresh_same_material_equations_chart4_imported_runtime.py')
    module('bhsm_baton_zoo_acb_current_canonical',work/'bhsm_baton_zoo_acb_current_canonical.py')
    canonical=module('actual_native_canonical_response',FAMILY+'/actual_native_MP_one_new_compatible316_cell0_run_2/native_MP_matrix_free_canonical_cell_imported_runtime.py')
    a=read(FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    if pins[FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz']!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':raise ValueError('Exact original ea02 target required')
    flow=FAMILY+'/actual_response_cut_compatible368_refinement_flow_run_1/'
    cut=read(flow+'last_actual_compatible_primal_with_unclosed_future.npz');F=a['completed_frames'];receipt=guard.assert_original_response_primal_chain(root,read,cut,F)
    md=read(tail/'result.json')
    if md['classification']!='ORIGINAL_EA02_RESPONSE_BRANCH_NEW_FULL368_CLASSICAL_COUPLED_TAIL_CELL'or md['status']!='GENUINELY_NEW_CLASSICAL_COUPLED_TAIL_CELL_ADMITTED':raise ValueError('Accepted NEW original-target primal cell required, not the principal branch')
    for filename in('retry_00_new_tail_original526.npz','initial_fixed_Cauchy_constitutive_rows.npz'):
        if sha256((tail/filename).read_bytes()).hexdigest()!=md['archives'][filename]['sha256']:raise ValueError('Accepted new-tail primal bytes changed')
    stage=read(tail/'retry_00_new_tail_original526.npz');initial=read(tail/'initial_fixed_Cauchy_constitutive_rows.npz')
    if _upper(exact(initial,'master368')-_matrix(cut['master368']))!=0 or _upper(exact(initial,'Pi158')-exact(cut,'Pi158'))!=0:raise ValueError('Exact new-cell initial master/Pi differs from original response frontier')
    eta=exact(stage,'midpoint_master368');h=float(stage['step']);time=_matrix([[stage['coordinate_time'].item()]])[0,0]+_matrix([[stage['coordinate_time_low'].item()]])[0,0]
    if abs(complex(time)-complex(cut['coordinate_time'].item()+h/2))>1e-18:raise ValueError('New-cell source clock must follow exact target frontier')
    b=read('artifacts/muon_birth_full_proper_port_saddle_20261013/run_1/birth_fixed_germ_and_source_compatibility.npz')
    birth=read('artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1/enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    params=read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    tables=read('artifacts/muon_baton_zoo_radial_convergence_20261014/literal_MP_point_wall_tables_run_1/degree_02_literal_MP_original_and_extra_point_wall_tables.npz')
    phase,_=retained_input('outgoing',pins);rep=dict(phase['representation']);P=phase['coordinates']['lift'];original=a['original252_to_augmented368'];extra=a['extra116_to_full'];n=158;dim=368
    maps=dict(old504_to_full=np.r_[np.arange(252),252+original],extra_coordinates_to_full=extra,full_dimension=620,child_original252_to_augmented=original)
    for name in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        for part in('high','low'):maps[name+'_'+part]=tables[name+'_'+part]
    for name,source in(('extra_point_lift','compatible_extra_point_lift'),('extra_wall_lift','compatible_extra_wall_lift')):
        for part in('high','low'):maps[name+'_'+part]=tables[source+'_'+part]
    maps['extra_point_lift']=maps['extra_point_lift_high']+maps['extra_point_lift_low']
    for key,rkey in(('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')):
        v=maps[key+'_high']+maps[key+'_low']
        if rkey!='wall_trace_map':v=v.reshape(len(rep['rho']),80,1,5,4)
        if np.any(v.imag!=0):raise ValueError('Original real numerical preconditioner basis required')
        rep[rkey]=v.real
    raw_parent=solver._affine_ball(b['raw_pair'][0],time);raw_child=_matrix(P)*gather(eta,original)
    rawh,rawl=_split(acb_mat([[raw_parent[i,0]for i in range(268)],[raw_child[i,0]for i in range(268)]]))
    refs=[solver._affine_ball(v,time)for v in b['reference_pair']];refh,refl=_split(acb_mat([[v[i,0]for i in range(268)]for v in refs]))
    extr=gather(eta,extra-252);exh,exl=_split(extr);zero=np.zeros((620,1),complex)
    def scalar(selected,*,direction=None,right=None,reference_direction=None):
        direction=acb_mat(620,1)if direction is None else direction;right=acb_mat(620,1)if right is None else right
        dh,dl=_split(direction);rh,rl=_split(right)
        return packed.phase_action_contractions(rawh,refh,rep,P,maps,selected,dh[:,0],dl[:,0],rh,rl,
            raw_pair_low=rawl,reference_pair_low=refl,extra_base=exh[:,0],extra_base_low=exl[:,0],
            reference_direction=reference_direction,include_directional_first=reference_direction is not None,include_parent_action=False,
            material_chart_precision='independent_mp_same_material_equations',material_chart_owner=chart.anchored_material_chart4,
            nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'],precision_bits=256,direction_exact=direction,right_exact=right)
    active=a['action_active_parent_source_indices100'];selected=np.r_[active,252+np.arange(dim)]
    base=scalar(selected);Gselected=exact(base,'phase_gradient');G=_rows(Gselected,100,468)
    approx=binary.augmented_scalar_action(rawh+rawl,refh+refl,(exh+exl)[:,0],rep,maps,action_parameters=params);Hpre=approx['Hessian'][252:,252:]
    Kpre=_matrix(np.block([[Hpre[n:,n:],F.T],[F,np.zeros((7,7))]]));C=_matrix(F)
    def affine_rate(v):
        d=np.zeros(268,complex);d[:37]=v[37:74];d[98]=v[99];return d
    parentrate=_matrix(P).transpose()*_matrix(affine_rate(b['raw_pair'][0]));refrate=np.array([affine_rate(v)for v in b['reference_pair']])
    # The fixed-primal clock is affine in the unknown rate. Reuse every
    # exact saved residual/rate operand; no old action application is replayed.
    attempted=Path(clock_attempt).resolve();failed=read(attempted/'result.json')
    if failed['source_sha256']!='16688145bd104695494eab7d398e4d83ddf7a0c3eefbedc2ee457aa0edc0ecc5' or failed['status']!='NEW_TARGET_CONTINUOUS_CLOCK_UNRESOLVED_NO_RESPONSE_ADMITTED':raise ValueError('Exact preserved unsuccessful clock application required')
    if failed['new_tail_primal_input']!=path_name(tail/'result.json'):raise ValueError('Clock attempt belongs to a different new primal cell')
    for name,digest in failed['input_sha256'].items():
        p=Path(name);p=p if p.is_absolute()else root/p
        if sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Preserved clock dependency changed: '+name)
    history=[]
    for filename,meta in sorted(failed['archives'].items()):
        if not filename.startswith('clock_'):continue
        if sha256((attempted/filename).read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Clock residual/rate bytes changed')
        z=read(attempted/filename);history.append((exact(z,'actual_child_master_rate'),_cat(exact(z,'original210_clock_rows'),exact(z,'frame7_clock_rows'))))
    if len(history)!=13:raise ValueError('All thirteen original failed clock steps must remain included')
    candidate,acceleration=affine_residual_combination(history)
    rate=_rows(candidate,n,dim);save('accelerated_clock_rate_numerical_candidate.npz',dict(actual_child_master_rate=candidate))
    target=_cat(_rows(G,0,n),acb_mat(52,1));clock_records=[];clock_pass=False
    for k in range(1):
        childrate=_cat(_rows(eta,n,2*n),rate);direction=_cat(parentrate,childrate)
        ck=scalar(252+np.arange(n,dim),direction=direction,reference_direction=refrate)
        clock=exact(ck,'phase_gradient_first');same=_upper(exact(ck,'phase_gradient')-_rows(G,n,dim));rows=clock-target;frames=C*rate
        record=dict(iteration=k,original210_upper=_upper(rows),frame7_upper=_upper(frames),same_gradient_upper=same);clock_records.append(record)
        save(f'clock_{k:02d}_original210_and_point_density_first.npz',dict(ck,actual_child_master_rate=childrate,actual_total_master_clock_direction=direction,original210_clock_rows=rows,frame7_clock_rows=frames))
        print(json.dumps(dict(stage='actual_NEW_target_continuous_clock',**record)),flush=True)
        if same>2e-10:raise ValueError('Same-primal gradient epoch changed in clock application')
        if max(_upper(rows),_upper(frames))<=2e-10:clock_pass=True;break
        correction=Kpre.solve(-_cat(rows,frames));rate=center(rate+_rows(correction,0,210))
    force=acb_mat(dim,7)
    for i in range(n):force[i,0]=G[i,0]-clock[i,0]
    for i in range(52):force[2*n+i,0]=G[2*n+i,0]
    if not clock_pass:
        response=None;status='NEW_TARGET_CONTINUOUS_CLOCK_UNRESOLVED_NO_RESPONSE_ADMITTED'
    else:
        q=read(FAMILY+'/actual_new_only_compatible316_matrixfree_retarded_cell7_warm_run_2/actual_new_only_compatible316_response_and_full252_source_return.npz')
        Q=exact(q,'retarded_and_homogeneous_separate316');Up=exact(birth,'fixed_position_parent_phase')
        J0=affine_parent_master_map(0);J=_matrix(J0)+time*_matrix(affine_parent_master_map(1)-J0)
        parent=acb_mat(252,7);pu=J*Up
        for i in range(252):
            for j in range(3):parent[i,1+j]=pu[i,j]
        applications=0;gradient_defect=0.
        def action(child,source):
            nonlocal applications,gradient_defect
            applications+=1;z=scalar(selected,right=_cat(source,child));v=exact(z,'phase_Hessian_on_actual_right');g=exact(z,'phase_gradient')
            gradient_defect=max(gradient_defect,_upper(_rows(g,100,468)-G));s=acb_mat(252,7);gp=acb_mat(252,1)
            for i,slot in enumerate(active):
                gp[int(slot),0]=g[i,0]
                for j in range(7):s[int(slot),j]=v[i,j]
            save(f'actual_new_target_CHILD620_on_R7_{applications:02d}.npz',z)
            return dict(child_cotangent=_rows(v,100,468),parent_cotangent252=s,direct_child_source_gradient252=gp)
        response=canonical.canonical_cell(Hpre,h,F,Q,parent,action,force,guard=2e-10,max_iterations=12,precision_bits=256,
            checkpoint=lambda x:print(json.dumps(dict(stage='actual_NEW_target_R7_response',**x)),flush=True))
        status=response['status']if gradient_defect<=2e-10 else'NEW_TARGET_SAME_GRADIENT_EPOCH_REPRODUCTION_FAILED'
        values=response['values'];S7=values['parent_source_cotangent'];S4=acb_mat(252,4);Q7=values['final_canonical'];Q4=acb_mat(316,4)
        for i in range(252):
            S4[i,0]=S7[i,0]+values['actual_affine_primal_source_gradient252'][i,0]
            for j in range(3):S4[i,j+1]=S7[i,j+1]+S7[i,j+4]
        for i in range(316):
            Q4[i,0]=Q7[i,0]
            for j in range(3):Q4[i,j+1]=Q7[i,j+1]+Q7[i,j+4]
        increment=_matrix([[h]])[0,0]*J.transpose()*S4;returned=exact(q,'existing_full252_source_return')+increment
        save('actual_new_target_R7_four_Cauchy_and_full252_return.npz',dict(response['arrays'],retarded_and_homogeneous_separate316=Q7,combined_four_Cauchy316=Q4,all_four_source_cotangent252=S4,
            full252_inherited_source_return_increment=increment,existing_full252_source_return=returned,actual_parent_source252=parent,baseline_Euler_force368x7=force,
            actual_midpoint_master368_high=stage['midpoint_master368_high'],actual_midpoint_master368_low=stage['midpoint_master368_low'],coordinate_time=stage['coordinate_time'],coordinate_time_low=stage['coordinate_time_low'],step=stage['step'],completed_frames=F))
    admitted=clock_pass and response is not None and status=='ALL_ACTUAL_MATRIX_FREE_ORIGINAL_CANONICAL_ROWS_PASS'
    result=dict(classification='ORIGINAL_EA02_NEW_CONTIGUOUS_TARGET_FOUR_RESPONSE_CELL',status=status,finite_new_response_cell_admitted=admitted,clock_records=clock_records,baseline_force_upper=_upper(force),
        clock_numerical_acceleration=acceleration,preserved_clock_attempt=path_name(attempted/'result.json'),original_target_history_guard=receipt,new_tail_primal_input=path_name(tail/'result.json'),input_sha256=dict(sorted(pins.items())),archives=archives,
        full_high_low_midpoint_and_clock_retained=True,parent_and_both_reference_clocks_once=True,direct_CHILD_source_Hpp_not_parent_own=True,
        original526_response_upper=None if response is None else response['original_rows_upper'],response_records=None if response is None else response['records'],
        same_gradient_reproduction_upper=None if response is None else gradient_defect,prefix_primal_recomputed=False,old_response_prefix_replayed=False,
        physical_outgoing_Y_R=None,physical_affine_s_R=None,physical_C0_Cj=None,physical_source_domain_derivative_pass=False,original_coupled_corrections=0,
        original_Maxwell226_after_pass=False,physical_muon_magnetic_moment=None,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=status,result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=str(ROOT));p.add_argument('--tail-folder',required=True);p.add_argument('--output',required=True)
    p.add_argument('--workspace',default='C:/Users/carbe/OneDrive/Documents/CODEX');p.add_argument('--clock-attempt',required=True);a=p.parse_args();execute(a.repository,a.tail_folder,a.output,a.workspace,a.clock_attempt)
