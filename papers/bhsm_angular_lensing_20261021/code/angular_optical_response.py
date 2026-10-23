"""First-order n=2 angular optical response on the frozen R1 background.

This module supplies the tracefree smooth-background Jacobi response, not a
complete scalar distance perturbation. Six physical anchor coordinates are
retained for every normalized n=2 spatial harmonic. No observed light curves,
image pixels, fitted physical amplitude, or preferred sky axis are used.

Conventions: ds^2=a^2[-(1+2 Phi)deta^2+(1-2 Psi)gamma_ij dx^i dx^j].
Lengths use c/H0. D_ab=d_ab[I-Gamma_ab+isotropic terms], with Gamma tracefree.
For STF3 C normalized by Tr(C^2)=1, Q=N sin^2(sqrt(K)chi) n.C.n,
N=sqrt(6/(pi^2 R^3)). H_C=2 E.T C E+(n.C.n) I is tracefree.
Gamma_ab=(g_ab @ anchor) H_C, where g_ab has the six unit responses.

The scalar endpoint/redshift/observer terms do not contribute to the first-
order tracefree map. They must be restored for a generic full distance map.
For the specially declared nodal quadrupole, Q=grad Q=0 along the central
ray; root's separate lens application may establish stronger conclusions.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import sys

import numpy as np
from scipy.integrate import quad, quad_vec, solve_ivp
from scipy.interpolate import CubicSpline

VENDOR = Path(__file__).resolve().parent / 'vendor_original' / 'code'
sys.path.insert(0, str(VENDOR))
import action_native_matter_n2 as an
import background as bg
from strong_lensing_transport import physical_anchor_to_canonical, ANCHOR_NAMES

ROOT = Path(__file__).resolve().parents[1]


def stf4_basis():
    """Frobenius-orthonormal real n=2 basis, angular sectors 1+3+5."""
    basis = [np.diag([3., -1., -1., -1.]) / np.sqrt(12.)]
    names = ['monopole']
    for j, name in enumerate(['x', 'y', 'z'], start=1):
        A = np.zeros((4, 4)); A[0, j] = A[j, 0] = 1/np.sqrt(2.)
        basis.append(A); names.append('dipole_'+name)
    for diagonal, name in [(np.array([1., -1., 0.])/np.sqrt(2.), 'xx_minus_yy'),
                           (np.array([1., 1., -2.])/np.sqrt(6.), 'xx_yy_minus_2zz')]:
        A = np.zeros((4, 4)); A[1:, 1:] = np.diag(diagonal)
        basis.append(A); names.append('quadrupole_'+name)
    for i, j, name in [(1, 2, 'xy'), (1, 3, 'xz'), (2, 3, 'yz')]:
        A = np.zeros((4, 4)); A[i, j] = A[j, i] = 1/np.sqrt(2.)
        basis.append(A); names.append('quadrupole_'+name)
    return names, np.asarray(basis)


def screen_basis(direction):
    n = np.asarray(direction, float)
    if n.shape != (3,) or not np.all(np.isfinite(n)) or np.linalg.norm(n) == 0:
        raise ValueError('direction must be a nonzero finite three-vector')
    n = n/np.linalg.norm(n)
    seed = np.eye(3)[int(np.argmin(np.abs(n)))]
    e1 = seed - n*(seed@n); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    return n, np.column_stack([e1, e2])


def angular_hessian_tf(A, direction, screen=None):
    """Dimensionless H_A; actual spatial Hessian_TF(Q)=N K H_A.

    Exact restriction of the S3 embedding Hessian to an observer-centered
    radial screen. Monopole and dipole sectors vanish identically.
    """
    A = np.asarray(A, float)
    if A.shape != (4, 4) or not np.allclose(A, A.T) or abs(np.trace(A)) > 1e-12:
        raise ValueError('A must be a symmetric tracefree 4x4 matrix')
    n, E = screen_basis(direction)
    if screen is not None:
        E = np.asarray(screen, float)
        if E.shape != (3, 2) or np.max(abs(E.T@E-np.eye(2))) > 1e-12 or np.max(abs(E.T@n)) > 1e-12:
            raise ValueError('screen must have orthonormal columns perpendicular to direction')
    B = E.T@A[1:, 1:]@E
    return 2*B-np.trace(B)*np.eye(2)


@dataclass
class SegmentResponse:
    z_a: float
    z_b: float
    chi_a: float
    chi_b: float
    distance: float
    g: np.ndarray
    quadrature_error_norm: float

    def as_dict(self):
        return {'z_a': self.z_a, 'z_b': self.z_b,
                'chi_a': self.chi_a, 'chi_b': self.chi_b,
                'background_distance_c_over_H0': self.distance,
                'g_per_physical_anchor': self.g.tolist(),
                'quadrature_error_norm': self.quadrature_error_norm}


class AngularOpticalProvider:
    """Current six-state action provider and first-order tracefree ray kernels."""
    def __init__(self, grid_size=801, prop_rtol=2e-10, prop_atol=2e-12,
                 prop_max_step=.01):
        self.K = bg.KCURV
        self.normalization = np.sqrt(6/(np.pi**2*self.K**(-1.5)))
        self.background = an.frozen_background()
        self.propagator = an.integrate_propagator(self.background, rtol=prop_rtol,
                                                atol=prop_atol, max_step=prop_max_step)
        self.anchor_to_canonical = physical_anchor_to_canonical(self.background)
        self.ns = np.linspace(an.N_START, 0., grid_size)
        self.row_samples = np.array([
            an.newtonian_map(N, self.background.sol(N))
            @ self.propagator.sol(N).reshape(6, 6) @ self.anchor_to_canonical
            for N in self.ns])
        self.rows = CubicSpline(self.ns, self.row_samples, axis=0)
        self.grid_size = grid_size
        self.prop_settings = {'rtol':prop_rtol,'atol':prop_atol,'max_step':prop_max_step}
        self.chi_max = self.chi_of_z(2.1)
        self.ray = solve_ivp(lambda chi, y: [-np.exp(y[0])*self.background.sol(y[0])[2]],
                             (0., self.chi_max), [0.], method='DOP853',
                             dense_output=True, rtol=2e-13, atol=1e-15, max_step=.005)
        if not self.ray.success:
            raise RuntimeError(self.ray.message)

    def S(self, chi):
        return np.sin(np.sqrt(self.K)*np.asarray(chi))/np.sqrt(self.K)

    def chi_of_z(self, z):
        if not 0 <= z <= 2.1:
            raise ValueError('redshift outside current action anchor domain 0<=z<=2.1')
        return quad(lambda N: np.exp(-N)/self.background.sol(N)[2],
                    -np.log1p(z), 0., epsabs=2e-13, epsrel=2e-13)[0]

    def weyl_rows(self, chi):
        N = float(self.ray.sol(chi)[0])
        r = self.rows(N)
        return r[0]+r[1]

    def segment(self, z_a, z_b):
        if not 0 <= z_a < z_b <= 2.05:
            raise ValueError('require 0<=z_a<z_b<=2.05')
        a, b = self.chi_of_z(z_a), self.chi_of_z(z_b)
        length = float(self.S(b-a))
        val, err = quad_vec(lambda chi: self.S(b-chi)*self.S(chi-a)*self.weyl_rows(chi),
                            a, b, epsabs=1e-13, epsrel=2e-12, quadrature='gk21')
        factor = self.normalization*self.K/length
        return SegmentResponse(z_a,z_b,a,b,length/(1+z_b),factor*val,float(factor*err))

    def segment_ode(self, z_a, z_b):
        """Independent forced Jacobi ODE rather than a Green-function quadrature."""
        a, b = self.chi_of_z(z_a), self.chi_of_z(z_b)
        def rhs(chi, state):
            J, V = state[:6], state[6:]
            source = self.normalization*self.K*self.weyl_rows(chi)*self.S(chi-a)
            return np.r_[V, -self.K*J+source]
        sol = solve_ivp(rhs, (a,b),np.zeros(12),method='DOP853',
                        rtol=2e-12,atol=2e-15,max_step=.006)
        if not sol.success:
            raise RuntimeError(sol.message)
        return sol.y[:6,-1]/self.S(b-a)

    def three_segments(self,z_l=.3,z_s=1.):
        return {'ol':self.segment(0.,z_l),'os':self.segment(0.,z_s),
                'ls':self.segment(z_l,z_s)}

    def audit_temporal(self):
        residual = 0.
        for N in np.linspace(an.N_START,0.,37):
            y = self.background.sol(N)
            state = self.propagator.sol(N).reshape(6,6)@self.anchor_to_canonical
            vel,aux = an.canonical_maps(N,y)
            for s in state.T:
                r = an.constraint_residuals(N,y,s[:3],vel@s,aux@s)
                residual=max(residual,float(np.max(abs(r))/max(1.,np.max(abs(s)))))
        N=an.N_START; y=self.background.sol(N); vel,aux=an.canonical_maps(N,y)
        import closed_horndeski_n2 as owner
        eye=np.eye(6)
        anchor_rows=np.array([eye[0],2*np.exp(3*N)*owner.gs_n2(y[1],y[2])*vel[0],
                              eye[1]-3*eye[0],(4/3)*(eye[2]-3*eye[0]),aux[2],aux[3]])
        return {'physical_anchor_reconstruction_max_abs':float(np.max(abs(anchor_rows@self.anchor_to_canonical-eye))),
                'original_constraint_scaled_max_abs':residual,
                'potential_no_slip_row_relative_max':float(np.max(abs(self.row_samples[:,0]-self.row_samples[:,1])/np.maximum(1.,abs(self.row_samples[:,0])))),
                'ray_anchor_N_residual':float(self.ray.y[0,-1]-an.N_START)}


def main():
    out=ROOT/'artifacts'/'temporal';out.mkdir(parents=True,exist_ok=True)
    provider=AngularOpticalProvider()
    configs=[(.3,1.),(.3,.6),(.5,1.5),(.8,2.)]
    data=[]
    max_ode=0.
    for zl,zs in configs:
        rows=provider.three_segments(zl,zs)
        item={'z_l':zl,'z_s':zs,'segments':{k:v.as_dict() for k,v in rows.items()}}
        checks={}
        for name,r in rows.items():
            ode=provider.segment_ode(r.z_a,r.z_b)
            diff=float(np.max(abs(ode-r.g)));max_ode=max(max_ode,diff)
            checks[name]={'forced_ode_g':ode.tolist(),'max_abs_difference':diff}
        item['independent_forced_ode']=checks
        item['fermat_shear_kernel_g_ol_minus_g_ls_plus_g_os']=(rows['ol'].g-rows['ls'].g+rows['os'].g).tolist()
        item['nodal_SIS_fractional_delay_kernel_sqrt2_g_os_minus_g_ol']=(np.sqrt(2)*(rows['os'].g-rows['ol'].g)).tolist()
        data.append(item)
    refined=AngularOpticalProvider(grid_size=1601,prop_rtol=2e-12,prop_atol=2e-14,prop_max_step=.005)
    max_refined=0.
    for item in data:
        r=refined.three_segments(item['z_l'],item['z_s'])
        item['refined_g']={k:v.g.tolist() for k,v in r.items()}
        item['max_abs_refinement_difference']=max(float(np.max(abs(v.g-np.array(item['segments'][k]['g_per_physical_anchor'])))) for k,v in r.items())
        max_refined=max(max_refined,item['max_abs_refinement_difference'])
    names,A=stf4_basis()
    rng=np.random.default_rng(20261021)
    directions=rng.normal(size=(31,3));directions/=np.linalg.norm(directions,axis=1)[:,None]
    H=np.array([[angular_hessian_tf(a,n) for a in A] for n in directions])
    shear_design=np.stack([H[:,:,0,0],H[:,:,0,1]],axis=1).reshape(-1,9)
    audit={'stf_basis_gram_max_abs':float(np.max(abs(np.einsum('aij,bij->ab',A,A)-np.eye(9)))),
           'monopole_dipole_shear_max_abs':float(np.max(abs(H[:,:4]))),
           'screen_hessian_trace_max_abs':float(np.max(abs(np.trace(H,axis1=2,axis2=3)))),
           'full_angular_shear_singular_values':np.linalg.svd(shear_design,compute_uv=False).tolist(),
           'full_angular_shear_rank':int(np.linalg.matrix_rank(shear_design,tol=1e-12)),
           'directions_count':len(directions),'directions_seed':20261021}
    result={'schema':'BHSM-N2-ANGULAR-OPTICAL-RESPONSE-V1','source_commit':'06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9',
            'status':'EXECUTED_CONDITIONAL_LINEAR_RESPONSE_NO_PHYSICAL_STATE_SELECTION',
            'anchor_coordinates':list(ANCHOR_NAMES),'anchor_redshift':2.1,
            'harmonic_normalization':provider.normalization,'K':provider.K,'distance_units':'c/H0',
            'harmonic_basis_order':names,'harmonic_basis_stf4':A.tolist(),
            'metric_convention':'Phi temporal, Psi conventional spatial sign; Weyl=Phi+Psi',
            'shear_convention':'D_ab=d_ab*(I-Gamma_ab+isotropic terms); Gamma_ab=(g_ab@q)*H_C',
            'main_provider_grid':provider.grid_size,'refined_provider_grid':refined.grid_size,
            'main_propagator':provider.prop_settings,'refined_propagator':refined.prop_settings,
            'temporal_audit':provider.audit_temporal(),'angular_audit':audit,
            'max_abs_quadrature_vs_forced_ode':max_ode,'max_abs_main_vs_refined':max_refined,
            'configurations':data,
            'limits':['tracefree cosmological response only unless a separate nodal-state proof applies',
                      'linear scalar perturbations about the frozen isotropic closed R1 background',
                      'six anchor coordinates per harmonic; no universal two-state or rank-one claim',
                      'no observed targets, calibration, selected amplitude, or microscopic BHSM normalization']}
    (out/'angular_response.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    np.savez_compressed(out/'temporal_rows.npz',N=provider.ns,rows=provider.row_samples,
                        anchor_to_canonical=provider.anchor_to_canonical,
                        harmonic_basis=A,angular_audit_directions=directions)
    print(json.dumps({'temporal_audit':result['temporal_audit'],'angular_audit':audit,
                      'max_abs_quadrature_vs_forced_ode':max_ode,'max_abs_main_vs_refined':max_refined,
                      'first_configuration':data[0]},indent=2))


if __name__=='__main__':
    main()
