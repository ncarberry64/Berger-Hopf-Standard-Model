"""Actual added-position Jacobi rows on the unchanged ea02 seven fields.

Uses the freshly admitted same-cut response clock, not zero phase rates.
K_position R = Dg_q[R] - D_h Dg_v[R] - Dg_v[Rdot]. The primal Euler
residual is exported separately, and is added once only to affine column0.
This application is not a higher-radial response solve or a correction.
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


def run(repository,position_folder,seven_clock_folder,output,*,precision=256):
    root,posdir,clockdir,out=map(lambda p:Path(p).resolve(),(repository,position_folder,seven_clock_folder,output));out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def read(p):
        p=pin(p)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    try:
        sys.path[:0]=[str(root/'src'),str(root/'scripts')]
        from flint import ctx,acb_mat
        from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
        from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
        from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
        from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
        ctx.prec=precision
        module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
        ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
        packed=module('same_field_position_jacobi_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
        chart=module('same_field_position_jacobi_chart4',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
        def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
        def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
        def record(values):
            d={}
            for k,a in values.items():d[k+'_high'],d[k+'_low']=_split(a);d.update(ex.export_acb_exact_dyadic(a,k+'_exact'))
            return d
        target,clock=read(TARGET),read(CLOCK)
        if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'or pins[CLOCK]!='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290':raise ValueError('Exact original ea02/native CUT required')
        pm,cm=read(posdir/'result.json'),read(clockdir/'result.json')
        if pm['degree']!=4 or not pm['epoch_basis_value_and_clock_reconstructed_from_native_point_germs']:raise ValueError('Reviewed corrected native-epoch D4 primal application required')
        if not cm['admitted_original210_and_frame7_clock']:raise ValueError('Actual same-cut seven response clock must pass original rows')
        for r in cm['records'][-1:]:
            if max(r['original210_linearized_clock_upper'],r['frame7_upper'])>2e-10:raise ValueError('Failed actual seven response clock')
        p=read(posdir/pm['archive']['name']);newmaps=read(posdir/pm['native_epoch_map_archive']['name'])
        if sha256((posdir/pm['archive']['name']).read_bytes()).hexdigest()!=pm['archive']['sha256']or sha256((posdir/pm['native_epoch_map_archive']['name']).read_bytes()).hexdigest()!=pm['native_epoch_map_archive']['sha256']:raise ValueError('Primal/map archive pin mismatch')
        cpath=clockdir/'actual_same_cut_seven_continuous_response_clock.npz';c=read(cpath)
        if sha256(cpath.read_bytes()).hexdigest()!=cm['archives'][cpath.name]['sha256']:raise ValueError('Actual seven clock bytes changed')
        for z in (p,c,clock):
            if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No field/source/clock epoch splice')
        maps=read('artifacts/muon_baton_zoo_radial_convergence_20261014/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/actual_degree_04_complete_clock_covariant_product_epoch_maps.npz')
        for k in ('extra_point_lift','extra_wall_lift'):
            for part in ('high','low'):maps[k+'_'+part]=newmaps[k+'_'+part]
        Th=packed._coefficient_array(None,newmaps['extra_point_lift_total_clock_high'],newmaps['extra_point_lift_total_clock_low'])
        Wh=packed._coefficient_array(None,newmaps['extra_wall_lift_total_clock_high'],newmaps['extra_wall_lift_total_clock_low'])
        phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=dict(phase['representation']);P=phase['coordinates']['lift']
        for k,rk in [('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')]:
            v=maps[k+'_high']+maps[k+'_low'];rep[rk]=v.real.reshape(len(rep['rho']),80,1,5,4)if rk!='wall_trace_map'else v.real
        full=int(maps['full_dimension']);n=int(p['enlarged_dynamic_count']);newq=p['new_position_indices'];m=len(newq);oldmap=p['old368_to_enlarged_child']
        h0=exact(clock,'actual_total_master_clock_direction');R0=exact(c,'actual_complete_seven_response');Rd0=exact(c,'actual_complete_seven_response_clock')
        def embed(a):
            z=acb_mat(full,a.ncols())
            for i in range(252):
                for j in range(a.ncols()):z[i,j]=a[i,j]
            for i,dest in enumerate(oldmap):
                for j in range(a.ncols()):z[252+int(dest),j]=a[252+i,j]
            return z
        h,R,Rd=embed(h0),embed(R0),embed(Rd0)
        params=read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters'];extra=np.asarray(maps['extra_coordinates_to_full'],int)
        base=p['same_field_child_coefficients'];zero=np.zeros(full,complex);hh,hl=_split(h)
        def scalar(tests,right,*,total_clock):
            rh,rl=_split(right)
            return packed.phase_action_contractions(target['raw_pair'],target['reference_pair'],rep,P,maps,tests,
                hh[:,0]if total_clock else zero,hl[:,0]if total_clock else zero,rh,rl,
                extra_base=base[extra-252],reference_direction=clock['reference_affine_clock_once']if total_clock else None,
                include_directional_first=total_clock,include_parent_action=False,precision_bits=precision,
                material_chart_precision='independent_mp_same_material_equations',material_chart_owner=chart.anchored_material_chart4,
                extra_point_lift_first=Th if total_clock else None,extra_wall_lift_first=Wh if total_clock else None,
                nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'],
                export_exact_action_balls=True,right_exact=right,direction_exact=h if total_clock else None)
        print(json.dumps(dict(stage='actual_D4_new_position_H_h_R_started',new_positions=m,rights=7)),flush=True)
        app=scalar(252+np.r_[newq,n+newq],R,total_clock=True);_compressed_npz(out/'actual_D4_position_velocity_h_R_seven.npz',app)
        print(json.dumps(dict(stage='actual_D4_new_velocity_H_Rdot_started',new_velocity_tests=m,rights=7)),flush=True)
        rateapp=scalar(252+n+newq,Rd,total_clock=False);_compressed_npz(out/'actual_D4_velocity_Rdot_seven.npz',rateapp)
        HR=exact(app,'phase_Hessian_on_actual_right');hHR=exact(app,'phase_Hessian_first_on_actual_right');HRd=exact(rateapp,'phase_Hessian_on_actual_right')
        qHR,vhHR=rows(HR,np.arange(m)),rows(hHR,np.arange(m,2*m));Kz=qHR-vhHR-HRd
        primal=exact(p,'new_position_primal_Euler_r');affine=acb_mat(Kz)
        for i in range(m):affine[i,0]+=primal[i,0]
        combined=acb_mat(m,4)
        for i in range(m):
            combined[i,0]=affine[i,0]
            for j in range(3):combined[i,1+j]=affine[i,1+j]+affine[i,4+j]
        initial=acb_mat(m,1);g=exact(app,'phase_gradient');gt=exact(app,'phase_gradient_first')
        for i in range(m):initial[i,0]=g[i,0]-gt[m+i,0]
        sameprimal=_upper(initial-primal)
        if sameprimal>2e-10:raise ValueError('The new Jacobi application changed the fixed primal Euler row')
        result_packet=dict(coordinate_time=target['coordinate_time'],master368=target['master368'],new_position_indices=newq,old368_to_enlarged_child=oldmap,
            **record(dict(actual_new_position_H_R=qHR,actual_new_velocity_h_H_R=vhHR,actual_new_velocity_H_Rdot=HRd,
                actual_new_position_Kz_trial=Kz,new_position_primal_r=primal,actual_affine_seven_position_trial_residual=affine,
                actual_combined_four_position_trial_residual=combined,actual_enlarged_seven_field=R,actual_enlarged_seven_field_clock=Rd)))
        archive=out/'actual_D4_same_field_position_Jacobi_and_affine_residual.npz';_compressed_npz(archive,result_packet)
        for name,mod in list(sys.modules.items()):
            f=getattr(mod,'__file__',None)
            if f and(name=='bhsm'or name.startswith('bhsm.'))and Path(f).resolve().is_relative_to(root):pin(Path(f).resolve())
        pin(Path(__file__))
        result=dict(classification='ACTUAL_ORIGINAL_EA02_SAME_FIELD_D4_POSITION_JACOBI_APPLICATION',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
            archive=dict(name=archive.name,sha256=sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size),new_positions=m,rights=7,arithmetic_precision_bits=precision,
            actual_new_position_Kz_upper=_upper(Kz),primal_position_r_upper=_upper(primal),actual_affine_seven_residual_upper=_upper(affine),combined_four_residual_upper=_upper(combined),
            same_primal_Euler_reproduction_upper=sameprimal,actual_response_clock_original210_and_frame7_passed=True,
            sourceDot_and_zDot_not_zero_assigned=True,primal_r_added_once_only_to_column0=True,old_field_and_response_extended_without_retraction=True,
            higher_radial_mean_or_response_solved=False,physical_radial_convergence=False,full_physical_outgoing_or_derivative_or_moment=False,original_coupled_corrections_applied=0)
        (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        print(json.dumps({k:result[k]for k in ('actual_new_position_Kz_upper','actual_affine_seven_residual_upper','same_primal_Euler_reproduction_upper')}),flush=True)
    except Exception as e:
        (out/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=pins),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT);p.add_argument('--position-folder',required=True,type=Path);p.add_argument('--seven-clock-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();run(a.repository,a.position_folder,a.seven_clock_folder,a.output)
