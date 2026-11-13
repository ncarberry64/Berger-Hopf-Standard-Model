"""Independent indefinite exact-rational checks of the arithmetic bound."""
from fractions import Fraction

import numpy as np
import pytest

from bhsm.interface.muon_frozen_normal_schur_certificate import certify_frozen_normal_contraction


@pytest.mark.parametrize('perturbation',[0.,1e-4,.1])
def test_indefinite_exact_rational_target_is_enclosed(perturbation):
    k=np.array([[2.,1.],[1.,-3.]])
    b=np.array([1.,2.])
    delta=np.array([-5/7,3/7])+perturbation*np.array([2.,-1.])
    result=certify_frozen_normal_contraction(k,b,7.,delta)
    exact=Fraction(50,7)
    low,high=(Fraction.from_float(x) for x in result['response_z_interval'])
    assert low<=exact<=high
    assert result['Neumann_preconditioner_defect_upper']<1e-12
    assert not result['positive_internal_operator_assumed']


def test_bad_inverse_cannot_produce_a_certificate():
    with pytest.raises(ArithmeticError,match='Neumann'):
        certify_frozen_normal_contraction(np.diag([1.,-1.]),np.ones(2),0.,np.ones(2),
                                         inverse_preconditioner=np.zeros((2,2)))


def test_singular_and_asymmetric_blocks_are_rejected():
    with pytest.raises(ArithmeticError,match='inverse preconditioner'):
        certify_frozen_normal_contraction(np.diag([1.,0.]),np.ones(2),0.,np.ones(2))
    with pytest.raises(ValueError,match='symmetric'):
        certify_frozen_normal_contraction(np.array([[1.,2.],[1.,-1.]]),np.ones(2),0.,np.ones(2))
