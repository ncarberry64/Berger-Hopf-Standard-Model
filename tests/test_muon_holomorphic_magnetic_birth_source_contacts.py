import numpy as np
from bhsm.interface.muon_holomorphic_magnetic_birth_source_contacts import magnetic_birth_source_contacts


def test_complex_source_cotangent_preserves_nonzero_reaction_without_free_defect():
    rng=np.random.default_rng(271);n=84;draw=lambda s:rng.normal(size=s)+.3j*rng.normal(size=s)
    C=np.eye(n)[:20];S=np.eye(n)[:,20:];L=C.T;F=np.eye(n)[[16,17,18,19]]
    q=draw((20,3));q[16:]=0;shared=S@draw((64,3))+L@q
    p=draw((n,3));reaction=draw((20,3));jump=C.T@reaction
    force=C.T@draw((20,3));force[16:]=0
    parent=dict(total_field=shared,canonical_momentum=p);child=dict(total_field=shared,canonical_momentum=p-jump,original_action_force=force)
    a=magnetic_birth_source_contacts(parent,child,C,S,L,F,q,q)
    np.testing.assert_allclose(a['momentum_named_constraint_multipliers'],reaction,atol=7e-16)
    np.testing.assert_allclose(a['momentum_full_free_projection'],0,atol=1e-16)
    np.testing.assert_allclose(a['full_interface_action_cotangent'],q.T@reaction,rtol=3e-14,atol=2e-14)
    np.testing.assert_allclose(a['full_minus_source_action_cotangent'],0,atol=3e-14)
    assert np.linalg.norm(a['prescribed_source_action_cotangent'])>1
    assert np.max(abs(a['named_frame_source_rows']))==0
