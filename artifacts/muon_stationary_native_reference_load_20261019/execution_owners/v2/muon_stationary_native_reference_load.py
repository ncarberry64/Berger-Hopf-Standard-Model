"""A new stationary native fermion component, on the saved coupled iterate.

This is the entire right-body constant-angular18 block and whole-line
frequency density, not a state covariance or a complete stratified domain.
Analytic continuation keeps BOTH native factors; it never re-daggers the
complex source. The cutoff is an explicit numerical coordinate. Uncomputed
state/domain/other-sector/overlap terms remain operands in the caller.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm, expm_frechet
from scipy.special import exp1, erfc
from numpy.polynomial.legendre import leggauss

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_adopted_incoming_reference import static_field_maps, M
from .muon_parent_retarded_hypercharge import WALL
from .muon_coupled_reference_replacement import GEOMETRY_IDS, _geometry_fields
from .muon_native_dirac_hamiltonian import (
    lepton_current_hilbert_representation, fixed_y_higgs_hamiltonian,
    canonical_lepton_hamiltonian_maps,
)
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


THETA_SIZE = 22  # R,N_ind,At4,Ai12,Hreal4; Ar has no intrinsic vertex.
FREQUENCY_PANELS = (0., .02, .1, .5, 2., 8.)


def field_pullback(x, *, anchor=False):
    """Full two-jet of the material wall trace into the common151 chart.

    Independent profiles are on fixed material rho=WALL. Normal motion is
    in the original metric/connection jets, not a second Eulerian sampling
    of those same material profiles. Ambient N is NOT substituted for N_ind.
    The optional source-free anchor retains the same mechanical connection.
    It is a functional decomposition, not a vacuum or occupation rule.
    """
    x = np.asarray(x, float)
    raw = _geometry_fields(x)
    w = intrinsic_m4_weight_jet(12, raw[:37], raw[37:74], raw[74:98],
                              source_value=raw[98], source_rate=raw[99])
    # Full chart retains qdot/sdot endpoint partials even though the saved
    # stationary comparison has those ordinary rates equal to zero.
    def lift(j):
        g, h = np.zeros(189), np.zeros((189,189))
        g[:100] = j.gradient
        h[:100,:100] = j.hessian
        return Jet(j.value,g,h)
    p, _ = static_field_maps(np.array([WALL]), enrich_temporal=True)
    p = p[0].reshape(5,4,84)
    lam = lift(w['mechanical_connection_lambda'])
    entries = [lift(w['R4']), lift(w['induced_lapse'])]
    for f in (0,2,3,4):
        for c in range(4):
            g = np.zeros(189)
            if not anchor: g[100:184] = p[f,c]
            v = Jet.affine(float(p[f,c]@x[62:146]) if not anchor else 0.,g)
            if f >= 2: v = v + M[f-2,c]*(lam-1)
            entries.append(v)
    for k in range(4):
        g = np.zeros(189)
        if not anchor: g[184+k] = 1.
        entries.append(Jet.affine(float(x[146+k]) if not anchor else 0.,g))
    fullg = np.array([j.gradient for j in entries])
    fullh = np.array([j.hessian for j in entries])
    indices = np.r_[GEOMETRY_IDS,np.arange(100,189)]
    return dict(value=np.array([j.value for j in entries]),
        gradient=fullg[:,indices],hessian=fullh[:,indices][:,:,indices],
        full_gradient189=fullg,full_hessian189=fullh,
        ambient_lapse=float(w['fields']['N'].value),
        mechanical_lambda=float(lam.value), material_trace_map=p)


def factor_twojet(theta):
    """Native W,Omega and their complete ordinary theta two-jets."""
    t = np.asarray(theta,float)
    if t.shape != (THETA_SIZE,) or not np.isfinite(t).all() or min(t[:2]) <= 0:
        raise ValueError('positive radius/lapse and finite22 field coordinates required')
    v = [Jet.affine(a,np.eye(THETA_SIZE)[i]) for i,a in enumerate(t)]
    rep = lepton_current_hilbert_representation()
    generators = lepton_unit_trace_gauge_representation()['generators']
    hb = fixed_y_higgs_hamiltonian(np.array([[1.,0.],[0.,1.],[1j,0.],[0.,1j]]))
    def collect(terms):
        return tuple(sum((getattr(j,name)[(...,)+(None,)*2]*m
                          if name != 'value' else j.value*m for j,m in terms),
                         np.zeros(((THETA_SIZE,)*(0 if name=='value' else 1 if name=='gradient' else 2))+(18,18),complex))
                     for name in ('value','gradient','hessian'))
    terms = [(1.5/v[0],rep['gamma5'])]
    for a in range(3):
        for c in range(4):
            terms.append((v[6+4*a+c]/v[0],-1j*rep['alpha'][a]@generators[c]))
    terms.extend((v[18+k],hb[k]) for k in range(4))
    return dict(W=collect(terms),Omega=collect([(v[2+c]/v[1],generators[c]) for c in range(4)]))


def native_pencil(factors, omega, *, z=-1j):
    """P_z=(W-zOmega-iw)(W+zOmega+iw), with analytic sharp fixed.

    At z=1 this is the original native A^dagger A. At z=-i it is
    its analytic source continuation, generally NOT a Hermitian square.
    All second contacts and both orders of the first vertices are kept.
    """
    w,wg,wh = factors['W']; o,og,oh = factors['Omega']
    l,r = w-z*o-1j*omega*np.eye(18), w+z*o+1j*omega*np.eye(18)
    lg,rg = wg-z*og,wg+z*og
    lh,rh = wh-z*oh,wh+z*oh
    p = l@r
    pg = lg@r+l@rg
    ph = lh@r+l@rh+np.einsum('iab,jbc->ijac',lg,rg)+np.einsum('jab,ibc->ijac',lg,rg)
    return p,pg,ph


def continuation_margin(factors):
    """Conservative finite-input all-frequency/all-unit-disk bound.

    Re P_z >= .5 omega^2 + delta, |z|<=1. Norms are Frobenius
    upper bounds; 1/||W^-1||_F is a lower bound for min singular W.
    Floating point evaluation is not an outward-rounded proof.
    """
    w,o = factors['W'][0],factors['Omega'][0]
    lower = 1/np.linalg.norm(np.linalg.solve(w,np.eye(18)))
    b = np.linalg.norm(o)
    comm = np.linalg.norm(w@(-1j*o)-(-1j*o)@w)
    delta = lower**2-3*b*b-comm
    if delta <= 0: raise ArithmeticError('continuation not justified by accretivity bound')
    return dict(W_gap_lower=float(lower),Omega_Frobenius=float(b),
        commutator_Frobenius=float(comm),uniform_delta=float(delta),
        endpoint_delta=float(lower**2-b*b),
        W_Hermiticity=float(np.max(abs(w-w.conj().T))),
        Omega_antiHermiticity=float(np.max(abs(o+o.conj().T))))


def heat_trace_twojet(factors, omega, cutoff):
    """Trace E1(cP)/2 two-jet, with c as an independent23rd coordinate.

    D exp is a matrix Frechet derivative, so changes of spectral weights
    are retained alongside the vertex/contact derivatives. No eigenvector
    derivative, occupation assignment or commuting approximation is used.
    """
    c = float(cutoff)
    if not np.isfinite(c) or c <= 0: raise ValueError('explicit positive numerical cutoff required')
    p,pg,ph = native_pencil(factors,omega)
    ev = np.linalg.eigvals(p)
    if np.min(ev.real) <= 0: raise ArithmeticError('positive-real analytic branch lost')
    e = expm(-c*p)
    gp = -np.linalg.solve(p,e)
    value = .5*np.sum(exp1(c*ev))
    gradient = np.zeros(23,complex); hessian = np.zeros((23,23),complex)
    gradient[:22] = .5*np.einsum('ab,iba->i',gp,pg)
    gradient[22] = -.5*np.trace(e)/c
    for j in range(22):
        de = expm_frechet(-c*p,-c*pg[j],compute_expm=False)
        dg = -np.linalg.solve(p,pg[j]@gp+de)
        hessian[:22,j] = .5*(np.einsum('ab,iba->i',dg,pg)+np.einsum('ab,iba->i',gp,ph[:,j]))
    hessian[:22,22] = .5*np.einsum('ab,iba->i',e,pg)
    hessian[22,:22] = hessian[:22,22]
    hessian[22,22] = .5*np.trace(e@(p/c+np.eye(18)/(c*c)))
    return value,gradient,hessian


def stationary_heat_twojet(theta, *, cutoff, points_per_panel=24):
    """Fresh native whole-frequency integral on a declared stationary core.

    H^1(R_proper) tensor the full18 constant-angular subspace. A trace
    density per unit proper duration is computed, not an event-domain
    determinant. Pairing +/- frequencies is analytic trace conjugacy;
    the integrand at +omega alone need not be real.
    """
    factors = factor_twojet(theta)
    margin = continuation_margin(factors)
    n = int(points_per_panel)
    if n < 8 or n != points_per_panel: raise ValueError('at least8 panel points required')
    nodes,weights = leggauss(n)
    value,gradient,hessian = 0.,np.zeros(23),np.zeros((23,23))
    imag_integral = 0.
    for lo,hi in zip(FREQUENCY_PANELS[:-1],FREQUENCY_PANELS[1:]):
        for node,weight in zip(nodes,weights):
            omega = lo+(node+1)*(hi-lo)/2
            v,g,h = heat_trace_twojet(factors,omega,cutoff)
            weight = weight*(hi-lo)/(2*np.pi)  # +/- pairing; fermion1/2 is already inside.
            value += weight*v.real;gradient += weight*g.real;hessian += weight*h.real
            imag_integral += weight*v.imag
    # integral dω/(2π), paired = integral_0∞ dω/π; previous weight had
    # panel Jacobian /π exactly: (hi-lo)/(2π).
    c=float(cutoff); end=FREQUENCY_PANELS[-1];delta=margin['endpoint_delta']
    # At the endpoint Re P=omega²+W²-(-iOmega)². Uniform in omega,
    # not a sampled-tail estimate. The bounds also cover derivatives.
    i0=.5*np.sqrt(np.pi/c)*erfc(np.sqrt(c)*end)
    i1=np.exp(-c*end*end)/(2*c)
    i2=end*i1+i0/(2*c)
    w,wg,wh=factors['W'];o,og,oh=factors['Omega']
    a=1+(np.linalg.norm(w)+np.linalg.norm(o))/end
    d=max(np.linalg.norm(wg[k])+np.linalg.norm(og[k]) for k in range(22))
    dd=max(np.linalg.norm(wh[k,l])+np.linalg.norm(oh[k,l]) for k in range(22) for l in range(22))
    scale=18*np.exp(-c*delta)/np.pi
    tail=.5*scale*i0/(c*end*end)
    gt=max(scale*a*d*i0/end,.5*scale*i0/c)
    ht=max(.5*scale*((4*a*a*(c+1/end**2)+2/end**2)*d*d+2*a*dd/end)*i0,
           scale*a*d*i1,.5*scale*(a*a*i2/c+i0/c**2))
    return dict(value=float(value),gradient=gradient,hessian=hessian,
        unsymmetrized_hessian_defect=float(np.max(abs(hessian-hessian.T))),
        positive_frequency_imaginary_density=float(imag_integral),
        value_tail_upper_bound_finite_input=float(tail),continuation=margin,
        theta23_gradient_tail_entry_bound=float(gt),theta23_hessian_tail_entry_bound=float(ht),
        cutoff=c,points_per_panel=n)


def lorentz_load(x, *, cutoff, points_per_panel=24, anchor=False):
    """-N_ind Gamma_E: complete common151 two-jet at fixed cutoff.

    Also return cutoff load and mixed derivative. Dc,D2c and changing
    domain/phase are additional physical chain terms, not set to zero.
    """
    pull = field_pullback(x,anchor=anchor)
    heat = stationary_heat_twojet(pull['value'],cutoff=cutoff,points_per_panel=points_per_panel)
    j,k = pull['full_gradient189'],pull['full_hessian189']
    gv,hv = heat['gradient'][:22],heat['hessian'][:22,:22]
    g = j.T@gv
    h = j.T@hv@j+np.einsum('i,ijk->jk',gv,k)
    lapse,ng,nh = pull['value'][1],j[1],k[1]
    v = heat['value']
    outg = -lapse*g-v*ng
    outh = -lapse*h-v*nh-np.outer(ng,g)-np.outer(g,ng)
    gc = heat['gradient'][22]
    indices = np.r_[GEOMETRY_IDS,np.arange(100,189)]
    mixed = -lapse*(j.T@heat['hessian'][:22,22])-ng*gc
    # Propagate the finite-input Gaussian tail bounds to the full chart.
    gt=np.sqrt(22)*heat['theta23_gradient_tail_entry_bound']
    ht=22*heat['theta23_hessian_tail_entry_bound']
    vt=heat['value_tail_upper_bound_finite_input']
    jnorm=np.linalg.norm(j);knorm=np.linalg.norm(k)
    tail_g=lapse*jnorm*gt+np.linalg.norm(ng)*vt
    tail_h=(lapse*(jnorm**2*ht+knorm*gt)+np.linalg.norm(nh)*vt
            +2*np.linalg.norm(ng)*jnorm*gt)
    lg=-lapse*heat['gradient'][:22].copy();lg[1]-=v
    wall=np.r_[lg[2:6],np.zeros(4),lg[6:18],lg[18:22]]
    return dict(value=float(-lapse*v),gradient=outg[indices],hessian=outh[np.ix_(indices,indices)],
        full_gradient189=outg,full_hessian189=outh,
        local_theta_Lorentz_covector22=lg,local_wall_Higgs_covector24=wall,
        full189_gradient_frequency_tail_norm_bound=float(tail_g),
        full189_Hessian_frequency_tail_norm_bound=float(tail_h),
        cutoff_gradient=float(-lapse*gc),
        field_cutoff_mixed=mixed[indices],full_field_cutoff_mixed189=mixed,
        cutoff_hessian=float(-lapse*heat['hessian'][22,22]),
        theta=pull['value'],theta_gradient=pull['gradient'],theta_hessian=pull['hessian'],heat=heat,
        ambient_lapse=pull['ambient_lapse'],induced_lapse=float(lapse),
        mechanical_lambda=pull['mechanical_lambda'])


def original_operator_checks(theta, *, cutoff):
    """Original-factor, contour, frequency-reality and global Ward checks."""
    f=factor_twojet(theta);w,o=f['W'][0],f['Omega'][0]
    om=.137;eye=np.eye(18);a=w+o+1j*om*eye
    p1,_,_=native_pencil(f,om,z=1.)
    p,pg,_=native_pencil(f,om)
    minus,_,_=heat_trace_twojet(f,-om,cutoff)
    plus,_,_=heat_trace_twojet(f,om,cutoff)
    b=-1j*o
    explicit=om*om*eye+w@w-b@b+w@b-b@w-2j*om*b
    e=expm(-cutoff*p);gp=-np.linalg.solve(p,e)
    ward=ward_derivative=comm_defect=0.
    for gen in lepton_unit_trace_gauge_representation()['generators']:
        dw,do=gen@w-w@gen,gen@o-o@gen
        l,r=w+1j*o-1j*om*eye,w-1j*o+1j*om*eye
        dp=(dw+1j*do)@r+l@(dw-1j*do)
        comm_defect=max(comm_defect,float(np.max(abs(dp-(gen@p-p@gen)))))
        ward=max(ward,float(abs(.5*np.trace(gp@dp))))
        de=expm_frechet(-cutoff*p,-cutoff*dp,compute_expm=False)
        dg=-np.linalg.solve(p,dp@gp+de)
        contact=gen@pg-pg@gen
        differentiated=.5*(np.einsum('ab,iba->i',dg,pg)+np.einsum('ab,iba->i',gp,contact))
        ward_derivative=max(ward_derivative,float(np.max(abs(differentiated))))
    generators=lepton_unit_trace_gauge_representation()['generators']
    temporal_defect=max(float(np.max(abs(f['Omega'][1][2+k]-generators[k]/theta[1]))) for k in range(4))
    conn=np.empty((1,4,18,18),complex);conn[0,0]=o
    conn[0,1:]=np.einsum('ac,cij->aij',theta[6:18].reshape(3,4),generators)
    ham=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1,3,18,18)),
        H=(theta[18:20]+1j*theta[20:22])[None],R4=theta[0],gauge_connection=conn)
    return dict(native_real_product_defect=float(np.max(abs(p1-a.conj().T@a))),
        original_Lorentz_Hamiltonian_coefficient_defect=float(np.max(abs(ham['hamiltonian_map'][0]-(w-1j*o)))),
        literal_continued_product_defect=float(np.max(abs(p-explicit))),
        native_temporal_vertex_defect=temporal_defect,
        paired_frequency_trace_defect=float(abs(minus-plus.conjugate())),
        global_gauge_pencil_covariance_defect=comm_defect,
        global_gauge_Ward_contraction=ward,
        differentiated_global_Ward_contraction=ward_derivative,
        wrong_redaggered_Hcan_square_difference=float(np.linalg.norm(p-(om*om*eye+(w-1j*o)@(w-1j*o)))))
