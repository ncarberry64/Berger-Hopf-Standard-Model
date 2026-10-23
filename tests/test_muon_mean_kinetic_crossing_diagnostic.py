"""Exact basis math and reached pairings; no selected physical quotient."""
import numpy as np
import pytest
import sympy as S
from flint import arb,arb_mat,ctx
from bhsm.interface.muon_mean_kinetic_crossing_diagnostic import (
    fixed_wall_velocity_basis_identity,certify_constraint_schur,
    retained_kinetic_data,targeted_action_pairing,_arb_frobenius_upper,spline_crossing_compatibility,
)


@pytest.mark.parametrize('order',[1,3,12])
def test_w_basis_inclusion_is_injective_and_adm_has_no_coordinate_null(order):
    result=fixed_wall_velocity_basis_identity(order);z=S.symbols('z')
    B=result['W_into_U']
    for j in range(order):
        reconstructed=sum(B[i,j]*S.chebyshevt(i,z) for i in range(order+1))
        assert S.expand(reconstructed-(1-z)*S.chebyshevt(j,z)/2)==0
    assert result['rank']==order
    assert result['endpoint_left_null']==S.zeros(1,order)
    assert result['pointwise_determinant']==-216
    # An independent rational positive Gram establishes the congruence
    # signature, rather than assigning it from tiny numerical eigenvalues.
    G=S.diag(*range(1,order+2))
    hessian=(-42*G).row_join(-6*G*B).col_join((-6*B.T*G).row_join(S.zeros(order)))
    schur=hessian[order+1:,order+1:]-hessian[order+1:,:order+1]*hessian[:order+1,:order+1].inv()*hessian[:order+1,order+1:]
    assert schur==S.Rational(6,7)*B.T*G*B
    assert schur.is_positive_definite
    assert result['exact_coordinate_redundancy'] is False
    assert result['physical_gauge_quotient_proved'] is False


def test_zero_centred_arb_balls_have_a_finite_outward_norm():
    previous=ctx.prec;ctx.prec=128
    try:
        x=arb_mat([[arb(0,'1e-30'),arb(0,'2e-30')]])
        upper=_arb_frobenius_upper(x)
        assert upper>arb('2.2360679e-30') and upper<arb('2.2360681e-30')
    finally:ctx.prec=previous


def test_actual_constraint_elimination_preserves_velocity_inertia_for_supplied_control():
    # CONTROL_ONLY exact finite example; a negative kinetic direction is
    # retained after the genuinely invertible algebraic block is eliminated.
    D=np.array([[2.,1.,.5],[1.,-1.,.25],[.5,.25,3.]])
    result=certify_constraint_schur(D,velocity_count=2)
    assert result['A']['congruence_inertia_certified']
    assert result['K']['congruence_inertia_certified']
    assert (result['A']['positive'],result['A']['negative'])==(1,0)
    assert (result['K']['positive'],result['K']['negative'])==(1,1)
    assert result['A_inverse_residual_upper']<1e-40
    assert result['small_modes_removed'] is False
    assert result['physical_gauge_quotient_selected'] is False


@pytest.mark.parametrize('bad',[np.array([[1.,2.],[0.,1.]]),np.array([[1.,0.],[0.,np.nan]]),np.eye(2,dtype=complex)])
def test_nonphysical_coercion_or_asymmetric_action_is_rejected(bad):
    with pytest.raises(ValueError):certify_constraint_schur(bad,velocity_count=1)


def test_singular_algebraic_block_is_not_pseudoinverted():
    with pytest.raises(ArithmeticError,match='not invertible'):
        certify_constraint_schur(np.array([[1.,1.],[1.,0.]]),velocity_count=1)


@pytest.fixture(scope='module')
def reached():return retained_kinetic_data()


@pytest.mark.parametrize('index,eigen_index,expected',[(10,24,3.552796994629886e-11),(11,24,-5.136827279594051e-11)])
def test_actual_retained_action_pairing_has_the_stored_small_sign(reached,index,eigen_index,expected):
    result=targeted_action_pairing(reached,index,eigen_index,decimal_digits=70,quadrature_points=48)
    value=float(result['total'])
    assert value==pytest.approx(expected,rel=2e-6,abs=2e-18)
    assert value*result['stored_pairing']>0
    assert result['direction_removed_or_quotiented'] is False
    assert result['conditional_nu_squared_action']==4.
    assert result['physical_primal_or_continuum_enclosure'] is False


def test_actual_stored_schur_preserves_the_reached_inertia_change(reached):
    records=[certify_constraint_schur(reached['stored']['restricted_legendre_matrices'][i]) for i in (10,11)]
    for r in records:
        assert r['A']['congruence_inertia_certified'] and r['K']['congruence_inertia_certified']
        assert (r['A']['positive'],r['A']['negative'])==(22,10)
        assert r['retained_velocity_count']==74
    assert (records[0]['K']['positive'],records[0]['K']['negative'])==(60,14)
    assert (records[1]['K']['positive'],records[1]['K']['negative'])==(59,15)


def test_actual_crossing_exports_all_phase_and_paired_source_compatibility_entries(reached):
    result=spline_crossing_compatibility(reached)
    assert .000625<result['numerical_root_time']<.0006875
    l=np.array(result['constitutive_null_covector'])
    assert np.linalg.norm(l)==pytest.approx(1.)
    assert l.shape==(106,) and np.array(result['phase_row']).shape==(148,)
    assert np.array(result['source_row']).shape==(8,8)
    assert np.linalg.norm(result['source_row'])>0
    assert result['null_residual_relative']<2e-14
    assert result['simple_crossing_slope_pairing']!=0
    assert result['source_row_alone_is_not_a_failure_verdict'] is True
    assert result['phase_or_compatibility_evaluated'] is False
