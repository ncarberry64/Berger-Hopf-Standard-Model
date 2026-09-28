"""Shared current incoming coefficient and local internal response primitives.

These functions do not select a birth endpoint or eliminate temporal, contact,
or heat variables. Local implicit response is explicitly a subsystem.
"""
from flint import arb, arb_mat
from bhsm.interface.aether_forward_boundary_radius import RADIUS0


def matrix(value):
    if isinstance(value, arb_mat):
        return value
    return arb_mat(value.tolist())


def coefficient_first(raw_state, raw_directions):
    """One coefficient map for every consumer, in supplied raw directions.

    The attached action's binary64 59/30 is preserved, not silently replaced
    by the nearby exact rational used in some historical spectral producers.
    """
    y = list(raw_state)
    U = matrix(raw_directions)
    if len(y) != 98 or U.nrows() != 98 or U.ncols() < 1:
        raise ValueError('current 98D state and nonempty raw direction family required')
    if not all(arb(v).is_finite() for v in y + U.entries()):
        raise ValueError('finite current coefficient family required')
    y = [arb(v) for v in y]
    m = U.ncols()
    row = lambda i: arb_mat(1, m, [U[i, j] for j in range(m)])
    signs = [(-1)**j for j in range(12)]
    v = sum((y[25+j]*signs[j] for j in range(12)), arb(0))
    dv = sum((row(25+j)*signs[j] for j in range(12)), arb_mat(1, m))
    t = (2*v).tanh()
    x = (arb(float(RADIUS0))/2).log()+y[0]
    x -= sum((y[1+j]*signs[j] for j in range(12)), arb(0))+(2*v).cosh().log()/2
    dx = row(0)-sum((row(1+j)*signs[j] for j in range(12)), arb_mat(1, m))-t*dv
    logN = -sum((y[74+j]*signs[j] for j in range(12)), arb(0))
    dlogN = -sum((row(74+j)*signs[j] for j in range(12)), arb_mat(1, m))
    N = logN.exp()
    vdot = sum((y[62+j]*signs[j] for j in range(12)), arb(0))
    numerator = y[37]-sum((y[38+j]*signs[j] for j in range(12)), arb(0))-t*vdot
    dnum = row(37)-sum((row(38+j)*signs[j] for j in range(12)), arb_mat(1, m))
    dnum -= t*sum((row(62+j)*signs[j] for j in range(12)), arb_mat(1, m))
    dnum -= 2*(1-t*t)*vdot*dv
    rate, drate = numerator/N, (dnum-numerator*dlogN)/N
    W, V, c = (-x).exp(), (-2*x).exp(), arb(float(59/30))
    values = dict(log_radius=x, log_lapse=logN, lapse=N,
                  unit_scalar_gauge_potential=V, unit_Weyl_superpotential=W,
                  proper_log_radius_rate=rate, zeta_proper_density=-c*W,
                  zeta_coordinate_density=-c*N*W)
    first = dict(log_radius=dx, log_lapse=dlogN, lapse=N*dlogN,
                 unit_scalar_gauge_potential=-2*V*dx, unit_Weyl_superpotential=-W*dx,
                 proper_log_radius_rate=drate, zeta_proper_density=c*W*dx,
                 zeta_coordinate_density=-c*N*W*(dlogN-dx))
    return values, first


def local_internal_system(shared):
    """Replay the coupled (psi,lambda,hard,b) subsystem, with one base.

    F=(H psi-lambda psi, (psi^T psi-1)/2,
       (H-lambda I)hard+b psi-rhs, psi^T hard).
    Every source derivative comes from the same retained action evaluation.
    """
    H = matrix(shared['H'])
    p, h = [arb_mat(len(shared[k]), 1, list(shared[k])) for k in ('psi', 'hard')]
    lam, b = shared['eigenvalue'], shared['bpsi']
    n = H.nrows()
    hp = matrix(shared['H_first_on_psi'])
    hh = matrix(shared['H_first_on_hard'])
    dp_all = matrix(shared['dpsi'])
    dhb = matrix(shared['dhard_b'])
    hard_rhs = matrix(shared['hard_first_rhs'])
    m = hp.ncols()
    dp = arb_mat(n, m, [dp_all[i, j] for i in range(n) for j in range(m)])
    dl = arb_mat(1, m, list(shared['deigenvalue']))
    rhs = arb_mat(n, 1, list(shared['rhs']))
    A = H-arb_mat([[lam if i == j else 0 for j in range(n)] for i in range(n)])
    F = arb_mat((A*p).tolist()+[[(p.transpose()*p)[0, 0]/2-arb(1)/2]]
                +(A*h+b*p-rhs).tolist()+[[(p.transpose()*h)[0, 0]]])
    Fn, Fx = arb_mat(2*n+2, 2*n+2), arb_mat(2*n+2, m)
    for i in range(n):
        Fn[i, n] = -p[i, 0]
        Fn[n, i] = p[i, 0]
        Fn[n+1+i, i] = b
        Fn[n+1+i, n] = -h[i, 0]
        Fn[n+1+i, 2*n+1] = p[i, 0]
        Fn[2*n+1, i] = h[i, 0]
        Fn[2*n+1, n+1+i] = p[i, 0]
        for j in range(n):
            Fn[i, j] = A[i, j]
            Fn[n+1+i, n+1+j] = A[i, j]
        for j in range(m):
            # Reverse only the algebraic rearrangement in the owner's RHS;
            # this recovers the partial source, not a fitted response.
            drhs = hard_rhs[i, j]+hh[i, j]-dl[0, j]*h[i, 0]+b*dp[i, j]
            Fx[i, j] = hp[i, j]
            Fx[n+1+i, j] = hh[i, j]-drhs
    Dn = arb_mat(dp.tolist()+dl.tolist()+dhb.tolist())
    replay = Fn*Dn+Fx
    target = arb_mat(1, 2*n+2)
    target[0, 2*n+1] = 1
    adjoint = Fn.transpose().solve(target.transpose())
    adjoint_first = -adjoint.transpose()*Fx
    return dict(residual=F, internal_jacobian=Fn, input_partial=Fx,
                internal_first=Dn, first_replay=replay, b_adjoint=adjoint,
                b_forward_adjoint_replay=adjoint_first-target*Dn,
                b_adjoint_replay=Fn.transpose()*adjoint-target.transpose())


def descriptor_clock_first(*, lapse, log_lapse_first, descriptor,
                           descriptor_first, delta, delta_first):
    """Lookback proper clock d tau_minus/d lambda = -N*s/Delta.

    The extra N converts coordinate time to proper time. Signed output is
    retained: a negative clock is not accepted as positive incoming duration.
    """
    N, s, D = map(arb, (lapse, descriptor, delta))
    if not N > 0 or D.contains(0):
        raise ValueError('positive lapse and nonzero descriptor numerator required')
    if any((x.nrows(), x.ncols()) != (1, log_lapse_first.ncols())
           for x in (log_lapse_first, descriptor_first, delta_first)):
        raise ValueError('same direction family for lapse, descriptor and Delta required')
    clock = -N*s/D
    first = clock*(log_lapse_first-delta_first/D)-N*descriptor_first/D
    return clock, first


def zero_descriptor_clock_germ(*, lapse, log_lapse_first, cpsi, bpsi,
                               cpsi_first, bpsi_first):
    """Formal s=0 proper-duration coefficient a=-N/(2*c*b) and first jet.

    T_minus(A)=a*A^2+o(A^2) at an actual event. This function neither selects
    A nor establishes an event/root/history from an approximate candidate.
    """
    N, c, b = map(arb, (lapse, cpsi, bpsi))
    if not N > 0 or not c*b < 0:
        raise ValueError('incoming orientation c*b<0 and positive lapse required')
    if any((x.nrows(), x.ncols()) != (1, log_lapse_first.ncols())
           for x in (log_lapse_first, cpsi_first, bpsi_first)):
        raise ValueError('one common incoming first-direction family required')
    a = -N/(2*c*b)
    return a, a*(log_lapse_first-cpsi_first/c-bpsi_first/b)
