from fractions import Fraction
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb,arb_mat,ctx,fmpq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_physical_endpoint_hessian_errors as producer
import certify_n12_gate7_physical_endpoint_hessian_pullbacks as pullback


def contains_rational(ball,value):
    exact=fmpq(value.numerator,value.denominator)
    return ball.lower().fmpq()<=exact<=ball.upper().fmpq()


def test_stored_endpoint_pullback_contains_independent_rational_contraction():
    old=ctx.prec;ctx.prec=256
    try:
        q=np.array([[[2.,-1.],[-1.,3.]],[[1/4,1/2],[1/2,-2.]]])
        basis=np.array([[1.,2.],[1/4,-1.],[-2.,1/2]])
        tensors=[arb_mat(v.tolist()) for v in q]
        for row in range(3):
            actual=producer.stored_projected_row(tensors,basis,row)
            for output,col in np.ndindex(actual.shape):
                exact=sum((Fraction(basis[row,i])*Fraction(q[output,i,j])*Fraction(basis[row+col,j])
                           for i in range(2) for j in range(2)),Fraction(0))
                assert contains_rational(actual[output,col],exact)
    finally:ctx.prec=old


def test_projector_normalization_keeps_nonbinary_entries_enclosed():
    old=ctx.prec;ctx.prec=256
    try:
        frame=np.array([[1.,0.],[0.,1.],[2.,-1.]])
        result=producer.exact_projector_directions(frame,np.array([1.,2.]))
        exact=[[Fraction(4,5),Fraction(-2,5)],[Fraction(-2,5),Fraction(1,5)],[Fraction(2),Fraction(-1)]]
        for i,j in np.ndindex(result.shape):assert contains_rational(result[i,j],exact[i][j])
        assert not result[0,0].contains(arb(float(result[0,0])))
    finally:ctx.prec=old


def test_zero_axis_and_incompatible_stored_projection_fail_closed():
    with pytest.raises(ValueError):producer.exact_projector_directions(np.eye(2),np.zeros(2))
    with pytest.raises(ValueError):producer.stored_projected_row([arb_mat(3,3)],np.eye(2),0)
    with pytest.raises(ValueError):producer.stored_projected_row([arb_mat(2,2)],np.eye(2),2)


def test_shared_endpoint_has_both_incident_outputs_and_terminal_only_one():
    assert pullback.incident_slots(1)==[(0,'right',1),(1,'left',0)]
    assert pullback.incident_slots(369)==[(368,'right',1),(369,'left',0)]
    assert pullback.incident_slots(370)==[(369,'right',1)]
    for node in (0,371,-1):
        with pytest.raises(ValueError):pullback.incident_slots(node)
