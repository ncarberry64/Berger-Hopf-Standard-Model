"""Continue the inherited daughter collar, retaining its nodal interfaces.

This is a muon-checkpoint realization, not a new child-observable framework.
The old geodesic is read, never reintegrated. New transverse/transport data
on that segment use its explicit Hermite reconstruction. All errors of that
reconstruction remain separate from continuum/history errors.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq


def _product(a, b):
    x, dx, ddx = a
    y, dy, ddy = b
    return (x*y, dx*y+x*dy,
            ddx*y+x*ddy+np.outer(dx,dy)+np.outer(dy,dx))


class SavedNodalMetric:
    """Actual products of bilinear nu/C/shift; analytic cell derivatives."""
    def __init__(self, geometry):
        self.times = np.asarray(geometry['proper_times'])
        self.rho = np.asarray(geometry['rho'])
        self.fields = np.array([geometry[k] for k in
            ('proper_lapse', 'C_rho', 'proper_shift_rho', 'base_radius')])

    def locate(self, X):
        t,r = X
        if not (self.times[0] <= t <= self.times[-1] and
                self.rho[0] <= r <= self.rho[-1]):
            raise ValueError('outside retained metric; no extrapolated physical point')
        return (min(max(np.searchsorted(self.times,t,side='right')-1,0),len(self.times)-2),
                min(max(np.searchsorted(self.rho,r,side='right')-1,0),len(self.rho)-2))

    def jet(self, X, cell):
        """Cell polynomial may serve internal RK stages; outputs stop at faces."""
        t,r = X; it,ir = cell
        dt,dr = self.times[it+1]-self.times[it], self.rho[ir+1]-self.rho[ir]
        a,b = (t-self.times[it])/dt, (r-self.rho[ir])/dr
        z = self.fields[:,it:it+2,ir:ir+2]
        values = (1-a)*((1-b)*z[:,0,0]+b*z[:,0,1])+a*((1-b)*z[:,1,0]+b*z[:,1,1])
        grad = np.array([((1-b)*(z[:,1,0]-z[:,0,0])+b*(z[:,1,1]-z[:,0,1]))/dt,
                         ((1-a)*(z[:,0,1]-z[:,0,0])+a*(z[:,1,1]-z[:,1,0]))/dr]).T
        hess = np.zeros((4,2,2))
        hess[:,0,1] = hess[:,1,0] = (z[:,1,1]-z[:,1,0]-z[:,0,1]+z[:,0,0])/(dt*dr)
        nu,C,zeta,radius = values
        scalar = [(values[i],grad[i],hess[i]) for i in range(4)]
        nn = _product(scalar[0],scalar[0]); cc = _product(scalar[1],scalar[1])
        cz = _product(scalar[1],scalar[2]); czcz = _product(cz,cz)
        ccz = _product(cc,scalar[2])
        entries = [[tuple(x-y for x,y in zip(nn,czcz)),tuple(-x for x in ccz)],
                   [tuple(-x for x in ccz),tuple(-x for x in cc)]]
        g = np.array([[entries[i][j][0] for j in range(2)] for i in range(2)])
        dg = np.array([[[entries[i][j][1][d] for j in range(2)] for i in range(2)] for d in range(2)])
        ddg = np.array([[[[entries[i][j][2][a,b] for j in range(2)] for i in range(2)] for b in range(2)] for a in range(2)])
        inv = np.linalg.solve(g,np.eye(2))
        dinv = np.array([-inv@dg[d]@inv for d in range(2)])
        Gamma = np.zeros((2,2,2)); dGamma = np.zeros((2,2,2,2))
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        h = dg[j,l,k]+dg[k,l,j]-dg[l,j,k]
                        Gamma[i,j,k] += inv[i,l]*h/2
                        for d in range(2):
                            dh = ddg[d,j,l,k]+ddg[d,k,l,j]-ddg[d,l,j,k]
                            dGamma[d,i,j,k] += (dinv[d,i,l]*h+inv[i,l]*dh)/2
        # Cartan convention: de^a+omega^a_b wedge e^b=0, signature +----.
        b0 = (grad[1,0]-zeta*grad[1,1]-C*grad[2,1])/nu
        omega01 = np.array([grad[0,1]/C+zeta*b0,b0])
        return dict(g=g,Gamma=Gamma,dGamma=dGamma,values=values,grad=grad,
                    omega01=omega01,cell=cell)


def phase_rhs(phase, jet):
    n = phase[2:4]
    return np.r_[n,-np.einsum('ijk,j,k->i',jet['Gamma'],n,n)]


def transverse_rhs(phase, V, jet):
    n = phase[2:4]; xi,eta = V[:2],V[2:]
    return np.r_[eta,
        -np.einsum('dijk,d,j,k->i',jet['dGamma'],xi,n,n)
        -2*np.einsum('ijk,j,k->i',jet['Gamma'],n,eta)]


def saltation(V, phase, old, new, axis):
    """Fixed-s transverse derivative, not derivative at each varied hit time."""
    n = phase[2:4]
    if abs(n[axis]) < 1e-12:
        raise ArithmeticError('grazing nodal face requires another justified chart')
    result = V.copy()
    delta_acc = phase_rhs(phase,new)[2:]-phase_rhs(phase,old)[2:]
    result[2:] += delta_acc*(V[axis]/n[axis])
    return result


def continue_saved_collar(geometry, saved, *, rtol=2e-10, atol=2e-12):
    """New transverse/transport/measure actions, then old-curve continuation.

    Stops at the first supplied-cache face. It does not turn that artificial
    face into a physical endpoint, or silently extend the tail metric.
    """
    metric = SavedNodalMetric(geometry)
    old_s = saved['s']; old_X = np.column_stack((saved['tau'],saved['rho']))
    old_n = np.column_stack((saved['tau_s'],saved['rho_s']))
    old_curve = CubicHermiteSpline(old_s,old_X,old_n)
    first = metric.jet(old_X[0],metric.locate(old_X[0]))
    wall_nu,wall_C,_,wall_r = first['values']
    wall_h = float(first['g'][0,0])
    V = np.array([1.,0.,0.,first['grad'][1,0]/wall_C**2])
    aux = np.r_[V,0.,0.]  # omega01 line integral and unnormalized I_part
    cuts = [(float(old_s[0]),None),(float(old_s[-1]),None)]
    for t in metric.times:
        if old_X[-1,0] < t < old_X[0,0]:
            cuts.append((brentq(lambda s:old_curve(s)[0]-t,old_s[0],old_s[-1],xtol=1e-15),0))
    cuts.sort()
    samples=[]; interfaces=[]; nfev=0; cached_defects=[]
    for ci in range(len(cuts)-1):
        sa,sb = cuts[ci][0],cuts[ci+1][0]
        cell = metric.locate(old_curve((sa+sb)/2))
        def rhs_old(s,a):
            X = old_curve(s); n = old_curve(s,1); phase=np.r_[X,n]
            j = metric.jet(X,cell)
            return np.r_[transverse_rhs(phase,a[:4],j),j['omega01']@n,np.sin(X[1]/2)**2]
        sol=solve_ivp(rhs_old,(sa,sb),aux,method='DOP853',rtol=rtol,atol=atol,dense_output=True,max_step=(sb-sa)/8)
        if not sol.success:raise ArithmeticError(sol.message)
        nfev+=sol.nfev
        nodes=old_s[(old_s>=sa)&(old_s<sb)]
        for s in nodes:
            phase=np.r_[old_curve(s),old_curve(s,1)]
            samples.append((float(s),phase,sol.sol(s),cell,0))
            j=metric.jet(phase[:2],cell)
            cached_defects.append((float(s),float(np.linalg.norm(old_curve(s,2)+np.einsum('ijk,j,k->i',j['Gamma'],phase[2:],phase[2:])))))
        aux=sol.y[:,-1]
        if ci+1<len(cuts)-1:
            phase=np.r_[old_curve(sb),old_curve(sb,1)]
            nextcell=metric.locate(old_curve((sb+cuts[ci+2][0])/2))
            before=aux[:4].copy()
            aux[:4]=saltation(aux[:4],phase,metric.jet(phase[:2],cell),metric.jet(phase[:2],nextcell),0)
            interfaces.append(dict(s=sb,axis=0,old_cell=list(map(int,cell)),new_cell=list(map(int,nextcell)),
                                   eta_jump=(aux[2:4]-before[2:4]).tolist(),old_segment=True))
    # All original phase points are reused; only subsequent phase is solved.
    phase=np.r_[old_X[-1],old_n[-1]]
    state=np.r_[phase,aux]; start=float(old_s[-1])
    cell=metric.locate(phase[:2]); maximum_end=start+0.2
    while True:
        def rhs(s,z):
            j=metric.jet(z[:2],cell)
            return np.r_[phase_rhs(z[:4],j),transverse_rhs(z[:4],z[4:8],j),
                         j['omega01']@z[2:4],np.sin(z[1]/2)**2]
        axes=[];events=[]
        for axis,grid in enumerate((metric.times,metric.rho)):
            if state[axis+2]>=0:
                raise ArithmeticError('unexpected turning direction; preserve it and implement matching before continuing')
            boundary=float(grid[cell[axis]])
            def event(s,z,axis=axis,boundary=boundary):return z[axis]-boundary
            event.terminal=True;event.direction=-1
            events.append(event);axes.append(axis)
        sol=solve_ivp(rhs,(start,maximum_end),state,method='DOP853',rtol=rtol,atol=atol,
                      events=events,max_step=2e-5,dense_output=True)
        if not sol.success:raise ArithmeticError(sol.message)
        nfev+=sol.nfev
        for s,z in zip(sol.t[:-1],sol.y.T[:-1]):samples.append((float(s),z[:4].copy(),z[4:].copy(),cell,1))
        end=float(sol.t[-1]);state=sol.y[:,-1].copy()
        hits=[i for i,e in enumerate(sol.t_events) if len(e)]
        if len(hits)!=1:raise ArithmeticError('no single transverse nodal exit; need full corner/turning handling')
        axis=hits[0]
        state[axis]=float((metric.times,metric.rho)[axis][cell[axis]])
        if cell[axis]==0:
            samples.append((end,state[:4].copy(),state[4:].copy(),cell,1));break
        nextcell=list(cell);nextcell[axis]-=1;nextcell=tuple(nextcell)
        before=state[4:8].copy()
        state[4:8]=saltation(state[4:8],state[:4],metric.jet(state[:2],cell),metric.jet(state[:2],nextcell),axis)
        interfaces.append(dict(s=end,axis=axis,old_cell=list(map(int,cell)),new_cell=list(map(int,nextcell)),
                               eta_jump=(state[6:8]-before[2:4]).tolist(),old_segment=False))
        cell=nextcell;start=end
    samples.sort(key=lambda a:a[0])
    ss=np.array([a[0] for a in samples]);ph=np.array([a[1] for a in samples]);auxs=np.array([a[2] for a in samples])
    jets=[metric.jet(p[:2],a[3]) for p,a in zip(ph,samples)]
    values=np.array([j['values'] for j in jets]);xi=auxs[:,:2]
    Delta=xi[:,0]*ph[:,3]-ph[:,2]*xi[:,1]
    J=values[:,0]*values[:,1]*values[:,3]**3*abs(Delta)/(np.sqrt(wall_h)*wall_r**3)
    normal=np.array([p[2:]@j['g']@p[2:] for p,j in zip(ph,jets)])
    orthogonal=np.array([v@j['g']@p[2:] for v,p,j in zip(xi,ph,jets)])
    xi_norm=np.array([v@j['g']@v for v,j in zip(xi,jets)])
    transverse=(values[:,0]*values[:,1]*Delta)**2
    arrays=dict(s=ss,tau=ph[:,0],rho=ph[:,1],tau_s=ph[:,2],rho_s=ph[:,3],
        tau_y=xi[:,0],rho_y=xi[:,1],tau_sy=auxs[:,2],rho_sy=auxs[:,3],
        Delta_X=Delta,J_c=J,omega01_line_integral=auxs[:,4],I_partial=auxs[:,5],
        normal_norm=normal,normal_transverse_pairing=orthogonal,transverse_norm=xi_norm,
        transverse_determinant_identity_residual=xi_norm-transverse,
        metric_cells=np.array([a[3] for a in samples]),phase_origin=np.array([a[4] for a in samples]),
        cached_curve_geodesic_defect=np.array(cached_defects))
    summary=dict(cache_exit_axis=axis,cache_exit_s=end,cache_exit_phase=state[:4].tolist(),
        cache_exit_transverse=state[4:8].tolist(),cache_exit_J=float(J[-1]),
        rho_range=[float(min(ph[:,1])),float(max(ph[:,1]))],
        time_range=[float(min(ph[:,0])),float(max(ph[:,0]))],
        minimum_abs_Delta=float(min(abs(Delta))),minimum_J=float(min(J)),
        maximum_unit_normal_residual=float(max(abs(normal+1))),
        maximum_orthogonality_residual=float(max(abs(orthogonal))),
        maximum_transverse_metric_identity_residual=float(max(abs(xi_norm-transverse))),
        maximum_cached_Hermite_geodesic_defect=float(max(a[1] for a in cached_defects)),
        I_partial=float(auxs[-1,5]),I_remainder=None,I_full=None,
        interfaces=interfaces,function_evaluations=nfev,rtol=rtol,atol=atol,
        cached_phase_reintegrated=False,wall_proper_time_coordinate=float(old_X[0,0]),
        scope='binary64 nodal metric and explicit cached-curve Hermite reconstruction; no rigorous ODE/continuum/history enclosure')
    return arrays,summary


def spin_transport(arrays,parent_gamma,gamma5):
    """Fixed-angle normal connection in the retained +---- Dirac carrier.

    Common-A has only angular components in this section, hence its pullback
    along this fixed-angle normal is zero. This does not discard angular
    outputs of the source. Spin boost is not an Euclidean unitary map.
    """
    G=np.asarray(parent_gamma);generator=G[0]@G[4]/2
    a=arrays['omega01_line_integral']
    U=np.cosh(a/2)[:,None,None]*np.eye(4)-2*np.sinh(a/2)[:,None,None]*generator
    PL=(np.eye(4)-gamma5)/2;PR=(np.eye(4)+gamma5)/2
    dirac=np.einsum('sji,jk,skl->sil',U.conj(),G[0],U)
    # A normal Spin(1,4) boost mixes the fixed Spin(1,3) chiral frame.
    # Transport the projectors, rather than claiming [U,gamma5]=0.
    inverse=np.cosh(a/2)[:,None,None]*np.eye(4)+2*np.sinh(a/2)[:,None,None]*generator
    PLe=U@PL@inverse;PRe=U@PR@inverse
    return dict(spin_transport=U,spin_transport_left=U@PL,spin_transport_right=U@PR,
                transported_chiral_left=PLe,transported_chiral_right=PRe,
                spin_transport_generator=generator),dict(
        Dirac_pairing_residual=float(np.max(abs(dirac-G[0]))),
        fixed_4D_chirality_mixing=float(np.max(abs(U@gamma5-gamma5@U))),
        transported_chiral_projector_residual=float(max(np.max(abs(PLe@PLe-PLe)),np.max(abs(PRe@PRe-PRe)),np.max(abs(PLe+PRe-np.eye(4))))),
        both_chiral_sectors_retained=True,SM_normal_pullback='zero in adopted angular section; internal I16 and family I3 remain symbolic',
        oriented_normal_gamma_plus='saved parent_gamma[4]',
        oriented_normal_gamma_minus='-saved parent_gamma[4]',
        uncomputed_source_transport_and_pairing_derivatives=True)


def prefix_coverage_enclosure(geometry, prefix_fields, tail_arrays, duration_upper):
    """Consume the inherited prefix in a thin-time Hamiltonian enclosure.

    p_rho'=1/2 (partial_rho g_ab) n^a n^b, g(n,n)=-1.
    A numerical strip is only a bootstrap enclosure, not a chosen collar.
    Arb bounds concern the binary64 nodal metric, not the continuum history.
    No interpolation in an invented or extended physical clock is needed:
    the inherited upper duration bounds every positive owned clock choice.
    """
    from flint import arb,ctx
    ctx.prec=192
    rho0=float(tail_arrays['rho'][-1]);n0=np.array([tail_arrays['tau_s'][-1],tail_arrays['rho_s'][-1]])
    grid=geometry['rho'];c=int(np.searchsorted(grid,rho0)-1)
    dr=float(grid[c+1]-grid[c]);x=float((rho0-grid[c])/dr)
    rho_width=1e-12;momentum_width=1e-12
    fields=np.array([prefix_fields[k][:,c:c+2] for k in ('proper_lapse','C_rho','proper_shift_rho','base_radius')])
    slopes=(fields[:,:,1]-fields[:,:,0])/dr
    centers=(1-x)*fields[:,:,0]+x*fields[:,:,1]
    x_ball=(arb(rho0)-arb(float(grid[c])))/(arb(float(grid[c+1]))-arb(float(grid[c])))
    dr_ball=arb(float(grid[c+1]))-arb(float(grid[c]))
    exact_centers=[[arb(float(a))*(1-x_ball)+arb(float(b))*x_ball for a,b in f] for f in fields]
    exact_slopes=[[(arb(float(b))-arb(float(a)))/dr_ball for a,b in f] for f in fields]
    def interval(lo,hi):
        a,b=arb(float(lo)),arb(float(hi));return (a+b)/2+arb(0,((b-a)/2).upper())
    def hull(balls):
        lo=min(float(np.nextafter(float(a.lower()),-np.inf)) for a in balls)
        hi=max(float(np.nextafter(float(a.upper()),np.inf)) for a in balls)
        return interval(lo,hi)
    def envelope(row,der):
        return hull([v+arb(0,abs(d).upper()*arb(rho_width)) for v,d in zip(row,der)])
    nu,C,zeta,r=[envelope(exact_centers[i],exact_slopes[i]) for i in range(4)]
    nur,Cr,zr,rr=[hull(a) for a in exact_slopes]
    # Match the tail's actual conormal momentum; both caches use rho=2chi.
    tail_names=('proper_lapse','C_rho','proper_shift_rho')
    tail_ball=[arb(float(geometry[k][0,c]))*(1-x_ball)+arb(float(geometry[k][0,c+1]))*x_ball for k in tail_names]
    tail=np.array([float(a.mid()) for a in tail_ball])
    nt0,nr0=map(arb,map(float,n0));nub,Cb,zb=tail_ball
    p0=-Cb*Cb*(nr0+zb*nt0)
    kappa=(p0/Cb)**2-(nub*nt0)**2  # retain old norm, do not refit the tangent
    p=p0+arb(0,arb(momentum_width))
    margin=p*p/(C*C)-kappa
    if not margin>0:raise ArithmeticError('normal time branch cannot be certified on the inherited prefix strip')
    nt=-margin.sqrt()/nu
    nr=-p/(C*C)-zeta*nt
    g00r=2*nu*nur-2*C*Cr*zeta*zeta-2*C*C*zeta*zr
    g01r=-2*C*Cr*zeta-C*C*zr;g11r=-2*C*Cr
    force=(g00r*nt*nt+2*g01r*nt*nr+g11r*nr*nr)/2
    dt=arb(float(duration_upper));min_nt=abs(nt).lower()
    ds=(dt/min_nt).upper();delta_r=(abs(nr).upper()*ds).upper();delta_p=(abs(force).upper()*ds).upper()
    if not (delta_r<arb(rho_width) and delta_p<arb(momentum_width)):
        raise ArithmeticError('prefix enclosure failed; retain explicit first-exit problem')
    # Tighten the bootstrap to its actual consumed displacement/error scale.
    p_tight=p0+arb(0,delta_p)
    tight_fields=[]
    for i in range(4):
        base=hull(exact_centers[i])
        tight_fields.append(base+arb(0,abs([nur,Cr,zr,rr][i]).upper()*delta_r))
    nu_t,C_t,z_t,r_t=tight_fields
    nt_t=-(p_tight*p_tight/(C_t*C_t)-kappa).sqrt()/nu_t
    nr_t=-p_tight/(C_t*C_t)-z_t*nt_t
    # Constant-p_rho representatives are diagnostic centers within the above
    # enclosure; their radial drift is not rounded into an invented new path.
    p_float=float(p0.mid());nt_nodes=-np.sqrt((p_float/centers[1])**2-float(kappa.mid()))/centers[0]
    nr_nodes=-p_float/centers[1]**2-centers[2]*nt_nodes
    root_norm=np.sqrt(float(kappa.mid()))
    rapidity=np.arcsinh(centers[0]*nt_nodes/root_norm)
    rapidity_start=np.arcsinh(tail[0]*n0[0]/root_norm)
    omega_nodes=float(tail_arrays['omega01_line_integral'][-1])+rapidity-rapidity_start
    # A small norm residual in reused tail data contributes to the exact
    # mass-shell momentum readout; it is not concealed as a prefix error.
    normal_defect=abs(1+(tail[0]*n0[0])**2-(p_float/tail[1])**2)
    def enc(a):return dict(interval=[float(np.nextafter(float(a.lower()),-np.inf)),
                                    float(np.nextafter(float(a.upper()),np.inf))],arb=str(a))
    arrays=dict(prefix_radial_field_centers=centers,prefix_field_rho_slopes=slopes,
        prefix_rho_reference=np.array(rho0),prefix_tau_s_constant_momentum_centers=nt_nodes,
        prefix_rho_s_constant_momentum_centers=nr_nodes,prefix_omega01_constant_momentum_centers=omega_nodes)
    result=dict(method='Hamiltonian first-exit enclosure using actual prefix nodal coefficients and inherited positive proper-clock duration',
        rho_at_cut=rho0,radial_cell=c,normal_proper_length_upper=enc(ds),
        radial_displacement_upper=enc(delta_r),radial_momentum_change_upper=enc(delta_p),
        tau_s_enclosure=enc(nt_t),rho_s_enclosure=enc(nr_t),
        p_rho_initial=enc(p0),preserved_norm_kappa=enc(kappa),prefix_margin=enc(margin),
        bootstrap_rho_width=rho_width,bootstrap_momentum_width=momentum_width,
        bootstrap_closed=True,normal_turning_excluded_in_nodal_strip=True,
        partial_normalization_addition_upper=enc(ds),
        reused_tail_norm_defect=float(normal_defect),
        prefix_state_geometry_reconstruction_error=None,
        center_interpolation_roundoff='Arb arithmetic on exact binary64 nodal coefficients/grid; continuum/input reconstruction error excluded',
        prefix_transverse_J_evaluated=False,
        prefix_transport='rapidity centers evaluated with momentum error enclosure; full source/pairing/domain jet remains unevaluated',
        reached_inherited_E1_reset=True,
        reset_scope='outgoing daughter patch reaches actual inherited reset; no pre-E0 arm and no assertion of physical absence',
        first_needed_patch_action='compatible source-restricted collar/half-density pullback beyond this evaluated Gaussian patch; reset compatibility applies if the chosen owned route crosses E1')
    return arrays,result
