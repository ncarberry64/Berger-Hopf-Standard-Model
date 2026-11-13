import numpy as np
import pytest
from bhsm_outgoing_missing_jet_sensitivity_20261015 import missing_jet_direction


def test_literal_left_and_mode_rescaling_covariance():
    ge=np.array([[1+.2j,.4j],[.3,2-.7j]])
    r=np.array([[.1+.2j],[.8-.3j]])
    l=np.array([[.6-.5j,.4+.9j]])
    a=missing_jet_direction(ge,r,l)
    b=missing_jet_direction(ge,(2+3j)*r,l/(2+3j))
    assert np.allclose(a['direction'],b['direction'],rtol=2e-14,atol=2e-14)
    assert abs(a['energy_slope_sensitivity']+1)<2e-14
    assert abs(a['projected_direction']-a['kinetic_pairing'])<2e-14


def test_independent_equation_row_basis_covariance():
    ge=np.array([[1+.2j,.4j],[.3,2-.7j]])
    r=np.array([[.1+.2j],[.8-.3j]])
    l=np.array([[.6-.5j,.4+.9j]])
    s=np.array([[1.2+.3j,.4],[.1j,1.7-.2j]])
    a=missing_jet_direction(ge,r,l)
    b=missing_jet_direction(s@ge,r,np.linalg.solve(s.T,l.T).T)
    assert np.allclose(b['direction'],s@a['direction'],rtol=2e-14,atol=2e-14)
    assert abs(a['energy_slope_sensitivity']-b['energy_slope_sensitivity'])<2e-14


def test_non_simple_pairing_is_rejected():
    with pytest.raises(ValueError,match='Nonzero simple-pole'):
        missing_jet_direction(np.eye(2),np.array([[1],[0]]),np.array([[0,1]]))
