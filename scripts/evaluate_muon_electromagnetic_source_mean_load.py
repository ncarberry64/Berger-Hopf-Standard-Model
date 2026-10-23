"""Evaluate the full sourced mean load on the new actual H-selected EM response."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_current_source_motion_mean_load import (
    enriched_reached_first_fields,
)
from bhsm.interface.muon_electromagnetic_source_mean_load import (
    load_electromagnetic_reached_mean_inputs,electromagnetic_source_complete_mean_load,
    electromagnetic_source_jet_at_node,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


def evaluate(directories):
    angular=retained_full_q_angular_space(ROOT);arrays={};rows=[];hashes={}
    for side,directory in directories.items():
        print(json.dumps(dict(stage='complete_same_phase_mean_load',side=side)),flush=True)
        inputs=load_electromagnetic_reached_mean_inputs(directory,repository=ROOT)
        if inputs['receipt']['side']!=side:raise ValueError('response side mismatch')
        fields=enriched_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
        kwargs={name:fields[name] for name in ('first_gauge','first_gauge_rate','first_gauge_radial','first_wall_gauge','first_H','first_H_rate')}
        source_jet=electromagnetic_source_jet_at_node(inputs,fields['response_time'])
        applied=electromagnetic_source_complete_mean_load(fields['raw_fields'],inputs['representation'],angular,
            source_jet,fields['profile'],fields['profile_rate'],**kwargs,
            nu_squared_action=inputs['receipt']['action_parameters']['nu_squared_action'])
        for name,value in applied.items():
            if isinstance(value,np.ndarray):arrays[side+'_'+name]=value
        for name,value in applied['geometry_application'].items():
            if isinstance(value,np.ndarray):arrays[side+'_geometry_'+name]=value
        arrays[side+'_raw268']=fields['raw_fields'];arrays[side+'_first_H']=fields['first_H'];arrays[side+'_first_H_rate']=fields['first_H_rate']
        arrays[side+'_first_wall_gauge']=fields['first_wall_gauge']
        hashes.update(inputs['input_hashes'])
        names=('raw_mean_cotangent','Maxwell_gauge_value_cotangent','Maxwell_gauge_rate_cotangent',
            'scalar_gauge_value_cotangent','scalar_value_cotangent','scalar_rate_cotangent')
        rows.append(dict(side=side,response_time=fields['response_time'],coordinate_time=fields['coordinate_time'],
            temporal_position='actual solved primal phase midpoint; fresh first response at the same retained node',
            profile=fields['profile'],profile_rate=fields['profile_rate'],
            source_motion_zero_here_reason='compact pulse duration=L/4, midpoint=L/2 lies outside support',
            norms={name:float(np.linalg.norm(applied[name])) for name in names},
            geometry_fixed_field_norm=float(np.linalg.norm(applied['geometry_application']['fixed_field_geometry_cubic'])),
            geometry_source_motion_norm=float(np.linalg.norm(applied['geometry_application']['moving_source_geometry_cubic'])),
            first_H_norm=float(np.linalg.norm(fields['first_H'])),first_H_rate_norm=float(np.linalg.norm(fields['first_H_rate'])),
            first_gauge_norm=float(np.linalg.norm(fields['first_gauge'])),first_gauge_rate_norm=float(np.linalg.norm(fields['first_gauge_rate'])),
            pair_symmetry_relative=float(np.linalg.norm(applied['raw_mean_cotangent']-applied['raw_mean_cotangent'].swapaxes(-1,-2))/(1+np.linalg.norm(applied['raw_mean_cotangent']))),
            At_time_derivative_scope=fields['At_time_derivative_scope']))
    sources=[record('src/bhsm/interface/muon_current_source_motion_mean_load.py',
        ('current_source_complete_mean_load','enriched_reached_first_fields')),
        record('src/bhsm/interface/muon_electromagnetic_source_mean_load.py',
            ('load_electromagnetic_reached_mean_inputs','electromagnetic_source_complete_mean_load','source_jet_motion_contact')),
        record('src/bhsm/interface/muon_primal_electromagnetic_source.py',('higgs_aligned_source_first_jets',)),
        record('scripts/evaluate_muon_electromagnetic_source_mean_load.py',('evaluate',)),
        record('src/bhsm/interface/muon_current_source_motion_cubic.py',('current_source_cubic_application',)),
        record('src/bhsm/interface/muon_parent_maxwell_source_mean_forcing.py',('maxwell_mean_cotangents','higgs_mean_cotangents'))]
    for item in sources:hashes[item['path']]=item['sha256']
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('consumed owner changed during application')
    return serial(dict(classification='EVALUATED_TOTAL_RAW268_CUBIC_MEAN_LOAD_FROM_FRESH_SAME_PHASE_RESPONSES',
        input_hashes=hashes,source_records=sources,applications=rows,array_records={k:array_record(v) for k,v in arrays.items()},
        raw_coordinate_order='q37,qdot37,m24,normal,normal_rate,gauge80,gauge_rate80,Hreal4,Hrate4',
        action_chain_rule='D_z S_AB=D3S[z,u_A,u_B]+D2S[D_z u_A,u_B]+D2S[u_A,D_z u_B]',
        normalization='Maxwell1/[8*(2piÂ²)^2], scalar1/(2piÂ²)^2; real2Re scalar and full Haar volume once',
        all_solved_first_Gauss_gauge_and_H_fields_used=True,all_represented_mean_rows_retained=True,
        source_coordinate_clock='incoming coordinate_time=u-L; outgoing coordinate_time=u; dcoordinate_time/du=+1; signed past phase step never reverses field derivatives',
        At_Gauss_rows_removed=False,paired_derivative_divided_by_two=False,source_motion_count=1,
        response_radial_scope='root fresh finite radial polynomial interior and actual Higgs-selected electromagnetic wall source; actual full220 attached80 background retained',
        homogeneous_geometry_first_variations_zero_scope='literal retained odd n1+n3 source sector has zero Haar projection to the represented homogeneous geometry100; unrepresented angular geometry not filled zero',
        complete_angular_geometry_first_response_claimed=False,old_response_or_bare_source_substituted=False,
        actual_H_selected_EM_source=True,old_transported_Q8_source_substituted=False,
        analytic_H_and_Hdot_source_motion_retained=True,
        consumed_full_attachment=True,consumed_endpoint_scope='evaluated full220 action attachment; fixed computational representation',
        midpoint_prescribed_source_native_heat_combined_with_total_mean_load=False,
        joint_mean_response_solved=False,physical_birth_domain_completed=False,complete_native_or_Pauli=False,
        error_scope='literal finite action third contractions in binary64 on saved48 radial quadrature and actual ODE response node; no continuum or rounding enclosure')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--incoming-response',type=Path,required=True);p.add_argument('--outgoing-response',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate(dict(incoming=a.incoming_response,outgoing=a.outgoing_response));data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('retain all arrays in lossless split archives')
    a.output.mkdir(parents=True);(a.output/'mean_load.npz').write_bytes(data)
    packet['archive']=dict(path='mean_load.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'mean_load.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],applications=packet['applications'])),flush=True)


if __name__=='__main__':main()
