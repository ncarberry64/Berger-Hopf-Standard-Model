#!/usr/bin/env python
"""Replay the actual eight-Q graph and source-paired finite-core heat."""
from __future__ import annotations
import argparse
import ast
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_native_product_factor_graph import (
    finite_family_eight_q_source_pairing, finite_eight_q_heat_core,
    finite_eight_q_heat_application, finite_eight_q_cutoff_heat_application,
)

BASE='artifacts/muon_parent_gauge_geometry_correction_20261010/material_wall_mean_run_1/'
PINNED={BASE+'result.json':'3137302eb7b92d7c6b5f999095e82f84f55996ed20b2a47ec35a56c96495539c',
        BASE+'application.npz':'4a16d56ec64eeb6c2db10000debf9695f24f7bef634e793011066ed88f8b9383',
        'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz':
        '146435df28178967c321c0aa7e89a1511395d196f96b8715532aa98e3e312c2b'}


def record(path,symbols=()):
    raw=(ROOT/path).read_bytes()
    out=dict(path=path,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    if symbols:
        nodes={n.name:n for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        out['symbols']={name:dict(line=nodes[name].lineno,end_line=nodes[name].end_lineno) for name in symbols}
    return out


def serial(value):
    if isinstance(value,np.ndarray):
        if np.iscomplexobj(value):
            return dict(shape=list(value.shape),real=value.real.tolist(),imag=value.imag.tolist())
        return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [serial(v) for v in value]
    return value


def array_record(array):
    a=np.ascontiguousarray(array)
    return dict(shape=list(a.shape),dtype=str(a.dtype),raw_sha256=hashlib.sha256(a.tobytes()).hexdigest())


def deterministic_npz(arrays):
    stream=BytesIO()
    with ZipFile(stream,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,value in sorted(arrays.items()):
            item=BytesIO();np.save(item,np.asarray(value),allow_pickle=False)
            info=ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=0o600<<16
            archive.writestr(info,item.getvalue(),compress_type=ZIP_DEFLATED,compresslevel=9)
    return stream.getvalue()


def matrix_summary(matrix):
    return dict(Frobenius_norm=float(np.linalg.norm(matrix)),
        real_trace=float(np.trace(matrix).real),imaginary_trace=float(np.trace(matrix).imag),
        real_matrix=matrix.real,imaginary_matrix=matrix.imag)


def evaluate():
    inputs=[record(path) for path in PINNED]
    for item in inputs:
        if item['sha256']!=PINNED[item['path']]:raise ValueError('frozen consumed input changed: '+item['path'])
    with np.load(ROOT/(BASE+'application.npz'),allow_pickle=False) as data:
        coefficients=data['updated_coefficients']
    rep=correction_representation(time_points=8,radial_points=48,cap_points=48,
        radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    reference=retained_state(ROOT)
    common=dict(coefficients=coefficients,representation=rep,reference=reference,
                quadrature_order=4,repository=ROOT)
    nodes=np.linspace(-rep['length'],0,5)
    graph=finite_family_eight_q_source_pairing(**common,time_nodes=nodes,
        negative_spectral_parameter=-1,source_beta_nodes=np.ones((5,8)))
    arrays=dict(raw_beta_source_image_unit_radius=graph['source']['unit_radius_source_image'],
        raw_Q_coefficients=graph['source']['angular']['source_coefficients'],
        graph_source_square_contact=graph['source_square_contact'],
        graph_ordered_two_insertion=graph['ordered_two_insertion'],
        graph_opposite_order_two_insertion=graph['opposite_order_two_insertion'],
        graph_paired_mixed=graph['source_paired_graph_mixed'],
        n0_two_endpoint_graph=graph['n0_two_endpoint_graph'],n0_Poisson_map=graph['n0_Poisson_map'])
    graph_rows={}
    for n,data in graph['shell_applications'].items():
        graph_rows[n]={k:v for k,v in data.items() if not isinstance(v,np.ndarray)}
        graph_rows[n]['complementary_application_identity']=array_record(data['complementary_Poisson_application'])
    graph_trace=lambda x:np.trace(x,axis1=-2,axis2=-1)
    graph_summary=dict(core_nodes=nodes,negative_axis_probe=-1,
        full_source_action_space_dimension=378,complete_n0_constant_angular_fiber_dimension=18,
        shell_applications=graph_rows,
        source_square_contact_channel_trace=matrix_summary(graph_trace(graph['source_square_contact'])),
        first_ordered_response_channel_trace=matrix_summary(graph_trace(graph['ordered_two_insertion'])),
        second_ordered_response_channel_trace=matrix_summary(graph_trace(graph['opposite_order_two_insertion'])),
        contact_minus_both_channel_trace=matrix_summary(graph_trace(graph['source_paired_graph_mixed'])),
        graph_signs='source_square_contact minus first_ordered_response minus second_ordered_response',
        higher_n_source_directed_core_remainder=graph['higher_n_source_directed_core_remainder'],
        higher_n_remainder_proof=graph['higher_n_remainder_proof'])
    mesh_counts=(5,9,17)
    cores={count:finite_eight_q_heat_core(**common,time_nodes=np.linspace(-rep['length'],0,count),
        source_beta_nodes=np.ones((count,8)),family_indices=(1,2)) for count in mesh_counts}
    gap=float(min(f['n0_eigenvalues'][0] for f in cores[17]['families'].values()))
    probes=[dict(scaled_parameter=q,proper_time_or_cutoff=q/gap) for q in (.25,1.,4.)]
    mesh_rows={};value_map={}
    for count,core in cores.items():
        spectra={}
        for f,data in core['families'].items():
            spectra[f]=dict(inherited_family=data['inherited_family'],fixed_Y=data['fixed_Y'],
                n0_spectral_minimum=float(data['n0_eigenvalues'][0]),
                n0_spectral_maximum=float(data['n0_eigenvalues'][-1]),
                n0_mode_count=len(data['n0_eigenvalues']),
                generalized_eigen_residual_relative=data['generalized_eigen_residual_relative'],
                positive_Gram_orthogonality_residual=data['positive_Gram_orthogonality_residual'],
                intermediate_shells={n:{k:v for k,v in s.items() if not isinstance(v,np.ndarray)}|
                    dict(spectral_minimum=float(s['eigenvalues'][0]),spectral_maximum=float(s['eigenvalues'][-1]),
                         mode_count=len(s['eigenvalues'])) for n,s in data['intermediate_shells'].items()})
            arrays[f'mesh_{count}_family_{f}_n0_eigenvalues']=data['n0_eigenvalues']
            for n,shell in data['intermediate_shells'].items():
                arrays[f'mesh_{count}_family_{f}_n{n}_eigenvalues']=shell['eigenvalues']
        results=[]
        for probe in probes:
            p=probe['proper_time_or_cutoff']
            heat=finite_eight_q_heat_application(core,p)
            integrated=finite_eight_q_cutoff_heat_application(core,p)
            value_map[(count,probe['scaled_parameter'])]=integrated
            results.append(dict(probe=probe,heat=heat,cutoff_integral=integrated))
        mesh_rows[str(count)]=dict(spectra=spectra,parameter_applications=results)
    convergence=[]
    for probe in probes:
        q=probe['scaled_parameter']
        for coarse,fine in ((5,9),(9,17)):
            a=value_map[(coarse,q)];b=value_map[(fine,q)]
            differences={}
            for family in ('1','2'):
                u=a['families'][family]['integrated_paired_heat_mixed']
                v=b['families'][family]['integrated_paired_heat_mixed']
                absolute=float(np.linalg.norm(u-v));denom=float(np.linalg.norm(v))
                differences[family]=dict(absolute_Frobenius_difference=absolute,
                    relative_Frobenius_difference=absolute/denom if denom else None)
            u=a['middle_minus_light_fixed_core_difference'];v=b['middle_minus_light_fixed_core_difference']
            absolute=float(np.linalg.norm(u-v));denom=float(np.linalg.norm(v))
            differences['middle_minus_light']=dict(absolute_Frobenius_difference=absolute,
                relative_Frobenius_difference=absolute/denom if denom else None,
                fine_difference_Frobenius_norm=denom,
                subtraction_precision='difference is tiny against each family application; ordinary double-precision subtraction is not a certified relative-family accuracy')
            convergence.append(dict(scaled_parameter=q,coarse_nodes=coarse,fine_nodes=fine,differences=differences))
    source_owners=[
        ('src/bhsm/interface/muon_native_product_factor_graph.py',('lepton_unit_trace_gauge_representation',
            'finite_common_family_intrinsic_operator','retained_eight_q_fermion_source_image',
            'finite_family_eight_q_source_pairing','finite_eight_q_heat_core',
            'finite_eight_q_heat_application','finite_eight_q_cutoff_heat_application')),
        ('src/bhsm/interface/muon_native_dirac_hamiltonian.py',('canonical_lepton_hamiltonian_maps',
            'lepton_current_hilbert_representation','fixed_y_higgs_hamiltonian')),
        ('src/bhsm/interface/muon_parent_maxwell_full_q_application.py',('retained_full_q_angular_space',)),
        ('src/bhsm/interface/muon_parent_gauge_geometry_correction.py',('finite_common_iterate_at_time','correction_representation')),
        ('src/bhsm/interface/muon_material_higgs_gauge_action.py',('material_intrinsic_higgs_gauge_action_jet',)),
        ('src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',('intrinsic_m4_weight_jet',)),
        ('src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',('charged_lepton_yukawa_operator',)),
        ('src/bhsm/interface/ae4_current_c2_factorized_hs_calderon.py',('_product_dirac_map',)),
        ('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',('forward_time_domain_contract','microscopic_owner_contract')),
        ('scripts/evaluate_muon_native_product_factor_graph.py',('evaluate',)),
    ]
    packet=dict(classification='EVALUATED_ACTUAL_EIGHT_Q_FIXED_CORE_GRAPH_AND_PROJECTED_HEAT_OPERANDS',
        consumed_input_records=inputs,source_records=[record(path,symbols) for path,symbols in source_owners],
        source_normalization=dict(raw_Gram=graph['source']['raw_source_Gram'],
            saved_normalized_Gram=graph['source']['normalized_source_Gram'],
            relation=graph['source']['normalization_relation'],
            insertion='Xi_A=-i alpha^i G_c Q_i,c,h,A phi_h/R4; full U2 lepton representation, not scalar EM charge',
            extra_e_Tb_Tr16Q_squared_or_family_factor_applied=False,
            Haar_normalization='owned real harmonics unit Haar; 2pi^2 physical S3 Haar volume applied once'),
        finite_family_scope=dict(branch='outgoing branch24 E1+ germ; M5 spatial sigma1 patch of outgoing M4',
            chart_interval=[-rep['length'],0],is_incoming_C1_or_E0_history=False,
            representation_count=rep['count'],nu_squared_action=4,
            total_multiplier_density_max=0.36207908379,stationary_native_base=False,
            temporal_pullback='Omega_t=rho(At_ref); factor (partial_t+Omega_t)/N+W; no extra wall advection'),
        graph_application=graph_summary,heat_mesh_applications=mesh_rows,
        parameter_family=dict(reference_fine_n0_spectral_gap=gap,probes=probes,
            interpretation='operator-function numerical probes q/gap, not selected formation c=i/r',
            spectral_units='inverse squared inherited proper-clock coordinate unit; physical intrinsic scale not bound',
            cutoff_units='squared inherited proper-clock coordinate unit',
            positivity='all computed generalized Dirichlet factor spectra strictly positive; numerical margins, not continuum/global theorem'),
        convergence=convergence,
        errors=dict(mesh_and_lag_differences_are_estimates_not_enclosures=True,
            improper_proper_time_tail='analytically included to infinity',
            middle_light_relative_difference_accuracy_established=False),
        array_records={name:array_record(a) for name,a in arrays.items()},
        complete_native_heat_supertrace=False,relative_eta_and_owned_overlap_subtraction_completed=False,
        physical_source_lift_and_total_genuine_mixed_domain_jets_evaluated=False,
        physical_E0_stop_reset_exterior_domain_selected=False,
        Lorentz_to_native_analytic_continuation_certified=False,
        complete_R_ind_or_Pauli_evaluated=False,full_native_remainder_bound=False,
        no_measured_anomaly_or_SM_total_consumed=True)
    return serial(packet),arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();packet,arrays=evaluate()
    args.output.mkdir(parents=True,exist_ok=True)
    archive=deterministic_npz(arrays)
    packet['matrix_archive']=dict(path='source_paired_graph.npz',bytes=len(archive),sha256=hashlib.sha256(archive).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (args.output/'source_paired_graph.npz').write_bytes(archive)
    (args.output/'product_factor_graph_and_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=hashlib.sha256(raw).hexdigest(),receipt_bytes=len(raw),
        archive_sha256=packet['matrix_archive']['sha256'],archive_bytes=len(archive),
        spectral_gap=packet['parameter_family']['reference_fine_n0_spectral_gap'],
        c_parameters=[p['proper_time_or_cutoff'] for p in packet['parameter_family']['probes']],
        finest_mesh=packet['heat_mesh_applications']['17']['spectra']),sort_keys=True))


if __name__=='__main__':main()
