"""Independent nodal metric angular-geodesic audit of the shear kernel.

The primary calculation starts from the angular Euler momentum L=S_K^2 theta'
and integrates theta and L; it does not insert the Green function or forced
Jacobi response. Along the nodal ray Q=grad Q=0, so its central metric, observed
redshift, radial coordinate and clocks coincide with the background in the
declared truncated metric completion. Finite amplitudes are derivative checks,
not new nonlinear solutions of the cosmological field equations.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp, quad
from angular_optical_response import AngularOpticalProvider, ANCHOR_NAMES, ROOT


def original_angular_map(provider, z_a, z_b, anchor, eigenvalue=np.sqrt(2.)):
    """Return D_ab/d_ab from original angular Euler equation.

    theta'=L/S(chi)^2,
    L'=-(Phi_coeff+Psi_coeff)*N*sin(sqrt(K)chi)^2*h*theta.
    Lens-vertex initial data theta_a=0,L_a=S(chi_a) implement unit local angle.
    At the observer theta_o=1,L_o=0 is imposed by its regular origin series.
    """
    a,b=provider.chi_of_z(z_a),provider.chi_of_z(z_b)
    q=np.asarray(anchor)
    dtype=np.result_type(q,float)
    if a==0.:
        eps=1e-6
        k0=provider.normalization*provider.K*eigenvalue*(provider.weyl_rows(0.)@q)
        start=eps
        state=np.asarray([1-k0*eps**2/6,-k0*eps**3/3],dtype=dtype)
    else:
        start=a; state=np.asarray([0.,provider.S(a)],dtype=dtype)
    def rhs(chi,y):
        Qh=provider.normalization*np.sin(np.sqrt(provider.K)*chi)**2*eigenvalue
        return np.asarray([y[1]/provider.S(chi)**2,
                           -(provider.weyl_rows(chi)@q)*Qh*y[0]],dtype=dtype)
    sol=solve_ivp(rhs,(start,b),state,method='DOP853',rtol=2e-13,atol=1e-15,max_step=.004)
    if not sol.success:
        raise RuntimeError(sol.message)
    return provider.S(b)*sol.y[0,-1]/provider.S(b-a)


def sampled_angular_maxima(provider,z_s,anchor,samples=2001):
    """Exact angular maxima, sampled along chi; not a certified continuum bound."""
    chi=np.linspace(0.,provider.chi_of_z(z_s),samples)
    N=provider.ray.sol(chi)[0]
    rows=provider.rows(N)@np.asarray(anchor,float)
    sinu=np.sin(np.sqrt(provider.K)*chi)
    qmax=provider.normalization*sinu**2/np.sqrt(2.)
    # For C=diag(1,-1,0)/sqrt2, max_n |grad_gamma Q| is exact below.
    gradmax=np.sqrt(2.)*provider.normalization*np.sqrt(provider.K)*abs(sinu)
    return {'max_relative_temporal_metric_2_abs_Phi':float(np.max(2*abs(rows[:,0])*qmax)),
            'max_relative_spatial_metric_2_abs_Psi':float(np.max(2*abs(rows[:,1])*qmax)),
            'max_first_order_physical_matter_speed_over_c':float(np.max(abs(rows[:,4])*gradmax/np.exp(N))),
            'radial_samples':samples,'maximum_redshift':z_s,
            'qualification':'exact angular maxima at sampled radial points; no certified continuous supremum'}


def main():
    p=AngularOpticalProvider()
    reports=[];max_complex=0.;max_finite=0.;max_background=0.
    for label,za,zb in [('ol',0.,.3),('os',0.,1.),('ls',.3,1.)]:
        segment=p.segment(za,zb)
        background=float(original_angular_map(p,za,zb,np.zeros(6)))
        max_background=max(max_background,abs(background-1))
        for j in range(6):
            e=np.eye(6)[j]
            bound=sampled_angular_maxima(p,zb,e)
            scale=max(bound['max_relative_temporal_metric_2_abs_Phi'],
                      bound['max_relative_spatial_metric_2_abs_Psi'],
                      bound['max_first_order_physical_matter_speed_over_c'])
            h=min(.02,1e-4/max(scale,1e-30))
            finite=[]
            for step in [h,h/2]:
                plus=float(original_angular_map(p,za,zb,step*e))
                minus=float(original_angular_map(p,za,zb,-step*e))
                finite.append({'step':step,'plus_fractional_map':plus,'minus_fractional_map':minus,
                               'central_derivative':(plus-minus)/(2*step)})
            hs=1e-20
            complex_derivative=float(np.imag(original_angular_map(p,za,zb,1j*hs*e))/hs)
            predicted=-np.sqrt(2)*segment.g[j]
            ce=abs(complex_derivative-predicted)
            fe=abs(finite[-1]['central_derivative']-predicted)
            max_complex=max(max_complex,ce);max_finite=max(max_finite,fe)
            reports.append({'segment':label,'coordinate':ANCHOR_NAMES[j],
                            'predicted_derivative_minus_sqrt2_g':predicted,
                            'original_angular_complex_step_derivative':complex_derivative,
                            'complex_step_absolute_difference':ce,
                            'finite_amplitude_trials':finite,'half_step_absolute_difference':fe,
                            'unit_anchor_sampled_maxima':bound,
                            'trial_max_metric_and_velocity':scale*h})
    constant_checks=[]
    for length in [.1,.5,1.]:
        numerical=quad(lambda x:p.S(length-x)*p.S(x),0.,length,epsabs=1e-14)[0]
        analytic=(p.S(length)-length*np.cos(np.sqrt(p.K)*length))/(2*p.K)
        constant_checks.append({'chi_length':length,'integral':numerical,'closed_form':float(analytic),
                                'absolute_difference':abs(numerical-analytic)})
    cases=[]
    for zl,zs in [(.3,1.),(.3,.6),(.5,1.5),(.8,2.)]:
        q=np.zeros(6);q[2]=.001
        cases.append({'z_l':zl,'z_s':zs,'anchor':q.tolist(),
                      **sampled_angular_maxima(p,zs,q)})
    result={'schema':'BHSM-NODAL-ANGULAR-EULER-AUDIT-V1',
            'equations':"theta'=L/S_K^2; L'=−(phi+psi) N sin²(sqrt(K)chi) h theta",
            'classification':'numerical derivative of declared metric completion; no selected physical amplitude',
            'nodal_quadrupole':'C=diag(1,-1,0)/sqrt2; central direction z',
            'max_background_fractional_map_defect':max_background,
            'max_complex_step_kernel_difference':max_complex,
            'max_half_step_finite_difference':max_finite,
            'records':reports,'constant_Weyl_kernel_identity':constant_checks,
            'illustrative_matter_density_seed':cases}
    out=ROOT/'artifacts'/'temporal';out.mkdir(parents=True,exist_ok=True)
    (out/'nodal_angular_geodesic_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
    assert max_background<2e-10
    assert max_complex<2e-10
    assert max_finite<2e-8


if __name__=='__main__':main()
