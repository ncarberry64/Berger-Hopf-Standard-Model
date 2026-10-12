"""Exact image/normalization controls; no physical state selected."""
import numpy as np
from bhsm.interface.muon_changing_magnetic_momentum_columns import (
    momentum_current_angular_images,generalized_vertex_sources,_possible)
from bhsm.interface.muon_intrinsic_scalar_discretization import real_scalar_basis_transform,scalar_section_labels


def test_literal_complex_angular_integrals_for_both_current_placements():
    # CONTROL_ONLY non-Hermitian vertices; literal left is not forced adjoint.
    a=momentum_current_angular_images();labels=scalar_section_labels(6)
    ids=np.array([i for i,l in enumerate(labels)if l[0]in(0,2,4,6)])
    hi=np.array([i for i,l in enumerate(labels)if l[0]==2]);U=real_scalar_basis_transform(6)[np.ix_(hi,ids)]
    rng=np.random.default_rng(23);f=rng.normal(size=(2,4,3));v=np.array([[[1j,.2],[-.7,2j]],[[.3,.4j],[.2,.8]]])
    G=a['external_gaunt'][('even','odd','input')][:,:4]
    r,l=generalized_vertex_sources(f,v,U,G)
    phi=a['basis_values']['even']@U.conj().T;F=np.einsum('qj,cja->qca',a['basis_values']['odd'][:,:4],f)
    expectedR=np.einsum('q,qh,qca,qx,cij->ihjxa',a['haar_weights'],phi.conj(),F,a['basis_values']['input'],v,optimize=True).reshape(r.shape)
    expectedL=np.einsum('q,qh,qca,qx,cji->jxiha',a['haar_weights'],phi,F,a['basis_values']['input'],v,optimize=True).reshape(l.shape)
    np.testing.assert_allclose(r,expectedR,atol=2e-14,rtol=2e-14)
    np.testing.assert_allclose(l,expectedL,atol=2e-14,rtol=2e-14)
    assert np.linalg.norm(l-r.conj().transpose(1,0,2))>1


def test_n6_is_source_return_not_enlarged_starting_field_loop():
    a=momentum_current_angular_images()
    assert(a['full_even_return_count'],a['full_odd_return_count'])==(84,56)
    assert(a['starting_even_field_count'],a['starting_odd_field_count'])==(35,20)
    # Exact highest-weight product phi4*phi1*phi1=(2sqrt(5/7))*phi6.
    import sympy as sp
    z=sp.Symbol('z')
    assert sp.simplify(sp.sqrt(5)*z**4*(sp.sqrt(2)*z)**2-2*sp.sqrt(sp.Rational(5,7))*sp.sqrt(7)*z**6)==0
    b={'level':4,'absolute_spectator':4}
    f={'level':6,'spectator':6}
    assert _possible(f,b,'out')
    assert not _possible(f,b,'input')
    # Fin5 reaches the n6 source square; starting B4 remains unchanged.
    assert _possible({'level':5,'spectator':5},b,'input')
