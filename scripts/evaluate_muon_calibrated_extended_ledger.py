#!/usr/bin/env python
"""Add the evaluated bosonic logarithm without changing prior receipts.

The common decay-theory sensitivity is added before its error propagation.
The partial observable remains distinct from the unfinished native response.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_component_ledger import shared_observable_uncertainty


def identity(path):
    b=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def evaluate():
    paths={
        'prior':ROOT/'artifacts/muon_calibrated_component_ledger_20261010/run_5/component_ledger.json',
        'log':ROOT/'artifacts/muon_calibrated_bosonic_weak_log_20261010/run_1/bosonic_weak_log.json',
        'weak':ROOT/'artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json',
        'inputs':ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json',
    }
    packets={k:json.loads(v.read_text(encoding='utf8')) for k,v in paths.items()}
    prior,log,weak,inputs=(packets[k] for k in ('prior','log','weak','inputs'))
    if identity(paths['prior'])['sha256']!='937843127402028a13ab8fd96df80ec63b9f54bd4e450fb34b028ffa6a29e945':
        raise ValueError('published component ledger changed')
    if log['input_uncertainty']['primitive_order']!=prior['primitive_order']:
        raise ValueError('shared input order mismatch')
    rows=prior['contribution_table']+[
        dict(component='bosonic EW2 leading logarithm, closed fermion loops excluded',
             value=log['evaluated_contribution'],owner=identity(paths['log'])['path'])]
    subtotal=math.fsum(row['value'] for row in rows)
    gradients=prior['component_gradients']+[log['input_uncertainty']['gradient']]
    mass=inputs['selected_consumer_values']['m_mu_GeV']['value']
    uncertainty={}
    for sign,name in ((1,'mu_plus'),(-1,'mu_minus')):
        uncertainty[name]={side:shared_observable_uncertainty(a_subtotal=subtotal,
            mass_GeV=mass,component_gradients=gradients,mass_gradient=prior['mass_gradient'],
            standard_uncertainties=log['input_uncertainty']['standard_uncertainties_'+side],
            charge_sign=sign) for side in ('plus','minus')}
    w=weak['local_EW_evaluated_subtotal_input_uncertainty']
    sensitivity=w['evaluated_consumer_derivatives']['GF']+log['errors']['GF_source_sensitivity']
    # Both entries consume the SAME inferred decay GF, so their signed
    # sensitivities must be summed. Adding their variances would be wrong.
    decay=dict(summed_GF_sensitivity=sensitivity,
        estimated_standard_uncertainty=abs(sensitivity)*log['errors']['GF_source_standard_uncertainty'],
        omitted_order_allowance_estimate=abs(sensitivity)*weak['decay_rematching']['omitted_order_GF_allowance_estimate'],
        GF_source_standard_uncertainty=log['errors']['GF_source_standard_uncertainty'],
        scope='common decay-theory source only; not total weak/native uncertainty')
    errors=prior['errors'].copy()
    errors['metrological_inputs']=uncertainty
    errors['weak_decay_estimated_standard_uncertainty']=decay['estimated_standard_uncertainty']
    errors['weak_decay_omitted_order_estimate']=decay['omitted_order_allowance_estimate']
    errors['bosonic_logarithm']=log['errors']
    errors['full_bosonic_finite_remainder']=None
    errors['weak_unexecuted_sectors']=dict(prior['errors']['weak_unexecuted_sectors'],
        bosonic_logarithm_now_evaluated=True,bosonic_finite_remainder=None,
        prior_whole_bosonic_reference_not_added=True,
        prior_finite_order_allowance_not_a_bound=True)
    return dict(prior,
        classification='EVALUATED_ADDITIVE_COMPONENT_LEDGER_WITH_SHARED_BOSONIC_LOG_DEPENDENCIES',
        evaluated_subtotal=subtotal,contribution_table=rows,component_gradients=gradients,
        gradient_component_order=prior['gradient_component_order']+[rows[-1]['component']],
        input_uncertainty=uncertainty,errors=errors,shared_decay_theory_propagation=decay,
        overlap_ledger=dict(prior['overlap_ledger'],
            bosonic_logarithm='no closed fermion loop; excluded from prior weak and local Higgs packets; added once'),
        input_hashes=[identity(path) for path in paths.values()],
        producer_hashes=[identity(Path(__file__))],
        status=dict(DERIVED=['signed common GF theory-source propagation'],
            EVALUATED=[r['component'] for r in rows],
            CONTROL_ONLY=['primitive independence illustration when covariance is unsupplied'],
            UNEVALUATED=['full native overlap and charge-subtracted Pauli response','finite weak remainder'],
            OWNER_DEFINITION_GAP=[]))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();packet=evaluate();args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'extended_ledger.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        bytes=target.stat().st_size,evaluated_subtotal=packet['evaluated_subtotal'],complete_observable=False),sort_keys=True))


if __name__=='__main__':main()
