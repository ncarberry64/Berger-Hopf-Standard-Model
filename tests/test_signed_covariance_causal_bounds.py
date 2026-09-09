import numpy as np
import pytest
from flint import ctx
from bhsm.interface.signed_covariance_causal_bounds import causal_covariance_bounds


def test_shared_node_cancellation_is_preserved_before_norms():
    local=np.zeros((2,3,1,1))
    local[0,2,0,0]=10000.
    local[1,0,0,0]=10000.
    adjacent=np.zeros((2,1,1));adjacent[1,0,0]=-10000.
    result=causal_covariance_bounds(local,np.zeros_like(local),adjacent,np.zeros_like(adjacent),
                                   np.ones((2,1,1)),np.ones((3,1)))
    assert 100.<=result['longitudinal_coefficient_upper'][1]<100.00000001
    assert result['longitudinal_coefficient_upper'][2]==0.
    assert result['transverse_coefficient_upper'][2]==0.


def test_nonunit_axis_and_single_pending_right_block():
    local=np.zeros((1,3,1,1));local[0,2,0,0]=.25
    adjacent=np.zeros((1,1,1))
    result=causal_covariance_bounds(local,np.zeros_like(local),adjacent,adjacent,
                                   np.ones((1,1,1)),np.array([[0.],[1.5]]))
    assert .75<=result['longitudinal_coefficient_upper'][1]<.75000001
    assert .625<=result['transverse_coefficient_upper'][1]<.62500001


def test_noncommuting_maps_enclose_direct_tensor_recurrence():
    rng=np.random.default_rng(370)
    count,dimension=4,2
    local_tensors=rng.integers(-3,4,size=(count,dimension,4,4)).astype(float)/8
    # Fixed reset removes all dependence on input node zero.
    local_tensors[0,:,:2,:]=0;local_tensors[0,:,:,:2]=0
    maps=rng.integers(-2,3,size=(count,dimension,dimension)).astype(float)/4
    local=np.empty((count,3,dimension,dimension));adjacent=np.zeros((count,dimension,dimension))
    previous=None
    for i,tensor in enumerate(local_tensors):
        blocks=[tensor[:,:2,:2],tensor[:,:2,2:]+tensor[:,2:,:2].transpose(0,2,1),tensor[:,2:,2:]]
        flat=[v.reshape(dimension,-1) for v in blocks]
        for j,v in enumerate(flat):local[i,j]=v@v.T
        if previous is not None:adjacent[i]=previous@flat[0].T
        previous=flat[2]
    axes=np.tile([1.,0.],(count+1,1))
    result=causal_covariance_bounds(local,np.zeros_like(local),adjacent,np.zeros_like(adjacent),maps,axes)
    inputs=np.array([[0.,0.],[1.,0.],[0.,1.],[-1.,0.],[0.,-1.]])
    state=np.zeros(dimension)
    for i in range(count):
        pair=np.concatenate((inputs[i],inputs[i+1]))
        state=maps[i]@state+np.einsum('oij,i,j->o',local_tensors[i],pair,pair)
        assert abs(state[0])<=result['longitudinal_coefficient_upper'][i+1]
        assert abs(state[1])<=result['transverse_coefficient_upper'][i+1]


def test_invalid_radius_rejected_and_precision_restored():
    previous=ctx.prec
    local=np.zeros((1,3,1,1));radius=local.copy();radius[0,0,0,0]=-1.
    with pytest.raises(ValueError):
        causal_covariance_bounds(local,radius,np.zeros((1,1,1)),np.zeros((1,1,1)),
                                 np.ones((1,1,1)),np.ones((2,1)))
    assert ctx.prec==previous


def test_partial_node_results_remain_explicitly_incomplete():
    local=np.zeros((3,3,1,1));adjacent=np.zeros((3,1,1))
    result=causal_covariance_bounds(local,local,adjacent,adjacent,np.ones((3,1,1)),
                                   np.ones((4,1)),target_nodes=[1,3])
    assert result['coverage']==dict(target_nodes=[1,3],complete=False)
    assert result['longitudinal_coefficient_upper'][2] is None
    for invalid in ([1,1],[2,1],[0],[4],[True],[]):
        with pytest.raises(ValueError):
            causal_covariance_bounds(local,local,adjacent,adjacent,np.ones((3,1,1)),
                                     np.ones((4,1)),target_nodes=invalid)
