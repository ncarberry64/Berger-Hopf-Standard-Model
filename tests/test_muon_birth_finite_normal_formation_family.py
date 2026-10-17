import numpy as np
import pytest

from bhsm.interface.muon_birth_finite_normal_boundary_action import load_completed_finite_normal_cell
from bhsm.interface.muon_birth_finite_normal_formation_family import fixed_primal_area_operator_family


@pytest.fixture(scope='module')
def actual_child():
    return load_completed_finite_normal_cell('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')


def test_zero_formal_area_coefficient_reproduces_saved_full_boundary_action(actual_child):
    a=fixed_primal_area_operator_family(actual_child,0.)
    np.testing.assert_allclose(a['normal_form'],.00029218679486367,rtol=2e-10,atol=1e-14)
    assert a['fixed_primal_area_load_norm']==0.
    assert not a['physical_stationarity_at_positive_gamma_claimed']
    assert not a['raw_area_Hessian_identified_with_Jacobi']


def test_positive_area_retains_its_offshell_euler_load_before_internal_elimination(actual_child):
    base=fixed_primal_area_operator_family(actual_child,0.)
    moved=fixed_primal_area_operator_family(actual_child,1e-4)
    n=(len(actual_child['arrays']['stage_action_gradient'][0])-40)//2
    np.testing.assert_allclose(moved['fixed_primal_algebraic_residual']-base['fixed_primal_algebraic_residual'],
        1e-4*moved['area_gradient'][2*n:],rtol=1e-9,atol=3e-15)
    assert moved['fixed_primal_area_load_norm']>0.
    assert abs(moved['normal_form']-base['normal_form'])>1e-8
    assert np.max(abs(moved['reduced']['attachment_stationarity_residual']))<1e-12


def test_negative_formal_surface_coefficient_is_rejected(actual_child):
    with pytest.raises(ValueError,match='nonnegative'):
        fixed_primal_area_operator_family(actual_child,-1.)
