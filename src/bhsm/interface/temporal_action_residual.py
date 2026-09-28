"""Contract the retained temporal Euler residual without another action jet.

The supplied normal equations are H psi=lambda psi and
(H-lambda I) h+b psi=rhs. Their residuals are retained explicitly. This
module does not substitute exact Euler--Lagrange stationarity for the
stored fixed-descriptor field or alter that field.
"""
from flint import arb, arb_mat
from bhsm.interface.gate7_current_action import checked


def descriptor_euler_residual(*, s, lam, b, psi, hard, norm,
                              eigen_residual, hard_residual,
                              ds, dlam, db, dpsi, dhard, dnorm,
                              deigen_residual, dhard_residual):
    """Return E=(H(b psi+s h)-s rhs)/norm and its supplied first jet.

    With common raw/action coordinate conversion, the first qdim entries
    are d_arc(L_v)-nu L_q and the remaining entries d_arc(L_m), where
    nu=dt/d_arc=s/norm. Algebraically its numerator is

      b*r_e+s*r_h+b*(lambda-s)*psi+s*lambda*h.

    On the selected fiber lambda=s and exact normal equations this is
    s^2*h. No division by s is used, including at the event s=0.
    """
    s, lam, b, norm = map(arb, (s, lam, b, norm))
    n, k = psi.nrows(), ds.ncols()
    if not norm > 0:
        raise ValueError('positive arc normalization required')
    for name, m in [('psi', psi), ('hard', hard), ('eigen residual', eigen_residual), ('hard residual', hard_residual)]:
        checked(m, n, 1, name)
    for name, m in [('ds', ds), ('dlam', dlam), ('db', db), ('dnorm', dnorm)]:
        checked(m, 1, k, name)
    for name, m in [('dpsi', dpsi), ('dhard', dhard), ('deigen residual', deigen_residual), ('dhard residual', dhard_residual)]:
        checked(m, n, k, name)
    r = b*eigen_residual+s*hard_residual+b*(lam-s)*psi+s*lam*hard
    dr = eigen_residual*db+b*deigen_residual
    dr += hard_residual*ds+s*dhard_residual
    dr += psi*((lam-s)*db+b*(dlam-ds))+b*(lam-s)*dpsi
    dr += hard*(lam*ds+s*dlam)+s*lam*dhard
    E = r/norm
    return dict(value=E, first=(dr-E*dnorm)/norm,
                numerator=r, numerator_first=dr,
                selected_fiber_term=s*s*hard/norm,
                off_fiber_and_solve_terms=(r-s*s*hard)/norm)


def temporal_source(*, qdim, euler_residual, deuler_residual,
                    multiplier_gradient, multiplier_gradient_first,
                    velocity, velocity_first, multiplier_arc_rate,
                    multiplier_arc_first, clock, clock_first):
    """First-variation integrand after temporal integration by parts.

    Returns sources on (q,v,m,t). The velocity source is zero because
    delta v is eliminated using the varied kinematic identity q'=nu*v.
    This does not remove velocity dependence from the source or adjoint.

    D integral L dt = [pi*dq_total+(L-pi*v)*dt]_ends
                       + integral source * (dY_arc,dt_arc) d_arc.
    """
    m, k = multiplier_gradient.nrows(), clock_first.ncols()
    checked(euler_residual, qdim+m, 1, 'Euler residual')
    checked(deuler_residual, qdim+m, k, 'Euler first')
    checked(multiplier_gradient, m, 1, 'L_m')
    checked(multiplier_gradient_first, m, k, 'D L_m')
    checked(velocity, qdim, 1, 'v'); checked(velocity_first, qdim, k, 'Dv')
    checked(multiplier_arc_rate, m, 1, 'm arc rate')
    checked(multiplier_arc_first, m, k, 'D m arc rate')
    nu = arb(clock)
    eq = arb_mat(qdim, 1, euler_residual.entries()[:qdim])
    deq = arb_mat(deuler_residual.tolist()[:qdim])
    sm = nu*multiplier_gradient
    dsm = multiplier_gradient*clock_first+nu*multiplier_gradient_first
    st = (eq.transpose()*velocity-multiplier_gradient.transpose()*multiplier_arc_rate)[0, 0]
    dst = velocity.transpose()*deq+eq.transpose()*velocity_first
    dst -= multiplier_arc_rate.transpose()*multiplier_gradient_first+multiplier_gradient.transpose()*multiplier_arc_first
    return dict(state=arb_mat((-eq).tolist()+arb_mat(qdim, 1).tolist()+sm.tolist()),
                state_first=arb_mat((-deq).tolist()+arb_mat(qdim, k).tolist()+dsm.tolist()),
                time=arb_mat([[st]]), time_first=dst)
