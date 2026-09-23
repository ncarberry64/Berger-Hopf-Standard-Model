"""Signed polynomial restriction of the existing HS history equations.

This is a composition kernel. A physical rate supplied as a polynomial model
still needs its uniform value/derivative tails, implicit branch and domain
certificates. The kernel does not declare any such tail to be zero.
"""
from flint import arb, arb_mat
from bhsm.interface.shared_parameter_residual import PolynomialMatrix


def scale(poly, value):
    return PolynomialMatrix({k:a*value for k,a in poly.terms.items()},
                            poly.rows,poly.cols,poly.parameters)


def derivative(poly, parameter):
    """Exact formal derivative, combining matching shared monomials first."""
    if type(parameter) is not int or not 0 <= parameter < poly.parameters:
        raise ValueError('a parameter in the common namespace is required')
    terms={}
    for key,value in poly.terms.items():
        count=key.count(parameter)
        if count:
            position=key.index(parameter)
            new_key=key[:position]+key[position+1:]
            term=value*count
            terms[new_key]=terms[new_key]+term if new_key in terms else term
    return PolynomialMatrix(terms,poly.rows,poly.cols,poly.parameters)


def history_residuals(endpoints, steps, rate):
    """Compose the actual midpoint relation BEFORE forming residual polynomials.

    Each endpoint polynomial occurs once in the common namespace and is reused
    in both incident intervals. `rate` owns its action/approximation semantics.
    Independent midpoint coordinates are never introduced here.
    """
    if len(endpoints)!=len(steps)+1 or not steps:
        raise ValueError('complete ordered endpoint history and steps required')
    signature=(endpoints[0].rows,1,endpoints[0].parameters)
    if any((z.rows,z.cols,z.parameters)!=signature for z in endpoints):
        raise ValueError('matching shared endpoint polynomials required')
    fields=[rate(z) for z in endpoints]
    if any((f.rows,f.cols,f.parameters)!=signature for f in fields):
        raise ValueError('matching rate polynomial required')
    residuals=[];midpoints=[]
    for i,step in enumerate(steps):
        h=arb(step)
        if not h.is_finite() or not h.rad().is_zero() or not h>0:
            raise ValueError('positive exact HS step required')
        midpoint=scale(endpoints[i]+endpoints[i+1],arb('0.5'))+scale(fields[i]-fields[i+1],h/8)
        fm=rate(midpoint)
        if (fm.rows,fm.cols,fm.parameters)!=signature:
            raise ValueError('matching actual-midpoint rate polynomial required')
        residual=endpoints[i+1]-endpoints[i]-scale(fields[i]+scale(fm,4)+fields[i+1],h/6)
        midpoints.append(midpoint);residuals.append(residual)
    return midpoints,residuals


def causal_pullback(residuals, causal_maps, frozen_pullbacks):
    """Return y_(i+1)=C_i*y_i-B_i*r_i as shared polynomials, with y_0=0.

    No support is taken inside the recurrence. Matrices may be outward Arb
    enclosures, but callers still own the frozen-map perturbation certificate.
    """
    if not residuals or len(causal_maps)!=len(residuals) or len(frozen_pullbacks)!=len(residuals):
        raise ValueError('complete causal maps and residual pullbacks required')
    p=residuals[0].parameters
    n=causal_maps[0].nrows()
    value=PolynomialMatrix({},n,1,p)
    result=[value]
    for residual,c,b in zip(residuals,causal_maps,frozen_pullbacks,strict=True):
        if (residual.cols!=1 or residual.parameters!=p or c.nrows()!=n or c.ncols()!=n
                or b.nrows()!=n or b.ncols()!=residual.rows):
            raise ValueError('matching complete shared causal graph required')
        cm=PolynomialMatrix({():c},n,n,p)
        bm=PolynomialMatrix({():b},n,residual.rows,p)
        value=cm@value-bm@residual
        result.append(value)
    return result


def projected_second(history, projection, first_parameter, second_parameter):
    """One exact restricted polynomial Hessian entry; no physical tail implied."""
    p=history.parameters
    project=PolynomialMatrix({():projection},projection.nrows(),projection.ncols(),p)
    return project@derivative(derivative(history,first_parameter),second_parameter)
