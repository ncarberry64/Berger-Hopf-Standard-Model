"""Preserve signs across scalar longitudinal blocks before norm support."""
from itertools import product
from flint import arb


def grouped_range(domain,c,a,q):
    """Exact vertex hull for a multi-affine scalar block, ball norms elsewhere.

    A diagonal scalar square can have an interior extremum; those cases use
    the domain's exact one-dimensional quadratic bounds instead. The frozen
    mixed u/v targets have no scalar squares and only six interval variables,
    so their entire longitudinal block costs at most 64 vertex evaluations.
    """
    scalars=[start for start,stop,kind in domain.groups if kind=='interval']
    scalar_set=set(scalars)
    if len(scalars)>12 or any(i==j and i in scalar_set for i,j in q):
        return domain.polynomial_range(c,a,q)
    scalar_q={key:v for key,v in q.items() if key[0] in scalar_set and key[1] in scalar_set}
    scalar_a={i:v for i,v in a.items() if i in scalar_set}
    rest_q={key:v for key,v in q.items() if key not in scalar_q}
    rest_a={i:v for i,v in a.items() if i not in scalar_set}
    values=[]
    for signs in product((-1,1),repeat=len(scalars)):
        x=dict(zip(scalars,signs))
        values.append(c+sum((v*x[i] for i,v in scalar_a.items()),arb(0))
                        +sum((v*x[i]*x[j] for (i,j),v in scalar_q.items()),arb(0)))
    lo=min(v.lower() for v in values);hi=max(v.upper() for v in values)
    rest,structure=domain.polynomial_range(arb(0),rest_a,rest_q)
    structure.append(dict(parameters=scalars,monomials=len(scalar_q),
                          method='exact_multiaffine_scalar_vertex_hull',vertices=len(values),
                          lower=str(lo.fmpq()),upper=str(hi.fmpq())))
    return (lo+hi)/2+arb(0,((hi-lo)/2).upper())+rest,structure
