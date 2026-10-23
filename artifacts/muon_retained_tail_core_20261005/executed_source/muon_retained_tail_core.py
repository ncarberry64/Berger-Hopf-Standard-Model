"""Same-source retained tail in a canonical minimal-core trial subspace.

This is a muon realization, not the complete stratified operator.  The
trial closure is inherited from the minimal core; exhaustive owned
wall/reset/completion pullback is deliberately not asserted.
"""
from __future__ import annotations
import numpy as np
from bhsm.interface.muon_prefix_time_element import integrate_linear_density_element


def endpoint_element(left,right,arc_width,source):
    """Transform new hierarchical forms AND load to geometric trace coordinates."""
    p=[dict(q,tau_x=arc_width*q['clock_density']) for q in (left,right)]
    scale=arc_width*(left['clock_density']+right['clock_density'])/2
    K,M,polys=integrate_linear_density_element(p,scale)
    d=len(source);I=np.eye(d)
    chart=np.block([[I/2,I/2],[-I/scale,I/scale]])
    original=np.r_[source,np.zeros(d)]
    return dict(K=chart.conj().T@K@chart,M=chart.conj().T@M@chart,
        f=chart.conj().T@(M@original),hierarchical_K=K,hierarchical_M=M,
        hierarchical_source=original,endpoint_to_hierarchical=chart,scale=scale,
        densities=polys)


def stop_regular_moments(s,basis,carrier,cut,arc_multiplier_rate,arc_width):
    """Clock times F0 at the actual zero-clock stop; no Y_tau=0/0.

    q_arc=0 at this stop, while m_arc is retained. Therefore
    rho_arc F0_W=-u iGamma0 L_nu,arc/(2nu), rho_arc F0_p=0.
    Both chiral/internal sectors enter the actual Gamma0 image Gram.
    """
    d=cut['independent_source_map'].shape[1];G0=np.zeros((d,d),complex)
    GH=np.zeros_like(G0)
    for n in (1,3):
        xi=basis[n]
        gxi=np.einsum('oi,imkj->omkj',1j*carrier['common_parent_Gamma'][0],xi).reshape(-1,d)
        x=xi.reshape(-1,d);G0+=gxi.conj().T@gxi;GH+=x.conj().T@x
    k=np.arange(1,13);rho=s['points']
    Larc=(np.cos(2*rho[:,None]*k)-(-1.)**k)@arc_multiplier_rate[:12]
    a=-arc_width*s['u']*Larc/(2*s['nu']);w=s['u']/s['nu'];p=s['p']/s['nu']
    weighted=cut['radial_weights']*s['volume']
    moment=lambda a,b:float(weighted@(a*b))
    Z=np.zeros_like(G0)
    A=np.block([[moment(a,a)*G0,Z],[Z,Z]])
    B=np.block([[moment(a,w)*G0,moment(a,p)*G0],[Z,Z]])
    C=np.kron(np.array([[moment(w,w),moment(w,p)],[moment(w,p),moment(p,p)]]),G0)
    gram=lambda measure:np.kron(np.array([[float((cut['radial_weights']*measure)@(s['u']**2)),
        float((cut['radial_weights']*measure)@(s['u']*s['p']))],
        [float((cut['radial_weights']*measure)@(s['u']*s['p'])),
         float((cut['radial_weights']*measure)@(s['p']**2))]]),GH)
    return dict(Areg=A,Breg=B,C=C,M=gram(s['volume']),Ms=gram(s['cauchy']),
        Lnu_arc=Larc,Gamma0_image_Gram=G0)


def terminal_core_element(left,stop,arc_width,source):
    """Exact regular moments for phi=(1-x)^2 at the zero-clock endpoint.

    rho_arc(x)=rho_left*(1-x). The proper-time P1 core trial has
    phi~(1-x)^2, whereas arc-P1 would have infinite derivative energy.
    This is a minimal-core trial limit, not a chosen physical endpoint law.
    """
    j=arc_width*left['clock_density']
    A=j*j*left['A'];B=j*left['B'];C=left['C'];M=left['M']
    # Exact beta moments of linearly interpolated REGULAR moment blocks.
    K=(A/5+stop['Areg']/20-(B+B.conj().T)/2
        -(stop['Breg']+stop['Breg'].conj().T)/6+4*C/3+2*stop['C']/3)/j
    mass=j*(M/7+stop['M']/42)
    forcing=j*(M/5+stop['M']/20)@source
    return dict(K=K,M=mass,f=forcing,clock_left=j,
        regular_A=np.array([A,stop['Areg']]),regular_B=np.array([B,stop['Breg']]),
        regular_C=np.array([C,stop['C']]),regular_M=np.array([M,stop['M']]))


def tail_response(elements,terminal,source_trace,shift):
    """Block solves; retain both mixed blocks and the nonzero continued source."""
    d=len(source_trace);count=len(elements)+1
    diag=np.zeros((count,d,d),complex);upper=np.zeros((count-1,d,d),complex);lower=upper.copy()
    f=np.zeros((count,d),complex)
    for i,e in enumerate(elements):
        H=e['K']+shift*e['M']
        diag[i]+=H[:d,:d];diag[i+1]+=H[d:,d:]
        upper[i]=H[:d,d:];lower[i]=H[d:,:d]
        f[i]+=e['f'][:d];f[i+1]+=e['f'][d:]
    diag[-1]+=terminal['K']+shift*terminal['M'];f[-1]+=terminal['f']
    S=diag[-1].copy();r=f[-1].copy();Y=[];y=[];conditions=[];Ds=[]
    for i in range(count-2,-1,-1):
        D=S.copy();sol=np.linalg.solve(D,np.column_stack((lower[i],r)))
        Ys=sol[:,:d];ys=sol[:,d];Y.append(Ys);y.append(ys);Ds.append(D)
        conditions.append(float(np.linalg.cond(D)))
        S=diag[i]-upper[i]@Ys;r=f[i]-upper[i]@ys
    Y=np.array(Y[::-1]);y=np.array(y[::-1]);Ds=np.array(Ds[::-1])
    homogeneous=np.zeros((count,d),complex);particular=homogeneous.copy()
    homogeneous[0]=source_trace
    for i in range(count-1):
        homogeneous[i+1]=-Y[i]@homogeneous[i]
        particular[i+1]=-Y[i]@particular[i]+y[i]
    u=homogeneous+particular
    def action(v):
        out=np.einsum('nij,nj->ni',diag,v)
        out[:-1]+=np.einsum('nij,nj->ni',upper,v[1:])
        out[1:]+=np.einsum('nij,nj->ni',lower,v[:-1])
        return out
    residual=action(u)-f;traction=residual[0].copy()
    backward=max(float(np.linalg.norm(residual[i])/(np.linalg.norm(diag[i])*np.linalg.norm(u[i])+
        (np.linalg.norm(lower[i-1])*np.linalg.norm(u[i-1]) if i else 0)+
        (np.linalg.norm(upper[i])*np.linalg.norm(u[i+1]) if i<count-1 else 0)+np.linalg.norm(f[i])))
        for i in range(1,count))
    return dict(S=S,r=r,solution=u,homogeneous_solution=homogeneous,
        source_particular=particular,diagonal=diag,upper=upper,lower=lower,rhs=f,
        backsubstitution_Y=Y,backsubstitution_y=y,interior_pivots=Ds,
        stationary_conormal_dual=traction,homogeneous_conormal_dual=S@source_trace,
        source_affine_conormal_dual=-r,equation_residual=residual[1:],
        stationary_conormal_identity_residual=traction-(S@source_trace-r),
        output_contraction=np.vdot(source_trace,traction),
        homogeneous_output_contraction=np.vdot(source_trace,S@source_trace),
        maximum_interior_backward_residual=backward,maximum_pivot_condition=max(conditions),
        interior_source_rhs_norm=float(np.linalg.norm(f[1:])),shift=shift)


def attach_core_tail(partial,last_trace,tail,shift):
    """Consume core response, preserving the uncomputed exhaustive owned terms."""
    H=partial['K']+shift*partial['M']+last_trace.conj().T@tail['S']@last_trace
    f=partial['source_weak_rhs']+last_trace.conj().T@tail['r']
    return dict(H=H,rhs=f,trace_continuity=partial['trace_continuity'],
        tail_trace_injection=last_trace,tail_shift=np.array(shift),
        original_source_coefficients=partial['source_coefficients'])
