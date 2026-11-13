"""Execute corrected-profile ONE gauge/intrinsic-H field inverse and current."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_parent_positive_coupled_field import positive_coupled_field_application
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def _phase(folder,classification):
    path=ROOT/folder;receipt=json.loads((path/'result.json').read_bytes())
    if receipt['classification']!=classification or receipt['completed_steps']!=receipt['steps']:
        raise ValueError('complete same-action corrected phase required')
    refs=dict(receipt['input_hashes'])
    for name,value in refs.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=value:
            raise ValueError('consumed owner changed: '+name)
    archive=path/'application.npz';h=sha256(archive.read_bytes()).hexdigest()
    if h!=receipt['numerical_sha256']:raise ValueError('phase numeric binding changed')
    refs[archive.relative_to(ROOT).as_posix()]=h
    refs[(path/'result.json').relative_to(ROOT).as_posix()]=sha256((path/'result.json').read_bytes()).hexdigest()
    with np.load(archive,allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
    return receipt,arrays,refs


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    base='artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'
    angular=retained_full_q_angular_space(ROOT);refs={};files={};records=[];out.mkdir(parents=True)
    for side in ('incoming','outgoing'):
        if side=='incoming':
            folder='artifacts/muon_finite_normal_phase_20261011/incoming_run_1'
            label='EVALUATED_NONLINEAR_ANCHORED_NORMAL_PHASE_AND_PROPER_CLOCK_WEAK_ROWS'
        else:
            folder='artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
            label='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION'
        receipt,saved,h=_phase(folder,label);refs.update(h)
        b=load_finite_normal_endpoint(base,side=side);refs.update(b['input_hashes']);rep=b['representation']
        L=abs(receipt['span']/receipt['steps'])
        if receipt['action_parameters']!={'nu_squared_action':4.0,'surface_gamma':None}:
            raise ValueError('bind the same assigned nu²4/gamma-unassigned action member')
        kwargs={}
        if side=='outgoing':
            raw=saved['stage_independent_raw'][0];t=float(saved['stage_coordinate_time'][0])
            kwargs=dict(initial_pair=saved['initial_pair'],reference_pair=saved['reference_pair'])
        else:
            raw=saved['stage_midpoint_raw'][0];t=receipt['span']/(2*receipt['steps'])
        print(json.dumps(dict(stage='begin_corrected_coupled_action',side=side,coordinate_time=t,length=L),sort_keys=True),flush=True)
        r=positive_coupled_field_application(raw,rep,angular,length=L,coordinate_time=t,nu_squared_action=4.,**kwargs)
        if side=='outgoing':
            # Interior profile is bound to the saved graph before the wall
            # is evaluated separately; no radial projection is introduced.
            if not np.allclose(r['inherited_profile_value_time_radial'],saved['stage_profile_increment'][0],rtol=0,atol=5e-16):
                raise ValueError('full inherited bulk action profile disagrees')
        group={
            'action':('coupled_action_Hessian','one_form_YM_Hessian_per_kappa','one_form_curvature_contact_per_kappa',
                'boundary_gauge_mass_Hessian','boundary_gauge_Higgs_mixed_Hessian','intrinsic_Higgs_Hessian','Lorenz_gauge_fixing_per_kappa'),
            'hilbert':('coupled_action_Gram','normalized_coupled_operator','normalized_coupled_eigenvalues',
                'one_form_Gram_per_kappa','ghost_Gram_per_kappa','ghost_FP_Hessian_per_kappa','weak_Lorenz_map','weak_gradient_pairing_per_kappa'),
            'green':('normalized_coupled_Green','coupled_action_Green','full_gauge_Higgs_wall_Green',
                'stable_gauge_Higgs_cross_wall_return','full18_coupled_open_field_Green_contraction','full18_gauge_Higgs_cross_return'),
            'images':('raw_fields','rho','radial_weights','background_values','background_time_derivatives','background_radial_derivatives',
                'positive_metric_coefficients','positive_two_form_densities','inherited_profile_value_time_radial',
                'metric_identity_relative_residual','wall_time_profile_value_maps','wall_projected_value_map','wall_background_values',
                'joint_field_trace_map','canonical_gauge_vertices','canonical_scalar_vertices','actual_H_covariant_time_derivative',
                'actual_H_covariant_spatial_derivatives','intrinsic_Higgs_covariant_angular_derivatives','intrinsic_Higgs_material_temporal_connection',
                'intrinsic_Higgs_potential_Hessian','vertex_time_projection','source_product_complement_Gram'),
        }
        for name,keys in group.items():
            p=out/(side+'_'+name+'.npz');deterministic_archive(p,{k:r[k] for k in keys})
            if p.stat().st_size>10*1024**2:raise ValueError('lossless complete archive exceeds publication limit: '+p.name)
            files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        rec=dict(side=side,coordinate_time=float(t),length=float(L),R4=r['R4'],induced_lapse=r['induced_lapse'],
            inherited_profile_norm=float(np.linalg.norm(r['inherited_profile_value_time_radial'])),
            actual_covariant_H_time_norm=float(np.linalg.norm(r['actual_H_covariant_time_derivative'])),
            gauge_boundary_mass_norm=float(np.linalg.norm(r['boundary_gauge_mass_Hessian'])),
            gauge_H_cross_norm=float(np.linalg.norm(r['boundary_gauge_Higgs_mixed_Hessian'])),
            normalized_gap=float(r['normalized_coupled_eigenvalues'][0]),
            normalized_max=float(r['normalized_coupled_eigenvalues'][-1]),
            normalized_operator_symmetry_defect=r['normalized_operator_symmetry_defect'],
            normalized_inverse_residual=r['normalized_inverse_residual'],
            original_coordinate_inverse_residual=r['original_coordinate_inverse_residual'],
            original_coordinate_inverse_relative_backward_error=r['original_coordinate_inverse_relative_backward_error'],
            stored_normalized_inverse_majorant=r['stored_normalized_inverse_majorant'],
            ghost_image_FP_relative_error=r['ghost_image_FP_relative_error'],
            full_gauge_Higgs_wall_Green_norm=float(np.linalg.norm(r['full_gauge_Higgs_wall_Green'])),
            full18_open_field_Green_norm=float(np.linalg.norm(r['full18_coupled_open_field_Green_contraction'])),
            full18_gauge_Higgs_cross_return_norm=float(np.linalg.norm(r['full18_gauge_Higgs_cross_return'])),
            common_cap_Maxwell_factor=r['common_cap_Maxwell_factor'])
        records.append(rec);print(json.dumps(dict(stage='completed_corrected_coupled_action',**rec),sort_keys=True),flush=True)
    names=('muon_parent_positive_coupled_field','muon_parent_positive_gauge_form','muon_parent_positive_brst_ghost',
        'muon_exact_material_response','muon_birth_finite_normal_trace_graph','muon_birth_inherited_finite_normal_phase',
        'muon_intrinsic_m4_normal_pullback','muon_parent_maxwell_corrected_retarded','muon_parent_maxwell_full_weak',
        'muon_magnetic_open_lepton_vertex','muon_parent_mean_causal_action')
    for name in names:
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed owner changed during application')
    result=dict(classification='EVALUATED_CORRECTED_PROFILE_ONE_COUPLED_PARENT_GAUGE_INTRINSIC_H_FIELD_GREEN',
        input_hashes=refs,numerical_files=files,records=records,
        action_parameters=dict(nu_squared_action=4.,surface_gamma=None),
        composition='one1200 Hessian: cap-normalized full1120 YM curvature+weak-Lorenz form, intrinsic-H gauge boundary mass, actual DH mixed rows, and H80 Jacobi; one joint inverse before current contraction',
        current_normalization='orthonormal Haar modesY/sqrt(V),pointwise canonicalchi=R4^(3/2)psi/V; no extraV in all18 open vertex',
        exact_normal_metric_and_unprojected_inherited_profile_applied=True,
        material_At_count=1,actual_background_Hdot_in_cross_rows=True,
        gauge_H_cross_and_both_open_current_placements_retained=True,
        one_form_exact_gradient_images_retained=True,
        scalar_temporal_domain='one existing tent; scalar ghost-orbit/product-image complement retained as an uncompleted domain, not set tozero',
        operator_scope='positive ADM coefficient-cell reference with actual first germs; not a physical Wick or canonical P_strat restriction, full coefficient-time DdaggerD or relative-BRST completion',
        intermediate_fermion_Green_inserted=False,EC_HS_auxiliary_identified_with_intrinsic_H=False,
        complete_quantum_self_energy_or_interacting_LSZ_soft_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 evaluated finite action/Gram/source; guarded normalized exact-stored Neumann bounds exclude operator/Gram/field production, temporal/radial continuum and physical matching. Current norms are not anomaly bounds.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records,numerical_files=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
