"""First-order flow tubes and moving proper-time jets from an owned field box.

No field, endpoint, or boundary law is selected here. The caller supplies an
enclosed C1 vector field and its Jacobian on a convex, verified domain.
"""
import numpy as np
from flint import arb, arb_mat


def amat(a):
    a = np.asarray(a, dtype=object)
    return arb_mat(*a.shape, list(a.flat))


def flow_certificate(initial, initial_jet, rate, derivative, radii, horizon):
    """Picard inclusion and a common variation bound in a scaled infinity norm.

    radii are exact symmetric domain radii about initial.mid(). A strict
    excursion bound proves existence up to horizon. The first variation is
    J(t)=J0+integral DF(y(u))J0 du+E(t), with the remainder bounded by
    (exp(L*t)-1-L*t)||J0||, separately for every input column.
    """
    y = [arb(v) for v in initial]
    f = [arb(v) for v in rate]
    r = [arb(v) for v in radii]
    h = arb(horizon)
    J, A = amat(initial_jet), amat(derivative)
    n, m = J.nrows(), J.ncols()
    if len(y) != n or len(f) != n or len(r) != n or (A.nrows(), A.ncols()) != (n, n):
        raise ValueError('aligned initial point, rate, domain and first jet required')
    if not h > 0 or not all(v > 0 and v.rad().is_zero() for v in r):
        raise ValueError('positive horizon and exact positive domain radii required')
    excursions = [(v.rad()+h*abs(w).upper())/rr for v,w,rr in zip(y,f,r)]
    if not all(v < 1 for v in excursions):
        raise ArithmeticError('flow leaves the certified domain; recenter/subdivide')
    L = max((sum((abs(A[i,j]).upper()*r[j]/r[i] for j in range(n)), arb(0)).upper()
             for i in range(n)), key=lambda v: v.fmpq())
    if not L*h < 1:
        raise ArithmeticError('Picard step requires subdivision')
    column_bounds = [max((abs(J[i,j]).upper()/r[i] for i in range(n)),
                         key=lambda v: v.upper().fmpq()).upper() for j in range(m)]
    return dict(initial=y, initial_jet=J, rate=f, derivative=A, radii=r,
                horizon=h, L=L, column_bounds=column_bounds, AJ=A*J,
                excursion_upper=max(v.upper().fmpq() for v in excursions))


def flow_at(certificate, time):
    """Outward state and 73-column first-variation enclosures at any stored time."""
    c=certificate; t=arb(time)
    if not t >= 0 or not t <= c['horizon']:
        raise ValueError('time outside the certified prefix')
    return _flow_enclosure(c,t,t.upper())


def flow_span(certificate, start, end):
    """Enclose a closed time interval without treating radius rounding as time."""
    a,b=arb(start),arb(end)
    if not a>=0 or not a<=b or not b<=certificate['horizon']:
        raise ValueError('time span outside certified prefix')
    t=(a+b)/2+arb(0,((b-a)/2).upper())
    return _flow_enclosure(certificate,t,b.upper())


def _flow_enclosure(c,t,maximum_time):
    y=np.array([v+t*f for v,f in zip(c['initial'],c['rate'])],dtype=object)
    J=c['initial_jet']+c['AJ']*t
    u=c['L']*maximum_time
    # Positive Taylor remainder, evaluated without subtracting nearly equal
    # numbers: sum_{k>=2}u^k/k! <= u^2 exp(u)/2 for u>=0.
    tail=u*u*u.exp()/2
    for i in range(J.nrows()):
        for j in range(J.ncols()):
            J[i,j]+=arb(0,(c['radii'][i]*c['column_bounds'][j]*tail).upper())
    return y,J


def proper_clock(state_action, weights, rate, derivative):
    """Owned q=N*s/||G|| via q=N*F_q0/(w_q0*qdot0).

    The equality follows from G_q0=s*w_q0*qdot0. This chart only applies
    when qdot0 is nonzero; it never divides by the descriptor speed.
    """
    y=[arb(v)/arb(w) for v,w in zip(state_action[:98],weights)]
    w=[arb(v) for v in weights]
    A=amat(derivative)
    logN=sum(((-1)**(j+1)*y[74+j] for j in range(12)),arb(0))
    N=logN.exp(); velocity=y[37]
    if velocity.contains(0):
        raise ArithmeticError('qdot0 chart is unavailable')
    f=arb(rate[0]); q=N*f/(w[0]*velocity)
    dq=arb_mat(1,99)
    for j in range(99):
        dq[0,j]=N*A[0,j]/(w[0]*velocity)
    for j in range(12):dq[0,74+j]+=q*((-1)**(j+1))/w[74+j]
    dq[0,37]-=q/(velocity*w[37])
    if not q > 0:
        raise ArithmeticError('proper-time monotonicity not certified')
    return q,dq
