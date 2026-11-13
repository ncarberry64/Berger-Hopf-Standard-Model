"""Saved-coordinate-column D5 diagnostics, with no solve or state selection.

Inputs are the already evaluated fields, derivatives, coefficients and
data. Component magnitudes and numerical chart scales are kept separate
from physical current/Cauchy norms, which are not supplied by this module.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.chebyshev import chebvander


def original_term_arrays(field,coefficients):
    """Original unsquared differential equation and all six source terms."""
    required=('value','time','radial','source','time_source','radial_source')
    if any(k not in field or field[k] is None for k in required):
        raise ValueError('explicit saved values and every consumed source derivative required')
    names=('time','radial','body','time_source','radial_source','body_source')
    if any(k not in coefficients or coefficients[k] is None for k in names):
        raise ValueError('explicit original coefficients and coefficient derivatives required')
    f={k:np.asarray(field[k]) for k in required};c={k:np.asarray(coefficients[k]) for k in names}
    if any(a.shape!=f['value'].shape for a in f.values()):raise ValueError('same coordinate-column identities required')
    p=dict(T_dt=c['time']@f['time'],R_dr=c['radial']@f['radial'],K_value=c['body']@f['value'],
        dT_dt=c['time_source']@f['time'],dR_dr=c['radial_source']@f['radial'],dK_value=c['body_source']@f['value'],
        T_dt_source=c['time']@f['time_source'],R_dr_source=c['radial']@f['radial_source'],K_source=c['body']@f['source'])
    p['original_D5']=p['T_dt']+p['R_dr']+p['K_value']
    p['source_vertex']=p['dT_dt']+p['dR_dr']+p['dK_value']
    p['source_state']=p['T_dt_source']+p['R_dr_source']+p['K_source']
    p['original_D5_source']=p['source_vertex']+p['source_state']
    return p


def magnitude(value):
    a=np.asarray(value)
    return dict(max_abs=float(np.max(abs(a))) if a.size else 0.,frobenius=float(np.linalg.norm(a)),
        shape=list(a.shape))


def term_report(field,coefficients,parts=None):
    """No normalization or admission criterion is changed by these ratios."""
    p=original_term_arrays(field,coefficients) if parts is None else parts
    values={k:magnitude(v) for k,v in p.items()}
    denominator=sum(values[k]['max_abs'] for k in ('T_dt','R_dr','K_value'))
    xden=sum(values[k]['max_abs'] for k in ('dT_dt','dR_dr','dK_value','T_dt_source','R_dr_source','K_source'))
    return dict(field={k:magnitude(v) for k,v in field.items()},coefficients={k:magnitude(v) for k,v in coefficients.items()},
        terms=values,conditioning_only=dict(value_sum_over_term_max_sum=None if denominator==0 else values['original_D5']['max_abs']/denominator,
            source_sum_over_term_max_sum=None if xden==0 else values['original_D5_source']['max_abs']/xden),
        reported_norm='unweighted original-coordinate component max and Frobenius of stated coefficient columns',
        physical_current_or_Cauchy_norm=None,physical_state_amplitudes=None,
        physical_admission=False,physical_guard=2e-10)


def saved_nodal_partitions(value,source,coefficients,Dt,Dr,inner_incoming,outer_incoming):
    """Differentiate SAVED nodal polynomials; no field is re-solved/rebuilt."""
    V,X=np.asarray(value),np.asarray(source);Dt,Dr=map(np.asarray,(Dt,Dr))
    if V.shape!=X.shape or V.ndim!=4:raise ValueError('saved time/radial/carrier/input-column arrays required')
    field=dict(value=V,source=X,time=np.einsum('ij,jrak->irak',Dt,V),radial=np.einsum('rs,isak->irak',Dr,V),
        time_source=np.einsum('ij,jrak->irak',Dt,X),radial_source=np.einsum('rs,isak->irak',Dr,X))
    parts=original_term_arrays(field,coefficients);L,Lx=parts['original_D5'],parts['original_D5_source']
    TI=np.linalg.inv(coefficients['time']);TIx=-TI@coefficients['time_source']@TI
    E=TI@L;Ex=TI@Lx+TIx@L
    incoming=[];incomingx=[];outgoing=[];outgoingx=[]
    for r,Qin,Qout in ((0,inner_incoming,outer_incoming),(-1,outer_incoming,inner_incoming)):
        incoming.append(Qin.conj().T@E[1:,r]);incomingx.append(Qin.conj().T@Ex[1:,r])
        outgoing.append(Qout.conj().T@E[1:,r]);outgoingx.append(Qout.conj().T@Ex[1:,r])
    arrays=dict(enforced_interior_original_D5=L[1:,1:-1],enforced_interior_original_D5_source=Lx[1:,1:-1],
        enforced_outgoing_evolution=np.array(outgoing),enforced_outgoing_evolution_source=np.array(outgoingx),
        held_incoming_evolution=np.array(incoming),held_incoming_evolution_source=np.array(incomingx),
        held_birth_original_D5=L[0],held_birth_original_D5_source=Lx[0])
    report={k:magnitude(v) for k,v in arrays.items()}
    report.update(norm_scope='enforced outgoing rows use Qout^dagger T^-1 L; interior/birth rows use original unsquared D5; no physical data or norm selected',
        physical_admission=False,physical_guard=2e-10)
    return arrays,report,field,parts


def time_polynomial_diagnostics(values,times,derivative):
    """Chebyshev content and time scales of supplied numerical coefficients."""
    a=np.asarray(values);t=np.asarray(times,float);D=np.asarray(derivative)
    if a.shape[0]!=len(t) or len(t)!=6 or t[-1]<=t[0]:raise ValueError('the saved six-node time chart is required')
    z=2*(t-t[0])/(t[-1]-t[0])-1;coeff=np.linalg.solve(chebvander(z,5),a.reshape(6,-1)).reshape(a.shape)
    first=np.einsum('ij,j...->i...',D,a);second=np.einsum('ij,j...->i...',D,first);width=t[-1]-t[0]
    maximum=max(float(np.max(abs(coeff))),np.finfo(float).tiny)
    return dict(coefficient_max_by_mode=[float(np.max(abs(c))) for c in coeff],
        coefficient_Frobenius_by_mode=[float(np.linalg.norm(c)) for c in coeff],
        high_two_mode_max_ratio=float(np.max(abs(coeff[-2:])))/maximum,
        actual_value=magnitude(a),coordinate_time_first=magnitude(first),coordinate_time_second=magnitude(second),
        proper_time_or_physical_unit_derivative=None,
        conditioning_only=dict(cell_width=width,width_times_time_first=float(width*np.max(abs(first))),
            width_squared_times_time_second=float(width**2*np.max(abs(second)))),
        note='fixed numerical polynomial/coordinate-column diagnostics only; scaled values are not physical norms or error bounds')


def boundary_data_diagnostics(birth,birth_source,incoming,incoming_source,coefficients,Dt,Dr,inner,outer):
    """C1 incoming boundary germs from the saved birth and incoming data."""
    birth,bx,inc,incx=map(np.asarray,(birth,birth_source,incoming,incoming_source))
    nr,d,k=birth.shape;half=d//2;nt=len(Dt)
    if inc.shape!=(nt-1,d,k) or incx.shape!=inc.shape:raise ValueError('both independent face incoming coefficient histories required')
    B=np.zeros((nt,2,half,k),complex);Bx=np.zeros_like(B)
    for face,r,Q in ((0,0,inner),(1,nr-1,outer)):
        B[0,face]=Q.conj().T@birth[r];Bx[0,face]=Q.conj().T@bx[r]
        B[1:,face]=inc[:,face*half:(face+1)*half];Bx[1:,face]=incx[:,face*half:(face+1)*half]
    bd=np.einsum('j,j...->...',Dt[0],B);bdx=np.einsum('j,j...->...',Dt[0],Bx)
    br=np.einsum('rs,sak->rak',Dr,birth);brx=np.einsum('rs,sak->rak',Dr,bx)
    T,R,K=(coefficients[q][0] for q in ('time','radial','body'))
    Tx,Rx,Kx=(coefficients[q][0] for q in ('time_source','radial_source','body_source'))
    TI=np.linalg.inv(T);TIx=-TI@Tx@TI;A=TI@R;Ax=TI@Rx+TIx@R;P=TI@K;Px=TI@Kx+TIx@K
    restoring=[];restoringx=[]
    for face,r,Q in ((0,0,inner),(1,nr-1,outer)):
        restoring.append(Q.conj().T@(A[r]@br[r]+P[r]@birth[r]))
        restoringx.append(Q.conj().T@(Ax[r]@br[r]+A[r]@brx[r]+Px[r]@birth[r]+P[r]@bx[r]))
    restoring=np.array(restoring);restoringx=np.array(restoringx)
    return dict(boundary_values=B,boundary_sources=Bx,original_C1_data_germ=bd+restoring,
        original_C1_data_germ_source=bdx+restoringx,incoming_time_germ=bd,
        incoming_time_germ_source=bdx,required_evolution_germ=-restoring,required_evolution_germ_source=-restoringx),dict(
        original_C1_value=magnitude(bd+restoring),original_C1_source=magnitude(bdx+restoringx),
        incoming_time_germ=magnitude(bd),incoming_time_germ_source=magnitude(bdx),
        required_evolution_germ=magnitude(restoring),required_evolution_germ_source=magnitude(restoringx),
        physical_future_incoming_data_selected=False,physical_admission=False,
        source_scope='both state and coefficient derivatives, including inverse time principal; fixed numerical faces, independent physical domain/contact ports not assigned')
