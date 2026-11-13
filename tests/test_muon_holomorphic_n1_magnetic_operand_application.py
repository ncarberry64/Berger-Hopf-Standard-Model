import numpy as np
from bhsm.interface.muon_holomorphic_n1_magnetic_operand_application import (
    homogeneous_original_field_trial,signed_point_mixed_action,signed_two_trace_temporal_block,PLACEMENTS)


def test_literal_high_low_field_trial_and_all_temporal_placements():
    rng=np.random.default_rng(418)
    draw=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    p=np.r_[np.arange(16,80),np.arange(16),np.arange(80,84)]
    labels=np.array([[0,0,0,0]]+[[2,0,0,k]for k in range(9)])
    raw=draw((268,2));a=homogeneous_original_field_trial(raw,p,labels)
    ev=a['field'];et=a['coordinate_rate'];ov=draw((336,3));ot=draw((336,3))
    np.testing.assert_array_equal(ev.reshape(84,10,2)[:,0],np.r_[raw[100:180],raw[260:264]][p])
    np.testing.assert_array_equal(et.reshape(84,10,2)[:,0],np.r_[raw[180:260],raw[264:268]][p])
    assert np.count_nonzero(ev.reshape(84,10,2)[:,1:])==0
    # Complete nonsymmetric complex rectangular operators detect literal
    # left/right order, rate placement and any unwanted conjugation.
    D={'delta_'+n:draw((3,840,336))for n in PLACEMENTS}
    for prefix in('Maxwell_','intrinsic_','intrinsic_off_shell_DH_'):
        D.update({prefix+'delta_'+n:(.2 if prefix=='Maxwell_'else .8 if prefix=='intrinsic_'else .1)*D['delta_'+n]for n in PLACEMENTS})
    m=signed_point_mixed_action(D,ev,et,ov,ot)
    expected=np.array([[ev[:,s]@D['delta_K'][k]@ov[:,j]+ev[:,s]@D['delta_B_forward'][k]@ot[:,j]
        +et[:,s]@D['delta_B_reverse'][k]@ov[:,j]+et[:,s]@D['delta_M'][k]@ot[:,j]
        for k in range(3)for j in range(3)]for s in range(2)]).reshape(2,3,3)
    np.testing.assert_allclose(m['total'],expected,rtol=4e-14,atol=2e-9)
    pv=np.array([.3,.7]);rv=np.array([-1/(.7+.2j),1/(.7+.2j)]);w=.1-.3j
    block=signed_two_trace_temporal_block(D,pv,rv,w)
    left,right=draw((2,840)),draw((2,336))
    actual=np.einsum('ae,abkef,bf->k',left,block,right,optimize=True)
    predicted=np.array([w*((pv@left)@D['delta_K'][k]@(pv@right)+(pv@left)@D['delta_B_forward'][k]@(rv@right)
        +(rv@left)@D['delta_B_reverse'][k]@(pv@right)+(rv@left)@D['delta_M'][k]@(rv@right))for k in range(3)])
    np.testing.assert_allclose(actual,predicted,rtol=8e-14,atol=2e-9)
