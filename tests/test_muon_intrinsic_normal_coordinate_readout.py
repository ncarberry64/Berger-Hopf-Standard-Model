import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_normal_coordinate_readout import (
    normal_coordinate_operator_action,local_matched_spin_functional,
)
from bhsm.interface.muon_intrinsic_covariant_open_current_jet import normal_coordinate_first_momentum_lift
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from bhsm.interface.muon_magnetic_open_lepton_vertex import PAULI


def _literal_multiplication():
    d=scalar_s3_discretization(3);labels=d['real_basis_labels'];Y=d['real_basis_values'];w=d['haar_weights']
    odd=[i for i,l in enumerate(labels)if l[0]==1];even=[i for i,l in enumerate(labels)if l[0]in(0,2)]
    # A complete complex matrix multiplication action, integrated before
    # projection. No Hermitian relation is imposed on the reverse test.
    rng=np.random.default_rng(291);M=rng.normal(size=(3,4,6,6))+1j*rng.normal(size=(3,4,6,6))
    point=np.einsum('ph,Ahij->Apij',Y[:,odd],M)
    C=np.einsum('p,ph,Apij->Ahij',w,Y[:,odd],point).reshape(3,24,6)
    T=np.einsum('p,pe,Apij,ph->Aeihj',w,Y[:,even],point,Y[:,odd]).reshape(3,60,24)
    return M,C,T


def test_constant_and_tangent_apply_literal_same_multiplication():
    M,C,T=_literal_multiplication();R=1.23
    n=normal_coordinate_first_momentum_lift(R);y=n['n1_value_at_identity'];dy=n['n1_unit_coframe_derivative_at_identity']/R
    a=np.zeros((5,4));a[2,1]=.21
    r=normal_coordinate_operator_action(C,T,2*C.conj().transpose(0,2,1),3*T.conj().transpose(0,2,1),
        radius=R,wall_connection=a,H=np.array([0.,1.]),family=1)
    value=np.einsum('h,Ahij->Aij',y,M);gradient=np.einsum('ah,Ahij->Aaij',dy,M)
    np.testing.assert_allclose(r['full_constant_symbol'],value,atol=2e-14)
    np.testing.assert_allclose(r['full_source_spatial_first_jet'],gradient,atol=2e-14)
    np.testing.assert_allclose(r['full_coordinate_response'],0,atol=2e-14)
    expected=np.zeros((3,3,3,6,6),complex)
    for j in range(3):expected[:,j,j]=value
    np.testing.assert_allclose(r['full_coordinate_response_spatial_jet'],expected,atol=3e-14)
    O=r['full_spatial_connection']
    np.testing.assert_allclose(r['full_Wilson_source_spatial_first_jet'],gradient+O[None]@value[:,None]-value[:,None]@O[None],atol=2e-14)
    assert np.linalg.norm(r['forward_reverse_value_difference'])>1
    assert r['finite_factor_kernel_identified_with_Lorentz_self_energy']is False


def test_local_matched_functional_recovers_actual_minimal_magnetic_jet():
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac'];alpha=np.array([gamma[0]@g for g in gamma[1:]])
    e=.31;m=.77;D=np.zeros((3,3,4,4),complex)
    eps=np.zeros((3,3,3));eps[0,1,2]=eps[1,2,0]=eps[2,0,1]=1;eps[0,2,1]=eps[2,1,0]=eps[1,0,2]=-1
    # V=e alpha.A, A=B cross X/2, not an inserted Pauli tensor.
    for A in range(3):
        for j in range(3):D[A,j]=.5*e*sum(eps[i,A,j]*alpha[i]for i in range(3))
    r=local_matched_spin_functional(np.zeros((3,4,4)),D,mass=m,electric_charge=e)
    np.testing.assert_allclose(r['matched_dimensionless_spin_functional'],np.eye(3),atol=2e-15)
    assert r['operator_identification_performed']is False


def test_nonhermitian_current_is_retained_not_hermitianized():
    V=1j*np.array([np.kron(np.eye(2),p)for p in PAULI]);D=np.zeros((3,3,4,4),complex)
    r=local_matched_spin_functional(V,D,mass=2,electric_charge=.5)
    np.testing.assert_allclose(r['matched_dimensionless_spin_functional'],8j*np.eye(3),atol=1e-14)
    assert np.linalg.norm(r['Hermitian_symbol_remainder'])>0


def test_missing_mismatched_operands_fail_before_a_readout():
    with pytest.raises(ValueError):local_matched_spin_functional(None,np.zeros((3,3,4,4)),mass=1,electric_charge=.3)
    with pytest.raises(ValueError):normal_coordinate_operator_action(np.zeros((3,24,6)),np.zeros((3,6,24)),np.zeros((3,6,24)),np.zeros((3,24,60)),radius=1,wall_connection=np.zeros((5,4)),H=[0,1],family=1)
