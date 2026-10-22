"""State-resolved ordered Jacobi response of the recovered conditional R1 model.

No observations, fitted amplitudes, new matter coupling or Berger spacetime
substitution. Lengths c/H0; harmonic coefficients use inherited volume units.
The finite optical ODE resums the specified first-order tidal field only.
"""
from pathlib import Path
import json
import sys
import numpy as np
from scipy.integrate import solve_ivp, simpson

ROOT = Path(__file__).resolve().parents[1]
INHERITED = ROOT.parent / 'bhsm_angular_lensing_20261021'
sys.path.insert(0, str(INHERITED / 'code'))
from angular_optical_response import AngularOpticalProvider

Z = np.diag([1., -1.])
X = np.array([[0., 1.], [1., 0.]])
J = Z @ X


def wedge_matrix(provider, za, zb, max_step=.006, rtol=2e-11, atol=2e-17):
    """B_ij in skew(D/S)=u^T B v J, and first-order normalized G row.

    Evolve all six first-order responses and all 36 ordered products.
    Auxiliary ODE is derived by expanding the original 2x2 Jacobi equation.
    """
    a, b = provider.chi_of_z(za), provider.chi_of_z(zb)
    c = np.sqrt(2.) * provider.normalization * provider.K
    def rhs(t, state):
        g, gd = state[:6], state[6:12]
        B, Bd = state[12:48].reshape(6,6), state[48:].reshape(6,6)
        w = provider.weyl_rows(t)
        forcing = c * (np.outer(w,g)-np.outer(g,w))
        return np.r_[gd, -provider.K*g+c*w*provider.S(t-a),
                     Bd.ravel(), (-provider.K*B+forcing).ravel()]
    sol = solve_ivp(rhs, (a,b), np.zeros(84), method='DOP853',
                    rtol=rtol, atol=atol, max_step=max_step, dense_output=True)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y[12:48,-1].reshape(6,6)/provider.S(b-a), sol.y[:6,-1]/provider.S(b-a), sol


def ordered_quadrature(provider, za, zb, n=801):
    """Independent double Simpson integration, no response ODE used."""
    a,b = provider.chi_of_z(za), provider.chi_of_z(zb)
    t = np.linspace(a,b,n)
    w = np.array([provider.weyl_rows(x) for x in t])
    c = np.sqrt(2.)*provider.normalization*provider.K
    integrand = []
    for k, tk in enumerate(t):
        if k == 0:
            inner = np.zeros(6)
        else:
            inner = simpson((provider.S(tk-t[:k+1])*provider.S(t[:k+1]-a))[:,None]*w[:k+1],
                            x=t[:k+1],axis=0)
        integrand.append(provider.S(b-tk)*(np.outer(w[k],inner)-np.outer(inner,w[k])))
    return c*c*simpson(np.asarray(integrand), x=t,axis=0)/provider.S(b-a)


def finite_map(provider, za, zb, u, v, amplitude=1., extra_symmetric=None):
    """Solve original matrix Jacobi ODE with specified tides.

    extra_symmetric(t) multiplies amplitude^2; probes robustness of the
    leading antisymmetric coefficient, not a derived second-order metric.
    """
    a,b = provider.chi_of_z(za),provider.chi_of_z(zb)
    c = np.sqrt(2.)*provider.normalization*provider.K
    def rhs(t,state):
        D,V=state[:4].reshape(2,2),state[4:].reshape(2,2)
        w=provider.weyl_rows(t)
        T=amplitude*c*((w@u)*Z+(w@v)*X)
        if extra_symmetric is not None:
            T=T+amplitude**2*extra_symmetric(t)
        return np.r_[V.ravel(), (-(provider.K*np.eye(2)+T)@D).ravel()]
    init=np.r_[np.zeros(4),np.eye(2).ravel()]
    sol=solve_ivp(rhs,(a,b),init,method='DOP853',rtol=3e-13,atol=1e-16,max_step=.004)
    if not sol.success:
        raise RuntimeError(sol.message)
    D=sol.y[:4,-1].reshape(2,2)/provider.S(b-a)
    return D


def skew_coefficient(M):
    return float((M[0,1]-M[1,0])/2)


def finite_rotation_components(provider,za,zb,u,v,amplitude):
    """Original finite ODE in I,Z,X,J components, avoiding off-diagonal cancellation."""
    a,b=provider.chi_of_z(za),provider.chi_of_z(zb)
    c=np.sqrt(2.)*provider.normalization*provider.K
    def rhs(t,state):
        d,vel=state[:4],state[4:]
        w=provider.weyl_rows(t)
        hz,hx=amplitude*c*(w@u),amplitude*c*(w@v)
        product=np.array([hz*d[1]+hx*d[2],hz*d[0]-hx*d[3],
                          hx*d[0]+hz*d[3],hz*d[2]-hx*d[1]])
        return np.r_[vel,-provider.K*d-product]
    init=np.zeros(8);init[4]=1.
    sol=solve_ivp(rhs,(a,b),init,method='DOP853',rtol=3e-13,atol=1e-24,max_step=.004)
    if not sol.success:
        raise RuntimeError(sol.message)
    return float(sol.y[3,-1]/provider.S(b-a))


def lens_response(provider,u,v,zl=.3,zs=1.,lens_kappa=.45,lens_shear=.35,lens_axis=.31):
    """Specified local lens Hessian; exact first derivative in fixed source chart."""
    segments=provider.three_segments(zl,zs)
    gam={name:np.sqrt(2.)*((r.g@u)*Z+(r.g@v)*X) for name,r in segments.items()}
    L=lens_kappa*np.eye(2)+lens_shear*(np.cos(2*lens_axis)*Z+np.sin(2*lens_axis)*X)
    F=gam['ol']+gam['os']-gam['ls']
    dA=-(gam['os']-gam['ls'])@L+L@gam['ol']
    first=skew_coefficient(dA)
    h=1e-2
    def exact(e):
        m={key:np.eye(2)-e*g for key,g in gam.items()}
        return np.eye(2)-np.linalg.solve(m['os'],m['ls'])@L@m['ol']
    numeric=(skew_coefficient(exact(h))-skew_coefficient(exact(-h)))/(2*h)
    # This symmetric metric relates the lens equation to the Fermat Hessian.
    Af=np.eye(2)-L
    fermat_skew=skew_coefficient(dA-F@Af)
    delay_plus=np.sqrt(2.)*(segments['os'].g-segments['ol'].g)@u
    delay_cross=np.sqrt(2.)*(segments['os'].g-segments['ol'].g)@v
    return {'z_l':zl,'z_s':zs,'reduced_local_hessian':L.tolist(),
            'Gamma':{k:x.tolist() for k,x in gam.items()},
            'lens_jacobian_rotation_first_order':first,
            'centered_finite_difference':numeric,'finite_difference_absolute_error':abs(numeric-first),
            'Fermat_weighted_jacobian_skew_first_order':fermat_skew,
            'nodal_SIS_fractional_delay_cos2phi':float(delay_plus),
            'nodal_SIS_fractional_delay_sin2phi':float(delay_cross)}


def admissibility(provider,u,v):
    """Finite domain samples and interval-independent harmonic bounds.

    Sampled numbers are not interval certificates or microscopic admission.
    """
    ns=np.linspace(-np.log(3.1),0.,161)
    condA=[];eigM=[];condB=[]
    import action_native_matter_n2 as an
    for N in ns:
        y=provider.background.sol(N)
        A=an.action_blocks(N,y)[0]
        M=an.reduced_blocks(N,y)[0]
        condA.append(np.linalg.cond(A));eigM.append(np.linalg.eigvalsh(M)[0])
    # |Q_+|,|Q_cross| <= N/sqrt(2), no angular sampling required.
    upper=[]
    anchor_states=np.array([u,v])
    for rows in provider.row_samples:
        vals=rows@anchor_states.T
        upper.append(provider.normalization/np.sqrt(2.)*np.sum(abs(vals),axis=1))
    return {'sample_count':len(ns),'max_auxiliary_condition':float(max(condA)),
            'min_reduced_kinetic_eigenvalue':float(min(eigM)),
            'sampled_global_potential_bound_Phi_Psi':np.max(upper,axis=0)[:2].tolist(),
            'sampled_global_bound_all_Newtonian_rows':np.max(upper,axis=0).tolist(),
            'physical_state_selection':False,'continuum_stability_proved':False}


def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    p=AngularOpticalProvider()
    # Declared coordinate probes: two distinct density harmonics, no data fit.
    u=np.array([0.,0.,.001,0.,0.,0.])
    v=np.array([0.,0.,0.,.001,0.,0.])
    configs=[(0.,.6),(0.,1.),(.3,1.),(0.,1.5),(0.,2.)]
    records=[]
    for za,zb in configs:
        B,G,sol=wedge_matrix(p,za,zb)
        val=float(u@B@v)
        records.append({'z_a':za,'z_b':zb,'B':B.tolist(),'G':G.tolist(),
                        'skew_B_error':float(np.max(abs(B+B.T))),
                        'singular_values_coordinate_dependent':np.linalg.svd(B,compute_uv=False).tolist(),
                        'omega2':val})
    B=np.array(records[1]['B']);omega=float(u@B@v)
    q1=ordered_quadrature(p,0.,1.,401)
    q2=ordered_quadrature(p,0.,1.,801)
    # Symmetric amplitude projection cancels odd orders and exposes O(eps^4).
    checks=[]
    for amp in [1.,2.,4.,8.,16.]:
        plus=finite_map(p,0.,1.,u,v,amp)
        minus=finite_map(p,0.,1.,u,v,-amp)
        even=(skew_coefficient(plus)+skew_coefficient(minus))/(2*amp*amp)
        checks.append({'amplitude_scale':amp,'even_rotation_over_scale_squared':even,
                       'absolute_coefficient_error':abs(even-omega)})
    null=finite_map(p,0.,1.,u,2*u,8.)
    reverse=finite_map(p,0.,1.,v,u,8.)
    reversed_even_matrix=(skew_coefficient(reverse)+skew_coefficient(finite_map(p,0.,1.,v,u,-8.)))/(2*64)
    reversed_even=(finite_rotation_components(p,0.,1.,v,u,8.)+
                   finite_rotation_components(p,0.,1.,v,u,-8.))/(2*64)
    extra=lambda t:1e-7*(1+t)*(np.eye(2)+.3*Z+.2*X)
    extra_checks=[]
    for amp in [1.,4.,16.]:
        even=(skew_coefficient(finite_map(p,0.,1.,u,v,amp,extra))+
              skew_coefficient(finite_map(p,0.,1.,u,v,-amp,extra)))/(2*amp*amp)
        extra_checks.append({'scale':amp,'coefficient':even,'difference':even-omega})
    refined=AngularOpticalProvider(grid_size=1601,prop_rtol=2e-12,prop_atol=2e-14,prop_max_step=.005)
    Br,_,_=wedge_matrix(refined,0.,1.,max_step=.003,rtol=2e-12,atol=2e-18)
    # Include every basis pair; do not select a pair for agreement with data.
    pair_table=[{'i':i,'j':j,'omega2_for_1e_minus3_each':float(B[i,j]*1e-6)}
                for i in range(6) for j in range(i+1,6)]
    momentum=np.array([0.,.001,0.,0.,0.,0.])
    momentum_omega=float(u@B@momentum)
    momentum_checks=[]
    for amp in [1.,4.,16.]:
        even=(skew_coefficient(finite_map(p,0.,1.,u,momentum,amp))+
              skew_coefficient(finite_map(p,0.,1.,u,momentum,-amp)))/(2*amp*amp)
        momentum_checks.append({'scale':amp,'coefficient':even,'difference':even-momentum_omega})
    b=p.chi_of_z(1.)
    c=np.sqrt(2.)*p.normalization*p.K
    ts=np.linspace(0,b,1601)
    tide_norm=max(c*np.hypot(p.weyl_rows(t)@u,p.weyl_rows(t)@v) for t in ts)
    nu=float(tide_norm*b*b)
    import math
    # S_K(r)<=r before the first conjugate point gives a Volterra majorant.
    remainder_even=float(b/p.S(b)*sum(nu**n/math.factorial(2*n+1) for n in range(4,20,2)))
    result={'schema':'BHSM_STATE_ORDERED_ROTATION_V1','status':'CONDITIONAL_R1_RESPONSE_NOT_MICROSCOPIC_PREDICTION',
            'anchor_plus':u.tolist(),'anchor_cross':v.tolist(),'anchor_z':2.1,
            'K':p.K,'normalization':p.normalization,'units':'length c/H0; anchors in inherited normalized harmonic coordinates',
            'convention':'omega=(D12-D21)/(2*d); J=[[0,1],[-1,0]]',
            'segments':records,'provider_audit':p.audit_temporal(),
            'all_coordinate_pairs_at_z1':pair_table,
            'matter_plus_momentum_cross':{'u':u.tolist(),'v':momentum.tolist(),
                 'omega2':momentum_omega,'finite_checks':momentum_checks,
                 'admissibility':admissibility(p,u,momentum)},
            'optical_control':{'sampled_tidal_norm_max':float(tide_norm),'sampled_nu':nu,
                 'even_remainder_majorant_using_sampled_max':remainder_even,
                 'is_interval_certificate':False},
            'quadrature_401_vs_ode_max_abs':float(np.max(abs(q1-B))),
            'quadrature_801_vs_ode_max_abs':float(np.max(abs(q2-B))),
            'quadrature_error_omega':float(abs(u@(q2-B)@v)),
            'refined_B_max_abs_difference':float(np.max(abs(Br-B))),
            'refined_omega_difference':float(abs(u@(Br-B)@v)),
            'finite_ode_checks':checks,'common_profile_finite_rotation':skew_coefficient(null),
            'swap_state_omega2':reversed_even,
            'swap_state_direct_matrix_subtraction':reversed_even_matrix,
            'swap_state_matrix_subtraction_error':float(abs(reversed_even_matrix+omega)),
            'added_symmetric_second_order_tide_checks':extra_checks,
            'admissibility':admissibility(p,u,v),'strong_lens':lens_response(p,u,v),
            'limitations':['chosen independent states; not a physical preparation or amplitude selection',
                           'parallel-screen response, not source-orientation independent astronomical rotation',
                           'no Berger squashed-spacetime calculation or preferred Hopf structure selected',
                           'finite ODE includes only specified first-order tides; full nonlinear metric not supplied']}
    (out/'rotation_response.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['status','provider_audit','quadrature_error_omega',
          'refined_omega_difference','finite_ode_checks','common_profile_finite_rotation','admissibility','strong_lens']},indent=2))


if __name__=='__main__':
    main()
