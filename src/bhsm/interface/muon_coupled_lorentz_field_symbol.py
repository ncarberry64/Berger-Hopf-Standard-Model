"""Consumer-directed full signed field symbol on the retained radial domain."""
from __future__ import annotations
import numpy as np
from .muon_local_normal_action_symbol import chronological_frequency_polynomial


def coupled_field_symbol(action,representation,*,lapse,H):
    """Restrict fixed geometry, retaining all radial gauge fields and Higgs.

    This is a weak-action restriction, not an intrinsic pointwise Maxwell
    model.  The original four named central A_rho slices provide the
    inherited computational frame; their reactions remain exported.
    """
    if not np.isfinite(lapse) or lapse<=0 or not np.isrealobj(H):
        raise ValueError('same real body and positive proper clock required')
    c=action['coordinates'];nx=c['x_count'];ny=c['y_count']
    x=np.arange(38,nx);y=np.arange(2*nx+24,2*nx+ny)
    ids=np.r_[x,nx+x,y];field_hessian=action['hessian'][np.ix_(ids,ids)]
    n=len(x);p=chronological_frequency_polynomial(field_hessian,n)
    coeff=np.array([p['constant']/lapse,1j*p['imaginary_linear'],lapse*p['quadratic']],complex)
    trace=np.zeros((24,n+len(y)))
    dynamic=c['dynamic_gauge_indices'];algebraic=c['At_indices']
    trace[:20,:len(dynamic)]=representation['wall_trace_map'].reshape(20,-1)[:,dynamic]
    trace[:20,n:]=representation['wall_trace_map'].reshape(20,-1)[:,algebraic]
    trace[20:,n-4:n]=np.eye(4)
    labels=representation['gauge_labels']
    framed=np.array([j for j,i in enumerate(dynamic)
        if labels[i]['field']=='A_rho' and labels[i]['internal']==3])
    if len(framed)!=4:raise ValueError('the inherited four central radial frame slices are required')
    frames=np.eye(len(trace.T))[framed]
    free=np.array([j for j in range(len(trace.T)) if j not in framed])
    lift=np.eye(len(trace.T))[:,free]
    norm=np.linalg.norm(H)
    if not np.isfinite(norm) or norm<=0:raise ValueError('actual nonzero radial Higgs section required')
    radial=np.zeros(len(trace.T));radial[n-4:n]=np.asarray(H)/norm/np.sqrt(2)
    return dict(proper_frequency_coefficients=coeff,field_quotient_lift=lift,
        joint_trace_map=trace,scalar_radial_source=radial,central_radial_frame_rows=frames,
        field_action_hessian=field_hessian,field_action_gradient=action['gradient'][ids],
        fixed_geometry_field_indices=ids,
        field_order='64 dynamic gauges ordered by original labels, Hreal4, algebraic A_t16',
        gauge_radial_domain='all four inherited radial functions; regular carrier, exact affine enrichment and wall lift',
        gauge_frame='four inherited central A_rho coordinate slices; original reactions required',
        normalization='original cap action including Maxwell-to-cap factor and scalar /VOLUME² once; proper density L_tau=L_t/lapse',
        local_fourier='delta x=exp(i omega_tau*lapse*t)x; metric and original full signed field coefficients held locally',
        BRST_or_full_physical_quotient_established=False,
        gauge_frame_equivalence_established=False,global_boundary_or_pole_identified=False,
        physical_Pauli=None,physical_overlap_subtracted=False)


def apply_weak_symbol(coefficients,omega,right):
    """Apply the original polynomial without constructing an inverse."""
    p=np.asarray(coefficients,complex);r=np.asarray(right,complex)
    if p.ndim!=3 or p.shape[0]!=3 or p.shape[1]!=p.shape[2] or r.shape[0]!=p.shape[1]:
        raise ValueError('same full weak polynomial and right source domain required')
    return sum(p[k]@r*omega**k for k in range(3))
