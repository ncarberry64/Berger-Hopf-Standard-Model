"""New radial position Euler rows on the unchanged original ea02 field/clock.

This is a matrix-free primal action application, not a retraction or solve.
New zero coefficients represent the SAME field; its momenta are differentiated
from the action. No new physical momenta or response time derivatives are set
to zero. The saved carried affine-Jacobi Gauss residual is kept separate from
the primal Gauss gradient and from its Hessian-times-trial term.
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

os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
ROOT=Path(__file__).resolve().parents[1]
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
CLOCK=CURRENT+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
EXPECTED={TARGET:'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b',
          CLOCK:'18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290'}


def run(repository,output,*,degree=4,precision=224):
    root,out=Path(repository).resolve(),Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    pins={}
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        k=p.relative_to(root).as_posix();h=sha256(p.read_bytes()).hexdigest();pins[k]=h
        if k in EXPECTED and h!=EXPECTED[k]:raise ValueError('Exact original target/clock bytes required: '+k)
        return p
    def read(path):
        p=pin(path)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,relative):
        p=pin(relative);spec=importlib.util.spec_from_file_location(name,p)
        m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    try:
        sys.path[:0]=[str(root/'src'),str(root/'scripts')]
        from flint import ctx,acb_mat
        from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
        from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
        from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
        from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
        ctx.prec=int(precision)
        module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
        exact=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
        packed=module('same_field_native_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
        chart=module('same_field_material_chart4',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
        def parse(z,k):return exact.parse_acb_exact_dyadic(z,k+'_exact')
        def highlow(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
        def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
        target,clock=read(TARGET),read(CLOCK)
        maps=read(f'{RADIAL}/actual_linear_cut_degree{degree}_complete_clock_epoch_maps_run_1/actual_degree_{degree:02d}_complete_clock_covariant_product_epoch_maps.npz')
        projection=read(f'{RADIAL}/actual_common_cut_degree{degree}_momentum_projection_run_1/actual_common_cut_new_field_momentum_projection_and_Gauss_guards.npz')
        projection_action=read(f'{RADIAL}/actual_common_cut_degree{degree}_momentum_projection_run_1/same_original_MP_scalar_on_actual_common_cut_field_directions.npz')
        params=read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
        phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root)
        pins.update(phase['input_hashes']);rep=dict(phase['representation']);P=phase['coordinates']['lift']
        for k in ('coordinate_time','master368'):
            if not np.array_equal(clock[k],target[k]):raise ValueError('The exact ea02 cut field and clock must agree')
        if not np.array_equal(maps['actual_nonzero_current_master368'],target['master368']):raise ValueError('Map selected on a different primal field')
        if maps['coordinate_time'].item()!=target['coordinate_time'].item()or projection['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('Different map/projection epoch')
        full,n=int(maps['full_dimension']),int(maps['dynamic_count']);child=full-252
        if child<=368 or full!=int(projection['full_dimension']):raise ValueError('An explicitly enlarged complete action dimension is required')
        old_to_new=np.asarray(projection['explicit_current368_to_complete_child'],int)
        if len(old_to_new)!=368 or len(np.unique(old_to_new))!=368:raise ValueError('Injective complete old368 map required')
        base=np.zeros(child,complex);base[old_to_new]=target['master368']
        if not np.array_equal(base,projection['full_current_primal_child_coefficients']):raise ValueError('Pre-retraction SAME field representation must agree bitwise')
        oldrate=parse(clock,'actual_child_master_rate');wholeold=parse(clock,'actual_total_master_clock_direction')
        for part in ('real_mid_mantissa','real_mid_exponent','real_rad_mantissa','real_rad_exponent','imag_mid_mantissa','imag_mid_exponent','imag_rad_mantissa','imag_rad_exponent'):
            if not np.array_equal(clock['actual_total_master_clock_direction_exact_'+part][252:],clock['actual_child_master_rate_exact_'+part]):raise ValueError('Exact old full clock and child clock incidence disagree')
        H=acb_mat(full,1)
        for i in range(252):H[i,0]=wholeold[i,0]
        for i,d in enumerate(old_to_new):H[252+int(d),0]=oldrate[i,0]
        newq=np.asarray(projection['new_dynamic_position_indices'],int)
        if not np.array_equal(newq,np.setdiff1d(np.arange(n),old_to_new[:158])):raise ValueError('Explicit old158/new position incidence required')
        if any(base[int(q)]!=0 or base[n+int(q)]!=0 or H[252+int(q),0]!=0 or H[252+n+int(q),0]!=0 for q in newq):raise ValueError('Added coefficients must encode the SAME old field/clock')
        # All old q/v pairings must survive this ordered complete dynamical map.
        if not np.array_equal(old_to_new[158:316],n+old_to_new[:158]):raise ValueError('Explicit q/v paired incidence required')
        for k,rk in [('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')]:
            v=maps[k+'_high']+maps[k+'_low']
            if rk!='wall_trace_map':v=v.reshape(len(rep['rho']),80,1,5,4)
            if np.max(abs(v.imag),initial=0)!=0:raise ValueError('Original real literal coefficient basis required')
            rep[rk]=v.real
        extra=np.asarray(maps['extra_coordinates_to_full'],int)
        # The archived epoch maps were built on the older same-cut clock.
        # Rebuild BOTH their value map (which already includes A_dot) and
        # their clock map on the corrected native clock. Added zero base
        # coefficients would hide this test-column mismatch in a germ check.
        epoch=module('same_field_epoch_incidence',f'{RADIAL}/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/executed_bhsm_baton_zoo_complete_covariant_epoch_maps.py')
        profile=read(f'{RADIAL}/literal_MP_radial_complex192_run_2/degree_{degree:02d}_literal_MP_radial_profiles_and_derivative_complex.npz')
        older=read(CURRENT+'/actual_true_linear_cut_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz')
        def clock_operand(z,k):
            return parse(z,k)if k+'_exact_real_mid_mantissa'in z else highlow(z,k)
        profiles={k:highlow(profile,k)for k in ('values','first','second')}
        wall_profiles={k:highlow(profile,'wall_'+k)for k in ('values','first','second')}
        def product(z):return epoch.complete_product_lifts(clock_operand(z,'child_point_coefficients'),
            clock_operand(z,'child_point_coefficients_directional_first'),clock_operand(z,'child_wall_connection'),
            clock_operand(z,'child_wall_connection_directional_first'),profiles,wall_profiles)
        old_product,native_product=product(older),product(clock)
        if not np.array_equal(native_product['generator_profile_internal_labels'],maps['generator_profile_internal_labels']):raise ValueError('The same complete product-coordinate incidence is required')
        def obj(a):
            z=np.empty((a.nrows(),a.ncols()),dtype=object)
            for i in range(a.nrows()):
                for j in range(a.ncols()):z[i,j]=a[i,j]
            return z
        N=len(native_product['generator_profile_internal_labels']);prefix=len(extra)-2*N
        old_arrays={k:packed._coefficient_array(None,maps[k+'_high'],maps[k+'_low'])for k in
            ('extra_point_lift','extra_point_lift_total_clock','extra_wall_lift','extra_wall_lift_total_clock')}
        def map_difference(a,b):
            if a.shape!=b.shape:raise ValueError('Complete incidence map shapes differ')
            return max((float(abs(x-y).upper())for x,y in zip(a.flat,b.flat)),default=0.)
        def arrays_of(p):return dict(extra_point_lift=np.asarray([obj(m)for m in p['point_lift']],dtype=object),
            extra_point_lift_total_clock=np.asarray([obj(m)for m in p['point_lift_total_clock']],dtype=object),
            extra_wall_lift=obj(p['wall_lift']).reshape(5,4,2*N),
            extra_wall_lift_total_clock=obj(p['wall_lift_total_clock']).reshape(5,4,2*N))
        old_p,native_p=arrays_of(old_product),arrays_of(native_product)
        reconstruction={k:map_difference(old_arrays[k][...,-2*N:],old_p[k])for k in old_p}
        if max(reconstruction.values())>1e-20:raise ValueError('The archived incidence constructor/operands do not reproduce its saved maps')
        native_incidence_change={k:map_difference(old_arrays[k][...,-2*N:],native_p[k])for k in native_p}
        rebuilt={k:np.concatenate((old_arrays[k][...,:prefix],native_p[k]),axis=-1)for k in native_p}
        for k in ('extra_point_lift','extra_wall_lift'):
            maps[k]=rebuilt[k];maps.pop(k+'_high');maps.pop(k+'_low')
        Th,Wh=rebuilt['extra_point_lift_total_clock'],rebuilt['extra_wall_lift_total_clock']
        tests=252+np.r_[newq,n+newq,np.arange(2*n,child)]
        zero=np.zeros((full,1),complex);hh,hl=_split(H)
        print(json.dumps(dict(stage='same_original_ea02_primal_position_Euler_started',degree=degree,new_positions=len(newq),Gauss_rows=child-2*n,full_dimension=full)),flush=True)
        app=packed.phase_action_contractions(target['raw_pair'],target['reference_pair'],rep,P,maps,tests,
            hh[:,0],hl[:,0],zero,zero,extra_base=base[extra-252],reference_direction=clock['reference_affine_clock_once'],
            include_directional_first=True,include_parent_action=False,precision_bits=precision,
            material_chart_precision='independent_mp_same_material_equations',material_chart_owner=chart.anchored_material_chart4,
            extra_point_lift_first=Th,extra_wall_lift_first=Wh,
            nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'],
            export_exact_action_balls=True,direction_exact=H)
        G,Gt=parse(app,'phase_gradient'),parse(app,'phase_gradient_first');m=len(newq)
        Lq,Lv,dtLv=rows(G,np.arange(m)),rows(G,np.arange(m,2*m)),rows(Gt,np.arange(m,2*m))
        Euler=Lq-dtLv;gauss=rows(G,np.arange(2*m,G.nrows()))
        # The saved seven-column Gauss trial uses the earlier original-binary
        # material formation. Do not silently identify it with this native-MP
        # primal gradient. Preserve each operand and its formation discrepancy.
        old_gradient=highlow(projection_action,'phase_gradient')
        old_Kz=rows(highlow(projection_action,'phase_Hessian_on_actual_right'),np.arange(n,child-n))
        old_r=rows(old_gradient,np.arange(n,child-n));old_combined=acb_mat(old_Kz)
        for i in range(old_combined.nrows()):old_combined[i,0]+=old_r[i,0]
        old_combined_defect=_upper(old_combined-highlow(projection,'original_all_enlarged_Gauss_projection_rows'))
        if old_combined_defect>1e-25:raise ValueError('Saved affine Gauss residual must be decomposed without source duplication')
        arrays=dict(app,coordinate_time=target['coordinate_time'],master368=target['master368'],
            same_field_child_coefficients=base,old368_to_enlarged_child=old_to_new,new_position_indices=newq,
            enlarged_dynamic_count=np.asarray(n),all_old368_and_source_clocks_retained=np.asarray(True),
            no_Cauchy_retraction_or_physical_correction=np.asarray(True),
            seven_response_time_derivatives_evaluated=np.asarray(False))
        operands={'new_position_Lq':Lq,'new_position_Lv':Lv,'new_position_total_clock_Lv':dtLv,
            'new_position_primal_Euler_r':Euler,'enlarged_primal_Gauss_r':gauss,
            'saved_original_binary_primal_Gauss_r':old_r,'saved_original_binary_Gauss_Kz_trial':old_Kz,
            'saved_original_binary_affine_Gauss_trial_residual':old_combined}
        for key,a in operands.items():
            arrays[key+'_high'],arrays[key+'_low']=_split(a);arrays.update(exact.export_acb_exact_dyadic(a,key+'_exact'))
        # Base and total physical point germs are checked independently of the
        # new position action rows. This rejects a hidden field/clock retraction.
        germ_checks={}
        for key in ('child_point_coefficients','child_metric_density','child_wall_connection'):
            for suffix in ('','_directional_first'):
                k=key+suffix;germ_checks[k]=_upper(parse(app,k)-parse(clock,k))
        maximum_germ=max(germ_checks.values())
        if maximum_germ>2e-10:raise ValueError('The old physical point/wall/density germ was not preserved')
        archive=out/'same_field_primal_position_Euler_and_Gauss.npz';_compressed_npz(archive,arrays)
        map_arrays={'generator_profile_internal_labels':native_product['generator_profile_internal_labels'],
            'coordinate_time':target['coordinate_time'],'extra_coordinates_to_full':extra}
        for k,a in rebuilt.items():
            flat=acb_mat(a.reshape(-1,a.shape[-1]).tolist());a_h,a_l=_split(flat)
            map_arrays[k+'_high'],map_arrays[k+'_low']=a_h.reshape(a.shape),a_l.reshape(a.shape)
        map_archive=out/'native_clock_reconstructed_epoch_point_wall_maps.npz';_compressed_npz(map_archive,map_arrays)
        for name,mod in sorted(sys.modules.copy().items()):
            q=getattr(mod,'__file__',None)
            if q and(name=='bhsm'or name.startswith('bhsm.')or name in ('bhsm_baton_zoo_exact_acb_packets','bhsm_exact_action_balls','same_field_native_scalar','same_field_material_chart4')):
                p=Path(q).resolve()
                if p.is_relative_to(root):pin(p)
        pin(Path(__file__))
        report=dict(classification='SAME_ORIGINAL_EA02_FIELD_OFF_SHELL_NEW_RADIAL_POSITION_EULER_APPLICATION',degree=degree,
            source_sha256=sha256(source).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
            archive=dict(name=archive.name,sha256=sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size),
            native_epoch_map_archive=dict(name=map_archive.name,sha256=sha256(map_archive.read_bytes()).hexdigest(),bytes=map_archive.stat().st_size),
            new_position_count=m,Gauss_count=gauss.nrows(),full_dimension=full,arithmetic_precision_bits=precision,
            primal_Euler_upper=_upper(Euler),primal_Gauss_upper=_upper(gauss),
            Lq_upper=_upper(Lq),total_clock_Lv_upper=_upper(dtLv),
            physical_point_germ_preservation_upper=germ_checks,
            archived_older_clock_epoch_map_reconstruction_upper=reconstruction,
            corrected_native_clock_epoch_map_change_upper=native_incidence_change,
            saved_Gauss_affine_decomposition_defect_upper=old_combined_defect,
            saved_binary_to_native_MP_primal_Gauss_formation_difference_upper=_upper(gauss-old_r),
            new_coefficients_zero_only_as_same_function_representation=True,new_canonical_momenta_zero_assigned=False,
            moving_epoch_basis_h_contact_retained_once=True,epoch_basis_value_and_clock_reconstructed_from_native_point_germs=True,
            implicit_material_constraints_original96_nodes=True,
            selected_epoch_chart_held_for_variations=True,reference_source_clock_retained_once=True,
            full_linearized_new_position_residual_evaluated=False,
            remaining_linearized_position_operands=['same-action J*h*R contraction','actual response zDot and sourceDot at this same cut'],
            physical_radial_convergence=False,full_outgoing_realization=False,full_derivative_2e_10_passed=False,
            original_coupled_corrections_applied=0,normalized_two_spin_state=False,muon_magnetic_moment_evaluated=False)
        (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        print(json.dumps({k:report[k]for k in ('degree','primal_Euler_upper','primal_Gauss_upper','saved_binary_to_native_MP_primal_Gauss_formation_difference_upper')}),flush=True)
    except Exception as e:
        (out/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(source).hexdigest(),input_and_source_hashes=pins),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--degree',type=int,choices=(4,6),default=4);p.add_argument('--precision',type=int,default=224)
    a=p.parse_args();run(a.repository,a.output,degree=a.degree,precision=a.precision)
