"""Actual original-rule real temporal action readouts; no solve/correction."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import numpy as np

REPO=Path(__file__).resolve().parents[1]


def evaluate(repository,output):
    root=Path(repository).resolve();out=Path(output).resolve()
    if out.exists():raise FileExistsError('preserve existing application output')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_real_two_arm_temporal_action import (
        paired_temporal_layout,pack_temporal_state,real_two_arm_temporal_action)
    from bhsm.interface.muon_birth_attached_phase import enriched_representation_from_values
    from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
    from bhsm.interface.muon_birth_finite_normal_trace_graph import (
        finite_normal_trace_graph_action_two_jet,finite_normal_trace_graph_action_value,pointwise_finite_normal_action)
    from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pins={}
    def pin(path,expected=None):
        p=Path(path);digest=sha256(p.read_bytes()).hexdigest()
        if expected is not None and digest!=expected:raise ValueError('input changed '+str(p))
        label='repo/'+p.relative_to(root).as_posix()
        pins[label]=digest;return digest
    base=root/'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'
    pin(base/'result.json','06867e31959910ec21385e8491bd5b794060c68e8404ae0524e3d0c9b544faa6')
    receipt=json.loads((base/'result.json').read_bytes())
    pin(base/'application.npz',receipt['numerical_sha256'])
    with np.load(base/'application.npz',allow_pickle=False) as f:original={k:f[k].copy() for k in f.files}
    rep=enriched_representation_from_values(receipt,original)
    if (len(rep['rho']),rep['cap_points'])!=(48,48):raise ValueError('exact retained radial48/cap48 baseline required')
    inherited=root/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    pin(inherited/'result.json');ir=json.loads((inherited/'result.json').read_bytes())
    pin(inherited/'application.npz',ir['numerical_sha256'])
    with np.load(inherited/'application.npz',allow_pickle=False) as f:child={k:f[k].copy() for k in f.files}
    if ir['steps']!=1 or ir['completed_steps']!=1 or not np.isrealobj(child['stage_independent_raw']):
        raise ValueError('retained REAL complete single child cell required')
    P=generic_coordinate_lift(rep['gauge_labels'])['lift'];h=float(ir['span']);t=float(child['stage_coordinate_time'][0])
    params=receipt['action_parameters']
    if params!=ir['action_parameters']:raise ValueError('same provisional action parameters required')
    cases=[('real_moving_trace_birth',original['updated_raw_pair'],original['reference_raw_pair'],0.),
        ('real_inherited_child_midpoint',np.array([affine_geometry_germ(child['initial_pair'][0],t),child['stage_independent_raw'][0]]),
         np.array([affine_geometry_germ(r,t) for r in child['reference_pair']]),t)]
    arrays={};records=[]
    for name,raw,ref,midtime in cases:
        if not np.isrealobj(raw) or not np.isfinite(raw).all():raise ValueError('no complex-to-real projection')
        layout=paired_temporal_layout(P,[midtime-h/2,midtime+h/2],[midtime-h/2,midtime+h/2])
        eta=np.array([P.T@r for r in raw]);x=np.array([[e[:106]-h*e[106:212]/2 for e in eta],
                                                     [e[:106]+h*e[106:212]/2 for e in eta]])
        state=pack_temporal_state(layout,x,eta[:,212:][None]);captured={}
        def joint(r,f):
            a=finite_normal_trace_graph_action_two_jet(r,f,rep,**params);captured['joint']=a;return a
        def parent(r):
            return pointwise_finite_normal_action(r,rep,**params)
        a=real_two_arm_temporal_action(state,layout,ref[None],rep,**params,
            joint_action_evaluator=joint,parent_action_evaluator=parent)
        actual=a['cell_raw_pairs'][0];difference=actual-raw
        # Literal action path constructs raw values from nodal positions,
        # independently of the assembler's J_cell matrix and local owner jet.
        def literal(z):
            xx=z[:424].reshape(2,2,106);yy=z[424:].reshape(1,2,40)
            rr=np.array([P@np.r_[(xx[0,s]+xx[1,s])/2,(xx[1,s]-xx[0,s])/h,yy[0,s]] for s in range(2)])
            return h*finite_normal_trace_graph_action_value(rr,ref,rep,**params)
        direction=np.zeros_like(state);dx=direction[:424].reshape(2,2,106)
        for s in range(2):
            dx[:,s,25]=.002*(s+1);dx[:,s,40]=.03;dx[:,s,103]=-.04*(s+1)
        direction[424+24]=.003
        analytic=float(a['gradient']@direction);checks=[]
        for step in (3e-4,1e-4,3e-5):
            plus=literal(state+step*direction);minus=literal(state-step*direction);finite=(plus-minus)/(2*step)
            error=abs(finite-analytic);den=max(abs(finite),abs(analytic),np.finfo(float).tiny)
            checks.append(dict(step=step,plus=plus,minus=minus,literal_directional=finite,
                assembled_directional=analytic,absolute_error=error,relative_to_nonzero_directional=error/den,
                symmetric_value_difference=plus-minus))
        direct=literal(state);faces=np.zeros((2,2,106));faces[0]+=a['cell_initial_cotangents'][0];faces[1]+=a['cell_final_cotangents'][0]
        # The full536 by global504 affine map is retained, not reconstructed
        # after the fact from a reduced response or selected scalar row.
        R=np.zeros((536,504));R[:268,:252]=P;R[268:,252:]=P
        T=np.zeros((504,504))
        for s in range(2):
            b=s*252;l=s*106;r=212+s*106;alg=424+s*40
            T[b:b+106,l:l+106]=np.eye(106)/2;T[b:b+106,r:r+106]=np.eye(106)/2
            T[b+106:b+212,l:l+106]=-np.eye(106)/h;T[b+106:b+212,r:r+106]=np.eye(106)/h
            T[b+212:b+252,alg:alg+40]=np.eye(40)
        J=R@T;local=captured['joint'];prefix=name+'__'
        for key,value in dict(original_raw_pair=raw,actual_reconstructed_raw_pair=actual,reference_pair=ref,
            global_state=state,coordinate_lift=P,raw536_from_global504=J,
            raw536_gradient=local['raw_gradient'],raw536_hessian=local['raw_hessian'],
            global504_gradient=a['gradient'],global504_hessian=a['hessian'],
            endpoint_cotangents=a['position_cotangents'],algebraic_rows=a['algebraic_rows'],
            cell_initial_cotangents=a['cell_initial_cotangents'],cell_final_cotangents=a['cell_final_cotangents'],
            declared_direction=direction).items():arrays[prefix+key]=value
        records.append(dict(case=name,coordinate_midpoint=midtime,equal_coordinate_step=h,
            original_radial_nodes=48,original_cap_quadrature=48,exact_response_normalization_rule=96,
            frozen_source_image_basis_reused=True,actual_retained_raw_reconstructed_max=float(np.max(abs(difference))),
            value=float(a['value']),independent_literal_value=direct,value_absolute_difference=abs(direct-a['value']),
            raw536_gradient_norm=float(np.linalg.norm(local['raw_gradient'])),raw536_hessian_norm=float(np.linalg.norm(local['raw_hessian'])),
            global504_gradient_norm=float(np.linalg.norm(a['gradient'])),global504_hessian_norm=float(np.linalg.norm(a['hessian'])),
            source_parent_child_hessian_norm=float(np.linalg.norm(local['raw_hessian'][:268,268:])),
            all_endpoint_cotangent_norm=float(np.linalg.norm(a['position_cotangents'])),all_algebraic80_row_norm=float(np.linalg.norm(a['algebraic_rows'])),
            endpoint_face_sum_max=float(np.max(abs(faces-a['position_cotangents']))),
            affine_gradient_pullback_max=float(np.max(abs(a['gradient']-h*J.T@local['raw_gradient']))),
            affine_hessian_pullback_max=float(np.max(abs(a['hessian']-h*J.T@local['raw_hessian']@J))),
            literal_directional_step_sweep=checks,native_application=a['native_application'],boundary_application=a['boundary_application'],
            extra_constraint_application=a['constraint_KKT'],complete_physical_mean_residual=a['complete_physical_mean_residual'],
            background_gradient_g_minus_g0_subtracted=False,owned_mechanical_Maxwell_baseline_preserved=True,
            parent_reference_affine_germs_are_solved_history=False,physical_pairing_incidence_selected=False,
            global_sigma_normal_admissibility_claimed=False))
    pin(Path(__file__).resolve())
    pin(root/'src/bhsm/interface/muon_real_two_arm_temporal_action.py')
    pin(root/'tests/test_muon_real_two_arm_temporal_action.py')
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(root):pin(Path(path))
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024*1024:raise ValueError('archive exceeds10MiB')
    result=dict(classification='ACTUAL_REAL_FULL_TWO_ARM_WHOLE_TEMPORAL_CLASSICAL_READOUT',records=records,
        input_and_source_sha256=dict(sorted(pins.items())),archive_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        archive_bytes=(out/'application.npz').stat().st_size,full_original_radial_and_cap_rule_preserved=True,
        newly_solved_histories_or_profiles=0,newton_or_matching_corrections=0,physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None,full_physical_derivative_at_2e_minus10_passed=False,
        radial_angular_or_outgoing_convergence_claimed=False,
        sigma_normal_scope='Classical action readout only. Separate full-D5 open-form attempt encounters interior sigma-gradient spacelike-normal guard; this application does not repair or bypass it, and no global inadmissibility theorem is inferred.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(cases=len(records),archive_bytes=result['archive_bytes'],archive_sha256=result['archive_sha256'],
        result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),physical_mean=False),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=str(REPO));p.add_argument('--output',required=True)
    a=p.parse_args();evaluate(a.repository,a.output)
