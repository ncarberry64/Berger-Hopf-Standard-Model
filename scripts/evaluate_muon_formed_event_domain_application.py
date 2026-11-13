"""Apply the interacting E1 domain to the actual saved endpoint fields."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,platform,sys
import numpy as np
import scipy

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_formed_event_domain_application import (
    endpoint_seam_numerator,event_frame_incidence,endpoint_checks,
)
from bhsm.interface.retained_response.finite_time_response import write_npz
from bhsm.interface.muon_native_event_incidence_contacts import evaluate_endpoint_incidence_contacts


def pin(path):
    return sha256(path.read_bytes()).hexdigest()


def run(output):
    output=Path(output)
    if output.exists():
        raise FileExistsError('preserve completed applications')
    folder=ROOT/'artifacts/muon_retained_response_20261018/inputs'
    provenance=json.loads((folder/'PROVENANCE.json').read_bytes())
    metadata=json.loads((folder/'history_metadata.json').read_bytes())
    if metadata['histories']!='PROVISIONAL_NOT_COLLIDER_SOLUTIONS':
        raise ValueError('preserved history scope changed')
    pins={};applications={};arrays={}
    base=ROOT/'artifacts/muon_cutoff_domain_binding_20261019/run_2'
    base_record=json.loads((base/'result.json').read_bytes())
    if pin(base/'cutoff_domain_binding.npz')!=base_record['arrays']['sha256']:
        raise ValueError('completed cutoff/domain arrays changed')
    for rel,expected in base_record['input_sha256'].items():
        if pin(ROOT/rel)!=expected:
            raise ValueError('completed application input changed: '+rel)
    pins.update({(base/name).relative_to(ROOT).as_posix():pin(base/name)
        for name in ('result.json','cutoff_domain_binding.npz')})
    with np.load(base/'cutoff_domain_binding.npz',allow_pickle=False) as z:
        saved_child=dict(raw268=z['retained_child_plus_raw268'].copy(),
            rate268=z['retained_child_plus_coordinate_time_derivative268'].copy())
        for target,source in [('density','canonical_Cauchy_density_factor'),
                              ('kappa','proper_density_connection')]:
            for suffix in ('value','gradient100','Hessian100'):
                saved_child[target+'_'+suffix]=z['retained_child_plus_'+source+'_'+suffix].copy()
    for side,label in (('incoming','hi'),('outgoing','lo')):
        path=folder/(side+'_history.npz')
        expected=provenance['files']['inputs/'+path.name]['sha256']
        if pin(path)!=expected:
            raise ValueError('actual saved history changed: '+side)
        incidence=next(a for a in metadata['sides'][side] if a['label']==label)
        if incidence['time']!=0.:
            raise ValueError('application must use the actual E1 endpoints')
        with np.load(path,allow_pickle=False) as z:
            x=z[label+'_raw_fields'].copy()
            xt=z[label+'_raw_coordinate_time_derivative'].copy()
        a=endpoint_seam_numerator(x,xt);applications[side]=a
        pins[path.relative_to(ROOT).as_posix()]=pin(path)
        arrays[side+'_raw268']=x
        arrays[side+'_raw_coordinate_time_derivative268']=xt
        for key in ('Nhat','Bhat','Ehat','image','complement_image','domain_complement_image',
            'original_weak_rows','isotropy_rows','nilpotence_rows',
            'selected_trace_image_rows','geometric_green_rows','free_hard_graph_defect'):
            arrays[side+'_'+key]=a[key][0]
            arrays[side+'_'+key+'_coordinate_time']=a[key][1]
        for channel,values in a['channels'].items():
            for key,value in values.items():
                arrays[side+'_'+channel+'_'+key]=value[0]
                arrays[side+'_'+channel+'_'+key+'_coordinate_time']=value[1]
        for key in ('domain_complement_singular_values','middle_charged_projector18',
            'middle_charged_forcing_singular_values'):
            arrays[side+'_'+key]=a[key]
        for eta in ('plus','minus'):
            arrays[side+'_'+eta+'_spin_boost128']=a['frames'][eta]['spin_boost128']
            arrays[side+'_'+eta+'_spin_boost_coordinate_time128']=a['frames'][eta]['spin_boost_time128']
    incidence=event_frame_incidence(applications['incoming'],applications['outgoing'])
    for key,value in incidence.items():
        if isinstance(value,np.ndarray):arrays['E1_'+key]=value
        elif isinstance(value,tuple):
            arrays['E1_'+key]=value[0]
            arrays['E1_'+key+'_coordinate_time']=value[1]
    pa,ca=applications['incoming'],applications['outgoing']
    native_arrays,native_report=evaluate_endpoint_incidence_contacts(
        pa['raw268'],pa['raw_coordinate_time_derivative268'],
        ca['raw268'],ca['raw_coordinate_time_derivative268'],
        saved_child_density=saved_child)
    arrays.update({'native_incidence_'+key:value for key,value in native_arrays.items()})
    output.mkdir(parents=True)
    path=output/'formed_event_domain_application.npz'
    write_npz(path,arrays)
    for p in (folder/'PROVENANCE.json',folder/'history_metadata.json',Path(__file__)):
        pins[p.relative_to(ROOT).as_posix()]=pin(p)
    for name,module in sorted(sys.modules.items()):
        file=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and file and Path(file).resolve().is_relative_to(ROOT):
            p=Path(file).resolve();pins[p.relative_to(ROOT).as_posix()]=pin(p)
    for rel in ('artifacts/muon_adopted_incoming_reference_20261018/adoption_v1.json',
        'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'):
        pins[rel]=pin(ROOT/rel)
    checks={side:endpoint_checks(a) for side,a in applications.items()}
    diagrams={name:dict(value_max=float(np.max(abs(incidence[name][0]))),
        independent_one_sided_time_difference_max=float(np.max(abs(incidence[name][1]))))
        for name in ('geometric_intertwining_rows','selected_numerator_intertwining_rows',
            'interacting_seam_intertwining_rows')}
    Ai=incidence['incoming_independent_plus_own_wall_connection']
    Ao=incidence['outgoing_independent_plus_own_wall_connection']
    record=dict(schema='bhsm.formed-event-domain-application.v1',
        parent_head='9738fc5ad9c82a6d7b3e5a9e0ecc21cdf33e5291',
        classification='EVALUATED_ACTUAL_E1_INTERACTING_SEAM_NUMERATOR_DOMAIN_AND_LOCAL_FRAME_INCIDENCE',
        input_sha256=pins,arrays=dict(path=path.name,sha256=pin(path)),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        executed=dict(
            weak_equation='Each chiral numerator J_plus Nhat_k=C_hat (rho P_left M_Y(H) P_right) B_hat, k=LR,RL; B_hat Nhat_k=0; every Nhat_k Nhat_l=0 separately',
            actual_application='Separate Nhat_LR Ehat_plus and Nhat_RL Ehat_plus on all18 action-owned coefficient generators, retaining full384 complement; their unweighted sum is a coefficient package only',
            complement_equation='For ACTUAL normalized B,E with BE=I: x=Eg+chi_plus, y=Eg+chi_minus, B chi=0, BN=0, N chi=0 give chi_minus-chi_plus=N E g. The non-null chiral coefficients of this forcing are evaluated; u_L/u_R are symbolic.',
            physical_normalized_forcing='N_phys=alpha_LR Nhat_LR+alpha_RL Nhat_RL, alpha_LR=1/(u_L_plus*u_R_minus), alpha_RL=1/(u_L_minus*u_R_plus). E_phys=Ehat*(u_R_plus P_L+u_R_minus P_R), hence N_phys E_phys=Nhat_LR Ehat/u_L_plus+Nhat_RL Ehat/u_L_minus.',
            complement_projectors='domain complement I384-W18 W18^T is distinct from retained particle+antiparticle36 complement I384-W36 W36^dagger; both forcing images saved',
            middle_family_projector='charged weak-L and e_R entries [8,9,14,15], zero-based, from original heavy,middle,light family order; fixed-Y action retained',
            eta_geometry='U_eta=S_minus S_plus^-1; each history has two eta collars, distinct from the two successive cap histories',
            temporal_frames='T_plus=S_plus,out S_plus,in^-1; T_minus=S_minus,out S_minus,in^-1',
            commuting_rows='U_eta,out T_plus=T_minus U_eta,in; Bhat_out T_plus=Bhat_in; Nhat_out T_plus=T_plus Nhat_in at the E1 value',
            derivative='all one-sided original coordinate-time jets include Hdot, Udot, rho_dot; unequal history jets are reported, not forced to match',
            paired_event_jet_scope=incidence['paired_jet_scope'],
            endpoint_checks=checks,event_value_and_independent_time_diagrams=diagrams,
            endpoints={side:{k:a[k] for k in ('velocity','velocity_time','surface_density',
                'surface_density_time','R4','induced_lapse','Cauchy_density_factor')}
                for side,a in applications.items()},
            plus_boost_distance_from_identity=float(np.linalg.norm(incidence['plus_boost'][0]-np.eye(384))),
            minus_boost_distance_from_identity=float(np.linalg.norm(incidence['minus_boost'][0]-np.eye(384))),
            Cauchy_density_ratio=incidence['Cauchy_density_ratio']),
        evaluated_native_incidence_contacts=native_report,
        preserved_ancestry=dict(completed_domain_array_sha256=base_record['arrays']['sha256'],
            saved_child_Cauchy_density_and_connection_twojets_reused=True,
            previous_preserved_scope=base_record['preserved'],
            unchanged_known_partial_residuals=base_record['residuals_after_whole_local_removal'],
            whole_local_removal_repeated=False, native_cutoff_derivatives_changed=False,
            native_past_return_changed=False, formation_cutoff_root=None),
        local_spatial_gauge=dict(
            equation='B_i=2 A_i+1/2 epsilon_ijk[A_j,A_k] on the retained homogeneous wall; A includes own mechanical connection once',
            spatial_connection_difference_max=float(np.max(abs(Ao[2:]-Ai[2:]))),
            coordinate_temporal_connection_difference_max=float(np.max(abs(Ao[0]-Ai[0]))),
            spatial_curvature_difference_max=float(np.max(abs(incidence['outgoing_homogeneous_spatial_curvature']-incidence['incoming_homogeneous_spatial_curvature']))),
            SU2_curvature_singular_values=incidence['spatial_SU2_curvature_singular_values'].tolist(),
            curvature_H_stabilizer_rank=incidence['simultaneous_curvature_H_stabilizer_rank'],
            stabilizer_singular_values=incidence['simultaneous_curvature_H_stabilizer_singular_values'].tolist(),
            discrete_center=incidence['gauge_center_rule'],scope=incidence['gauge_scope'],
            total_outgoing_inherited_wall_image_verified=False),
        normalization=dict(
            right_incidence=incidence['normalized_right_trace_rule'],
            left_incidence=incidence['normalized_left_trace_rule'],
            LR='1/(u_L_plus*u_R_minus)',RL='1/(u_L_minus*u_R_plus)',
            time_derivative='each inverse factor keeps -alpha*(u_Ldot/u_L+u_Rdot/u_R)',
            normal_values_assigned=False,normal_mode_formed=False),
        scope=dict(
            saved_histories='PROVISIONAL_NOT_COLLIDER_SOLUTIONS',
            new_vacuum_or_occupation_selected=False,old_native0_heat_recomputed=False,
            native_past_map_recomputed=False,native_resolvent_lambda_is_independent_of_cutoff_c=True,
            actual_E1_native_return_claimed=False,global_reset_history_or_FR_sign_reconstructed=False,
            eta_normal_identified_with_native_temporal_normal=False,
            two_histories_identified_with_incoming_beams=False,
            coupled_correction_applied=False,physical_2e10_admission=False,
            original_Maxwell_or_all226_recheck_claimed=False,
            magnetic_moment_or_uncertainty_claimed=False),
        remaining_equation='(A) constrained mechanical Jacobi/KKT first-crossing branch psi with causal background/event/native loads; (B) same-branch D5 fermion localization/domain equations for independent u_R,u_L and full complement, with actual Cauchy pairing; (C) composed event incidence and Lorentz/native causal contour. These are different problems, not one scalar mode.',
        NEXT_OPERAND='consume the saved non-null chiral complement boundary forcing in the D5 localization/domain solve, retaining unknown exterior/reference return and normalization; compose that with mechanical KKT branch and derived causal/native event contour')
    (output/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    result=run(args.output_dir)
    print(json.dumps(dict(classification=result['classification'],arrays=result['arrays'],
        endpoint_checks=result['executed']['endpoint_checks']),sort_keys=True))
