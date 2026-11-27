"""Physical thin-lens encounters and complete matched-map sensitivities.

Distances are physical angle-to-separation matrices in Mpc; angles are radians.
The main galaxy is excluded from these matrices and inserted exactly once here.
The source is a fixed transverse physical displacement unless explicitly varied.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import numpy as np
from scipy.optimize import root

C_KM_S = 299792.458
MPC_KM = 3.0856775814913673e19
DAY_S = 86400.
ARCSEC = np.pi/(180*3600)
MPC_OVER_C_DAYS = MPC_KM/C_KM_S/DAY_S


@dataclass(frozen=True)
class LensGeometry:
    D_ol: np.ndarray
    D_os: np.ndarray
    D_ls: np.ndarray
    z_l: float

    def __post_init__(self):
        for name in ('D_ol','D_os','D_ls'):
            value = np.array(getattr(self,name),dtype=float,copy=True)
            if value.shape != (2,2) or not np.isfinite(value).all() or np.linalg.det(value) <= 0:
                raise ValueError('finite pre-caustic physical2x2 distance maps required')
            object.__setattr__(self,name,value)
        if not np.isfinite(self.z_l) or self.z_l <= 0:
            raise ValueError('positive measured lens redshift required')
        defect = np.max(abs(self.T-self.T.T))/max(1.,np.max(abs(self.T)))
        if defect > 1e-10:
            raise ValueError('incompatible screen/Jacobi maps: time-delay matrix is not symmetric')

    @property
    def G(self):
        return np.linalg.solve(self.D_os,self.D_ls)

    @property
    def T(self):
        return (1+self.z_l)*self.D_ol.T@np.linalg.solve(self.D_ls,self.D_os)

    def displaced(self,d_maps,step):
        return LensGeometry(*(D+step*d for D,d in zip((self.D_ol,self.D_os,self.D_ls),d_maps)),self.z_l)


@dataclass(frozen=True)
class GalaxyPotential:
    """Declared SIS or circular softened-isothermal potential, in physical units.

    psi_hat=b sqrt(|x-centre|^2+core^2) + .5 (x-centre)^T sheet (x-centre).
    b is a physical deflection angle, core and centre are Mpc; sheet is1/Mpc.
    The core is an illustrative alternative galaxy, not a BHSM parameter.
    """
    b: float
    core_Mpc: float = 0.
    centre_Mpc: tuple = (0.,0.)
    sheet_per_Mpc: tuple = ((0.,0.),(0.,0.))

    def __post_init__(self):
        if self.b <= 0 or self.core_Mpc < 0:
            raise ValueError('positive strength and nonnegative declared core required')
        if not np.allclose(self.sheet,self.sheet.T,atol=1e-15,rtol=0):
            raise ValueError('encounter sheet must be a potential Hessian')

    @property
    def sheet(self):
        return np.asarray(self.sheet_per_Mpc,float)

    def application(self,x):
        y = np.asarray(x,float)-np.asarray(self.centre_Mpc)
        r = np.sqrt(y@y+self.core_Mpc**2)
        if r == 0:
            raise ValueError('SIS centre is singular; use an image away from it')
        potential = self.b*r+.5*y@self.sheet@y
        alpha = self.b*y/r+self.sheet@y
        hessian = self.b*(np.eye(2)/r-np.outer(y,y)/r**3)+self.sheet
        return potential,alpha,hessian


def source_angle(geometry,source_Mpc):
    return np.linalg.solve(geometry.D_os,np.asarray(source_Mpc,float))


def lens_application(theta,geometry,galaxy,source_Mpc):
    theta = np.asarray(theta,float)
    beta = source_angle(geometry,source_Mpc)
    potential,alpha,hessian = galaxy.application(geometry.D_ol@theta)
    residual = theta-beta-geometry.G@alpha
    jacobian = np.eye(2)-geometry.G@hessian@geometry.D_ol
    u = theta-beta
    ct_Mpc = .5*u@geometry.T@u-(1+geometry.z_l)*potential
    stationarity = geometry.T@u-(1+geometry.z_l)*geometry.D_ol.T@alpha
    return dict(residual=residual,jacobian=jacobian,ct_Mpc=float(ct_Mpc),
        arrival_days=float(ct_Mpc*MPC_OVER_C_DAYS),beta=beta,
        potential=potential,alpha=alpha,hessian=hessian,stationarity=stationarity)


def solve_images(geometry,galaxy,source_Mpc,*,seeds=None,angle_scale=None):
    beta = source_angle(geometry,source_Mpc)
    scale = float(angle_scale or galaxy.b*np.sqrt(np.linalg.det(geometry.G)))
    if scale <= 0:
        raise ValueError('positive image-search angular scale required')
    if seeds is None:
        angles = np.linspace(0,2*np.pi,16,endpoint=False)
        trials = [beta, -beta, np.zeros(2)]
        for radius in (.01,.3,.7,1.,1.4,2.):
            trials.extend(beta+scale*radius*np.c_[np.cos(angles),np.sin(angles)])
    else:
        trials = np.asarray(seeds)
    images=[]
    def f(q):
        return lens_application(scale*q,geometry,galaxy,source_Mpc)['residual']/scale
    def jac(q):
        return lens_application(scale*q,geometry,galaxy,source_Mpc)['jacobian']
    for seed in trials:
        try:
            sol = root(f,np.asarray(seed)/scale,jac=jac,tol=1e-11)
            image = sol.x*scale
            residual = np.max(abs(f(sol.x)))
        except (ValueError, FloatingPointError):
            continue
        if np.isfinite(image).all() and residual < 2e-9 and not any(np.linalg.norm(image-other)<1e-7*scale for other in images):
            images.append(image)
    if len(images)<2:
        raise ArithmeticError('fewer than two stationary images found in declared search')
    axis = beta/np.linalg.norm(beta)
    images = np.array(sorted(images,key=lambda t:float(t@axis),reverse=True))
    applications = [lens_application(t,geometry,galaxy,source_Mpc) for t in images]
    return dict(images_rad=images,images_arcsec=images/ARCSEC,
        arrival_days=np.array([a['arrival_days'] for a in applications]),
        relative_delays_days=np.array([a['arrival_days']-applications[0]['arrival_days'] for a in applications[1:]]),
        max_lens_residual_rad=max(np.max(abs(a['residual'])) for a in applications),
        max_stationarity_Mpc=max(np.max(abs(a['stationarity'])) for a in applications),
        inverse_magnification_determinants=np.array([np.linalg.det(a['jacobian']) for a in applications]),
        minimum_image_Jacobian_singular_value=min(np.linalg.svd(a['jacobian'],compute_uv=False)[-1] for a in applications))


def complete_map_response(images,geometry,galaxy,source_Mpc,d_maps,*,d_source_Mpc=None,
                          intrinsic_encounter=None):
    """Original off-shell lens equation and stationary arrival derivative.

    d_maps=(dDol,dDos,dDls), with measured redshifts fixed. The intrinsic
    intrinsic_encounter(x), if supplied, returns (dpsi_hat, dalpha_hat) at
    fixed physical impact x, in Mpc and radians per parameter unit. Its
    alpha must be the spatial gradient of its potential. This term must
    not duplicate metric propagation. None retains the fixed galaxy.
    """
    dDol,dDos,dDls = np.asarray(d_maps,float)
    beta = source_angle(geometry,source_Mpc)
    ds = np.zeros(2) if d_source_Mpc is None else np.asarray(d_source_Mpc,float)
    dbeta = np.linalg.solve(geometry.D_os,ds-dDos@beta)
    dG = np.linalg.solve(geometry.D_os,dDls-dDos@geometry.G)
    lsos = np.linalg.solve(geometry.D_ls,geometry.D_os)
    dT=(1+geometry.z_l)*(dDol.T@lsos+geometry.D_ol.T@np.linalg.solve(
        geometry.D_ls,dDos-dDls@lsos))
    defect=np.max(abs(dT-dT.T))/max(1.,np.max(abs(dT)))
    if defect>2e-9:
        raise ValueError('map derivative violates compatible time-delay symmetry')
    positions=[];time=[];pieces=[]
    for theta in images:
        a=lens_application(theta,geometry,galaxy,source_Mpc)
        impact=dDol@theta
        dpsi,dalpha=(0.,np.zeros(2)) if intrinsic_encounter is None else intrinsic_encounter(
            geometry.D_ol@theta)
        dalpha=np.asarray(dalpha,float)
        if np.shape(dpsi)!=() or dalpha.shape!=(2,) or not np.isfinite(dpsi) or not np.isfinite(dalpha).all():
            raise ValueError('intrinsic encounter requires finite scalar potential and two-vector deflection')
        dtheta=np.linalg.solve(a['jacobian'],dbeta+dG@a['alpha']+
            geometry.G@(a['hessian']@impact+dalpha))
        u=theta-beta
        terms=np.array([.5*u@dT@u,-u@geometry.T@dbeta,
            -(1+geometry.z_l)*a['alpha']@impact,-(1+geometry.z_l)*dpsi])*MPC_OVER_C_DAYS
        positions.append(dtheta/ARCSEC);time.append(terms.sum());pieces.append(terms)
    time=np.array(time)
    return dict(images_arcsec=np.array(positions),arrival_days=time,
        relative_delays_days=time[1:]-time[0],source_angle_response=dbeta,
        time_delay_matrix_response=dT,arrival_response_terms_days=np.array(pieces),
        terms_order=['map_T','physical_source_remapping','physical_galaxy_impact','intrinsic_encounter'])


def observable_vector(solution):
    return np.r_[solution['images_arcsec'].ravel(),solution['relative_delays_days']]


def response_vector(response):
    return np.r_[response['images_arcsec'].ravel(),response['relative_delays_days']]


def nuisance_columns(geometry,galaxy,source_Mpc,solution):
    """Declared local nuisance derivatives with physical conventions retained."""
    images=solution['images_rad'];base=observable_vector(solution)
    zero=np.zeros((3,2,2));columns=[];names=[]
    for i in range(2):
        dsource=geometry.D_os[:,i]*ARCSEC
        columns.append(response_vector(complete_map_response(images,geometry,galaxy,
            source_Mpc,zero,d_source_Mpc=dsource)))
        names.append('source_transverse_'+str(i)+'_per_arcsec')
    step=2e-5
    def galaxy_difference(plus,minus):
        p=solve_images(geometry,plus,source_Mpc,seeds=images)
        m=solve_images(geometry,minus,source_Mpc,seeds=images)
        if len(p['images_rad'])!=len(images) or len(m['images_rad'])!=len(images):
            raise ArithmeticError('nuisance crossed an image branch')
        return (observable_vector(p)-observable_vector(m))/(2*step)
    columns.append(galaxy_difference(replace(galaxy,b=galaxy.b*(1+step)),
        replace(galaxy,b=galaxy.b*(1-step))))
    names.append('log_galaxy_deflection_strength')
    for i in range(2):
        dc=geometry.D_ol[:,i]*ARCSEC
        centre=np.asarray(galaxy.centre_Mpc)
        columns.append(galaxy_difference(replace(galaxy,centre_Mpc=tuple(centre+step*dc)),
            replace(galaxy,centre_Mpc=tuple(centre-step*dc))))
        names.append('lens_centre_'+str(i)+'_per_arcsec')
    # The compensated mass-sheet transformation keeps image angles and
    # rescales all relative delays. Its source rescaling is part of this
    # degeneracy direction, not a second fixed physical experiment.
    mst=np.zeros_like(base);mst[2*len(images):]=solution['relative_delays_days']
    columns.append(mst);names.append('independent_mass_sheet_log_scale')
    # LOS sheet is deliberately a nuisance alternative. It is not added to
    # the primary response, which already includes smooth propagation.
    sheet=np.linalg.solve(geometry.D_ol.T,geometry.T)@np.linalg.inv(geometry.D_ol)/(1+geometry.z_l)
    columns.append(galaxy_difference(replace(galaxy,sheet_per_Mpc=tuple(map(tuple,galaxy.sheet+step*sheet))),
        replace(galaxy,sheet_per_Mpc=tuple(map(tuple,galaxy.sheet-step*sheet)))))
    names.append('independent_external_convergence_nuisance_only')
    # Fixed dimensional source and fixed physical galaxy: do not assign -tau.
    h0_response=complete_map_response(images,geometry,galaxy,source_Mpc,
        -np.array([geometry.D_ol,geometry.D_os,geometry.D_ls]))
    columns.append(response_vector(h0_response));names.append('log_H0_fixed_physical_source_and_galaxy')
    if galaxy.core_Mpc>0:
        columns.append(galaxy_difference(replace(galaxy,core_Mpc=galaxy.core_Mpc*(1+step)),
            replace(galaxy,core_Mpc=galaxy.core_Mpc*(1-step))))
        names.append('log_galaxy_core_radius')
    return np.column_stack(columns),names


def nuisance_projected_information(B,N,covariance,*,relative_tolerance=1e-8):
    """Whiten and project, reporting unmeasured state directions explicitly.

    No inverse Fisher matrix is returned for rank-deficient data. Right
    singular vectors in its nullspace are unconstrained, not zero variance.
    Nuisance columns are column-normalized before SVD to remove unit choices.
    """
    B,N,C=map(lambda a:np.asarray(a,float),(B,N,covariance))
    if C.shape!=(B.shape[0],B.shape[0]) or N.shape[0]!=B.shape[0]:
        raise ValueError('matching signal, nuisance and covariance rows required')
    if not np.allclose(C,C.T,atol=1e-14,rtol=0):
        raise ValueError('symmetric observational covariance required')
    L=np.linalg.cholesky(C)
    WB,WN=np.linalg.solve(L,B),np.linalg.solve(L,N)
    norms=np.linalg.norm(WN,axis=0)
    keep=norms>1e-14
    normalized=WN[:,keep]/norms[keep]
    U,s,_=np.linalg.svd(normalized,full_matrices=False)
    rankN=int(np.sum(s>relative_tolerance*(s[0] if len(s) else 1.)))
    residual=WB-U[:,:rankN]@(U[:,:rankN].T@WB)
    _,sr,Vh=np.linalg.svd(residual,full_matrices=True)
    reference=max(np.linalg.svd(WB,compute_uv=False)[0],1e-30)
    rank=int(np.sum(sr>relative_tolerance*reference))
    return dict(nuisance_rank=rankN,signal_rank=rank,raw_signal_singular_values=np.linalg.svd(WB,compute_uv=False),
        projected_signal_singular_values=sr,relative_rank_tolerance=relative_tolerance,
        absolute_rank_threshold=relative_tolerance*reference,Fisher=residual.T@residual,
        projected_response=residual,null_directions=Vh[rank:],
        null_direction_interpretation='unconstrained without declared independent information; no finite zero-uncertainty estimate',
        nuisance_whitened_column_norms=norms)
