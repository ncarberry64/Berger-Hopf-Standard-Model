"""Exact quotient checks and literal transported Fermi normalization."""
from fractions import Fraction
import numpy as np
import pytest
import sympy as s
from bhsm.interface.muon_parent_mean_causal_action import VOLUME
from bhsm.interface.muon_primal_charged_current_response import charged_current_matrices
from bhsm.interface.muon_charged_current_cell_amputation import variational_cayley_amputation
from bhsm.interface.muon_charged_current_fermi_reduction import (
    transported_fermi_template,exact_stored_fermi_template_fit,
)


def test_common_raw_S4_prefactor_cancels_in_kinetic_but_not_quartic_current():
    V,N,R=s.symbols('V N R',positive=True)
    physical_spinor_per_unit_coefficient=V/(R**s.Rational(3,2)*s.sqrt(V))
    common_density=N*R**3*V/V**2
    assert s.simplify(common_density*physical_spinor_per_unit_coefficient**2-N)==0
    assert s.simplify(common_density*physical_spinor_per_unit_coefficient**4-N*V/R**3)==0


def test_untransported_chiral_current_normalization_CONTROL_ONLY():
    a=transported_fermi_template(np.eye(18),N=2.,R4=3.,step=-.125)
    eta=np.diag([1.,-1.,-1.,-1.]);factor=-4*np.sqrt(2)*(-.125)*2*VOLUME/27
    np.testing.assert_allclose(a['muon_current_map'],np.eye(8),atol=7e-16,rtol=0)
    np.testing.assert_allclose(a['template_tensor'],factor*np.kron(np.eye(2),eta),atol=2e-16,rtol=2e-15)
    assert not a['physical_action_unit_or_low_energy_LSZ_match_evaluated']


def test_literal_complex_raising_current_agrees_with_real_template_CONTROL_ONLY():
    rng=np.random.default_rng(773);M=rng.normal(size=(18,18))+1j*rng.normal(size=(18,18));K=(M+M.conj().T)/2
    V=variational_cayley_amputation(K,np.zeros((1,18,18)),.13)['midpoint_lift']
    a=transported_fermi_template(V,N=1.3,R4=.9,step=.13)
    density_mu=rng.normal(size=8);density_e=rng.normal(size=8)
    # Hermitian bilinear coefficient directions, not chosen physical states.
    Dmu=np.einsum('a,aij->ij',density_mu,charged_current_matrices(1))
    De=np.einsum('a,aij->ij',density_e,charged_current_matrices(2))
    def current(density,family):
        X=charged_current_matrices(family);physical_raising=(X[:4]+1j*X[4:])
        return np.einsum('ij,aji->a',density,np.einsum('ij,ajk,kl->ail',V.conj().T,physical_raising,V))
    jm=current(Dmu,1);je=current(De,2);eta=np.array([1.,-1.,-1.,-1.])
    physical_cross=np.sum(eta*(je*jm.conj()+je.conj()*jm))
    literal=-2*np.sqrt(2)*.13*1.3*VOLUME/.9**3*physical_cross
    assert density_e@a['template_tensor']@density_mu==pytest.approx(literal.real,abs=2e-14,rel=2e-14)
    assert abs(literal.imag)<1e-15


def test_exact_dyadic_template_coefficient_and_zero_remainder_CONTROL_ONLY():
    T=np.eye(8);G=3.25*T;a=exact_stored_fermi_template_fit(T,G,G)
    x=Fraction(13,4)
    assert Fraction.from_float(a['finite_cell_template_fit_coefficient_lower'])<=x
    assert Fraction.from_float(a['finite_cell_template_fit_coefficient_upper'])>=x
    assert a['remainder_Frobenius_norm_lower']==0
    assert a['remainder_Frobenius_norm_upper']==0
    assert not a['exact_stored_template_and_pairing_one_coefficient_representation_excluded']
    assert a['physical_c_F'] is None


def test_whole_tensor_remainder_excludes_one_coefficient_CONTROL_ONLY():
    T=np.eye(8);G=3.25*T;G[0,1]=.125
    a=exact_stored_fermi_template_fit(T,G,G)
    assert a['exact_stored_template_and_pairing_one_coefficient_representation_excluded']
    assert Fraction.from_float(a['remainder_Frobenius_norm_lower'])<=Fraction(1,8)
    assert Fraction.from_float(a['remainder_Frobenius_norm_upper'])>=Fraction(1,8)
    assert a['relative_remainder_lower']>0


def test_pairing_interval_uncertainty_is_not_halved_or_dropped_CONTROL_ONLY():
    T=np.eye(8);center=2*T;lo=center.copy();hi=center.copy();lo[0,0]-=.5;hi[0,0]+=.5
    a=exact_stored_fermi_template_fit(T,lo,hi)
    assert a['finite_cell_template_fit_coefficient_lower']<=2-.5/8
    assert a['finite_cell_template_fit_coefficient_upper']>=2+.5/8
    assert not a['source_Cayley_metric_template_formation_error_enclosed']


def test_unknown_metric_and_zero_template_are_rejected():
    with pytest.raises(ValueError):transported_fermi_template(np.eye(18),N=None,R4=1.,step=.1)
    with pytest.raises(ValueError):transported_fermi_template(np.eye(18),N=1.,R4=1.,step=0.)
    with pytest.raises(ValueError):exact_stored_fermi_template_fit(np.zeros((8,8)),np.eye(8),np.eye(8))
    with pytest.raises(ValueError):exact_stored_fermi_template_fit(np.eye(8),np.eye(8),-np.eye(8))
