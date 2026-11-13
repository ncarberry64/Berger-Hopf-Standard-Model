"""Changing same-phase1200 field action/Gram/current, with paired scalar orbit."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_parent_positive_coupled_temporal import temporal_coupled_field_application
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_parent_positive_coupled_field import _phase
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,quadrature_order):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous operator applications')
    out.mkdir(parents=True);refs={};files={};records=[];angular=retained_full_q_angular_space(ROOT)
    for side in ('incoming','outgoing'):
        folder=('artifacts/muon_finite_normal_phase_20261011/incoming_run_1' if side=='incoming'
            else 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        label=('EVALUATED_NONLINEAR_ANCHORED_NORMAL_PHASE_AND_PROPER_CLOCK_WEAK_ROWS' if side=='incoming'
            else 'EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION')
        receipt,saved,h=_phase(folder,label);refs.update(h)
        base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side=side)
        refs.update(base['input_hashes']);L=abs(receipt['span']/receipt['steps'])
        if receipt['action_parameters']!={'nu_squared_action':4.0,'surface_gamma':None}:raise ValueError('bind the same parameter-trial action')
        kwargs={};stage_time=(-L/2 if side=='incoming' else float(saved['stage_coordinate_time'][0]))
        if side=='incoming':raw=saved['stage_midpoint_raw'][0];origin=-L
        else:
            raw=saved['stage_independent_raw'][0];origin=0.
            kwargs=dict(initial_pair=saved['initial_pair'],reference_pair=saved['reference_pair'])
        print(json.dumps(dict(stage='begin_changing_coupled_form',side=side,quadrature_order=quadrature_order),sort_keys=True),flush=True)
        r=temporal_coupled_field_application(raw,stage_time,base['representation'],angular,length=L,
            quadrature_order=quadrature_order,coordinate_time_origin=origin,nu_squared_action=4.,**kwargs)
        group={
            'action':('coupled_action_Hessian','one_form_curvature_contact_common_cap','intrinsic_scalar_complete_Hessian'),
            'hilbert':('coupled_action_Gram','normalized_coupled_operator','normalized_coupled_eigenvalues',
                'one_form_Gram_per_kappa','ghost_Gram_per_kappa','ghost_FP_Hessian_per_kappa','weak_Lorenz_map'),
            'green':('normalized_coupled_Green','coupled_action_Green','full18_changing_coupled_open_field_Green_contraction'),
            'images':('canonical_full18_current_source_image','chronological_quadrature_samples'),
        }
        for name,keys in group.items():
            p=out/(side+'_'+name+'.npz');deterministic_archive(p,{k:r[k] for k in keys})
            if p.stat().st_size>10*1024**2:raise ValueError('complete lossless archive exceeds publication limit: '+p.name)
            files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        rec=dict(side=side,coordinate_time_origin=origin,length=L,quadrature_order=quadrature_order,
            normalized_gap=float(r['normalized_coupled_eigenvalues'][0]),normalized_max=float(r['normalized_coupled_eigenvalues'][-1]),
            normalized_inverse_residual=r['normalized_inverse_residual'],original_coordinate_inverse_residual=r['original_coordinate_inverse_residual'],
            normalized_operator_symmetry_defect=r['normalized_operator_symmetry_defect'],
            stored_normalized_inverse_majorant=r['stored_normalized_inverse_majorant'],
            paired_scalar_gauge_covariance_defect=r['paired_scalar_gauge_covariance_defect'],
            full18_open_field_Green_norm=float(np.linalg.norm(r['full18_changing_coupled_open_field_Green_contraction'])),
            proper_time_external_tent_Gram=r['proper_time_external_tent_Gram'],
            actual_inherited_profile_min_norm=float(r['chronological_quadrature_samples'][:,3].min()),
            actual_inherited_profile_max_norm=float(r['chronological_quadrature_samples'][:,3].max()))
        records.append(rec);print(json.dumps(dict(stage='completed_changing_coupled_form',**rec),sort_keys=True),flush=True)
    names=('muon_parent_positive_coupled_temporal','muon_parent_positive_coupled_field','muon_parent_positive_gauge_form',
        'muon_parent_positive_brst_ghost','muon_inherited_lepton_temporal_weak_action','muon_exact_material_response',
        'muon_birth_finite_normal_trace_graph','muon_birth_inherited_finite_normal_phase','muon_intrinsic_m4_normal_pullback',
        'muon_magnetic_open_lepton_vertex','muon_parent_mean_causal_action')
    for name in names:
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in (Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_parent_positive_coupled_field.py',
              'scripts/evaluate_muon_reached_trace_action.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed owner changed during integration')
    result=dict(classification='EVALUATED_CHANGING_SAME_PHASE_COUPLED_GAUGE_HIGGS_FIELD_GREEN_AND_CANONICAL_CURRENT',
        input_hashes=refs,numerical_files=files,records=records,
        action_parameters=dict(nu_squared_action=4.,surface_gamma=None),
        operator_composition='literal positive ADM YM Hessian including curvature contact, intrinsic-H complete mass/cross/Jacobi, pure one-form Lorenz fixing, one1200 action/Gram inverse',
        source_current_pairing='actual full18 deltaHcan action vertices with Ndt, external tent b² and intN*b² norm once; modesY/sqrt(V), no extraV',
        same_phase_interpolation='incoming futuret=u-L,outgoing futuret=u; exact x-linear/vy-midpoint phase cells plus declared affine parent/reference germs',
        coefficient_time_integration_performed=True,coefficient_frozen_at_center=False,
        paired_scalar_orbit='deltaH=-T(eta)H; deltaHdot=-T(eta_t)H-T(eta)Hdot; dependent images of existing320 DG coordinates, no extra scalar state',
        scalar_orbit_same_covariant_derivative_checked=True,
        Rxi_scalar_mass_gauge_fixing_added=False,
        one_field_inverse_before_full18_current_contraction=True,
        actual_intermediate_fermion_Green_inserted=False,
        canonical_P_strat_restriction_or_physical_Wick_equivalence_proved=False,
        continuum_relative_BRST_completion_or_quantum_Sigma_or_external_LSZ_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 split-Gauss finite phase integration; exact-stored normalized inverse Neumann guard only. Temporal quadrature, field/action/Gram production, radial/temporal continuum and physical matching are not outward enclosed; no anomaly bound.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records,numerical_files=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--quadrature-order',type=int,default=6)
    a=p.parse_args();print(json.dumps(materialize(a.output,a.quadrature_order),sort_keys=True))
