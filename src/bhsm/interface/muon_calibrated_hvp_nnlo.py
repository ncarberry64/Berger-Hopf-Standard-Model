"""Published NNLO HVP kernels evaluated against the same measured spectrum.

Balzani--Laporta--Passera arXiv:2112.05704v3 Eqs. (28)--(45), Tables 1--3.
The three-loop and different-line kernels have the stated series approximation
error; tau NNLO is neglected by that source. This is not a full native form.
"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.laguerre import laggauss
import sympy as sp

from .muon_calibrated_hvp_higher import (
    _positive, _row, nlo_photonic_kernel_log_endpoint, one_loop_lepton_delta_alpha,
)
from .muon_calibrated_hvp_spectral import delta_alpha_had_spacelike

COEFFICIENT_SHA256='5f9b09543d4875c3316d8c047322b41d1df69f7b6b348365e37f361619920f3b'
COEFFICIENT_PATH=Path(__file__).resolve().parents[3]/'artifacts/muon_calibrated_hvp_nnlo_20261010/input/coefficients.json'


def retained_nnlo_coefficients(mass_ratio, *, path=COEFFICIENT_PATH):
    """48 source rational/transcendental coefficients at the supplied m_e/m_mu.

    A hash-pinned exact expression table is used, not a fitted anomaly or
    rounded NNLO component. Coefficients are evaluated at 60 decimal digits
    before conversion to the numerical quadrature representation.
    """
    rho_value=_positive(mass_ratio,'m_e/m_mu')
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=COEFFICIENT_SHA256:
        raise ValueError('primary NNLO coefficient identity mismatch')
    source=json.loads(raw)
    rho=sp.Symbol('rho',positive=True)
    exact_rho=sp.Rational(str(rho_value))
    return {name:{family:np.array([float(sp.sympify(rows[family+str(i)]['expression'],
                       locals={'rho':rho}).evalf(60,subs={rho:exact_rho})) for i in range(4)])
                  for family in 'ghjp'} for name,rows in source['tables'].items()}


def _approximate_kernel(x,end,coefficients):
    threshold=(math.sqrt(5)-1)/2
    if x<threshold:
        xi=x*x/end
        return (2-x)/(x*end)*np.polynomial.polynomial.polyval(xi,coefficients['p'])
    xi=end/(x*x)
    log_xi=math.log(xi)
    L=(np.polynomial.polynomial.polyval(xi,coefficients['g'])
       +np.polynomial.polynomial.polyval(xi,coefficients['h'])*log_xi
       +np.polynomial.polynomial.polyval(xi,coefficients['j'])*log_xi*log_xi)
    return (2-x)/(x*x*x)*L


def _different_line_double_hvp(spectrum,a,m,*,order,spectral_order):
    """Eq.40--42, split at xi=xi' before quadrature.

    xi_large=t, xi_small=t*z cancels the kernel's 1/t against the triangular
    Jacobian. Then t=exp(-v), z=exp(-w) and Gauss--Laguerre quadrature
    treat both logarithmic endpoints on [0,infinity). Both variations of
    the same spectrum enter its gradient.
    """
    nodes,weights=laggauss(order)
    if not np.all(np.isfinite(nodes)) or 2*max(nodes)>math.log(np.finfo(float).max)-2*math.log(m):
        raise ValueError('double quadrature endpoint exceeds finite arithmetic; lower its numerical order')
    A=1855-188*math.pi**2;B=988*math.pi**2-9765;C=24*(435-44*math.pi**2)
    factor=(a/math.pi)**2/(2*(32*math.pi**2-315))
    value=0.;stat=systematic=None;undressing=0.
    for v,wt in zip(nodes,weights):
        left=delta_alpha_had_spacelike(spectrum,m*m*math.exp(v),a,order=spectral_order)
        hl=left['value'];sl=np.asarray(left['statistical_error_vector']);yl=np.asarray(left['systematic_error_vector'])
        if stat is None:
            stat=np.zeros_like(sl);systematic=np.zeros_like(yl)
        for vprime,wz in zip(nodes,weights):
            z=math.exp(-vprime)
            right=delta_alpha_had_spacelike(spectrum,m*m*math.exp(v+vprime),a,order=spectral_order)
            hr=right['value'];w=factor*wt*wz*(A*z+B*z*z+C*z*z*z)
            value+=w*hl*hr
            stat+=w*(hr*sl+hl*np.asarray(right['statistical_error_vector']))
            systematic+=w*(hr*yl+hl*np.asarray(right['systematic_error_vector']))
            undressing+=abs(w)*(abs(hr)*left['undressing_error_estimate']+abs(hl)*right['undressing_error_estimate'])
    return _row(value,stat,systematic,undressing)


def next_to_next_to_leading_hvp_pauli(spectrum,alpha0,m_mu,m_e,*,order=32,
                                    spectral_order=12,double_order=24,endpoint_v=32.):
    """Compute all standard source NNLO classes, keeping approximation scope.

    6a/6b/6bll and 6c2 use the published approximating kernels. 6c1,6c3,
    6c4,6d use exact kernels. No purely leptonic term or internal-HVP FSR
    is added. Source covariance is propagated to first order, with common
    rows summed coherently across all classes.
    """
    a=_positive(alpha0,'alpha0');m=_positive(m_mu,'muon pole mass');me=_positive(m_e,'electron pole mass')
    V=_positive(endpoint_v,'endpoint_v')
    if V<8 or V>48 or any(not isinstance(q,int) or q<4 for q in [order,spectral_order,double_order]):
        raise ValueError('endpoint_v in [8,48] and integer orders>=4 required')
    coefficients=retained_nnlo_coefficients(me/m)
    vmu=-math.log(1-(math.sqrt(5)-1)/2)
    edges=sorted(set([0.,vmu,1.,2.,4.,8.,16.,V]+([32.] if V>32 else [])))
    edges=[v for v in edges if v<=V]
    z,w=leggauss(order)
    names=['6a','6b','6bll','6c1','6c3','6c4','6d']
    values=np.zeros(7);stat=systematic=None;undressing=np.zeros(7)
    for lo,hi in zip(edges[:-1],edges[1:]):
        for v,weight in zip((lo+hi)/2+(hi-lo)/2*z,(hi-lo)/2*w):
            end=math.exp(-v);x=-math.expm1(-v);Q=m*m*x*x/end
            row=delta_alpha_had_spacelike(spectrum,Q,a,order=spectral_order)
            h=row['value'];electron=one_loop_lepton_delta_alpha(Q,me,a);muon=one_loop_lepton_delta_alpha(Q,m,a)
            k4=nlo_photonic_kernel_log_endpoint(float(v),decimal_precision=110)
            lam4=k4-2*math.pi/a*end*muon
            factors=np.array([(a/math.pi)**3*_approximate_kernel(x,end,coefficients[n])*end for n in names[:3]]+
                             [(a/math.pi)**2*lam4*end,3*a/math.pi*end*end*electron,
                              3*a/math.pi*end*end*muon,a/math.pi*end*end])*weight
            values+=factors*np.array([h,h,h,h*h,h*h,h*h,h**3])
            gradients=factors*np.array([1.,1.,1.,2*h,2*h,2*h,3*h*h])
            st=np.asarray(row['statistical_error_vector']);sy=np.asarray(row['systematic_error_vector'])
            if stat is None:
                stat=np.zeros((7,len(st)));systematic=np.zeros((7,len(sy)))
            stat+=gradients[:,None]*st;systematic+=gradients[:,None]*sy
            undressing+=np.abs(gradients)*row['undressing_error_estimate']
    classes={name:_row(values[i],stat[i],systematic[i],undressing[i]) for i,name in enumerate(names)}
    classes['6c2']=_different_line_double_hvp(spectrum,a,m,order=double_order,spectral_order=spectral_order)
    total=_row(sum(row['value'] for row in classes.values()),
               np.sum([row['statistical_error_vector'] for row in classes.values()],axis=0),
               np.sum([row['systematic_error_vector'] for row in classes.values()],axis=0),
               sum(row['undressing_error_estimate'] for row in classes.values()))
    return dict(NNLO_HVP=total,classes=classes,alpha0=a,m_mu_GeV=m,m_e_GeV=me,
                outer_order=order,spectral_order=spectral_order,double_order=double_order,endpoint_v=V,
                double_integral_method='min/max triangular split, t=exp(-v), z=exp(-w), Gauss-Laguerre endpoints',
                coefficient_sha256=COEFFICIENT_SHA256,kernel_source='https://arxiv.org/abs/2112.05704',
                kernel_equations='28-45; Tables1-3',
                kernel_approximation_error_estimate=4e-12,
                kernel_error_meaning='conservative sum of four published O(1e-12) approximation scales; not a rigorous bound',
                omitted_tau_NNLO_error_estimate=1e-12,
                tau_error_meaning='source footnote4 estimates below O(1e-12); not computed or promoted to exact zero',
                covariance_scope='first-order coherent shared spectral covariance; no full cross-experiment covariance supplied',
                overlap='6e internal HVP radiation belongs to NLO inclusive R; 6f/6g/6h to LO input; pureleptonic terms excluded',
                classification='CALIBRATED_MEASURED_TWO_CURRENT_NNLO_PROJECTION_WITH_PUBLISHED_KERNEL_APPROXIMATIONS',
                complete_native_remainder=False,measured_anomaly_used=False,SM_total_used=False,
                rigorous_quadrature_enclosure=False,action_selected=False,Gate7_closed=False)
