#!/usr/bin/env python
"""Consume the closed finite-order sectors with common metrological inputs.

This is contribution accounting during the coupled native calculation.
No uncomputed parent term is assigned zero or a finite error allowance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_component_ledger import (
    shared_observable_uncertainty,leading_top_electromagnetic_vp,
)


def identity(path):
    b=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def evaluate():
    paths={
        'inputs':ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json',
        'baseline':ROOT/'artifacts/muon_calibrated_pauli_20261009/run_1/calibrated_pauli.json',
        'higher_QED':ROOT/'artifacts/muon_calibrated_higher_qed_20261010/run_1/higher_qed.json',
        'weak':ROOT/'artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json',
        'hadronic':ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/hadronic_ledger_run_1/physical_hadronic_ledger.json',
    }
    p={k:json.loads(v.read_text(encoding='utf8')) for k,v in paths.items()}
    config,baseline,qed,weak,had=(p[k] for k in ('inputs','baseline','higher_QED','weak','hadronic'))
    if identity(paths['inputs'])['sha256']!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('retained calibration input changed')
    if identity(paths['baseline'])['sha256']!='20a4b5a169439f2db2ff8d37c9746bb7a43c6887a266d6c3e5262d8500fad419':
        raise ValueError('retained partial calculation changed')
    primitive=config['uncertainty_and_correlations']['primitive_order']
    if baseline['uncertainty']['primitive_order']!=primitive or qed['input_uncertainty']['primitive_order']!=primitive:
        raise ValueError('shared primitive order mismatch')
    if had['gradient_order']!=primitive:
        raise ValueError('hadronic metrological derivative order mismatch')
    external=weak['local_EW_evaluated_subtotal_input_uncertainty']
    if external['primitive_order'][:6]!=primitive:
        raise ValueError('weak shared primitive order mismatch')
    mass=config['selected_consumer_values']['m_mu_GeV']['value']
    mass_row=np.r_[config['uncertainty_and_correlations']['consumer_vs_primitive_jacobian'][3],[0.]*3]
    alpha=config['alpha_consumer']['value']
    top_mass=weak['additional_weak_measurements']['top_pole']['mass_GeV']
    top=leading_top_electromagnetic_vp(alpha=alpha,muon_mass_GeV=mass,top_pole_mass_GeV=top_mass)
    # The newly rematched weak packet replaces the provisional leading-EW
    # and Hgamma/HZ entries of current_response's historical LO receipt.
    rows=[
        dict(component='retained local QED alpha1,alpha2 and literal fixed-Y H1',
             value=baseline['contribution_accounting']['evaluated_partial_a_mu'],
             owner=identity(paths['baseline'])['path'],reused=True),
        dict(component='local leptonic QED alpha3-alpha5',value=qed['qed']['increment'],
             owner=identity(paths['higher_QED'])['path']),
        dict(component='rematched leading EW, fermionic-rest, VVA and fixed-Y lepton Hgamma/HZ',
             value=weak['local_EW_evaluated_sector_subtotal'],owner=identity(paths['weak'])['path']),
        dict(component='hadronic two-current LO,NLO,NNLO',value=had['HVP_subtotal'],
             owner=identity(paths['hadronic'])['path']),
        dict(component='published connected hadronic four-current projection',
             value=had['HLbL_projection'],owner=identity(paths['hadronic'])['path'],
             evaluated_at_source_metrology=True),
        dict(component='lowest electromagnetic top two-current VP',value=top['value'],
             owner='literal normalized Dirac-vector current, color-charge factor4/3; independently measured top pole mass',
             five_flavor_data_overlap=0.),
    ]
    subtotal=math.fsum(row['value'] for row in rows)
    gradients=[np.r_[baseline['uncertainty']['combined_gradient'],[0.]*3],
               np.r_[qed['input_uncertainty']['gradient'],[0.]*3],
               np.asarray(external['gradient']),
               np.r_[had['selected_input_gradient'],[0.]*3]]
    top_row=top['derivative_muon_mass']*mass_row
    top_row[0]-=top['derivative_alpha']*alpha**2
    top_row[-1]+=top['derivative_top_mass']
    gradients.append(top_row)
    uncertainty={}
    for sign,name in ((1,'mu_plus'),(-1,'mu_minus')):
        uncertainty[name]={}
        for side in ('plus','minus'):
            uncertainty[name][side]=shared_observable_uncertainty(a_subtotal=subtotal,
                mass_GeV=mass,component_gradients=gradients,mass_gradient=mass_row,
                standard_uncertainties=external['standard_uncertainties_'+side],charge_sign=sign)
    errors=dict(metrological_inputs=uncertainty,
        QED_coefficients_and_truncation=qed['qed']['errors'],
        hadronic=had['errors'],
        hadronic_metrology_derivative_scope=had['metrology_derivative_scope'],
        top_current=top,
        weak_source_uncertainty_and_mass_approximation=weak['VVA_current_sectors'],
        weak_unexecuted_sectors=weak['remaining_weak_sectors'],
        weak_decay_estimated_standard_uncertainty=external['decay_theory_estimated_standard_uncertainty'],
        weak_decay_omitted_order_estimate=external['decay_omitted_order_allowance_estimate'],
        gamma_Z_correlator_standard_uncertainty=abs(external['gamma_Z_correlator_derivative'])*.1,
        parent_native_error_allowance=None,complete_observable_uncertainty=None)
    return dict(classification='EVALUATED_FINITE_ORDER_COMPONENT_LEDGER_WITH_SHARED_METROLOGY',
        contribution_table=rows,evaluated_subtotal=subtotal,
        approximation_order='local leptonic QED through alpha5; hadronic VP through alpha4; published connected HLbL alpha3; explicitly evaluated local EW sectors only',
        overlap_ledger=dict(
            preserved_QED12_vs_new_QED345='disjoint perturbative orders',
            hadronic_vs_leptonic_QED='disjoint electromagnetic current flavor content',
            HVP_vs_HLbL='two-current insertions versus connected four-current; exclusive/OPE light poles removed once in published HLbL',
            HVP_internal_radiation='inclusive source radiation not added again as class4d',
            weak='provisional old leading EW and lepton Hgamma/HZ replaced by rematched packet; not added twice',
            complete_common_action_native_overlap=None),
        input_uncertainty=uncertainty,errors=errors,
        primitive_order=external['primitive_order'],component_gradients=[g.tolist() for g in gradients],
        gradient_component_order=[rows[i]['component'] for i in (0,1,2,3,5)],
        HLbL_exact_selected_input_gradient=None,
        HLbL_omitted_gradient_is_not_zero=True,
        mass_gradient=mass_row.tolist(),
        native_application_in_progress='full-Q same-action parent Euler/constraint and event boundary application on the singular birth germ, followed by the charge-subtracted DtN/native Pauli contraction',
        remaining_parent_term_order_and_size_established=False,
        strong_sectors_counted_once=True,measured_anomaly_used=False,
        complete_native_response=False,complete_observable=False,
        action_selected=False,Gate7_closed=False,
        input_hashes=[identity(path) for path in paths.values()],
        producer_hashes=[identity(ROOT/'src/bhsm/interface/muon_calibrated_component_ledger.py'),identity(Path(__file__))],
        status=dict(DERIVED=['shared anomaly/mass SI-moment tangent and covariance propagation'],
            EVALUATED=[r['component'] for r in rows],
            CONTROL_ONLY=['independence illustration for unprovided primitive cross-source covariance'],
            UNEVALUATED=['full native parent/interface contraction and its overlap; unevaluated weak sectors'],
            OWNER_DEFINITION_GAP=[]))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();packet=evaluate();args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'component_ledger.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        bytes=target.stat().st_size,evaluated_subtotal=packet['evaluated_subtotal'],complete_observable=False),sort_keys=True))


if __name__=='__main__':main()
