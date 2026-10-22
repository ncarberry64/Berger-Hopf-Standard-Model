"""Independent numerical checks of the conditional compact-source provider.

No observed source or horizon matching is selected. eta is supplied and its
normalization is explicit. Continuum/interval claims are deliberately absent.
"""
import json
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad, solve_ivp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from radial_response import ScreenedExterior,N2,N0,VENDOR


def main():
    s=ScreenedExterior()
    r=np.geomspace(s.r0_pc,1000*s.rV_pc,121)
    x=r/s.L0_pc;p=s.p(x)
    flux=s.C*x*x*p-4/s.lambda_hat*x*p*p+s.flux_ratio*s.beta_hat*s.mhat
    flux_error=float(np.max(abs(flux))/(s.flux_ratio*s.beta_hat*s.mhat))
    translation=s.radial(r,1)
    translation_error=float(np.max(abs(translation-p/p[0])/translation))
    # Independent original logarithmic radial equation, integrated inward.
    rho=r/s.rV_pc
    def rhs(t,y):
        u=np.exp(-3*t);q=(1+u/4)/(1+u)
        return [-y[0]**2+(1-2*q)*y[0]+6*q,y[0]]
    ts=np.log(rho)
    sol=solve_ivp(rhs,(ts[-1],ts[0]),[-3.,0.],method='DOP853',
                  rtol=2e-12,atol=1e-13,max_step=.015,dense_output=True)
    vals=sol.sol(ts)
    ode_shape=np.exp(vals[1]-vals[1,0])
    ode_error=float(np.max(abs(ode_shape/s.radial(r)-1)))
    # Independent direct z quadratures retain the field-to-metric units.
    b=1000.
    # z=b*sinh(t), r=b*cosh(t), unlike the provider's angular substitution.
    # The tail after r=1e8*rV is negligible under its explicit exterior bound.
    breaks=[0,np.arccosh(s.rV_pc/b),np.arccosh(10*s.rV_pc/b),
            np.arccosh(1e8*s.rV_pc/b)]
    phase=-2*s.beta_hat*N2*b*sum(quad(
        lambda t:s.radial(b*np.cosh(t))/np.cosh(t),lo,hi,
        epsabs=2e-16,epsrel=2e-11)[0]
        for lo,hi in zip(breaks[:-1],breaks[1:]))
    alpha=-2*s.beta_hat*b/s.L0_pc*sum(quad(
        lambda t:float(s.p(b*np.cosh(t)/s.L0_pc)),lo,hi,
        epsabs=1e-18,epsrel=2e-11)[0]
        for lo,hi in zip(breaks[:-1],breaks[1:]))
    axial_phase=-2*s.beta_hat*N0*b*sum(quad(
        lambda t:s.radial(b*np.cosh(t))*(2*np.cosh(t)-3/np.cosh(t)),lo,hi,
        epsabs=2e-16,epsrel=2e-11)[0]
        for lo,hi in zip(breaks[:-1],breaks[1:]))
    projected=s.projected_quad(b);mono=s.monopole_deflection(b)
    axial=s.projected_axial(b)
    phase_error=abs(projected[0]-phase)
    mono_error=abs(mono[0]-alpha)
    h=b*.001
    qm2,qm1,qp1,qp2=[s.projected_quad(b+k*h) for k in [-2,-1,1,2]]
    d1=(-qp2[0]+8*qp1[0]-8*qm1[0]+qm2[0])/(12*h)
    d2=(-qp2[1]+8*qp1[1]-8*qm1[1]+qm2[1])/(12*h)
    derivative_errors=[abs(d1/projected[1]-1),abs(d2/projected[2]-1)]
    am2,am1,ap1,ap2=[s.projected_axial(b+k*h) for k in [-2,-1,1,2]]
    axial_d1=(-ap2[0]+8*ap1[0]-8*am1[0]+am2[0])/(12*h)
    axial_d2=(-ap2[1]+8*ap1[1]-8*am1[1]+am2[1])/(12*h)
    axial_derivative_errors=[abs(axial_d1/axial[1]-1),abs(axial_d2/axial[2]-1)]
    # Far/deep analytic projected limits, and the exact flux=0 limit.
    far=300*s.rV_pc
    R0=float(s._normalizations[2])
    far_leading=-s.beta_hat*N2*s.rV_pc**3/R0*4/(3*far**2)
    far_projection_error=abs(s.projected_quad(far)[0]/far_leading-1)
    deep_leading=-2*s.beta_hat*N2*s.r0_pc
    deep_projection_error=abs(s.projected_quad(s.r0_pc)[0]/deep_leading-1)
    zero=ScreenedExterior(flux_ratio=0)
    zero_expected=-zero.beta_hat*N2*zero.r0_pc**3*4/(3*b*b)
    zero_projection_error=abs(zero.projected_quad(b)[0]/zero_expected-1)
    zero_impedance_error=abs(zero.impedance()/(3*zero.C*zero.x0)-1)
    # Supplied physical amplitude. Hessians use dimensionless local x.
    eta=1e-3
    amplitude=eta*s.x0*abs(float(s.p(s.x0)))/6
    rng=np.random.default_rng(20261021)
    directions=np.vstack([np.eye(3),rng.normal(size=(97,3))])
    directions/=np.linalg.norm(directions,axis=1)[:,None]
    Cmat=np.diag([1.,-1.,0.]);I=np.eye(3)
    linear_errors=[];hessian_ratios=[];nonlinear_ratios=[]
    for rr in np.geomspace(s.r0_pc,10*s.rV_pc,65):
        xx=rr/s.L0_pc;pp=float(s.p(xx));Kr,_,_=s.principal(rr)
        ppd=(-2*s.C*xx*pp+4*pp*pp/s.lambda_hat)/(xx*xx*Kr)
        f,df,ddf=s.radial_derivatives(rr)
        Df=rr*df;DDf=rr*rr*ddf+Df
        for n in directions:
            nn=np.outer(n,n);cn=Cmat@n;Y=float(n@cn)
            H0=ppd*nn+(pp/xx)*(I-nn)
            Hd=amplitude*N2/xx**2*((DDf-6*Df+8*f)*Y*nn
                +(Df-2*f)*Y*I+2*(Df-2*f)*(np.outer(n,cn)+np.outer(cn,n))+2*f*Cmat)
            Z=s.C*I-4/s.lambda_hat*(np.trace(H0)*I-H0)
            norm=np.linalg.norm(Hd)
            scale=(s.C+4/s.lambda_hat*(abs(np.trace(H0))+np.linalg.norm(H0)))*norm
            linear_errors.append(abs(np.sum(Z*Hd))/scale)
            quadratic=-2/s.lambda_hat*(np.trace(Hd)**2-np.sum(Hd*Hd))
            nonlinear_ratios.append(abs(quadratic)/scale)
            hessian_ratios.append(norm/np.linalg.norm(H0))
    # Einstein impact radius uses the SAME frozen closed R1 background.
    import action_native_matter_n2 as an
    import background as bg
    background=an.frozen_background()
    def chi(z):
        return quad(lambda N:np.exp(-N)/background.sol(N)[2],-np.log1p(z),0.,epsabs=1e-13)[0]
    def S(c):return np.sin(np.sqrt(bg.KCURV)*c)/np.sqrt(bg.KCURV)
    cl,cs=chi(.3),chi(1.)
    dol=s.L0_pc*S(cl)/1.3;dos=s.L0_pc*S(cs)/2;dls=s.L0_pc*S(cs-cl)/2
    rE=np.sqrt(4*s.m_pc*dol*dls/dos)
    epsilon=amplitude*s.projected_quad(rE)[0]/(4*s.m_pc)
    table_report=s.prepare_tables(10,1e5,241)
    result={'status':'PASS_CONDITIONAL_EXTERIOR_PROVIDER_INTERNAL_CHECK',
        'source':s.summary(),'source_flux_relative_residual':flux_error,
        'translation_relative_error':translation_error,'independent_radial_ODE_relative_error':ode_error,
        'independent_z_phase_absolute_error_pc':phase_error,
        'independent_z_monopole_deflection_absolute_error':mono_error,
        'analytic_projection_derivative_relative_errors':derivative_errors,
        'axial_projection_at_1000pc':list(axial),
        'independent_original_z_axial_phase_error_pc':abs(axial[0]-axial_phase),
        'axial_analytic_derivative_relative_errors':axial_derivative_errors,
        'zero_flux_axial_projection':list(zero.projected_axial(b)),
        'deep_projection_plateau_relative_difference':deep_projection_error,
        'far_projection_limit_relative_difference':far_projection_error,
        'zero_flux_projection_relative_error':zero_projection_error,
        'zero_flux_impedance_relative_error':zero_impedance_error,
        'eta_state':{'eta':eta,'a_definition':'eta*x0*abs(p0)/6','boundary_scalar_amplitude':amplitude,
            'sampled_radius_count':65,'sampled_directions_count':len(directions),
            'max_Hessian_perturbation_ratio':max(hessian_ratios),
            'max_scaled_linearized_equation_residual':max(linear_errors),
            'max_quadratic_residual_over_principal_term_scale':max(nonlinear_ratios),
            'interval_certificate':False,'rE_pc_at_zl03_zs1':rE,
            'epsilon_a_q_over_4m_at_rE':epsilon},
        'table_report':table_report,'finite_matching_tail':s.matching_tail_bounds(rE,1e7)}
    print(json.dumps(result,indent=2))
    assert flux_error<3e-14 and translation_error<3e-12 and ode_error<3e-9
    assert phase_error<3e-11 and mono_error<3e-22
    assert max(derivative_errors)<2e-7
    assert abs(axial[0]-axial_phase)<3e-11 and max(axial_derivative_errors)<2e-7
    assert zero.projected_axial(b)==(0.,0.,0.)
    assert far_projection_error<1e-7 and deep_projection_error<1e-6
    assert zero_projection_error<2e-12 and zero_impedance_error<2e-14
    assert max(linear_errors)<2e-12 and max(hessian_ratios)<.01 and max(nonlinear_ratios)<.001
    (ROOT/'review'/'radial_response_provider_check.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
