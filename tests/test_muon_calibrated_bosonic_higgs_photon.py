"""Physical fixed-Y normalization, source integral and shared-input checks."""
import importlib.util
import math
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_calibrated_bosonic_higgs_photon import (
    bosonic_higgs_photon_w_projection, transverse_w_higgs_kernel,
)

INPUT = dict(alpha_0=1/137.035999206,
    fermi_constant_GeV_inverse_squared=1.1663774240217167e-5,
    muon_mass_GeV=.10565842526040435, w_mass_GeV=80.3602,
    higgs_mass_GeV=125.11)


def test_symmetrization_is_exact_primary_integral_identity():
    x = sp.Symbol('x')
    b = x*(3*x*(4*x-1)+10)
    assert sp.expand((b+b.subs(x, 1-x))/2
                     -(sp.Rational(19, 2)-15*x*(1-x))) == 0


def test_selected_physical_projection_against_literal_high_precision():
    out = bosonic_higgs_photon_w_projection(**INPUT)
    with mp.workdps(65):
        a, gf, m, w, h = [mp.mpf(str(INPUT[k])) for k in (
            'alpha_0','fermi_constant_GeV_inverse_squared',
            'muon_mass_GeV','w_mass_GeV','higgs_mass_GeV')]
        z = (w/h)**2
        F = mp.quad(lambda x: (x*(3*x*(4*x-1)+10)*z-x*(1-x))
                    *mp.log(z/(x*(1-x)))/(z-x*(1-x))/2, [0, .5, 1])
        v = 1/mp.sqrt(mp.sqrt(2)*gf)
        fixed_y = mp.mpf(str(out['fixed_Y_mu']))
        value = a*m*fixed_y/mp.sqrt(2)*F/(8*mp.pi**3*v)
    assert out['kernel']['value'] == pytest.approx(float(F), rel=5e-15)
    assert out['value'] == pytest.approx(float(value), rel=5e-15)
    assert out['value'] == pytest.approx(3.23649055044526e-11, rel=5e-15)
    assert out['value'] > 0
    assert out['relative_H_muon_coupling_diagnostic'] != 1.
    assert out['relative_H_muon_coupling_is_fit'] is False
    assert out['native_evaluated'] is False
    assert out['finite_bosonic_remainder'] is None
    assert out['gauge_dependent_vertex_and_non_Barr_Zee_completion_included'] is False


@pytest.mark.parametrize('z', [.25, .1])
def test_removable_internal_thresholds_are_not_poles(z):
    out = transverse_w_higgs_kernel(z)
    with mp.workdps(65):
        zz = mp.mpf(str(z))
        points = [mp.mpf(0), mp.mpf('.5'), mp.mpf(1)]
        if z < .25:
            root = mp.sqrt(1-4*zz)
            points = [mp.mpf(0), (1-root)/2, mp.mpf('.5'),
                      (1+root)/2, mp.mpf(1)]
        def literal(x):
            t = x*(1-x)
            numerator = x*(3*x*(4*x-1)+10)*zz-t
            ell = 1/t if abs(zz-t) < mp.mpf('1e-55') else mp.log(zz/t)/(zz-t)
            return numerator*ell/2
        expected = mp.quad(literal, points)
    assert out['value'] == pytest.approx(float(expected), rel=2e-12)
    step = 1e-5
    finite = (transverse_w_higgs_kernel(z*math.exp(step))['value']
              -transverse_w_higgs_kernel(z*math.exp(-step))['value'])/(2*step)
    assert out['log_z_derivative'] == pytest.approx(finite, rel=3e-8)


@pytest.mark.parametrize('name,derivative', [
    ('alpha_0','alpha'), ('fermi_constant_GeV_inverse_squared','GF'),
    ('muon_mass_GeV','muon_mass'), ('w_mass_GeV','w_mass'),
    ('higgs_mass_GeV','higgs_mass')])
def test_analytic_fixed_Y_partials_against_actual_formula(name, derivative):
    out = bosonic_higgs_photon_w_projection(**INPUT)
    step = 2e-5
    p, q = dict(INPUT), dict(INPUT)
    p[name] *= math.exp(step)
    q[name] *= math.exp(-step)
    finite = (bosonic_higgs_photon_w_projection(**p)['value']
              -bosonic_higgs_photon_w_projection(**q)['value'])/(2*step*INPUT[name])
    assert out['derivatives'][derivative] == pytest.approx(finite, rel=3e-8)


def test_fixed_Y_mass_scaling_is_linear_and_not_pole_Yukawa_substitution():
    out = bosonic_higgs_photon_w_projection(**INPUT)
    changed = bosonic_higgs_photon_w_projection(**dict(INPUT,
        muon_mass_GeV=1.1*INPUT['muon_mass_GeV']))
    assert changed['fixed_Y_mu'] == out['fixed_Y_mu']
    assert changed['radial_H_muon_coupling'] == out['radial_H_muon_coupling']
    assert changed['value']/out['value'] == pytest.approx(1.1, rel=2e-15)
    assert changed['relative_H_muon_coupling_diagnostic'] == pytest.approx(
        out['relative_H_muon_coupling_diagnostic']/1.1, rel=2e-15)


@pytest.mark.parametrize('name,bad', [
    ('alpha_0',0), ('alpha_0',True), ('muon_mass_GeV',None),
    ('higgs_mass_GeV',float('nan')), ('w_mass_GeV',float('inf')),
    ('fermi_constant_GeV_inverse_squared',-1), ('muon_mass_GeV',100)])
def test_input_and_external_mass_hierarchy_guards(name, bad):
    with pytest.raises(ValueError):
        bosonic_higgs_photon_w_projection(**dict(INPUT, **{name:bad}))


def test_executed_rematched_GF_and_shared_primitive_chain():
    spec = importlib.util.spec_from_file_location('higgs_photon_replay',
        ROOT/'scripts/evaluate_muon_calibrated_bosonic_higgs_photon.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    packet = module.evaluate()
    row = packet['selected_input_gradient']
    assert len(row) == 9 and row[7] == row[8] == 0
    assert row[3] != 0 and row[4] != 0 and row[5] != 0
    assert packet['input_uncertainty']['fixed_Y_partial_muon_mass_power'] == 1
    assert packet['overlap']['bosonic_log_included_again'] is False
    assert packet['overlap']['fixed_Y_closed_lepton_Hgamma_HZ_added_again'] is False
    assert packet['errors']['full_finite_bosonic_remainder_enclosure'] is None
    assert packet['complete_native'] is False
    assert np.isfinite(row).all()
