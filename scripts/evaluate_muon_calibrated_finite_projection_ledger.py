#!/usr/bin/env python
"""Add the evaluated finite transverse W/Hgamma row to the published ledger."""
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


def identity(p):
    b=p.read_bytes()
    return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def evaluate():
    paths={
        'prior':ROOT/'artifacts/muon_calibrated_extended_ledger_20261010/run_1/extended_ledger.json',
        'projection':ROOT/'artifacts/muon_calibrated_bosonic_higgs_photon_20261010/run_1/bosonic_higgs_photon.json',
        'weak':ROOT/'artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json',
        'inputs':ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'}
    p={k:json.loads(v.read_text(encoding='utf8')) for k,v in paths.items()}
    prior,projection,weak,inputs=(p[k] for k in ('prior','projection','weak','inputs'))
    if identity(paths['prior'])['sha256']!='9aa5b2d31e9087cbd70fa6d1c71702be38c40ff53f3c2b86961c1ce3c01f3726':
        raise ValueError('published additive ledger changed')
    if prior['primitive_order']!=projection['input_uncertainty']['primitive_order']:
        raise ValueError('common input order mismatch')
    rows=prior['contribution_table']+[dict(component='finite transverse W/Hgamma projection with fixed Y_mu',
        value=projection['evaluated_contribution'],owner=identity(paths['projection'])['path'])]
    subtotal=math.fsum(row['value'] for row in rows)
    gradients=prior['component_gradients']+[projection['input_uncertainty']['gradient']]
    uncertainty={}
    mass=inputs['selected_consumer_values']['m_mu_GeV']['value']
    for sign,name in ((1,'mu_plus'),(-1,'mu_minus')):
        uncertainty[name]={side:shared_observable_uncertainty(a_subtotal=subtotal,mass_GeV=mass,
            component_gradients=gradients,mass_gradient=prior['mass_gradient'],charge_sign=sign,
            standard_uncertainties=projection['input_uncertainty']['standard_uncertainties_'+side])
            for side in ('plus','minus')}
    sensitivity=prior['shared_decay_theory_propagation']['summed_GF_sensitivity']+projection['errors']['GF_source_sensitivity']
    decay=dict(summed_GF_sensitivity=sensitivity,
        GF_source_standard_uncertainty=prior['shared_decay_theory_propagation']['GF_source_standard_uncertainty'],
        estimated_standard_uncertainty=abs(sensitivity)*prior['shared_decay_theory_propagation']['GF_source_standard_uncertainty'],
        omitted_order_allowance_estimate=abs(sensitivity)*weak['decay_rematching']['omitted_order_GF_allowance_estimate'],
        scope='common signed weak sensitivity times the SAME decay theory source')
    errors=dict(prior['errors'],metrological_inputs=uncertainty,
        finite_transverse_W_Hgamma=projection['errors'],
        weak_decay_estimated_standard_uncertainty=decay['estimated_standard_uncertainty'],
        weak_decay_omitted_order_estimate=decay['omitted_order_allowance_estimate'])
    return dict(prior,classification='EVALUATED_ADDITIVE_FINITE_TRANSVERSE_W_HGAMMA_LEDGER',
        evaluated_subtotal=subtotal,contribution_table=rows,component_gradients=gradients,
        gradient_component_order=prior['gradient_component_order']+[rows[-1]['component']],
        input_uncertainty=uncertainty,errors=errors,shared_decay_theory_propagation=decay,
        overlap_ledger=dict(prior['overlap_ledger'],
            finite_transverse_W_Hgamma='no external-mass logarithm; distinct from bosonic LL and closed-lepton Hgamma; no full finite bosonic sum added'),
        input_hashes=[identity(v) for v in paths.values()],producer_hashes=[identity(Path(__file__))],
        status=dict(DERIVED=['same signed common GF source propagation and fixed-Y mass tangent'],
            EVALUATED=[r['component'] for r in rows],
            CONTROL_ONLY=['primitive-independence covariance illustration'],
            UNEVALUATED=['non-Barr-Zee/HZ/counterterm finite bosonic completion','full native overlap and Pauli remainder'],
            OWNER_DEFINITION_GAP=[]))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier evidence; select a fresh output directory')
    packet=evaluate();args.output.mkdir(parents=True)
    target=args.output/'finite_projection_ledger.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        bytes=target.stat().st_size,evaluated_subtotal=packet['evaluated_subtotal'],complete_observable=False),sort_keys=True))


if __name__=='__main__':main()
