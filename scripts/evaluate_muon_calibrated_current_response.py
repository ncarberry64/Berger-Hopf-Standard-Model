#!/usr/bin/env python
"""Execute the calibrated hadronic-current photon response and Pauli return."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_current_response import (
    transverse_current_response,spectral_soft_pauli_application,magnetic_moment_accounting,
    paired_two_current_pauli,
)
from bhsm.interface.muon_calibrated_hvp_spectral import (
    load_alphaqed26_spectrum,delta_alpha_had_spacelike_jet,leading_hvp_pauli,
    delta_alpha_had_spacelike,
)


def digest(path):
    b=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def serial(value):
    if isinstance(value,complex):return dict(real=value.real,imag=value.imag)
    if isinstance(value,np.ndarray):return serial(value.tolist())
    if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serial(v) for v in value]
    if isinstance(value,np.generic):return serial(value.item())
    return value


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--spectral-input',type=Path,default=ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input')
    args=parser.parse_args()
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    baseline_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/run_1/calibrated_pauli.json'
    higher_path=ROOT/'artifacts/muon_calibrated_higher_qed_20261010/run_1/higher_qed.json'
    config=json.loads(config_path.read_text());higher=json.loads(higher_path.read_text())
    if digest(config_path)['sha256']!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('Retained calibrated input changed')
    alpha=config['alpha_consumer']['value'];mass=config['selected_consumer_values']['m_mu_GeV']['value']
    spectrum=load_alphaqed26_spectrum(args.spectral_input)
    spectral=leading_hvp_pauli(spectrum,alpha,mass)
    paired=paired_two_current_pauli(spectrum,alpha=alpha,muon_mass_GeV=mass,
        electron_mass_GeV=config['selected_consumer_values']['m_e_GeV']['value'])
    rows=[]
    for Q in (.001,.01,.1,1.,10.):
        jet=delta_alpha_had_spacelike_jet(spectrum,Q,alpha)
        r=transverse_current_response(Q,tuple(jet[k]['value'] for k in ('value','first','second')))
        rows.append(dict(Q_squared_GeV2=Q,spectral_jet=jet,application=r))
    # Execute the actual source-return in spacelike momentum, independently
    # of the timelike scalar integration. The charge-normalized one-insertion
    # response Q^2 * L^dagger(u-u0)|LO equals Delta_alpha(-Q^2).
    spacelike=[]
    for order in (32,64,128):
        z,w=leggauss(order);x=(z+1)/2;w=w/2;returns=[];max_residual=0.;max_unscaled=0.
        for xi in x:
            Q=mass*mass*xi*xi/(1-xi)
            d=delta_alpha_had_spacelike(spectrum,Q,alpha)['value']
            r=transverse_current_response(Q,(d,0.,0.))
            returns.append(r['first_insertion_dimensionless_return'].real)
            max_residual=max(max_residual,r['primal_residual'],r['full_adjoint_residual'],r['dimensionless_return_identity_residual'])
            max_unscaled=max(max_unscaled,r['return_identity_residual'])
        value=alpha/math.pi*float(np.dot(w*(1-x),returns))
        spacelike.append(dict(order=order,value=value,timelike_difference=abs(value-spectral['value']),
            maximum_action_residual=max_residual,
            maximum_unscaled_return_identity_roundoff_GeV_inverse_squared=max_unscaled,
            derivative_scope='Q^2 derivatives unused at these scalar quadrature points; physical sampled jets recorded separately'))
    soft=[]
    for t,k in ((-.01,96),(.01,96),(.003,64),(.003,96),(.003,128)):
        row=spectral_soft_pauli_application(spectrum,alpha=alpha,mass_GeV=mass,t=t,
            direction=(0.,0.,1.),kernel_order=k)
        row['kernel_quadrature_order']=k
        soft.append(row)
    ledger=[dict(name='retained local QED alpha/alpha2 and fixed-Y H1',value=.0011655419088320725,
                 owner='muon_calibrated_pauli_20261009',reused=True),
            dict(name='new local leptonic QED alpha3 through alpha5',value=higher['qed']['increment']),
            dict(name='leading local weak',value=higher['leading_EW']['a_mu_leading_EW']),
            dict(name='fixed-Y lepton Hgamma2',value=higher['fixed_Y_charged_lepton_Hgamma_two_loop']['a_mu_Hgamma_charged_leptons']),
            dict(name='fixed-Y lepton HZ2',value=higher['fixed_Y_charged_lepton_HZ_two_loop']['a_mu_HZ_charged_leptons']),
            dict(name='native hadronic two-current LO',value=spectral['value'],
                 overlap_with_retained_local=0.,overlap_zero_provenance='disjoint current flavor and diagram sectors; local subtotal has leptonic VP and one-loop radial H only')]
    subtotal=math.fsum(row['value'] for row in ledger)
    packet=dict(classification='EVALUATED_CALIBRATED_HADRONIC_TWO_CURRENT_NATIVE_PAULI_SECTOR',
        domain='on-shell matched local Minkowski charged-lepton/photon EFT, spacelike transverse current, R_bare standard-ee five-flavor source',
        pairing='one unit transverse polarization in canonical physical-current normalization',
        physical_normalization=dict(R_bare='12*pi*Im(Pi)',j='sum Q_f qbar gamma q; e excluded',
            alpha='independent Rb Thomson alpha',mass='optical/spectroscopic pole matching',
            Delta_alpha='alpha*Q^2/(3*pi) integral R(s)/(s*(s+Q^2)) ds',
            F2_LO='(alpha/pi)^2/3 integral K(s)*R(s)/s ds'),
        source_adjoint_applications=rows,spacelike_return_convergence=spacelike,
        spectral_Pauli=spectral,signed_soft_transfer_applications=soft,
        paired_electron_muon_two_current_Pauli=paired,
        contribution_ledger=ledger,
        evaluated_components_subtotal=subtotal,
        subtotal_observable_arithmetic=magnetic_moment_accounting(a_mu=subtotal,mass_GeV=mass,charge_sign=1),
        subtotal_arithmetic_scope='accounted components only; not the complete a_mu, g_mu or magnetic moment',
        uncertainty=dict(spectral_source_standard_uncertainty=spectral['spectral_error'],
            spacelike_quadrature_convergence=abs(spacelike[-1]['value']-spacelike[-2]['value']),
            independent_spacelike_timelike_difference=spacelike[-1]['timelike_difference'],
            finite_transfer_kernel_convergence=abs(soft[-1]['F2_finite']-soft[-2]['F2_finite']),
            soft_bias_bound=soft[-1]['soft_bias_bound'],
            all_native_or_observable_enclosure=None,all_errors_accounted=False),
        remaining_execution_queue=['higher hadronic VP and four-current light-by-light',
            'weak/pole matching beyond the evaluated local terms',
            'charge-subtracted parent DtN and remaining common-action native kernel'],
        sources=dict(dispersion='https://arxiv.org/abs/2112.05704',
            spectral_release='https://people.physik.hu-berlin.de/~fjeger/software.html'),
        hashes=[digest(p) for p in [config_path,baseline_path,higher_path,
            ROOT/'src/bhsm/interface/muon_calibrated_current_response.py',
            ROOT/'src/bhsm/interface/muon_calibrated_hvp_spectral.py',Path(__file__)]]+
            [digest(p) for p in sorted(args.spectral_input.glob('*')) if p.is_file()],
        measured_anomaly_used=False,action_selected=False,Gate7_closed=False,
        complete_native_response=False,complete_observable=False,
        status=dict(DERIVED=['spectral current normalization, source/adjoint identity, finite-transfer massive-photon Pauli kernel and soft bound'],
            EVALUATED=['five-flavor two-current spectral form, primal/adjoints, Pauli scalar and signed projection'],
            CONTROL_ONLY=['polynomial operator-identity unit test'],
            UNEVALUATED=['remaining queued contributions'],OWNER_DEFINITION_GAP=[]))
    args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'current_response.json'
    target.write_text(json.dumps(serial(packet),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        bytes=target.stat().st_size,hadronic_current_Pauli=spectral['value'],
        evaluated_subtotal=subtotal,complete_observable=False),sort_keys=True))


if __name__=='__main__':main()
