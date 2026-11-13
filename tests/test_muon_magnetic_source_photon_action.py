import numpy as np
import pytest
from bhsm.interface.muon_magnetic_source_photon_action import stable_magnetic_source_return


def test_exact_inserted_axis_return_and_no_padded_inverse():
    A=np.zeros((8,8));R=np.zeros((8,8));A[:3,:3]=np.diag([2.,3.,4.]);R[:3,:3]=np.diag([.1,-.1,.2])
    actual=stable_magnetic_source_return(A,R,precision_bits=160)
    expected=np.diag(1/(np.diag(A[:3,:3])+np.diag(R[:3,:3]))-1/np.diag(A[:3,:3]))
    np.testing.assert_allclose(actual['stable_native_return'],expected,rtol=2e-14,atol=1e-17)
    assert actual['active_source_indices']==[0,1,2]
    assert not actual['eight_dimensional_inverse_claimed']
    assert actual['exact_stored_return_identity_defect_upper']<1e-40


def test_unsupported_axis_cannot_be_silently_discarded():
    A=np.zeros((8,8));R=np.zeros_like(A);A[:3,:3]=np.eye(3);R[4,4]=1e-90
    with pytest.raises(ValueError,match='exact absent-axis'):stable_magnetic_source_return(A,R)
