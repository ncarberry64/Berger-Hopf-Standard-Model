import numpy as np
from bhsm.interface.muon_paired_local_normal_action_symbol import shared_normal_frequency_jet


def test_full_action_glues_attachment_before_static_and_kinetic_reduction():
    # Each arm (attachment,normal), plus two literal algebraic coordinates.
    Kp=np.array([[3.,.7],[.7,2.]]);Kc=np.array([[5.,-.4],[-.4,1.]])
    M=np.diag([2.,3.,4.,5.]);K=np.zeros((4,4));K[:2,:2]=Kp;K[2:,2:]=Kc
    H=np.zeros((10,10));H[:4,:4]=-K;H[4:8,4:8]=M;H[8:,8:]=np.eye(2)
    a=shared_normal_frequency_jet(H,np.eye(2),np.eye(2),np.zeros((0,6)),lapse=1.)
    attachment=-(Kp[0,1]+Kc[0,1])/(Kp[0,0]+Kc[0,0]);phi=np.array([attachment,1.,attachment,1.])
    np.testing.assert_allclose(a['coordinate_restoring_density'],phi@K@phi,rtol=2e-15)
    np.testing.assert_allclose(a['coordinate_low_frequency_inertia'],phi@M@phi,rtol=2e-15)
    assert np.max(abs(a['action_rows_including_trace_gluing_duals']))<1e-15
    assert np.max(abs(a['physical_trace_gluing_reactions']))>.5


def test_parent_child_cross_contact_changes_the_same_shared_normal_symbol():
    H=np.zeros((10,10));H[:4,:4]=-np.eye(4);H[4:8,4:8]=np.eye(4);H[8:,8:]=np.eye(2)
    H[1,3]=H[3,1]=-.25
    a=shared_normal_frequency_jet(H,np.eye(2),np.eye(2),np.zeros((0,6)),lapse=.7)
    np.testing.assert_allclose(a['coordinate_restoring_density'],2.5,rtol=2e-15)
    np.testing.assert_allclose(a['proper_restoring_density'],2.5/.7,rtol=2e-15)
    np.testing.assert_allclose(a['proper_low_frequency_inertia'],1.4,rtol=2e-15)
