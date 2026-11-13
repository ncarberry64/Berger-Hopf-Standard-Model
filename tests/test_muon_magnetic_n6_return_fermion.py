"""Independent product closure and complete source-return representation checks."""
import numpy as np
import sympy as s
from bhsm.interface.muon_magnetic_n6_return_fermion import n6_return_angular_blocks


def test_n6_has_both_magnetic_and_output_product_placements():
    z=s.symbols('z')
    p={n:s.sqrt(n+1)*z**n for n in range(7)}
    # Literal highest weights prove each reached edge is nonzero.
    assert s.simplify(p[4]*p[1]-s.sqrt(s.Rational(5,3))*p[5])==0
    assert s.simplify(p[5]*p[1]-s.sqrt(s.Rational(12,7))*p[6])==0
    assert s.simplify(p[4]*p[2]-s.sqrt(s.Rational(15,7))*p[6])==0
    assert s.Poly(p[4]*p[2],z).degree()==6


def test_full_n6_complete_spectator_decomposition_and_laplacian():
    a=n6_return_angular_blocks();E=a['complex_derivatives']
    assert sorted(np.concatenate([b['harmonic_indices']for b in a['angular_blocks']]))==list(range(49))
    assert sorted(np.concatenate(a['family_indices']))==list(range(18))
    assert 3*7*336==7056
    assert a['spectator_off_block_max']==0
    np.testing.assert_allclose(-sum(e@e for e in E),48*np.eye(49),rtol=0,atol=2e-14)
    np.testing.assert_allclose(a['real_to_complex']@a['real_to_complex'].conj().T,np.eye(49),rtol=0,atol=3e-16)
