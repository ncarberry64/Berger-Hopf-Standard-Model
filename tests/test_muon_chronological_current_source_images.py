import numpy as np
from bhsm.interface.muon_chronological_current_source_images import (
    restore_original_field_direction,current_direction_wall_point,native_images_of_current_direction)
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction
from bhsm.interface.muon_source_directed_em_normal_current import normal_left_current_gaunt


def test_response_and_literal_adjoint_restore_the_same_original_pairing():
    rng=np.random.default_rng(4203);U=homogeneous_scalar_degree_reduction(1)['real_to_complex_coefficient_map']
    ids=(np.arange(84)[:,None]*4+np.arange(2)[None,:]*2+1).ravel()
    u=rng.normal(size=(176,3))+1j*rng.normal(size=(176,3))
    p=rng.normal(size=(176,3))+1j*rng.normal(size=(176,3))
    a=restore_original_field_direction(u,U,ids)
    b=restore_original_field_direction(p,U,ids,analytic_adjoint=True)
    ur=a['original_field_direction'].reshape(336,3);pr=b['original_field_direction'].reshape(336,3)
    np.testing.assert_allclose(pr.T@ur,p[:168].T@u[:168],rtol=3e-14,atol=3e-14)
    # A common inverse-U shortcut for both duals changes a complex pairing.
    wrong=restore_original_field_direction(p,U,ids)['original_field_direction'].reshape(336,3)
    assert np.linalg.norm(wrong.T@ur-p[:168].T@u[:168])>1
    W=rng.normal(size=(24,84));rows=np.array([[40,.3,-2],[41,.7,2]])
    y=np.array([u,1.2j*u]);N=.8+.1j;w=.3+.7j
    z=current_direction_wall_point(y,rows,W,U,ids,lapse=N,right_clock=w)
    expected=np.einsum('af,fhc->ahc',W,
        restore_original_field_direction(.3*u+.7*1.2j*u,U,ids)['original_field_direction'])
    np.testing.assert_allclose(z['wall_coefficients'],expected)
    np.testing.assert_allclose(z['wall_coordinate_rate'],
        1j*N/w*np.einsum('af,fhc->ahc',W,
        restore_original_field_direction(-2*u+2*1.2j*u,U,ids)['original_field_direction']))
    np.testing.assert_array_equal(a['original_frame_direction'],u[168:])


def test_full_gaunt_source_placements_match_direct_haar_application():
    from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
    rng=np.random.default_rng(438)
    c=rng.normal(size=(24,4,2))+1j*rng.normal(size=(24,4,2))
    a=native_images_of_current_direction(c,radius=.8+.2j,lapse=.9+.3j,
        reflected_radius=.8-.2j,reflected_lapse=.9-.3j,family=1,
        even_field_odd_gaunt=normal_left_current_gaunt()['gaunt'])
    s=scalar_s3_discretization(2);labels=s['real_basis_labels'];Y=s['real_basis_values'];weights=s['haar_weights']
    odd=np.array([j for j,l in enumerate(labels) if l[0]==1]);even=np.array([j for j,l in enumerate(labels) if l[0]in(0,2)])
    v=rng.normal(size=(6,4))+1j*rng.normal(size=(6,4))
    z=rng.normal(size=(6,10))+1j*rng.normal(size=(6,10))
    for col in range(2):
        Xq=np.einsum('qh,hij->qij',Y[:,odd],a['Xi_source_harmonics'][col])
        yq=np.einsum('qh,ih->qi',Y[:,odd],v)
        direct=np.einsum('qt,qij,qj,q->it',Y[:,even],Xq,yq,weights)
        np.testing.assert_allclose(a['even_from_odd_source'][col]@v.ravel(),direct.ravel(),rtol=2e-13,atol=2e-13)
        zq=np.einsum('qh,ih->qi',Y[:,even],z)
        reverse=np.einsum('qt,qij,qj,q->it',Y[:,odd],Xq,zq,weights)
        np.testing.assert_allclose(a['odd_from_even_source'][col]@z.ravel(),reverse.ravel(),rtol=2e-13,atol=2e-13)
    assert np.linalg.norm(a['independent_dual_odd_from_even_source']-
                          a['even_from_odd_source'].conj().transpose(0,2,1))>1
