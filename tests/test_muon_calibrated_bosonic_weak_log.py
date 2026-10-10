"""Independent EFT coefficient and input-chain checks for the partial weak log."""
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
from bhsm.interface.muon_calibrated_bosonic_weak_log import (
    bosonic_weak_leading_log, bosonic_weak_log_eft_identity,
)

INPUT = dict(alpha_0=1/137.035999206,
    fermi_constant_GeV_inverse_squared=1.1663774240217167e-5,
    muon_mass_GeV=.10565842526040435, w_mass_GeV=80.3602,
    z_mass_GeV=91.1876)


def test_independent_closed_loop_subtraction_matches_direct_polynomial_exactly():
    s = sp.Symbol('s', real=True)
    r = 1-4*s
    dipole, vector, axial = (5+r*r)/12, r*r/8, sp.Rational(1, 8)
    full = 16*dipole+sp.Rational(40, 3)*vector+sp.Rational(808, 9)*axial
    closed_muon = sp.Rational(32, 9)*vector+48*axial
    direct = (-65+92*s-184*s*s)/9
    assert sp.expand(-(full-closed_muon)/2-direct) == 0
    # Omitting the neutral-current mixing or subtracting the entire
    # identical-current block would give a different physical coefficient.
    assert sp.expand(-8*dipole-direct) != 0
    identity = bosonic_weak_log_eft_identity()
    assert identity['anomalous_dimensions']['open_vector'] == '88/9'
    assert identity['anomalous_dimensions']['open_axial'] == '376/9'
    assert identity['Higgs_Yukawa_assigned'] is False
    assert identity['full_two_loop_bosonic_constant_inferred'] is False


def test_physical_selected_term_with_independent_high_precision():
    out = bosonic_weak_leading_log(**INPUT)
    with mp.workdps(70):
        a, gf, m, w, z = [mp.mpf(str(INPUT[k])) for k in (
            'alpha_0', 'fermi_constant_GeV_inverse_squared',
            'muon_mass_GeV', 'w_mass_GeV', 'z_mass_GeV')]
        s = 1-(w/z)**2
        r = 1-4*s
        # Independent EFT contraction and log(MW/m), instead of the direct
        # polynomial and squared-scale logarithm used by production.
        mix = 16*(5+r*r)/12+mp.mpf(88)/9*r*r/8+mp.mpf(376)/9/8
        expected = -gf*m*m*a/(8*mp.sqrt(2)*mp.pi**3)*mix*mp.log(w/m)
    assert out['value'] == pytest.approx(float(expected), rel=4e-15)
    assert out['value'] == pytest.approx(-2.141590149659739e-10, rel=4e-15)
    assert abs(out['direct_minus_EFT_arithmetic_residual']) < 1e-24
    assert out['value'] < 0
    assert out['finite_bosonic_remainder'] is None
    assert out['full_bosonic_two_loop'] is None
    assert out['native_evaluated'] is False


@pytest.mark.parametrize('name,derivative',[
    ('alpha_0','alpha'), ('fermi_constant_GeV_inverse_squared','GF'),
    ('muon_mass_GeV','muon_mass'), ('w_mass_GeV','w_mass'),
    ('z_mass_GeV','z_mass')])
def test_analytic_derivatives_against_refined_actual_formula(name, derivative):
    out = bosonic_weak_leading_log(**INPUT)
    step = 2e-5
    p, q = dict(INPUT), dict(INPUT)
    p[name] *= math.exp(step)
    q[name] *= math.exp(-step)
    finite = (bosonic_weak_leading_log(**p)['value']
              -bosonic_weak_leading_log(**q)['value'])/(2*step*INPUT[name])
    assert out['derivatives'][derivative] == pytest.approx(finite, rel=2e-8)


def test_common_mass_scale_and_finite_endpoint_shift():
    out = bosonic_weak_leading_log(**INPUT)
    scaled = dict(INPUT)
    for name in ('muon_mass_GeV','w_mass_GeV','z_mass_GeV'):
        scaled[name] *= 1.125
    other = bosonic_weak_leading_log(**scaled)
    assert other['value']/out['value'] == pytest.approx(1.125**2, rel=2e-15)
    endpoint = out['common_prefactor']*out['dimensionless_log_coefficient']*2*math.log(INPUT['z_mass_GeV']/INPUT['muon_mass_GeV'])
    assert endpoint-out['value'] == pytest.approx(
        out['logarithm_endpoint_MZ_minus_MW_diagnostic'], abs=1e-25)


@pytest.mark.parametrize('name,bad',[
    ('alpha_0', 0), ('alpha_0', True), ('muon_mass_GeV', None),
    ('fermi_constant_GeV_inverse_squared', float('nan')),
    ('w_mass_GeV', float('inf')), ('z_mass_GeV', -1),
    ('muon_mass_GeV', 100), ('w_mass_GeV', 92)])
def test_consumed_numeric_and_hierarchy_guards(name, bad):
    with pytest.raises(ValueError):
        bosonic_weak_leading_log(**dict(INPUT, **{name:bad}))


def test_shared_primitive_chain_and_overlap_scope():
    spec = importlib.util.spec_from_file_location('weak_log_replay',
        ROOT/'scripts/evaluate_muon_calibrated_bosonic_weak_log.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    packet = module.evaluate()
    row = packet['selected_input_gradient']
    assert len(row) == 9 and row[4] == row[8] == 0
    assert row[3] != 0  # rematched GF retains the measured lifetime.
    assert row[5] != 0  # tau dependence enters through the executed decay.
    assert packet['overlap']['closed_fermion_sector_added_again'] is False
    assert packet['remaining']['bosonic_finite_remainder'] is None
    assert packet['remaining']['quark_Hgamma_HZ'] is None
    assert packet['complete_native'] is False
    assert packet['errors']['bosonic_remainder_enclosure'] is None
    assert np.isfinite(row).all()
