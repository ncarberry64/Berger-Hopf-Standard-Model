"""Laplace action of an evaluated global canonical impulse trajectory.

The original complex clock and measure are retained on every source and
corner edge.  A time-varying action cannot be replaced by C(-is) at one
anchor.  The finite endpoint source and weak action identity stay explicit.
"""
from __future__ import annotations
import numpy as np


def represented_global_proper_clock(rows,right_clock,measure,*,temporal_nodes):
    """Integrate the SAME finite quadrature clock with its polynomial lift.

    The clock polynomial interpolates the executed w values on each edge.
    This gives a definite quadrature-level antiderivative and corner value,
    not a certified continuum interpolation or a new absolute-clock choice.
    """
    r=np.asarray(rows,complex);w,m=map(lambda a:np.asarray(a,complex),(right_clock,measure))
    if r.ndim!=3 or r.shape[1:]!=(2,3)or w.shape!=(len(r),)or m.shape!=w.shape:
        raise ValueError('all original incidence, clock and holomorphic measure required')
    edge=r[:,0,0].real.astype(int)
    if (np.any(r[:,:,0].imag)or not np.array_equal(r[:,1,0].real,edge+1)
            or np.any(r[:,:,1:].imag)or np.any(edge<0)or np.any(edge>=temporal_nodes-1)):
        raise ValueError('real computational FE shapes on the complete complex action clock required')
    tau=np.zeros(temporal_nodes,complex);points=np.zeros(len(r),complex);closure=np.zeros(temporal_nodes-1,complex)
    for j in range(temporal_nodes-1):
        ids=np.flatnonzero(edge==j)
        if not len(ids):raise ValueError('no source or corner edge may be skipped')
        f=r[ids,1,1].real;d=r[ids,1,2].real
        if not np.all(d==d[0])or d[0]<=0 or len(np.unique(f))!=len(f):
            raise ValueError('the original directed edge shapes must be retained')
        length=1/d[0]
        coeff=np.polynomial.polynomial.polyfit(f,w[ids],len(ids)-1)
        primitive=np.polynomial.polynomial.polyint(coeff)
        points[ids]=tau[j]+length*np.polynomial.polynomial.polyval(f,primitive)
        step=length*np.polynomial.polynomial.polyval(1.,primitive)
        tau[j+1]=tau[j]+step;closure[j]=step-sum(m[ids])
    return dict(proper_clock_nodes=tau,proper_clock_points=points,
        clock_quadrature_antiderivative_closure=closure,
        complex_clock_replaced_by_absolute_measure=False,
        clock_polynomial_interpolation_error_enclosed=False)


def global_causal_laplace_response(rows,right_clock,measure,trajectory,literal_radial_left,
        laplace_rates,*,birth_node):
    """Evaluate the future part of the actual impulse, without another inverse.

    G_T(s)=int_birth^final exp(-s*(tau-tau_birth))*S_L.T*x(tau) d_tau.
    The scalar radial source section is held in its recorded action chart;
    it is not moved to a new instantaneous Higgs direction or pole mode.
    Original coupled gauge/H/Gauss/frame fields stay in x.
    """
    x,l=map(lambda a:np.asarray(a,complex),(trajectory,literal_radial_left))
    r=np.asarray(rows,complex);m=np.asarray(measure,complex);rates=np.asarray(laplace_rates,complex)
    if (x.ndim!=3 or l.ndim!=2 or l.shape[0]!=x.shape[1]or rates.ndim!=1
            or not np.isfinite(rates).all()or not 0<birth_node<len(x)-1):
        raise ValueError('actual full trajectory, independent literal target and action frequencies required')
    clock=represented_global_proper_clock(r,right_clock,m,temporal_nodes=len(x))
    a=r[:,:,0].real.astype(int);p=r[:,:,1]
    value=np.einsum('qj,qjfc->qfc',p,x[a])
    pairing=np.einsum('fa,qfb->qab',l,value)
    future=a[:,0]>=birth_node
    dt=clock['proper_clock_points']-clock['proper_clock_nodes'][birth_node]
    weights=np.exp(-rates[:,None]*dt[None])*m[None]
    result=np.einsum('sq,qab->sab',weights[:,future],pairing[future])
    previous=np.einsum('sq,qab->sab',weights[:,~future],pairing[~future])
    return dict(**clock,laplace_rates=rates,global_future_Laplace_Green=result,
        before_source_Laplace_pairing=previous,radial_pairing_at_quadrature=pairing,
        future_source_domain_mask=future,relative_proper_clock_points=dt,
        final_relative_proper_clock=clock['proper_clock_nodes'][-1]-clock['proper_clock_nodes'][birth_node],
        static_C_minus_is_pulled_outside_global_integral=False,
        physical_quantum_covariance_or_LSZ_selected=False)


def global_laplace_weak_boundary_identity(action_rows,source_rows,literal_left,clock_nodes,
        laplace_rates,initial_cotangent,final_force,*,birth_node):
    """Apply the original action to the nodal exponential test, including ends.

    The actual action rows are K*x minus the original impulse source.  The
    held initial row is restored independently and the computed final force
    is not discarded.  This is the variable-coefficient global weak action,
    not a frozen three-term Fourier polynomial or a quantum prescription.
    """
    r,b=map(lambda a:np.asarray(a,complex),(action_rows,source_rows));l=np.asarray(literal_left,complex)
    tau=np.asarray(clock_nodes,complex);s=np.asarray(laplace_rates,complex)
    initial,final=map(lambda a:np.asarray(a,complex),(initial_cotangent,final_force))
    if (r.ndim!=3 or b.shape!=r.shape or l.shape[0]!=r.shape[1]
            or len(tau)!=len(r)+1 or initial.shape!=r.shape[1:]or final.shape!=initial.shape):
        raise ValueError('every original weak row and both actual canonical endpoint sources required')
    weight=np.exp(-s[:,None]*(tau[None]-tau[birth_node]))
    pair=lambda a:np.einsum('fa,nfb->nab',l,a)
    initial_contact=weight[:,0,None,None]*(l.T@initial)[None]
    source_contact=np.einsum('sn,nab->sab',weight[:,1:],pair(b))
    final_contact=weight[:,-1,None,None]*(l.T@final)[None]
    applied=np.einsum('sn,nab->sab',weight[:,1:],pair(r+b))+initial_contact
    return dict(global_applied_weak_action=applied,actual_impulse_source_contact=source_contact,
        initial_canonical_endpoint_contact=initial_contact,final_canonical_endpoint_contact=final_contact,
        global_weak_source_endpoint_identity=applied-source_contact-initial_contact-final_contact,
        final_source_endpoint_automatically_dropped=False,
        constant_coefficient_meromorphic_response_substituted=False)
