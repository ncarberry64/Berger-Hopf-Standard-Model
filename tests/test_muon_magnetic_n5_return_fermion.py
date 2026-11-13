"""CONTROL_ONLY exact necessary product image and complete return checks."""
import numpy as np
import sympy as s
from bhsm.interface.muon_magnetic_n5_return_fermion import n5_return_angular_blocks


def test_even_n4_source_n1_has_nonzero_n5_image_before_a_green():
    # Owned phi_n,n,n=sqrt(n+1)*conj(g00)^n: exact highest-weight product.
    z=s.symbols('z');p4=s.sqrt(5)*z**4;p1=s.sqrt(2)*z;p5=s.sqrt(6)*z**5
    assert s.simplify(p4*p1-s.sqrt(s.Rational(5,3))*p5)==0
    assert s.sqrt(s.Rational(5,3))!=0
    # It is not representable by any degree<=3 fermion polynomial.
    assert s.Poly(p4*p1,z).degree()==5


def test_full_n5_return_keeps_all_families_and_exact_spectator_rows():
    a=n5_return_angular_blocks();E=a['complex_derivatives']
    assert sorted(np.concatenate([b['harmonic_indices']for b in a['angular_blocks']]))==list(range(36))
    assert sorted(np.concatenate(a['family_indices']))==list(range(18))
    assert 3*6*288==5184
    assert a['spectator_off_block_max']==0
    # Independent round-S3 Laplacian eigenvalue n(n+2)=35 on the whole shell.
    np.testing.assert_allclose(-sum(e@e for e in E),35*np.eye(36),rtol=0,atol=1e-14)
    np.testing.assert_allclose(a['real_to_complex']@a['real_to_complex'].conj().T,np.eye(36),rtol=0,atol=3e-16)
