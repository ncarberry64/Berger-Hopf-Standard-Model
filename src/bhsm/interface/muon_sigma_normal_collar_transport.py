"""Sigma-normal characteristic, density and analytic source-dual transport."""
from __future__ import annotations
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.integrate import solve_ivp
from scipy.special import gammaln
from .muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt,_response,_compose,_sin,anchored_holomorphic_chart
from .muon_holomorphic_d5_trace_action import d5_sigma_foliation_eta,d5_sigma_normal_flow_germ
from .muon_parent_retarded_hypercharge import WALL,ALPHA
from .muon_parent_maxwell_full_weak import M


class CanonicalC1History:
    """Original position/velocity and algebraic nodal jets, no extrapolation.

    Position Hermite interpolation supplies its OWN velocity and
    acceleration. Algebraic fields use their supplied canonical firsts.
    The analytic polynomial of each actual cell is evaluated at complex
    time; its supplied real part domain is retained. Complex-face jumps
    are explicitly accessible, rather than presumed zero.
    """
    def __init__(self,times,raw,raw_time,coordinates):
        self.times=np.asarray(times,float);self.raw=np.asarray(raw,complex);self.rates=np.asarray(raw_time,complex)
        self.P=np.asarray(coordinates['lift']);self.n=coordinates['x_count']
        if self.raw.shape!=(len(self.times),268)or self.rates.shape!=self.raw.shape or np.any(np.diff(self.times)<=0):
            raise ValueError('complete ordered birth/stage/true endpoint history and canonical firsts required')
        eta=self.raw@self.P;rates=self.rates@self.P;n=self.n
        self.x=CubicHermiteSpline(self.times,eta[:,:n],eta[:,n:2*n],extrapolate=False)
        self.y=CubicHermiteSpline(self.times,eta[:,2*n:],rates[:,2*n:],extrapolate=False)
    def cell(self,t):
        if t.real<self.times[0]-1e-22 or t.real>self.times[-1]+1e-22:
            raise ValueError('outside actual canonical history, original callback continuation required')
        return min(max(np.searchsorted(self.times,t.real,side='right')-1,0),len(self.times)-2)
    @staticmethod
    def polynomial(p,t,cell,order=0):
        c=p.c[:,cell];z=t-p.x[cell]
        if order==0:return ((c[0]*z+c[1])*z+c[2])*z+c[3]
        if order==1:return (3*c[0]*z+2*c[1])*z+c[2]
        if order==2:return 6*c[0]*z+2*c[1]
        raise ValueError('owned C1 cubic value/rate/acceleration only')
    def value(self,t,cell=None):
        t=complex(t);cell=self.cell(t)if cell is None else int(cell)
        x=self.polynomial(self.x,t,cell);v=self.polynomial(self.x,t,cell,1);y=self.polynomial(self.y,t,cell)
        xt=v;vt=self.polynomial(self.x,t,cell,2);yt=self.polynomial(self.y,t,cell,1)
        return self.P@np.r_[x,v,y],self.P@np.r_[xt,vt,yt]


def _fixed_radial_maps(rep,rho):
    """Literal analytic continuation of the original four radial functions."""
    x=complex(rho)/WALL;regular=x**ALPHA;der=ALPHA*x**(ALPHA-1)/WALL
    vals=[];dr=[];a,b=2.,4+2*ALPHA
    for j in range(2):
        norm=np.exp(-(gammaln(j+a+1)+gammaln(j+b+1)-gammaln(j+1)-gammaln(j+a+b+1)-np.log(2*j+a+b+1))/2)
        p=1 if j==0 else .5*(a-b+(a+b+2)*(2*x-1))
        pr=0 if j==0 else (a+b+2)/WALL
        vals.append(norm*regular*(1-x)*p)
        dr.append(norm*((der*(1-x)-regular/WALL)*p+regular*(1-x)*pr))
    def lam(ref):
        g=np.r_[ref[:98],0j,0j];q,v,m,delta,rate,wall,_=_geometry_variables(g)
        f=_fields(12,q,v,m,(rho/WALL)*wall)
        den=f['A']**2+f['B']**2;l=f['A']**2/den
        lr=2*l*(1-l)*(f['ap']-f['bp'])*wall/WALL
        return l.value,lr.value
    p,c=(lam(r)for r in rep['affine_profile_reference_states'])
    f=(p[0]-c[0]-np.dot(vals,rep['affine_interior_projection'])-regular*rep['affine_wall_coefficient'])/rep['affine_complement_norm']
    fr=(p[1]-c[1]-np.dot(dr,rep['affine_interior_projection'])-der*rep['affine_wall_coefficient'])/rep['affine_complement_norm']
    return np.r_[vals,f,regular],np.r_[dr,fr,der]


def sigma_geometry_point(raw,raw_time,rho):
    """Evaluate the original holomorphic geometry at an actual complex point."""
    raw=np.asarray(raw,complex);dt=np.asarray(raw_time,complex)
    q,v,m,d,dr,wall,_=_geometry_variables(raw[:100]);chart=anchored_holomorphic_chart(d.value)
    chi=(complex(rho)/WALL)*wall;f=_fields(12,q,v,m,chi);r=_response(chi,d,dr,chart)
    R=f['A']*f['B']/_sqrt(f['A']**2+f['B']**2);C=f['C']*wall/WALL
    z=(f['beta']+(rho/WALL)*dr)/(wall/WALL)
    lr=(f['ap']+f['bp']-(f['A']**2*f['ap']+f['B']**2*f['bp'])/(f['A']**2+f['B']**2))*wall/WALL
    Z=_compose(d,chart['normalization'],*chart['normalization_derivatives'][:2])
    sr=.25*_sin(2*r['f'])**2/Z*wall/WALL;srr=.5*_sin(4*r['f'])*r['fprime']/Z*(wall/WALL)**2
    vr=np.zeros(100,complex);vr[:37]=raw[37:74];vr[98]=raw[99]
    def tjet(j):
        extra=np.r_[np.zeros(37),j.gradient[:37],np.zeros(25),j.gradient[98]]
        return type(j)(j.gradient@vr,j.hessian@vr+extra,np.zeros((100,100),complex))
    values=dict(lapse=f['N'],radial_coframe=C,radius=R,coordinate_shift=z,
        volume_density=f['N']*C*R**3,lapse_log_radial=f['np']*wall/WALL,
        radius_log_radial=lr,radial_coframe_log_radial=f['cp']*wall/WALL,
        coordinate_shift_radial=f['betap']+dr/wall,
        sigma_radial=sr,sigma_radial_second=srr,sigma_coordinate_time=tjet(r['sigma']),
        eta_profile=r['f'],eta_profile_radial=r['fprime']*wall/WALL,
        eta_profile_coordinate_time=tjet(r['f']))
    c={k:np.array([a.value])for k,a in values.items()}
    c.update({k+'_first':np.array([[a.gradient@dt[:100]]])for k,a in values.items()})
    return c


def transport_sigma_normal(history,rep,full,*,start_time,wall_amplitude,literal_left_wall_amplitude,normal_length,
        rtol=2e-9,atol=2e-11):
    """Execute the inward normal flow until a supplied history/pole face.

    J starts at1 in proper wall-time coordinates. The mode uses the
    supplied trial amplitude and the actual normal action integral. All
    particle/conjugate gauge line transports and their analytic inverses
    are integrated independently, with source coefficients unchanged.
    No partial integral is substituted for the unknown full normalization.
    """
    gamma=full['gamma5D_particle'];G=full['unitTr16_gauge_particle'];Gb=G.conj()
    raw,rate=history.value(start_time)
    c=sigma_geometry_point(raw,rate,WALL)
    sig=d5_sigma_foliation_eta(c,gamma=gamma,carrier_count=1,angular_count=1,sheet_orientation=1)
    U=(sig['sigma_normal_timelike_component']/sig['sigma_normal_radial_component'])[0]
    ell=c['lapse'][0]*np.sqrt(1-U*U);Rwall=c['radius'][0];fwall=c['eta_profile'][0]
    amplitude=complex(wall_amplitude)/np.sin(fwall)
    left_amplitude=complex(literal_left_wall_amplitude)/np.sin(fwall)
    ident=np.eye(16,dtype=complex)
    # X2, Xi2, logJ, I, Spin integral, then four independent16x16 maps.
    init=np.r_[complex(start_time),WALL,1/ell,0j,0j,0j,0j,
        ident.ravel(),ident.ravel(),ident.ravel(),ident.ravel()]
    current_cell=history.cell(start_time)
    def point(t,rho,cell=None):
        raw,rate=history.value(t,cell)
        c=sigma_geometry_point(raw,rate,rho)
        n=d5_sigma_foliation_eta(c,gamma=gamma,carrier_count=1,angular_count=1,sheet_orientation=1)
        flow=d5_sigma_normal_flow_germ(c,n,coordinate_time_first_slot=0)
        return raw,c,n,flow
    def rhs(s,y):
        # Numerical RK stages may use the polynomial of the final
        # supplied cell before its event is located. No such point is
        # retained as an exterior continuation of the physical history.
        raw,c,n,a=point(y[0],y[1],current_cell)
        nv=-a['sigma_flow_coordinate_velocity'][0]
        D=-np.c_[a['sigma_flow_coordinate_velocity_time'][0],a['sigma_flow_coordinate_velocity_radial'][0]]
        xi=D@y[2:4];div=-a['sigma_flow_log_density_normal_first'][0]
        N,C,z=(c[k][0]for k in('lapse','radial_coframe','coordinate_shift'))
        nr=c['lapse_log_radial'][0]*N;cr=c['radial_coframe_log_radial'][0]*C;zr=c['coordinate_shift_radial'][0]
        ct=c['radial_coframe_first'][0,0]
        aa=nr/(N*C);bb=(ct-z*cr-C*zr)/(N*C)
        omega=-(aa*n['sigma_normal_timelike_component'][0]+bb*n['sigma_normal_radial_component'][0])
        B,_=_fixed_radial_maps(rep,y[1]);A=np.einsum('r,rfc->fc',B,raw[100:180].reshape(4,5,4))
        connection=A[0]*nv[0]+A[1]*nv[1]
        Om=np.einsum('a,aij->ij',connection,G);Omb=np.einsum('a,aij->ij',connection,Gb)
        T,L,Tb,Lb=y[7:].reshape(4,16,16)
        return np.r_[nv,xi,div,np.sin(c['eta_profile'][0])**2,omega,
            (-Om@T).ravel(),(L@Om).ravel(),(-Omb@Tb).ravel(),(Lb@Omb).ravel()]
    samples=[];corners=[];function_evaluations=0;start=0.;state=init;hit=None
    while start<float(normal_length):
        def right(s,y):return history.times[current_cell+1]-y[0].real
        def left(s,y):return y[0].real-history.times[current_cell]+1e-22
        def radial(s,y):return y[1].real
        for f in(right,left,radial):f.terminal=True;f.direction=-1
        sol=solve_ivp(rhs,(start,float(normal_length)),state,method='DOP853',rtol=rtol,atol=atol,
            max_step=float(normal_length)/16,dense_output=True,events=(right,left,radial))
        if not sol.success:raise ArithmeticError(sol.message)
        function_evaluations+=sol.nfev
        samples.extend((float(ss),yy.copy(),current_cell)for ss,yy in zip(sol.t[:-1],sol.y.T[:-1]))
        end=float(sol.t[-1]);state=sol.y[:,-1].copy();face=next((i for i,v in enumerate(sol.t_events)if len(v)),None)
        if face is None:hit=None;samples.append((end,state.copy(),current_cell));break
        if face==2:hit=2;samples.append((end,state.copy(),current_cell));break
        nextcell=current_cell+(1 if face==0 else-1)
        if nextcell<0 or nextcell>=len(history.times)-1:
            hit=0 if face==0 else 1;samples.append((end,state.copy(),current_cell));break
        oldraw,oldc,_,oldflow=point(state[0],state[1],current_cell)
        newraw,newc,_,newflow=point(state[0],state[1],nextcell)
        oldv=-oldflow['sigma_flow_coordinate_velocity'][0];newv=-newflow['sigma_flow_coordinate_velocity'][0]
        if abs(oldv[0].real)<1e-14:raise ArithmeticError('complex interpolation face is grazing; no saltation quotient')
        oldxi=state[2:4].copy();newxi=oldxi+(newv-oldv)*(oldxi[0].real/oldv[0].real)
        determinant=lambda xi,v:xi[0]*v[1]-xi[1]*v[0]
        oldJ=-oldc['volume_density'][0]*determinant(oldxi,oldv)/Rwall**3
        newJ=-newc['volume_density'][0]*determinant(newxi,newv)/Rwall**3
        ratio=newJ/oldJ
        if abs(ratio)<1e-14 or abs(np.angle(ratio))>=np.pi/2:raise ArithmeticError('interpolation density return left its inherited logarithm chart')
        oldlog=state[4];newlog=oldlog+np.log(ratio)
        before=amplitude*np.sin(oldc['eta_profile'][0])*np.exp(-oldlog/2)
        after=amplitude*np.sin(newc['eta_profile'][0])*np.exp(-newlog/2)
        oldrawt=history.value(state[0],current_cell)[1];newrawt=history.value(state[0],nextcell)[1]
        corners.append(dict(s=end,located_complex_time=state[0],from_cell=current_cell,to_cell=nextcell,
            complex_face_raw_jump_norm=float(np.linalg.norm(newraw-oldraw)),complex_face_raw_time_jump_norm=float(np.linalg.norm(newrawt-oldrawt)),
            vector_field_jump=newv-oldv,transverse_return=newxi-oldxi,normal_log_density_return=np.log(ratio),
            density_before=oldJ,density_after=newJ,density_original_before_rows=np.exp(oldlog)-oldJ,
            density_original_after_rows=np.exp(newlog)-newJ,mode_trace_interpolation_return=after-before,
            real_linear_face_source_derivative_not_a_holomorphic_physical_sewing=True))
        samples.append((end,state.copy(),current_cell));state[2:4]=newxi;state[4]=newlog
        samples.append((end,state.copy(),nextcell));current_cell=nextcell;start=end
    s=np.array([a[0]for a in samples]);y=np.array([a[1]for a in samples])
    mode=[];left_mode=[];mode_rows=[];det_rows=[];unit_rows=[];actual=[]
    for ss,yy,cell in samples:
        raw,c,n,a=point(yy[0],yy[1],cell)
        J=np.exp(yy[4]);f=c['eta_profile'][0];u=amplitude*np.sin(f)*np.exp(-yy[4]/2)
        left_mode.append(left_amplitude*np.sin(f)*np.exp(-yy[4]/2))
        nv=-a['sigma_flow_coordinate_velocity'][0];div=-a['sigma_flow_log_density_normal_first'][0]
        fn=nv[0]*c['eta_profile_coordinate_time'][0]+nv[1]*c['eta_profile_radial'][0]
        us=u*(fn/np.tan(f)-div/2);m=-fn/np.tan(f)
        mode.append(u);mode_rows.append(us+div*u/2+m*u)
        det=yy[2]*nv[1]-yy[3]*nv[0]
        # inward orientation has negative determinant at the seam.
        jacobian=-c['volume_density'][0]*det/Rwall**3
        det_rows.append(jacobian-J)
        unit_rows.append(n['sigma_normal_unit_rows'][0]);actual.append((fn,div,m,J,us))
    maps=y[:,7:].reshape(len(s),4,16,16)
    arrays=dict(s=s,coordinate_time=y[:,0],material_rho=y[:,1],normal_leaf_transverse=y[:,2:4],
        normal_log_density=y[:,4],normal_density=np.exp(y[:,4]),normal_action_integral=y[:,5],
        spin_normal_connection_integral=y[:,6],particle_gauge_transport=maps[:,0],particle_analytic_dual_transport=maps[:,1],
        conjugate_gauge_transport=maps[:,2],conjugate_analytic_dual_transport=maps[:,3],
        normal_mode=np.array(mode),literal_left_normal_mode=np.array(left_mode),actual_normal_derivative_density_mass=np.array(actual),
        original_normal_mode_rows=np.array(mode_rows),original_flow_volume_Jacobian_rows=np.array(det_rows),
        original_unit_normal_rows=np.array(unit_rows),
        particle_analytic_dual_rows=maps[:,1]@maps[:,0]-np.eye(16),
        conjugate_analytic_dual_rows=maps[:,3]@maps[:,2]-np.eye(16),
        partial_mode_norm=np.array(left_amplitude*amplitude*y[-1,5]),
        trial_wall_amplitude=np.array(wall_amplitude),literal_left_trial_wall_amplitude=np.array(literal_left_wall_amplitude),original_surface_clock=np.array(ell))
    summary=dict(status=('SUPPLIED_CANONICAL_TIME_FACE'if hit==0 else'BIRTH_RESET_FACE'if hit==1 else'COMPLEX_RADIAL_CONTROL_FACE'if hit==2 else'BOUNDED_NORMAL_LENGTH'),
        function_evaluations=function_evaluations,s_end=float(s[-1]),coordinate_time_end=y[-1,0],rho_end=y[-1,1],
        actual_partial_normal_action_integral=y[-1,5],actual_partial_mode_norm=left_amplitude*amplitude*y[-1,5],
        original_normal_mode_rows_max=float(np.max(abs(arrays['original_normal_mode_rows']))),
        original_flow_volume_Jacobian_rows_max=float(np.max(abs(arrays['original_flow_volume_Jacobian_rows']))),
        original_unit_normal_rows_max=float(np.max(abs(arrays['original_unit_normal_rows']))),
        analytic_dual_rows_max=max(float(np.max(abs(arrays[k])))for k in('particle_analytic_dual_rows','conjugate_analytic_dual_rows')),
        interpolation_corners=corners,actual_normal_flow_density_source_dual_evaluated=True,
        internal_RK_polynomial_stage_extension_not_a_retained_physical_continuation=True,
        partial_integral_not_full_mode_normalization=True,history_outside_supplied_cells_not_extrapolated=True,
        physical_retarded_tail_pole_or_Pauli_selected=False,source_complement_or_continuum_error_enclosed=False)
    return arrays,summary
