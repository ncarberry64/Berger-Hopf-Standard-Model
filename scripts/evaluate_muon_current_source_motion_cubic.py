"""Evaluate current-source chart contacts on actual enriched primal endpoints."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_current_source_motion_cubic import prescribed_source_cubic_application

ENDPOINT='artifacts/muon_parent_gauge_geometry_correction_20261010/paired_field_endpoint_enriched_run_1'
ENDPOINT_ARCHIVE_SHA256='6b6b5226a0f93ad0ddc2bd4b0671814514a7cf3ca470fe66ee1052b589282eb5'


def evaluate():
    folder=ROOT/ENDPOINT;data=(folder/'application.npz').read_bytes()
    if sha256(data).hexdigest()!=ENDPOINT_ARCHIVE_SHA256:raise ValueError('pinned actual enriched primal fields changed')
    receipt=json.loads((folder/'result.json').read_text(encoding='utf8'))
    if receipt['numerical_sha256']!=ENDPOINT_ARCHIVE_SHA256:raise ValueError('endpoint receipt/archive disagree')
    inputs={ENDPOINT+'/'+name:sha256((folder/name).read_bytes()).hexdigest() for name in ('result.json','application.npz')}
    for name,digest in receipt['input_hashes'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('endpoint owner changed:'+name)
        inputs[name]=digest
    with np.load(folder/'application.npz',allow_pickle=False) as a:fields={k:a[k].copy() for k in a.files}
    rep=correction_representation(radial_points=receipt['radial_points'],cap_points=receipt['cap_points'],radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    for name in ('rho','radial_quadrature','gauge_basis','gauge_radial_basis','wall_trace_map','wall_radial_derivative_map','radial_value_map','radial_derivative_map'):
        rep[name]=fields[name]
    rep['gauge_labels']=receipt['gauge_labels'];rep['gauge_count']=80
    angular=retained_full_q_angular_space(ROOT);b=angular['source_coefficients'];arrays={'raw_enriched_primal_pair':fields['updated_raw_pair'],'fixed_b_test_source_coefficients':b};rows=[]
    for side,raw in zip(('incoming23','outgoing24'),fields['updated_raw_pair']):
        print(json.dumps(dict(stage='actual_enriched_endpoint_source_chart_cubic',side=side)),flush=True)
        application=prescribed_source_cubic_application(raw,rep,angular,b,1.,0.,nu_squared_action=receipt['action_parameters']['nu_squared_action'])
        for key,value in application.items():
            if isinstance(value,np.ndarray):arrays[side+'_'+key]=value
        names=('fixed_field_geometry_cubic','moving_source_geometry_cubic','complete_geometry_cubic_at_fixed_interior_first_coefficients','Maxwell_moving_source_geometry_cubic','scalar_moving_source_geometry_cubic')
        rows.append(dict(side=side,position='exact_common_birth',T_b=application['T_b'],T_b_dot=application['T_b_dot'],
            source_profile_value=1.,source_profile_coordinate_rate=0.,
            profile_scope='instantaneous coefficient-basis action test; not a selected source temporal history',
            norms={name:float(np.linalg.norm(application[name])) for name in names},
            pair_symmetry_relative={name:float(np.linalg.norm(application[name]-application[name].swapaxes(-1,-2))/(1+np.linalg.norm(application[name]))) for name in names},
            normal_geometry_pair=application['complete_geometry_cubic_at_fixed_interior_first_coefficients'][98],
            normal_rate_geometry_pair=application['complete_geometry_cubic_at_fixed_interior_first_coefficients'][99],
            scalar_first_zero_scope=application['scalar_first_zero_scope']))
    sources=[record('src/bhsm/interface/muon_current_source_motion_cubic.py',('current_face_source_jets','maxwell_cross_hessian','higgs_cross_hessian','current_source_cubic_application','prescribed_source_cubic_application')),
        record('scripts/evaluate_muon_current_source_motion_cubic.py',('evaluate',)),
        record('src/bhsm/interface/muon_parent_maxwell_source_mean_forcing.py',('maxwell_mean_cotangents','higgs_mean_cotangents')),
        record('src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',('intrinsic_m4_weight_jet',))]
    for row in sources:inputs[row['path']]=row['sha256']
    if inputs!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in inputs}:raise RuntimeError('consumed source/input changed during application')
    report=dict(classification='EVALUATED_EXPLICIT_MOVING_SOURCE_CUBIC_ON_ACTUAL_ENRICHED_PRIMAL_ENDPOINTS',input_hashes=inputs,source_records=sources,
        applications=rows,array_records={k:array_record(v) for k,v in arrays.items()},
        action_chain_rule='D_z S_AB=D3S[z,u_A,u_B]+D2S[D_z u_A,u_B]+D2S[u_A,D_z u_B]',
        normalization='Tb=(2pi² R4)^(-1/2); Tbdot=-Tb*dlogR4_dt/2; unit-Haar angular Gram; common Maxwell1/[8*(2pi²)^2] and scalar1/(2pi²)^2 each once',
        b_test_basis='fixed inherited raw fullQ400x8 computational directions in b coordinates; rawGram16/3 I8 preserved; no e,QNORM or oldTb inserted',
        retained_angular_scope='complete real n1+n3 source images20; background angular-homogeneous, all4 internal components/all5fields retained',
        radial_scope='actual enriched4-function gauge frame; independent wall lift gives the explicit instantaneous source restriction only',
        actual_nonzero_independent_gauge_and_H_background_used=True,source_motion_count=1,
        scalar_gauge_Hessian_interference_retained=True,
        actual_new_causal_first_response_used=False,old_backward_response_substituted=False,
        zero_interior_or_scalar_variation_is_physical_assertion=False,
        full_cubic_mean_forcing_or_second_response_solved=False,
        geometric_jump_unit_area_formation_or_complementary_graph_closed=False,
        complete_native_heat_or_Pauli_evaluated=False,
        error_scope='analytic finite source/geometry contractions evaluated in binary64 on48radial quadrature; no continuum/rounding enclosure; coefficient test has no temporal extension')
    return serial(report),arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate();archive=deterministic_npz(arrays)
    if len(archive)>10*1024**2:raise ValueError('retain every array and split losslessly')
    args.output.mkdir(parents=True);(args.output/'source_motion_cubic.npz').write_bytes(archive)
    packet['archive']=dict(path='source_motion_cubic.npz',bytes=len(archive),sha256=sha256(archive).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(args.output/'source_motion_cubic.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),receipt_bytes=len(raw),archive=packet['archive'])),flush=True)


if __name__=='__main__':main()
