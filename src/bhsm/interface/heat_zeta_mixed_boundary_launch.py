"""Only the seven boundary by 73 launch contractions, not a full Hessian.

Every numerical routine is conditional on supplied, co-based owned inputs.
No native output covector is reinterpreted as a boundary direction; no local
border is substituted for the complete internal stationarity system.
"""
from math import factorial
from flint import arb, arb_mat
from bhsm.interface.joint_boundary_port_reduction import reduce_seven_port

OBJECT = 'CURRENT_CENTER_HEAT_ZETA_MIXED_BOUNDARY_LAUNCH_JET_7x73'


def exponential_moment(delta, degree, terms=32):
    """Outward integral_0^1 u^degree exp(-delta*u) du, including delta=0."""
    delta=arb(delta)
    if degree < 0 or terms < 2 or not abs(delta) <= 1:
        raise ValueError('small-difference moment chart requires |delta|<=1')
    result=arb(0);power=arb(1)
    for k in range(terms):
        result+=power/(factorial(k)*(k+degree+1))
        power*=(-delta)
    magnitude=abs(delta).upper()
    tail=magnitude**terms*magnitude.exp()/(factorial(terms)*(terms+degree+1))
    return result+arb(0,tail.upper())


def heat_divided_difference(x, y, heat_length=1):
    """q[x,y] for q(t)=exp(-ell^2*t)/(2t), without a spectral-gap divisor."""
    x,y,ell=arb(x),arb(y),arb(heat_length)
    if not x>0 or not y>0 or not ell>0:
        raise ValueError('strictly positive spectral enclosures and heat length required')
    a=ell*ell;delta=a*(y-x)
    if abs(delta)<=1:
        moment=exponential_moment(delta,0)
    elif not delta.contains(0):
        moment=-(-delta).expm1()/delta
    else:
        # Monotonicity of the integral in delta, including a wide crossing.
        low,high=delta.lower(),delta.upper()
        def endpoint(t):
            return exponential_moment(t,0) if abs(t)<=1 else -(-t).expm1()/t
        lo,hi=endpoint(high).lower(),endpoint(low).upper()
        moment=(lo+hi)/2+arb(0,((hi-lo)/2).upper())
    return -(-a*x).exp()*(1+a*x*moment)/(2*x*y)


def heat_pair_7x73(eigenvalues, boundary_first, launch_first, heat_length=1):
    """Tr(DQ[P_j] P_ba) in a supplied certified common real spectral frame.

    Eigenvalues alone do not certify that frame: caller must own the operator,
    its frame and all jets. This is a conditional contraction, not an eigensolve.
    It streams spectral entries and never allocates a mixed operator tensor.
    """
    n=len(eigenvalues)
    if len(boundary_first)!=7 or len(launch_first)!=73 or n<1:
        raise ValueError('exactly seven boundary and 73 launch first jets required')
    if any((m.nrows(),m.ncols())!=(n,n) for m in list(boundary_first)+list(launch_first)):
        raise ValueError('first jets must share the owned spectral frame')
    result=arb_mat(7,73)
    for k,x in enumerate(eigenvalues):
        for l,y in enumerate(eigenvalues):
            weight=heat_divided_difference(x,y,heat_length)
            b=arb_mat(7,1,[m[l,k] for m in boundary_first])
            p=arb_mat(1,73,[m[k,l] for m in launch_first])
            result+=(b*p)*weight
    return result


def element_mixed(*, x, h, xb, xp, xbp, hb, hp, hbp,
                  channel, value, chirality=1):
    """One mixed directional action-form jet of the existing AE2 element.

    x is midpoint log radius. xbp/hbp are required inputs, not default zeros.
    Returned K_bp,M_bp are form jets; K alone is not the heat operator.
    """
    x,h,xb,xp,xbp,hb,hp,hbp,value=map(arb,(x,h,xb,xp,xbp,hb,hp,hbp,value))
    if not h>0 or not value>=0:raise ValueError('positive duration and nonnegative mode required')
    S=arb_mat([[1,-1],[-1,1]]);A=arb_mat([[2,1],[1,2]]);C=arb_mat([[-1,0],[0,1]])
    W=arb(0)
    if channel=='scalar':V=value*(-2*x).exp()
    elif channel=='product_Dirac' and chirality in (-1,1):
        W=chirality*value*(-x).exp();V=W*W
    else:raise ValueError('owned scalar or signed product_Dirac channel required')
    Vb=-2*V*xb;Vp=-2*V*xp;Vbp=V*(4*xb*xp-2*xbp)
    kinetic=S*(2*hb*hp/(h*h*h)-hbp/(h*h))
    potential=A*((h*Vbp+hb*Vp+hp*Vb+V*hbp)/6)
    factorized=C*(W*(xb*xp-xbp))
    return dict(K_bp=kinetic+potential+factorized,M_bp=A*(hbp/6),
                kinetic=kinetic,potential=potential,factorized=factorized)


def zeta_element_mixed(*, xl, xr, h, xb, xp, xbp, hb, hp, hbp):
    """Exact mixed jet of -59/30*h*integral exp(-linear x) on one element."""
    xl,xr,h,hb,hp,hbp=map(arb,(xl,xr,h,hb,hp,hbp))
    if not h>0:raise ValueError('positive proper duration required')
    if any(len(v)!=2 for v in (xb,xp,xbp)):raise ValueError('two endpoint jets required')
    b0,b1=map(arb,xb);p0,p1=map(arb,xp);c0,c1=map(arb,xbp)
    db=b1-b0;dp=p1-p0;dc=c1-c0
    polynomials=[h*(b0*p0-c0)-hb*p0-hp*b0+hbp,
                 h*(b0*dp+db*p0-dc)-hb*dp-hp*db,h*db*dp]
    return -(arb(59)/30)*(-xl).exp()*sum(
        (v*exponential_moment(xr-xl,k) for k,v in enumerate(polynomials)),arb(0))


def reduce_mixed_reactions(*, pair, mixed_operator_trace, zeta_mixed,
                           Gamma_bn, F_n, F_p, moving_seed):
    """Stationary-envelope Schur/adjoint reduction with both seed conventions.

    Requires F=Gamma_n (or the corresponding owned bordered stationary action)
    and boundary reactions Gamma_b. For arbitrary constraints use the Lagrange
    adjoint Hessian identity instead; this shortcut is not valid in general.
    mixed_operator_trace is the streamed Tr(Q P_ba,pj), not a tensor.
    """
    if mixed_operator_trace is None:
        raise ValueError(OBJECT+': genuine mixed operator contraction required')
    for value in (pair,mixed_operator_trace,zeta_mixed,moving_seed):
        if (value.nrows(),value.ncols())!=(7,73):raise ValueError('7x73 contractions required')
    if F_p.ncols()!=73:raise ValueError('73 common launch columns required')
    direct=pair+mixed_operator_trace-zeta_mixed
    result=reduce_seven_port(F_n,F_p,{'joint_history':{'p':direct,'n':Gamma_bn}})
    result.update(ordinary_reaction_derivative=result['reduced']+moving_seed,
                  requested_minus_seed_convention=result['reduced']-moving_seed,
                  moving_seed=moving_seed)
    return result


def implicit_objective_adjoint(F_n, Gamma_n):
    """L=Gamma-eta^T F with F_n^T eta=Gamma_n^T at the common base."""
    if Gamma_n.nrows()!=1 or Gamma_n.ncols()!=F_n.nrows():
        raise ValueError('one objective-normal row required')
    eta=F_n.transpose().solve(Gamma_n.transpose())
    return eta,F_n.transpose()*eta-Gamma_n.transpose()


def reduce_implicit_mixed(*, L_bp, L_bn, L_np, L_nn, F_n, F_b, F_p):
    """General history-sector objective on an implicit full-system graph.

    L_uv=Gamma_uv-eta^T F_uv, with eta supplied by the objective adjoint.
    All four L blocks must include those contractions. Seven boundary solves
    and seven adjoint solves avoid forming either Phi_bp or 73 normal solves.
    The result is the fixed-seed Hessian; add the owned moving-seed term later.
    """
    n=F_n.nrows()
    required=((L_bp,7,73),(L_bn,7,n),(L_np,n,73),(L_nn,n,n),
              (F_n,n,n),(F_b,n,7),(F_p,n,73))
    if any((v.nrows(),v.ncols())!=(r,c) for v,r,c in required):
        raise ValueError('common internal frame and 7x73 mixed blocks required')
    Phi_b=-F_n.solve(F_b)
    combined_normal=L_bn+Phi_b.transpose()*L_nn
    adjoint=F_n.transpose().solve(combined_normal.transpose())
    reduced=L_bp+Phi_b.transpose()*L_np-adjoint.transpose()*F_p
    return dict(reduced=reduced,boundary_normal=Phi_b,adjoint=adjoint,
                boundary_replay=F_n*Phi_b+F_b,
                adjoint_replay=F_n.transpose()*adjoint-combined_normal.transpose())
