"""Analytic paired normal trial on a supplied complete complex action germ.

The proper normal and attachment maps precede the internal solve.  Literal
transpose duals retain complex coefficients and all multiplier rows.  The
frequency germ freezes coefficients; it is not the time-dependent selected
formation operator.  Surface gamma is an unassigned action parameter.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_normal_geometry import _geometry_variables, _fields, _sqrt
from .muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from .muon_complex_canonical_compatibility import canonical_central_frame
from .muon_birth_trace_enriched_action import generic_coordinate_lift


def analytic_frequency_polynomial(hessian, dynamic_count):
    """Apply v_right=i*omega*x and v_left=-i*omega*x independently."""
    H=np.asarray(hessian,complex); n=int(dynamic_count); m=len(H)-2*n
    if n<1 or m<1 or H.shape!=(2*n+m,)*2 or not np.isfinite(H).all():
        raise ValueError('complete finite complex (x,v,y) Hessian required')
    x=np.arange(n);v=n+x;y=np.arange(2*n,2*n+m);xy=np.r_[x,y]
    A0=H[np.ix_(xy,xy)];A1=np.zeros_like(A0);A2=np.zeros_like(A0)
    A1[:n,:n]=H[np.ix_(x,v)]-H[np.ix_(v,x)]
    A1[:n,n:]=-H[np.ix_(v,y)];A1[n:,:n]=H[np.ix_(y,v)]
    A2[:n,:n]=H[np.ix_(v,v)]
    return np.array([A0,1j*A1,A2])


def _balanced_solver(K):
    row=np.max(abs(K),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('unbound original bordered row')
    scale=1/np.sqrt(row);balanced=scale[:,None]*K*scale[None,:]
    def solve(rhs,transpose=False):
        b=balanced.T if transpose else balanced
        r=np.asarray(rhs);s=scale[:,None]if r.ndim==2 else scale
        return s*np.linalg.solve(b,s*r)
    return solve,balanced


def analytic_normal_frequency_jet(hessian,normal_trace,constraints,*,lapse):
    """Full bordered polynomial and independent analytic left through omega².

    Coefficients are Taylor coefficients, rather than second derivatives.
    Constraints consist of physical gluing and separately named frames.
    No real part, dagger, matrix symmetrization or spectral deletion enters.
    """
    normal=np.asarray(normal_trace,complex);C=np.asarray(constraints,complex)
    p=analytic_frequency_polynomial(hessian,len(normal));d=len(p[0]);lapse=complex(lapse)
    if C.ndim!=2 or C.shape[1]!=d or not np.isfinite(C).all() or not np.isfinite(lapse) or lapse==0:
        raise ValueError('same finite normal, constraint and nonzero clock required')
    T=np.vstack((np.r_[normal,np.zeros(d-len(normal))],C))
    K=np.zeros((3,d+len(T),d+len(T)),complex)
    K[:,:d,:d]=p;K[0,:d,d:]=T.T;K[0,d:,:d]=T
    rhs=np.zeros(len(K[0]),complex);rhs[d]=1
    solve,balanced=_balanced_solver(K[0])
    z=np.empty((len(rhs),3),complex);left=np.empty_like(z)
    z[:,0]=solve(rhs);left[:,0]=solve(rhs,True)
    for k in (1,2):
        z[:,k]=solve(-sum(K[j]@z[:,k-j]for j in range(1,k+1)))
        left[:,k]=solve(-sum(K[j].T@left[:,k-j]for j in range(1,k+1)),True)
    residual=np.column_stack([sum(K[j]@z[:,k-j]for j in range(k+1))-(rhs if k==0 else 0)for k in range(3)])
    dual=np.column_stack([sum(K[j].T@left[:,k-j]for j in range(k+1))-(rhs if k==0 else 0)for k in range(3)])
    response=-z[d];action=np.column_stack([sum(p[j]@z[:d,k-j]for j in range(k+1))for k in range(3)])
    return dict(action_polynomial=p,bordered_polynomial=K,bordered_rhs=rhs,
        right_taylor=z,left_taylor=left,response_taylor=response,
        right_original_rows=residual,left_original_rows=dual,
        original_action_rows_without_constraint_reactions=action,
        normal_and_constraint_rows=T,constraint_reactions=z[d+1:],
        constraint_coefficients=T@z[:d],lapse=lapse,
        coordinate_restoring=-response[0],coordinate_frequency_inertia=response[2],
        proper_restoring=-response[0]/lapse,proper_frequency_inertia=lapse*response[2],
        linear_response=response[1],balanced_condition=float(np.linalg.cond(balanced)),
        complete_Lyy_retained=True,coefficient_freezing_used=True,
        analytic_left_is_independently_solved=True,physical_formation_section_selected=False)


def frequency_parameter_jet(application,hessian_parameter):
    """Exact held-trace/clock gamma derivative, including internal responses."""
    a=application;d=len(a['action_polynomial'][0])
    # Recover n from Hessian dimension 2*n+m and polynomial dimension n+m.
    n=len(hessian_parameter)-d
    dp=analytic_frequency_polynomial(hessian_parameter,n);dK=np.zeros_like(a['bordered_polynomial']);dK[:,:d,:d]=dp
    solve,_=_balanced_solver(a['bordered_polynomial'][0]);z=a['right_taylor'];dz=np.empty_like(z)
    for k in range(3):
        source=-sum(dK[j]@z[:,k-j]for j in range(k+1))
        source-=sum(a['bordered_polynomial'][j]@dz[:,k-j]for j in range(1,k+1))
        dz[:,k]=solve(source)
    rows=np.column_stack([sum(a['bordered_polynomial'][j]@dz[:,k-j]+dK[j]@z[:,k-j]for j in range(k+1))for k in range(3)])
    response=-dz[d]
    return dict(Hessian_parameter=hessian_parameter,bordered_polynomial_parameter=dK,
        right_taylor_parameter=dz,response_taylor_parameter=response,parameter_original_rows=rows,
        proper_restoring_parameter=-response[0]/a['lapse'],proper_frequency_inertia_parameter=a['lapse']*response[2],
        trace_clock_held_at_supplied_state=True)


def analytic_frequency_sector_pairings(application,sector_hessians):
    """Contract signed sectors with the same independent analytic responses."""
    a=application;d=len(a['action_polynomial'][0]);left=a['left_taylor'][:d];right=a['right_taylor'][:d]
    sectors={}
    for name,H in sector_hessians.items():
        p=analytic_frequency_polynomial(H,len(H)-d)
        c=np.array([sum(left[:,i]@p[j]@right[:,k-i-j]for i in range(k+1)for j in range(k-i+1))for k in range(3)])
        sectors[name]=c
    return dict(sector_taylor=sectors,total_taylor=sum(sectors.values()),
        total_minus_reduced_response=sum(sectors.values())-a['response_taylor'])


def complex_proper_normal_trace(raw,one_lift):
    """-g(n_out,deltaX)=C_wall*D_x chi/sqrt(1-U²), including moving q."""
    x=np.asarray(raw,complex);P=np.asarray(one_lift);q,v,m,delta,dr,wall,Cstar=_geometry_variables(x[:100])
    f=_fields(12,q,v,m,wall);U=f['C']*(dr+f['beta'])/f['N'];root=_sqrt(1-U*U)
    factor=f['C'].value/root.value;normal=factor*wall.gradient@P[:100,:106]
    attachment=holomorphic_moving_trace(x)['attachment_first']@P[:100,:106]
    return dict(trace=np.vstack((attachment,normal)),proper_normal=normal,
        induced_lapse=f['N'].value*root.value,normal_projection=factor,
        wall_velocity=U.value,normal_chart_coefficient=normal[37])


def paired_complex_normal_application(hessian,parent_hessian,area_hessian,raw_pair,representation):
    """Bind all current action sectors, proper gluing and exact named frames."""
    c=generic_coordinate_lift(representation['gauge_labels']);P=c['lift'];n=106;m=40
    order=np.r_[np.arange(n),252+np.arange(n),n+np.arange(n),252+n+np.arange(n),
        2*n+np.arange(m),252+2*n+np.arange(m)]
    H=np.asarray(hessian,complex)[np.ix_(order,order)];Ha=np.asarray(area_hessian,complex)[np.ix_(order,order)]
    Hp=np.zeros((504,504),complex);Hp[:252,:252]=parent_hessian;Hp=Hp[np.ix_(order,order)]
    traces=[complex_proper_normal_trace(x,P)for x in raw_pair];Bp,Bc=[x['trace']for x in traces]
    d=292;glue=np.zeros((3,d),complex);glue[:,:n]=Bp;glue[:,n:2*n]=-Bc
    labels=representation['gauge_labels'];Ar=[j for j,i in enumerate(c['dynamic_gauge_indices'])if labels[i]['field']=='A_rho'and labels[i]['internal']==3]
    if len(Ar)!=4:raise ValueError('all four central radial slices per arm required')
    F=np.zeros((8,d),complex)
    for arm in range(2):F[arm*4+np.arange(4),arm*n+38+np.asarray(Ar)]=1
    normal=np.r_[Bp[-1],np.zeros(n)];clock=traces[1]['induced_lapse']
    frequency=analytic_normal_frequency_jet(H,normal,np.vstack((glue,F)),lapse=clock)
    gamma=frequency_parameter_jet(frequency,Ha)
    pairings=analytic_frequency_sector_pairings(frequency,dict(parent=Hp,inherited_child=H-Hp))
    phase=np.arange(212,504);D=H[np.ix_(phase,phase)];Da=Ha[np.ix_(phase,phase)]
    temporal=np.zeros((4,d),complex)
    for arm,x in enumerate(raw_pair):
        frame=canonical_central_frame(x,representation)['named_frame_covectors']
        ids=np.r_[arm*n+np.arange(n),2*n+arm*m+np.arange(m)]
        temporal[np.ix_(arm*2+np.arange(2),ids)]=frame
    T=np.vstack((np.r_[normal,np.zeros(80)],glue,temporal))
    K=np.block([[D,T.T],[T,np.zeros((len(T),len(T)),complex)]])
    rhs=np.zeros(len(K),complex);rhs[d]=1;solve,balance=_balanced_solver(K)
    z=solve(rhs);left=solve(rhs,True);inertia=left[:d]@D@z[:d]
    gamma_inertia=left[:d]@Da@z[:d]
    return dict(ordered_hessian=H,ordered_area_Hessian=Ha,ordering=order,parent_sector_Hessian=Hp,
        parent_trace=traces[0],child_trace=traces[1],physical_gluing=glue,
        named_static_radial_frames=F,named_temporal_frames=temporal,
        frequency=frequency,area_frequency_parameter=gamma,frequency_sector_pairings=pairings,
        kinetic=dict(original_saddle=K,right=z,left=left,original_rhs=rhs,
            right_original_rows=K@z-rhs,left_original_rows=K.T@left-rhs,
            coordinate_inertia=inertia,proper_inertia=clock*inertia,
            proper_inertia_gamma_parameter=clock*gamma_inertia,
            phase_lift=z[:d],frame_reactions=z[-4:],all_Lyy_retained=True,
            balanced_condition=float(np.linalg.cond(balance))),
        coefficient_chart='same common coordinate t; child-plus induced lapse for explicit proper readout',
        local_trial_normal_is_action_selected_section=False,
        time_dependent_Lvx_Lvv_Lvy_derivatives_not_dropped_from_physical_operator=True)


def full_joint_canonical_tangent(gradient,hessian,coefficients,named_phase_frames,*,gradient_clock_first=None):
    """Original joint canonical DAE tangent, retaining all v/y equations.

    D(vdot,ydot)=(Lx-Lvx*v-Lvt, -Lyx*v-Lyt).  Explicit clock motion
    is supplied as a separate original gradient jet; zero means a held
    reference snapshot application and is never a physical clock claim.
    """
    G=np.asarray(gradient,complex);H=np.asarray(hessian,complex);eta=np.asarray(coefficients,complex)
    x=np.r_[np.arange(106),252+np.arange(106)];v=x+106;y=np.r_[np.arange(212,252),np.arange(464,504)]
    phase=np.r_[v,y];F=np.asarray(named_phase_frames,complex);D=H[np.ix_(phase,phase)]
    gt=np.zeros(504,complex)if gradient_clock_first is None else np.asarray(gradient_clock_first,complex)
    rhs=np.r_[G[x]-H[np.ix_(v,x)]@eta[v]-gt[v],-H[np.ix_(y,x)]@eta[v]-gt[y]]
    K=np.block([[D,F.T],[F,np.zeros((len(F),len(F)),complex)]])
    solve,balance=_balanced_solver(K);z=solve(np.r_[rhs,np.zeros(len(F))]);rate=np.zeros(504,complex)
    rate[x]=eta[v];rate[phase]=z[:292]
    return dict(original_saddle=K,original_rhs=np.r_[rhs,np.zeros(len(F))],solution=z,
        original_rows=K@z-np.r_[rhs,np.zeros(len(F))],unframed_original_rows=D@z[:292]-rhs,
        phase_acceleration_rate=z[:292],full_master_coordinate_rate=rate,frame_reactions=z[292:],
        explicit_gradient_clock_first=gt,held_reference_clock=gradient_clock_first is None,
        balanced_condition=float(np.linalg.cond(balance)),joint_momenta_not_replaced_by_ownparent_momenta=True)


def chronological_jacobi_coefficient_contact(hessian_time_first,dynamic_count):
    """The omitted-by-freeze Euler coefficient contacts, in (x,y) order.

    Lxx-D_t Lvx + i*omega*(Lxv-Lvx-D_t Lvv)+omega² Lvv;
    Lxy-D_t Lvy-i*omega Lvy. Algebraic Ly rows retain no coefficient
    derivative. This uses the literal action equation Lx-D_t Lv.
    """
    Ht=np.asarray(hessian_time_first,complex);n=int(dynamic_count);m=len(Ht)-2*n;d=n+m
    if Ht.shape!=(2*n+m,)*2 or m<1:raise ValueError('same full Hessian time jet required')
    out=np.zeros((3,d,d),complex);out[0,:n,:n]=-Ht[n:2*n,:n]
    out[0,:n,n:]=-Ht[n:2*n,2*n:];out[1,:n,:n]=-1j*Ht[n:2*n,n:2*n]
    return out
