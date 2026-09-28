"""Same-action constrained formation stationarity and its shared first jet.

All Gamma blocks must be the internally reduced joint-history objective,
with its owned duration, reset, contact and operator dependence. A local
Lagrangian gradient at the terminal point is not that objective gradient.
"""
from flint import arb_mat


def assemble_stationarity(*, constraints, constraint_y, constraint_p,
                          multipliers, action_y, action_yy, action_yp,
                          constraint_yy, constraint_yp):
    """Assemble F=[Gamma_y+R_y^T mu; R], K=F_(y,mu), and F_p.

    Moving reset normals contribute mu*R_yy and mu*R_yp. Omitting them
    would differentiate a different problem even when R=0 at the center.
    No missing action or constraint derivative defaults to zero.
    """
    required=(constraints,constraint_y,constraint_p,multipliers,action_y,
              action_yy,action_yp,constraint_yy,constraint_yp)
    if any(x is None for x in required):
        raise ValueError('complete current joint-action and reset derivatives required')
    m,n=constraint_y.nrows(),constraint_y.ncols();p=constraint_p.ncols()
    checks=((constraints,m,1),(multipliers,m,1),(constraint_p,m,p),
            (action_y,n,1),(action_yy,n,n),(action_yp,n,p))
    if any((x.nrows(),x.ncols())!=(a,b) for x,a,b in checks):
        raise ValueError('shared action/reset coordinates required')
    if len(constraint_yy)!=m or len(constraint_yp)!=m:
        raise ValueError('one explicit curvature block per reset equation required')
    if any(x is None or (x.nrows(),x.ncols())!=(n,n) for x in constraint_yy):
        raise ValueError('complete normal curvature required')
    if any(x is None or (x.nrows(),x.ncols())!=(n,p) for x in constraint_yp):
        raise ValueError('complete mixed normal curvature required')
    H=arb_mat(action_yy.tolist());mixed=arb_mat(action_yp.tolist())
    for i in range(m):
        H+=constraint_yy[i]*multipliers[i,0]
        mixed+=constraint_yp[i]*multipliers[i,0]
    stationary=action_y+constraint_y.transpose()*multipliers
    K=arb_mat(n+m,n+m)
    for i in range(n):
        for j in range(n):K[i,j]=H[i,j]
        for j in range(m):K[i,n+j]=constraint_y[j,i];K[n+j,i]=constraint_y[j,i]
    return dict(residual=arb_mat(stationary.tolist()+constraints.tolist()),
        jacobian=K,forcing=arb_mat(mixed.tolist()+constraint_p.tolist()),
        constrained_hessian=H)


def stationary_first_jet(system,*,owned_border=None):
    """Differentiate an established stationary base, optionally in an owned slice.

    The caller must establish base stationarity. If a physical/gauge/time
    null remains, its authorized border and parameter forcing must be supplied;
    this function never silently takes a pseudoinverse or fixes a microstate.
    """
    K,F=system['jacobian'],system['forcing'];n=K.nrows()
    if owned_border is None:
        response=-K.solve(F)
        return dict(response=response,replay=K*response+F)
    columns=owned_border.get('columns');rows=owned_border.get('rows')
    forcing=owned_border.get('forcing');owner=owned_border.get('owner')
    if not owner or any(x is None for x in (columns,rows,forcing)):
        raise ValueError('explicit action-owned quotient/parameter border required')
    k=columns.ncols()
    if columns.nrows()!=n or (rows.nrows(),rows.ncols())!=(k,n) or (forcing.nrows(),forcing.ncols())!=(k,F.ncols()):
        raise ValueError('matching owned border and shared parameter columns required')
    bordered=arb_mat(n+k,n+k)
    for i in range(n):
        for j in range(n):bordered[i,j]=K[i,j]
        for j in range(k):bordered[i,n+j]=columns[i,j];bordered[n+j,i]=rows[j,i]
    total_F=arb_mat(F.tolist()+forcing.tolist())
    response=-bordered.solve(total_F)
    return dict(response=response,replay=bordered*response+total_F,border_owner=owner)
