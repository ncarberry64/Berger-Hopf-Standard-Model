"""Original coupled field action on the restored finite contour graph.

The coefficient family is the saved literal Lorentz M/B/K polynomial.
Field variables use the common material Lorentz one-form coordinates;
proper A_tau,E=(-i/N)A_t,L is a pointwise coframe conversion, not an
identity between unequal proper-lapse trace coordinates.  This module
does not replace that signed bilinear action by a reflected norm.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor,lu_solve


def common_field_proper_forms(lorentz_forms,lapse,At_count):
    """Pull literal proper-Euclidean forms back to common Lorentz labels.

    The temporal-coordinate derivative multiplies only algebraic At rate
    rows. Their vanishing is checked before using this exact conversion.
    No extra wall advection or reflection of coefficient variables occurs.
    """
    from .muon_literal_euclidean_higgs_green import literal_proper_euclidean_forms
    app=literal_proper_euclidean_forms(lorentz_forms,lapse,At_count)
    R=app['coordinate_rotation'];outer=R[:,None]*R[None,:]
    result=tuple(outer*a for a in app['forms'])
    M,B,K=(np.asarray(a,complex)for a in lorentz_forms);N=complex(lapse)
    expected=(N*M,-1j*B,-K/N)
    if max(np.max(abs(a-b))for a,b in zip(result,expected))>2e-12*max(1.,*(np.max(abs(a))for a in expected)):
        raise ArithmeticError('the original one-form coframe pullback failed')
    return dict(forms=result,proper_Euclidean_field_rotation=R,
        derivative_of_rotation_in_algebraic_velocity_slots_only=True,
        common_coordinates='material Lorentz At/Ar/Ai and realified intrinsic H',
        reflected_absolute_square_substituted=False)


def continued_field_weak_action(quadrature,*,temporal_nodes,At_count,frame_indices):
    """Assemble every original field/Gauss row and both endpoint traces.

    Each item contains its literal common-label proper forms, original
    holomorphic measure and right clock, and FE rows(node,value,d_s value).
    The initial right trace alone is removed; all final cotangents remain.
    Named central radial coordinate frames border the SAME action matrix.
    """
    if not quadrature or type(temporal_nodes)is not int or temporal_nodes<2:
        raise ValueError('actual original coefficient/clock quadrature required')
    d=len(quadrature[0]['forms'][0]);n=temporal_nodes
    if type(At_count)is not int or not 0<At_count<d:
        raise ValueError('all original At/Gauss coordinates must be identified')
    frames=np.asarray(frame_indices,int)
    if frames.ndim!=1 or len(set(frames.tolist()))!=len(frames) or np.any((frames<At_count)|(frames>=d)):
        raise ValueError('literal named dynamic frame rows required')
    K=np.zeros((n*d,n*d),complex)
    for q in quadrature:
        M,B,C=(np.asarray(a,complex)for a in q['forms'])
        if any(a.shape!=(d,d)or not np.isfinite(a).all()for a in(M,B,C)):
            raise ValueError('complete common coupled field coefficients required')
        w=complex(q['right_clock']);measure=complex(q['measure'])
        if w==0:raise ValueError('nonzero original holomorphic clock required')
        for j,pj,dj in q['rows']:
            if type(j)is not int or j not in range(n):raise ValueError('actual trace incidence required')
            sj=slice(j*d,(j+1)*d)
            for k,pk,dk in q['rows']:
                sk=slice(k*d,(k+1)*d)
                K[sj,sk]+=measure*(dj*dk*M/w**2+pj*dk*B/w+dj*pk*B.T/w+pj*pk*C)
    free=np.arange(d,n*d);H=K[np.ix_(free,free)]
    frame=(np.arange(n-1)[:,None]*d+frames).ravel()
    C=np.eye(len(free))[frame]
    saddle=np.block([[H,C.T],[C,np.zeros((len(C),len(C)),complex)]])
    return dict(original_all_trace_Hessian=K,original_Hessian=H,frame_rows=C,saddle=saddle,
        free_indices=free,field_count=d,temporal_nodes=n,At_count=At_count,
        Gauss_rows=(np.arange(n-1)[:,None]*d+np.arange(At_count)).ravel(),
        initial_zero_computational_face=True,final_natural_cotangent_retained=True,
        common_material_oneform_trace=True,physical_E0_birth_or_BRST_domain_identified=False,
        reflected_positive_field_action_substituted=False)


def continued_field_wall_inverse(action,wall_trace_map):
    """Solve the full original saddle for every wall source direction.

    This is a source-directed action inverse, not a wall-only Hessian.
    Every interior field, Higgs, At/Gauss and named-frame response remains.
    """
    P=np.asarray(wall_trace_map,complex);d=action['field_count'];n=action['temporal_nodes']-1
    if P.ndim!=2 or P.shape[1]!=d or P.shape[0]%24 or not np.isfinite(P).all():
        raise ValueError('the original complete wall image is required')
    W=np.kron(np.eye(n),P);H=action['original_Hessian'];C=action['frame_rows']
    rhs=np.vstack((W.T,np.zeros((len(C),len(W)),complex)))
    LU=lu_factor(action['saddle'])
    solved=lu_solve(LU,rhs);u,reaction=solved[:len(H)],solved[len(H):]
    original=H@u+C.T@reaction-W.T;frame=C@u
    return dict(field_wall_source_response=u,frame_reactions=reaction,
        wall_source_Green=W@u,wall_trace_map=W,original_action_row_residual=original,
        original_Gauss_row_residual=original[action['Gauss_rows']],frame_residual=frame,
        original_action_row_residual_max=float(np.max(abs(original))),
        original_Gauss_row_residual_max=float(np.max(abs(original[action['Gauss_rows']]))),
        frame_residual_max=float(np.max(abs(frame))),
        initial_face_reaction=action['original_all_trace_Hessian'][:d,d:]@u,
        full_field_not_replaced_by_wall_Hessian=True)


def joint_literal_wall_current_sources(quadrature,*,temporal_nodes,wall_fields,
                                        right_harmonics,even_gaunt,left_tests):
    """Integrate JR and complete C-left before applying the field inverse.

    Items supply gauge-source-selected vertices in common Lorentz labels;
    scalar driving-current rows are zero there, while the field action
    retains its Higgs response. Right/left generators are literal, never
    inferred by a Hilbert dagger. Both field and fermion midpoint halves
    enter via the same piecewise trace shape functions.
    """
    n=temporal_nodes-1;nh=right_harmonics;wall=wall_fields*nh
    G=np.asarray(even_gaunt,float);tests=np.asarray(left_tests,complex)
    if wall_fields!=24 or nh!=4 or G.ndim!=3 or G.shape[1]!=nh or tests.ndim!=3 or tests.shape[1]!=6 or tests.shape[2]!=6*G.shape[2]:
        raise ValueError('complete n1 wall image and matching-test C left maps required')
    ne=G.shape[0];axes=len(tests)
    right=np.zeros((n*6*nh,6,n*wall),complex)
    left=np.zeros((axes,6,n*6*ne,n*wall),complex)
    for q in quadrature:
        V=np.asarray(q['selected_vertices_common'],complex)
        if V.shape!=(24,6,6):raise ValueError('same literal projected current vertices required')
        # Source coefficient c,h enters internal n1 with the unit constant
        # external harmonic; the source harmonic is normalized Haar once.
        JR=np.einsum('cij,th->itjch',V,np.eye(nh)).reshape(6*nh,6,wall)
        raw_left=np.einsum('cij,thx->ixjtch',V,G).reshape(6*G.shape[2],6*ne,wall)
        ell=np.einsum('ado,ofb->adfb',tests,raw_left,optimize=True)
        for j,pj,_ in q['rows']:
            if j==0:continue
            sf,se=slice((j-1)*6*nh,j*6*nh),slice((j-1)*6*ne,j*6*ne)
            for k,pk,_ in q['rows']:
                if k==0:continue
                sb=slice((k-1)*wall,k*wall);weight=complex(q['measure'])*pj*pk
                right[sf,:,sb]+=weight*JR;left[:,:,se,sb]+=weight*ell
    return dict(literal_right_current=right,C_literal_left_current=left,
        scalar_driving_current_removed=True,induced_H_action_removed=False,
        fermion_inverse_or_magnetic_bridge_inserted=False)


def joint_wall_current_responses(wall_inverse,sources):
    """Apply the same full saddle to actual JR and original-transpose C-left.

    Outputs remain factored in wall/source coordinates; no scalar p.u
    shortcut replaces the required rectangular fermion magnetic bridge.
    """
    G=np.asarray(wall_inverse['wall_source_Green']);J=sources['literal_right_current'];L=sources['C_literal_left_current']
    nr=len(G)
    if J.shape[-1]!=nr or L.shape[-1]!=nr:raise ValueError('one common original wall/current graph required')
    jr=J.transpose(2,0,1).reshape(nr,-1)
    return dict(wall_u=G@jr,
        wall_p=np.einsum('bc,adfc->badf',G.transpose(),L,optimize=True).reshape(nr,len(L),-1),
        u_column_shape=J.shape[:2],p_column_shape=L.shape[1:3],
        original_transpose_left=True,rectangular_fermion_bridge_still_required=True,
        old_FE2_source_covariance_reused=False,physical_Pauli_identified=False)
