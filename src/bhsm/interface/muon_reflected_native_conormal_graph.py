"""Strong conormal graph of the EXISTING reflected geometric-L2 form.

For A=b*d_s+C and q[u,v]=integral (Au)^dagger G (Av) ds, G is the
positive Hermitian matrix density on the declared REAL parameter graph.
It excludes an independently applied numerical quadrature weight.  C is
unrestricted: no anti-Hermitian temporal-connection assumption is needed.
The canonical conormal is p=conj(b)*G*A u, not A u alone.

All b,G,C,z inputs carry explicit (value,x,y,xy) derivatives for REAL x,y.
Conjugating every jet is correct only for these real parameter derivatives;
this module does not conjugate independent holomorphic source axes or turn
an analytic action dual into a Hilbert adjoint.  No new contour, pairing,
physical endpoint/domain, field background or outgoing state is selected.
"""
from __future__ import annotations

import numpy as np


JET_ORDER = ('value', 'x', 'y', 'xy')
FORM_OWNER = 'muon_transported_native_pairing.transported_native_quadrature'
REAL_FACTOR_OWNER = 'muon_owned_native_product_connection.owned_native_product_node'


def _jet(value, name, shape):
    if value is None:
        raise ValueError(f'complete explicit {name} jets required, including owned zeros')
    a = np.asarray(value, complex)
    if a.shape != (4,) + shape or not np.isfinite(a).all():
        raise ValueError(f'{name} needs finite shape {(4,) + shape}: {JET_ORDER}')
    return a


def _mul(a, b):
    return np.stack((a[0]@b[0], a[1]@b[0]+a[0]@b[1],
        a[2]@b[0]+a[0]@b[2],
        a[3]@b[0]+a[1]@b[2]+a[2]@b[1]+a[0]@b[3]))


def _dagger(a):
    return a.conj().swapaxes(-1,-2)


def _solve(a, rhs):
    """Differentiate a X=rhs, retaining both ordered mixed contacts."""
    x0 = np.linalg.solve(a[0], rhs[0])
    xx = np.linalg.solve(a[0], rhs[1]-a[1]@x0)
    xy = np.linalg.solve(a[0], rhs[2]-a[2]@x0)
    xxy = np.linalg.solve(a[0], rhs[3]-a[3]@x0-a[1]@xy-a[2]@xx)
    return np.stack((x0,xx,xy,xxy))


def reflected_native_conormal_graph_jets(*, b_jet, density_jet, body_jet,
                                         spectral_parameter_jet):
    """Construct the exact strong graph and supplied real mixed derivatives.

    P=A*_G A has eigen-equation P u=z u.  For Y=(u,p),

      u'=-C*u/b + (|b|^2 G)^(-1) p,
      p'=-z*G*u + C^dagger*p/conj(b).

    The canonical state absorbs the derivative of the density and clock;
    it does not delete it.  The expanded formal adjoint is
      A*_G=-conj(b)*d_s+G^-1 C^dagger G-G^-1 (conj(b)*G)'.
    It is valid on the form's already-supplied domain.  A global closure,
    OS/contour identification and physical exterior are not inferred.
    """
    raw = np.asarray(density_jet) if density_jet is not None else np.array([])
    if raw.ndim != 3 or raw.shape[0] != 4 or raw.shape[1] != raw.shape[2] or raw.shape[1] == 0:
        raise ValueError('complete density jets need (4,fiber,fiber)')
    n=raw.shape[1]
    G=_jet(density_jet,'positive matrix density',(n,n))
    C=_jet(body_jet,'factor body',(n,n))
    b=_jet(b_jet,'complex principal scalar',())
    z=_jet(spectral_parameter_jet,'spectral parameter',())
    if b[0] == 0:
        raise ValueError('nonzero complex principal scalar required')
    if not np.allclose(G,_dagger(G),atol=1e-12,rtol=1e-12):
        raise ValueError('density and all real source jets must be Hermitian')
    try:
        np.linalg.cholesky(G[0])
    except np.linalg.LinAlgError as error:
        raise ValueError('positive definite base density required') from error
    I=np.eye(n,dtype=complex)
    ident=np.zeros((4,n,n),complex);ident[0]=I
    bj=b[:,None,None]*I
    barbj=bj.conj()
    principal=_mul(_mul(barbj,bj),G)
    block00=-_solve(bj,C)
    block01=_solve(principal,ident)
    block10=-_mul(z[:,None,None]*I,G)
    block11=_solve(barbj,_dagger(C))
    generator=np.concatenate((np.concatenate((block00,block01),axis=2),
                              np.concatenate((block10,block11),axis=2)),axis=1)
    J=np.block([[np.zeros((n,n)),I],[-I,np.zeros((n,n))]])
    Jjet=np.zeros_like(generator);Jjet[0]=J
    current=_mul(_dagger(generator),Jjet)+_mul(Jjet,generator)
    target=np.zeros_like(generator)
    target[:,:n,:n]=_mul((z.conj()-z)[:,None,None]*I,G)
    if not np.isfinite(generator).all():
        raise ValueError('strong graph exceeds numerical range')
    return dict(jet_order=JET_ORDER,canonical_generator_jet=generator,
        positive_form_principal_density_jet=principal,
        inverse_principal_density_jet=block01,
        canonical_green_matrix=J,
        current_identity_jet=current,current_identity_target_jet=target,
        current_identity_defect_jet=current-target,
        factor='A=b*d_s+C on the already declared real parameter form domain',
        formal_adjoint='A*_G=-conj(b)*d_s+G^-1 C^dagger G-G^-1 d_s(conj(b)*G)',
        canonical_conormal='p=conj(b)*G*(b*u_prime+C*u)',
        strong_graph='Y_prime=H_z Y, Y=(u,p), P=A*_G A, P u=z u',
        green_identity='integral (Au)^dagger G Av-u^dagger G P v=[u^dagger p_v]',
        current_identity='d_s(Y1^dagger J Y2)=(conj(z1)-z2)*u1^dagger G u2 on graph solutions',
        moving_pairing_clock_contacts_retained_in_conormal=True,
        antiHermitian_temporal_connection_assumed=False,
        source_parameter_scope='real x,y,xy; independent analytic source duals are not replaced',
        new_contour_or_domain_selected=False,physical_native_binding_completed=False,
        physical_outgoing_solution_evaluated=False,physical_energy_or_field_derivative_passed=False,
        coupled_corrections=0,physical_spin_normalization=None,physical_muon_magnetic_moment=None)
