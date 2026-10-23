"""Evaluate active magnetic gauge/H contact and both heat insertions."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs,magnetic_reached_first_fields
from bhsm.interface.muon_magnetic_cell_source_heat import (
    magnetic_source_heat_polynomial,magnetic_source_even_y2_coefficient,magnetic_source_analytic_error_estimates)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


def _arrays(value,prefix,output):
    if isinstance(value,np.ndarray):output[prefix]=value
    elif isinstance(value,dict):
        for name,child in value.items():_arrays(child,prefix+'_'+name,output)
    elif isinstance(value,tuple):
        for i,child in enumerate(value):_arrays(child,prefix+'_'+str(i),output)


def evaluate(directories):
    angular=retained_full_q_angular_space(ROOT);bound={};hashes={};arrays={};arms=[]
    for side,path in directories.items():
        inputs=load_magnetic_reached_mean_inputs(path,repository=ROOT)
        if inputs['receipt']['side']!=side:raise ValueError('source arm differs')
        fields=magnetic_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
        poly=magnetic_source_heat_polynomial(fields,inputs['representation'],angular,length=inputs['times'][-1])
        bound[side]=(inputs,fields,poly);hashes.update(inputs['input_hashes'])
    gap=min(float(np.linalg.eigvalsh(p['n0_pencil'][0])[0]) for _,_,p in bound.values())
    for side,(inputs,fields,poly) in bound.items():
        print(json.dumps(dict(stage='actual_magnetic_contact_both_insertions',side=side)),flush=True)
        for key in ('n0_pencil','contact','shells'):_arrays(poly[key],side+'_'+key,arrays)
        for key in ('raw_fields','first_H','first_H_rate','first_wall_gauge'):arrays[side+'_'+key]=fields[key]
        applications=[]
        for q in (.25,1.,4.):
            c=q/gap;label=side+'_q_'+str(q).replace('.','p')
            result=magnetic_source_even_y2_coefficient(poly,c,contour_radius=16384,contour_order=32,lag_order=64)
            refined=magnetic_source_even_y2_coefficient(poly,c,contour_radius=32768,contour_order=64,lag_order=96)
            estimates=magnetic_source_analytic_error_estimates(poly,c)
            _arrays(result,label,arrays);_arrays(estimates,label+'_analytic_estimates',arrays)
            a=result['paired_middle_minus_light_Y2_source_pair'];b=refined['paired_middle_minus_light_Y2_source_pair']
            difference=float(np.linalg.norm(a['available_source_pair']-b['available_source_pair']))
            applications.append(dict(q_probe=q,cutoff_probe=c,
                ungraded_direct_trace=float(np.trace(a['available_source_pair']).real),
                contact_trace=float(np.trace(a['source_square_contact']).real),
                first_ordered_trace=float(np.trace(a['ordered_two_insertion']).real),
                opposite_ordered_trace=float(np.trace(a['opposite_order_two_insertion']).real),
                contour_lag_refinement_absolute=difference,
                contour_lag_refinement_relative=difference/np.linalg.norm(a['available_source_pair']),
                coefficient_imaginary_rounding_norm=result['coefficient_imaginary_rounding_norm'],
                numerical_circle_accretivity_margin=result['numerical_circle_accretivity_margin'],
                paired_even_Y4_majorant_estimate_maximum=float(np.max(estimates['paired_even_Y4_remainder_majorant_estimate'])),
                paired_contour_alias_estimate_maximum=float(np.max(estimates['unit_Y2_contour_alias_majorant_estimate'])*abs(result['fixed_Y_square_difference'])),
                analytic_estimates_outward_certified=False))
        arms.append(dict(side=side,response_time=fields['response_time'],coordinate_time=fields['coordinate_time'],
            source_profile=fields['profile'],source_profile_rate=fields['profile_rate'],
            active_magnetic_axes=[0,1,2],absent_padded_axes=[3,4,5,6,7],
            first_wall_gauge_norm=float(np.linalg.norm(fields['first_wall_gauge'])),
            first_H_norm=float(np.linalg.norm(fields['first_H'])),applications=applications))
    sources=[record('src/bhsm/interface/muon_magnetic_cell_source_heat.py',
        ('magnetic_source_heat_polynomial','analytic_magnetic_source_pair','magnetic_source_even_y2_coefficient','magnetic_source_analytic_error_estimates')),
        record('src/bhsm/interface/muon_magnetic_source_mean_load.py',('load_magnetic_reached_mean_inputs','magnetic_reached_first_fields')),
        record('src/bhsm/interface/muon_primal_cell_reached_source_heat.py',('actual_reached_cell_vertices',)),
        record('scripts/evaluate_muon_magnetic_native_source_heat.py',('evaluate',))]
    for item in sources:hashes[item['path']]=item['sha256']
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('consumed owner changed')
    return serial(dict(classification='EVALUATED_ACTIVE_MAGNETIC_GAUGE_PLUS_H_SAME_CELL_HEAT_SOURCE_PAIR',
        input_hashes=hashes,source_records=sources,arms=arms,array_records={k:array_record(v) for k,v in arrays.items()},
        common_zero_Y_gap=gap,complete_n1_n3_source_images=True,both_source_orders_retained=True,
        direct_Xi_adjoint_Xi_contact_retained=True,actual_solved_H_response_and_active_gauge_source_retained=True,
        complex_Grassmann_statistics_factor_not_yet_inserted=True,mean_second_operator_contact_not_in_this_direct_component=True,
        source_normalization='actual canonical e R4^2/2 magnetic source is inserted once; no extra Tb/e/QNORM/Haar factor',
        temporal_scope='same actual attached midpoint coefficient cell, positive Dirichlet temporal tent; source response is retarded ramp then inherited plateau',
        even_Y2_is_coefficient_algorithm_not_zero_H_state=True,
        local_overlap_subtraction_applied=False,full_native_relative_eta_ghost_or_Pauli_completed=False,
        physical_formation_cutoff_selected=False,complete_observable=False,
        error_scope='finite binary64 analytic coefficient application with contour/lag refinement and separately evaluated conditional majorants; no upstream norm/eigen, continuum, temporal projection, domain or cutoff enclosure')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--incoming-response',type=Path,required=True)
    p.add_argument('--outgoing-response',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate(dict(incoming=a.incoming_response,outgoing=a.outgoing_response))
    data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('preserve all arrays by lossless split')
    a.output.mkdir(parents=True);(a.output/'source_heat.npz').write_bytes(data)
    packet['archive']=dict(path='source_heat.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'source_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],arms=packet['arms'])),flush=True)


if __name__=='__main__':main()
