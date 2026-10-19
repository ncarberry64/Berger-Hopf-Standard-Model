import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_d5_two_sided_constraint_rows import (
    realified_higgs_matrix,combine_constraint_gradient,explicit_constraint_kernel,
    transport_higgs_time_field_ports,
)
from bhsm.interface.muon_d5_higgs_temporal_bundle_application import complex_higgs,real_higgs


def test_higgs_realification_and_map_contacts_match_original_nonlinear_section():
    U=expm(np.array([[.12j,.23+.17j],[-.23+.17j,-.12j]]))
    h=np.array([.2,-.4,.1,.7]);hp=complex_higgs(h)
    generators=np.array([[[0,-.5j],[-.5j,0]],[[0,-.5],[.5,0]],[[-.5j,0],[0,.5j]],1j*np.eye(2)])
    Uf=np.zeros((7,2,2),complex);Uf[3:]=generators@U
    F=np.column_stack([real_higgs(a@hp) for a in Uf])
    J=combine_constraint_gradient(np.zeros((13,546)),U,F)
    direction=np.array([-.3,.8,.12,-.2]);theta=np.linspace(-.3,.5,7)
    x=np.zeros(555);x[546:550]=direction;x[540:546]=theta[:6];x[554]=theta[6]
    eps=1e-6;G=np.einsum('i,iab->ab',theta[3:],generators)
    def row(s):return real_higgs(-expm(s*G)@U@complex_higgs(h+s*direction))
    finite=(row(eps)-row(-eps))/(2*eps)
    np.testing.assert_allclose(J[13:]@x,finite,atol=8e-11,rtol=2e-9)
    np.testing.assert_allclose(realified_higgs_matrix(U)@h,real_higgs(U@hp),atol=2e-16)


def test_full_field_chart_retains_all538_free_coordinates():
    A=np.zeros((13,546));A[0,100]=2
    A[1:,528:540]=np.eye(12);A[1:,508:520]=-np.eye(12)
    F=np.arange(28).reshape(4,7)/37
    J=combine_constraint_gradient(A,np.eye(2),F)
    pivot=np.r_[100,np.arange(528,540),np.arange(550,554)]
    K,free=explicit_constraint_kernel(J,pivot)
    assert K.shape==(555,538) and len(free)==538
    np.testing.assert_allclose(J@K,0,atol=2e-16)
    np.testing.assert_array_equal(K[free],np.eye(538))


def test_changed_map_time_port_uses_same_original_gradient_and_new_map():
    # A noncommuting change of the gauge/phase map must affect the parent
    # time port even though the prepared fields and their time jets hold.
    old=expm(np.array([[.13j,.21],[-.21,-.13j]]))
    new=expm(np.array([[-.17j,.09+.11j],[-.09+.11j,.17j]]))
    hp_time=np.array([.21+.08j,-.31+.17j])
    hc_time=np.array([-.11+.09j,.27-.06j])
    old_ports=np.column_stack((old@hp_time,-hc_time))
    ports,recovered=transport_higgs_time_field_ports(old,new,old_ports)
    np.testing.assert_allclose(recovered,hp_time,atol=6e-17,rtol=2e-16)
    np.testing.assert_allclose(ports[:,0],new@hp_time,atol=6e-17,rtol=2e-16)
    np.testing.assert_array_equal(ports[:,1],old_ports[:,1])
    assert np.max(abs(ports[:,0]-old_ports[:,0]))>.05
