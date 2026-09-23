"""Shared Taylor residuals for implicit second variations and normalization.

The caller supplies an already certified inverse defect on the same domain.
Neither a point inverse nor an eigenvector value enclosure supplies that proof
or derivatives of an implicit solution. Every derivative operand is explicit.
"""
from flint import arb
from bhsm.interface.shared_action_taylor import Taylor


def dot(left, right):
    if len(left) != len(right) or not left:
        raise ValueError('matching nonempty vectors required')
    return sum((a*b for a,b in zip(left,right,strict=True)), 0)


def matvec(matrix, vector):
    if not matrix or any(len(row)!=len(vector) for row in matrix):
        raise ValueError('matching complete matrix and vector required')
    return [dot(row,vector) for row in matrix]


def _domain(values):
    if not values or not all(isinstance(v,Taylor) for v in values):
        raise ValueError('complete shared Taylor operands required')
    d=values[0].domain
    if any(v.domain is not d for v in values):
        raise ValueError('one common physical parameter namespace required')
    return d


def solve(matrix, rhs, preconditioner, weights, defect_upper):
    """Enclose K(theta)^-1 b(theta) about an exact affine predictor.

    Requires sup ||I-R K(theta)||_w <= q < 1, R exact and square. The
    predictor is a choice, not a narrowing of any certified solution: take
    midpoint constant/linear coefficients of R*b and prove its full residual.
    Return signed coefficients and a certified tail, never a solution box.
    """
    n=len(rhs)
    if len(matrix)!=n or any(len(row)!=n for row in matrix):
        raise ValueError('complete square physical operator required')
    _domain(list(rhs)+[v for row in matrix for v in row])
    return solve_with_operator(rhs,lambda v:matvec(matrix,v),preconditioner,weights,defect_upper)


def solve_with_operator(rhs,apply_operator,preconditioner,weights,defect_upper):
    """Residual solve with matrix-free action on the affine predictor.

    The supplied action must enclose the SAME linear K certified by q. This
    permits contracted action Hessians without forming all matrix entries.
    """
    n=len(rhs)
    domain=_domain(list(rhs))
    if preconditioner.nrows()!=n or preconditioner.ncols()!=n or len(weights)!=n:
        raise ValueError('matching frozen inverse and weights required')
    r=list(weights);q=arb(defect_upper)
    if (any(not v.is_finite() or not v.rad().is_zero() for v in preconditioner.entries())
            or any(not v.is_finite() or not v.rad().is_zero() or not v>0 for v in r)
            or not q.is_finite() or not q>=0 or not q<1):
        raise ValueError('exact frozen preconditioner, positive weights and q<1 required')
    R=[[preconditioner[i,j] for j in range(n)] for i in range(n)]
    proposal=matvec(R,rhs)
    predictor=[domain.affine(v.c.mid(),[a.mid() for a in v.a.entries()]) for v in proposal]
    applied=apply_operator(predictor)
    if len(applied)!=n or _domain(list(rhs)+list(applied)) is not domain:
        raise ValueError('complete same-domain operator action required')
    residual=[b-a for b,a in zip(rhs,applied,strict=True)]
    residual=matvec(R,residual)
    eta=max((v.support()/w).upper() for v,w in zip(residual,r,strict=True))
    rho=(eta/(1-q)).upper()
    enclosed=[Taylor(domain,p.c,p.a,(w*rho).upper()) for p,w in zip(predictor,r,strict=True)]
    return enclosed,dict(weighted_residual_upper=eta,weighted_correction_upper=rho,
        reused_inverse_defect_upper=q,preconditioned_residual_models=residual,
        joint_domain_inverse_defect_requires_frozen_certificate=True)


def mixed_response(K,Ku,Kv,Kuv,Fuv,x,xu,xv,preconditioner,weights,defect_upper):
    """K*x_uv=F_uv-K_uv*x-K_u*x_v-K_v*x_u, including border coordinates.

    All terms are combined as shared models before the residual is bounded.
    Supplying a value model in place of a certified derivative is invalid;
    this routine deliberately never differentiates a Taylor value enclosure.
    """
    n=len(x)
    if any(len(v)!=n for v in (xu,xv,Fuv)):
        raise ValueError('complete primal, both first variations and forcing required')
    _domain(list(x)+list(xu)+list(xv)+list(Fuv)+[v for A in (K,Ku,Kv,Kuv) for row in A for v in row])
    terms=[matvec(Kuv,x),matvec(Ku,xv),matvec(Kv,xu)]
    rhs=[Fuv[i]-terms[0][i]-terms[1][i]-terms[2][i] for i in range(n)]
    result,proof=solve(K,rhs,preconditioner,weights,defect_upper)
    proof['complete_mixed_rhs_models']=rhs
    return result,proof


def normalized_mixed(U,Uu,Uv,Uuv,physical_components):
    """Differentiate nu^2=N.N and f=U/nu using one common numerator jet.

    N is the physical-state part of U; the descriptor component is NOT used
    in its normalization. Uniform positivity is checked on this same model.
    """
    if not 0<physical_components<=len(U) or any(len(v)!=len(U) for v in (Uu,Uv,Uuv)):
        raise ValueError('matching complete numerator jets and physical prefix required')
    domain=_domain(list(U)+list(Uu)+list(Uv)+list(Uuv))
    N,Nu,Nv,Nuv=[list(v[:physical_components]) for v in (U,Uu,Uv,Uuv)]
    squared=dot(N,N)
    if not squared.enclosure()>0:
        raise ArithmeticError('positive normalization on the original domain required')
    nu=(squared.log()*arb('0.5')).exp()
    nuu=dot(N,Nu)/nu;nuv=dot(N,Nv)/nu
    nuuv=(dot(Nu,Nv)+dot(N,Nuv)-nuu*nuv)/nu
    result=[d/nu-(a*nuv+b*nuu+c*nuuv)/nu**2+2*c*nuu*nuv/nu**3
            for c,a,b,d in zip(U,Uu,Uv,Uuv,strict=True)]
    return result,dict(norm=nu,norm_u=nuu,norm_v=nuv,norm_uv=nuuv,
                       normalization_from_shared_equation=True)
