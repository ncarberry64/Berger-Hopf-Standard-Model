"""Conditional, local quasi-static response of the frozen R1 cubic EFT.

This is the independent T scalar already present in the R1 action. It is not
the constant S6 target phase and is not a completed fundamental BHSM closure.
The body is the same prescribed finite density excess as the prior control.
H0=Mpl=1 background units are converted to Mpc before optical projection.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

import action_native_matter_n2 as an
import background as bg
from strong_lensing_comparison import ARCSEC, C_KM_S, lens_application
from strong_lensing_local_family import TolmanVIILens


@dataclass(frozen=True)
class R1Coefficients:
    z_l: float
    H0_km_s_Mpc: float
    H_over_H0: float
    Tdot_over_MplH0: float
    Tddot_over_MplH02: float
    lambda_over_MplH02: float
    b: float
    C: float

    @classmethod
    def frozen(cls, z_l=.3, H0_km_s_Mpc=67.4):
        background = an.frozen_background()
        N = -np.log1p(z_l)
        y = background.sol(N)
        v, H = float(y[1]), float(y[2])
        d = H*float(bg.rhs(N, y)[1])
        lam = bg.LAMBDA
        b = 2*v*v/lam
        C = 1+4*(d+2*H*v)/lam-2*v**4/lam**2
        if C <= 0 or lam <= 0:
            raise ValueError('the admitted regular screened branch requires C,lambda>0')
        return cls(z_l,H0_km_s_Mpc,H,v,d,lam,b,C)

    @property
    def hubble_length_Mpc(self):
        return C_KM_S/self.H0_km_s_Mpc

    @property
    def unscreened_extra(self):
        return self.b**2/(2*self.C)


class R1ScreenedLens:
    """Projected Weyl potential, with its potential/gradient/Hessian consistent.

    Phi=Psi to the retained local QS order. For r physical and m=GM/c^2,
    F(r)=delta Phi'/Phi_N'=2*F_inf/[1+sqrt(1+rV^3 mu(r)/r^3)].
    delta alpha(b)=4m/b integral_0^(pi/2) mu(b sec t)F(b sec t)cos(t)dt.
    The projected potential is the integral of this deflection from R to b.
    """
    def __init__(self, base=None, coefficients=None, *, quadrature_rtol=2e-10):
        self.base = base or TolmanVIILens()
        self.coefficients = coefficients or R1Coefficients.frozen()
        self.mass_Msun = self.base.mass_Msun
        self.radius_Mpc = self.base.radius_Mpc
        self.centre_Mpc = self.base.centre_Mpc
        self.mass_length_Mpc = self.base.mass_length_Mpc
        self.b = self.base.b  # inherited angular search scale, not scalar mixing
        self.quadrature_rtol = quadrature_rtol
        c = self.coefficients
        self.rV3_Mpc3 = 16*c.b*self.mass_length_Mpc*c.hubble_length_Mpc**2/(c.lambda_over_MplH02*c.C**2)
        self.rV_Mpc = self.rV3_Mpc3**(1/3)

    def mass_and_slope(self, r):
        x = r/self.radius_Mpc
        if x >= 1:
            return 1.,0.,1/r**3
        return x**3*(2.5-1.5*x*x), (7.5-7.5*x*x)/(2.5-1.5*x*x), (2.5-1.5*x*x)/self.radius_Mpc**3

    def extra_force(self, r):
        _,_,mu_over_r3 = self.mass_and_slope(float(r))
        return 2*self.coefficients.unscreened_extra/(1+math.sqrt(1+self.rV3_Mpc3*mu_over_r3))

    def scalar_gradient_natural(self, radius_Mpc):
        """d(delta T/Mpl)/d(r H0/c), finite at the centre."""
        r = float(radius_Mpc)
        if r == 0:
            return 0.
        c = self.coefficients
        x = r/c.hubble_length_Mpc
        mn = self.mass_length_Mpc/c.hubble_length_Mpc
        mu,_,mr3 = self.mass_and_slope(r)
        root = c.C*math.sqrt(1+self.rV3_Mpc3*mr3)
        return -2*c.b*mn*mu/(x*x*(c.C+root))

    def _theta_integrand(self, theta, impact, derivative):
        cost = math.cos(theta)
        if cost <= 0:
            return 0.
        r = impact/cost
        mu,slope,mr3 = self.mass_and_slope(r)
        root = math.sqrt(1+self.rV3_Mpc3*mr3)
        F = 2*self.coefficients.unscreened_extra/(1+root)
        L = mu*F
        if derivative:
            logarithmic_slope = .5*((1+1/root)*slope+3*(1-1/root))
            L *= logarithmic_slope-1
        return L*cost

    def _integral(self, impact, derivative=False, radius_cut=None):
        upper = math.pi/2 if radius_cut is None else math.acos(impact/radius_cut)
        points = [math.acos(impact/r) for r in (self.radius_Mpc,self.rV_Mpc)
                  if r > impact and (radius_cut is None or r < radius_cut)]
        return quad(lambda t:self._theta_integrand(t,impact,derivative),0,upper,
                    points=points,epsabs=2e-15,epsrel=self.quadrature_rtol,limit=180)[0]

    @lru_cache(maxsize=8192)
    def extra_alpha(self, impact):
        impact = float(impact)
        if impact == 0:
            return 0.
        return 4*self.mass_length_Mpc/impact*self._integral(impact)

    def extra_alpha_prime(self, impact):
        if impact <= 0:
            raise ValueError('use the finite centre limit explicitly')
        return 4*self.mass_length_Mpc/impact**2*self._integral(impact,True)

    @lru_cache(maxsize=8192)
    def extra_potential(self, impact):
        """Potential at R is zero; all delay differences are invariant to it."""
        return quad(self.extra_alpha,self.radius_Mpc,float(impact),epsabs=1e-23,
                    epsrel=self.quadrature_rtol,limit=160)[0]

    def extra_application(self, x):
        v = np.asarray(x,float)-np.asarray(self.centre_Mpc)
        r = float(np.linalg.norm(v))
        if r == 0:
            def integrand(t):
                rr = self.radius_Mpc*math.exp(t)
                mu,_,_ = self.mass_and_slope(rr)
                return mu*self.extra_force(rr)/rr**2
            # Exponentially tiny end tails; this is used only at the centre.
            slope = 4*self.mass_length_Mpc*quad(integrand,-30,30,epsabs=1e-14,epsrel=1e-10)[0]
            return self.extra_potential(0.),np.zeros(2),slope*np.eye(2)
        unit = v/r
        a = self.extra_alpha(r)
        ap = self.extra_alpha_prime(r)
        h = a/r*np.eye(2)+(ap-a/r)*np.outer(unit,unit)
        return self.extra_potential(r),a*unit,h

    def application(self, x):
        p,a,h = self.base.application(x)
        dp,da,dh = self.extra_application(x)
        return p+dp,a+da,h+dh

    def intrinsic_extra(self, x):
        p,a,_ = self.extra_application(x)
        return p,a

    def checks(self, impacts):
        c = self.coefficients
        rr = np.geomspace(self.radius_Mpc*1e-6,100*self.rV_Mpc,181)
        flux=[]
        for r in rr:
            x = r/c.hubble_length_Mpc
            mu,_,_=self.mass_and_slope(r)
            p=self.scalar_gradient_natural(r)
            rhs=c.b*self.mass_length_Mpc/c.hubble_length_Mpc*mu
            flux.append(abs(c.C*x*x*p-4/c.lambda_over_MplH02*x*p*p+rhs)/rhs)
        derivative=[];potential=[];tails=[]
        for r in impacts:
            h=r*2e-4
            ap=(-self.extra_alpha(r+2*h)+8*self.extra_alpha(r+h)-8*self.extra_alpha(r-h)+self.extra_alpha(r-2*h))/(12*h)
            derivative.append(abs(ap-self.extra_alpha_prime(r))/max(abs(ap),1e-40))
            pp=(self.extra_potential(r+h)-self.extra_potential(r-h))/(2*h)
            potential.append(abs(pp-self.extra_alpha(r))/self.extra_alpha(r))
            tails.append({"impact_Mpc":float(r),"fraction_extra_alpha_beyond_20_Mpc":
                1-self._integral(r,radius_cut=20.)/self._integral(r)})
        return dict(max_integrated_scalar_equation_relative_residual=max(flux),
                    max_independent_alpha_derivative_relative_error=max(derivative),
                    max_independent_potential_derivative_relative_error=max(potential),
                    finite_matching_tail=tails)


def solve_axis_images(geometry, lens, source, baseline_images):
    """Re-solve the same three noncritical axial image branches."""
    if abs(source[1])>1e-20 or any(np.max(abs(g-g[0,0]*np.eye(2)))>1e-12
          for g in (geometry.D_ol,geometry.D_os,geometry.D_ls)):
        raise ValueError('this root helper is for the inherited axial preparation')
    dol=geometry.D_ol[0,0]; q=geometry.G[0,0]
    beta=source[0]/geometry.D_os[0,0]
    def residual(theta):
        r=abs(dol*theta)
        alpha=lens.base.application([dol*theta,0.])[1][0]+np.sign(theta)*lens.extra_alpha(r)
        return theta-beta-q*alpha
    images=[]
    for theta in np.asarray(baseline_images)[:,0]:
        width=.001*ARCSEC
        images.append([brentq(residual,theta-width,theta+width,xtol=2e-20,rtol=1e-14),0.])
    images=np.asarray(images)
    app=[lens_application(t,geometry,lens,source) for t in images]
    arrival=np.array([a['arrival_days'] for a in app])
    return dict(images_rad=images,images_arcsec=images/ARCSEC,arrival_days=arrival,
                relative_delays_days=arrival[1:]-arrival[0],
                max_lens_residual_rad=max(np.max(abs(a['residual'])) for a in app))
