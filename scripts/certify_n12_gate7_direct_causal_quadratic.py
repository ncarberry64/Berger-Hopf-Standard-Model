"""Compose paired direct physical local sources through matching frozen maps."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_direct_physical_quadratic_sources as producer
from bhsm.interface import direct_causal_quadratic as causal

local=producer.local
THEORY=ROOT/'theory/n12_gate7_direct_causal_quadratic.md'
ALGORITHM='DIRECT_PHYSICAL_FIXED_FRAME_CAUSAL_QUADRATIC_SPARSE_SIGNED_ARB512_V1'


def merge_raw(inputs,raw,additional):
    """Verify newly encountered files once; common files must retain their hash."""
    if any(name in raw and raw[name]!=digest for name,digest in additional.items()):
        raise RuntimeError('inconsistent shared quadratic source fingerprint')
    new={name:digest for name,digest in additional.items() if name not in raw}
    local.residual.merge_verified_raw_sources(inputs,raw,new)


def indices_or_all(indices):
    values=list(range(370)) if indices is None else list(indices)
    if not values or len(set(values))!=len(values) or any(type(i) is not int or not 0<=i<370 for i in values):
        raise ValueError('distinct intervals in 0..369 required')
    return sorted(values)


def result_path(indices):
    values=indices_or_all(indices)
    if values==list(range(370)):suffix='FULL'
    else:
        suffix='SELECTED_'+('_'.join(f'{i:03d}' for i in values) if len(values)<=6
                            else hashlib.sha256(json.dumps(values).encode()).hexdigest()[:16])
    return ROOT/f'artifacts/flagship_integration/BHSM_N12_GATE7_{suffix}_DIRECT_CAUSAL_QUADRATIC.json'


def verify_manifest(index,manifest,receipt,path):
    expected={local.df.file_key(path.parent/f'{family}_{pair}.{ext}')
        for family in ('LL','LT','TT') for pair in ('00','01','10','11') for ext in ('json','npz')}
    if (manifest.get('algorithm')!=producer.ALGORITHM or manifest.get('interval')!=index
            or manifest.get('complete_local_source_blocks') is not True or set(manifest.get('files',{}))!=expected
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('manifest_SHA256')!=local.df.values.sha(path)
            or path.read_bytes()!=producer.hessian.encoded(manifest)):
        raise RuntimeError('complete independently reproduced local quadratic sources required')


def verify_record(index,family,pair,record,path,base):
    source=dict(inputs=record.get('inputs'),raw_inputs=record.get('raw_input_SHA256'),
        axes_SHA256=base['axes_SHA256'],causal_maps_SHA256=base['causal_maps_SHA256'])
    expected=producer.metadata(index,family,pair,source)
    expected['data_SHA256']=local.df.values.sha(path)
    if (record!=expected or not isinstance(source['inputs'],dict) or not isinstance(source['raw_inputs'],dict)
            or path.with_suffix('.json').read_bytes()!=producer.hessian.encoded(record)):
        raise RuntimeError('local source record differs from the verified common operands')
    for code in (Path(producer.__file__),producer.THEORY,Path(producer.quadratic.__file__),Path(producer.second.__file__)):
        if source['raw_inputs'].get(local.df.file_key(code))!=local.df.values.sha(code):
            raise RuntimeError('local source implementation binding missing or changed')
    for stage,i in (('endpoint',index),('midpoint',index),('endpoint',index+1)):
        directory=producer.hessian.point_directory(stage,i)
        if any(local.df.file_key(directory/name) not in source['raw_inputs'] for name in ('manifest.json','reproduction.json')):
            raise RuntimeError('local source lacks paired physical Hessian dependencies')
    return source


def load_inputs(indices):
    base,inputs,_,_=local.residual.load_foundation();raw={};paths={}
    for index in indices:
        directory=producer.WORK/f'interval_{index:03d}'
        manifest_path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
        manifest=json.loads(manifest_path.read_text());receipt=json.loads(receipt_path.read_text())
        verify_manifest(index,manifest,receipt,manifest_path)
        additional=dict(manifest['files'])
        for path in (manifest_path,receipt_path):additional[local.df.file_key(path)]=local.df.values.sha(path)
        merge_raw(inputs,raw,additional)
        interval_source=None
        for family in ('LL','LT','TT'):
            for pair in ('00','01','10','11'):
                path=directory/f'{family}_{pair}.npz'
                record=json.loads(path.with_suffix('.json').read_text())
                source=verify_record(index,family,pair,record,path,base)
                if interval_source is not None and source!=interval_source:
                    raise RuntimeError('local source blocks have inconsistent input bindings')
                interval_source=source;paths[index,family,pair]=path
        local.residual.merge(inputs,interval_source['inputs'])
        merge_raw(inputs,raw,interval_source['raw_inputs'])
    with np.load(local.residual.center.DATA,allow_pickle=False) as arrays:
        maps=arrays['causal_maps_center'].copy()
    axes=local.residual.center.component._load_axes()
    array_hash=local.residual.foundation.maps._array_hash
    if (maps.shape!=(370,74,74) or axes.shape!=(371,74)
            or array_hash(maps)!=base['causal_maps_SHA256'] or array_hash(axes)!=base['axes_SHA256']):
        raise RuntimeError('complete common frozen causal maps and axes required')
    code_paths=(Path(__file__),THEORY,Path(producer.__file__),Path(causal.__file__),
        Path(causal._matrix.__code__.co_filename),Path(causal._squared_norm.__code__.co_filename),
        Path(causal._float_upper.__code__.co_filename),Path(causal.transport_local_errors.__code__.co_filename),
        Path(causal.combine_stored_causal_errors.__code__.co_filename),Path(local.df.values.hs.__file__))
    additional={local.df.file_key(path):local.df.values.sha(path) for path in code_paths}
    merge_raw(inputs,raw,additional)
    local.residual.foundation.coordinate._verified_inputs(dict(inputs=inputs))
    local.df.values.verify_binding(dict(files=raw))
    return dict(base=base,inputs=inputs,raw_inputs=raw,paths=paths,maps=maps,axes=axes)


def read_interval(source,index,family):
    blocks={};shape=(74,dict(LL=1,LT=74,TT=5476)[family])
    for pair in ('00','01','10','11'):
        with np.load(source['paths'][index,family,pair],allow_pickle=False) as arrays:
            if set(arrays.files)!={'Q_mid_q','Q_rad_q'} or any(arrays[k].shape!=shape for k in arrays.files):
                raise RuntimeError('complete rational source tensor required')
            blocks[pair]=local.df.values.hs.restore_balls(arrays['Q_mid_q'],arrays['Q_rad_q'])
    return blocks


def build_payload(indices=None,progress=None):
    selected=indices_or_all(indices);previous=ctx.prec;ctx.prec=512
    try:
        source=load_inputs(selected);families={}
        # Source loaders restore rational balls at the active 512-bit precision.
        ctx.prec=512
        for family in ('LL','LT','TT'):
            report=(lambda atoms,start,count:progress(family,atoms,start,count)) if progress else None
            families[family]=causal.bound_causal_quadratic_family(source['maps'],source['axes'],
                lambda i:read_interval(source,i,family),family,source['base']['frozen_map_perturbation_gain_upper'],
                active_intervals=selected,progress=report)
            if families[family]['fixed_axis_projection_norms_upper']!=source['base']['fixed_axis_projection_norms_upper']:
                raise RuntimeError('quadratic projection norms differ from the frozen foundation')
        local.residual.foundation.coordinate._verified_inputs(dict(inputs=source['inputs']))
        local.df.values.verify_binding(dict(files=source['raw_inputs']))
        complete=selected==list(range(370))
        return dict(algorithm=ALGORITHM,scope=('SELECTED_BRANCH_FIXED_FRAME_FINITE_HISTORY_QUADRATIC_BOUND' if complete
            else 'ISOLATED_ADDITIVE_PHYSICAL_POINT_CAUSAL_QUADRATIC_COMPONENT'),
            coverage=dict(active_intervals=selected,interval_count=len(selected),total_intervals=370,complete=complete),
            inputs=source['inputs'],raw_input_SHA256=source['raw_inputs'],
            input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',raw_input_hash_convention='SHA256_EXACT_FILE_BYTES',
            causal_maps_SHA256=source['base']['causal_maps_SHA256'],axes_SHA256=source['base']['axes_SHA256'],
            families=families,quadratic_coefficients_upper={key:value['frozen_inverse_quadratic_coefficients_upper'] for key,value in families.items()},
            polynomial_convention='LL*rL^2+2*LT*rL*rT+TT*rT^2',validation_passed=True,
            claim_boundary=dict(complete_point_source_causal_composition=complete,
                independent_longitudinal_amplitudes=True,actual_physical_HS_midpoints_used=True,
                physical_branch_continuation_certified=False,state_dependent_frame_derivatives_enclosed=False,
                neighborhood_remainder_enclosed=False,physical_quotient_identified=False,
                physical_Z2_recertified=False,physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False))
    finally:ctx.prec=previous


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--intervals')
    parser.add_argument('--recompute',action='store_true');args=parser.parse_args()
    indices=[int(i) for i in args.intervals.split(',')] if args.intervals is not None else None
    path=result_path(indices);receipt=path.with_suffix('.reproduction.json')
    if args.recompute and not path.exists():raise RuntimeError('independent repeat requires a prior result')
    if path.exists() and not args.recompute:raise RuntimeError('result exists; use --recompute')
    if args.recompute and receipt.exists():receipt.replace(path.with_suffix(f'.reproduction.before_attempt_{time.time_ns()}.json'))
    def progress(family,atoms,start,count):
        if atoms==1 or atoms%10==0:print(json.dumps(dict(family=family,atoms=atoms,input_node=start,total_nodes=count)),flush=True)
    payload=build_payload(indices,progress);data=producer.hessian.encoded(payload)
    candidate=path.with_suffix(f'.candidate_{time.time_ns()}.json');candidate.write_bytes(data)
    if args.recompute:
        if path.read_bytes()!=data:raise ArithmeticError('independent causal quadratic result differs; both preserved')
        candidate.unlink();producer.hessian.write_json(receipt,dict(byte_identical=True,independent_recomputation=True,
            result_SHA256=local.df.values.sha(path),FULL_BHSM_COMPLETE=False))
    else:candidate.replace(path)
    print(json.dumps(dict(coverage=payload['coverage'],coefficients=payload['quadratic_coefficients_upper'],
        reproduced=args.recompute,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()
