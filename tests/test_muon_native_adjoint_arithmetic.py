from fractions import Fraction
import numpy as np
import pytest
from flint import ctx
from bhsm.interface.muon_native_adjoint_arithmetic import certify_native_adjoint_contractions


def test_exact_rational_consumed_pairings_and_context_restore():
    A=np.array([[2.,1.],[1.,3.]]);F=np.array([[1.,2.,-1.],[3.,0.,2.]])
    L=np.array([[1.,-2.],[2.,1.]])
    exact=[[Fraction(-2),Fraction(2),Fraction(-3)],
        [Fraction(1),Fraction(2),Fraction(-1)]]
    previous=ctx.prec;a=certify_native_adjoint_contractions(A,F,L)
    assert ctx.prec==previous
    for i,row in enumerate(exact):
        for j,value in enumerate(row):
            assert Fraction(float(a['contraction_lower'][i,j]))<=value<=Fraction(float(a['contraction_upper'][i,j]))
    assert a['stored_operator_certified_invertible']
    assert a['independent_first_column_intervals_overlap']
    assert a['exact_stored_adjoint_residual_upper']<1e-50
    assert not a['physical_source_target_formation_or_Pauli_error_enclosed']


def test_certification_rejects_singular_stored_operator():
    with pytest.raises((ValueError,ZeroDivisionError,ArithmeticError)):
        certify_native_adjoint_contractions(np.array([[1.,1.],[2.,2.]]),np.ones((2,1)),np.ones((1,2)))


def test_null_or_nonfinite_load_is_not_a_zero():
    with pytest.raises(ValueError):
        certify_native_adjoint_contractions(np.eye(2),None,np.ones((1,2)))
    with pytest.raises(ValueError):
        certify_native_adjoint_contractions(np.eye(2),np.array([[np.nan],[0.]]),np.ones((1,2)))
