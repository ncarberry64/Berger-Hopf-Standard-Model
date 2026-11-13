"""Narrow physical-rho roundtrip and matching source cardinal equations."""
import numpy as np
import pytest
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule
from bhsm.interface.muon_d5_event_represented_radial_source import represented_radial_rule
from bhsm.interface.muon_d5_event_consumed_source_refinement import source_forcing_gauss_update


def test_stage_and_dense_polynomial_use_same_actually_represented_nodes():
    ideal,oldpolys,_,_=_collocation_rule(5)
    left=np.pi/2;right=left-1.1875863735508981e-7/2;h=right-left
    rho=left+h*ideal;nodes=(rho-left)/h
    assert np.max(abs(nodes-ideal))>1e-10
    polys,integral,A=represented_radial_rule(nodes)
    np.testing.assert_array_equal(np.array([[p(x) for p in polys] for x in nodes]),np.eye(5))
    assert np.max(abs(np.array([[p(x) for p in oldpolys] for x in nodes])-np.eye(5)))>1e-9
    for k in range(5):
        np.testing.assert_allclose(A@nodes**k,nodes**(k+1)/(k+1),atol=5e-16,rtol=2e-15)
        np.testing.assert_allclose(integral(1.)@nodes**k,1/(k+1),atol=4e-16)
    with pytest.raises(ValueError):represented_radial_rule(nodes[::-1])


def test_original_source_stage_equation_matches_represented_rho_evaluation():
    ideal,oldpolys,_,_=_collocation_rule(5)
    left=np.pi/2;right=left-1.1875863735508981e-7/2;h=right-left
    nodes=((left+h*ideal)-left)/h
    polys,integral,A=represented_radial_rule(nodes)
    forcing=(1e6*(1+nodes+nodes**2))[:,None,None]
    slope,report=source_forcing_gauss_update(np.zeros((5,1,1)),forcing,
        np.array([[.7]]),h,A,np.full((5,1,1),.8))
    correct=np.array([np.einsum('q,qdk->dk',np.array([p(x) for p in polys]),slope)[0,0] for x in nodes])
    wrong=np.array([np.einsum('q,qdk->dk',np.array([p(x) for p in oldpolys]),slope)[0,0] for x in nodes])
    np.testing.assert_allclose(correct,forcing[:,0,0],atol=0,rtol=0)
    assert np.max(abs(wrong-forcing[:,0,0]))>1e-4
    assert report['corrected_stage_residual_max']<3e-16
