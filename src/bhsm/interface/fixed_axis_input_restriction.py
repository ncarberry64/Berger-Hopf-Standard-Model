"""Restrict a homogeneous input model while retaining all auxiliary symbols."""
from flint import arb, arb_mat
from bhsm.interface.input_linear_taylor import InputLinearTaylor, vector_norm


def restrict_physical_axis(value, axis, physical_dimension=74, auxiliary_scales=None):
    """Replace u by t*axis, retaining every correction coordinate and tail.

    The remainder is homogeneous in all input coordinates. If the exact
    retained axis has norm slightly above one, its enlargement is charged.
    State parameters and their original groups are untouched.
    """
    if (axis.nrows()!=physical_dimension or axis.ncols()!=1
            or any(not v.is_finite() for v in axis.entries())
            or tuple(map(tuple,value.input_groups)) != ((0,physical_dimension,'euclidean'),
                (physical_dimension,value.c.ncols(),'box'))):
        raise ValueError('one physical Euclidean block and its complete auxiliary box required')
    auxiliary=value.c.ncols()-physical_dimension
    scales=[arb(1)]*auxiliary if auxiliary_scales is None else [arb(v) for v in auxiliary_scales]
    if len(scales)!=auxiliary or any(not v.is_finite() or not v>=0 for v in scales):
        raise ValueError('one finite nonnegative scale per auxiliary coordinate required')
    columns=1+auxiliary
    transform=arb_mat(value.c.ncols(),columns)
    for i in range(physical_dimension):
        transform[i,0]=axis[i,0]
    for i in range(auxiliary):
        transform[physical_dimension+i,1+i]=scales[i]
    gauge=max(vector_norm(axis.entries()),*[abs(v).upper() for v in scales])
    return InputLinearTaylor(value.domain,value.c*transform,value.a*transform,
        (value.r*gauge).upper(),[(0,1,'euclidean'),(1,columns,'box')])
