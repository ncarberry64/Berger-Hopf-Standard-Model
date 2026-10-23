import numpy as np
from bhsm.interface.muon_native_radial_overlap_tail import (
    radial_schur_pencil,radial_schur_application,certify_projected_radial_tail,
    radial_tail_quadrature,radial_cluster_contour_residue,radial_detoured_soft_covector)


def complete_pencil():
    p=2.;u=np.array([.2,.4,0.]);q=np.array([.3,.1,0.])
    C=np.zeros((3,4,4),complex)
    C[0,0,0]=p;C[0,0,1:]=u;C[0,1:,0]=u
    C[0,1:,1:]=np.diag([1.,-3.,4.])
    linear=np.zeros((4,4));linear[0,1:]=q;linear[1:,0]=-q
    linear[1,2]=.7;linear[2,1]=-.7;C[1]=-1j*linear
    C[2,1:,1:]=np.diag([1.,2.,1.])
    S=np.array([[0.],[1.],[.25],[0.]])
    F=np.array([[0.,0.,0.,1.]])
    return C,S,F


def test_literal_schur_keeps_gauss_and_independent_action_placements():
    C,S,F=complete_pencil();p=radial_schur_pencil(C,S,F,At_count=1)
    for z in(0.,.3,4.,2+.5j):
        got=radial_schur_application(p,z)
        A=C[0]+1j*z*C[1]-z*z*C[2]
        direct=np.zeros_like(S,dtype=complex);direct[:3]=np.linalg.solve(A[:3,:3],S[:3])
        np.testing.assert_allclose(got['full_source_response'],direct,rtol=3e-14,atol=1e-14)
        assert np.max(abs(got['original_Gauss_residual']))<3e-14
    # The action-owned source has a nonzero algebraic return; discarding it
    # changes the scalar consumer rather than just the coordinate metadata.
    assert abs(got['full_source_response'][0,0])>1e-3


def test_uniform_outward_tail_encloses_full_coupled_projected_application():
    C,S,F=complete_pencil();p=radial_schur_pencil(C,S,F,At_count=1)
    args=dict(matched_mass_action=.3,fixed_Y=.02,kinetic_residue=.8,log_start=10.)
    cert,U=certify_projected_radial_tail(p,**args,precision_bits=160)
    a=radial_tail_quadrature(p,**args,order=16)
    b=radial_tail_quadrature(p,**args,order=24)
    assert cert['uniform_projected_tail_enclosed']
    assert abs(b['tail_covector_value'])<cert['reached_omitted_tail_absolute_upper']
    assert abs(a['tail_covector_value']-b['tail_covector_value'])<1e-12*abs(b['tail_covector_value'])
    assert cert['uniform_coercivity_loss_upper']<.01


def test_complete_cluster_residue_has_actual_soft_weight_and_bypass_sign():
    C=np.zeros((3,4,4),complex);C[0]=np.diag([2.,4.,-3.,5.]);C[2]=np.diag([0.,1.,2.,1.])
    S=np.array([[0.],[1.],[0.],[0.]]);F=np.array([[0.,0.,0.,1.]])
    p=radial_schur_pencil(C,S,F,At_count=1)
    args=dict(center=2.,radius=.05,matched_mass_action=.3,fixed_Y=.02,kinetic_residue=.8)
    r=radial_cluster_contour_residue(p,**args,order=32)
    np.testing.assert_allclose(r['radial_cluster_residue'],[[-.25]],atol=1e-13)
    x=2/(1+np.sqrt(1+4*(.3/2)**2))
    expected=(-.02**2/(16*np.pi**2)*2*.3**2*x**3*.8/2)*(-.25)
    np.testing.assert_allclose(r['soft_covector_cluster_residue'],expected,rtol=1e-12,atol=1e-19)
    np.testing.assert_allclose(r['upper_minus_lower_path_bypass'],-2j*np.pi*expected,rtol=1e-12,atol=1e-18)
    assert not r['native_Feynman_or_retarded_loop_branch_selected']
    a=radial_detoured_soft_covector(p,[(2.,.05)],matched_mass_action=.3,fixed_Y=.02,
        kinetic_residue=.8,reference_mass_squared=3.,log_end=10.,order=24)
    np.testing.assert_allclose(a['upper_minus_lower'],r['upper_minus_lower_path_bypass'],rtol=1e-10,atol=1e-17)
    assert abs(a['upper_same_coordinate_reference']-a['lower_same_coordinate_reference'])<1e-17
