"""Replay the joint finite descriptor and stable paired mean heat readout."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
from bhsm.interface.muon_native_mean_core_heat_target import corrected_even_y_paired_heat_cotangent,joint_heat_target_to_mean_descriptor
from bhsm.interface.muon_parent_mean_causal_descriptor import certified_sampled_mean_descriptor,implicit_mean_source_target_application,mean_descriptor_diagnostics

FIXED='artifacts/muon_native_product_factor_graph_20261010/run_1/product_factor_graph_and_heat.json'
FIXED_SHA='aac59f831b5e5cd328e352993427159ca1d4c89ebde25d1687e3a036b9510197'


def evaluate(*,time_steps=(32,64,128),precision_per_step=16):
    """Execute actual source-pair loads; no instantaneous inverse at a crossing."""
    response=retained_corrected_scalar_photon_response(ROOT);descriptor=certified_sampled_mean_descriptor(ROOT)
    if sha256((ROOT/FIXED).read_bytes()).hexdigest()!=FIXED_SHA:raise ValueError('frozen numerical cutoff probes changed')
    probes=json.loads((ROOT/FIXED).read_bytes())['parameter_family']['probes'];central=probes[1]['proper_time_or_cutoff']
    arrays={};targets={};target_refinement=[]
    for count in (5,9,17):
        row=corrected_even_y_paired_heat_cotangent(response,time_nodes=np.linspace(-.001,0,count),quadrature_order=4,
            parameter=central,divided_difference_order=64)
        targets[count]=row
        for name in ('normalized_P0_eigenvalues','normalized_P1','normalized_P2','normalized_LR_sign_grading',
                     'actual_FE_K0','actual_FE_Gram','actual_FE_K1','actual_FE_K2','actual_FE_LR_sign_grading','computed_generalized_eigenvectors','computed_eigenbasis_K0','computed_eigenbasis_Gram','weighted_raw228_Z0_Z1_Z2_norm_majorant_inputs',
                     'weighted_raw228_Y_fourth_majorant','coefficient_time_samples','response_time_samples'):
            arrays[f'target_nodes_{count}_{name}']=row[name]
        arrays[f'target_nodes_{count}_paired_raw228_load']=row['families']['middle_minus_light']['weighted_raw228_cotangent']
    for a,b in ((5,9),(9,17)):
        x=targets[a]['families']['middle_minus_light']['constant_raw228_cotangent'];y=targets[b]['families']['middle_minus_light']['constant_raw228_cotangent']
        target_refinement.append(dict(coarse_nodes=a,fine_nodes=b,absolute_norm_difference=float(np.linalg.norm(x-y)),
            relative_norm_difference=float(np.linalg.norm(x-y)/np.linalg.norm(y))))
    fine=targets[17];low=corrected_even_y_paired_heat_cotangent(response,time_nodes=np.linspace(-.001,0,17),quadrature_order=4,
        parameter=central,divided_difference_order=32)
    dd_error=float(np.linalg.norm(low['families']['middle_minus_light']['weighted_raw228_cotangent']-fine['families']['middle_minus_light']['weighted_raw228_cotangent']))
    binding=joint_heat_target_to_mean_descriptor(fine,descriptor['samples']);applications=[]
    for steps in time_steps:
        bits=max(384,precision_per_step*steps)
        print(json.dumps(dict(stage='joint_descriptor',time_steps=steps,precision_bits=bits)),flush=True)
        a=implicit_mean_source_target_application(descriptor,time_steps=steps,target_times=binding['target_times'],
            target_loads=binding['target_loads'],precision_bits=bits)
        if not a['exact_stored_forward_adjoint_intervals_overlap']:raise RuntimeError('exact-stored discrete readouts disagree')
        if a['exact_stored_target_entry_radius_upper']>1e-14:raise RuntimeError('exact-stored target arithmetic did not achieve meaningful precision')
        for name in ('time_grid','phase_values','midpoint_value_rate_algebraic','prescribed_wall_reactions','initial_advanced_adjoint'):
            arrays[f'steps_{steps}_{name}']=a[name]
        # Propagate the analytic target-tail majorant through the actual discrete readout.
        full_bounds=fine['weighted_raw228_Y_fourth_majorant'];P=descriptor['samples']['lift_to_full_mean']
        from bhsm.interface.muon_parent_mean_causal_action import mean_coordinate_lift
        lift=mean_coordinate_lift(descriptor['samples']['raw_gauge_labels'])['lift']@P
        reduced_bound=full_bounds@abs(lift);tail=np.zeros((8,8));n=descriptor['n']
        for t,b in zip(binding['target_times'],reduced_bound):
            k=min(max(np.searchsorted(a['time_grid'],t,side='right')-1,0),steps-1)
            theta=(t-a['time_grid'][k])/(a['time_grid'][k+1]-a['time_grid'][k])
            x=(1-theta)*a['phase_values'][k,:n]+theta*a['phase_values'][k+1,:n]
            eta=np.concatenate((x,a['midpoint_value_rate_algebraic'][k]),axis=0)
            tail+=np.einsum('i,iAB->AB',b,abs(eta))
        a['paired_target_Y_fourth_propagated_majorant_numeric']=tail
        a['paired_channel_trace']=float(np.trace(a['adjoint_target'][0]));a['paired_target_Frobenius_norm']=float(np.linalg.norm(a['adjoint_target']))
        a['time_steps']=steps
        applications.append({k:v for k,v in a.items() if k not in ('phase_values','midpoint_value_rate_algebraic','prescribed_wall_reactions','initial_advanced_adjoint','time_grid')})
    convergence=[]
    for a,b in zip(applications[:-1],applications[1:]):
        x=np.asarray(a['adjoint_target']);y=np.asarray(b['adjoint_target']);e=float(np.linalg.norm(x-y));q=float(np.linalg.norm(y))
        convergence.append(dict(coarse_steps=a['time_steps'],fine_steps=b['time_steps'],absolute_Frobenius_difference=e,
            relative_Frobenius_difference=e/q if q else None,coarse_channel_trace=a['paired_channel_trace'],fine_channel_trace=b['paired_channel_trace']))
    target_metadata={count:{k:v for k,v in row.items() if k not in ('families','normalized_P0_eigenvalues','normalized_P1','normalized_P2','normalized_LR_sign_grading',
        'actual_FE_K0','actual_FE_Gram','actual_FE_K1','actual_FE_K2','actual_FE_LR_sign_grading','computed_generalized_eigenvectors','computed_eigenbasis_K0','computed_eigenbasis_Gram',
        'weighted_raw228_Z0_Z1_Z2_norm_majorant_inputs','weighted_raw228_Y_fourth_majorant','coefficient_time_samples','response_time_samples')}
        for count,row in targets.items()}
    owners=[
        ('src/bhsm/interface/muon_parent_mean_causal_descriptor.py',('certified_sampled_mean_descriptor','mean_implicit_descriptor_step','implicit_mean_source_target_application','_arb_implicit_application')),
        ('src/bhsm/interface/muon_native_mean_core_heat_target.py',('corrected_joint_mean_heat_cotangent','corrected_even_y_paired_heat_cotangent','joint_heat_target_to_mean_descriptor')),
        ('src/bhsm/interface/muon_parent_mean_causal_action.py',('retained_mean_action_family','local_mean_action')),
        ('scripts/evaluate_muon_native_mean_causal_heat.py',('evaluate',)),
    ]
    packet=dict(classification='EVALUATED_JOINT_FINITE_IMPLICIT_MEAN_DESCRIPTOR_AND_STABLE_PAIRED_HEAT_TARGET',
        consumed_input_records=response['source_records']+[record(FIXED),record(descriptor['samples']['action_samples_path'])],
        source_records=[record(p,s) for p,s in owners],cutoff_probe=probes[1],paired_target_metadata=target_metadata,
        target_mesh_refinement=target_refinement,divided_difference_32_to_64_absolute_target_norm_difference=dd_error,
        descriptor_applications=applications,temporal_refinement=convergence,instantaneous_descriptor_diagnostics=mean_descriptor_diagnostics(descriptor),
        scalar_only_inverse_used=False,instantaneous_saddle_inverse_across_crossing_used=False,
        source='actual combined Maxwell+intrinsic-H D³S on the retained corrected radial response; raw betaPhoton eight-by-eight ordering',
        source_scope='outgoing branch24 backward numerical germ, compact affine source pulse; omitted angular geometry first responses are not asserted zero',
        prescribed_wall_condition='all20 second parent wall traces zero for this affine Dirichlet source; all20 reaction outputs retained',
        finite_native_readout='n0 positive-Hilbert fixed product core Tr E1(cP); partial mean contact, no statistics/charge factor or supertrace applied',
        paired_family_sign='middle minus light, formed from the shared even-Y target before the joint adjoint',
        continuous_causal_interval_regularity=False,physical_E0_stop_reset_or_birth_domain_bound=False,
        continuous_temporal_error_enclosed=False,producer_interpolation_or_rounding_error_enclosed=False,
        complete_genuine_source_jet_or_native_Pauli_evaluated=False,
        array_records={k:array_record(v) for k,v in arrays.items()})
    return serial(packet),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--steps',type=int,nargs='+',default=[32,64,128]);p.add_argument('--precision-per-step',type=int,default=16)
    args=p.parse_args();packet,arrays=evaluate(time_steps=tuple(args.steps),precision_per_step=args.precision_per_step)
    args.output.mkdir(parents=True,exist_ok=True)
    # One archive per time mesh preserves each complete phase below the artifact cap.
    groups={}
    for name,value in arrays.items():groups.setdefault(name.split('_')[1] if name.startswith('steps_') else 'targets',{})[name]=value
    records=[]
    for key,group in groups.items():
        data=deterministic_npz(group);name=f'mean_causal_{key}.npz'
        if len(data)>10*1024**2:raise ValueError('complete phase archive exceeds retained artifact cap; split losslessly')
        (args.output/name).write_bytes(data);records.append(dict(path=name,bytes=len(data),sha256=sha256(data).hexdigest()))
    packet['matrix_archives']=records
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(args.output/'mean_causal_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_bytes=len(raw),receipt_sha256=sha256(raw).hexdigest(),archives=records),sort_keys=True))


if __name__=='__main__':main()
