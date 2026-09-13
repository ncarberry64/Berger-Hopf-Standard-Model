"""Compare the component enclosure to independently solved fixed systems."""
import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.componentwise_weighted_response import enclose_response_rows
from bhsm.interface.weighted_response_enclosure import enclose_response


def test_component_bound_contains_actual_solution_and_improves_unused_rows():
    previous=ctx.prec;ctx.prec=256
    try:
        z=[arb(1)/4,-arb(1)/8];r=[arb(1),arb(4)];V=[arb(1)/2,arb(1)/2]
        e=[arb(1,arb(1)/64),arb(1)/8]
        box,proof=enclose_response_rows(z,e,r,V)
        old,_=enclose_response(z,e,r,V)
        # I-RJ is diag(1/2,1/8), with R=I here.
        J=arb_mat([[arb(1)/2,arb(0)],[arb(0),arb(7)/8]])
        for first in (e[0].lower(),e[0].upper()):
            exact=J.solve(arb_mat(2,1,[first,e[1]]))
            assert all(box[i].contains(z[i]+exact[i,0]) for i in range(2))
        assert box[1].rad()<old[1].rad()/4
        assert proof['componentwise_residual_plus_defect_bound'] is True
    finally:ctx.prec=previous


def test_noncontractive_rows_still_fail_closed():
    with pytest.raises(ArithmeticError,match='strict weighted contraction'):
        enclose_response_rows([arb(0)],[arb(1)],[arb(1)],[arb(1)])
