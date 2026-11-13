#!/usr/bin/env python
"""Replay the independently isolated bosonic weak large logarithm."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import math
import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_calibrated_bosonic_weak_log import (
    bosonic_weak_leading_log, bosonic_weak_log_eft_identity,
)
from bhsm.interface.muon_calibrated_higher_qed import leading_electroweak_pauli

CONFIG = 'artifacts/muon_calibrated_pauli_20261009/inputs.json'
CONFIG_SHA = '0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da'
WEAK = 'artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json'
WEAK_SHA = '9c31575ce0889571790f8767cf53ffe043cb9906e0a45a96b194971320a0aad7'
ACTION = 'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py'
ACTION_SHA = 'f3fee1ef24a3f13ef94d4ce5b146f9ac7a827045e369819b35ee8af5ccf0678a'


def _record(path):
    relative = str(path.relative_to(ROOT)).replace('\\', '/')
    raw = path.read_bytes()
    return dict(path=relative, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _frozen_json(relative, sha):
    path = ROOT/relative
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError(f'frozen consumed input changed: {relative}')
    return json.loads(raw), _record(path)


def evaluate():
    config, config_record = _frozen_json(CONFIG, CONFIG_SHA)
    weak, weak_record = _frozen_json(WEAK, WEAK_SHA)
    action_record = _record(ROOT/ACTION)
    if action_record['sha256'] != ACTION_SHA:
        raise ValueError('retained intrinsic Yukawa/action owner changed')
    # The replay consumes the executed Fermi matching and its shared-input
    # derivative, rather than the older provisional GF in the input config.
    for item in weak['sources']:
        if _record(ROOT/item['path'])['sha256'] != item['sha256']:
            raise ValueError(f"retained weak producer changed: {item['path']}")
    measurements = config['primary_measurements']
    values = config['selected_consumer_values']
    ai = measurements['alpha_inverse_0']['value']
    gf = weak['decay_rematching']['G_F_GeV_minus2']
    m = values['m_mu_GeV']['value']
    w = weak['additional_weak_measurements']['W_mass']['value_GeV']
    z = weak['additional_weak_measurements']['Z_mass']['value_GeV']
    params = dict(alpha_0=1/ai, fermi_constant_GeV_inverse_squared=gf,
                  muon_mass_GeV=m, w_mass_GeV=w, z_mass_GeV=z)
    result = bosonic_weak_leading_log(**params)
    derivative = result['derivatives']
    gf_row = np.asarray(weak['input_uncertainty']['GF_vs_primitive_gradient'])
    mass_row = np.asarray(weak['input_uncertainty']['muon_mass_vs_primitive_gradient'])
    row = derivative['GF']*gf_row+derivative['muon_mass']*mass_row
    row[0] -= derivative['alpha']/ai**2
    row = np.r_[row, derivative['w_mass'], derivative['z_mass'], 0.]
    common = weak['local_EW_evaluated_subtotal_input_uncertainty']
    std_plus = np.asarray(common['standard_uncertainties_plus'])
    std_minus = np.asarray(common['standard_uncertainties_minus'])
    uncertainty = dict(primitive_order=common['primitive_order'],
        gradient=row.tolist(), consumer_derivatives=derivative,
        standard_uncertainties_plus=std_plus.tolist(),
        standard_uncertainties_minus=std_minus.tolist(),
        illustrative_independent_standard_uncertainty_plus=float(np.linalg.norm(row*std_plus)),
        illustrative_independent_standard_uncertainty_minus=float(np.linalg.norm(row*std_minus)),
        standard_uncertainty_upper_over_all_correlations_plus=float(np.sum(abs(row)*std_plus)),
        standard_uncertainty_upper_over_all_correlations_minus=float(np.sum(abs(row)*std_minus)),
        actual_cross_source_covariance=None,
        shared_GF_muon_mass_alpha_dependencies_included=True,
        scope='first-order input uncertainty of the evaluated log only; no finite bosonic/native remainder bound')
    with mp.workdps(70):
        a, g, mass, W, Z = [mp.mpf(str(params[k])) for k in (
            'alpha_0', 'fermi_constant_GeV_inverse_squared', 'muon_mass_GeV',
            'w_mass_GeV', 'z_mass_GeV')]
        r = 1-4*(1-(W/Z)**2)
        contraction = 16*(5+r*r)/12+mp.mpf(88)/9*r*r/8+mp.mpf(376)/9/8
        high = -g*mass*mass*a/(8*mp.sqrt(2)*mp.pi**3)*contraction*mp.log(W/mass)
        high_decimal = mp.nstr(high, 65)
        arithmetic_difference = float(abs(mp.mpf(result['value'])-high))
    leading = leading_electroweak_pauli(
        fermi_constant_GeV_inverse_squared=gf, muon_mass_GeV=m,
        w_mass_GeV=w, z_mass_GeV=z)
    dipole_from_retained = 2*math.sqrt(2)*math.pi**2*leading['a_mu_leading_EW']/(gf*m*m)
    dipole_from_source = (5+(1-4*result['sin_squared_theta_W'])**2)/12
    decay = weak['decay_rematching']
    errors = dict(
        float64_minus_independent_70_digit_application_absolute=arithmetic_difference,
        numerical_comparison_scope='independent arithmetic comparison at the same selected float inputs, not an interval enclosure',
        independent_70_digit_decimal=high_decimal,
        quadrature_not_used=True,
        GF_source_standard_uncertainty=decay['decay_GF_combined_estimated_standard_uncertainty'],
        GF_source_sensitivity=derivative['GF'],
        GF_source_induced_estimated_standard_uncertainty=
            abs(derivative['GF'])*decay['decay_GF_combined_estimated_standard_uncertainty'],
        GF_omitted_order_induced_allowance_estimate=
            abs(derivative['GF'])*decay['omitted_order_GF_allowance_estimate'],
        GF_source_correlation_scope='same decay theory source as retained weak packet; sensitivities must be summed before propagating it',
        logarithm_endpoint_MZ_minus_MW_diagnostic=result['logarithm_endpoint_MZ_minus_MW_diagnostic'],
        logarithm_endpoint_difference_is_uncertainty_bound=False,
        suppressed_weak_mass_ratio_squared=(m/w)**2,
        suppressed_mass_ratio_is_remainder_bound=False,
        bosonic_remainder_enclosure=None,
        missing_bosonic_constant_standard_uncertainty=None,
        complete_uncertainty=False)
    module = ROOT/'src/bhsm/interface/muon_calibrated_bosonic_weak_log.py'
    return dict(
        classification='CALIBRATED_MINIMAL_GAUGE_CURRENT_BOSONIC_EW2_LEADING_LOG',
        evaluated_contribution=result['value'],
        a_mu_bosonic_EW2_leading_log=result['value'], result=result,
        selected_consumer_inputs=params,
        selected_input_gradient=row.tolist(),
        selected_input_primitive_order=common['primitive_order'],
        input_uncertainty=uncertainty, errors=errors,
        operator_reduction=bosonic_weak_log_eft_identity(),
        retained_dipole_coefficient_check=dict(
            C_dipole_from_retained_leading_EW=dipole_from_retained,
            C_dipole_from_EFT=dipole_from_source,
            arithmetic_residual=dipole_from_retained-dipole_from_source,
            C_dipole_is_Higgs_Yukawa=False),
        overlap=dict(
            addition_target='previously unevaluated bosonic EW2 slot: logarithmic part only',
            previous_weak_packet_modified=False,
            prior_weak_subtotal=weak['local_EW_evaluated_sector_subtotal'],
            weak_subtotal_with_this_log=math.fsum((weak['local_EW_evaluated_sector_subtotal'], result['value'])),
            closed_fermion_sector_added_again=False,
            fermionic_VVA_and_gammaZ_rest_excluded=True,
            fixed_Y_lepton_Hgamma_HZ_excluded=True,
            scalar_H_one_loop_photonic_dressing_included=False,
            pure_QED_HVP_HLbL_top_EM_sectors_excluded=True,
            whole_bosonic_reference_added=False,
            matching_class='same retained minimal calibrated W/Z dipole and Z-current EFT; not a new BHSM full-action matching claim'),
        remaining=dict(
            bosonic_finite_remainder=None,
            bosonic_finite_remainder_definition='full matched bosonic EW2 minus this MW-endpoint leading logarithm',
            fixed_Y_scalar_two_loop_remainder=None,
            quark_Hgamma_HZ=None,
            quark_Y_owner='ae31_c2_intrinsic_m4_lepton_action.action_composition_contract',
            quark_Y_status='up_down_Yukawa_terms_added=False; no absolute transported quark-Y prefactor assigned from pole masses',
            full_bosonic_EW2_evaluated=False,
            full_native_overlap=None, full_native_response=None),
        primary_source_evidence=[
            dict(url='https://arxiv.org/pdf/hep-ph/9512369v3',
                 sha256='3b8da26be8a13e3f0c3f6ab7257d8bcf046b297fedfbfe5158d769064eb069df',
                 bytes=126287, equations='10-11',
                 retained_archive_location='external BHSM_MUON_SPECTRAL_INPUTS_20261010; primary PDF not redistributed'),
            dict(url='https://arxiv.org/pdf/hep-ph/9803384v1',
                 sha256='388c770b6aa8ab23c71e21242971aa23dc02144d65c1e61eada389604dbd5b8d',
                 bytes=144341, equations='11-15,19-24', pages='3-5',
                 retained_archive_location='external BHSM_MUON_SPECTRAL_INPUTS_20261010; primary PDF not redistributed')],
        consumed_inputs=[config_record, weak_record, action_record],
        source_records=[_record(module), _record(Path(__file__)),
                        *weak['sources']],
        measured_muon_anomaly_used=False, Higgs_or_quark_Yukawa_fitted=False,
        complete_native=False, complete_a_mu=None,
        full_EW_two_loop_evaluated=False, action_selected=False,
        Gate7_closed=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    packet = evaluate()
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output/'bosonic_weak_log.json'
    target.write_text(json.dumps(packet, sort_keys=True, indent=2, allow_nan=False)+'\n',
                      encoding='utf8', newline='\n')
    record = _record(target) if target.is_relative_to(ROOT) else dict(
        path=str(target), bytes=target.stat().st_size,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    print(json.dumps(dict(record, value=packet['evaluated_contribution']), sort_keys=True))


if __name__ == '__main__':
    main()
