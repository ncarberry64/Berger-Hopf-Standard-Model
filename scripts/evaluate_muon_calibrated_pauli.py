#!/usr/bin/env python
"""Execute calibrated local Pauli contractions and preserved action applications.

This is a partial physical calculation: local matched QED through two
loops and the fixed-Y neutral scalar diagram. It does not close the native
observable or give a complete uncertainty.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))

from bhsm.interface.muon_calibrated_matching import (
    calibrated_tree_matching, local_calibrated_higgs_radial_newton,
)
from bhsm.interface.muon_calibrated_local_pauli import (
    calibrated_local_qed_two_loop, fixed_yukawa_higgs_pauli,
    signed_soft_transfer_application, local_spin_pole_application,
)
from bhsm.interface.muon_calibrated_decay_matching import calibrated_muon_decay_one_loop


def encode(value):
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return dict(real=value.real.tolist(), imag=value.imag.tolist())
        return value.tolist()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, complex):
        return dict(real=value.real, imag=value.imag)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def write(path, value):
    path.write_text(json.dumps(encode(value), sort_keys=True, indent=2,
                              allow_nan=False)+'\n', encoding='utf8', newline='\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config_path = ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    config = json.loads(config_path.read_text(encoding='utf8'))
    values = {k: v['value'] for k, v in config['selected_consumer_values'].items()}
    primitive = config['primary_measurements']
    alpha_inverse = primitive['alpha_inverse_0']['value']
    alpha = 1/alpha_inverse
    rme = primitive['muon_electron_mass_ratio']['value']
    mmu, mtau, mh = [values[k] for k in ('m_mu_GeV', 'm_tau_GeV', 'm_h_GeV')]
    rms = mmu/mtau
    decay=calibrated_muon_decay_one_loop(alpha_0=alpha,muon_electron_ratio=rme,
        reference_decay_factor=config['fermi_matching_scope']['decay_factor_provisional'])
    matching = calibrated_tree_matching(
        fermi_constant_GeV_inverse_squared=values['G_F_GeV_minus2'],
        higgs_mass_GeV=mh,
        pole_masses_GeV=[mtau, mmu, values['m_e_GeV']],
        input_covariance=config['uncertainty_and_correlations']['illustrative_independent_primitive_consumer_covariance'])
    matching['input_covariance_scope']='Illustrative propagation from independent primitives; not the measured cross-source covariance'
    newton = local_calibrated_higgs_radial_newton(
        fermi_constant_GeV_inverse_squared=values['G_F_GeV_minus2'], higgs_mass_GeV=mh)
    qed = calibrated_local_qed_two_loop(alpha=alpha, muon_electron_ratio=rme,
                                      muon_tau_ratio=rms, eps=2e-13)
    higgs = fixed_yukawa_higgs_pauli(muon_mass_GeV=mmu, higgs_mass_GeV=mh)
    soft = [signed_soft_transfer_application(
        alpha=alpha, mass_GeV=mmu, t=t, direction=u)
        for t in (1e-3, -1e-3, 1e-4, -1e-4, 1e-5, -1e-5)
        for u in np.eye(3)]
    poles = [local_spin_pole_application(mmu, p, spin=spin)
             for p in (0., mmu/10) for spin in (-1, 1)]
    # Exact dependency chain: m_e proportional to R_infinity*alpha_inverse^2,
    # m_mu=r_mu_e*m_e. Ratios used in VP are never treated as independent masses.
    d_e, d_t = [qed[k] for k in ('derivative_log_muon_electron_ratio',
                                'derivative_log_muon_tau_ratio')]
    d_h = higgs['derivative_log_muon_mass']
    rydberg = primitive['R_infinity']['value']
    grad_qed = np.array([
        -qed['derivative_alpha']/alpha_inverse**2+2*d_t/alpha_inverse,
        d_t/rydberg, (d_e+d_t)/rme, 0., 0., -d_t/mtau])
    grad_higgs = np.array([2*d_h/alpha_inverse, d_h/rydberg, d_h/rme,
                          0., -d_h/mh, 0.])
    grad = grad_qed+grad_higgs
    std = np.asarray(config['uncertainty_and_correlations']['primitive_standard_uncertainties'])
    terms = dict(qed['contributions'])
    terms['local_fixed_Y_radial_Higgs_one_loop'] = higgs['a_mu_local_radial_Higgs_one_loop']
    partial = sum(terms.values())
    uncertainty = dict(
        primitive_order=config['uncertainty_and_correlations']['primitive_order'],
        local_QED_gradient=grad_qed, fixed_Y_Higgs_gradient=grad_higgs, combined_gradient=grad,
        illustrative_input_standard_uncertainty_assuming_independent_primitives=float(np.linalg.norm(grad*std)),
        input_standard_uncertainty_upper_over_all_primitive_correlations=float(np.sum(abs(grad)*std)),
        measured_cross_source_covariance=None,
        input_uncertainty_scope='linear input standard uncertainty only; not a probability enclosure',
        quadrature_error_estimate=qed['quadrature_error_estimate']+higgs['quadrature_error_estimate'],
        one_loop_signed_soft_bias_bounds=[s['soft_bias_bound'] for s in soft],
        exact_arithmetic_total_VP_observable_series_tail_bound=(alpha/np.pi)**2*(
            qed['electron_VP_application']['integrated_series_truncation_bound']+
            qed['tau_VP_application']['integrated_series_truncation_bound']),
        binary64_roundoff_enclosure=None,
        higher_local_QED_order_bound=None,
        complete_scalar_and_weak_matching_bound=None,
        GF_reextraction_and_BHSM_decay_correction_bound=None,
        native_remainder_and_overlap_bound=None,
        continuum_and_native_response_bound=None,
        complete_observable_uncertainty=False)
    reduction = dict(
        minimal_scalar="d/dt <L_u,[Gamma_AE4-Gamma_owned_overlap]_R(tu)> at t=0, with matched pole injections and charge division",
        charge_reduction="a=A2(0)/A1(0); a common multiplicative LSZ factor cancels, but internal response and source motion do not",
        Ward_projection="q_mu P^mu=0; the charge condition constrains A1, not transverse A2",
        native_photon_source="J_gamma=bar_gamma B_tilde r_in on the owned quotient",
        reached_native_equation="(K0_Q+zeta M0_Q) u_zeta=J_gamma",
        reached_native_contraction="l_out^dagger gamma u_zeta; differentiate with source, heat weights, completion, contacts, overlap and external-mode motion",
        resolvent_remainder_identity="A u=J; A0 u0=J; A0^dagger p=L; L^dagger(u-u0)=-p^dagger R_ind u, where A=A0+R_ind on one common quotient",
        minimal_response_application="R_ind u paired with the downstream adjoint p, and its soft/source/domain jets; not a full R_ind matrix",
        first_native_application="complete positive quotient photon form and its source-directed action on the matched current",
        retained_angular_component_scope="negative Lorentzian angular density only; not a positive proper-time operator, temporal completion or quotient",
        smallest_remaining_calculation="same-action positive sourced photon response on the matched pole current, plus its soft derivative and relative completion/overlap",
        raw_heat_cutoff_derivative="d_c[(Q_c(x)-Q_c(y))/(x-y)]=(exp(-c*y)-exp(-c*x))/(2*(x-y)); diagonal=c*exp(-c*x)/2",
        full_completion_cutoff_cancellation_established=False,
        cutoff_owner="BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08",
        cutoff="c_mu=i_mu_plus/r_mu_plus on child-plus at birth; no finite time offset",
        mass_or_lifetime_implies_cutoff=False,
        full_PF_CAR_or_history_proved_necessary=False,
        physical_underdetermination_claim=False, owner_definition_gap=False)
    identities = []
    for path in ('src/bhsm/interface/muon_calibrated_matching.py',
                 'src/bhsm/interface/muon_calibrated_local_pauli.py',
                 'src/bhsm/interface/muon_calibrated_decay_matching.py',
                 'src/bhsm/interface/muon_intrinsic_lepton_primal.py',
                 'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
                 'src/bhsm/interface/universal_lsz.py',
                 'src/bhsm/interface/universal_quadratic_spectrum.py',
                 'src/bhsm/interface/universal_precision_form_factor.py',
                 'src/bhsm/interface/muon_native_kkt_downstream.py',
                 'src/bhsm/interface/muon_native_photon_response.py',
                 'theory/muon_minimum_pauli_readout_20260930.md',
                 'artifacts/muon_calibrated_pauli_20261009/inputs.json',
                 'scripts/evaluate_muon_calibrated_pauli.py'):
        identities.append(dict(path=path, sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
    output = dict(
        classification='EVALUATED_CALIBRATED_LOCAL_PAULI_COMPONENTS_AND_LOCAL_HIGGS_SOLVE',
        base_head='914505d4f4e649be8a62bf066f01b09e01586b04',
        renormalization='local QED on-shell Thomson charge and selected poles through alpha^2; fixed-Y local neutral scalar one-loop skeleton',
        matching=matching, local_Higgs_Newton=newton,local_decay_matching_application=decay,
        local_QED=qed, local_radial_Higgs=higgs, local_poles=poles,
        signed_soft_transfer=soft, contribution_accounting=dict(
            evaluated=terms, evaluated_partial_a_mu=partial, evaluated_partial_g_mu=2*(1+partial),
            historical_frozen_local_values_added=False,
            local_QED_alpha3_and_higher=None, remaining_local_weak=None,
            disjoint_native_after_owned_overlap=None,
            strong_contributions='reserved to the unevaluated native/overlap ledger; no separate strong total added',
            full_a_mu=None, full_g_mu=None),
        uncertainty=uncertainty, native_reduction=reduction, input_identities=identities,
        muon_anomaly_used=False, independent_Yukawas_fitted=False,
        action_selected=False, Gate7_closed=False,
        interacting_birth_base_stationary=False, native_Pauli_evaluated=False,
        claim_classes=dict(
            DERIVED=['matched local Pauli tensor reduction and common LSZ/charge cancellation',
                     'fixed-Y matching constraints; exact input dependency gradients',
                     'source-directed native resolvent reduction with surviving completion and overlap'],
            EVALUATED=['local Higgs weak residual Newton solve',
                       'local spin-sector poles and descriptor normalization',
                       'signed one-loop Pauli limit; complete local QED alpha and alpha^2',
                       'fixed-Y local neutral scalar loop and matching discrepancies'],
            CONTROL_ONLY=['flat local matched reference, not an E1 stationary realization'],
            UNEVALUATED=['complete interacting pole/self-energy matching',
                         'positive native photon source application, completion and overlap',
                         'birth cutoff on the owned formation section; complete Pauli prediction and error'],
            OWNER_DEFINITION_GAP=[]))
    write(args.output/'calibrated_pauli.json', output)
    print(json.dumps(dict(
        classification=output['classification'],
        a_mu_local_QED_alpha_through_alpha2=qed['a_mu_local_QED_through_two_loops'],
        fixed_Y_Higgs_one_loop=higgs['a_mu_local_radial_Higgs_one_loop'],
        evaluated_partial_a_mu=partial, evaluated_partial_g_mu=2*(1+partial),
        local_Higgs_Newton_converged=newton['converged'],
        input_only_std=uncertainty['illustrative_input_standard_uncertainty_assuming_independent_primitives'],
        native_evaluated=False, full_a_mu=None, full_g_mu=None), sort_keys=True))


if __name__ == '__main__':
    main()
