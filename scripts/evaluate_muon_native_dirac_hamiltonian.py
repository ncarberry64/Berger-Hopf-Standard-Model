#!/usr/bin/env python
"""Replay actual E1 geometric/current coefficients, without selecting H/gauge."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_native_dirac_hamiltonian import (
    canonical_product_factor_contract, lepton_current_hilbert_representation,
    retained_e1_source_vertices,
)

CONFIG = 'artifacts/muon_calibrated_pauli_20261009/inputs.json'
CONFIG_SHA = '0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da'


def record(relative, symbols=()):
    raw = (ROOT/relative).read_bytes()
    result = dict(path=relative, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    if symbols:
        nodes = {n.name: n for n in ast.parse(raw).body
                 if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        result['symbols'] = {name: dict(line=nodes[name].lineno, end_line=nodes[name].end_lineno)
                             for name in symbols}
    return result


def serial(value):
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return dict(shape=list(value.shape), real=value.real.tolist(), imag=value.imag.tolist())
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def evaluate():
    config_record = record(CONFIG)
    if config_record['sha256'] != CONFIG_SHA:
        raise ValueError('frozen selected alpha input changed')
    config = json.loads((ROOT/CONFIG).read_bytes())
    alpha_inverse = config['primary_measurements']['alpha_inverse_0']['value']
    e = float(np.sqrt(4*np.pi/alpha_inverse))
    vertices = retained_e1_source_vertices(e, ROOT)
    rep = lepton_current_hilbert_representation()
    xi = vertices['photon_vertices']
    contacts = vertices['photon_source_square_contacts']
    checks = dict(
        spatial_photon_vertex_Frobenius_norms=[float(np.linalg.norm(x)) for x in xi[1:]],
        spatial_full18_contact_traces=[float(np.trace(x).real) for x in contacts[range(1,4),range(1,4)]],
        spatial_charged_spin4_contact_trace=float(np.trace(contacts[1,1][np.ix_([6,7,12,13],[6,7,12,13])]).real),
        contact_Hermitian_residual=float(np.max(abs(contacts-contacts.conj().transpose(0,1,3,2)))),
        source_Hermitian_residual=float(np.max(abs(xi-xi.conj().transpose(0,2,1)))),
        neutral_photon_vertex_residual=float(np.max(abs(xi[:,:6]))),
        nonzero_retained_H4=float(vertices['geometry']['H4']),
    )
    owners = [
        ('src/bhsm/interface/muon_native_dirac_hamiltonian.py', (
            'lepton_current_hilbert_representation', 'fixed_y_higgs_hamiltonian',
            'canonical_lepton_hamiltonian_maps', 'electromagnetic_hamiltonian_source_maps',
            'canonical_product_factor_contract', 'product_factor_form_jets', 'retained_e1_source_vertices')),
        ('src/bhsm/interface/muon_intrinsic_lepton_primal.py', (
            'intrinsic_round_dirac_coefficients', 'retained_e1_lepton_geometry_coefficients', '_euler')),
        ('src/bhsm/interface/muon_intrinsic_higgs_weak_action.py', ('retained_higgs_spin_charge_representation',)),
        ('src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py', ('charged_lepton_yukawa_operator',)),
        ('src/bhsm/interface/ae4_current_c2_factorized_hs_calderon.py', ('_product_dirac_map', 'factorized_product_dirac_hs_weyl_jet')),
        ('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py', ('forward_time_domain_contract', 'microscopic_owner_contract')),
        ('scripts/evaluate_muon_native_dirac_hamiltonian.py', ('evaluate',)),
    ]
    result = dict(
        classification='EVALUATED_RETAINED_E1_GEOMETRIC_CURRENT_AND_FIXED_Y_OPERATOR_COEFFICIENTS',
        selected_electromagnetic_coupling=e, alpha_inverse_0=alpha_inverse,
        source_records=[config_record]+[record(path, names) for path, names in owners],
        represented_point_fiber=rep, actual_E1_operator_vertices=vertices,
        factor_and_native_scope=canonical_product_factor_contract(), numerical_checks=checks,
        H_or_gauge_background_selected=False,
        source_basis_is_physical_photon_mode=False,
        complete_native_heat_or_Pauli_value_evaluated=False,
        full_native_remainder_bound_established=False,
        next_application='Attach source-paired initial/reset/child/exterior factor graphs and total domain jets to the same coupled field maps.',
    )
    return serial(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    packet = evaluate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(packet, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()
    args.output.write_bytes(raw)
    print(json.dumps(dict(path=str(args.output), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                          checks=packet['numerical_checks']), sort_keys=True))


if __name__ == '__main__':
    main()
