"""Exact global current directions in the inherited material source chart.

Right responses and analytic-transpose adjoints have different inverse
unitary maps. Neither the directions nor their coefficients are conjugated.
The full wall/H image and both complete even/odd Gaunt placements remain.
"""
from __future__ import annotations
import numpy as np
from .muon_transported_native_pairing import independent_native_source_images


def restore_original_field_direction(direction,real_to_complex,spectator_indices,*,analytic_adjoint=False):
    """Restore all336 field rows from one exact168-row spectator saddle.

    K_c=U K_real U^dagger, J_R,c=U J_R, J_L,c=U* J_L.
    Thus u_real=U^dagger u_c and p_real=U^T p_c. Frame reactions are
    exported separately and never converted into fictitious field rows.
    """
    y=np.asarray(direction,complex);U=np.asarray(real_to_complex,complex);ids=np.asarray(spectator_indices)
    if (y.ndim<2 or y.shape[-2]!=176 or U.shape!=(4,4) or ids.shape!=(168,)
            or not np.issubdtype(ids.dtype,np.integer) or len(np.unique(ids))!=168
            or np.any(ids<0) or np.any(ids>=336) or not np.isfinite(y).all()
            or not np.isfinite(U).all() or np.max(abs(U.conj().T@U-np.eye(4)))>2e-12):
        raise ValueError('original176 saddle, complete unitary angular map and exact spectator indices required')
    embedded=np.zeros(y.shape[:-2]+(336,y.shape[-1]),complex)
    embedded[...,ids,:]=y[...,:168,:]
    embedded=embedded.reshape(y.shape[:-2]+(84,4,y.shape[-1]))
    back=U.T if analytic_adjoint else U.conj().T
    fields=np.einsum('ab,...fbc->...fac',back,embedded,optimize=True)
    return dict(original_field_direction=fields,original_frame_direction=y[...,168:,:].copy(),
                source_direction_conjugated=False,analytic_transpose_backtransform=bool(analytic_adjoint))


def current_direction_wall_point(nodal_directions,rows,wall_map,real_to_complex,spectator_indices,*,
                                 lapse,right_clock,analytic_adjoint=False):
    """Interpolate one actual source/adjoint and its inherited time germ.

    All24 material At/Ar/Ai/H coordinates are lifted. Their rate is
    iN/w*d_s on the original chart. This rate does not invent kinetic At
    rows; it is a field/source germ for the action's downstream contacts.
    """
    y=np.asarray(nodal_directions,complex);r=np.asarray(rows,complex);W=np.asarray(wall_map,complex)
    N,w=complex(lapse),complex(right_clock)
    if (y.ndim!=3 or y.shape[0]!=2 or y.shape[1]!=176 or r.shape!=(2,3) or W.shape!=(24,84)
            or not np.isfinite(r).all() or not np.isfinite(W).all() or not np.isfinite([N,w]).all() or N==0 or w==0):
        raise ValueError('both original node directions/rows and complete material wall map required')
    p,d=r[:,1],r[:,2]
    v=np.einsum('j,jfc->fc',p,y);t=1j*N/w*np.einsum('j,jfc->fc',d,y)
    rv=restore_original_field_direction(v,real_to_complex,spectator_indices,analytic_adjoint=analytic_adjoint)
    rt=restore_original_field_direction(t,real_to_complex,spectator_indices,analytic_adjoint=analytic_adjoint)
    return dict(wall_coefficients=np.einsum('af,fhc->ahc',W,rv['original_field_direction']),
                wall_coordinate_rate=np.einsum('af,fhc->ahc',W,rt['original_field_direction']),
                original_field_direction=rv['original_field_direction'],
                original_field_coordinate_rate=rt['original_field_direction'],
                original_frame_direction=rv['original_frame_direction'],
                source_direction_conjugated=False,material_At_coefficient_rotated_again=False,
                fixed_geometry_scope='same original converged84-field graph; no geometry field direction introduced')


def native_images_of_current_direction(wall_coefficients,*,radius,lapse,reflected_radius,reflected_lapse,
                                       family,even_field_odd_gaunt):
    """Apply each independently sharp source to the complete0+2/1 image.

    Wall coefficients have (wall24,realn1=4,currentcolumn). Both source
    placements retain the original real Gaunt and independently fixed
    body dual. No source SVD, covariance, external spin or charged/neutral
    member is selected by this representation.
    """
    c=np.asarray(wall_coefficients,complex);G=np.asarray(even_field_odd_gaunt,complex)
    if (c.ndim!=3 or c.shape[:2]!=(24,4) or G.shape!=(10,4,4)
            or not np.isfinite(c).all() or not np.isfinite(G).all()):
        raise ValueError('all24 wall coordinates, complete realn1 source and full n0+n2 Gaunt image required')
    coeff=c.transpose(2,0,1)
    a=independent_native_source_images(coeff[:,:20].reshape(-1,5,4,4),coeff[:,20:],
        radius=radius,lapse=lapse,reflected_radius=reflected_radius,reflected_lapse=reflected_lapse,
        family=family,transport_lorentz_coordinates=True)
    X,Xs=a['Xi'],a['Xisharp'];n=len(X)
    forward=np.einsum('ths,chij->citjs',G,X,optimize=True).reshape(n,60,24)
    reverse=np.einsum('ths,chij->cisjt',G,X,optimize=True).reshape(n,24,60)
    dual_reverse=np.einsum('ths,chij->cisjt',G,Xs,optimize=True).reshape(n,24,60)
    dual_forward=np.einsum('ths,chij->citjs',G,Xs,optimize=True).reshape(n,60,24)
    return dict(Xi_source_harmonics=X,independent_Xisharp_source_harmonics=Xs,
        even_from_odd_source=forward,odd_from_even_source=reverse,
        independent_dual_odd_from_even_source=dual_reverse,independent_dual_even_from_odd_source=dual_forward,
        source_direction_conjugated=False,complete_even_harmonics=10,complete_odd_harmonics=4,
        action_scalar_H_source_retained=True,material_At_rotation_inserted_once=True,
        physical_pole_or_native_loop_completion_selected=False)
