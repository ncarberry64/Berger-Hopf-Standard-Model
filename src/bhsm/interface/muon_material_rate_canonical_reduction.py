"""Fixed-position material-rate chart for the original canonical action.

This is a constitutive reduction only.  Its x-dependent velocity matrix
is not used as a canonical phase transformation without its x contacts.
Successful reduced states are returned to the original x/Pi coordinates.
"""
from __future__ import annotations
import numpy as np
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_quadratic_canonical_field_elimination import eliminate_quadratic_canonical_fields


def fixed_position_material_rate_chart(raw_geometry,n=106,m=40):
    raw=np.asarray(raw_geometry,complex)
    if raw.shape!=(100,)or(n,m)!=(106,40)or not np.isfinite(raw).all():
        raise ValueError('same full geometry100 and original v106/y40 required')
    ell=np.r_[1.,(-1.)**np.arange(1,13),(-1.)**np.arange(12),np.zeros(12)]
    Cstar=RADIUS0*np.exp(ell@raw[:37]);s=raw[98]
    if not np.isfinite(Cstar)or Cstar==0:raise ValueError('nonsingular original material wall chart required')
    T=np.eye(n+m,dtype=complex);T[37,:37]=s*ell;T[37,37]=Cstar
    Ti=np.eye(n+m,dtype=complex);Ti[37,:37]=-s*ell/Cstar;Ti[37,37]=1/Cstar
    phase=np.eye(2*n+m,dtype=complex);phase[n:,n:]=T
    return dict(velocity_algebraic_lift=T,velocity_algebraic_inverse=Ti,
        fixed_position_phase_lift=phase,Cstar=Cstar,normal_coordinate=s,wall_log_rate_covector=ell,
        field_indices=np.r_[np.arange(37),np.arange(38,n),np.arange(n+24,n+m)],
        nonlinear_geometry_indices=np.r_[37,np.arange(n,n+24)],
        identity_residual=T@Ti-np.eye(n+m),
        transform_scope='fixed x only: raw normalrate=Cstar*d+s*ell.qdot; d is material wall delta rate',
        canonical_x_force_transform_without_chart_contacts=False)


def eliminate_material_rate_quadratic_fields(eta,p0,evaluate,frame,chart,*,frame_reference=None):
    """Solve121 original quadratic coordinates+2 frames, leave25 rows."""
    eta=np.asarray(eta,complex);p0=np.asarray(p0,complex);n=len(p0)
    T,Ti,S=(chart[k]for k in('velocity_algebraic_lift','velocity_algebraic_inverse','fixed_position_phase_lift'))
    fixed=eta[:n].copy();enew=np.r_[fixed,Ti@eta[n:]]
    target=T.T@np.r_[p0,np.zeros(len(eta)-2*n,complex)]
    if np.any(target[n:]):raise ValueError('this original material chart cannot move algebraic target rows')
    reference=eta[n:]if frame_reference is None else np.asarray(frame_reference,complex)
    newframe=dict(named_frame_covectors=frame['named_frame_covectors']@T,
                  literal_generators=Ti@frame['literal_generators'])
    def application(e):
        if not np.array_equal(e[:n],fixed):raise ValueError('fixed-x material congruence only')
        a=evaluate(S@e)
        return dict(value=a['value'],gradient=S.T@a['gradient'],hessian=S.T@a['hessian']@S,
                    original_action=a)
    a=eliminate_quadratic_canonical_fields(enew,target[:n],application,newframe,
        field_indices=chart['field_indices'],geometry_indices=chart['nonlinear_geometry_indices'],frame_reference=Ti@reference)
    original_eta=S@a['coefficients'];original=a['action']['original_action']
    original_r=np.r_[original['gradient'][n:2*n]-p0,original['gradient'][2*n:]]
    a.update(original_coefficients=original_eta,original_canonical_momentum_target=p0,
        original_action=original,original_coordinate_constitutive_rows=original_r,
        original_named_frame_reference=reference,original_literal_generator_image=original['hessian'][n:,n:]@frame['literal_generators'],
        original_literal_gauge_source_compatibility=frame['literal_generators'].T@original_r,
        transformed_original_row_identity=a['original_constitutive_rows']-T.T@original_r,
        fixed_original_position_defect=original_eta[:n]-fixed,
        material_rate=original_eta[n+37]/chart['Cstar']-chart['normal_coordinate']*(chart['wall_log_rate_covector']@original_eta[n:n+37])/chart['Cstar'],
        material_rate_chart=chart,original_x_force_has_not_been_replaced=True)
    return a
