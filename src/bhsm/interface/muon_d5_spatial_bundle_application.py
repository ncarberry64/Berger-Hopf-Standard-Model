"""Actual homogeneous E1 spatial connection graph and its field-source rows.

Every algebraic orientation candidate is retained. A value-level spatial
connection equation determines its SU2/rotation factors, rather than a
fermion fit. Right translation, central phase and spin-cover freedom remain.
Field corrections below solve only these boundary Jacobi equations; they
are not Maxwell stationarity or a selected physical event state.
"""
from __future__ import annotations

from itertools import product
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.linalg import expm

from .muon_parent_retarded_hypercharge import WALL
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_intrinsic_worldvolume_scalar_transport import unit_quaternion_to_su2


def cross_matrix(vector):
    x,y,z=np.asarray(vector,float)
    return np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])


def rotation_su2(rotation):
    """One computational double-cover representative; both signs remain free."""
    q=Rotation.from_matrix(rotation).as_quat(canonical=True)
    return unit_quaternion_to_su2(np.array([[q[3],q[0],q[1],q[2]]]))[0]


def known_spin_gauge_factor(base_rotation,gauge_rotation):
    """Known SU2/spatial-Spin factors; independent U1/SU3 factors stay open.

    The spin pullback uses O^-1, since F sends child frame i to O[j,i]
    times parent frame j. This function checks the original Clifford law.
    """
    full=full_d5_localized_lepton_trace();G=full['gamma5D_self_dual128']
    O,R=np.asarray(base_rotation),np.asarray(gauge_rotation)
    generators=np.array([G[2]@G[3],G[3]@G[1],G[1]@G[2]])/2
    theta=Rotation.from_matrix(O.T).as_rotvec()
    spin=expm(np.einsum('i,iab->ab',theta,generators))
    K2=rotation_su2(R);K16=np.eye(16,dtype=complex)
    for a in (0,2,4,6):K16[a:a+2,a:a+2]=K2
    gauge=np.block([[np.kron(np.eye(4),K16),np.zeros((64,64),complex)],
        [np.zeros((64,64),complex),np.kron(np.eye(4),K16.conj())]])
    middle=spin@gauge
    J2=-1j*np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])/2
    gauge_generators=[]
    for j2 in J2:
        j16=np.zeros((16,16),complex)
        for a in (0,2,4,6):j16[a:a+2,a:a+2]=j2
        gauge_generators.append(np.block([[np.kron(np.eye(4),j16),np.zeros((64,64),complex)],
            [np.zeros((64,64),complex),np.kron(np.eye(4),j16.conj())]]))
    # deltaO=O Omega_base -> delta(O^-1)=-Omega_base O^-1.
    free=np.array([-a@middle for a in generators]+[a@middle for a in gauge_generators])
    inverse=np.linalg.inv(middle)
    cliff=np.array([middle@sum(O[j,i]*G[j+1] for j in range(3))@inverse-G[i+1] for i in range(3)])
    return dict(known_middle128=middle,known_middle_free_rotation_first128=free,
        known_spatial_spin128=spin,known_SU2_gauge128=gauge,
        original_Clifford_pullback_rows=cliff)


def spatial_connection_row(parent,child,base_rotation,gauge_rotation):
    """Child->parent F, with F* A_parent=O.T A_parent and Ad(K)=R.

    Row order is unit-Tr16 (A1 H1,H2,H3,HY, A2..., A3...).
    """
    p,c=np.asarray(parent),np.asarray(child)
    O,R=np.asarray(base_rotation),np.asarray(gauge_rotation)
    if p.shape!=(3,4) or c.shape!=p.shape or O.shape!=(3,3) or R.shape!=(3,3):
        raise ValueError('complete unit-Tr16 spatial connection and SO3 factors required')
    target=np.column_stack((O.T@p[:,:3]@R.T,O.T@p[:,3]))
    return (c-target).ravel()


def spatial_rotation_jacobian(child):
    """deltaO=O Omega_b, deltaR=Omega_g R; independent six rotation slots."""
    c=np.asarray(child)
    if c.shape!=(3,4):raise ValueError('three complete unit-Tr16 rows required')
    columns=[]
    for axis in np.eye(3):
        columns.append((cross_matrix(axis)@c).ravel())
    for axis in np.eye(3):
        a=np.zeros((3,4),dtype=c.dtype);a[:,:3]=c[:,:3]@cross_matrix(axis)
        columns.append(a.ravel())
    return np.column_stack(columns)


def _real(a):
    a=np.asarray(a)
    if np.iscomplexobj(a) and np.any(a.imag!=0):
        raise ValueError('actual real-background connection required; no complex projection')
    return np.asarray(a.real if np.iscomplexobj(a) else a,float)


def _curvature_component_matrix(connection):
    """Original homogeneous weak curvature F23,F31,F12 in unit-Tr16 basis."""
    A=np.asarray(connection)
    return np.array([2*A[i,:3]+np.cross(A[j,:3],A[k,:3])/np.sqrt(2)
        for i,j,k in ((0,1,2),(1,2,0),(2,0,1))])


def spatial_bundle_application(parent_coefficients,child_coefficients,child_history):
    """Solve value orientation families and full12 field Jacobi equations.

    Nonflat full-rank weak curvature plus a round-S3 isometry implies the
    gauge adjoint is spatially constant. The residual U1 phase has constant
    right-frame derivatives; d²phi=0 and [Ei,Ej]=-2eps E force them zero.
    Consequently the constant O/R reduction follows on this represented
    homogeneous wall component. It supplies no general angular closure.
    """
    p,c=parent_coefficients,child_coefficients
    for a in (p,c):
        if not np.array_equal(a['radial_points'],[WALL]):raise ValueError('actual E1 wall only')
    Ap,Ac=(_real(a['gauge_connection_material'][0,2:]) for a in (p,c))
    Apx,Acx=(_real(a['gauge_connection_material_first'][0,0,2:]) for a in (p,c))
    Fp,Fc=(_curvature_component_matrix(a) for a in (Ap,Ac))
    fp_s,fc_s=(np.linalg.svd(f,compute_uv=False) for f in (Fp,Fc))
    if min(fp_s[-1],fc_s[-1])<1e-12:
        raise ValueError('constant-adjoint reduction unavailable at a degenerate weak curvature')
    Up,sp,Vpt=np.linalg.svd(Ap[:,:3]);Uc,sc,Vct=np.linalg.svd(Ac[:,:3])
    # The exact wall trace lift, not an assumed unit wall profile.
    trace=np.asarray(child_history.gauge_basis(np.array([WALL])))[0].reshape(5,4,80)[2:].reshape(12,80)
    labels=child_history.original_radial_representation['gauge_labels']
    selected=np.array([k for k,a in enumerate(labels) if a['wall_lift'] and a['field'] in ('A_1','A_2','A_3')])
    B=trace[:,selected]
    if len(selected)!=12 or np.linalg.matrix_rank(B)!=12:
        raise ValueError('all12 original independent spatial wall-field pivots required')
    records=[];out=dict(parent_spatial_connection=Ap,child_spatial_connection=Ac,
        parent_spatial_connection_first=Apx,child_spatial_connection_first=Acx,
        parent_weak_curvature_components=Fp,child_weak_curvature_components=Fc,
        parent_weak_curvature_singular_values=fp_s,child_weak_curvature_singular_values=fc_s,
        parent_weak_connection_singular_values=sp,child_weak_connection_singular_values=sc,
        child_spatial_wall_field_raw_indices=100+selected,child_spatial_wall_trace_pivot=B)
    Olist=[];Rlist=[];Klist=[];rows=[];source_rows=[];fields=[];raws=[];free_raw=[];after=[];matrows=[];signs=[];middle_rows=[]
    higgs=higgs_u2_real_representation()['complex_generators']
    for sign in product((-1.,1.),repeat=3):
        S=np.diag(sign);O=Up@S@Uc.T;R=Vct.T@S@Vpt
        if min(np.linalg.det(O),np.linalg.det(R))<0:continue
        K=rotation_su2(R)
        row=spatial_connection_row(Ap,Ac,O,R)
        rowx=spatial_connection_row(Apx,Acx,O,R)
        target=Ac-row.reshape(3,4)
        # Jacobian is evaluated at the actual transformed parent operand,
        # not by silently substituting a value residual equal to zero.
        J=spatial_rotation_jacobian(target)
        correction=np.linalg.solve(B,-rowx)
        free=-np.linalg.solve(B,J)
        raw=np.zeros(268);raw[100+selected]=correction
        rawfree=np.zeros((268,6));rawfree[100+selected]=free
        reconstructed=spatial_connection_row(Apx,Acx+(trace@raw[100:180]).reshape(3,4),O,R)
        source_free_rows=J+B@free
        Aparent=np.einsum('ic,cab->iab',O.T@Ap,higgs)
        Achild=np.einsum('ic,cab->iab',Ac,higgs)
        mr=Achild@K-K@Aparent
        middle=known_spin_gauge_factor(O,R);middle_rows.append(middle)
        Olist.append(O);Rlist.append(R);Klist.append(K);rows.append(row);source_rows.append(rowx)
        fields.append(correction);raws.append(raw);free_raw.append(rawfree);after.append(reconstructed);matrows.append(mr);signs.append(sign)
        records.append(dict(candidate_index=len(records),orientation_signs=list(sign),
            value_component_row_max=float(np.max(abs(row))),value_Higgs2_intertwiner_row_max=float(np.max(abs(mr))),
            source_component_row_before_max=float(np.max(abs(rowx))),source_component_row_after_max=float(np.max(abs(reconstructed))),
            child_wall_field_correction_max=float(np.max(abs(correction))),
            original_Clifford_pullback_max=float(np.max(abs(middle['original_Clifford_pullback_rows']))),
            free_rotation_coefficient_row_max=float(np.max(abs(source_free_rows))),
            joint_row_rank=int(np.linalg.matrix_rank(np.c_[B,J])),
            rotation_only_singular_values=np.linalg.svd(J,compute_uv=False).tolist(),
            candidate_selected_as_physical_map=False))
    if not records:raise ValueError('no orientation/spin preserving algebraic candidate exists')
    out.update(base_rotations=np.array(Olist),gauge_rotations=np.array(Rlist),
        gauge_SU2_lifts=np.array(Klist),orientation_signs=np.array(signs),
        value_component_rows=np.array(rows),value_Higgs2_intertwiner_rows=np.array(matrows),
        source_component_rows_before=np.array(source_rows),source_component_rows_after=np.array(after),
        child_wall_field_source_corrections=np.array(fields),
        child_raw_field_source_corrections=np.array(raws),
        child_raw_field_free_rotation_coefficients=np.array(free_raw))
    out.update({key:np.array([a[key] for a in middle_rows]) for key in middle_rows[0]})
    # Report the finite value-equation residual for EVERY candidate; even
    # central-incompatible candidates remain historical numerical evidence.
    report=dict(classification='EXECUTED_FULL_SPATIAL_CONNECTION_FAMILY_AND_CHILD_FIELD_SOURCE_ELIMINATION',
        original_equation='A_child,i K=K sum_j O[j,i] A_parent,j with child->parent F(q)=a q b, Ad(a)=O',
        full_component_equation='[C_child-O.T C_parent R.T, y_child-O.T y_parent]=0',
        row_order='A1[H1,H2,H3,HY],A2[H1,H2,H3,HY],A3[H1,H2,H3,HY]',
        source_equation='row_Xi+B_child_wall delta_field+J_base_gauge delta_rot=0',
        candidates=records,candidate_count=len(records),spatial_gauge_adjoint_constant_derived_on_this_component=True,
        constant_phase_derivative_equation='E_i phi=constant_i; d2phi=0 and [Ei,Ej]=-2epsilon_ijk Ek imply constant_i=0',
        finite_joint_row_rank=12,free_rotation_source_coordinates=6,
        initial_right_translation_parameters=3,initial_central_phase_parameters=1,spin_cover_sign_unselected=True,
        independent_strong_gauge_factor_unassigned=True,
        known_middle_factor_scope='spatial Spin pullback and SU2 factors only; U1 phase, strong-gauge factor and independent density/normal maps remain open',
        independent_wall_field_trace_pivot_rank=12,
        value_singular_spectrum_difference_max=float(np.max(abs(sp-sc))),
        inherited_mechanical_connection_composed_before_restriction=True,
        all_algebraic_candidates_retained=True,no_identity_map_assumed=True,no_fermion_trace_fitted=True,
        source_field_extension='provisional constant raw spatial wall-lift coefficient correction through the saved child cell; its additional raw coordinate-time first is zero, not a physical formation field prescription',
        source_background_value_unchanged=True,source_family_is_not_full_event_solution=True,
        outer_Maxwell_field_stationarity_solved=False,normal_profile_normalization=None,
        parent_homogeneous_coordinates_retained=3660,physical_g_and_normal_sources_assigned=False,
        complete_physical_derivative=False,physical_admission=False,physical_guard=2e-10,
        scope='homogeneous n0 SU2/U1 wall component and necessary full connection rows; no arbitrary strong field, radial extension, native or inherited correlation is assigned',
        error_scope='binary64 finite matrix factorization; near-degenerate singular-value sensitivity is retained, not a continuum or physical error bound')
    return out,report
