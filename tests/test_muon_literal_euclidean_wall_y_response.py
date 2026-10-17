"""CONTROL_ONLY exact operator recurrence and energy-contact algebra."""
import numpy as np
import pytest
from bhsm.interface.muon_literal_euclidean_wall_y_response import inverse_polynomial_coefficients


def test_control_general_complex_recurrence_retains_odd_and_both_quadratic_products():
    A=np.array([[3+.2j,.4-.1j],[.1+.3j,2-.2j]])
    B=np.array([[.3,.7j],[-.4,.2]]);C=np.array([[.1,.2],[.3j,-.2]])
    G=inverse_polynomial_coefficients(A,B,C,order=4)
    np.testing.assert_allclose(A@G[0],np.eye(2),atol=2e-16)
    for j in range(1,5):
        np.testing.assert_allclose(A@G[j]+B@G[j-1]+(C@G[j-2]if j>1 else 0),0,atol=8e-17)
    assert np.linalg.norm(G[1])>.05
    assert np.linalg.norm(G[2]-(G[0]@B@G[0]@B@G[0]-G[0]@C@G[0]))<1e-16
    y=.01;exact=np.linalg.inv(A+y*B+y*y*C);approx=sum(y**j*g for j,g in enumerate(G))
    assert np.linalg.norm(exact-approx)<5e-12


def test_control_missing_quadratic_operand_never_zero_filled():
    with pytest.raises(ValueError):inverse_polynomial_coefficients(np.eye(2),np.eye(2),None,order=2)


def test_control_analytic_energy_dual_uses_opposite_real_signs_without_conjugating_left():
    L=np.array([[1+.3j,.2j]]);R=np.array([[.7j],[-.4+.2j]]);G=np.array([[1,.2j],[.3,2]])
    left_time=.4;right_time=.1
    def value(E):return -(np.exp(E*left_time)*L)@G@(np.exp(-E*right_time)*R)
    expected=(left_time-right_time)*value(0)
    np.testing.assert_allclose((value(1e-5)-value(-1e-5))/2e-5,expected,rtol=2e-10,atol=2e-12)
    assert np.linalg.norm(expected.imag)>0
