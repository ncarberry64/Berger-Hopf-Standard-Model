import numpy as np
import pytest
from bhsm.interface.muon_magnetic_native_return_enclosure import enclosed_magnetic_return


def test_interval_uncertainty_is_propagated_through_signed_return():
    B=np.zeros((8,8));B[:3,:3]=np.diag([2.,-3.,4.])
    lo=np.zeros_like(B);hi=lo.copy();lo[:3,:3]=np.diag([.09,-.2,.1]);hi[:3,:3]=np.diag([.11,-.1,.3])
    actual=enclosed_magnetic_return(B,lo,hi,np.zeros_like(B),precision_bits=160)
    for R in (lo,hi):
        point=1/(np.diag(B[:3,:3])+np.diag(R[:3,:3]))-1/np.diag(B[:3,:3])
        assert np.all(np.diag(actual['stable_native_return_real_lower'])<=point)
        assert np.all(point<=np.diag(actual['stable_native_return_real_upper']))
    assert actual['native_real_entry_intervals_retained']
    assert not actual['source_return_promoted_to_quantum_propagator']


def test_nonzero_complement_cannot_be_removed():
    B=np.zeros((8,8));B[:3,:3]=np.eye(3);lo=np.zeros_like(B);hi=lo.copy();hi[7,7]=1e-90
    with pytest.raises(ValueError,match='three inserted'):enclosed_magnetic_return(B,lo,hi,np.zeros_like(B))
