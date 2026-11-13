"""Actual same-ea02 seven-column continuous Jacobi clock application.

The retained parent source is the owned affine J(t)Up, and child qDot=v.
The remaining phaseDot is solved from the same literal action's linearized
Euler/Gauss clock equations. A stored Hessian only preconditions; every
unreacted row is freshly evaluated. No response time derivative is set to0.
This is a carried finite response germ, not a higher-radial or exterior solve.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback
import numpy as np
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
ROOT=Path(__file__).resolve().parents[1]
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
CLOCK=FAMILY+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'
SEED=FAMILY+'/actual_linear_cut_enlarged_Gauss_Legendre_prolongation_run_2/actual_original_Gauss_and_old_Legendre_complete_current_Cauchy_prolongation.npz'
BIRTH='artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1/enlarged_birth_proper_three_columns_and_canonical_seeds.npz'


def run(repository,output,*,precision=256,iterations=8):
    root,out=Path(repository).resolve(),Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source);pins={}
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p;pins[p.relative_to(root).as_posix()]=sha256(p.read_bytes()).hexdigest();return p
    def read(path):
        p=pin(path)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    try:
        sys.path[:0]=[str(root/'src'),str(root/'scripts')]
        from flint import ctx,acb,acb_mat
        from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
        from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
        from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
        from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
        from bhsm.interface.muon_changing_weak_birth_action import affine_parent_master_map
        ctx.prec=precision
        module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
        ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
        packed=module('seven_clock_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
        chart=module('seven_clock_material_chart',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
        def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
        def hi(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
        def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
        def center(a):return acb_mat([[acb(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
        def cat(*args):return acb_mat([[a[i,j]for j in range(a.ncols())]for a in args for i in range(a.nrows())])
        def save(name,z):_compressed_npz(out/name,z)
        def packet(values):
            z={}
            for k,a in values.items():z[k+'_high'],z[k+'_low']=_split(a);z.update(ex.export_acb_exact_dyadic(a,k+'_exact'))
            return z
        a,c,s,b=read(TARGET),read(CLOCK),read(SEED),read(BIRTH)
        if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'or pins[CLOCK]!='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290':raise ValueError('Exact ea02 and native CUT clock bytes required')
        if not np.array_equal(a['master368'],c['master368'])or a['coordinate_time'].item()!=c['coordinate_time'].item()or s['authoritative_node_time'].item()!=a['coordinate_time'].item():raise ValueError('Same complete state/clock/response cut required')
        phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=dict(phase['representation']);P=phase['coordinates']['lift']
        tables=read('artifacts/muon_baton_zoo_radial_convergence_20261014/literal_MP_point_wall_tables_run_1/degree_02_literal_MP_original_and_extra_point_wall_tables.npz')
        maps=dict(full_dimension=620,old504_to_full=np.r_[np.arange(252),252+a['original252_to_augmented368']],extra_coordinates_to_full=a['extra116_to_full'])
        for k in ('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
            for part in ('high','low'):maps[k+'_'+part]=tables[k+'_'+part]
        for k,t in [('extra_point_lift','compatible_extra_point_lift'),('extra_wall_lift','compatible_extra_wall_lift')]:
            for part in ('high','low'):maps[k+'_'+part]=tables[t+'_'+part]
        for k,rk in [('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')]:
            v=maps[k+'_high']+maps[k+'_low'];rep[rk]=v.real.reshape(len(rep['rho']),80,1,5,4)if rk!='wall_trace_map'else v.real
        R=cat(hi(s,'actual_parent_source252'),hi(s,'actual_solved_child_field368'));h=exact(c,'actual_total_master_clock_direction')
        Up=hi(b,'fixed_position_parent_phase');J=_matrix(affine_parent_master_map(a['coordinate_time'].item()));Jdot=acb_mat(252,252)
        for i in range(37):Jdot[i,106+i]=1
        Jdot[37,143]=1
        source,sourceDot=acb_mat(252,7),acb_mat(252,7);v,vd=J*Up,Jdot*Up
        for i in range(252):
            for j in range(3):source[i,1+j],sourceDot[i,1+j]=v[i,j],vd[i,j]
        source_identity=_upper(source-rows(R,np.arange(252)))
        if source_identity>1e-24:raise ValueError('Actual seven parent columns are not the owned J(t)Up source')
        params=read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters'];zero=np.zeros((620,7),complex);hz=np.zeros(620,complex)
        extra=a['master368'][np.asarray(a['extra116_to_full'])-252]
        def scalar(tests,right,*,clock=False):
            rh,rl=_split(right);hh,hl=_split(h)
            return packed.phase_action_contractions(a['raw_pair'],a['reference_pair'],rep,P,maps,tests,
                hh[:,0]if clock else hz,hl[:,0]if clock else hz,rh,rl,extra_base=extra,
                reference_direction=c['reference_affine_clock_once']if clock else None,
                include_directional_first=clock,include_parent_action=False,precision_bits=precision,
                material_chart_precision='independent_mp_same_material_equations',material_chart_owner=chart.anchored_material_chart4,
                nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'],
                export_exact_action_balls=True,right_exact=right,direction_exact=h if clock else None)
        print(json.dumps(dict(stage='actual_ea02_seven_right_clock_contraction_started',rights=7,phase_tests=210)),flush=True)
        phaseapp=scalar(252+np.arange(158,368),R,clock=True);save('actual_same_cut_phase_h_R_seven.npz',phaseapp)
        third=exact(phaseapp,'phase_Hessian_first_on_actual_right')
        print(json.dumps(dict(stage='actual_ea02_seven_right_position_HR_started',position_tests=158)),flush=True)
        qapp=scalar(252+np.arange(158),R);save('actual_same_cut_position_H_R_seven.npz',qapp);qHR=exact(qapp,'phase_Hessian_on_actual_right')
        # Canonical pDot = H_q R + primal_Euler_q in the affine column0.
        # Differentiating the original affine Gauss constraint adds G_yDot
        # only to column0. No derivative of a missing response is set to0.
        target=cat(qHR,acb_mat(52,7));force=exact(c,'actual_native_MP_baseline_Euler_force368')
        Gt=exact(c,'phase_gradient_first')
        for i in range(158):target[i,0]+=force[i,0]
        for i in range(52):target[158+i,0]-=Gt[158+i,0]
        known=cat(sourceDot,rows(R,np.arange(252+158,252+316)),acb_mat(210,7))
        knownapp=scalar(252+np.arange(158,368),known);save('actual_known_qDot_and_sourceDot_action.npz',knownapp)
        rhs=target-third-exact(knownapp,'phase_Hessian_on_actual_right')
        H=hi(a,'true_child_Hessian368');F=_matrix(a['completed_frames']);K=acb_mat(217,217)
        for i in range(210):
            for j in range(210):K[i,j]=H[158+i,158+j]
            for j in range(7):K[i,210+j]=F[j,i];K[210+j,i]=F[j,i]
        phaseDot=center(rows(K.solve(cat(rhs,acb_mat(7,7))),np.arange(210)))
        records=[];admitted=False;last=None
        for iteration in range(iterations+1):
            rightDot=cat(sourceDot,rows(R,np.arange(252+158,252+316)),phaseDot)
            app=scalar(252+np.arange(158,368),rightDot);last=app
            residual=exact(app,'phase_Hessian_on_actual_right')+third-target;frames=F*phaseDot
            record=dict(iteration=iteration,original210_linearized_clock_upper=_upper(residual),frame7_upper=_upper(frames));records.append(record)
            save(f'iteration_{iteration:02d}_fresh_original210_seven_clock.npz',dict(app,**packet(dict(actual_complete_seven_response_clock=rightDot,actual_child_seven_response_clock=rows(rightDot,np.arange(252,620)),original210_clock_rows=residual,frame7_clock_rows=frames))))
            print(json.dumps(dict(stage='actual_ea02_seven_response_clock_rows',**record)),flush=True)
            if max(_upper(residual),_upper(frames))<=2e-10:admitted=True;break
            correction=K.solve(-cat(residual,frames));phaseDot=center(phaseDot+rows(correction,np.arange(210)))
        save('actual_same_cut_seven_continuous_response_clock.npz',dict(coordinate_time=a['coordinate_time'],master368=a['master368'],original252_to_augmented368=a['original252_to_augmented368'],extra116_to_full=a['extra116_to_full'],
            **packet(dict(actual_complete_seven_response=R,actual_complete_seven_response_clock=rightDot,actual_child_seven_response_clock=rows(rightDot,np.arange(252,620)),actual_parent_seven_source_clock=sourceDot,
                same_action_phase_h_R=third,same_action_position_H_R=qHR,original210_clock_rows=residual,frame7_clock_rows=frames))))
        for name,m in list(sys.modules.items()):
            p=getattr(m,'__file__',None)
            if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(root):pin(Path(p).resolve())
        pin(Path(__file__));archives={p.name:dict(sha256=sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)for p in sorted(out.glob('*.npz'))}
        result=dict(classification='ACTUAL_ORIGINAL_EA02_CARRIED_SEVEN_CONTINUOUS_JACOBI_CLOCK',source_sha256=sha256(source).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),archives=archives,
            records=records,admitted_original210_and_frame7_clock=admitted,parent_source_JUp_identity_upper=source_identity,
            parent_affine_sourceDot_derived_from_exact_map=True,child_qDot_is_retained_velocity=True,phaseDot_zero_assigned=False,
            stored_Hessian_used_as_preconditioner_only=True,actual_original_rows_freshly_evaluated=True,
            physical_outgoing_or_radial_mean_or_full_derivative=False,original_coupled_corrections_applied=0)
        (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    except Exception as e:
        (out/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),input_and_source_hashes=pins,source_sha256=sha256(source).hexdigest()),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);p.add_argument('--precision',type=int,default=256);p.add_argument('--iterations',type=int,default=8)
    a=p.parse_args();run(a.repository,a.output,precision=a.precision,iterations=a.iterations)
