"""Pointwise symmetry integrability and covariant charge on one comparison.

This version supersedes the constant-compensator proof scope of the v1
application. It does not select a stationary past, a dressed state, or a
collider incidence. All coefficients belong to the saved intrinsic round
S3 comparison, with its complete constant-angular eighteen-component fiber.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import qr

from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_primal_electromagnetic_source import higgs_aligned_charge
from .muon_incoming_comparison_time_lift import execute_electron_comparison


def _comm(a, b):
    return a @ b - b @ a


def stationary_curvature_rows(theta, theta_gradient):
    """Evaluate original F and its full declared comparison source.

    Ei are unit RIGHT-body duals, [Ei,Ej]=-2 epsilon_ijk Ek. Ai are
    unit-S3 components, A0=At/ell is proper time. Hence F23=(2A1+
    [A2,A3])/R^2 and F0i=[A0,Ai]/R. These include the central
    Maurer-Cartan terms, not merely matrix commutators. R/ell vary in
    the source; they are not replaced by a unit frame.
    """
    t, g = np.asarray(theta), np.asarray(theta_gradient)
    if (t.shape != (22,) or g.ndim != 2 or g.shape[0] != 22
            or not np.isrealobj(t) or not np.isrealobj(g)
            or not np.isfinite(t).all() or not np.isfinite(g).all()
            or min(t[:2]) <= 0):
        raise ValueError('same real22 coefficients and declared source map required')
    R, ell = t[:2]
    G = higgs_u2_real_representation()['complex_generators']
    body = np.einsum('mc,cab->mab', t[6:18].reshape(3,4), G)
    body_x = np.einsum('kmc,cab->kmab', g[6:18].T.reshape(-1,3,4), G)
    temporal = np.einsum('c,cab->ab', t[2:6]/ell, G)
    temporal_x = np.einsum('kc,cab->kab',
        g[2:6].T/ell-t[2:6][None]*g[1,:,None]/ell**2, G)
    F, Fx = [], []
    for i in range(3):
        f = _comm(temporal,body[i])/R
        fx = (_comm(temporal_x,body[i])+_comm(temporal,body_x[:,i]))/R
        fx -= f[None]*g[0,:,None,None]/R
        F.append(f); Fx.append(fx)
    for i,j,k in ((0,1,2),(1,2,0),(2,0,1)):
        f = (2*body[i]+_comm(body[j],body[k]))/R**2
        fx = (2*body_x[:,i]+_comm(body_x[:,j],body[k])
            +_comm(body[j],body_x[:,k]))/R**2
        fx -= 2*f[None]*g[0,:,None,None]/R
        F.append(f); Fx.append(fx)
    F, Fx = np.asarray(F), np.asarray(Fx).swapaxes(0,1)
    H = t[18:20]+1j*t[20:22]
    Hx = g[18:20].T+1j*g[20:22].T
    columns, source_columns = [], []
    for generator in G:
        z = np.r_[_comm(F,generator).ravel(),generator@H]
        zx = np.concatenate((_comm(Fx,generator).reshape(len(Hx),-1),
            np.einsum('ab,kb->ka',generator,Hx)),axis=1)
        columns.append(np.r_[z.real,z.imag])
        source_columns.append(np.concatenate((zx.real,zx.imag),axis=1))
    return dict(original_curvature=F,original_curvature_source=Fx,
        original_integrability_matrix=np.column_stack(columns),
        original_integrability_matrix_source=np.stack(source_columns,axis=-1),
        proper_Higgs_temporal_connection=temporal,
        proper_Higgs_temporal_connection_source=temporal_x,
        unit_S3_Higgs_spatial_connection=body,Higgs_section=H,
        Higgs_section_source=Hx)


def execute_pointwise_time_lift(theta, theta_gradient):
    """Solve necessary integrability without assuming lambda spatially constant.

    On this stationary coefficient background the original symmetry laws
    are D_mu lambda=0, lambda_H H=0. Their integrability gives [F,lambda]=0.
    A rank-four pointwise matrix forces lambda=0 locally. A parallel
    section then vanishes throughout a connected comparison component;
    zero also solves all the original symmetry equations. A rank failure
    retains its nullspace, rather than imposing a constant-class answer.
    This establishes only the represented U2 time lift, not stationarity
    of the complete interacting background.
    """
    a=stationary_curvature_rows(theta,theta_gradient)
    C=a['original_integrability_matrix']
    _,s,Vh=np.linalg.svd(C,full_matrices=False)
    rank=int(np.sum(s>1e-12*max(1.,s[0])))
    _,_,p=qr(C.T,pivoting=True,mode='economic')
    piv=np.asarray(p[:rank])
    a.update(pointwise_time_gauge_rank=np.array(rank),
        pointwise_integrability_singular_values=s,
        pointwise_original_row_pivots=piv,
        pointwise_remaining_gauge_generators=Vh[rank:].T,
        proper_material_clock_inverse=np.array(1/float(theta[1])),
        proper_material_clock_inverse_source=-np.asarray(theta_gradient)[1]/theta[1]**2)
    if rank == 4:
        lam=np.linalg.solve(C[piv],np.zeros(4))
        # C Dlambda = -(DC)lambda is solved on the SAME original pivot.
        rhs=-np.einsum('krc,c->kr',a['original_integrability_matrix_source'],lam)
        lamx=np.linalg.solve(C[piv],rhs[:,piv].T).T
        a.update(pointwise_gauge_compensator=lam,
            pointwise_gauge_compensator_source=lamx,
            pointwise_original_integrability_rows=C@lam,
            pointwise_original_integrability_source_rows=(
                np.einsum('rc,kc->kr',C,lamx)
                +np.einsum('krc,c->kr',a['original_integrability_matrix_source'],lam)),
            pointwise_pivot_condition=np.array(np.linalg.cond(C[piv])))
    return a


def execute_covariant_electron_comparison(theta, theta_gradient, *, comparison_data=None):
    """Consume pointwise time lift in the original charge-stationarity row.

    With h=W-iOmega, the one-body covariant charge contact is
        ordinary_Qdot+i[h,Q] = D_tau Q+i[W,Q].
    Ordinary Qdot=0 only on the stationary comparison; D_tau Q retains
    [Omega,Q], including the H covariant motion. It is not added twice.
    A nonzero row is a dressing/coupled-charge obligation, not a failure
    or nonuniqueness theorem for the adopted incoming prescription.
    """
    t,g=np.asarray(theta),np.asarray(theta_gradient)
    lift=execute_pointwise_time_lift(t,g)
    if int(lift['pointwise_time_gauge_rank']) != 4:
        raise ValueError('retain the unresolved pointwise time-lift family before sector application')
    # This reuses only existing coefficient/projector/current applications.
    # Its v1 constant-class lift entries remain explicitly diagnostic.
    if comparison_data is None:
        a=execute_electron_comparison(t,g)
    else:
        a=dict(comparison_data)
        if (not np.array_equal(a.get('input_theta22'),t)
                or not np.array_equal(a.get('input_theta_gradient22x151'),g)):
            raise ValueError('reused comparison application must match exact input identities')
    C=a['electron_family_lift']; Q=a['electron_Higgs_charge']
    Qx=a['electron_charge_source']; h=a['electron_H']; hx=a['electron_H_source']
    Omega=C.T@a['Omega']@C
    G=lepton_unit_trace_gauge_representation()['generators']
    Omegax=np.einsum('kc,cab->kab',g[2:6].T/t[1]-t[2:6][None]*g[1,:,None]/t[1]**2,G)
    Omegax=np.einsum('ai,kab,bj->kij',C,Omegax,C)
    W=C.T@a['W']@C; Wx=hx+1j*Omegax
    covariant_Qdot=_comm(Omega,Q)
    covariant_Qdot_x=_comm(Omegax,Q)+_comm(Omega,Qx)
    row=covariant_Qdot+1j*_comm(W,Q)
    rowx=covariant_Qdot_x+1j*(_comm(Wx,Q)+_comm(W,Qx))
    ordinary_form=1j*_comm(h,Q)
    ordinary_form_x=1j*(_comm(hx,Q)+_comm(h,Qx))
    H=lift['Higgs_section']; DH=lift['proper_Higgs_temporal_connection']@H
    via_H=C.T@higgs_aligned_charge(H,DH)['charge_rate']@C
    a.update(lift)
    a.update(electron_proper_temporal_connection=Omega,
        electron_proper_temporal_connection_source=Omegax,
        ordinary_charge_time_rate=np.zeros_like(Q),
        covariant_Higgs_time_rate=DH,
        covariant_charge_time_rate=covariant_Qdot,
        covariant_charge_time_rate_source=covariant_Qdot_x,
        covariant_Higgs_charge_rate_identity_rows=via_H-covariant_Qdot,
        original_covariant_charge_stationarity_rows=row,
        original_covariant_charge_stationarity_source_rows=rowx,
        original_charge_clock_forms_identity_rows=row-ordinary_form,
        original_charge_clock_forms_source_identity_rows=rowx-ordinary_form_x,
        pointwise_proof_replaces_constant_compensator_class=True)
    return a
