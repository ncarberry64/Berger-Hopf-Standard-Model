"""Actual proper-normal mixed source of the signed material action.

The source is a prescribed trial amplitude, not an action-selected mode.
Independent phase-rate variations are retained as weak covectors, rather
than erased while changing from raw normal coordinate to proper length.
"""
import numpy as np
from .muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt


def proper_normal_shape_coefficient(raw,one_lift):
    """At fixed coordinate time, delta s=Cstar sqrt(1-U²)/Cwall * psi.

    For the owned outward convention this is the reciprocal of the x37
    proper-normal graph trace. Fields are fixed in the original MATERIAL
    chart; this does not add an Eulerian advection to the embedded action.
    """
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(np.asarray(raw,complex)[:100])
    f=_fields(12,q,v,m,wall);U=f['C']*(dr+f['beta'])/f['N']
    a=Cstar*_sqrt(1-U*U)/f['C'];P=np.asarray(one_lift,complex)[:100]
    return dict(value=a.value,gradient=P.T@a.gradient,hessian=P.T@a.hessian@P,
        raw_gradient=a.gradient,raw_hessian=a.hessian,wall_velocity=U.value,
        proper_graph_direction_is_not_a_time_embedding_shift=True)


def mixed_normal_shape_weak_source(G,H,rate,a,da,dda,*,normal_position,
        normal_velocity,amplitude,amplitude_coordinate_first):
    """D[L_eta b] = (H b+Db.T G) d eta + (Db_rate.T G) d eta_dot.

    b_s=a psi; b_v=(D_eta a . eta_dot)psi+a psi_dot. The normal
    coframe depends on v/y, so its rate covector must stay in the weak
    action until the chronological domain/canonical rate is applied.
    Inputs are literal analytic coefficients, with no conjugation.
    """
    G=np.asarray(G,complex);H=np.asarray(H,complex);r=np.asarray(rate,complex)
    da=np.asarray(da,complex);dda=np.asarray(dda,complex);d=len(G)
    if H.shape!=(d,d)or r.shape!=(d,)or da.shape!=(d,)or dda.shape!=(d,d):
        raise ValueError('full original action and independent phase/rate shape jets required')
    s=int(normal_position);v=int(normal_velocity);psi=complex(amplitude);pt=complex(amplitude_coordinate_first)
    b=np.zeros(d,complex);b[s]=a*psi;b[v]=(da@r)*psi+a*pt
    Db=np.zeros((d,d),complex);Db[s]=psi*da;Db[v]=psi*(dda@r)+pt*da
    Dr=np.zeros((d,d),complex);Dr[v]=psi*da
    ordinary=H@b;embedding=Db.T@G;rate_contact=Dr.T@G
    return dict(shape_direction=b,shape_direction_state_first=Db,
        shape_direction_rate_first=Dr,ordinary_action_shape_source=ordinary,
        moving_embedding_action_source=embedding,
        full_weak_state_source=ordinary+embedding,full_weak_phase_rate_source=rate_contact,
        literal_shape_action_state_gradient=H.T@b+embedding,
        stored_mixed_source_minus_literal_gradient=(H-H.T)@b,
        shape_action_first=np.array(G@b),normal_amplitude=np.array(psi),
        normal_amplitude_coordinate_first=np.array(pt),
        proper_graph_coefficient=np.array(a),proper_graph_coefficient_time_first=np.array(da@r),
        phase_rate_contact_not_silently_frozen=True)


def normal_shape_source_pairing(source,state_direction,phase_rate_direction):
    """Apply BOTH full weak covectors to a supplied actual variation."""
    x=np.asarray(state_direction,complex);xt=np.asarray(phase_rate_direction,complex)
    if x.shape!=xt.shape or x.shape[0]!=len(source['full_weak_state_source']):
        raise ValueError('state AND phase-rate variation required; absent rate is not zero')
    return source['full_weak_state_source']@x+source['full_weak_phase_rate_source']@xt
