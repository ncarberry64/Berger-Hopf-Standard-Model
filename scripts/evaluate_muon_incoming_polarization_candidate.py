"""Materialize a conditional incoming selector control, never collider admission."""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT)]
from bhsm.interface.muon_incoming_polarization_candidate import execute_boundary_transport_control
from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from audits.bhsm_collider_incoming_field_current import (
    PAIR_PACKET_SHA256, apply_incoming_packet_current, construct_action_packet_sections,
    current_algebra, original_material_Gauss_source,
)


def exact_saved_pair():
    folder = ROOT/'artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation'
    path = folder/'actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz'
    if sha256(path.read_bytes()).hexdigest() != PAIR_PACKET_SHA256:
        raise ValueError('unchanged exact pair input required')
    with np.load(path, allow_pickle=False) as data:
        rho = data['pair_Fock_density16'].copy()
    spec = importlib.util.spec_from_file_location('retained_pair', folder/'executed_producer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return rho, module.annihilators(4)


def complex_record(array):
    return dict(real=np.asarray(array).real.tolist(), imag=np.asarray(array).imag.tolist())


def execute(output):
    if output.exists():
        raise ValueError('new checkpoint directory required; reuse saved completed output')
    result, packet = execute_boundary_transport_control()
    rho, ops = exact_saved_pair()
    cases = ('transported', 'instantaneous')
    u, v, synthesis = [], [], {}
    for name in cases:
        c = packet[name+'_coefficients']
        sections = construct_action_packet_sections(value_map=packet['value_map'],
            spatial_derivative_map=np.zeros((1, 3, 18, 4)), H=packet['H'], R4=1.,
            gauge_connection=np.zeros((1, 4, 18, 18)), particle_coefficients=c[:, :2],
            antiparticle_coefficients=c[:, 2:], Cauchy_quadrature=packet['Cauchy_quadrature'])
        u.append(sections['particle_modes'][0]); v.append(sections['antiparticle_modes'][0])
        synthesis[name] = sections['Cauchy_Gram_application']
    vertices = canonical_open_field_vertices(1., 1.)
    full = np.concatenate((vertices['gauge'].reshape(20, 18, 18), vertices['scalar']))
    metadata = {k: 'UNADOPTED_HOMOGENEOUS_ORIGINAL_ACTION_CONTROL_NOT_COLLIDER_PACKET'
                for k in ('action_owner', 'background_owner', 'Cauchy_domain_owner',
                          'particle_mode_owner', 'antiparticle_mode_owner', 'vertex_owner')}
    metadata['benchmark_id'] = 'BHSM_NEW_COLLIDER_ELECTRON_POSITRON_TO_MUON_ANTIMUON_V1'
    current = apply_incoming_packet_current(particle_modes=np.array(u), antiparticle_modes=np.array(v),
        canonical_Hamiltonian_vertices=np.broadcast_to(full, (2, 24, 18, 18)),
        pair_density=rho, annihilators=ops, metadata=metadata)
    material = original_material_Gauss_source(particle_modes=np.array(u), antiparticle_modes=np.array(v),
        canonical_spatial_density=np.ones(2), pair_density=rho, annihilators=ops,
        normalization_owner='chi=R4^(3/2)psi, Haar dOmega; constant sections normalized by sqrt(2*pi^2); trial only')
    algebra = current_algebra(ops, rho)
    bilinears = algebra['bilinear_difference_operators4x4x16x16']
    compressed = current['compressed_packet_vertices']
    fock_currents = np.einsum('paij,ijuv->pauv', compressed, bilinears)
    direct = np.array([[[np.trace(rho@a@b) for b in row] for a in row] for row in fock_currents])
    current_defect = float(np.max(abs(direct-current['ordered_Hamiltonian_vertex_product'])))
    result['residuals']['all_24_by_24_ordered_currents_vs_direct_exact_Fock_trace'] = current_defect
    result['Cauchy_synthesis'] = synthesis
    source = material['lepton_material_At_action_source_density']
    result['trial_application'] = dict(
        cases=list(cases), time=packet['time'],
        sections=complex_record(np.concatenate((u, v), axis=2)),
        mean_24_original_Hamiltonian_vertices=complex_record(current['Hamiltonian_vertex_expectation']),
        ordered_24_by_24_original_vertices=complex_record(current['ordered_Hamiltonian_vertex_product']),
        material_At_source_density=source.tolist(),
        material_At_constant_test_Haar_load=(source*packet['Cauchy_quadrature'][0]).tolist(),
        transported_vs_instantaneous_mean_current_max=float(np.max(abs(np.diff(current['Hamiltonian_vertex_expectation'], axis=0)))),
        original_local_Gauss_subtotal_nonpass=float(np.max(abs(source))),
        Gauss_scope='Declared trial has zero classical gauge curvature and a spatially uniform real Higgs amplitude, hence zero classical Higgs temporal charge. The evaluated finite-pair lepton load is a nonzero Gauss subtotal. Native/reference/interface contributions and full physical constraints are not evaluated or set to zero.',
        exact_pair_trace=float(np.trace(rho).real), exact_pair_purity=float(np.trace(rho@rho).real),
        ordered_products_retained=True, occupation_fitted=False,
        source_consumer_repair='Distinct channel and spin indices in ordered-current einsum; previous expression failed for 24 channels.')
    inputs = [
        'src/bhsm/interface/muon_incoming_polarization_candidate.py',
        'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
        'src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',
        'src/bhsm/interface/muon_native_product_factor_graph.py',
        'src/bhsm/interface/muon_intrinsic_higgs_weak_action.py',
        'audits/bhsm_collider_incoming_field_current.py',
        'scripts/evaluate_muon_incoming_polarization_candidate.py',
        'theory/bhsm_operator_reference_construction_20261016.md',
        'theory/muon_ideal_preparation_action_derivation_20261016.md',
        'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json',
        'artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/executed_producer.py',
        'artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz',
    ]
    result['input_sha256'] = {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    output.mkdir(parents=True)
    path = output/'result.json'
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf-8', newline='\n')
    temporary.replace(path)
    print(json.dumps(dict(output=str(path), sha256=sha256(path.read_bytes()).hexdigest(),
                         residuals=result['residuals'], Gauss_subtotal=result['trial_application']['original_local_Gauss_subtotal_nonpass'],
                         physical_incoming_realization=False), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    execute(parser.parse_args().output.resolve())
