"""Retain the common physical input in constant directional-error terms.

The original input-linear enclosure is valid for v=(u,eta), with eta in a
box. If eta=E(theta)u for an interval matrix E, replace c_eta eta by the
interval row c_eta E times u. Keep every state-times-eta coefficient and
the original nonlinear remainder. This is a pointwise interval-affine
enclosure; the interval constant coefficients must not be differentiated.
"""
from flint import arb,arb_mat
from bhsm.interface.input_linear_taylor import InputLinearTaylor


def pullback_constant_coefficients(original,maps,physical_dimension=74):
    if original.nrows()!=1 or original.ncols()<physical_dimension:
        raise ValueError('complete input coefficient row required')
    constant=arb_mat(1,original.ncols(),original.entries())
    used=set()
    for offset,matrix in maps:
        slots=list(range(offset,offset+matrix.nrows()))
        if (not slots or matrix.ncols()!=physical_dimension or offset<physical_dimension
                or slots[-1]>=original.ncols() or used.intersection(slots)):
            raise ValueError('disjoint complete directional-error input blocks required')
        used.update(slots)
        correction=arb_mat(1,matrix.nrows(),[original[0,j] for j in slots])*matrix
        for j in range(physical_dimension): constant[0,j]+=correction[0,j]
        for j in slots: constant[0,j]=arb(0)
    return constant


def pullback_constant_errors(value,maps,physical_dimension=74):
    if list(value.input_groups[0])!=[0,physical_dimension,'euclidean']:
        raise ValueError('one unchanged physical input sphere required')
    constant=pullback_constant_coefficients(value.c,maps,physical_dimension)
    return InputLinearTaylor(value.domain,constant,value.a,value.r,value.input_groups)
