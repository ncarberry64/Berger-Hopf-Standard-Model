"""Pointwise common-input substitution in all state-affine coefficients.

This is a value enclosure only. The interval maps may depend on the state;
neither the resulting constant nor state-affine coefficients may be used as
derivatives. Original error coordinates remain as zero dummy columns.
"""
from flint import arb, arb_mat
from bhsm.interface.input_linear_taylor import InputLinearTaylor, vector_norm
from bhsm.interface.common_input_error_pullback import pullback_constant_coefficients


def pullback_all_errors(value,maps,physical_dimension=74):
    if (list(value.input_groups[0])!=[0,physical_dimension,'euclidean']
            or any(kind!='box' for _,_,kind in value.input_groups[1:])):
        raise ValueError('one physical sphere and auxiliary error boxes required')
    maps=list(maps)
    c=pullback_constant_coefficients(value.c,maps,physical_dimension)
    used={j for offset,matrix in maps for j in range(offset,offset+matrix.nrows())}
    if used!=set(range(physical_dimension,value.c.ncols())):
        raise ValueError('every auxiliary error coordinate must have a common-input map')
    a=arb_mat(value.domain.dimension,value.c.ncols())
    for i in range(value.domain.dimension):
        for j in range(physical_dimension): a[i,j]=value.a[i,j]
    gauge=arb(1)
    for offset,matrix in maps:
        if any(not v.is_finite() for v in matrix.entries()): raise ValueError('finite error maps required')
        gauge=max(gauge,max(vector_norm([matrix[i,j] for j in range(physical_dimension)])
                            for i in range(matrix.nrows())))
        correction=arb_mat(value.domain.dimension,matrix.nrows(),
            [value.a[i,j] for i in range(value.domain.dimension)
             for j in range(offset,offset+matrix.nrows())])*matrix
        for i in range(value.domain.dimension):
            for j in range(physical_dimension): a[i,j]+=correction[i,j]
    return InputLinearTaylor(value.domain,c,a,value.r*gauge,value.input_groups)
