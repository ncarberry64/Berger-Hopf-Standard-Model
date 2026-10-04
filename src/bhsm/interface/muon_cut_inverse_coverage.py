"""Source-directed cut range of the inherited muon normal realization."""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from flint import arb,ctx
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0

from bhsm.interface.muon_collar_source_coverage import (
    SavedNodalMetric,phase_rhs,transverse_rhs,saltation)


def ball_interval(lo,hi):
    a,b=arb(float(lo)),arb(float(hi))
    return (a+b)/2+arb(0,((b-a)/2).upper())


def hull(balls):
    lo=min(float(np.nextafter(float(a.lower()),-np.inf)) for a in balls)
    hi=max(float(np.nextafter(float(a.upper()),np.inf)) for a in balls)
    return ball_interval(lo,hi)


def encoded(a):
    return dict(arb=str(a),interval=[float(np.nextafter(float(a.lower()),-np.inf)),
                                   float(np.nextafter(float(a.upper()),np.inf))])


def tail_connection_boxes(geometry,*,width=0.02):
    """Whole-cell Arb enclosures, not extrema at sampled corners.

    rho is restricted to the specified outer-cell bootstrap strip. The
    actual products defining g are retained through Cartan's a,b equations.
    """
    ctx.prec=192
    times=geometry['proper_times'];grid=geometry['rho'];wall=float(grid[-1])
    if width>=float(grid[-1]-grid[-2]):raise ValueError('strip must remain in outer nodal cell')
    records=[];r=arb(wall)+arb(0,arb(width)/2)-arb(width)/2
    ir=len(grid)-2;dr=arb(float(grid[-1]))-arb(float(grid[-2]));b=(r-arb(float(grid[-2])))/dr
    tfrac=ball_interval(0,1)
    for it in range(len(times)-1):
        dt=arb(float(times[it+1]))-arb(float(times[it]))
        values=[];tr=[];rr=[]
        for key in ('proper_lapse','C_rho','proper_shift_rho'):
            z=[[arb(float(geometry[key][it+i,ir+j])) for j in range(2)] for i in range(2)]
            val=(1-tfrac)*((1-b)*z[0][0]+b*z[0][1])+tfrac*((1-b)*z[1][0]+b*z[1][1])
            # Tighten the value by the convex hull of the actual strip
            # endpoints, avoiding cancellation of dependent t and 1-t.
            values.append(hull([z[i][0]*(1-be)+z[i][1]*be for i in range(2) for be in [b.lower(),b.upper()]]))
            tr.append(hull([((1-be)*(z[1][0]-z[0][0])+be*(z[1][1]-z[0][1]))/dt for be in [b.lower(),b.upper()]]))
            rr.append(hull([(z[i][1]-z[i][0])/dr for i in range(2)]))
        nu,C,zeta=values;nur,Cr,zr=rr;Ct=tr[1]
        a=nur/(nu*C);bb=(Ct-zeta*Cr-C*zr)/(nu*C)
        if not (nu>0 and C>0):raise ArithmeticError('Lorentz frame not certified on strip')
        records.append(dict(cell=it,nu=encoded(nu),C=encoded(C),zeta=encoded(zeta),a=encoded(a),b=encoded(bb)))
    def merged(key):return hull([ball_interval(*r[key]['interval']) for r in records])
    return {k:merged(k) for k in ('nu','C','zeta','a','b')},records


def prefix_owned_connection_box(states,geometry,*,width=0.02):
    """New contracted time jet needed for prefix-born wall branches.

    Never infer C_tau=0 from sub-ulp configuration motion. The same action
    gives d_tau log C=(qdot0+udot+wdot)/N_boundary, because the physical
    boundary attachment cancels ub/vb in log Rcap. No H substitution.
    Inputs are the already retained prefix states; no old hull/bound is rerun.
    """
    ctx.prec=192
    q=states[:,:37];v=states[:,37:74];m=states[:,74:]
    boxes=lambda z:[ball_interval(float(np.nextafter(min(z[:,i]),-np.inf)),float(np.nextafter(max(z[:,i]),np.inf))) for i in range(z.shape[1])]
    qb,vb,mb=map(boxes,(q,v,m))
    r=ball_interval(float(geometry['rho'][-1]-width),float(geometry['rho'][-1]))
    ck=[(2*k*r).cos() for k in range(1,13)];sk=[(2*k*r).sin() for k in range(1,13)]
    cj=[(2*j*r).cos() for j in range(12)];sj=[(2*j*r).sin() for j in range(12)]
    sinr=r.sin();cosr=r.cos();window=sinr*sinr
    nb=sum((mb[k-1]*((-1)**k) for k in range(1,13)),arb(0)).exp()
    nu=(sum((mb[k-1]*(ck[k-1]-((-1)**k)) for k in range(1,13)),arb(0))).exp()
    L=(vb[0]+sum((vb[k]*ck[k-1] for k in range(1,13)),arb(0))+
       window*sum((vb[13+j]*cj[j] for j in range(12)),arb(0)))/nb
    logCr=(sum((-2*k*qb[k]*sk[k-1] for k in range(1,13)),arb(0))+
        2*sinr*cosr*sum((qb[13+j]*cj[j] for j in range(12)),arb(0))+
        window*sum((-2*j*qb[13+j]*sj[j] for j in range(12)),arb(0)))
    coeff=sum((mb[12+j]*cj[j] for j in range(12)),arb(0))
    coeffr=sum((-2*j*mb[12+j]*sj[j] for j in range(12)),arb(0))
    zeta=2*(2*r).sin()*coeff/nb
    zr=4*(2*r).cos()*coeff/nb+2*(2*r).sin()*coeffr/nb
    # Rcap=RADIUS0 exp(q0) follows from boundary_log_radius AND the
    # Rcap=2 R4 exp(-ub) sqrt(cosh(2vb)) attachment. The reference
    # normalization enters through that identity, never as a new radius.
    C=(arb(RADIUS0)/2)*(qb[0]+sum((qb[k]*ck[k-1] for k in range(1,13)),arb(0))+
       window*sum((qb[13+j]*cj[j] for j in range(12)),arb(0))).exp()
    a=sum((-2*k*mb[k-1]*sk[k-1] for k in range(1,13)),arb(0))/C
    bb=(L-zeta*logCr-zr)/nu
    return dict(nu=nu,C=C,zeta=zeta,a=a,b=bb,owned_logC_tau=L),dict(
        derivative_equation='partial_tau log C_rho=(qdot0+u_dot+sin(rho)^2*w_coeff_dot)/N_boundary',
        source='current_parent_fields and boundary_log_radius attachment, v15.81 physical velocities; same prefix state arrays',
        C_tau_inferred_from_rounded_constant_nodes=False,
        scope='Arb bounds on supplied prefix state/velocity/multiplier hull; unsampled continuum/history error separate')


def family_range_certificate(geometry,tail_box,prefix_box,*,prefix_duration_upper,width=0.02,theta_max=0.1):
    """A first-exit range theorem for every wall time in the retained domain.

    Inward orthonormal n=(-sinh(theta),-cosh(theta)), theta(0)=0:
      tau'=-sinh(theta)/nu,
      rho'=-cosh(theta)/C+zeta*sinh(theta)/nu,
      theta'=a*sinh(theta)+b*cosh(theta).
    The inequalities apply to every nodal cell; derivative jumps do not
    invalidate them. They also include any fold in the family parametrization.
    """
    ctx.prec=192;T=arb(float(geometry['proper_times'][-1]));Theta=arb(theta_max)
    def limits(box):
        A=abs(box['a']).upper();B0=(box['b'].lower()-A*Theta.sinh()).lower()
        B1=(A*Theta.sinh()+box['b'].upper()*Theta.cosh()).upper()
        if not B0>0:raise ArithmeticError('rapidity may turn; need explicit branch subdivision')
        return B0,B1
    B0,B1=limits(tail_box);P0,P1=limits(prefix_box)
    nu=tail_box['nu'];C=tail_box['C'];z=tail_box['zeta']
    radial_upper=(-1/C.upper()+abs(z).upper()*Theta.sinh()/nu.lower()).upper()
    pradial_upper=(-1/prefix_box['C'].upper()+abs(prefix_box['zeta']).upper()*Theta.sinh()/prefix_box['nu'].lower()).upper()
    if not (radial_upper<0 and pradial_upper<0):
        raise ArithmeticError('inward-pointing wall/strip premise not certified')
    S=(2*nu.upper()*T/B0).sqrt().upper()
    speed=(Theta.cosh()/C.lower()+abs(z).upper()*Theta.sinh()/nu.lower()).upper()
    drop=(speed*S).upper();theta_bound=(B1*S).upper()
    if not (drop<arb(width) and theta_bound<Theta):
        raise ArithmeticError('first-exit bootstrap does not close; no range exclusion claimed')
    # A new family bound for prefix-born n_tau=0 curves, NOT a refinement
    # of the previous 5.275e-26 bound for the single already-transverse curve.
    Tp=arb(float(prefix_duration_upper));pn=prefix_box['nu'];pc=prefix_box['C'];pz=prefix_box['zeta']
    Sp=(2*pn.upper()*Tp/P0).sqrt().upper()
    Vp=(Theta.cosh()/pc.lower()+abs(pz).upper()*Theta.sinh()/pn.lower()).upper()
    dp=(Vp*Sp).upper();tp=(P1*Sp).upper()
    if not (drop+dp<arb(width) and theta_bound+tp<Theta):
        raise ArithmeticError('prefix-to-E1 first-exit bootstrap does not close')
    rho_lower=(arb(float(geometry['rho'][-1]))-drop).lower()
    return dict(wall_tail_interval=[0.,float(T)],rho_hit_enclosure=encoded(ball_interval(float(np.nextafter(float(rho_lower),-np.inf)),float(geometry['rho'][-1]))),
        all_tail_wall_times_enclosed=True,normal_length_upper=encoded(S),radial_drop_upper=encoded(drop),
        rapidity_upper=encoded(theta_bound),rapidity_bootstrap=theta_max,radial_strip=width,
        tail_rapidity_rate_lower=encoded(B0),tail_rapidity_rate_upper=encoded(B1),
        tail_radial_velocity_upper=encoded(radial_upper),prefix_radial_velocity_upper=encoded(pradial_upper),
        prefix_rapidity_rate_lower=encoded(P0),prefix_rapidity_rate_upper=encoded(P1),
        prefix_family_length_upper=encoded(Sp),prefix_family_radial_drop_upper=encoded(dp),
        prefix_family_rapidity_increment_upper=encoded(tp),prefix_duration_upper=prefix_duration_upper,
        prefix_family_bound_is_old_single_curve_bound=False,
        prefix_born_wall_branches='nonpositive initial tau and strictly decreasing tau after s>0; no future-directed cut hit before E1',
        at_y_zero='grazing wall contact; implicit boundary limit, no division by tau_s',
        uniqueness='one transverse inward cut hit for each tail y>0; after the cut tau stays decreasing on the inherited prefix',
        possible_family_focal_points='do not affect this phase/image enclosure; no global chart-rank theorem asserted',
        oriented_sectors='inward geometric sheet; simultaneous s,n reversal is a reparametrization only; independent physical strata are not identified; LR carriers remain retained',
        ODE_replay_used_for_proof=False,old_prefix_bound_refined=False,
        scope='rigorous coefficient-box first-exit range in the declared tail nodal metric and supplied owned prefix-jet hull; continuum/history error unevaluated')


def evaluate_hit(geometry,y,*,s_upper):
    """A source-directed wall-parameter branch application, with saltation.

    y is inside the already proven physical range. This does not inspect an
    arbitrary normal curve or use a linear slope as an inverse certificate.
    """
    metric=SavedNodalMetric(geometry);wall=float(metric.rho[-1]);y=float(y)
    if not 0<y<=float(metric.times[-1]):raise ValueError('only transverse physical tail-wall branch')
    it=min(max(int(np.searchsorted(metric.times,y,side='left'))-1,0),len(metric.times)-2);cell=(it,len(metric.rho)-2)
    first=metric.jet([y,wall],cell);C=first['values'][1]
    state=np.r_[y,wall,0.,-1/C,1.,0.,0.,first['grad'][1,0]/C**2,0.,0.]
    current=0.;samples=[];interfaces=[];evaluations=0
    while True:
        def rhs(s,z):
            j=metric.jet(z[:2],cell)
            return np.r_[phase_rhs(z[:4],j),transverse_rhs(z[:4],z[4:8],j),
                         j['omega01']@z[2:4],np.sin(z[1]/2)**2]
        boundary=float(metric.times[cell[0]])
        def time_face(s,z):return z[0]-boundary
        time_face.terminal=True;time_face.direction=-1
        def radial_face(s,z):return z[1]-float(metric.rho[cell[1]])
        radial_face.terminal=True;radial_face.direction=-1
        sol=solve_ivp(rhs,(current,float(s_upper)),state,method='DOP853',rtol=2e-10,atol=2e-12,
                      max_step=2e-5,events=[time_face,radial_face])
        if not sol.success:raise ArithmeticError(sol.message)
        evaluations+=sol.nfev
        samples.extend((float(s),z.copy(),cell) for s,z in zip(sol.t[:-1],sol.y.T[:-1]))
        end=float(sol.t[-1]);state=sol.y[:,-1].copy()
        if len(sol.t_events[1]):raise ArithmeticError('radial bootstrap contradicted by numerical branch; retain discrepancy')
        if not len(sol.t_events[0]):raise ArithmeticError('certified event not found within bound; retain discrepancy')
        state[0]=boundary
        if cell[0]==0:
            samples.append((end,state.copy(),cell));break
        nextcell=(cell[0]-1,cell[1]);before=state[4:8].copy()
        state[4:8]=saltation(state[4:8],state[:4],metric.jet(state[:2],cell),metric.jet(state[:2],nextcell),0)
        interfaces.append(dict(s=end,old_cell=list(cell),new_cell=list(nextcell),jump=(state[4:8]-before).tolist()))
        cell=nextcell;current=end
    X=state[:2];n=state[2:4];xi=state[4:6];Delta=xi[0]*n[1]-n[0]*xi[1]
    if abs(n[0])<1e-10:
        raise ArithmeticError('transverse quotient not justified; use implicit branch relation')
    dsdy=-xi[0]/n[0];slope=xi[1]-n[1]*xi[0]/n[0]
    phase=np.array([a[1] for a in samples]);ss=np.array([a[0] for a in samples])
    return dict(s=ss,phase=phase,metric_cells=np.array([a[2] for a in samples])),dict(
        y=y,s0=end,R_hit=float(X[1]),tau_s=float(n[0]),Delta_X=float(Delta),
        ds0_dy=float(dsdy),dR_hit_dy=float(slope),determinant_slope=float(-Delta/n[0]),
        interfaces=interfaces,function_evaluations=evaluations,
        classification='new numerical endpoint on the physical cut-intersection branch; global range certificate independent of ODE errors',
        absolute_ODE_error_bound=None,normalization_integral_partial=float(state[9]),normalization_full=None)


def retained_radial_density_conversion(geometry,pairing):
    """Evaluate the geometric-L2 correction to the retained radial route.

    This is not an assertion that radial and Gaussian inclusions intertwine
    the same Dirac/domain. It identifies a computable part of that matching
    at the actual saved source nodes, without a new profile or normalization.
    """
    rho=np.array(pairing['gauss_rho']);cells=np.array(pairing['gauss_cells'],int)
    grid=geometry['rho'];width=np.diff(grid)[cells];x=(rho-grid[cells])/width
    def interp(k):
        z=geometry[k][0];return z[cells]*(1-x)+z[cells+1]*x
    def derivative(k):
        z=geometry[k][0];return (z[cells+1]-z[cells])/width
    nu,C,r=map(interp,('proper_lapse','C_rho','base_radius'))
    nu_r,r_r=map(derivative,('proper_lapse','base_radius'))
    nuw=float(geometry['proper_lapse'][0,-1]);rw=float(geometry['base_radius'][0,-1])
    Jr=(r/rw)**3;Jv=nu/nuw*Jr;conversion=np.sqrt(nuw/nu)
    h4rad=3*r_r/(2*C*r);delta=nu_r/(2*C*nu);h4cur=h4rad+delta
    log_u_rad_r=-3*r_r/(2*r)+.5/np.tan(rho/2)
    log_u_vol_r=log_u_rad_r-nu_r/(2*nu)
    # This radial mass coefficient is a candidate-route identity only,
    # never substituted for the adopted Gaussian m_eta along X.
    m_rad=-.5/(C*np.tan(rho/2))
    residual=log_u_vol_r/C+h4cur+m_rad
    arrays=dict(gauss_rho=rho,J_rad=Jr,J_vol=Jv,u_vol_over_u_rad=conversion,
        delta_h4=delta,radial_candidate_normal_cancellation=residual,
        temporal_principal_ratio=nuw/nu,
        normalization_density_conversion_residual=Jv*conversion**2-Jr)
    return arrays,dict(
        producer='v14.45, v15.76 shell_geometry, v15.82 regular_einstein_cartan_kernel',
        consumer='current canonical Dirac body and AE4 geometric-L2 pairing',
        equations=['J_vol=(nu/nu_wall) J_rad','u_vol=sqrt(nu_wall/nu) u_rad',
            'h4_current=h4_rad+(partial_rho log nu)/(2C)',
            '(partial_rho log u_vol)/C+h4_current+m_eta_rad=0'],
        delta_h4_range=[float(min(delta)),float(max(delta))],
        temporal_principal_ratio_range=[float(min(nuw/nu)),float(max(nuw/nu))],
        max_normal_cancellation_residual=float(max(abs(residual))),
        max_pairing_density_residual=float(max(abs(arrays['normalization_density_conversion_residual']))),
        normalization_full_evaluated=False,Gaussian_m_eta_replaced=False,
        same_owner_inclusion_intertwining_proved=False,
        numerical_scope='binary64 pointwise arithmetic on actual saved Gauss source nodes; no quadrature/tail/domain certificate',
        remaining_equation='retain time/shift/Spin x SM and connected terms in current D5 W_rad, and match the inherited trace/reset domain before using it as W_eta')
