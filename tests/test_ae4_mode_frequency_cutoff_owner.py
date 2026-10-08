"""Focused adopted-owner/quotient controls; no old production replay."""
import math
from pathlib import Path
import sys

import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import (
    CUTOFF_OWNER_TAG, enclosure_holding_threshold_hypothesis,
    native_spectral_length_contract, native_mode_frequency_energy,
    native_heat_length_squared, native_heat_length_squared_jets,
)


def test_adopted_owner_retains_total_resistance_and_action_inertia():
    c = native_spectral_length_contract()
    assert c['cutoff_owner_tag'] == CUTOFF_OWNER_TAG
    assert c['total_restoring_resistance'] == 'R_star=gamma_star J_Sigma+H_impedance'
    assert c['surface_Jacobi_contribution_retained']
    assert not c['bulk_impedance_only_cutoff_allowed']
    assert 'I_lambda D_tau^2' in c['kinetic_inertia']
    assert '<psi_star,I_star psi_star>' in c['core_energy_rule_natural_units']


def test_bulk_only_and_unsupplied_surface_input_are_rejected():
    with pytest.raises(TypeError):
        native_mode_frequency_energy(bulk_impedance=4, kinetic_inertia=2)
    with pytest.raises(TypeError):
        native_heat_length_squared(surface_jacobi=None, bulk_impedance=4, kinetic_inertia=2)
    assert math.isclose(native_mode_frequency_energy(
        surface_jacobi=2, bulk_impedance=4, kinetic_inertia=2)**2, 3)


def test_birth_is_parent_loss_and_decay_is_distinct_scalar_holding_historical():
    c = native_spectral_length_contract()
    h = enclosure_holding_threshold_hypothesis()
    assert not c['formation_zero_is_support_loss_by_default']
    assert c['surface_rule'] == 'Sigma_star^mu=Sigma_(P->mu)=Sigma_P,out=Sigma_mu,in'
    assert c['evaluation_side'] == 'MUON_CHILD_PLUS_SIDE_AT_BIRTH'
    assert c['parent_loss_and_child_formation_can_share_event']
    assert not c['decay_surface_sets_birth_cutoff']
    assert not c['energy_equality_automatically_removed_by_transfer']
    assert not h['active_owner'] and 'SUPERSEDED' in h['classification']
    assert h['current_owner'] == 'RHO-B2_OPERATOR_VALUED_FORMATION_QUOTIENT'


def test_frequency_squared_and_heat_length_squared_are_reciprocal():
    # Supplied scalar control, with a signed Jacobi contribution.
    data = dict(surface_jacobi=-1, bulk_impedance=5, kinetic_inertia=3)
    E = native_mode_frequency_energy(**data)
    c = native_heat_length_squared(**data)
    assert math.isclose(E*E, 4/3) and c == 3/4
    assert math.isclose(c*E*E, 1)


def test_invalid_resistance_inertia_and_jet_values_fail_closed():
    with pytest.raises(ValueError):
        native_mode_frequency_energy(surface_jacobi=-5, bulk_impedance=4, kinetic_inertia=2)
    with pytest.raises(ValueError):
        native_heat_length_squared(surface_jacobi=1, bulk_impedance=4, kinetic_inertia=0)
    with pytest.raises(ValueError):
        native_heat_length_squared_jets(r=4, i=2, r_x=1, r_y=0, r_xy=float('nan'),
                                       i_x=0, i_y=0, i_xy=0)


def test_total_quotient_mixed_jet_matches_independent_finite_difference():
    r = lambda x,y: 4+.7*x-.4*y+.6*x*y+.1*x*x
    i = lambda x,y: 1.3-.2*x+.3*y-.15*x*y+.05*y*y
    j = native_heat_length_squared_jets(r=4, i=1.3, r_x=.7, r_y=-.4,
                                       r_xy=.6, i_x=-.2, i_y=.3, i_xy=-.15)
    c = lambda x,y: i(x,y)/r(x,y)
    for h in (1e-3, 5e-4, 2.5e-4):
        mixed = (c(h,h)-c(h,-h)-c(-h,h)+c(-h,-h))/(4*h*h)
        assert abs(mixed-j['c_xy']) < 2e-8
        assert abs((c(h,0)-c(-h,0))/(2*h)-j['c_x']) < 2e-8
        assert abs((c(0,h)-c(0,-h))/(2*h)-j['c_y']) < 2e-8


def test_source_direction_extension_is_complex_linear_not_sesquilinear():
    data = dict(r=4, i=1.3, r_x=.7, r_y=-.4, r_xy=.6, i_x=-.2, i_y=.3, i_xy=-.15)
    real = native_heat_length_squared_jets(**data)
    weight = 1.2-.7j
    for key in ('r_y','r_xy','i_y','i_xy'): data[key] *= weight
    extended = native_heat_length_squared_jets(**data)
    assert abs(extended['c_y']-weight*real['c_y']) < 1e-16
    assert abs(extended['c_xy']-weight*real['c_xy']) < 1e-16


def test_total_surface_motion_is_consumed_once():
    x,y,t = sp.symbols('x y t', real=True)
    surface = 2+sp.Rational(1,5)*x-sp.Rational(1,7)*y+sp.Rational(1,9)*x*y
    r = (4+t/3+x/2+y/4+x*y/6).subs(t,surface)
    i = (2+t/5-x/7+y/8+x*y/10).subs(t,surface)
    zero = {x:0,y:0}
    vals = lambda f: (float(f.subs(zero)), float(sp.diff(f,x).subs(zero)),
                      float(sp.diff(f,y).subs(zero)), float(sp.diff(f,x,y).subs(zero)))
    rv,rx,ry,rxy = vals(r);iv,ix,iy,ixy = vals(i)
    j = native_heat_length_squared_jets(r=rv,i=iv,r_x=rx,r_y=ry,r_xy=rxy,
                                       i_x=ix,i_y=iy,i_xy=ixy)
    assert abs(j['c_xy']-float(sp.diff(i/r,x,y).subs(zero))) < 1e-16


def test_owner_does_not_assume_energy_eigenline_or_default_length():
    c = native_spectral_length_contract()
    assert not c['selected_mode_is_resistance_eigenvector_by_default']
    assert c['source_jets_are_total_branch_derivatives']
    assert not c['physical_default_ell_equals_one_allowed']
    with pytest.raises(TypeError): native_heat_length_squared()
    assert not c['numerical_ell_star_evaluated_on_current_C2']


def test_no_measured_particle_or_anomaly_inputs_enter_definition():
    c = native_spectral_length_contract()
    assert not c['measured_particle_or_anomaly_input']
    assert not c['black_hole_magnetar_neutron_and_atomic_data_set_ell_star']
    assert 'hbar=c_light=1' in c['proper_clock_units']
