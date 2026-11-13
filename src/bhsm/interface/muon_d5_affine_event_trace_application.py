"""Consume the saved full D5 family in the exact affine event trace row.

Only child trace COORDINATES are eliminated. The base correspondence,
middle bundle lift, normal/density maps and physical boundary state remain
unknown. The saved eta-normal frame is never identified with the material
wall frame used to express this event row.
"""
from __future__ import annotations

import numpy as np

from .muon_d5_temporal_bulk_refinement import (
    evaluate_refined_field, apply_refined_fundamental,
)
from .muon_parent_retarded_hypercharge import WALL


def parent_trace_coordinates(operand, spin_frame, spin_first, spin_time):
    """Express actual ambient operands in the material wall coefficient frame.

    `radial_fixed_frame` keeps the independent physical radial frame contact
    -S^-1 S_r q explicit; this function does not supply an off-wall frame.
    Its source is the declared Xi, not the complete physical source.
    """
    required = ('value', 'source', 'time', 'radial', 'time_source', 'radial_source')
    if any(k not in operand for k in required):
        raise ValueError('full saved field, coordinate gradients and source gradients required')
    values = {k: np.asarray(operand[k], complex) for k in required}
    v = values['value']
    S, Sx, St = map(lambda a: np.asarray(a, complex), (spin_frame, spin_first, spin_time))
    if v.ndim != 2 or S.shape != (v.shape[0], v.shape[0]) or Sx.shape != S.shape or St.shape != S.shape:
        raise ValueError('one full ambient trace matrix and explicit material frame jets required')
    if any(a.shape != v.shape for a in values.values()):
        raise ValueError('same saved trace column identities required')
    J = np.linalg.inv(S)
    Jx, Jt = -J@Sx@J, -J@St@J
    q = J@v
    return dict(value=q, source=J@values['source']+Jx@v,
        time=J@values['time']+Jt@v,
        radial_fixed_frame=J@values['radial'],
        ambient_time_source_in_frame=J@values['time_source'],
        ambient_radial_source_in_frame=J@values['radial_source'],
        frame_source_connection=J@Sx, frame_time_connection=J@St,
        parent_reconstruction_rows=S@q-v)


def reconstruct_child_trace_jet(coordinates, coordinates_first, *,
        child_spin, child_spin_first, child_density, child_density_first,
        middle_lift, middle_lift_first, parent_density, parent_density_first):
    """Full ordered reconstruction for explicitly supplied physical maps.

    Gamma_c=S_c D_c^-1 K0 D_p qbar_c. All five first placements are
    retained. The application below deliberately does not call this with
    manufactured numerical density maps or K0.
    """
    q, qx = map(np.asarray, (coordinates, coordinates_first))
    S, Sx, D, Dx, K, Kx, P, Px = map(np.asarray, (child_spin, child_spin_first,
        child_density, child_density_first, middle_lift, middle_lift_first,
        parent_density, parent_density_first))
    if q.ndim != 2 or qx.shape != q.shape or any(a.shape != (q.shape[0], q.shape[0]) for a in (S,Sx,D,Dx,K,Kx,P,Px)):
        raise ValueError('all ordered maps, firsts and child coordinate columns required')
    Di = np.linalg.inv(D); Dix = -Di@Dx@Di
    value = S@Di@K@P@q
    first = (Sx@Di@K@P@q+S@Dix@K@P@q+S@Di@Kx@P@q
        +S@Di@K@Px@q+S@Di@K@P@qx)
    return value, first


def complete_parent_pullback_first(coordinates, source, coordinate_time,
        radial_fixed_frame, *, event_time_first, event_radius_first,
        radial_frame_connection):
    """Add the base-incidence Jacobi contact with child point motion once.

    event_*_first must be the TOTAL delta F_B, already including DF_B delta
    x_child. Supplying that child motion a second time would double count it.
    The independent radial material-frame connection is mandatory.
    """
    q, qx, qt, qr = map(np.asarray, (coordinates,source,coordinate_time,radial_fixed_frame))
    A = np.asarray(radial_frame_connection)
    if q.ndim != 2 or any(a.shape != q.shape for a in (qx,qt,qr)) or A.shape != (q.shape[0],q.shape[0]):
        raise ValueError('all total pullback slots and radial frame contact required')
    return qx+qt*event_time_first+(qr-A@q)*event_radius_first


def consume_saved_affine_event_trace(arrays, *, parent_spin128,
        parent_spin_first128, parent_spin_time128, batch_size=64,
        particular_overrides=None):
    """Solve qbar_child-S_parent^-1 Gamma_parent=0 for every saved column.

    qbar_child=D_p^-1 K0^-1 D_c S_c^-1 Gamma_raw_child is only an
    invertible coordinate definition. K0, D_p, D_c are retained symbols.
    All366 homogeneous coordinates at EACH temporal node stay free, shared
    behind the two eta collars. No child D5 or physical outer row is solved.
    """
    times = np.asarray(arrays['times'], float)
    if times[-1] != 0 or not 1 <= batch_size <= 256:
        raise ValueError('saved E1 endpoint and bounded explicit column batch required')
    n, hcount = len(times), 366*len(times)
    S, Sx, St = (np.kron(np.eye(3), np.asarray(a, complex)) for a in
        (parent_spin128,parent_spin_first128,parent_spin_time128))
    if S.shape != (384,384) or Sx.shape != S.shape or St.shape != S.shape:
        raise ValueError('actual original128 material spin frame and its two declared first slots required')
    output, summaries = {}, {}
    norm = lambda a: float(np.linalg.norm(a))
    maximum = lambda a: float(np.max(abs(a)))
    keys = ('value','source','time','radial_fixed_frame',
        'ambient_time_source_in_frame','ambient_radial_source_in_frame')
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        if particular_overrides is not None and label in particular_overrides:
            operand = {k:np.asarray(v) for k,v in particular_overrides[label].items()}
        else:
            saved = evaluate_refined_field(arrays,label,[0.],[WALL])
            operand = {k:v[0,0] for k,v in saved.items()}
        q = parent_trace_coordinates(operand,S,Sx,St)
        for key in keys:
            output[label+'_'+key] = q[key]
        # The affine unknown child coordinate equals this RHS exactly.
        # Residuals here are coefficient arithmetic, not physical field data.
        child_coordinates = q['value'].copy()
        summaries[label] = dict(rhs_Frobenius=norm(q['value']),rhs_max_entry=maximum(q['value']),
            before_uneliminated_row_rhs_Frobenius=norm(q['value']),
            after_affine_coordinate_row_max=maximum(child_coordinates-q['value']),
            after_affine_coordinate_source_row_max=maximum(q['source']-q['source']),
            parent_reconstruction_max=maximum(q['parent_reconstruction_rows']),
            declared_Xi_rhs_Frobenius=norm(q['source']),
            time_pullback_coefficient_Frobenius=norm(q['time']),
            radial_pullback_fixed_frame_coefficient_Frobenius=norm(q['radial_fixed_frame']))
    for side in ('plus','minus'):
        Q = np.asarray(arrays['wall_'+side+'_complement_basis'])
        Qx = np.asarray(arrays['wall_'+side+'_complement_basis_source'])
        if Q.shape != (n,384,366) or Qx.shape != Q.shape:
            raise ValueError('all366 original complement columns per time node required')
        target = {k:np.zeros((384,hcount),complex) for k in keys}
        reconstruction = 0.
        for start in range(0,hcount,batch_size):
            end = min(start+batch_size,hcount);columns=np.arange(start,end)
            W = np.zeros((n,384,end-start),complex);Wx=np.zeros_like(W)
            for local,column in enumerate(columns):
                node,index=divmod(int(column),366)
                W[node,:,local],Wx[node,:,local]=Q[node,:,index],Qx[node,:,index]
            raw = apply_refined_fundamental(arrays,side,W,Wx,times=[0.],radii=[WALL])
            q = parent_trace_coordinates({k:v[0,0] for k,v in raw.items()},S,Sx,St)
            for key in keys:target[key][:,start:end]=q[key]
            reconstruction=max(reconstruction,maximum(q['parent_reconstruction_rows']))
        for key,value in target.items():output[side+'_homogeneous_'+key]=value
        summaries[side+'_homogeneous'] = dict(column_count=hcount,
            rhs_Frobenius=norm(target['value']),rhs_max_entry=maximum(target['value']),
            before_uneliminated_row_rhs_Frobenius=norm(target['value']),
            after_affine_coordinate_row_max=0.,after_affine_coordinate_source_row_max=0.,
            parent_reconstruction_max=reconstruction,
            declared_Xi_rhs_Frobenius=norm(target['source']),
            time_pullback_coefficient_Frobenius=norm(target['time']),
            radial_pullback_fixed_frame_coefficient_Frobenius=norm(target['radial_fixed_frame']))
    output.update(parent_material_spin384=S,parent_material_spin_first384=Sx,
        parent_material_spin_time384=St)
    report = dict(classification='EXECUTED_AFFINE_FULL384_EVENT_TRACE_COORDINATE_ELIMINATION',
        equation_executed='qbar_child-S_parent^-1 Gamma_raw_parent=0 at the original E1 wall',
        child_coordinate_definition='qbar_child=D_parent^-1 K0^-1 D_child S_child^-1 Gamma_raw_child',
        child_reconstruction='Gamma_raw_child=S_child D_child^-1 K0 D_parent qbar_child',
        physical_event_equation='Gamma0_child-U_R (Gamma0_parent composed with F_B)=0',
        physical_event_residual=None,full_physical_event_solved=False,
        numerical_coordinate_rows=summaries,
        remaining_parent_homogeneous_coordinates=hcount,homogeneous_coordinates_per_node=366,
        parent_h_values_assigned=False,parent_h_source_coefficient='same homogeneous_value matrix multiplies independent delta h',
        amplitude_relations='a_R=(u_R,+ P_L+u_R,- P_R)g; a_LR=g/u_L,+; a_RL=g/u_L,-; g and independent normal profiles remain unknown',
        amplitude_source_coefficient='same particular value matrix multiplies independent delta a; complete normal/profile/g source remains open',
        scalar_angular_pullback='the represented parent Y0=1 is constant under angular F_B pullback; no angular/spin/bundle map is selected',
        middle_lift_K0_selected=False,density_normal_maps_selected=False,
        normalized_child_coordinates_identified=False,child_projector_or_angular_image_closure_assumed=False,
        saved_eta_frame_equals_material_frame_assumed=False,
        Jacobi_equation='delta Gamma_c-(delta U_R)(Gamma_p composed F_B)-U_R[(delta Gamma_p composed F_B)+(dGamma_p composed F_B)delta F_B]=0',
        parent_coordinate_source='S_p^-1 deltaXi Gamma_p-S_p^-1 deltaXi S_p qbar_parent, plus independent amplitude and h derivatives',
        parent_time_coefficient='S_p^-1 partial_t Gamma_p-S_p^-1 partial_t S_p qbar_parent',
        parent_radial_coefficient='saved radial_fixed_frame-S_p^-1(partial_rho S_p)qbar_parent; physical radial frame extension is unassigned',
        moving_child_point='delta F_B is total, including DF_B delta x_child once; no second child-point contact is appended',
        source_gradient_scope='ambient source gradients are saved in parent frame; unknown mixed frame/source and physical domain contacts are not set to zero',
        physical_outer_equations_solved=False,normal_profile_normalization=None,
        child_future_D5_solved=False,mechanical_formation_solution_selected=False,
        physical_admission=False,error_scope='exact finite coefficient elimination only; original bulk/family/source nonpasses and unknown physical source remain separate')
    return output,report
