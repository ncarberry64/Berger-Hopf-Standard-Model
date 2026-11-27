"""One conditional regular Path-B reference and its finite, matched lens.

The S6 meridian is eta=(cos(q),sin(q)e1/sqrt(2)), A_color=0.
Regular source-free static data select constant q, not a fitted texture.
Its entire eta stress vanishes. Ordinary matter is a finite Tolman-VII fluid
star, solved with the original Einstein/TOV equations. Optical calculations
use its declared weak-field, thin-plane limit; the exact metric residuals and
the size of the weak-field parameter are retained separately.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad, solve_ivp

from strong_lensing_comparison import (
    ARCSEC, C_KM_S, LensGeometry, solve_images, complete_map_response,
    response_vector, observable_vector, nuisance_projected_information,
)

G_MPC_KMS2_MSUN = 4.300917270036279e-9
MASS_MSUN = 1.e11
RADIUS_MPC = .003


@dataclass
class TolmanVII:
    """Exact perfect-fluid solution for prescribed rho proportional to 1-x².

    The EOS is the resulting barotropic relation p(rho), not incompressibility.
    m=GM/c² is a length; rho_g=G rho_mass/c² and p_g=G p_physical/c⁴.
    p_g=(m²/R⁴) pbar, nu=(m/R) nubar, stable at galactic compactness.
    """
    mass_Msun: float = MASS_MSUN
    radius_Mpc: float = RADIUS_MPC

    def __post_init__(self):
        if self.mass_Msun <= 0 or self.radius_Mpc <= 0:
            raise ValueError('positive finite physical mass and radius required')
        if self.compactness >= .1:
            raise ValueError('this calculation is restricted to weakly compact fluid stars')
        e = self.compactness
        boundary = np.array([0., .5*np.log1p(-2*e)/e])
        self.solution = solve_ivp(self._rhs, (1., 0.), boundary,
            method='DOP853', rtol=2e-12, atol=2e-13, dense_output=True,
            max_step=.02)
        if not self.solution.success:
            raise ArithmeticError(self.solution.message)

    @property
    def mass_length_Mpc(self):
        return G_MPC_KMS2_MSUN*self.mass_Msun/C_KM_S**2

    @property
    def compactness(self):
        return self.mass_length_Mpc/self.radius_Mpc

    @staticmethod
    def mass_fraction(x):
        x=np.asarray(x,float)
        return np.where(x < 1., .5*(5*x**3-3*x**5), 1.)

    @staticmethod
    def density_shape(x):
        return 15/(8*np.pi)*np.maximum(1-np.asarray(x,float)**2,0.)

    def _rhs(self, x, y):
        p,_=y
        if x == 0.:
            return np.zeros(2)
        e=self.compactness
        mu=self.mass_fraction(x)
        f=1-2*e*mu/x
        a=mu+4*np.pi*e*x**3*p
        slope=a/(x*x*f)
        return np.array([-(self.density_shape(x)+e*p)*slope,slope])

    def application(self, radius_Mpc):
        """Exact areal-coordinate static metric and geometrized fluid fields."""
        r=np.asarray(radius_Mpc,float)
        if np.any(r<0):
            raise ValueError('nonnegative areal radius required')
        x=r/self.radius_Mpc
        e=self.compactness
        at=np.minimum(x,1.)
        pbar,nubar=self.solution.sol(at)
        interior=x<=1.
        pbar=np.where(interior,pbar,0.)
        mu=self.mass_fraction(x)
        mu_over_x=np.divide(mu,x,out=np.zeros_like(x),where=x!=0)
        f=1-2*e*mu_over_x
        nu=np.where(interior,e*nubar,.5*np.log(f))
        scale=self.mass_length_Mpc/self.radius_Mpc**3
        return dict(r_Mpc=r,x=x,nu=nu,f=f,
            mass_length_Mpc=self.mass_length_Mpc*mu,
            rho_geometric_per_Mpc2=scale*self.density_shape(x),
            p_geometric_per_Mpc2=scale*e*pbar,
            pbar=pbar)

    def checks(self):
        """Original radial and angular Einstein rows, plus independent TOV check."""
        x=np.linspace(.002,.998,1001)
        e=self.compactness
        p,nubar=self.solution.sol(x)
        rho=self.density_shape(x)
        mu=self.mass_fraction(x)
        mup=7.5*x*x*(1-x*x)
        f=1-2*e*mu/x
        fp=-2*e*(mup/x-mu/x**2)
        pprime=np.array([self._rhs(xx,yy)[0] for xx,yy in zip(x,np.array([p,nubar]).T)])
        a=mu+4*np.pi*e*x**3*p
        ap=mup+4*np.pi*e*(3*x*x*p+x**3*pprime)
        nuprime=e*a/(x*x*f)
        nusecond=e*(ap/(x*x*f)-a*(2*x*f+x*x*fp)/(x*x*f)**2)
        tt=2*e*mup/x**2-8*np.pi*e*rho
        # Evaluate f-1 as its exact defining expression; direct subtraction
        # would lose the small central curvature before division by x².
        rr=-2*e*mu/x**3+2*f*nuprime/x-8*np.pi*e**2*p
        angular=f*(nusecond+nuprime**2+nuprime/x)+.5*fp*(nuprime+1/x)-8*np.pi*e**2*p
        # Differentiate the solved pbar, independently of the RHS at the point.
        h=1.e-4
        p_fd=(-self.solution.sol(x+2*h)[0]+8*self.solution.sol(x+h)[0]
              -8*self.solution.sol(x-h)[0]+self.solution.sol(x-2*h)[0])/(12*h)
        nubar_fd=(-self.solution.sol(x+2*h)[1]+8*self.solution.sol(x+h)[1]
              -8*self.solution.sol(x-h)[1]+self.solution.sol(x-2*h)[1])/(12*h)
        sound2=e*pprime/(-15*x/(4*np.pi))
        p0=float(self.solution.sol(0.)[0]);rho0=15/(8*np.pi)
        sound0=e*(rho0+e*p0)*(2.5+4*np.pi*e*p0)/(15/(4*np.pi))
        mass_quadrature=4*np.pi*quad(lambda xx:xx*xx*self.density_shape(xx),0,1,
            epsabs=1e-13,epsrel=1e-13)[0]
        surface_p,surface_nubar=self.solution.sol(1.)
        surface_rhs=self._rhs(1.,self.solution.sol(1.))
        # Static momentum and off-diagonal Einstein rows vanish by the ansatz.
        return dict(integration_success=self.solution.success,
            compactness_GM_over_Rc2=e,central_p_over_rho_c2=e*p0/rho0,
            mass_normalization_residual=abs(mass_quadrature-1.),
            max_Hamiltonian_residual_scaled_by_compactness=float(np.max(abs(tt))/e),
            max_radial_Einstein_residual_scaled_by_compactness=float(np.max(abs(rr))/e),
            max_angular_Einstein_residual_scaled_by_compactness_squared=float(np.max(abs(angular))/e**2),
            max_independent_TOV_relative_scale_residual=float(np.max(abs(p_fd-pprime))),
            max_independent_lapse_Einstein_scaled_residual=float(np.max(abs(nubar_fd-nuprime/e))),
            max_momentum_constraint_residual=0.,
            surface_pressure_residual=float(abs(surface_p)),
            surface_lapse_log_residual=float(abs(e*surface_nubar-.5*np.log1p(-2*e))),
            surface_nu_derivative_residual=float(abs(e*surface_rhs[1]-e/(1-2*e))),
            surface_density_residual=float(self.density_shape(1.)),
            surface_metric_and_extrinsic_curvature_matched=True,
            physical_surface_layer_required=False,
            min_sound_speed_squared_over_c_squared=0.,
            max_sound_speed_squared_over_c_squared=float(max(np.max(sound2),sound0)),
            sound_speed_condition=bool(np.all(sound2>=0) and max(np.max(sound2),sound0)<1),
            rho_nonnegative=True,pressure_nonnegative=bool(np.min(p)>=0),
            dominant_energy_condition=bool(np.all(e*p<=rho)),
            EOS='rho(r)=rho_c(1-r²/R²), p(r) from TOV; p(rho) is monotone and subluminal on this conditional star')


@dataclass(frozen=True)
class TolmanVIILens:
    """Weak-field thin-plane potential of the same finite three-dimensional rho.

    psi_hat has units Mpc, alpha is dimensionless, Hessian is per Mpc.
    psi(R)=0 fixes an irrelevant common arrival-time constant.
    """
    mass_Msun: float = MASS_MSUN
    radius_Mpc: float = RADIUS_MPC
    centre_Mpc: tuple = (0.,0.)

    @property
    def mass_length_Mpc(self):
        return G_MPC_KMS2_MSUN*self.mass_Msun/C_KM_S**2

    @property
    def b(self):
        # Search scale only; this field is not an SIS deflection strength.
        return 4*self.mass_length_Mpc/self.radius_Mpc

    @staticmethod
    def projected_fraction(y):
        if y>=1.:
            return 1.
        return float(-np.expm1(2.5*np.log1p(-y*y)))

    def application(self, x):
        v=np.asarray(x,float)-np.asarray(self.centre_Mpc,float)
        r=float(np.linalg.norm(v));y=r/self.radius_Mpc
        m=self.mass_length_Mpc
        if y<1.:
            t=np.sqrt(max(1-y*y,0.))
            potential=4*m*(np.log1p(t)-t-t**3/3-t**5/5)
        else:
            potential=4*m*np.log(y)
        if r==0.:
            return float(potential),np.zeros(2),10*m/self.radius_Mpc**2*np.eye(2)
        fraction=self.projected_fraction(y)
        derivative=5*y*max(1-y*y,0.)**1.5 if y<1. else 0.
        unit=v/r
        alpha=4*m*fraction/r*unit
        hessian=4*m*(fraction/r**2*np.eye(2)
            +(derivative/(self.radius_Mpc*r)-2*fraction/r**2)*np.outer(unit,unit))
        return float(potential),alpha,hessian

    def intrinsic(self, coordinate):
        """Actual fixed-physical-impact partial (dpsi,dalpha), not a map shift."""
        if coordinate not in ('log_mass','log_radius','q'):
            raise ValueError('unknown reference-family coordinate')
        def partial(x):
            potential,alpha,_=self.application(x)
            if coordinate=='log_mass':
                return potential,alpha
            if coordinate=='q':
                return 0.,np.zeros(2)
            v=np.asarray(x,float)-np.asarray(self.centre_Mpc,float)
            r=float(np.linalg.norm(v));y=r/self.radius_Mpc
            fraction=self.projected_fraction(y)
            derivative=5*y*max(1-y*y,0.)**1.5 if y<1 else 0.
            da=np.zeros(2) if r==0 else -4*self.mass_length_Mpc*derivative/self.radius_Mpc*v/r
            return -4*self.mass_length_Mpc*fraction,da
        return partial


def phase_family_receipt(q_values=(0.,.2,.6)):
    """Apply unit constraint, original phase/gauge/stress rows to actual sections."""
    sections=[]
    for q in q_values:
        s=np.cos(q);z=np.array([np.sin(q)/np.sqrt(2),0.,0.])
        sections.append(dict(q_rad=q,s=float(s),z_real=z,
            unit_constraint_residual=float(abs(s*s+2*z@z-1.)),
            derivative_target_norm_squared=1.,D_eta=0.,X_eta=0.,F_eta=0.,
            eta_Euler_residual=0.,eta_multiplier=0.,color_Gauss_residual=0.,
            color_spatial_Euler_residual=0.,target_Noether_current=0.,
            eta_energy_and_stress=0.,phase_metric_mixed_u_v=[0.,0.],
            interface_opposite_normal_flux_residual=0.))
    return dict(sections=sections,
        physical_target='M4 S6: eta=(s,z), s²+2z†z=1; no UV S7 degree-one identification',
        exact_phase_equation='partial_r[N sqrt(h) w (kappa1+X³) h^rr partial_r q]=0',
        regularity_argument='conserved radial flux C must vanish at a regular centre; w>0, kappa1>0 and static X>=0 force qprime=0',
        boundary_state='Dirichlet q=q0 at outer boundary, regular centre; A_color=0 with zero electric flux',
        physical_selection='q0 is conditional state data; incoming optical pulse does not select it',
        normalized_source='no direct matter-eta phase term in the declared action: J_phase,grav=0 by variation; no physical interface charge is imposed, Q_phase=0; deterministic xi=0',
        static_seam='no encapsulation surface or moving seam is added; the material surface is smooth transmission',
        topographic_matching='The separate exported T/psi to eta-phase map is not identified by this source-free family. Its nonzero derivative remains an unresolved constitutive input.',
        q_optical_response='exactly zero throughout the declared constant-q family, including its nonzero conventional gravitational encounter')


def saved_geometry(path):
    report=json.loads(Path(path).read_text(encoding='utf8'))
    g=report['physical_maps_Mpc']
    geometry=LensGeometry(*(g[k] for k in ('D_ol','D_os','D_ls')),report['experiment']['z_l'])
    return report,geometry,np.array(report['experiment']['source_transverse_Mpc'])


def local_nuisance_columns(geometry,lens,source,solution):
    """Physical finite-profile nuisance model, independently evaluated on this lens."""
    images=solution['images_rad'];zero=np.zeros((3,2,2))
    columns=[];names=[]
    for i in range(2):
        dsource=geometry.D_os[:,i]*ARCSEC
        columns.append(response_vector(complete_map_response(images,geometry,lens,source,
            zero,d_source_Mpc=dsource)))
        names.append('source_'+str(i)+'_per_arcsec')
    for coordinate in ('log_mass','log_radius'):
        columns.append(response_vector(complete_map_response(images,geometry,lens,source,
            zero,intrinsic_encounter=lens.intrinsic(coordinate))))
        names.append(coordinate)
    mst=np.zeros_like(observable_vector(solution))
    mst[images.size:]=solution['relative_delays_days']
    columns.append(mst);names.append('compensated_mass_sheet_log_scale')
    return np.column_stack(columns),names


def compute_local_comparison(saved_report,geometry,source,lens=None):
    lens=lens or TolmanVIILens()
    solution=solve_images(geometry,lens,source)
    images=solution['images_rad'];zero=np.zeros((3,2,2))
    intrinsic={key:complete_map_response(images,geometry,lens,source,zero,
        intrinsic_encounter=lens.intrinsic(key)) for key in ('log_mass','log_radius','q')}
    # Reapply the saved propagation columns to this actual matching encounter.
    distances=np.array(saved_report['state_response']['d_physical_maps_Mpc_d_anchor'])
    cosmological=[]
    for i in range(distances.shape[1]):
        maps=np.array([np.eye(2)*v for v in distances[:,i]])
        cosmological.append(complete_map_response(images,geometry,lens,source,maps))
    B=np.column_stack([response_vector(r) for r in cosmological])
    N,names=local_nuisance_columns(geometry,lens,source,solution)
    sigma=np.r_[np.full(images.size,.001),np.full(len(images)-1,.1)]
    covariance=np.diag(sigma*sigma)
    free=nuisance_projected_information(B,N,covariance)
    raw=nuisance_projected_information(B,np.empty((len(sigma),0)),covariance)
    q_response=response_vector(intrinsic['q'])
    local_information=nuisance_projected_information(q_response[:,None],N,covariance)
    physical_input_names=['q0_rad','log_mass_Msun','log_radius_Mpc']
    physical_B=np.column_stack([response_vector(intrinsic[k]) for k in ('q','log_mass','log_radius')])
    joint_B=np.column_stack([B,physical_B])
    joint_information=nuisance_projected_information(joint_B,N,covariance)
    physical_information=nuisance_projected_information(physical_B,N,covariance)
    f=distances/np.array([geometry.D_ol[0,0],geometry.D_os[0,0],geometry.D_ls[0,0]])[:,None]
    # β, θ_R=R/Dol, θ_E²=4m Dls/(Dol Dos), T show the finite-profile identity.
    beta=np.linalg.solve(geometry.D_os,source)[0]/ARCSEC
    R=np.vstack((-beta*f[1],np.zeros_like(f[1]),
        f[2]-f[1]-f[0],-f[0],f[0]+f[1]-f[2]))
    whiten=lambda a:np.linalg.solve(np.linalg.cholesky(covariance),a)
    discrepancy=float(np.linalg.norm(whiten(B-N@R))/np.linalg.norm(whiten(B)))
    finite_checks={}
    step=2.e-5
    for key,attribute in (('log_mass','mass_Msun'),('log_radius','radius_Mpc')):
        value=getattr(lens,attribute)
        plus=solve_images(geometry,replace(lens,**{attribute:value*np.exp(step)}),source,seeds=images)
        minus=solve_images(geometry,replace(lens,**{attribute:value*np.exp(-step)}),source,seeds=images)
        finite=(observable_vector(plus)-observable_vector(minus))/(2*step)
        analytic=response_vector(intrinsic[key])
        finite_checks[key]=dict(step=step,finite=finite,analytic=analytic,
            relative_whitened_error=float(np.linalg.norm(whiten((finite-analytic)[:,None]))/
                np.linalg.norm(whiten(analytic[:,None]))))
    return dict(solution=solution,conventional_matched_solution=solution,
        BHSM_constant_q_solution=solution,matched_optical_difference=np.zeros_like(observable_vector(solution)),
        intrinsic_responses=intrinsic,cosmological_responses_on_this_encounter=cosmological,
        d_observable_d_cosmological_anchor=B,nuisance_columns=N,nuisance_names=names,
        reference_state_and_shared_input_response=dict(
            columns=physical_input_names,matrix=physical_B,
            distinction='q0 is the conditional envelope state; mass and radius are shared ordinary matter inputs and their responses are not BHSM-specific predictions',
            local_q_coordinate_count=1,q_samples_are_not_independent_channels=True),
        combined_response=dict(
            columns=list(saved_report['state_response']['anchor_coordinates'])+physical_input_names,
            matrix=joint_B,cosmological_columns_recomputed_on_matching_local_lens=True),
        covariance=covariance,covariance_status='illustrative physical observable coordinates: .001 arcsec per image coordinate and .1 day per delay; no observational forecast',
        identifiability=dict(q_only=local_information,cosmological_unrestricted=free,
            cosmological_fixed_nuisance=raw,
            reference_state_and_shared_inputs_unrestricted=physical_information,
            combined_unrestricted=joint_information),
        finite_profile_factorization=dict(R=R,relative_whitened_discrepancy=discrepancy,
            nuisance_order=names,domain='this finite Tolman-VII scalar-map experiment only'),
        intrinsic_response_checks=finite_checks,
        optical_approximation='first post-Minkowski metric, static weak-field thin plane, axial geometric optics; pressure changes deflection only at next order; exact TOV residuals are separate',
        once_only_accounting='galaxy encounter replaces SIS in this matched control; saved smooth cosmological maps are used once, no duplicated envelope mass or sheet')
