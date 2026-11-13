import numpy as np
from bhsm.interface.muon_corrected_birth_canonical_mean import affine_mean_lift,joint_birth_canonical_means
from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ


def test_affine_mean_map_is_literal_chart_derivative():
    rng=np.random.default_rng(43);x=rng.normal(size=268);d=rng.normal(size=268);t=.031;h=1e-5
    finite=(affine_geometry_germ(x+h*d,t)-affine_geometry_germ(x-h*d,t))/(2*h)
    np.testing.assert_allclose(affine_mean_lift(268,t)@d,finite,atol=4e-11,rtol=4e-11)


def test_canonical_source_once_and_parent_cross_retained():
    # Small algebraic chart with one x, one v, forty y; not a field state.
    rng=np.random.default_rng(74);nr=50;P=np.eye(nr)[:,:42];H=rng.normal(size=(2*nr,2*nr));H=(H+H.T)/2
    Hp=np.diag(np.linspace(1,2,nr));d=rng.normal(size=(2,nr,2,2));g=rng.normal(size=d.shape);gp=rng.normal(size=d[0].shape)
    a=joint_birth_canonical_means(d,Hp,H,g,gp,P)
    parent=np.einsum('ij,jab->iab',Hp,d[0])+gp
    child=np.einsum('ij,jab->iab',H[nr:],d.reshape(2*nr,2,2))+g[1]
    np.testing.assert_allclose(a['canonical_states'][0,1],parent[1])
    np.testing.assert_allclose(a['canonical_states'][1,1],child[1])
    assert np.linalg.norm(a['outgoing_inherited_parent_raw_cotangent'])>0
    assert a['momentum_source_count']==1
