#!/usr/bin/env python
"""Replay the finite transverse W/Hgamma application with literal fixed Y_mu."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_calibrated_bosonic_higgs_photon import (
    bosonic_higgs_photon_w_projection,
)

CONFIG = 'artifacts/muon_calibrated_pauli_20261009/inputs.json'
CONFIG_SHA = '0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da'
WEAK = 'artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json'
WEAK_SHA = '9c31575ce0889571790f8767cf53ffe043cb9906e0a45a96b194971320a0aad7'
ACTION = 'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py'
ACTION_SHA = 'f3fee1ef24a3f13ef94d4ce5b146f9ac7a827045e369819b35ee8af5ccf0678a'
LOG = 'artifacts/muon_calibrated_bosonic_weak_log_20261010/run_1/bosonic_weak_log.json'
LOG_SHA = '64b89011c453108e651cb2a1d461b97f8c68d2f61ee20ce096ad18677f57f85c'


def _record(path):
    raw = path.read_bytes()
    relative = str(path.relative_to(ROOT)).replace('\\', '/')
    return dict(path=relative, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _frozen(relative, expected):
    path = ROOT/relative
    record = _record(path)
    if record['sha256'] != expected:
        raise ValueError(f'frozen consumed source changed: {relative}')
    return json.loads(path.read_bytes()), record


def evaluate():
    config, config_record = _frozen(CONFIG, CONFIG_SHA)
    weak, weak_record = _frozen(WEAK, WEAK_SHA)
    log, log_record = _frozen(LOG, LOG_SHA)
    action_record = _record(ROOT/ACTION)
    if action_record['sha256'] != ACTION_SHA:
        raise ValueError('fixed-Y intrinsic action owner changed')
    for record in weak['sources']:
        if _record(ROOT/record['path'])['sha256'] != record['sha256']:
            raise ValueError(f"retained weak producer changed: {record['path']}")
    values = config['selected_consumer_values']
    ai = config['primary_measurements']['alpha_inverse_0']['value']
    params = dict(alpha_0=1/ai,
        fermi_constant_GeV_inverse_squared=weak['decay_rematching']['G_F_GeV_minus2'],
        muon_mass_GeV=values['m_mu_GeV']['value'],
        w_mass_GeV=weak['additional_weak_measurements']['W_mass']['value_GeV'],
        higgs_mass_GeV=values['m_h_GeV']['value'])
    result = bosonic_higgs_photon_w_projection(**params)
    refined = bosonic_higgs_photon_w_projection(**params, epsabs=1e-12,
                                               epsrel=1e-13)
    derivative = result['derivatives']
    gf_row = np.asarray(weak['input_uncertainty']['GF_vs_primitive_gradient'])
    mass_row = np.asarray(weak['input_uncertainty']['muon_mass_vs_primitive_gradient'])
    row = derivative['GF']*gf_row+derivative['muon_mass']*mass_row
    row[0] -= derivative['alpha']/ai**2
    row[4] += derivative['higgs_mass']
    row = np.r_[row, derivative['w_mass'], 0., 0.]
    common = weak['local_EW_evaluated_subtotal_input_uncertainty']
    std_plus = np.asarray(common['standard_uncertainties_plus'])
    std_minus = np.asarray(common['standard_uncertainties_minus'])
    with mp.workdps(70):
        alpha, gf, m, w, h = [mp.mpf(str(params[name])) for name in (
            'alpha_0', 'fermi_constant_GeV_inverse_squared',
            'muon_mass_GeV', 'w_mass_GeV', 'higgs_mass_GeV')]
        z = (w/h)**2
        # Literal unsymmetrized primary integral, independent of production's
        # symmetrization and log-quotient series.
        F3 = mp.quad(lambda x: (x*(3*x*(4*x-1)+10)*z-x*(1-x))
                     *mp.log(z/(x*(1-x)))/(z-x*(1-x))/2, [0, .5, 1])
        y = mp.mpf(str(result['fixed_Y_mu']))
        v = 1/mp.sqrt(mp.sqrt(2)*gf)
        high = alpha*m*y/mp.sqrt(2)/(8*mp.pi**3*v)*F3
        high_decimal, F3_decimal = mp.nstr(high, 65), mp.nstr(F3, 65)
        difference = float(abs(mp.mpf(result['value'])-high))
    decay = weak['decay_rematching']
    packet = dict(
        classification='CALIBRATED_FIXED_Y_TRANSVERSE_W_HGAMMA_EW2_PROJECTION',
        evaluated_contribution=result['value'], result=result,
        selected_consumer_inputs=params, selected_input_gradient=row.tolist(),
        selected_input_primitive_order=common['primitive_order'],
        input_uncertainty=dict(
            primitive_order=common['primitive_order'], gradient=row.tolist(),
            standard_uncertainties_plus=std_plus.tolist(),
            standard_uncertainties_minus=std_minus.tolist(),
            illustrative_independent_standard_uncertainty_plus=float(np.linalg.norm(row*std_plus)),
            illustrative_independent_standard_uncertainty_minus=float(np.linalg.norm(row*std_minus)),
            standard_uncertainty_upper_over_all_correlations_plus=float(np.sum(abs(row)*std_plus)),
            standard_uncertainty_upper_over_all_correlations_minus=float(np.sum(abs(row)*std_minus)),
            actual_cross_source_covariance=None,
            fixed_Y_partial_muon_mass_power=1,
            shared_GF_mass_alpha_and_Higgs_dependencies_included=True,
            scope='input uncertainty of evaluated transverse projection only'),
        errors=dict(
            quadrature_error_estimate=result['quadrature_error_estimate'],
            refined_quadrature_error_estimate=refined['quadrature_error_estimate'],
            quadrature_refinement_absolute_difference=abs(result['value']-refined['value']),
            independent_70_digit_literal_integral=high_decimal,
            independent_70_digit_F3=F3_decimal,
            float64_minus_independent_70_digit_application_absolute=difference,
            numerical_comparisons_are_enclosures=False,
            GF_source_sensitivity=derivative['GF'],
            GF_source_induced_estimated_standard_uncertainty=
                abs(derivative['GF'])*decay['decay_GF_combined_estimated_standard_uncertainty'],
            GF_omitted_order_induced_allowance_estimate=
                abs(derivative['GF'])*decay['omitted_order_GF_allowance_estimate'],
            GF_source_correlation_scope='same decay source; sum sensitivities with other weak contributions before propagation',
            suppressed_external_mass_ratio_squared=(params['muon_mass_GeV']/min(params['w_mass_GeV'], params['higgs_mass_GeV']))**2,
            suppressed_mass_ratio_is_remainder_bound=False,
            transverse_omitted_completion_enclosure=None,
            full_finite_bosonic_remainder_enclosure=None,
            complete_uncertainty=False),
        overlap=dict(
            addition_target='previously unevaluated finite bosonic EW2 remainder: transverse W/Hgamma projection only',
            bosonic_log_included_again=False,
            reason_disjoint_from_log='F3 depends on MW/MH; literal fixed-Y prefactor linear in external m_mu and contains no log(m_mu)',
            prior_weak_subtotal=weak['local_EW_evaluated_sector_subtotal'],
            retained_bosonic_log=log['evaluated_contribution'],
            weak_subtotal_with_log_and_transverse_projection=math.fsum((weak['local_EW_evaluated_sector_subtotal'], log['evaluated_contribution'], result['value'])),
            fixed_Y_closed_lepton_Hgamma_HZ_added_again=False,
            fermionic_VVA_gammaZ_rest_excluded=True,
            pure_QED_HVP_HLbL_top_EM_excluded=True,
            minimal_local_gauge_Higgs_matching=True,
            all_action_native_overlap_evaluated=False),
        remaining=dict(
            finite_bosonic_remainder_after_log_and_transverse_W_Hgamma=None,
            finite_bosonic_remainder_definition='complete matched bosonic EW2 minus retained MW-endpoint log minus this transverse W/Hgamma application',
            gauge_dependent_vertex_and_non_Barr_Zee_completion=None,
            HZ_W_counterpart=None,
            Gmu_scheme_finite_counterterm_and_Delta_r_composition=None,
            quark_Hgamma_HZ=None,
            quark_Y_owner_status='up_down_Yukawa_terms_added=False; absolute transported quark-Y vertex not assigned from poles',
            no_finite_bosonic_or_native_remainder_bound=True),
        action_matching=dict(
            radial_coupling='g_hmumu=Y_mu/sqrt(2)',
            fixed_Y_owner='ae31_c2_intrinsic_m4_lepton_action.charged_lepton_yukawa_operator',
            gauge_vertex='g_hWW=2*MW^2/v from minimal calibrated local Higgs kinetic term',
            v='(sqrt(2)*GF)^(-1/2)',
            measured_pole_is_external_on_shell_argument=True,
            intrinsic_pole_matching_completed=False,
            actual_E1_Higgs_profile_inferred=False),
        primary_source_evidence=[
            dict(url='https://arxiv.org/pdf/1502.04199v3', bytes=9728610,
                sha256='b0b886104b0a5bc000d01c82973fcc36b9183d04dfe13e4f0938a4e95b063d5e',
                equations='21,28', sections='4.1-4.2',
                scope='transverse gauge-independent part; omitted structures/non-Barr-Zee cancellation not evaluated here'),
            dict(url='https://arxiv.org/pdf/hep-ph/0509205v1', bytes=552972,
                sha256='db56c21652d3c56e80a8608daaffebf8e2790bc4c5081796092cd74ab0df84e6',
                equations='30-33', scope='complete finite bosonic constants need counterterms and Gmu reparametrization'),
            dict(url='https://arxiv.org/pdf/1607.06292v3', bytes=2806476,
                sha256='03f36fd57574de9f131850652b6e55f98ca971326f24583ce5ee0ff61c4de0a7',
                equation='49', scope='full Higgs-Yukawa-dependent difference includes non-Barr-Zee diagrams and counterterm; not used as a supplied numerical correction')],
        primary_archive_scope='original PDFs retained externally under BHSM_MUON_SPECTRAL_INPUTS_20261010; not redistributed',
        consumed_inputs=[config_record, weak_record, action_record, log_record],
        source_records=[_record(ROOT/'src/bhsm/interface/muon_calibrated_bosonic_higgs_photon.py'),
                        _record(Path(__file__)),
                        _record(ROOT/'src/bhsm/interface/muon_calibrated_matching.py'),
                        *weak['sources']],
        measured_muon_anomaly_used=False, Higgs_or_quark_Yukawa_fitted=False,
        complete_native=False, complete_a_mu=None,
        full_bosonic_EW2_evaluated=False, full_EW_two_loop_evaluated=False,
        action_selected=False, Gate7_closed=False)
    return packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    packet = evaluate()
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output/'bosonic_higgs_photon.json'
    target.write_text(json.dumps(packet, sort_keys=True, indent=2, allow_nan=False)+'\n',
                      encoding='utf8', newline='\n')
    raw = target.read_bytes()
    print(json.dumps(dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                          value=packet['evaluated_contribution']), sort_keys=True))


if __name__ == '__main__':
    main()
