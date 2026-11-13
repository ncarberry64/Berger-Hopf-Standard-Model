"""Single-mesh exact-stored mean phase with outward binary64 export errors."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_parent_mean_causal_descriptor import certified_sampled_mean_descriptor
from bhsm.interface.muon_native_mean_core_heat_target import joint_heat_target_to_mean_descriptor
from bhsm.interface.muon_native_mean_phase_export import implicit_mean_phase_export,RETAINED_DESCRIPTOR_SOURCE_SHA256

TARGET='artifacts/muon_native_mean_causal_heat_20261010/target_coefficients_run_5'
TARGET_HASHES={'paired_target_coefficients.json':'45b249f5b6f3aa5710478f8fbd9ba5ce67bbbc3cdf03a2880cbfd306f8cef7c8',
    'paired_target_coefficients.npz':'6db9b664f6f18ac8763186ed15cdd749ce13ea844db2060af434869aec75d800'}


def evaluate(*,time_steps,precision_bits):
    path='src/bhsm/interface/muon_parent_mean_causal_descriptor.py'
    if sha256((ROOT/path).read_bytes()).hexdigest()!=RETAINED_DESCRIPTOR_SOURCE_SHA256:
        raise ValueError('retained same-step descriptor source changed')
    refs=[]
    for name,digest in TARGET_HASHES.items():
        if sha256((ROOT/TARGET/name).read_bytes()).hexdigest()!=digest:raise ValueError('frozen target coefficient input changed')
        refs.append(record(TARGET+'/'+name))
    descriptor=certified_sampled_mean_descriptor(ROOT)
    with np.load(ROOT/TARGET/'paired_target_coefficients.npz',allow_pickle=False) as a:
        target=dict(response_time_samples=a['response_time_samples'],families={'middle_minus_light':dict(weighted_raw228_cotangent=a['paired_raw228_heat_target'])})
    binding=joint_heat_target_to_mean_descriptor(target,descriptor['samples'])
    applied=implicit_mean_phase_export(descriptor,time_steps=time_steps,target_times=binding['target_times'],target_loads=binding['target_loads'],precision_bits=precision_bits)
    if not applied['exact_stored_forward_adjoint_intervals_overlap'] or applied['exact_stored_target_entry_radius_upper']>1e-14:
        raise RuntimeError('finite descriptor readout arithmetic did not achieve useful precision')
    keys=('time_grid','phase_values','midpoint_value_rate_algebraic','phase_export_entry_error_bounds',
        'midpoint_export_entry_error_bounds','initial_advanced_adjoint_export_entry_error_bounds','prescribed_wall_reactions','initial_advanced_adjoint')
    arrays={k:applied[k] for k in keys};arrays.update(target_times=binding['target_times'],weighted_reduced_target_loads=binding['target_loads'])
    receipt={k:v for k,v in applied.items() if k not in keys}
    receipt.update(classification='EVALUATED_EXACT_STORED_FINITE_DESCRIPTOR_PHASE_EXPORT_WITH_ENTRYWISE_ERRORS',
        time_steps=time_steps,paired_channel_trace=float(np.trace(applied['adjoint_target'][0])),
        consumed_input_records=refs+[record(descriptor['samples']['action_samples_path'])],
        source_records=[record('src/bhsm/interface/muon_native_mean_phase_export.py',('implicit_mean_phase_export','_arb_export_application')),
            record(path,('certified_sampled_mean_descriptor','mean_implicit_descriptor_step')),
            record('src/bhsm/interface/muon_native_mean_core_heat_target.py',('joint_heat_target_to_mean_descriptor',)),
            record('scripts/evaluate_muon_native_mean_phase_export.py',('evaluate',))],
        temporal_convergence_or_continuous_causal_regular_interval_certified=False,
        actual_128_crossing_is_not_removed=True,
        weighted_raw228_target_scope='same frozen even-Y finite-core target, middle-minus-light formed before the joint adjoint',
        source_scope='actual retained outgoing24 finite-germ D3S eight-source pair; not selected C1/E0/stop',
        array_records={k:array_record(v) for k,v in arrays.items()})
    return serial(receipt),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--steps',type=int,required=True);p.add_argument('--precision-bits',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('preserve previous finite applications')
    packet,arrays=evaluate(time_steps=args.steps,precision_bits=args.precision_bits)
    groups={'phase':{k:arrays[k] for k in ('time_grid','phase_values')},
        'midpoint':{k:arrays[k] for k in ('midpoint_value_rate_algebraic','prescribed_wall_reactions')},
        'phase_errors':{'phase_export_entry_error_bounds':arrays['phase_export_entry_error_bounds']},
        'midpoint_errors':{'midpoint_export_entry_error_bounds':arrays['midpoint_export_entry_error_bounds']},
        'readout':{k:arrays[k] for k in ('target_times','weighted_reduced_target_loads','initial_advanced_adjoint','initial_advanced_adjoint_export_entry_error_bounds')}}
    records=[];args.output.mkdir(parents=True)
    for group,values in groups.items():
        raw=deterministic_npz(values)
        if len(raw)>10*1024**2:raise ValueError('complete archive exceeds cap; split without loss')
        name=f'mean_causal_{args.steps}_{group}.npz';(args.output/name).write_bytes(raw)
        records.append(dict(path=name,bytes=len(raw),sha256=sha256(raw).hexdigest()))
    packet['matrix_archives']=records;raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (args.output/'mean_phase_export.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),paired_trace=packet['paired_channel_trace'],
        phase_export_error_upper=packet['exact_stored_phase_export_entry_error_upper'],
        midpoint_export_error_upper=packet['exact_stored_midpoint_export_entry_error_upper'],archives=records),sort_keys=True))


if __name__=='__main__':main()
