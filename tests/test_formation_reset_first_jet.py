import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.formation_reset_first_jet import reset_hit_jet,incoming_reset_jet
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box
from bhsm.interface.arb_symmetric_inertia import isolate_index


def test_hit_removes_event_motion_but_preserves_duration():
    result=reset_hit_jet(arb_mat([[1,2],[3,4]]),arb_mat([[2],[1]]),arb_mat([[0,1]]))
    assert result['hit_jet']==arb_mat([[-5,-6],[0,0]])
    assert result['arc_shift']==arb_mat([[-3,-4]])


def test_nontransverse_hit_rejected():
    with pytest.raises(ValueError,match='transverse'):
        reset_hit_jet(arb_mat([[1],[2]]),arb_mat([[1],[0]]),arb_mat([[0,1]]))


def test_upstream_stationarity_is_required_and_changes_incoming_jet():
    # Synthetic exact system with the same dimension/row ownership as the owner.
    J=arb_mat(58,196);T=arb_mat(98,73);K=arb_mat(66,196)
    for i in range(26):J[i,i]=1
    for i in range(32):J[26+i,98+i]=1;J[26+i,26+i]=-1
    for i in range(66):K[i,98+32+i]=1
    T[26,0]=1
    with pytest.raises(ValueError,match='upstream'):
        incoming_reset_jet(J,T,None)
    first=incoming_reset_jet(J,T,K)
    K[0,26]=-3
    second=incoming_reset_jet(J,T,K)
    assert first['incoming_hit_jet'][32,0]==0
    assert second['incoming_hit_jet'][32,0]==3
    assert second['reset_replay']==arb_mat(58,73)
    assert second['upstream_replay']==arb_mat(66,73)


def test_incoming_index_is_not_hardcoded_to_outgoing():
    previous=ctx.prec;ctx.prec=512
    try:
        H=np.array([[arb(2),arb(1)],[arb(1),arb(2)]],dtype=object)
        for index,reference in [(0,np.array([1.,-1.])),(1,np.array([1.,1.]))]:
            p,lam,_,_=indexed_proposal(H,index,reference)
            assert verify_eigenpair_box(H,p,lam)['validation_passed']
            assert isolate_index(H,lam.lower(),lam.upper(),index)['validation_passed']
    finally:ctx.prec=previous
