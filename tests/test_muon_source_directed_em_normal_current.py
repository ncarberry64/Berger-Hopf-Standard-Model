"""Action representation/dual controls, not physical primal state choices."""
import numpy as np
from bhsm.interface.muon_source_directed_em_normal_current import holomorphic_charge_projection,normal_left_current_gaunt,normal_test_wall_inverse


def test_actual_neutral_charge_and_holomorphic_opposite_branch_agree():
    from bhsm.interface.muon_primal_electromagnetic_source import higgs_aligned_charge
    h=np.array([.3,.8,-.2,.1]);H=h[:2]+1j*h[2:]
    owned=higgs_aligned_charge(H,np.zeros(2))
    q=holomorphic_charge_projection(h)
    np.testing.assert_allclose(q['unit_Tr16_charge_coefficients'],owned['unit_Tr16_coefficients'],atol=4e-16)
    z=h+1j*np.array([.01,-.03,.02,.04]);p=holomorphic_charge_projection(z)
    np.testing.assert_allclose(p['projection']@p['projection'],p['projection'],atol=3e-16)
    np.testing.assert_allclose(holomorphic_charge_projection(z.conj())['projection'],p['projection'].conj(),atol=0)
    assert np.linalg.norm(p['projection']-p['projection'].conj().T)>.02


def test_n1_output_current_keeps_the_full_even_product_image():
    from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
    s=scalar_s3_discretization(2);labels=s['real_basis_labels'];y=s['real_basis_values']
    odd=[j for j,l in enumerate(labels)if l[0]==1];even=[j for j,l in enumerate(labels)if l[0]in(0,2)]
    g=normal_left_current_gaunt()['gaunt']
    np.testing.assert_allclose(np.einsum('qt,thx->qhx',y[:,even],g),y[:,odd,None]*y[:,None,odd],atol=5e-14)
    assert g.shape==(10,4,4)
    assert np.linalg.norm(g[1:])>1


def test_literal_normal_adjoint_is_computed_after_current_test_before_inverse():
    K=np.array([[2.,.2j,.4],[.1,3.,.2j],[.4,.1,1.7]],complex);C=np.array([[1,0,0.]])
    saddle=np.block([[K,C.T],[C,np.zeros((1,1))]]);inverse=np.linalg.inv(saddle)
    r=np.random.default_rng(4);J=r.normal(size=(2,6,3))+1j*r.normal(size=(2,6,3));J[:,:,2]=0
    L=r.normal(size=(24,3,3))+1j*r.normal(size=(24,3,3));ell=r.normal(size=(6,24))+1j*r.normal(size=(6,24))
    field=dict(original_Hessian=K,frame_rows=C,original_action_Green=inverse[:3,:3],frame_reactions=inverse[3:,:3])
    moments=dict(literal_right_current=J,actual_A_sharp_numerator=2*J,literal_n1_left_current=L)
    a=normal_test_wall_inverse(field,moments,{'C':[dict(left_tests=ell,right_tests=np.eye(6))]})
    soft=np.einsum('do,ofb->dfb',ell,L);source=soft.transpose(2,0,1).reshape(3,-1)
    expected=np.linalg.solve(saddle.T,np.vstack((source,np.zeros((1,source.shape[1])))))
    np.testing.assert_allclose(a['normal_test_adjoint']['C'][0]['field_adjoint'],expected[:3],atol=3e-15)
    assert np.linalg.norm(a['literal_field_response'][2])>.01
    assert np.max(abs(a['literal_original_row_residual']))<2e-15
