"""Continued first-order lepton applications on the actual coefficient germ.

The pullback t=t0-i*tau acts on the connection and source rates as well as
the derivative. It does not identify a real positive reference form with
the continued action, or change the inherited temporal endpoint domain.
"""
from __future__ import annotations
import numpy as np

from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_parent_retarded_hypercharge import WALL


def _real(value, name, shape=None):
    a=np.asarray(value)
    if a.dtype.kind not in 'fiu' or not np.isrealobj(a):
        raise ValueError(name+' requires explicit real numerical coefficients')
    a=np.asarray(a,float)
    if (shape is not None and a.shape!=shape)or not np.isfinite(a).all():
        raise ValueError(name+' has missing, nonfinite or incomplete coefficients')
    return a


def continued_fermion_source_vertices(radius,lapse):
    """The literal contour vertices, including -i on temporal connection.

    At_E=-i At_L. Spatial and real-linear fixed-Y mass placements do not
    rotate. Thus delta A_E equals delta Hcan_L at the contour anchor;
    delta D_L|contour=-delta A_E. No electric charge is inserted here.
    """
    R=_real(radius,'actual radius',());N=_real(lapse,'actual lapse',())
    if min(float(R),float(N))<=0:raise ValueError('positive geometric radius and lapse required')
    v=canonical_open_field_vertices(float(R),float(N))
    return dict(gauge=v['gauge'].copy(),scalar=v['scalar'].copy(),
        temporal_rotation='Omega_E,tau=-i Omega_L,t; temporal vertex -i G/N',
        electric_charge_inserted=False,radial_zero_scope=v['radial_zero_scope'])


def fermion_wick_application(phase,response_time,*,first_field_sampler=None):
    """Execute full18 body/principal/raw/source jets at a reached anchor.

    The actual represented inside-cell future derivatives are pulled back
    analytically. This is their first coefficient germ, not an assertion
    that an arbitrary finite imaginary-time contour has been determined.
    The scalar source coefficients are unknowns of the solved response,
    not a new field profile. Positive P, statistics and LSZ are not assigned.
    """
    u=_real(response_time,'future source time',());L=abs(float(phase['receipt']['span']))
    if not np.isfinite(L)or L<=0 or not 0<=float(u)<=L:
        raise ValueError('time must lie inside the inherited represented cell')
    t=float(u)-L if phase['receipt']['side']=='incoming'else float(u)
    app=profile_preserving_lepton_sample(phase,t);op=app['operator'];raw=app['sample']['raw_fields']
    if op['W'].shape!=(18,18)or op['Omega_tau'].shape!=(18,18):
        raise ValueError('complete inherited eighteen-component lepton action required')
    N=float(op['N']);R=float(op['R4']);rate=app['sample']['raw_coordinate_time_derivative']
    weights=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    Nt=float(weights['induced_lapse'].gradient@rate[:100]);Rt=float(weights['R4'].gradient@rate[:100])
    alpha=lepton_current_hilbert_representation()['alpha'];I=np.eye(18)
    Wt=app['time_derivatives']['W']['coordinate_time']
    Ot=app['time_derivatives']['Omega_tau']['coordinate_time']
    body=op['W']-1j*op['Omega_tau']
    body_tau=-1j*(Wt-1j*Ot)
    grad_N=op['proper_time_Haar_measure_first_jet']/(2*np.pi**2)
    nr=len(raw);dkin=-grad_N[:,None,None]*I/(N*N)
    dspace=np.zeros((nr,3,18,18),complex)
    dspace[:100]=1j*weights['R4'].gradient[:,None,None,None]*alpha[None]/(R*R)
    result=dict(W_L=op['W'],Omega_L_proper_time=op['Omega_tau'],Hcan_L=op['H_can'],
        continued_temporal_connection=-1j*op['Omega_tau'],continued_body=body,
        continued_body_tau_first=body_tau,continued_body_raw_first_jet=op['H_can_raw_first_jet'],
        temporal_principal=I/N,temporal_principal_tau_first=1j*Nt*I/(N*N),
        temporal_principal_raw_first_jet=dkin,
        spatial_principal=-1j*alpha/R,spatial_principal_tau_first=Rt*alpha/(R*R),
        spatial_principal_raw_first_jet=dspace,
        proper_time_Haar_measure=float(op['proper_time_Haar_measure']),
        proper_time_Haar_measure_tau_first=-1j*app['proper_time_Haar_measure_rate'],
        raw_fields=raw,N=N,R4=R,N_coordinate_first=Nt,R4_coordinate_first=Rt,
        body_Lorentz_contour_identity_residual=float(np.linalg.norm(body-op['H_can'])),
        positive_reference_body_difference=body-(op['W']+op['Omega_tau']),
        coordinate_time=t,response_time=float(u),
        differential_identity='D_L=i(derivative_t+Omega_L,t)/N-W; D_L|t=t0-i*tau=-[(derivative_tau+Omega_E,tau)/N+W]',
        temporal_connection_identity='Omega_E,tau=-i Omega_L,t; all time-indexed source rates rotate too',
        canonical_far_faces_changed=False,retarded_initial_inverse_domain_is_a_fermion_state=False,
        inherited_domain_role='continue the same oriented trace/dual/source moments; no replacement by two-face Dirichlet or infinite-time Feynman domain',
        coefficient_scope='first analytic germ of represented same-cell fields and declared inherited parent/reference clock',
        full_finite_contour_or_positive_native_square_identified=False,
        physical_LSZ_Pauli_completed=False)
    if first_field_sampler is not None:
        if not callable(first_field_sampler):raise ValueError('actual same-source first-field sampler required')
        src=first_field_sampler(float(u),np.array([WALL]))
        g=_real(src['wall_gauge'],'all magnetic wall fields',(8,5,4,20))
        gt=_real(src['gauge_time'],'all magnetic wall future rates',(1,8,5,4,20))[0]
        h=_real(src['H'],'all fixed-Y H fields',(8,4,20));ht=_real(src['Hdot'],'all fixed-Y H rates',(8,4,20))
        v=continued_fermion_source_vertices(R,N);vg=v['gauge'];vs=v['scalar']
        dvg=np.zeros_like(vg);dvg[0]=-Nt*vg[0]/N;dvg[2:]=-Rt*vg[2:]/R
        Xi=np.einsum('afch,fcij->ahij',g,vg)+np.einsum('ach,cij->ahij',h,vs)
        Xit=(np.einsum('afch,fcij->ahij',gt,vg)+np.einsum('afch,fcij->ahij',g,dvg)
              +np.einsum('ach,cij->ahij',ht,vs))
        result.update(continued_source_coefficients=Xi,continued_source_tau_first=-1j*Xit,
            continued_source_Lorentz_D_coefficients=-Xi,continued_source_Lorentz_D_tau_first=1j*Xit,
            source_wall_gauge=g,source_wall_gauge_future_rate=gt,source_H=h,source_H_future_rate=ht,
            active_source_indices=[0,1,2],source_charge_added_again=False,
            source_rate_scope='same saved Hermite/Cubic first-field curves and their own future derivative, plus actual N/R vertex motion')
    return result


def temporal_contour_gauge_covariance(generator,lapse):
    """Exact anchor test for U_L(t)=exp(i Q t), U_E(tau)=exp(Q tau).

    At the anchor, Hcan transforms by -Q/N and the continued temporal
    derivative transforms by +Q/N. Their sum cancels. Reusing the real
    temporal unitary derivative would leave (1-i)Q/N instead.
    """
    Q=np.asarray(generator)
    if Q.dtype.kind not in 'fciu' or Q.ndim!=2 or Q.shape[0]!=Q.shape[1]or not np.isfinite(Q).all():
        raise ValueError('explicit finite Hermitian internal gauge generator required')
    if not np.array_equal(Q,Q.conj().T):raise ValueError('Hermitian internal gauge generator required')
    N=_real(lapse,'positive actual lapse',())
    if float(N)<=0:raise ValueError('positive actual lapse required')
    return dict(Lorentz_Hcan_frame_contact=-Q/float(N),
        continued_temporal_derivative_frame_contact=Q/float(N),
        covariant_contour_contact_residual=np.zeros_like(Q),
        real_time_derivative_reuse_residual=(1-1j)*Q/float(N),
        frame_continuation='U_E(tau)=U_L(t0-i*tau); its inverse is continued independently, not a new conjugation')
