"""Evaluate reached open-lepton vertices on the common-birth magnetic pair."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_magnetic_open_lepton_vertex import reached_magnetic_open_vertex,magnetic_open_fields_at_node
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    hashes={};results={};summaries=[]
    angular=retained_full_q_angular_space(ROOT)
    for side in ('incoming','outgoing'):
        folder=Path('artifacts/muon_electromagnetic_soft_magnetic_source_20261011')/(side+'_run_1')
        bound=load_magnetic_reached_mean_inputs(folder,repository=ROOT);hashes.update(bound['input_hashes'])
        for position,index in (('midpoint',2),('birth',-1 if side=='incoming' else 0)):
            t=bound['source']['times'][index]
            fields=magnetic_open_fields_at_node(bound,t)
            result=reached_magnetic_open_vertex(fields,bound['representation'],angular,electric_charge=bound['electric_charge'])
            prefix=side+'_'+position
            for name in ('canonical_gauge_source_vertices','canonical_fixed_Y_H_source_vertices','canonical_total_source_vertices',
                'canonical_point_vertices','canonical_physical_spatial_gradient','charged_point_vertices',
                'charged_physical_spatial_gradient','covariant_charged_point_vertices','neutral_point_source_leakage',
                'neutral_background_leakage','charged_background_Hamiltonian'):
                results[prefix+'_'+name]=result[name]
            for key,value in result['matched_local_tree_symbol_spin_application'].items():
                if isinstance(value,np.ndarray):results[prefix+'_local_spin_'+key]=value
            results[prefix+'_charged_injection']=result['charged_injection']['charged']
            summaries.append(dict(side=side,position=position,response_time=float(t),coordinate_time=fields['coordinate_time'],
                actual_plateau_value=fields['profile'],actual_plateau_rate=fields['profile_rate'],
                source_value_reconstruction_discrepancy=fields['source_value_reconstruction_discrepancy'],
                source_rate_reconstruction_discrepancy=fields['source_rate_reconstruction_discrepancy'],
                saved_source_values_replaced=fields['saved_source_values_replaced'],
                fixed_Y_mass_action=result['fixed_Y_mass_action'],R4=result['operator']['R4'],N=result['operator']['N'],
                full_gauge_source_vertex_norm=float(np.linalg.norm(result['canonical_gauge_source_vertices'])),
                solved_H_source_vertex_norm=float(np.linalg.norm(result['canonical_fixed_Y_H_source_vertices'])),
                charged_point_vertex_norm=float(np.linalg.norm(result['charged_point_vertices'])),
                neutral_background_leakage_norm=float(np.linalg.norm(result['neutral_background_leakage'])),
                neutral_source_leakage_norm=float(np.linalg.norm(result['neutral_point_source_leakage'])),
                matched_local_tree_symbol_spin_norm=float(np.linalg.norm(result['matched_local_tree_symbol_spin_application']['spin_coefficients'])),
                current_Gram_defect=result['charged_injection']['current_Gram_defect'],charge_defect=result['charged_injection']['charge_defect']))
    own=('src/bhsm/interface/muon_magnetic_open_lepton_vertex.py','src/bhsm/interface/muon_magnetic_source_mean_load.py',
         'src/bhsm/interface/muon_native_dirac_hamiltonian.py','src/bhsm/interface/muon_native_product_factor_graph.py',
         'src/bhsm/interface/muon_intrinsic_higgs_weak_action.py','src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',
         'src/bhsm/interface/muon_intrinsic_scalar_discretization.py','scripts/evaluate_muon_reached_trace_action.py',
         Path(__file__).relative_to(ROOT).as_posix())
    for name in own:hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',results)
    archive=out/'application.npz'
    if archive.stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds retained publication limit')
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:
        raise RuntimeError('consumed action/source changed during application')
    receipt=dict(classification='EVALUATED_COMMON_BIRTH_MAGNETIC_OPEN_LEPTON_FIELD_VERTICES',
        application_sha256=sha256(archive.read_bytes()).hexdigest(),application_bytes=archive.stat().st_size,
        input_hashes=hashes,samples=summaries,active_magnetic_axes=[0,1,2],inactive_padded_axes=[3,4,5,6,7],
        canonical_current='chi_hat=R4^(3/2)psi/(2pi^2); unit current Gram',electric_charge_inserted_once=True,
        action_vertex='deltaHcan=-i alpha_i G_c deltaA_i/R4-i G_c deltaA_t/N+M_fixedY(deltaH)',
        mixed_open_lepton_field_Hessian_applied=True,both_LR_mass_placements_retained=True,
        solved_H80_used=True,physical_local_magnetic_first_jet_used=True,common_birth_canonical_transfer_used=True,
        local_spin_application='P+ V(0) P+ -i/(4m_tree) P+ sum_i[alpha_i,partial_i V] P+; explicit free-rest-symbol derivative expansion only',
        local_spin_mass='original fixed Y_middle times actual |H| in action units; no independent Yukawa fitting',
        neutral_background_leakage_exported=True,neutral_leakage_removed=False,
        complete_angular_geometry_first_response_claimed=False,
        actual_interacting_LSZ_selected=False,quantum_P_A_ghost_P_HS_loop_contracted=False,
        intrinsic_H_identified_with_EC_HS_auxiliary=False,
        native_photon_return_assigned_to_F2=False,local_spin_diagnostic_assigned_to_F2=False,
        complete_a_mu=None,complete_g_mu=None,complete_observable=False,
        error_scope='binary64 action matrices on frozen common-birth finite response; no continuum, source-rounding, quantum loop, interacting-pole or soft-limit enclosure')
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=receipt['classification'],application_sha256=receipt['application_sha256'],samples=summaries)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
