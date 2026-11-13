"""Actual interacting incoming/outgoing midpoint native-form components."""
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
from bhsm.interface.muon_primal_cell_native_heat import actual_cell_heat_polynomial,actual_cell_even_y_target,actual_cell_eight_q_heat_core,actual_cell_eight_q_cutoff_application

BASE='artifacts/muon_parent_gauge_geometry_correction_20261010'
PHASES={
'incoming23':('enriched_phase_incoming_1steps_run_1','958dc8353823b362fd655c3a8562a8f2531019d2b0575ddc2338f2917ae96af8','6de4d0655947a1ba4053979accb669e018343991f5c15164c6d4a6bbc74e4edb'),
'outgoing24':('enriched_phase_outgoing_1steps_run_1','2dc5ec7a15a670d8dfa6ab6f600f9ddc4225799df961cbe07157bd8df469ef36','4daeae0ced32deb3604329386ea37a36fb3091c706a27202e6818f7427bd062b')}


def evaluate():
    bound=[];inputs={};arrays={};rows=[]
    for side,(name,archive_hash,receipt_hash) in PHASES.items():
        folder=ROOT/BASE/name;data=(folder/'application.npz').read_bytes();raw=(folder/'result.json').read_bytes()
        if sha256(data).hexdigest()!=archive_hash or sha256(raw).hexdigest()!=receipt_hash:raise ValueError('actual enriched phase changed')
        md=json.loads(raw)
        if md['numerical_sha256']!=archive_hash:raise ValueError('actual phase receipt/archive mismatch')
        for name2,digest in md['input_hashes'].items():
            if sha256((ROOT/name2).read_bytes()).hexdigest()!=digest:raise ValueError('actual phase owner changed:'+name2)
            inputs[name2]=digest
        inputs[BASE+'/'+name+'/application.npz']=archive_hash;inputs[BASE+'/'+name+'/result.json']=receipt_hash
        with np.load(folder/'application.npz',allow_pickle=False) as a:fields=a['stage_midpoint_raw'][0].copy();wall=a['wall_trace_map'].copy()
        rep=correction_representation(radial_points=md['radial_points'],cap_points=md['cap_points'],radial_order=2,include_wall_lift=True,include_scalar_mean=True)
        rep['gauge_labels']=md['gauge_labels'];rep['wall_trace_map']=wall
        length=abs(md['span']);polynomial=actual_cell_heat_polynomial(fields,rep,length=length)
        core=actual_cell_eight_q_heat_core(fields,rep,length=length,repository=ROOT)
        bound.append((side,md,polynomial,core));arrays[side+'_actual_midpoint_raw']=fields
        for key,value in polynomial.items():
            if isinstance(value,np.ndarray):arrays[side+'_'+key]=value
        for family,f in core['families'].items():
            arrays[side+'_family_'+family+'_n0_eigenvalues']=f['n0_eigenvalues'];arrays[side+'_family_'+family+'_mixed_contact_n0']=f['mixed_contact_n0_spectral_diagonal']
            for shell,data in f['intermediate_shells'].items():
                for key,value in data.items():
                    if isinstance(value,np.ndarray):arrays[side+'_family_'+family+'_shell_'+shell+'_'+key]=value
    common_gap=min(float(np.linalg.eigvalsh(p['P0'])[0]) for _,_,p,_ in bound)
    for side,md,polynomial,core in bound:
        print(json.dumps(dict(stage='actual_enriched_primal_cell_heat',side=side)),flush=True)
        applications=[]
        for q in (.25,1.,4.):
            c=q/common_gap;target=actual_cell_even_y_target(polynomial,c,divided_difference_order=16);coarse=actual_cell_even_y_target(polynomial,c,divided_difference_order=8)
            source=actual_cell_eight_q_cutoff_application(core,c)
            target['8_to_16_DD_paired_raw_cotangent_absolute_difference']=float(np.linalg.norm(target['paired_middle_minus_light_raw_cotangent']-coarse['paired_middle_minus_light_raw_cotangent']))
            target['8_to_16_DD_paired_value_absolute_difference']=abs(target['paired_middle_minus_light_Y2_value']-coarse['paired_middle_minus_light_Y2_value'])
            label=side+'_q_'+str(q).replace('.','p')
            for key,value in target.items():
                if isinstance(value,np.ndarray):arrays[label+'_'+key]=value
            for family,value in source['families'].items():
                for key,matrix in value.items():
                    if isinstance(matrix,np.ndarray):arrays[label+'_family_'+family+'_'+key]=matrix
            applications.append(dict(q_probe=q,cutoff_probe=c,cutoff_role='numerical common-gap function probe, not c=i/r formation',even_Y_target=target,explicit_source_heat_pair=source))
        op=polynomial['operator']
        rows.append(dict(side=side,signed_primal_step=md['span'],cell_length=polynomial['length'],midpoint_coordinate_time=md['span']/2,
            N=op['N'],R4=op['R4'],H=op['H'],W_norm=float(np.linalg.norm(op['W'])),Omega_tau_norm=float(np.linalg.norm(op['Omega_tau'])),
            positive_Gram_scalar=polynomial['FE_Gram_scalar'],numerical_P0_gap=float(np.linalg.eigvalsh(polynomial['P0'])[0]),
            temporal_policy='future coordinate derivative and material Atref/N; negative incoming integrationstep does not reverse field-derivative sign',
            coefficient_cell_scope=polynomial['coefficient_cell_scope'],domain=polynomial['domain'],applications=applications))
    sources=[record('src/bhsm/interface/muon_primal_cell_native_heat.py',('actual_cell_heat_polynomial','actual_cell_even_y_target','actual_cell_eight_q_heat_core','actual_cell_eight_q_cutoff_application')),
        record('scripts/evaluate_muon_primal_cell_native_heat.py',('evaluate',)),
        record('src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',('primal_trace_enriched_lepton_operator',)),
        record('src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py',('primal_intrinsic_lepton_operator',)),
        record('src/bhsm/interface/muon_native_product_factor_graph.py',('retained_eight_q_fermion_source_image','_ordered_cutoff_heat_lag'))]
    for row in sources:inputs[row['path']]=row['sha256']
    if inputs!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in inputs}:raise RuntimeError('actual phase/operator/source changed during application')
    return serial(dict(classification='EVALUATED_NATIVE_FACTOR_HEAT_COMPONENTS_ON_ACTUAL_ENRICHED_PRIMAL_CELLS',input_hashes=inputs,source_records=sources,
        common_probe_gap=common_gap,applications=rows,array_records={k:array_record(v) for k,v in arrays.items()},
        normalized_positive_factor='A=(partial_t+Omega_t)/N+W; chi=R4^(3/2)psi; current Gram I18',
        Lorentz_Hcan_used_as_Euclidean_temporal_connection=False,
        temporal_FE_equation='P=12/(NÂ²LÂ²)I+(W+Omega_tau)dagger(W+Omega_tau); FEGram=N*2piÂ²*L/3',
        actual_enriched_nonzero_gauge_H_and_geometry_rate_used=True,old_compact_H_or_old_backward_operator_borrowed=False,
        stable_paired_target='(Y_muÂ²-Y_eÂ²)*YÂ²_coefficient and full raw268 derivative; no nearby-large-family subtraction',
        source_scope='explicit fixed-H/interior8Q b tests beta=Tb(currentR4)b; fulln1+n3 images and both orderedinsertions, not solved samephase firstresponse yet',
        Haar_or_QNORM_or_e_or_family_statistics_factor_reapplied=False,
        coefficient_cell_and_cutoff_probes_are_numerical=True,
        signed_phase_step_reverses_future_derivative=False,
        cross_arm_birth_transmission_or_dual_invented=False,
        complete_physical_time_domain_relative_completion_overlap_or_LSZ_selected=False,
        source_correlator_covariance_or_physical_Pauli_value_selected=False,
        error_scope='binary64 actual-field coefficient-cell matrices and stable divided-difference/cutoffquadrature; Y4 analytic estimates use numerical norm/gap inputs and are not outward certificates; no temporal or continuum error bound')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('preserve prior applications')
    packet,arrays=evaluate();archive=deterministic_npz(arrays)
    if len(archive)>10*1024**2:raise ValueError('retain every array and split losslessly')
    args.output.mkdir(parents=True);(args.output/'primal_cell_heat.npz').write_bytes(archive)
    packet['archive']=dict(path='primal_cell_heat.npz',bytes=len(archive),sha256=sha256(archive).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(args.output/'primal_cell_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),receipt_bytes=len(raw),archive=packet['archive'])),flush=True)


if __name__=='__main__':main()
