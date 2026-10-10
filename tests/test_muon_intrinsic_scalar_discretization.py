"""Scalar representation, exact quadrature and common-coefficient tests.

All coefficient/interval examples are CONTROL_ONLY mathematical checks;
they assign no physical Higgs, event load, Cauchy data or selected state.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_intrinsic_scalar_discretization import (
    UNIT_S3_VOLUME,adjoint_rotation_values,polynomial_temporal_discretization,
    real_scalar_basis_labels,real_scalar_basis_transform,
    realify_coefficients,realify_complex_linear_map,scalar_angular_derivative_matrices,
    scalar_basis_values,scalar_s3_discretization,scalar_section_labels,
    symmetric_power_matrix,tensor_product_scalar_fields,unrealify_coefficients,
)


@pytest.mark.parametrize('level',[0,1,2,3])
def test_scalar_labels_and_haar_gram_have_no_spinor_sign_or_weyl_copy(level):
    space=scalar_s3_discretization(level)
    count=sum((n+1)**2 for n in range(level+1))
    assert len(space['scalar_labels'])==count
    assert all(len(row)==3 for row in space['scalar_labels'])
    assert len(space['weak_section_labels'])==2*count
    assert space['complex_doublet_coefficient_count']==2*count
    assert space['real_doublet_coefficient_count']==4*count
    V=space['basis_values']; weights=space['haar_weights']
    np.testing.assert_allclose(V.conj().T@(weights[:,None]*V),np.eye(count),atol=9e-15,rtol=0)
    np.testing.assert_allclose(V.conj().T@(space['unit_s3_weights'][:,None]*V),
                               UNIT_S3_VOLUME*np.eye(count),atol=2e-13,rtol=0)
    assert weights.sum()==pytest.approx(1.,abs=2e-15)
    assert space['unit_s3_weights'].sum()==pytest.approx(2*math.pi**2,abs=3e-14)
    assert not space['physical_mode_selected']
    assert not space['physical_boundary_conditions_selected']


@pytest.mark.parametrize('level',[0,1,2,3])
def test_real_scalar_harmonics_obey_conjugation_and_have_no_complex_redundancy(level):
    space=scalar_s3_discretization(level); labels=space['scalar_labels']
    index={label:i for i,label in enumerate(labels)}
    V=space['basis_values']; U=real_scalar_basis_transform(level)
    real_labels=real_scalar_basis_labels(level)
    assert real_labels==space['real_basis_labels']
    assert U.shape==(len(labels),len(labels))
    assert len(real_labels)==len(labels)
    assert sum(part=='self' for n,m,k,part in real_labels)==level//2+1
    np.testing.assert_array_equal(U,space['real_basis_coefficient_transform'])
    for i,(n,m,k) in enumerate(labels):
        sign=1 if ((m-k)//2)%2==0 else -1
        np.testing.assert_allclose(V[:,i].conj(),sign*V[:,index[n,-m,-k]],atol=2e-15,rtol=0)
    np.testing.assert_allclose(U.conj().T@U,np.eye(len(labels)),atol=3e-16,rtol=0)
    transformed=V@U
    np.testing.assert_allclose(transformed.imag,0,atol=2e-15,rtol=0)
    VR=space['real_basis_values']
    assert not np.iscomplexobj(VR)
    np.testing.assert_allclose(VR,transformed.real,atol=0,rtol=0)
    for column,(n,m,k,part) in enumerate(real_labels):
        f=V[:,index[n,m,k]]
        expected=f.real if part=='self' else math.sqrt(2)*(f.real if part=='real' else f.imag)
        np.testing.assert_allclose(VR[:,column],expected,atol=7e-16,rtol=0)
    np.testing.assert_allclose(VR.T@(space['haar_weights'][:,None]*VR),
                               np.eye(len(labels)),atol=9e-15,rtol=0)
    # CONTROL_ONLY arbitrary real gauge-chart scalar, not a chosen field.
    coefficients=np.linspace(-.7,.9,len(labels))
    complex_coefficients=U@coefficients
    np.testing.assert_allclose(V@complex_coefficients,VR@coefficients,atol=5e-15,rtol=0)
    conjugate_coefficients=np.array([((-1)**((m-k)//2))*complex_coefficients[index[n,-m,-k]].conjugate()
                                    for n,m,k in labels])
    np.testing.assert_allclose(complex_coefficients,conjugate_coefficients,atol=0,rtol=0)
    assert not space['physical_mode_selected']


@pytest.mark.parametrize('level',[0,1,2,3])
def test_real_scalar_derivatives_are_real_antisymmetric_same_coframe_maps(level):
    space=scalar_s3_discretization(level); U=space['real_basis_coefficient_transform']
    ER=space['real_angular_derivative_matrices']; VR=space['real_basis_values']
    transformed=U.conj().T@space['angular_derivative_matrices']@U
    assert not np.iscomplexobj(ER)
    assert not np.iscomplexobj(space['real_basis_derivative_values'])
    np.testing.assert_allclose(transformed.imag,0,atol=8e-16,rtol=0)
    np.testing.assert_allclose(ER,transformed.real,atol=0,rtol=0)
    np.testing.assert_allclose(ER+ER.transpose(0,2,1),0,atol=8e-16,rtol=0)
    np.testing.assert_allclose(np.einsum('pm,amn->pan',VR,ER),
                               space['real_basis_derivative_values'],atol=3e-15,rtol=0)
    np.testing.assert_allclose(ER[0]@ER[1]-ER[1]@ER[0],-2*ER[2],atol=4e-15,rtol=0)
    levels=np.array([n*(n+2) for n,m,k,part in space['real_basis_labels']])
    np.testing.assert_allclose(-sum(a@a for a in ER),np.diag(levels),atol=8e-15,rtol=0)
    # Independently differentiate group values, rather than only compare
    # a matrix transform to itself.  All sample charts are CONTROL_ONLY.
    g=space['su2_points'][::47]
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    eps=1e-5; real_at_points=(scalar_basis_values(g,level)@U).real
    for a in range(3):
        gp=(math.cos(eps)*np.eye(2)-1j*math.sin(eps)*sigma[a])[None]@g
        gm=(math.cos(eps)*np.eye(2)+1j*math.sin(eps)*sigma[a])[None]@g
        differentiated=((scalar_basis_values(gp,level)-scalar_basis_values(gm,level))@U).real/(2*eps)
        np.testing.assert_allclose(differentiated,real_at_points@ER[a],atol=8e-10,rtol=3e-10)


def test_real_gauge_sampling_removes_actual_complex_conjugate_pair_null_direction():
    # CONTROL_ONLY algebraic null direction in the old Re(complex field)
    # coordinates.  It is absent from the orthonormal real harmonic chart.
    space=scalar_s3_discretization(1); labels=space['scalar_labels']
    i=labels.index((1,1,-1)); j=labels.index((1,-1,1))
    redundant=np.zeros(len(labels),complex); redundant[i]=1; redundant[j]=1
    assert np.linalg.norm(redundant)>0
    np.testing.assert_allclose((space['basis_values']@redundant).real,0,atol=0,rtol=0)
    VR=space['real_basis_values']; weights=space['haar_weights']
    coefficient=np.linspace(.1,.9,len(labels))
    assert weights@((VR@coefficient)**2)==pytest.approx(coefficient@coefficient,abs=2e-15)


@pytest.mark.parametrize('level',[0,1,2,3])
def test_symmetric_power_is_the_actual_unitary_su2_representation(level):
    # CONTROL_ONLY group elements from the quadrature, not a selected field.
    points=scalar_s3_discretization(1)['su2_points'][[0,11,17,33]]
    other=points[[2,3,0,1]]
    D=symmetric_power_matrix(points,level)
    np.testing.assert_allclose(D.conj().transpose(0,2,1)@D,np.broadcast_to(np.eye(level+1),D.shape),atol=4e-15)
    product=symmetric_power_matrix(points@other,level)
    np.testing.assert_allclose(product,D@symmetric_power_matrix(other,level),atol=3e-15)


def test_right_coframe_derivative_maps_match_differentiated_group_values():
    # CONTROL_ONLY independent group differentiation fixes the coframe sign.
    N=3; space=scalar_s3_discretization(N); g=space['su2_points'][::47]
    V=scalar_basis_values(g,N); E=space['angular_derivative_matrices']
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    eps=1e-5
    for a in range(3):
        gp=(math.cos(eps)*np.eye(2)-1j*math.sin(eps)*sigma[a])[None]@g
        gm=(math.cos(eps)*np.eye(2)+1j*math.sin(eps)*sigma[a])[None]@g
        derivative=(scalar_basis_values(gp,N)-scalar_basis_values(gm,N))/(2*eps)
        np.testing.assert_allclose(derivative,V@E[a],atol=8e-10,rtol=3e-10)
        np.testing.assert_allclose(E[a].conj().T,-E[a],atol=0,rtol=0)
    np.testing.assert_allclose(E[0]@E[1]-E[1]@E[0],-2*E[2],atol=4e-15)
    eigen=np.array([n*(n+2) for n,m,k in space['scalar_labels']])
    np.testing.assert_allclose(-sum(a@a for a in E),np.diag(eigen),atol=4e-15)


@pytest.mark.parametrize('N',[0,1,2])
def test_quadrature_integrates_every_polynomial_monomial_in_its_claimed_band(N):
    # Exhaust all z1^a bar(z1)^b z2^c bar(z2)^d up to the declared degree.
    # Nonzero phases vanish; balanced powers give the exact beta integral.
    space=scalar_s3_discretization(N)
    degree=space['quadrature_polynomial_degree'];g=space['su2_points']; w=space['haar_weights']
    z1=g[:,0,0];z2=g[:,0,1]
    powers=[[z**k for k in range(degree+1)] for z in (z1,z1.conj(),z2,z2.conj())]
    for a in range(degree+1):
        for b in range(degree-a+1):
            for c in range(degree-a-b+1):
                for d in range(degree-a-b-c+1):
                    value=w@(powers[0][a]*powers[1][b]*powers[2][c]*powers[3][d])
                    exact=math.factorial(a)*math.factorial(c)/math.factorial(a+c+1) if a==b and c==d else 0.
                    assert value==pytest.approx(exact,abs=8e-16)
    assert degree>=4*N
    assert space['torus_count']>degree
    assert 2*space['radial_count']-1>=degree//2


def test_quartic_normalization_is_not_gaussian_or_fermion_shell_multiplicity():
    space=scalar_s3_discretization(1)
    index=space['scalar_labels'].index((1,1,1))
    other=space['scalar_labels'].index((1,1,-1))
    f=space['basis_values'][:,index];h=space['basis_values'][:,other]
    assert space['haar_weights']@abs(f)**4==pytest.approx(4/3,abs=5e-16)
    assert space['haar_weights']@(abs(f)**2*abs(h)**2)==pytest.approx(2/3,abs=5e-16)
    assert space['unit_s3_weights']@abs(f)**4==pytest.approx((2*math.pi**2)*4/3,abs=8e-15)


def test_actual_adjoint_quaternion_rotation_and_owned_unit_sp1_norm():
    space=scalar_s3_discretization(1);g=space['su2_points']; R=space['adjoint_rotations']
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    np.testing.assert_allclose(R.transpose(0,2,1)@R,np.broadcast_to(np.eye(3),R.shape),atol=9e-16)
    np.testing.assert_allclose(np.linalg.det(R),1.,atol=1e-15)
    conjugated=np.einsum('pij,djk,plk->pdil',g,-1j*sigma,g.conj())
    reconstructed=np.einsum('pad,aij->pdij',R,-1j*sigma)
    np.testing.assert_allclose(conjugated,reconstructed,atol=5e-16)
    tau=np.einsum('pid,dab->piab',R,-1j*sigma)
    norm=np.einsum('piab,piac->pbc',tau.conj(),tau)
    np.testing.assert_allclose(norm,np.broadcast_to(3*np.eye(2),norm.shape),atol=3e-15)
    assert np.linalg.norm(R[0]-R[1])>0.


def test_unscaled_realification_preserves_complex_maps_and_real_pairing():
    # CONTROL_ONLY arbitrary complex coefficient/map algebra.
    rng=np.random.default_rng(748);c=rng.normal(size=(3,5,2))+1j*rng.normal(size=(3,5,2))
    r=realify_coefficients(c)
    np.testing.assert_array_equal(unrealify_coefficients(r,c.shape),c)
    A=rng.normal(size=(8,c.size))+1j*rng.normal(size=(8,c.size))
    np.testing.assert_allclose(realify_complex_linear_map(A)@r,realify_coefficients(A@c.ravel()),atol=8e-15)
    v=rng.normal(size=c.shape)+1j*rng.normal(size=c.shape)
    assert r@realify_coefficients(v)==pytest.approx(np.vdot(c,v).real,abs=2e-14)
    # A Hermitian complex form becomes a real symmetric form; 2 Re belongs
    # in the action pairing, not in an independently doubled momentum.
    B=A.conj().T@A; RB=realify_complex_linear_map(B)
    np.testing.assert_allclose(RB,RB.T,atol=4e-14)
    assert 2*r@RB@r==pytest.approx(2*np.vdot(c.ravel(),B@c.ravel()).real,rel=3e-15)


@pytest.mark.parametrize('degree',[1,2,4])
def test_temporal_basis_exact_physical_clock_derivatives_and_endpoint_identity(degree):
    # CONTROL_ONLY explicit coordinate interval; no physical BC selected.
    time=polynomial_temporal_discretization(-.3,.7,degree)
    nodes=time['interpolation_times'];t=time['quadrature_times'];B=time['basis_values'];D=time['basis_time_derivatives']
    for power in range(degree+1):
        np.testing.assert_allclose(B@(nodes**power),t**power,atol=2e-15)
        expected=np.zeros_like(t) if power==0 else power*t**(power-1)
        derivative_rounding=2*np.finfo(float).eps*max(1.,np.linalg.norm(D,np.inf))
        np.testing.assert_allclose(D@(nodes**power),expected,atol=derivative_rounding)
    W=np.diag(time['quadrature_weights']); ends=time['endpoint_values']
    np.testing.assert_allclose(B.T@W@D+D.T@W@B,
                               np.outer(ends[1],ends[1])-np.outer(ends[0],ends[0]),atol=9e-15)
    assert time['endpoint_orientations']==(-1,1)
    assert time['selected_cauchy_data'] is None
    assert not time['retarded_homogeneous_component_selected']
    assert not time['physical_boundary_conditions_selected']


def test_temporal_quartic_trial_products_are_integrated_exactly():
    time=polynomial_temporal_discretization(2.,5.,3)
    nodes=time['interpolation_times'];t=time['quadrature_times'];w=time['quadrature_weights']
    cubic=(nodes-2)**3; values=time['basis_values']@cubic
    assert w@(values**4)==pytest.approx(3**13/13,rel=4e-15)
    np.testing.assert_allclose(values,(t-2)**3,atol=7e-15)


def test_tensor_product_h_and_p_use_one_consistent_coefficient_block_each():
    space=scalar_s3_discretization(1);time=polynomial_temporal_discretization(1.,2.,2)
    rng=np.random.default_rng(420);c=rng.normal(size=(3,5,2))+1j*rng.normal(size=(3,5,2))
    fields=tensor_product_scalar_fields(space,time,c)
    # Independent evaluate time polynomials, then each angular derivative
    # as a coefficient map; never independently specify D_t H.
    at_time=np.einsum('tl,lnw->tnw',time['basis_values'],c)
    rate=np.einsum('tl,lnw->tnw',time['basis_time_derivatives'],c)
    np.testing.assert_allclose(fields['field_values'],np.einsum('an,tnw->taw',space['basis_values'],at_time),atol=3e-15)
    np.testing.assert_allclose(fields['coordinate_time_derivatives'],np.einsum('an,tnw->taw',space['basis_values'],rate),atol=8e-15)
    for i,E in enumerate(space['angular_derivative_matrices']):
        ec=np.einsum('nm,tmw->tnw',E,at_time)
        np.testing.assert_allclose(fields['unit_s3_derivatives'][:,:,i],
                                   np.einsum('an,tnw->taw',space['basis_values'],ec),atol=3e-15)
    np.testing.assert_allclose(fields['endpoint_values'][0],space['basis_values']@c[0],atol=1e-15)
    np.testing.assert_allclose(fields['endpoint_values'][1],space['basis_values']@c[-1],atol=1e-15)
    assert fields['spacetime_quadrature_weights'].sum()==pytest.approx((2-1)*2*math.pi**2,abs=4e-14)
    assert fields['all_derivatives_from_same_coefficients']
    assert not fields['full_covariant_derivatives_selected']
    momentum=tensor_product_scalar_fields(space,time,2*c)
    np.testing.assert_allclose(momentum['field_values'],2*fields['field_values'],atol=0.)


@pytest.mark.parametrize('level',[-1,True,1.5])
def test_invalid_scalar_band_rejected(level):
    with pytest.raises(ValueError,match='integer'):
        scalar_s3_discretization(level)


def test_quadrature_and_representation_fail_closed():
    with pytest.raises(ValueError,match='four scalar'):
        scalar_s3_discretization(2,quadrature_polynomial_degree=7)
    with pytest.raises(ValueError,match='determinant-one'):
        symmetric_power_matrix(np.array([np.diag([1.,2.])]),1)
    with pytest.raises(ValueError,match='finite SU2'):
        adjoint_rotation_values(np.ones((3,3)))
    with pytest.raises(ValueError,match='quartic'):
        polynomial_temporal_discretization(0.,1.,2,quadrature_order=4)
    with pytest.raises(ValueError,match='future-oriented'):
        polynomial_temporal_discretization(1.,0.,2)


def test_coefficient_shape_and_finiteness_are_not_independent_field_data():
    angular=scalar_s3_discretization(0);temporal=polynomial_temporal_discretization(0.,1.,1)
    with pytest.raises(ValueError,match='coefficient block'):
        tensor_product_scalar_fields(angular,temporal,np.zeros((2,2)))
    with pytest.raises(ValueError,match='finite nonempty'):
        realify_coefficients([complex(float('nan'),0)])
    with pytest.raises(ValueError,match='real coefficient'):
        unrealify_coefficients([1+1j,0],(1,))
    with pytest.raises(ValueError,match='complex shape'):
        unrealify_coefficients([1,0],(2,))
