"""Full-source restoration, analytic dual and zero-kernel controls."""
import numpy as np
from bhsm.interface.muon_canonical_descriptor_frame_application import canonical_reference_schur_application


def test_named_gauge_section_restores_nonsymmetric_full_source_and_reactions():
    C=np.c_[np.zeros((2,4)),np.eye(2)]
    Z=np.r_[np.array([[.2j,.1],[.3,-.2j],[.4,.2],[.1j,.3]]),np.eye(2)]
    P=np.eye(6)-Z@C
    H=np.array([[2,.3j,.2,.1],[.2j,4,.3,.4j],[.4,.1,3,.2],[.1j,.3,.1,5]],complex)
    D=P.T@np.pad(H,((0,2),(0,2)))@P
    a=canonical_reference_schur_application(D,C,Z,[0,1],np.array([1,.2j]))
    S=H[:2,:2]-H[:2,2:]@np.linalg.solve(H[2:,2:],H[2:,:2])
    np.testing.assert_allclose(a['reduced_geometry_hessian'],S,rtol=2e-13,atol=2e-13)
    np.testing.assert_allclose(a['original_full_source_rows'],0,atol=2e-13)
    np.testing.assert_allclose(a['original_generator_image'],0,atol=2e-13)
    np.testing.assert_allclose(a['analytic_left_eigen_rows'],0,atol=2e-13)
    np.testing.assert_allclose(a['coefficient_left_right_pairing'],1,atol=2e-13)


def test_internal_source_response_preserves_true_kernel_without_physical_mode_selection():
    B=np.array([[.4,.2],[.1,.3]],complex);I=np.array([[2,.1j],[.1j,3]],complex)
    S=np.diag([0.,4.]);G=S+B@np.linalg.solve(I,B.T)
    D=np.pad(np.block([[G,B],[B.T,I]]),((0,2),(0,2)))
    C=np.c_[np.zeros((2,4)),np.eye(2)];Z=C.T
    a=canonical_reference_schur_application(D,C,Z,[0,1],np.array([1.,0.]))
    assert np.linalg.norm(a['primitive_reference_internal_source'])>.1
    np.testing.assert_allclose(D@a['reference_control_full_direction'],0,atol=3e-13)
    assert not a['physical_stop_or_formation_or_pole_reference_selected']
