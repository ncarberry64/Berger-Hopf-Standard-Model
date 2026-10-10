#!/usr/bin/env python
"""Replay reached fixed-Y scalar mass terms in the actual eight-Q heat."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz,matrix_summary
from bhsm.interface.muon_native_coupled_source_heat import (
    retained_corrected_scalar_photon_response,corrected_response_source_vertices,
    corrected_first_response_heat_core,corrected_first_response_heat_application,
)

FIXED='artifacts/muon_native_product_factor_graph_20261010/run_1/product_factor_graph_and_heat.json'
FIXED_SHA='aac59f831b5e5cd328e352993427159ca1d4c89ebde25d1687e3a036b9510197'


def evaluate():
    r=retained_corrected_scalar_photon_response(ROOT)
    fixed_record=record(FIXED)
    if fixed_record['sha256']!=FIXED_SHA:raise ValueError('frozen fixed-field probe receipt changed')
    fixed=json.loads((ROOT/FIXED).read_bytes());probes=fixed['parameter_family']['probes']
    arrays={};vertex_rows=[]
    for i,u in enumerate((r['duration']/2,.0002,.0008,.001)):
        v=corrected_response_source_vertices(r,u+r['time_shift'])
        arrays[f'vertex_{i}_complex_H_response']=v['complex_H_response']
        arrays[f'vertex_{i}_fixed_Y_mass']=v['fixed_Y_mass_vertex']
        arrays[f'vertex_{i}_raw_gauge_unit_radius']=v['raw_gauge_unit_radius_vertex']
        vertex_rows.append(dict(response_time=u,coefficient_time=v['coefficient_time'],same_source_pulse=v['pulse'],
            actual_complex_H_response_Frobenius_norm=float(np.linalg.norm(v['complex_H_response'])),
            fixed_Y_mass_vertex_Frobenius_norm=float(np.linalg.norm(v['fixed_Y_mass_vertex'])),
            raw_gauge_unit_radius_vertex_Frobenius_norm=float(np.linalg.norm(v['raw_gauge_unit_radius_vertex'])),
            mass_vertex_Hermitian_residual=float(np.max(abs(v['fixed_Y_mass_vertex']-v['fixed_Y_mass_vertex'].conj().transpose(0,1,3,2))))))
    mesh_rows={};values={}
    for count in (5,9,17):
        core=corrected_first_response_heat_core(r,time_nodes=np.linspace(r['time_shift'],0,count),quadrature_order=4)
        spectra={}
        for f,data in core['families'].items():
            arrays[f'mesh_{count}_family_{f}_n0_eigenvalues']=data['n0_eigenvalues']
            spectra[f]=dict(inherited_family=data['inherited_family'],fixed_Y=data['fixed_Y'],
                n0_minimum=float(data['n0_eigenvalues'][0]),n0_maximum=float(data['n0_eigenvalues'][-1]),
                n0_mode_count=len(data['n0_eigenvalues']),
                generalized_eigen_residual_relative=data['generalized_eigen_residual_relative'],
                intermediate_shells={n:dict(mode_count=len(s['eigenvalues']),
                    eigen_minimum=float(s['eigenvalues'][0]),eigen_maximum=float(s['eigenvalues'][-1]),
                    all_complementary_modes_retained=s['all_complementary_eigenmodes_retained'],
                    actual_gauge_first_jet_Frobenius_norm=float(np.linalg.norm(s['first_jet_n0']['gauge'])),
                    actual_fixed_Y_scalar_first_jet_Frobenius_norm=float(np.linalg.norm(s['first_jet_n0']['scalar'])))
                    for n,s in data['intermediate_shells'].items()})
        applications=[]
        for probe in probes:
            c=probe['proper_time_or_cutoff']
            heat=corrected_first_response_heat_application(core,c)
            integral=corrected_first_response_heat_application(core,c,integrate_cutoff=True)
            values[(count,probe['scaled_parameter'])]=integral
            applications.append(dict(probe=probe,heat=heat,cutoff_integral=integral))
        mesh_rows[str(count)]=dict(spectra=spectra,applications=applications)
    differences=[]
    for probe in probes:
        q=probe['scaled_parameter']
        for coarse,fine in ((5,9),(9,17)):
            row={}
            for f in ('1','2'):
                row[f]={}
                for component in ('gauge','scalar','interference'):
                    a=values[(coarse,q)]['families'][f]['components'][component]['reached_first_response_pair']
                    b=values[(fine,q)]['families'][f]['components'][component]['reached_first_response_pair']
                    absolute=float(np.linalg.norm(a-b));denom=float(np.linalg.norm(b))
                    row[f][component]=dict(absolute_Frobenius_difference=absolute,
                        relative_Frobenius_difference=absolute/denom if denom else None,
                        fine_application=matrix_summary(b))
            differences.append(dict(scaled_parameter=q,coarse_nodes=coarse,fine_nodes=fine,components=row))
    owners=[
        ('src/bhsm/interface/muon_native_coupled_source_heat.py',('retained_corrected_scalar_photon_response',
            'corrected_response_source_vertices','corrected_first_response_heat_core','corrected_first_response_heat_application')),
        ('src/bhsm/interface/muon_native_product_factor_graph.py',('_family_shell_heat_forms','_ordered_heat_lag','_ordered_cutoff_heat_lag')),
        ('src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py',('coupled_corrected_retarded_form','corrected_retarded_application')),
        ('src/bhsm/interface/muon_native_dirac_hamiltonian.py',('fixed_y_higgs_hamiltonian',)),
        ('src/bhsm/interface/muon_parent_retarded_hypercharge.py',('compact_trace_pulse',)),
        ('scripts/evaluate_muon_native_coupled_source_heat.py',('evaluate',)),
        ('scripts/evaluate_muon_native_product_factor_graph.py',('record','serial','deterministic_npz')),
    ]
    packet=dict(classification='EVALUATED_SAME_SOURCE_SOLVED_H80_FIXED_Y_MASS_AND_EIGHT_Q_FIRST_RESPONSE_HEAT_COMPONENTS',
        consumed_input_records=r['source_records']+[fixed_record],source_records=[record(p,s) for p,s in owners],
        scalar_response_binding=dict(H_response_order=r['H_response_order'],
            source_profile=r['source_profile'],time_shift=r['time_shift'],duration=r['duration'],
            interpolation='CubicHermiteSpline of actual stored H80 value and Hdot from the same retarded dynamics',
            response_records=385,actual_H80_maximum=float(np.max(abs(r['H80']))),
            fixed_Y_source_equation='delta M_LR=(delta H) Y_l; reverse vertex is dagger; general doublet, all18 Weyl entries',
            spatial_wall_source_equation='delta Omega_i=g(u) sum_c,h Q_i,c,h,A phi_h G_c; At=Ar wall source zero; parent radial phi(WALL)=0',
            extra_e_Tb_Tr16Q_squared_or_family_factor_applied=False,
            physical_source_profile_or_history_selected=False),
        actual_vertex_applications=vertex_rows,parameter_probes=probes,
        parameter_role='same explicit numerical operator-function parameters as fixed-field receipt, not physical c=i/r',
        finite_domain_role='outgoing24 backward local coefficient germ t=u-L; NOT incoming C1/E0 history or physical birth domain',
        heat_mesh_applications=mesh_rows,mesh_convergence=differences,
        first_response_pair_equation='-s Tr0(e^-sP0 (Xi_v†Xi_J+Xi_J†Xi_v))+both ordered Duhamel insertions, Xi=raw gauge+actual fixed-Y scalar',
        components='gauge,scalar,andinterference evaluated independently before summing; tiny scalar term not recovered by subtraction of large totals',
        reached_genuine_mixed_term=dict(id='ACTUAL_MEAN_H_VJ_MASS_CONTACT',
            operator='A0† M(H_vJ,mean)+M(H_vJ,mean)† A0 in projected n0 row',
            value=None,status='NOT_YET_SOLVED_BY_REACHED_NONLINEAR_RESPONSE_PRODUCER',
            is_forced_affine_zero=False),
        full_geometric_and_domain_first_response=None,complete_source_pair_heat=None,
        array_records={name:array_record(a) for name,a in arrays.items()},
        continuum_error_enclosure=False,relative_eta_or_overlap_subtraction_completed=False,
        physical_native_domain_closed=False,complete_R_ind_or_Pauli_evaluated=False,
        no_measured_anomaly_or_SM_total_consumed=True)
    return serial(packet),arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();packet,arrays=evaluate();args.output.mkdir(parents=True,exist_ok=True)
    archive=deterministic_npz(arrays)
    packet['matrix_archive']=dict(path='source_mass_vertices.npz',bytes=len(archive),sha256=hashlib.sha256(archive).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (args.output/'source_mass_vertices.npz').write_bytes(archive)
    (args.output/'coupled_source_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_bytes=len(raw),receipt_sha256=hashlib.sha256(raw).hexdigest(),
        archive_bytes=len(archive),archive_sha256=packet['matrix_archive']['sha256'],
        actual_H80_maximum=packet['scalar_response_binding']['actual_H80_maximum']),sort_keys=True))


if __name__=='__main__':main()
