import numpy as np
import pytest
from bhsm.interface.muon_mixed_changing_birth_action import (
    mixed_chronological_arm_action, mixed_variation_from_actual_stages,
    mixed_cell_cotangent,
)


def test_direct_cell_action_and_original_boundary_work_agree_for_complex_changing_coefficients():
    rng=np.random.default_rng(106398)
    n,m,nc=3,2,2;na=2*n+m;h=np.array([2e-8,3e-8])
    H=rng.normal(size=(nc,na,na))+1j*rng.normal(size=(nc,na,na))
    g=rng.normal(size=(nc,na))+1j*rng.normal(size=(nc,na))
    a=mixed_chronological_arm_action(H,g,h,dynamic_count=n,algebraic_count=m)
    u=rng.normal(size=len(a['matrix']))+1j*rng.normal(size=len(a['matrix']))
    t=rng.normal(size=len(u))+1j*rng.normal(size=len(u))
    s=np.einsum('kij,j->ki',a['cell_lifts'],u)
    direct=sum(h[j]*(a['cell_lifts'][j]@t)@(H[j]@s[j]+g[j])for j in range(nc))
    assert abs(direct-t@(a['matrix']@u+a['gradient']))<1e-21
    c=mixed_cell_cotangent(H,g,h,s,dynamic_count=n)
    assert abs(direct-(a['mixed_to_nodes']@t)@c['cotangent'])<2e-14
    assert np.linalg.norm(a['matrix']-a['matrix'].T)>1e-8
    np.testing.assert_allclose(mixed_variation_from_actual_stages(u[:n],s,dynamic_count=n),u,rtol=0,atol=0)


def test_stage_velocities_are_retained_when_nodal_subtraction_loses_their_digits():
    # A tiny displacement on a large background can round to zero. The
    # original stage velocity remains the canonical action operand.
    s=np.array([[1e8,7+2j,.3]],complex)
    u=mixed_variation_from_actual_stages(np.array([1e8]),s,dynamic_count=1)
    assert u[1]==7+2j
    assert ((1e8+1e-12*7)-1e8)/1e-12==0
    with pytest.raises(ValueError):
        mixed_variation_from_actual_stages(np.array([1,2]),s,dynamic_count=1)


def test_batched_boundary_cotangents_preserve_each_independent_complex_source_column():
    H=np.array([[[2,3j],[.2j,4]]],complex);g=np.array([[.3j,.8]])
    s=np.array([[[.4,.7j],[.6j,-.2]]]);h=[.05]
    c=mixed_cell_cotangent(H,g,h,s,dynamic_count=1)['cotangent']
    for j in range(2):
        np.testing.assert_array_equal(c[:,j],mixed_cell_cotangent(H,g,h,s[:,:,j],dynamic_count=1)['cotangent'])
    sources=np.array([[[.3j,.8],[.1,-.4j]]])
    cc=mixed_cell_cotangent(H,sources,h,s,dynamic_count=1)['cotangent']
    for j in range(2):
        np.testing.assert_array_equal(cc[:,j],mixed_cell_cotangent(H,sources[:,:,j],h,s[:,:,j],dynamic_count=1)['cotangent'])
