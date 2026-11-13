"""Resume the saved D5 family on an independently checked finite domain."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.interpolate import BarycentricInterpolator
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups,save_groups,pin,owners
from bhsm.interface.retained_response.finite_time_response import write_npz
from bhsm.interface.muon_d5_temporal_bulk_refinement import (
    solve_refined_incoming_bulk_family,evaluate_refined_field,time_evaluation_matrix,independent_factor_residuals)
from bhsm.interface.muon_d5_independent_residuals import (
    SavedOneStepPolynomialField,independent_residual_application,original_d5_coefficient_callback)

def dump(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def verify_reuse_pins(pins):
    """Permit only proved byte-level, non-numerical consumer compatibility."""
    receipt={}
    for rel,expected in pins.items():
        path=ROOT/rel;current=path.read_bytes()
        if sha256(current).hexdigest()==expected:continue
        if path.suffix not in ('.py','.json','.md','.txt') and path.name!='.gitattributes':
            raise ValueError('binary numerical input changed: '+rel)
        lf=current.replace(b'\r\n',b'\n');variants=[lf,lf.replace(b'\n',b'\r\n')]
        reason='line-ending normalization only'
        if rel=='src/bhsm/interface/muon_d5_independent_residuals.py':
            old=lf.replace(b'    history.original_phase_operands = operands\n',b'')
            variants.extend([old,old.replace(b'\n',b'\r\n')])
            reason='line-ending normalization and exposure of unchanged saved operands to new child consumer; numerical methods unchanged'
        if not any(sha256(v).hexdigest()==expected for v in variants):
            raise ValueError('saved numerical input or owner changed: '+rel)
        receipt[rel]=dict(saved_sha256=expected,current_sha256=pin(path),verified_change=reason)
    return receipt

def old_application():
    p=ROOT/'artifacts/muon_d5_complement_bulk_response_20261019/run_4'
    record=json.loads((p/'core_result.json').read_bytes())
    return load_groups(p,record['archives']),{(p/'core_result.json').relative_to(ROOT).as_posix():pin(p/'core_result.json'),
        **{(p/name).relative_to(ROOT).as_posix():md['sha256'] for name,md in record['archives'].items()}}

def inputs():
    p=ROOT/'artifacts/muon_formed_event_domain_application_20261019/run_2/formed_event_domain_application.npz'
    with np.load(p,allow_pickle=False) as z:cache={k:z[k].copy(order='K') for k in z.files}
    folder=ROOT/'artifacts/muon_retained_response_20261018/inputs'
    md=json.loads((folder/'history_metadata.json').read_bytes())
    histories={}
    for side in ('incoming','outgoing'):
        with np.load(folder/(side+'_history.npz'),allow_pickle=False) as z:
            samples=md['sides'][side]
            histories[side]=(np.array([s['time'] for s in samples]),
                np.array([z[s['label']+'_raw_fields'] for s in samples]),
                np.array([z[s['label']+'_raw_coordinate_time_derivative'] for s in samples]))
    pins={q.relative_to(ROOT).as_posix():pin(q) for q in (p,folder/'history_metadata.json',
        folder/'incoming_history.npz',folder/'outgoing_history.npz')}
    return cache,histories,pins

def run(output,*,temporal_count=10,radial_steps=2,radial_order=5,resume=False,core_only=False,reuse_core_from=None,compare_core6=None,reuse_consumer_from=None):
    output=Path(output).resolve()
    if not resume:
        if output.exists():raise FileExistsError('preserve every prior application')
        output.mkdir(parents=True)
    old,oldpins=old_application();cache,histories,pins=inputs();pins.update(oldpins)
    # Recovered original callbacks are loaded by a dedicated pinned adapter.
    from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
    history,receipt=recovered_export_history(ROOT,'incoming',*histories['incoming'])
    child_history,childreceipt=recovered_export_history(ROOT,'outgoing',*histories['outgoing'])
    pins.update(receipt['input_sha256']);pins.update(childreceipt['input_sha256'])
    cp=output/'core_result.json'
    reuse_compatibility={}
    if resume or reuse_core_from is not None:
        source=output if resume else Path(reuse_core_from)
        core=json.loads((source/'core_result.json').read_bytes())
        reuse_compatibility=verify_reuse_pins(core['input_sha256'])
        arrays=load_groups(source,core['archives'])
        if reuse_core_from is not None:
            archives=save_groups(output,arrays,'refined')
            if archives!=core['archives']:raise ValueError('rematerialized core bytes differ')
            cp.write_bytes((source/'core_result.json').read_bytes())
    else:
        arrays,report,history=solve_refined_incoming_bulk_family(*histories['incoming'],saved_endpoint=cache,
            temporal_count=temporal_count,radial_steps=radial_steps,radial_order=radial_order,
            saved_application=old,history=history)
        core=dict(schema='bhsm.d5-valid-domain-core.v1',parent_head='e0d604eb84cec54502b25bb1f699ac2c62143fc9',
            input_sha256={**pins,**owners()},original_history_receipt=receipt,child_history_receipt=childreceipt,
            report=report,archives=save_groups(output,arrays,'refined'))
        dump(cp,core)
        print(json.dumps(dict(stage='REFINED_CORE_SAVED',sha256=pin(cp),report=report)),flush=True)
    if core_only:return core
    if (output/'result.json').exists():raise FileExistsError('preserve completed consumer')
    times=old['times'];width=float(old['computational_strip_width']);wall=float(old['radial_nodes'][0])
    tf=np.array([.079,.413,.913]);rf=np.array([.043,.319,.947])
    independent_times=times[0]+(times[-1]-times[0])*tf
    independent_radii=wall-width*rf
    points=np.array([(t,r) for t in independent_times for r in independent_radii])
    # Also retain old endpoint-time checks and radial Gauss stages separately.
    nodal_points=np.array([(t,r) for t in times for r in independent_radii])
    legacy=lambda t:(time_evaluation_matrix(times,[t])[0]@histories['incoming'][1],
        time_evaluation_matrix(times,[t])[0]@histories['incoming'][2])
    coef_old=original_d5_coefficient_callback(legacy,sheet_orientation=-1)
    coef=original_d5_coefficient_callback(lambda t:(history.value(t)[0],history.source(t)[0]),sheet_orientation=-1,
        gauge_basis_evaluate=history.gauge_basis)
    reports={};diagnostics={}
    factor_values,factor_report=independent_factor_residuals(arrays,history,points)
    reports['full_unit_fundamental']=factor_report
    diagnostics.update({'factor_'+k:v for k,v in factor_values.items()})
    comparison=None;comparison_pins={}
    if compare_core6 is not None:
        comparison_path=Path(compare_core6).resolve();comparison_record=json.loads((comparison_path/'core_result.json').read_bytes())
        comparison=load_groups(comparison_path,comparison_record['archives'])
        if len(comparison['times'])!=6:raise ValueError('explicit same-operator six-time comparison required')
        for key in ('radial_boundaries','radial_order','amplitude_times'):
            if not np.array_equal(comparison[key],arrays[key]):raise ValueError('temporal comparison changed '+key)
        reuse_compatibility.update(verify_reuse_pins(comparison_record['input_sha256']))
        comparison_pins={(comparison_path/'core_result.json').relative_to(ROOT).as_posix():pin(comparison_path/'core_result.json'),
            **{(comparison_path/name).relative_to(ROOT).as_posix():md['sha256'] for name,md in comparison_record['archives'].items()}}
    for label in ('minus_LR','minus_RL'):
        saved=SavedOneStepPolynomialField(old,old,label)
        # SciPy randomizes weight-product ordering by default. This fixes
        # numerical interpolation arithmetic, not a physical random state.
        saved.time_basis=BarycentricInterpolator((times-times[0])/(times[-1]-times[0]),np.eye(6),axis=0,rng=465)
        refined=lambda t,r:evaluate_refined_field(arrays,label,[t],[r])
        def newfield(t,r):return {k:a[0,0] for k,a in refined(t,r).items()}
        for prefix,field,coeff,probes in (
            ('before_independent',saved,coef_old,points),('before_original_callback',saved,coef,points),
            ('before_old_times',saved,coef_old,nodal_points),('after_independent',newfield,coef,points),
            ('after_old_times',newfield,coef,nodal_points)):
            values,r=independent_residual_application(field,coeff,probes)
            reports[label+'_'+prefix]=r
            for key in ('points','strong','strong_source'):
                diagnostics[label+'_'+prefix+'_'+key]=values[key]
        reports[label+'_saved_dense_reconstruction']=saved.saved_derivative_checks()
        if comparison is not None:
            def sixfield(t,r):return {k:a[0,0] for k,a in evaluate_refined_field(comparison,label,[t],[r]).items()}
            values,r=independent_residual_application(sixfield,coef,points)
            reports[label+'_same_operator_temporal6']=r
            for key in ('points','strong','strong_source'):diagnostics[label+'_same_operator_temporal6_'+key]=values[key]
    path=output/'independent_rows.npz';write_npz(path,diagnostics)
    from bhsm.interface.muon_d5_refined_domain_application import consume_refined_domain_family
    child_folder=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/domain_core'
    child_record=json.loads((child_folder/'result.json').read_bytes())
    reuse_compatibility.update(verify_reuse_pins(child_record['input_sha256']))
    child_path=child_folder/'arrays.npz'
    if pin(child_path)!=child_record['arrays']['sha256']:raise ValueError('saved child operator application changed')
    with np.load(child_path,allow_pickle=False) as z:child_arrays={k:z[k].copy(order='K') for k in z.files}
    child_pins={p.relative_to(ROOT).as_posix():pin(p) for p in (child_folder/'result.json',child_path)}
    if reuse_consumer_from is None:
        returned,consumed=consume_refined_domain_family(arrays,history,child_history,
            child_application=(child_arrays,child_record['report']))
    else:
        consumer_folder=Path(reuse_consumer_from).resolve()
        consumer_record=json.loads((consumer_folder/'result.json').read_bytes())
        if consumer_record['core_record_sha256']!=pin(cp):raise ValueError('consumer transfer input changed')
        if consumer_record['child_record_sha256']!=pin(child_folder/'result.json'):raise ValueError('consumer child input changed')
        verify_reuse_pins(consumer_record['input_sha256'])
        returned=load_groups(consumer_folder,consumer_record['archives']);consumed=consumer_record['report']
        child_pins.update({(consumer_folder/'result.json').relative_to(ROOT).as_posix():pin(consumer_folder/'result.json'),
            **{(consumer_folder/name).relative_to(ROOT).as_posix():md['sha256'] for name,md in consumer_record['archives'].items()}})
    archives=save_groups(output,returned,'returned')
    result=dict(schema='bhsm.d5-valid-domain-application.v1',parent_head=core['parent_head'],
        core_record_sha256=pin(cp),core_report=core['report'],input_sha256={**core['input_sha256'],**comparison_pins,**child_pins,**owners(),
            Path(__file__).relative_to(ROOT).as_posix():pin(Path(__file__))},
        saved_core_source_compatibility=reuse_compatibility,
        independent_checks=reports,independent_rows=dict(sha256=pin(path),bytes=path.stat().st_size),
        consumed=consumed,archives=archives,physical_guard=2e-10,physical_admission=False,
        NEXT_OPERAND='control remaining independent D5/source discretization error; determine U_R, physical outer and independent normal data in the joint child/event/formation equations; no physical closure from the finite response family')
    dump(output/'result.json',result)
    print(json.dumps(dict(stage='VALID_DOMAIN_APPLICATION_SAVED',sha256=pin(output/'result.json'),checks=reports,consumed=consumed)),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--temporal-count',type=int,default=10);p.add_argument('--radial-steps',type=int,default=2)
    p.add_argument('--radial-order',type=int,default=5);p.add_argument('--resume',action='store_true')
    p.add_argument('--core-only',action='store_true')
    p.add_argument('--reuse-core-from',type=Path)
    p.add_argument('--compare-core6',type=Path)
    p.add_argument('--reuse-consumer-from',type=Path)
    a=p.parse_args();run(a.output,temporal_count=a.temporal_count,radial_steps=a.radial_steps,
        radial_order=a.radial_order,resume=a.resume,core_only=a.core_only,reuse_core_from=a.reuse_core_from,
        compare_core6=a.compare_core6,reuse_consumer_from=a.reuse_consumer_from)
