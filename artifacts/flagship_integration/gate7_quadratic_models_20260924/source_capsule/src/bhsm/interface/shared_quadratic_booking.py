"""Frozen LL/LT booking in the same physical degree-two monomial namespace."""
from flint import arb
from bhsm.interface.sparse_quadratic_enclosure import accumulate,clean


def projected_booking(blocks, projection, rL, rT):
    """Project first, fuse symmetric endpoint/direction keys, then support.

    projection is one row on the frozen 74-dimensional Newton residual.
    LL/LT inputs already contain the Taylor half Hessian convention.
    """
    if projection.nrows()!=1:
        raise ValueError('one signed output projection required')
    out={}
    for endpoints in ('00','01','10','11'):
        a,b=map(int,endpoints)
        ll=projection*blocks['LL'][endpoints]
        lt=projection*blocks['LT'][endpoints]
        for i,j in ((150+75*a,300+75*b),(300+75*a,150+75*b)):
            accumulate(out,tuple(sorted((i,j))),ll[0,0]*rL*rL)
        for j in range(lt.ncols()):
            for i,k in ((150+75*a,301+75*b+j),(300+75*a,151+75*b+j)):
                accumulate(out,tuple(sorted((i,k))),2*rL*rT*lt[0,j])
    return clean(out)
