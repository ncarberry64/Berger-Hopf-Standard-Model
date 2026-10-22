"""Nodal-quadrupole strong-lens prediction with a fixed physical preparation.

The scalar response coefficients come from angular_optical_response.py.  The
present file solves the two noncaustic SIS image branches and evaluates the
full Fermat function, including moving source angle and physical impact.
Finite matrices complete a first-order map for derivative checks only; they
are not a second-order BHSM metric solution or an observed lens fit.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[1]
C_KM_S = 299792.458
MPC_METERS = 3.085677581491367e22
C_METERS_S = C_KM_S * 1000.
ARCSEC_PER_RADIAN = 180. * 3600. / np.pi
E = np.diag([1., -1.])


@dataclass(frozen=True)
class Preparation:
    z_l: float
    z_s: float
    d_ol: float
    d_os: float
    d_ls: float
    H0_km_s_Mpc: float = 67.4
    sigma_v_km_s: float = 200.
    source_offset_kpc: float = .8

    @property
    def length_unit_Mpc(self):
        return C_KM_S / self.H0_km_s_Mpc

    @property
    def b(self):
        return 4. * np.pi * (self.sigma_v_km_s/C_KM_S)**2

    @property
    def theta_E(self):
        return self.b*self.d_ls/self.d_os

    @property
    def source_length(self):
        return self.source_offset_kpc / 1000. / self.length_unit_Mpc

    @property
    def seconds_per_length(self):
        return self.length_unit_Mpc*MPC_METERS/C_METERS_S

    @property
    def T0(self):
        return (1.+self.z_l)*self.d_ol*self.d_os/self.d_ls


def from_record(record):
    return Preparation(record['z_l'], record['z_s'],
                       *(record['segments'][key]['background_distance_c_over_H0']
                         for key in ['ol', 'os', 'ls']))


def state_maps(preparation, segments, state):
    state = np.asarray(state, float)
    scales = [preparation.d_ol, preparation.d_os, preparation.d_ls]
    coefficients = [-np.sqrt(2.)*np.asarray(segments[key]['g_per_physical_anchor'])@state
                    for key in ['ol','os','ls']]
    return [d*(np.eye(2)+a*E) for d,a in zip(scales, coefficients)]


def solve_images(preparation, maps, azimuth):
    Dol, Dos, Dls = maps
    direction = np.array([np.cos(azimuth), np.sin(azimuth)])
    source = preparation.source_length*direction
    beta = np.linalg.solve(Dos, source)
    transport = np.linalg.solve(Dos, Dls)
    T = (1.+preparation.z_l)*Dol.T@np.linalg.solve(Dls,Dos)
    symmetry = float(np.max(abs(T-T.T)))
    if symmetry > 1.e-12*max(1.,np.max(abs(T))):
        raise ValueError('unsymmetrized Fermat matrix is not symmetric')

    def lens_equation(x):
        theta = preparation.theta_E*x
        impact = Dol@theta
        r = np.linalg.norm(impact)
        return x-beta/preparation.theta_E-transport@(preparation.b*impact/r)/preparation.theta_E

    def lens_jacobian(x):
        impact = Dol@(preparation.theta_E*x)
        r = np.linalg.norm(impact); u = impact/r
        return np.eye(2)-transport@(preparation.b/r*(np.eye(2)-np.outer(u,u)))@Dol

    def arrival(theta):
        v=theta-beta
        return .5*v@T@v-(1.+preparation.z_l)*preparation.b*np.linalg.norm(Dol@theta)

    q0=preparation.source_length/preparation.d_os/preparation.theta_E
    if not 0 < q0 < 1:
        raise ValueError('benchmark requires the unperturbed two-image SIS branch')
    images=[]
    for label,guess in [('outer_positive',(q0+1)*direction),('inner_negative',(q0-1)*direction)]:
        result=root(lens_equation,guess,jac=lens_jacobian,tol=2.e-12)
        residual=float(np.max(abs(lens_equation(result.x))))
        if residual > 2.e-12:
            raise RuntimeError(f'image root failed: {result.message}; residual={residual}')
        theta=preparation.theta_E*result.x
        jac=lens_jacobian(result.x)
        images.append({'branch':label,'theta_radian':theta.tolist(),
                       'theta_arcsec':(theta*ARCSEC_PER_RADIAN).tolist(),
                       'fermat_length':float(arrival(theta)),
                       'magnification':float(1./np.linalg.det(jac)),
                       'lens_residual_dimensionless':residual})
    delay=(images[1]['fermat_length']-images[0]['fermat_length'])*preparation.seconds_per_length
    return {'images':images,'beta_radian':beta.tolist(),'delay_seconds':float(delay),
            'T':T.tolist(),'time_matrix_symmetry_max_abs':symmetry}


def full_delay_derivative(preparation, baseline, map_derivatives):
    """Derivative in seconds per trial parameter, using all Fermat terms."""
    Eol,Eos,Els=map_derivatives
    beta=np.asarray(baseline['beta_radian'])
    values=[]
    for image in baseline['images']:
        v=np.asarray(image['theta_radian'])-beta
        values.append(preparation.T0*(.5*v@(Eos-Eol-Els)@v+v@(Eos-Eol)@beta))
    return float((values[1]-values[0])*preparation.seconds_per_length)


def correspondence_audit(preparation, maps, azimuth):
    Dol,Dos,Dls=maps
    source=preparation.source_length*np.array([np.cos(azimuth),np.sin(azimuth)])
    beta=np.linalg.solve(Dos,source)
    T=(1.+preparation.z_l)*Dol.T@np.linalg.solve(Dls,Dos)
    M=T/preparation.T0
    beta_eff=M@beta
    scalar=(1.+preparation.z_l)/preparation.T0
    constant=.5*beta@(M-M@M)@beta
    max_value=0.; max_gradient=0.
    for x in [(.7,.2),(-.8,.1),(.1,1.3),(1.4,-.7)]:
        theta=preparation.theta_E*np.asarray(x)
        r=Dol@theta; norm=np.linalg.norm(r)
        v=theta-beta
        original=.5*v@M@v-scalar*preparation.b*norm
        effective=.5*np.dot(theta-beta_eff,theta-beta_eff)-(
            scalar*preparation.b*norm+.5*theta@(np.eye(2)-M)@theta)
        grad0=M@v-scalar*Dol.T@(preparation.b*r/norm)
        grad1=theta-beta_eff-scalar*Dol.T@(preparation.b*r/norm)-(np.eye(2)-M)@theta
        max_value=max(max_value,abs(original-effective-constant)/preparation.theta_E**2)
        max_gradient=max(max_gradient,float(np.max(abs(grad0-grad1)))/preparation.theta_E)
    return {'scaled_fermat_identity_max_abs':float(max_value),'scaled_gradient_identity_max_abs':float(max_gradient)}


def main():
    temporal=json.loads((ROOT/'artifacts/temporal/angular_response.json').read_text())
    result={'schema':'BHSM-NODAL-QUADRUPOLE-SIS-PREDICTION-V1',
            'status':'EXECUTED_CONDITIONAL_FORWARD_RESPONSE',
            'preparation':{'H0_km_s_Mpc':67.4,'sigma_v_km_s':200.,'physical_source_offset_kpc':.8,
                           'quadrupole_C':'diag(1,-1,0)/sqrt(2)','central_direction':'z',
                           'anchor_coordinates':temporal['anchor_coordinates'],
                           'illustrative_state':[0.,0.,.001,0.,0.,0.],
                           'state_status':'chosen small density-seed illustration; not inferred or action-selected'},
            'configurations':[]}
    max_deriv=0.; max_root=0.; max_correspondence=0.
    for record in temporal['configurations']:
        p=from_record(record)
        kernel=np.array(record['nodal_SIS_fractional_delay_kernel_sqrt2_g_os_minus_g_ol'])
        zero=[p.d_ol*np.eye(2),p.d_os*np.eye(2),p.d_ls*np.eye(2)]
        base=solve_images(p,zero,0.)
        q=np.array(result['preparation']['illustrative_state'])
        angular=[]
        for degrees in [0.,22.5,45.,67.5,90.]:
            alpha=np.deg2rad(degrees)
            b0=solve_images(p,zero,alpha)
            finite=solve_images(p,state_maps(p,record['segments'],q),alpha)
            linear=base['delay_seconds']*(kernel@q)*np.cos(2*alpha)
            angular.append({'source_azimuth_deg':degrees,'linear_delta_delay_seconds':float(linear),
                            'finite_linear_map_delta_delay_seconds':finite['delay_seconds']-b0['delay_seconds'],
                            'finite_linear_map_images':finite['images']})
            max_root=max(max_root,max(x['lens_residual_dimensionless'] for x in finite['images']))
        checks=[]
        # Independent optical-matrix perturbations test all three map slots.
        # These are derivative probes, not physical finite-state selections.
        for coeff in [(1.,0.,0.),(0.,1.,0.),(0.,0.,1.),(.31,-.22,.19)]:
            for degrees in [0.,22.5,45.,90.]:
                alpha=np.deg2rad(degrees); b0=solve_images(p,zero,alpha)
                analytic=full_delay_derivative(p,b0,[a*E for a in coeff])/b0['delay_seconds']
                sis=(coeff[0]-coeff[1])*np.cos(2*alpha)
                def value(h):
                    maps=[d*(np.eye(2)+h*a*E) for d,a in zip([p.d_ol,p.d_os,p.d_ls],coeff)]
                    return solve_images(p,maps,alpha)['delay_seconds']/b0['delay_seconds']
                h=2.e-4
                fd=(-value(2*h)+8*value(h)-8*value(-h)+value(-2*h))/(12*h)
                err=abs(fd-sis);max_deriv=max(max_deriv,err)
                checks.append({'map_derivative_coefficients':list(coeff),'source_azimuth_deg':degrees,
                               'full_stationary_derivative':analytic,'closed_SIS_derivative':float(sis),
                               'direct_four_point_image_derivative':float(fd),'absolute_error':float(err)})
        corr=correspondence_audit(p,state_maps(p,record['segments'],q),.37)
        max_correspondence=max(max_correspondence,*corr.values())
        result['configurations'].append({'z_l':p.z_l,'z_s':p.z_s,
             'background_distances_Mpc':{k:d*p.length_unit_Mpc for k,d in zip(['ol','os','ls'],[p.d_ol,p.d_os,p.d_ls])},
             'baseline_delay_seconds':base['delay_seconds'],'baseline_delay_days':base['delay_seconds']/86400.,
             'baseline_images':base['images'],'theta_E_arcsec':p.theta_E*ARCSEC_PER_RADIAN,
             'source_angle_arcsec':p.source_length/p.d_os*ARCSEC_PER_RADIAN,
             'fractional_delay_kernel':kernel.tolist(),
             'delay_seconds_per_unit_anchor':(base['delay_seconds']*kernel).tolist(),
             'illustrative_angular_response':angular,'derivative_checks':checks,'effective_representation_check':corr})
    result['checks']={'max_fractional_four_point_derivative_error':max_deriv,
                      'max_lens_equation_residual':max_root,'max_scaled_effective_representation_error':max_correspondence}
    result['limits']=['first-order smooth scalar geometry and paraxial thin-lens encounter',
                      'fixed physical source displacement and SIS strength at fixed measured redshifts',
                      'continued two noncaustic image branches; no global image-count claim',
                      'finite-map values check derivatives only; no nonlinear BHSM solution',
                      'no observed data, no fitted or uniquely selected physical state',
                      'effective-potential representation preserves lensing observables; no unique state inference']
    assert max_deriv < 2.e-8
    assert max_root < 2.e-12
    assert max_correspondence < 2.e-13
    out=ROOT/'artifacts/lensing/nodal_sis_prediction.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'checks':result['checks'],'benchmarks':[{'z_l':i['z_l'],'z_s':i['z_s'],
                     'delay_days':i['baseline_delay_days'],'density_seed_delta_seconds':i['illustrative_angular_response'][0]['linear_delta_delay_seconds']}
                      for i in result['configurations']]},indent=2))


if __name__=='__main__':
    main()
