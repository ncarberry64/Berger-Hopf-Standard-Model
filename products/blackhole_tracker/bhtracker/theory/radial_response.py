"""Same-action screened compact-source exterior and worldtube response.

The scalar flux is supplied, not selected by a black-hole horizon solution.
The exact radial multipoles linearize the retained homogeneous-background,
weak-metric quasi-static cubic R1 action. Projection extends that local
profile along a thin lens; it is not a global static cosmological solution.

Units: x=r/(c/H0), p=d(delta T/Mpl)/dx. ``projected_quad`` returns the
phase integral in pc per unit scalar Dirichlet amplitude at r0, its first
derivative (dimensionless), and second derivative (pc^-1). The phase uses
Phi+Psi, with no second mass or arbitrary metric quadrupole added.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import importlib
from pathlib import Path
import sys

import numpy as np
from scipy.interpolate import BPoly
from scipy.special import gamma, hyp2f1, roots_legendre

ROOT = Path(__file__).resolve().parents[1]
VENDOR = Path(__file__).resolve().parent/'provider'
C_KM_S = 299792.458
G_PC_KMS2_MSUN = 1.3271244e20 / (3.085677581491367e16 * 1e6)  # IAU nominal GM_sun
N2 = np.sqrt(15/(16*np.pi))  # integral [N2 (nx^2-ny^2)]^2 dOmega = 1
N0 = np.sqrt(5/(16*np.pi))   # integral [N0 (3*nz^2-1)]^2 dOmega = 1
PINNED = {
    'code/action_native_matter_n2.py':'eee6ffc6f31d743cc36c31300c8a51c6a28cc50fbbb7526342b7f88978dfcb81',
    'code/background.py':'9bf7107e0e9f716a8176baed6ae638f887c3aabb295b580bf09d6c51364aae89',
    'code/closed_horndeski_n2.py':'0d7e596ae40bd01ba9331128afdda9d163e52c955096f70209f06975e197f36d',
    'preregistration/prediction_manifest.json':'afaf697100a70d43eab2a6086931bad5efe1ced02f9a56d422b709896be51113',
}


@lru_cache(maxsize=16)
def _background(z):
    for rel, expected in PINNED.items():
        if hashlib.sha256((VENDOR/rel).read_bytes()).hexdigest() != expected:
            raise ValueError(f'pinned R1 input changed: {rel}')
    sys.path.insert(0,str(VENDOR/'code'))
    an=importlib.import_module('action_native_matter_n2')
    bg=importlib.import_module('background')
    for module, rel in [(an,'code/action_native_matter_n2.py'),(bg,'code/background.py')]:
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()!=PINNED[rel]:
            raise ValueError(f'another incompatible {module.__name__} is already imported')
    N=-np.log1p(z)
    sol=an.frozen_background()
    T,v,H=map(float,sol.sol(N))
    d=float(H*bg.rhs(N,sol.sol(N))[1])
    lam=float(bg.LAMBDA)
    beta=2*v*v/lam
    A=1+4*(d+2*H*v)/lam
    C=A-beta*beta/2
    D=1+12*H*v/lam+6*v**4/lam**2
    return dict(T=T,v=v,H=H,d=d,lambda_hat=lam,beta_hat=beta,A=A,C=C,D=D)


@lru_cache(maxsize=32)
def _parameters(ell):
    a,b,c=(ell+1)/2,(ell+2)/6,(2*ell+4)/3
    dec=gamma(c)*gamma(a-b)/(gamma(a)*gamma(c-b))
    grow=gamma(c)*gamma(b-a)/(gamma(b)*gamma(c-a))
    return a,b,c,dec,grow


def _term(rho,power,a,b,c,k,coefficient=1.):
    """R,D R,D^2 R,(1+D)R,(D^2+D)R for rho^power H(t).

    D=rho*d/drho, t=-rho^k. Computing the last two combinations directly
    avoids catastrophic cancellation of the deep l=2 rho^-1 term.
    """
    t=-rho**k
    H=hyp2f1(a,b,c,t)
    Ht=a*b/c*hyp2f1(a+1,b+1,c+1,t)
    Htt=a*(a+1)*b*(b+1)/(c*(c+1))*hyp2f1(a+2,b+2,c+2,t)
    pref=coefficient*rho**power
    return np.array([
        pref*H,
        pref*(power*H+k*t*Ht),
        pref*(power**2*H+k*t*(2*power+k)*Ht+k*k*t*t*Htt),
        pref*((power+1)*H+k*t*Ht),
        pref*(power*(power+1)*H+k*t*(2*power+k+1)*Ht+k*k*t*t*Htt),
    ])


def _shape_components(rho,ell):
    arr=np.asarray(rho,dtype=float)
    flat=arr.reshape(-1)
    if np.any(~np.isfinite(flat)) or np.any(flat<=0):
        raise ValueError('positive finite radius required')
    a,b,c,dec,grow=_parameters(ell)
    out=np.empty((5,len(flat)))
    deep=flat<.3
    r=flat[deep]
    if len(r):
        out[:,deep]=(
            _term(r,-ell/2,b,1-c+b,1-a+b,3,dec)
            +_term(r,(ell+1)/2,a,1-c+a,1-b+a,3,grow))
    r=flat[~deep]
    if len(r):
        out[:,~deep]=_term(r,-ell-1,a,b,c,-3)
    return out.reshape((5,)+arr.shape)


@lru_cache(maxsize=16)
def _legendre(n):
    return roots_legendre(n)


class ScreenedExterior:
    """Conditional compact-source response outside a declared worldtube.

    ``flux_ratio`` scales Q relative to the regular-body value beta_hat*mhat.
    It is an open horizon/matching datum, not a fitted universal coupling.
    The metric monopole mass stays M. No homogeneous metric quadrupole is
    silently selected: projected_quad is the scalar-driven metric piece.
    """
    def __init__(self,M_msun=1e9,z_l=.3,H0=67.4,r0_pc=10.,flux_ratio=1.,
                 quadrature_rtol=2e-9):
        if not (M_msun>0 and r0_pc>0 and H0>0 and 0<=z_l<=2.1 and flux_ratio>=0):
            raise ValueError('require M,r0,H0>0, 0<=z_l<=2.1, flux_ratio>=0')
        if not np.all(np.isfinite([M_msun,z_l,H0,r0_pc,flux_ratio])):
            raise ValueError('finite physical inputs required')
        self.M_msun=float(M_msun);self.z_l=float(z_l);self.H0=float(H0)
        self.r0_pc=float(r0_pc);self.flux_ratio=float(flux_ratio)
        self.quadrature_rtol=float(quadrature_rtol)
        self.coefficients=dict(_background(self.z_l))
        for key,val in self.coefficients.items():
            setattr(self,key,val)
        if self.C<=0 or self.D<=0 or self.lambda_hat<=0:
            raise ValueError('positive C,D,lambda required by this exterior branch')
        self.L0_pc=C_KM_S/self.H0*1e6
        self.m_pc=G_PC_KMS2_MSUN*self.M_msun/C_KM_S**2
        self.mass_length_pc=self.m0physical=self.m_pc
        self.mhat=self.m_pc/self.L0_pc
        self.x0=self.r0_pc/self.L0_pc
        self.rV_pc=(16*self.flux_ratio*self.beta_hat*self.m_pc*self.L0_pc**2/
                    (self.lambda_hat*self.C**2))**(1/3)
        self.epsilon_infty=self.flux_ratio*self.beta_hat**2/(2*self.C)
        self._normalizations={}
        self._tables=None
        self.last_projection_errors={}

    def _radii(self,r):
        r=np.asarray(r,dtype=float)
        if np.any(~np.isfinite(r)) or np.any(r<self.r0_pc*(1-2e-14)):
            raise ValueError('radius enters unresolved interior worldtube')
        return r

    def p(self,x_dimless):
        """Formal exterior p=d(delta T/Mpl)/dx; physical use requires x>=x0."""
        x=np.asarray(x_dimless,dtype=float)
        if np.any(x<=0) or np.any(~np.isfinite(x)):
            raise ValueError('positive finite x required')
        charge=self.flux_ratio*self.beta_hat*self.mhat
        S=np.sqrt(self.C**2+16*charge/(self.lambda_hat*x**3))
        return -2*charge/(x*x*(self.C+S))

    def principal(self,r_pc):
        """Leading local scalar (Kr,Kangular,Ktime); no UV/horizon admission."""
        r=self._radii(r_pc)
        u=(self.rV_pc/r)**3
        S=self.C*np.sqrt(1+u)
        rSp=-1.5*self.C*u/np.sqrt(1+u)
        return S,S+rSp/2,self.D+1.5*(S-self.C)+rSp/2

    def _components(self,r,ell):
        if not isinstance(ell,(int,np.integer)) or ell<1:
            raise ValueError('ell must be an integer >=1')
        if self.rV_pc==0:
            f=(self.r0_pc/np.asarray(r))**(ell+1)
            s=-ell-1
            return np.array([f,s*f,s*s*f,(1+s)*f,s*(s+1)*f])
        if ell not in self._normalizations:
            self._normalizations[ell]=float(_shape_components(self.r0_pc/self.rV_pc,ell)[0])
        return _shape_components(np.asarray(r)/self.rV_pc,ell)/self._normalizations[ell]

    def radial(self,r_pc,l=2):
        """Exact decaying radial shape, with f_l(r0)=1."""
        return self._components(self._radii(r_pc),l)[0]

    def radial_derivatives(self,r_pc,l=2):
        """f,df/dr,d2f/dr2, in 1,pc^-1,pc^-2."""
        r=self._radii(r_pc)
        R,DR,DDR=self._components(r,l)[:3]
        return R,DR/r,(DDR-DR)/(r*r)

    def impedance(self,l=2):
        """Dimensionless-x conormal coefficient q_l/f0=-x0^2 Kr f_x(x0)."""
        DR=float(self._components(self.r0_pc,l)[1])
        Kr=float(self.principal(self.r0_pc)[0])
        return -self.x0*Kr*DR

    def _breaks(self,b):
        radii=self.rV_pc*np.array([.001,.01,.1,1.,10.,100.])
        return np.unique([0.,np.pi/2]+[np.arccos(b/r) for r in radii if r>b])

    def _integrate(self,b,kind,n):
        nodes,weights=_legendre(n)
        total=np.zeros(3)
        breaks=self._breaks(b)
        for lo,hi in zip(breaks[:-1],breaks[1:]):
            theta=(hi+lo)/2+(hi-lo)/2*nodes
            cost=np.cos(theta)
            r=b/cost
            if kind in ['quad','axial']:
                fields=self._components(r,2)[[0,3,4]]
                if kind=='axial':
                    fields=fields*(2/cost**2-3)
            else:
                u=(self.rV_pc/r)**3
                root=np.sqrt(1+u)
                F=2*self.epsilon_infty/(1+root)
                eta=1.5*(1-1/root)
                Deta=-2.25*u/root**3
                fields=np.array([F,F*(eta-1),F*((eta-1)*(eta-2)+Deta)])*cost
            total+=(hi-lo)/2*(fields@weights)
        if kind=='quad':
            return -2*self.beta_hat*N2*total*np.array([b,1.,1/b])
        if kind=='axial':
            return -2*self.beta_hat*N0*total*np.array([b,1.,1/b])
        return 4*self.m_pc*total*np.array([1/b,1/b**2,1/b**3])

    def _direct(self,b,kind):
        b=float(self._radii(b))
        old=self._integrate(b,kind,48)
        for n in [96,192,384]:
            val=self._integrate(b,kind,n)
            err=np.abs(val-old)
            scale=np.maximum(abs(val),abs(val[0])*np.array([1.,1/b,1/b**2])*2e-13)
            if np.all(err<=self.quadrature_rtol*scale+1e-28):
                break
            old=val
        self.last_projection_errors[kind]={'b_pc':b,'gauss_order':n,
            'absolute_refinement_difference':err.tolist(),
            'relative_target_met':bool(np.all(err<=self.quadrature_rtol*scale+1e-28)),
            'interval_certificate':False}
        return val

    def _application(self,b_pc,kind):
        b=self._radii(b_pc)
        if (self._tables is not None and kind in self._tables
                and np.all((b>=self._tables['lo'])&(b<=self._tables['hi']))):
            poly=self._tables[kind]
            t=np.log(b)
            y=poly(t)+self._tables[kind+'_offset'];d=poly.derivative()(t);dd=poly.derivative(2)(t)
            result=tuple(np.asarray(x) for x in (y,d/b,(dd-d)/b**2))
            return tuple(float(x) for x in result) if b.ndim==0 else result
        vals=np.array([self._direct(x,kind) for x in b.reshape(-1)])
        result=tuple(vals[:,j].reshape(b.shape) for j in range(3))
        return tuple(float(x) for x in result) if b.ndim==0 else result

    def projected_quad(self,b_pc):
        """q,q',q'' for phase=a*q(b)*cos(2phi), in pc,1,pc^-1.

        a is the supplied dimensionless scalar Dirichlet coefficient at r0.
        q=-beta*N2*int f(r)*b^2/r^2 dz_pc. All line points stay outside r0.
        """
        if self.rV_pc==0:
            b=self._radii(b_pc)
            q=-4*self.beta_hat*N2*self.r0_pc**3/(3*b*b)
            result=(q,-2*q/b,6*q/b**2)
            return tuple(float(x) for x in result) if b.ndim==0 else result
        return self._application(b_pc,'quad')

    def projected_axial(self,b_pc):
        """Axial Y20 phase q0,q0',q0'', in pc,1,pc^-1 per boundary a0.

        Y20=N0*(3*nz^2-1). The full line integral is
        q0=-beta*N0*int f(r)*(2-3*b^2/r^2) dz_pc. Its harmonic
        flux=0 limit vanishes identically, rather than selecting a mass.
        This supplied radial nuisance is distinct from central scalar flux.
        """
        if self.rV_pc==0:
            b=self._radii(b_pc)
            result=tuple(np.zeros_like(b) for _ in range(3))
            return tuple(float(x) for x in result) if b.ndim==0 else result
        return self._application(b_pc,'axial')

    def monopole_deflection(self,b_pc):
        """Extra scalar alpha,alpha',alpha'' in 1,pc^-1,pc^-2; mass not added.

        alpha=-beta*b/L0 * int p(r/L0)/r dz_pc, over both line halves.
        The ordinary Newtonian 4m/b belongs to the caller exactly once.
        """
        return self._application(b_pc,'mono')

    def prepare_tables(self,b_min_pc,b_max_pc,n=241,include_axial=False):
        """Quintic Hermite tables for thousands of lens/fit applications.

        Derivatives at every logarithmic node are the analytic projected
        derivatives, not finite differences. Returns measured midpoint
        interpolation discrepancies; these are numerical, not interval bounds.
        """
        if b_max_pc<=b_min_pc or n<8:
            raise ValueError('increasing bounds and at least eight nodes required')
        self._radii(b_min_pc)
        t=np.linspace(np.log(b_min_pc),np.log(b_max_pc),int(n))
        b=np.exp(t)
        tables={'lo':float(b_min_pc),'hi':float(b_max_pc),'nodes':int(n)}
        report={}
        for kind in ['quad','mono']+(['axial'] if include_axial else []):
            values=np.array([self._direct(x,kind) for x in b])
            # Remove the exact deep-screening phase plateau before polynomial
            # construction. Its large constant otherwise pollutes tiny q''.
            offset=0.
            if kind=='quad' and self.rV_pc:
                offset=-2*self.beta_hat*N2*self.rV_pc*_parameters(2)[3]/self._normalizations[2]
            jets=np.column_stack([values[:,0]-offset,b*values[:,1],b*values[:,1]+b*b*values[:,2]])
            poly=BPoly.from_derivatives(t,jets)
            tables[kind]=poly
            tables[kind+'_offset']=offset
            checks=[];relative=[]
            for i in np.linspace(0,len(t)-2,11,dtype=int):
                tm=(t[i]+t[i+1])/2;bm=np.exp(tm)
                direct=self._direct(bm,kind)
                y=poly(tm)+offset;d=poly.derivative()(tm);dd=poly.derivative(2)(tm)
                error=abs(np.array([y,d/bm,(dd-d)/bm**2])-direct)
                checks.append(error)
                relative.append(error/np.maximum(abs(direct),1e-100))
            report[kind+'_midpoint_max_abs_difference']=np.max(checks,axis=0).tolist()
            report[kind+'_midpoint_max_relative_difference']=np.max(relative,axis=0).tolist()
        self._tables=tables
        return {'nodes':int(n),'b_min_pc':b_min_pc,'b_max_pc':b_max_pc,
                'interval_certificate':False,**report}

    def matching_tail_bounds(self,b_pc,L_pc):
        """Finite-matching tail controls for L>>max(b,rV).

        Monopole bound is relative to ordinary 4m/b. The quad bound uses
        R2(r)<= (rV/r)^3 /R2(r0/rV), valid from its positive Euler integral.
        Both retain the assumed isolated exterior and frozen coefficients.
        """
        b=float(self._radii(b_pc))
        if L_pc<=max(b,self.rV_pc):
            raise ValueError('tail control requires L>max(b,rV)')
        # z cutoff L; r>=z. Integral_L^infty z^-5 dz =1/(4 L^4).
        if self.rV_pc:
            far_amplitude=self.rV_pc**3/self._normalizations.get(2,float(_shape_components(self.r0_pc/self.rV_pc,2)[0]))
        else:
            far_amplitude=self.r0_pc**3
        return {'monopole_extra_deflection_tail_over_GR':self.epsilon_infty*b*b/(2*L_pc**2),
                'absolute_quadrupole_phase_tail_pc_per_boundary_amplitude':
                    float(self.beta_hat*N2*far_amplitude*b*b/(2*L_pc**4)),
                'tail_only_not_total_approximation_error':True}

    def summary(self):
        return {'status':'CONDITIONAL_R1_EXTERIOR_OPEN_BLACK_HOLE_FLUX',
                'M_msun':self.M_msun,'z_l':self.z_l,'H0_km_s_Mpc':self.H0,
                'r0_pc':self.r0_pc,'flux_ratio':self.flux_ratio,
                'm_pc':self.m_pc,'L0_pc':self.L0_pc,'rV_pc':self.rV_pc,
                'worldtube_compactness':self.m_pc/self.r0_pc,
                'H_rV_over_c':self.H*self.rV_pc/self.L0_pc,
                'N2':float(N2),'coefficients':self.coefficients,
                'impedance_l2_dimensionless_x':self.impedance(2),
                'input_sha256':PINNED,
                'limitations':['supplied flux, worldtube amplitude and boundary state',
                    'weak metric, quasi-static leading cubic Hessian equations',
                    'scalar-driven metric only; ordinary multipoles remain independent',
                    'no horizon, photon ring, physical state selection or BHSM microscopic identification']}
