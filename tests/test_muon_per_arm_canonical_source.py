import numpy as np
from bhsm.interface.muon_per_arm_canonical_source import per_arm_source_reconstitution,arm_variational_midpoint_map
from bhsm.interface.muon_complex_canonical_midpoint import complex_canonical_midpoint_rows


def test_parent_own_Pi_and_child_inherited_source_are_kept_independent():
    rng=np.random.default_rng(148);Hp=np.eye(252,dtype=complex)*(2+.1j);H=np.eye(504,dtype=complex)*(3-.1j)
    H[:252,:252]*=2;H[252:,:252]=rng.normal(size=(252,252))*.003+.001j
    d=rng.normal(size=504)+.1j*rng.normal(size=504);g=rng.normal(size=504)*.02+.01j
    d[212:252]=-g[212:252]/(2+.1j)
    d[464:504]=-(H[464:504,:252]@d[:252]+g[464:504])/(3-.1j)
    F=np.zeros((2,146));F[np.arange(2),106+np.array([3,7])]=1
    a=per_arm_source_reconstitution(Hp,H,d,g,F,F,standalone_parent_source=g[:252])
    np.testing.assert_allclose(a['parent']['direction'],d[:252],atol=2e-14)
    np.testing.assert_allclose(a['child']['direction'],d[252:],atol=2e-14)
    assert np.max(abs(a['parent']['original_phase_rows']))<2e-14
    assert np.max(abs(a['child']['original_phase_rows']))<2e-14
    assert np.linalg.norm(a['parent_own_momentum_target']-a['parent_joint_momentum_same_trial'])>1
    np.testing.assert_allclose(a['child_inherited_source'],H[252:,:252]@a['parent']['direction'],atol=0)


def test_original358_structure_matches_literal_midpoint_action_and_transpose():
    H=np.array([[4,.2,.1,.3,.1],[.2,3,.4,.2,.1],[.1,.4,2,.1,.3],[.3,.2,.1,2,.2],[.1,.1,.3,.2,1]],complex)
    H+=.1j*np.eye(5);x=np.array([.4+.1j,-.2]);p=np.array([-.1,.3j]);g=np.array([.1j,.2,-.3,.1,.2j])
    a=arm_variational_midpoint_map(H,.07,x,p,g,np.zeros((0,3)),normal_covector=np.array([.2j,1]))
    rhs=lambda eta:dict(gradient=H@eta+g,hessian=H)
    literal=complex_canonical_midpoint_rows(a['solution'],x,p,.07,rhs)
    np.testing.assert_allclose(a['original358_rows'],literal['residual'],atol=2e-16)
    assert np.max(abs(a['original358_rows']))<2e-15
    assert np.max(abs(a['literal_transpose_rows']))<2e-15
    np.testing.assert_allclose(a['transpose_pairing'],a['test_pairing'],atol=2e-15)
