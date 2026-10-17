import numpy as np
from bhsm.interface.muon_native_radial_overlap_tail import radial_schur_pencil
from bhsm.interface.muon_causal_radial_matching import causal_radial_boundary_application,causal_radial_soft_path_application,finite_causal_radial_covector


def test_retarded_laplace_sign_and_finite_canonical_endpoint_are_literal():
    C=np.zeros((3,3,3),complex);C[0]=np.diag([2.,-4.,1.]);C[2]=np.diag([0.,1.,1.])
    p=radial_schur_pencil(C,np.array([[0.],[1.],[0.]]),np.array([[0.,0.,1.]]),At_count=1)
    a=causal_radial_boundary_application(p,proper_length=.7,laplace_rates=[.3,4.])
    np.testing.assert_allclose(a['terminal_dynamic_field'],[[np.sin(1.4)/2]],atol=2e-15)
    for row in a['applications']:
        s=complex(row['laplace_rate']);expected=(1-np.exp(-s*.7)*(np.cos(1.4)+s*np.sin(1.4)/2))/(s*s+4)
        np.testing.assert_allclose(row['finite_driven_response'],[[expected]],atol=2e-15)
        np.testing.assert_allclose(row['infinite_meromorphic_action_response'],[[1/(s*s+4)]],atol=2e-15)
        assert np.max(abs(row['finite_boundary_identity_residual']))<3e-15
    assert abs(a['applications'][0]['radial_endpoint_response'][0,0])>.05
    cov=finite_causal_radial_covector(p,proper_length=.7,matched_mass_action=.3,fixed_Y=.02,
        kinetic_residue=.8,quadrature_order=8,log_edges=(0,4,8,12))
    y=cov['log_nodes'];x=-np.expm1(-y);s=cov['proper_Laplace_rates']
    exact=(1-np.exp(-s*.7)*(np.cos(1.4)+s*np.sin(1.4)/2))/(s*s+4)
    expected=.02**2/(16*np.pi**2)*.3**2*x*x*(2-x)*.8*exact
    np.testing.assert_allclose(cov['finite_causal_covector_samples'],expected,rtol=4e-13,atol=1e-19)


def test_causal_at_reconstruction_keeps_derivative_endpoint_and_nonzero_source_residue():
    C=np.zeros((3,4,4),complex);C[0]=np.diag([2.,4.,-3.,1.]);C[0,0,1]=C[0,1,0]=.2
    L=np.zeros((4,4));L[0,1]=.3;L[1,0]=-.3;L[1,2]=.5;L[2,1]=-.5;C[1]=-1j*L
    C[2]=np.diag([0.,1.,2.,1.]);S=np.array([[0.],[1.],[.2],[0.]])
    p=radial_schur_pencil(C,S,np.array([[0.,0.,0.,1.]]),At_count=1)
    a=causal_radial_boundary_application(p,proper_length=.1,laplace_rates=[.4,10.])
    for row in a['applications']:
        assert np.max(abs(row['original_dynamic_equation_residual']))<2e-14
        assert np.max(abs(row['original_Gauss_equation_residual']))<2e-14
        assert np.max(abs(row['finite_boundary_identity_residual']))<2e-14
    b=causal_radial_soft_path_application(p,[(2.,.2)],matched_mass_action=.3,fixed_Y=.02,
        kinetic_residue=.8,reference_mass_squared=3.,log_end=10.,order=16)
    assert abs(b['causal_rotation_minus_opposite'])>1e-8
    assert b['causal_frequency_sign']=='C(-i*s); owner exp(+i*z*t)'
    assert not b['adopted_Feynman_quantum_contour_identified']
