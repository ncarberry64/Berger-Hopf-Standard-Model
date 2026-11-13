import numpy as np
import pytest
from bhsm.interface.muon_d5_event_child_cauchy_coupling import (
    bind_event_birth_data, event_coordinate_partial, event_constraint_rank)


def test_event_binding_preserves_every_unbound_coordinate_and_source():
    C=np.eye(384)[:,[2,17,301]]
    d=(np.arange(8*384*2).reshape(8,384,2)+1j)*1e-4
    dx=3*d; r=C@np.array([[2,1j],[4,-2],[1,8]],complex);rx=2*r
    out,source=bind_event_birth_data(d,dx,r,rx,C)
    assert np.array_equal(out[[0,1,3,4,5,6,7]],d[[0,1,3,4,5,6,7]])
    np.testing.assert_array_equal(C.T@out[2],C.T@r)
    np.testing.assert_array_equal(C.T@source[2],C.T@rx)
    Q=np.eye(384)-C@C.T
    np.testing.assert_array_equal(Q@out[2],Q@d[2])
    np.testing.assert_array_equal(Q@source[2],Q@dx[2])
    with pytest.raises(ValueError):bind_event_birth_data(d,None,r,rx,C)


def test_h_block_rank_does_not_select_a_physical_parent_state():
    C=np.eye(384)[:,:4];Q=np.zeros((384,3660),complex)
    Q[:3,-3:]=np.eye(3);L=C.T;K=np.eye(4)
    r=event_constraint_rank(Q,L,K,C)
    assert r['numerical_h_block_rank']==3
    assert r['h_block_kernel_dimension']==3657
    assert r['joint_constraint_row_rank']==4
    assert r['parent_h_selected_rank']==0
    assert not r['nullspace_classified_as_gauge']
    d,dx=event_coordinate_partial(Q,2*Q)
    assert d.shape==(8,384,3660)
    np.testing.assert_array_equal(d[2],Q)
    np.testing.assert_array_equal(dx[2],2*Q)
