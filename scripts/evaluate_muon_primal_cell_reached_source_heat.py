"""Evaluate actual fresh Higgs source heat on the enriched numerical cells."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_current_source_motion_mean_load import load_enriched_reached_mean_inputs,enriched_reached_first_fields
from bhsm.interface.muon_primal_cell_reached_source_heat import actual_midpoint_reached_source_heat
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


def _arrays(value,prefix,output):
    if isinstance(value,np.ndarray):output[prefix]=value
    elif isinstance(value,dict):
        for name,child in value.items():_arrays(child,prefix+'_'+name,output)


def evaluate(directories,cutoff):
    angular=retained_full_q_angular_space(ROOT);arrays={};rows=[];hashes={}
    for side,directory in directories.items():
        print(json.dumps(dict(stage='actual_midpoint_total_first_source_heat',side=side)),flush=True)
        inputs=load_enriched_reached_mean_inputs(directory,repository=ROOT)
        if inputs['receipt']['side']!=side:raise ValueError('response side mismatch')
        fields=enriched_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
        length=abs(inputs['receipt']['actual_phase_span'])
        result=actual_midpoint_reached_source_heat(fields,inputs['representation'],angular,length=length,cutoff=cutoff)
        _arrays(result,side,arrays);hashes.update(inputs['input_hashes'])
        r=result['paired_middle_minus_light_Y2_source_pair']
        rows.append(dict(side=side,response_time=fields['response_time'],coordinate_time=fields['coordinate_time'],
            source_profile=fields['profile'],source_profile_rate=fields['profile_rate'],
            wall_gauge_norm=result['vertices']['intrinsic_wall_gauge_norm'],first_H_norm=float(np.linalg.norm(fields['first_H'])),
            paired_middle_minus_light_Y2_channel_trace=result['paired_middle_minus_light_Y2_channel_trace'],
            paired_lag_rule32_64_difference_norm=result['paired_middle_minus_light_lag_rule32_64_difference_norm'],
            lag_difference_scope='quadrature refinement estimate, not outward enclosure; proper-time tail integrated analytically to infinity',
            channel_matrix_norms={name:float(np.linalg.norm(value)) for name,value in r.items()},
            ordered_source_labels='first order AB and opposite BA, both retained',
            n0_gap=float(min(result['zero_Y_source_core']['n0_eigenvalues'])),
            intermediate_mode_counts={n:s['intermediate_mode_count'] for n,s in result['zero_Y_source_core']['intermediate_shells'].items()}))
    sources=[record('src/bhsm/interface/muon_primal_cell_reached_source_heat.py',
        ('actual_reached_cell_vertices','_spectral_source_core','_cutoff_source_pair','actual_midpoint_reached_source_heat')),
        record('src/bhsm/interface/muon_current_source_motion_mean_load.py',('load_enriched_reached_mean_inputs','enriched_reached_first_fields')),
        record('src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',('primal_trace_enriched_lepton_operator',)),
        record('src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py',('primal_intrinsic_lepton_operator',)),
        record('src/bhsm/interface/muon_native_dirac_hamiltonian.py',('fixed_y_higgs_hamiltonian','lepton_current_hilbert_representation')),
        record('src/bhsm/interface/muon_native_product_factor_graph.py',('lepton_unit_trace_gauge_representation','_ordered_cutoff_heat_lag')),
        record('src/bhsm/interface/muon_native_mean_core_heat_target.py',('_unit_lepton_mass6',)),
        record('src/bhsm/interface/muon_primal_cell_native_heat.py',('_positive_length',)),
        record('src/bhsm/interface/muon_parent_maxwell_full_q_application.py',('retained_full_q_angular_space',)),
        record('scripts/evaluate_muon_primal_cell_reached_source_heat.py',('evaluate',))]
    for item in sources:hashes[item['path']]=item['sha256']
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('source owner changed')
    return serial(dict(classification='EVALUATED_ACTUAL_SAME_PHASE_FIXED_Y2_SOURCE_HEAT_PARTIAL',
        input_hashes=hashes,source_records=sources,applications=rows,array_records={k:array_record(v) for k,v in arrays.items()},
        cutoff_probe=cutoff,cutoff_scope='explicit numerical probe shared with the frozen actualcell midpoint target; not physical c=i/r',
        positive_core_scope='same numerical Dirichlet temporal tent and actual midpoint coefficients; normalized Haar/clock Gram',
        source_pair_equation='Xi=Y Xi_H; exact Y² coefficient is -Tr0[e^-cP0/P0*(Xi_A†Xi_B+Xi_B†Xi_A)] plus both complete n1/n3 ordered insertions',
        total_first_gauge_and_H_response_used=True,wall_gauge_zero_has_owned_Dirichlet_provenance=True,
        fixed_prescribed_b_source_native_insertions_substituted=False,
        body_Grassmann_source_reselected=False,independent_C_or_anomaly_input_used=False,
        source_motion_or_Haar_normalization_applied_twice=False,
        full_angular_geometry_first_response_closed=False,induced_mean_second_operator_contact_included=False,
        Y4_remainder_outward_certified=False,relative_supertrace_or_statistics_selected=False,
        complete_native_or_Pauli=False,
        error_scope='binary64 spectral application and retained64-point lag quadrature on the actual finite coefficient cell; Y² coefficient evaluated, higher even Y and physical-domain remainder separate')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--incoming-response',type=Path,required=True);p.add_argument('--outgoing-response',type=Path,required=True);p.add_argument('--cutoff',type=float,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve previous applications')
    packet,arrays=evaluate(dict(incoming=a.incoming_response,outgoing=a.outgoing_response),a.cutoff);data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('retain all source images in lossless split archives')
    a.output.mkdir(parents=True);(a.output/'source_heat.npz').write_bytes(data)
    packet['archive']=dict(path='source_heat.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'source_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],applications=packet['applications'])),flush=True)


if __name__=='__main__':main()
