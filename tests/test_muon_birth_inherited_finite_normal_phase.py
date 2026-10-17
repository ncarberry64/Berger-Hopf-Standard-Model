import numpy as np
import pytest

from bhsm.interface.muon_birth_inherited_finite_normal_phase import (
    affine_geometry_germ, child_action_block,
)
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift


def test_affine_first_germ_advances_only_owned_positions_and_normal():
    x=np.arange(108,dtype=float)/100
    a=affine_geometry_germ(x,.07)
    np.testing.assert_allclose(a[:37]-x[:37],.07*x[37:74],atol=1e-16)
    assert a[98]==x[98]+.07*x[99]
    indices=np.r_[np.arange(37,98),np.arange(99,len(x))]
    np.testing.assert_array_equal(a[indices],x[indices])
    with pytest.raises(ValueError):affine_geometry_germ(x,np.nan)


def test_child_restriction_retains_all_algebraic_and_nonlinear_graph_contacts():
    # A dense quadratic graph tests cross/internal contacts independently of
    # the producer's child-block indexing; this is a representation test.
    rep={'gauge_labels':[]};P=generic_coordinate_lift([])['lift'];nr,nm=P.shape
    rng=np.random.default_rng(17);R=rng.normal(size=(2*nr,2*nr));K=R+R.T
    base=rng.normal(size=2*nr);linear=rng.normal(size=2*nr)
    def literal(child):
        x=np.r_[base[:nr],child];return .5*x@K@x+linear@x-3.5
    graph={'value':literal(base[nr:])+3.5,'raw_gradient':K@base+linear,
           'raw_hessian':K,'profile_increment':np.ones((2,3))}
    app=child_action_block(graph,{'value':3.5},rep)
    z=P.T@base[nr:];u=rng.normal(size=nm);v=rng.normal(size=nm);eps=2e-5
    first=(literal(P@(z+eps*u))-literal(P@(z-eps*u)))/(2*eps)
    np.testing.assert_allclose(first,u@app['gradient'],rtol=1e-9,atol=1e-7)
    mixed=((K@np.r_[base[:nr],P@(z+eps*v)]+linear)[nr:]
           -(K@np.r_[base[:nr],P@(z-eps*v)]+linear)[nr:])/(2*eps)
    np.testing.assert_allclose(P.T@mixed,app['hessian']@v,rtol=2e-10,atol=2e-8)
    assert app['Lyy'].shape==(24,24)
    assert np.linalg.norm(app['Lyy'])>0
    assert app['source_image_projected'] is False
    np.testing.assert_array_equal(app['inherited_profile_increment'],graph['profile_increment'])
