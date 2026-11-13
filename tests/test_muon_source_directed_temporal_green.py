"""CONTROL_ONLY exact source-image and invariant decomposition checks."""
import numpy as np
import pytest
import sympy as s
from bhsm.interface.muon_source_directed_temporal_green import source_product_temporal_values,invariant_source_blocks
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_angular_derivative_matrices,real_scalar_basis_transform,scalar_section_labels


def test_source_polynomial_products_are_in_entire_declared_span():
    # Independent exact polynomial coefficient calculation, not fitted values.
    u=s.symbols('u',real=True);p=[s.legendre(k,2*u-1)for k in range(7)]
    g=[u**2*(1-u)**2,(2*u-1)*u**2*(1-u)**2]
    mon=s.Matrix([[s.expand(x).coeff(u,j)for x in p]for j in range(7)])
    assert mon.det()!=0
    for q in g:
        for source in (q,s.diff(q,u),u*q):
            v=s.Matrix([s.expand(source).coeff(u,j)for j in range(7)])
            assert s.expand(sum(a*b for a,b in zip(p,mon.inv()*v))-source)==0


def test_piecewise_source_trial_has_positive_exact_gram_and_true_rates():
    u=s.symbols('u',real=True);p=[s.legendre(k,2*u-1)for k in range(7)]
    functions=[[2*u*x for x in p]+[4*u*u], [2*(1-u)*x for x in p]+[4*(1-u)**2]]
    G=s.zeros(8)
    for f,lo,hi in zip(functions,(0,s.Rational(1,2)),(s.Rational(1,2),1)):
        G+=s.Matrix(8,8,lambda i,j:s.integrate(s.expand(f[i]*f[j]),(u,lo,hi)))
    # Sylvester's criterion proves all8 retained functions independent.
    assert all(G[:k,:k].det()>0 for k in range(1,9))
    x=np.array([.17,.43,.64,.89]);L=.7;app=source_product_temporal_values(x*L,L)
    for row,t in enumerate(x):
        f=functions[0 if t<.5 else 1]
        np.testing.assert_allclose(app['value'][row],[float(a.subs(u,t))for a in f],atol=2e-14,rtol=0)
        np.testing.assert_allclose(app['coordinate_rate'][row],[float(s.diff(a,u).subs(u,t))/.7 for a in f],atol=2e-13,rtol=0)
    assert app['variable_coefficient_image_exact'] is False


def test_full_odd_angular_derivative_has_exact_spectator_blocks():
    labels=scalar_section_labels(3);ids=[i for i,l in enumerate(labels)if l[0]in(1,3)]
    U=real_scalar_basis_transform(3)[np.ix_(ids,ids)]
    E=scalar_angular_derivative_matrices(3)[:,ids][:,:,ids]
    real=np.array([U.conj().T@e@U for e in E]).real
    result=invariant_source_blocks({'derivative_matrices':real})
    assert [len(b['harmonic_indices'])for b in result['angular_blocks']]==[2,2,4,4,4,4]
    assert result['spectator_off_block_max']==0
    assert sum(8*6*len(b['harmonic_indices'])for b in result['angular_blocks'])*3==2880
    # The union is the entire source image, not only eight source columns.
    assert sorted(np.concatenate([b['harmonic_indices']for b in result['angular_blocks']]).tolist())==list(range(20))
    broken=real.copy();broken[0,0,7]=.01
    with pytest.raises(ValueError,match='spectators'):invariant_source_blocks({'derivative_matrices':broken})


def test_complex_harmonic_left_placement_is_not_vertex_conjugation():
    # CONTROL_ONLY source with an anti-Hermitian temporal vertex.
    U=np.array([[1,1],[1j,-1j]])/np.sqrt(2);f=np.array([.2,-.7]);A=np.array([[0,1],[-1,0]],complex)
    right=np.einsum('gh,h,ij->gij',U,f,A)
    left=np.einsum('gh,h,ij->gij',U.conj(),f,A)
    for h in range(2):
        np.testing.assert_allclose(left[h],-right[h].conj().T)
    assert np.linalg.norm(left-right.conj().transpose(0,2,1))>1


@pytest.mark.parametrize('times,L',[(np.array([-.1]),1),(np.array([1.1]),1),(np.array([.2]),0),(np.array([np.nan]),1)])
def test_source_interval_guards(times,L):
    with pytest.raises(ValueError):source_product_temporal_values(times,L)
