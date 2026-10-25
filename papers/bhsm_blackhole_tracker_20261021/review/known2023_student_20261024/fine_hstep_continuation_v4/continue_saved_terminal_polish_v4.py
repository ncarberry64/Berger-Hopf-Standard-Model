"""Fixed fine-Hstep continuation of all32 frozen terminal states; no new model."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def binding(args):
    raw=args.freeze.read_bytes()
    if sha(raw)!=args.freeze_sha256:raise ValueError('Exact prospective diagnostic freeze required')
    freeze=json.loads(raw)
    for row in freeze['source_files']+freeze['bound_artifacts']:
        raw=Path(row['path']).read_bytes()
        if len(raw)!=row['bytes']or sha(raw)!=row['sha256']:raise ValueError('Source/data/state binding changed: '+row['path'])
    admission_raw=args.admission.read_bytes();admission=json.loads(admission_raw)
    if sha(admission_raw)!=args.admission_sha256 or admission.get('schema')!='bhsm.known2023.fixed_terminal_polish_execution_admission.v1'or admission.get('execution_admitted')is not True or admission.get('prospective_freeze_sha256')!=args.freeze_sha256:
        raise ValueError('Separate root diagnostic execution admission required')
    peer=admission['independent_source_gate']
    if sha(Path(peer['path']).read_bytes())!=peer['sha256']:raise ValueError('Independent source gate differs')
    if freeze['state_count']!=32 or freeze['difference_step']!=.0000003 or freeze['polish_iterations']!=16 or freeze['score_tolerance']!=.02 or freeze['max_scaled_step']!=1.:raise ValueError('Unreviewed state/polish configuration')
    if len(freeze['campaigns'])!=2 or {c['purpose']for c in freeze['campaigns']}!={'AUTHENTIC2023','ACTUAL_CADENCE_CONTROL'}:raise ValueError('Both complete frozen campaigns required')
    for campaign in freeze['campaigns']:
        if len(campaign['states'])!=16 or [s['start_index']for s in campaign['states']]!=list(range(16))or any(type(s['start_index'])is not int for s in campaign['states']):raise ValueError('All16 unique ordered original starts required')
    return freeze

def worker(args,freeze,initial):
    import numpy as np
    import scipy
    import astropy
    from known2023_student_model_v1 import Known2023StudentModel
    from periodic_chart_v1 import native_from_chart
    from bounded_trust_polish_v1 import polish_score
    runtime={'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__,'astropy':astropy.__version__}
    if runtime!=freeze['runtime']:raise ValueError('Exact frozen numerical runtime required')
    models={};states=[];calls=0;records=[];global_failure=None;endpoint_trials={c['purpose']:[]for c in freeze['campaigns']}
    for campaign in freeze['campaigns']:
        for item in campaign['states']:states.append((campaign,item))
    with(args.output/'ALL_POSTPOLISH_CALLS_v4.jsonl').open('x',encoding='utf-8',newline='\n')as stream:
        audit=JournalLatch(stream,freeze['journal_max_bytes'])
        for campaign,item in states:
            started=time.monotonic();identity={'purpose':campaign['purpose'],'start_index':item['start_index'],'original_terminal_sha256':item['sha256']};record=dict(identity,status='NOT_EVALUATED',post_endpoint_numerically_eligible=False)
            def guard():
                if global_failure is not None:raise RuntimeError(global_failure)
                audit.before_model_call()
                if time.monotonic()-initial>=freeze['worker_seconds']:raise TimeoutError('Whole continuation budget')
                if time.monotonic()-started>=freeze['state_seconds']:raise TimeoutError('Per-state continuation budget')
                if calls>=freeze['maximum_model_calls']:raise RuntimeError('Frozen model-call budget')
            try:
                guard();purpose=campaign['purpose']
                if purpose not in models:
                    raw=Path(campaign['input']['path']).read_bytes();registry=load(campaign['registry']['path'])if campaign.get('registry')else{}
                    models[purpose]=Known2023StudentModel(raw,purpose=purpose,expected_sha256=campaign['input']['sha256'],core_path=freeze['core_path'],student_directory=freeze['student_directory'],control_registry=registry,numerical_time_origin=freeze['numerical_time_origin_jd_tdb'],angular_reference=freeze['angular_reference_jd_tdb'])
                model=models[purpose];model.verify_snapshot();original=load(item['path'])
                if original['start_index']!=item['start_index']or original['phase']!='GRADIENT_TRUST_POLISH'or original['status']!='RETURNED':raise ValueError('Exact complete original v3 terminal required')
                center=original['chart_center_angle_rad'];state=np.asarray(original['chart_state'],dtype=float);scales=model.scales;zlo=model.lower/scales;zhi=model.upper/scales
                record.update(original_full_scaled_projected_score=original['full_scaled_projected_score'],original_deviance=original['deviance'],original_numerically_eligible=original['numerically_eligible'],original_chart_state=state,chart_center_angle_rad=center)
                def evaluate(point,details=False):
                    nonlocal calls
                    guard()
                    # Preserve the exact v3 callback scale round-trip/face mapping.
                    z=np.asarray(point,dtype=float)/scales;chart=z*scales
                    for j in range(len(chart)):
                        if j==3:continue
                        if z[j]==zlo[j]:chart[j]=model.lower[j]
                        elif z[j]==zhi[j]:chart[j]=model.upper[j]
                    native=native_from_chart(chart,center,model.lower,model.upper);calls+=1
                    try:value=model.evaluate(native,details=details)
                    except Exception as error:
                        audit.append(dict(identity,event='MODEL_CALL_FAILED',call=calls,requested_chart_state=point,actual_chart_state=chart,error_type=type(error).__name__,error=str(error)));raise
                    fullg=np.asarray(value['gradient'])*scales;projected=fullg.copy()
                    for j,g in enumerate(fullg):
                        if j!=3 and((native[j]==model.lower[j]and g>0)or(native[j]==model.upper[j]and g<0)):projected[j]=0.
                    description=dict(identity,event='MODEL_CALL',call=calls,requested_chart_state=point,actual_chart_state=chart,physical_state=native,deviance=value['negative_two_log_likelihood'],gradient=value['gradient'],full_scaled_projected_score=float(np.max(abs(projected))),linear_rank=value['linear_profile_rank'],linear_identified=value['linear_profile_identified'],linear_KKT_score=value['linear_profile_projected_score'],feature_knot_ids=value['feature_knot_source_ids'])
                    endpoint_trials[purpose].append({'call':calls,'deviance':description['deviance']})
                    audit.append(description)
                    return value,chart,native,description['full_scaled_projected_score']
                def callback(point):
                    value,_,_,_=evaluate(point)
                    return value['negative_two_log_likelihood'],(np.asarray(value['gradient'])*scales)/scales
                lo,hi=model.lower.copy(),model.upper.copy();lo[3],hi[3]=-np.inf,np.inf
                polish=polish_score(callback,state,lo,hi,scales,max_iterations=16,score_tolerance=.02,difference_step=.0000003,max_scaled_step=1.)
                detail,chart,native,score=evaluate(polish['state'],details=True)
                eligible=score<=.02 and detail['linear_profile_identified']and not detail['feature_knot_source_ids']and audit.permits_resolution()
                record.update(status='RETURNED_POSTPOLISH',post_endpoint_numerically_eligible=bool(eligible),full_scaled_projected_score=score,deviance=detail['negative_two_log_likelihood'],chart_state=chart,physical_state=native,polish=polish,detail=detail,exact_analysis_contacts=[{'parameter':model.parameter_names[j],'side':'LOWER'if native[j]==model.lower[j]else'UPPER','role':'PERIODIC_REPRESENTATION'if j==3 else'ANALYSIS_DOMAIN_NOT_CONFIDENCE_LIMIT'}for j in range(len(native))if native[j]==model.lower[j]or native[j]==model.upper[j]],accepted_mass_interval=None,known_BH_recovery_accepted=False)
                model.verify_snapshot()
            except Exception as error:record.update(status='FAILED_OR_UNRESOLVED',error_type=type(error).__name__,error=str(error),accepted_mass_interval=None,known_BH_recovery_accepted=False)
            if audit.failure is not None:global_failure='LATCHED_AUDIT_FAILURE: '+audit.failure
            if time.monotonic()-initial>=freeze['worker_seconds']:global_failure='WHOLE_CONTINUATION_BUDGET_EXHAUSTED'
            record['elapsed_seconds']=time.monotonic()-started;records.append(record)
            write_new(args.output/f"{campaign['purpose']}_start_{item['start_index']:02d}_terminal.json",record)
        summaries=[]
        for purpose in [c['purpose']for c in freeze['campaigns']]:
            subset=[r for r in records if r['purpose']==purpose];eligible=[r for r in subset if r['post_endpoint_numerically_eligible']];best=min(eligible,key=lambda r:(r['deviance'],r['full_scaled_projected_score'],r['start_index']))if eligible else None
            lower=[]if best is None else[t for t in endpoint_trials[purpose]if t['deviance']<best['deviance']-1e-8*max(1.,abs(best['deviance']))]
            summaries.append({'purpose':purpose,'eligible_start_indices':[r['start_index']for r in eligible],'all16_post_endpoints_eligible':len(eligible)==16,'best_returned_post_endpoint':None if best is None else{'start_index':best['start_index'],'deviance':best['deviance'],'score':best['full_scaled_projected_score'],'conditional_parameters':best['detail']['parameters']},'known_lower_trials_in_this_continuation':lower,'global_optimality_or_original_history_certified':False,'accepted_mass_interval':None,'known_BH_recovery_accepted':False})
        outcome={'schema':'bhsm.known2023.fixed_terminal_postpolish.v4','states':records,'state_count':len(records),'purpose_summaries':summaries,'normalized_model_calls':calls,'maximum_model_calls':freeze['maximum_model_calls'],'runtime':runtime,'global_failure':global_failure,'journal_failure':audit.failure,'unrecorded_event':audit.unrecorded_event,'data_generation_or_rng_calls':0,'requested_optimization_continuations':32,'accepted_mass_interval':None,'known_BH_recovery_accepted':False,'elapsed_seconds':time.monotonic()-initial,'qualification':'Append-only numerical continuation. Full original point campaigns remain unresolved artifacts; no model adequacy, physical mass interval, global search certificate or known-BH recovery is inferred.'}
        write_new(args.output/'TERMINAL_POSTPOLISH_OUTCOME_v4.json',outcome)
    return 0

def main():
    global JournalLatch,write_new
    initial=time.monotonic();p=argparse.ArgumentParser(description=__doc__)
    for name in ('freeze','output','admission'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--freeze-sha256',required=True);p.add_argument('--admission-sha256',required=True);p.add_argument('--_worker',action='store_true');args=p.parse_args();freeze=binding(args)
    from run_known2023_point_v2 import JournalLatch,write_new
    if args._worker:return worker(args,freeze,initial)
    args.output.mkdir(exist_ok=False);write_new(args.output/'INITIAL32_STATE_LEDGER_v1.json',[{'purpose':c['purpose'],'start_index':s['start_index'],'status':'NOT_STARTED'}for c in freeze['campaigns']for s in c['states']])
    write_new(args.output/'FREEZE.original.json',freeze)
    command=[sys.executable,'-B',str(Path(__file__).resolve()),'--_worker','--freeze',str(args.freeze),'--freeze-sha256',args.freeze_sha256,'--output',str(args.output),'--admission',str(args.admission),'--admission-sha256',args.admission_sha256]
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONNOUSERSITE='1');env.pop('PYTHONPATH',None);timeout=False
    with(args.output/'worker.stdout.log').open('xb')as stdout,(args.output/'worker.stderr.log').open('xb')as stderr:
        if time.monotonic()-initial>=freeze['supervisor_seconds']:raise TimeoutError('Deadline before launching any worker')
        child=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=env,cwd=Path(__file__).resolve().parent)
        while child.poll()is None:
            if time.monotonic()-initial>=freeze['supervisor_seconds']:timeout=True;child.kill();break
            time.sleep(.1)
        code=child.wait()
    integrity=None
    try:binding(args)
    except Exception as error:integrity=type(error).__name__+': '+str(error)
    terminals=[]
    for campaign in freeze['campaigns']:
        for state in campaign['states']:
            record={'purpose':campaign['purpose'],'start_index':state['start_index'],'status':'NOT_COMPLETED_WORKER_FAILURE'};path=args.output/f"{campaign['purpose']}_start_{state['start_index']:02d}_terminal.json"
            if path.exists():
                try:
                    candidate=load(path)
                    if candidate['purpose']!=record['purpose']or type(candidate['start_index'])is not int or candidate['start_index']!=record['start_index']:raise ValueError('Saved terminal identity mismatch')
                    record=candidate
                except Exception as error:record.update(status='INVALID_TERMINAL_RETAINED',error=str(error))
            terminals.append(record)
    write_new(args.output/'FINAL32_STATE_LEDGER_v1.json',terminals)
    outcome_present=(args.output/'TERMINAL_POSTPOLISH_OUTCOME_v4.json').exists();outcome_valid=False
    if outcome_present:
        try:
            outcome=load(args.output/'TERMINAL_POSTPOLISH_OUTCOME_v4.json');actual=[(r['purpose'],r['start_index'])for r in outcome['states']];wanted=[(c['purpose'],s['start_index'])for c in freeze['campaigns']for s in c['states']]
            outcome_valid=actual==wanted and outcome['accepted_mass_interval']is None and outcome['known_BH_recovery_accepted']is False
        except Exception as error:integrity=(integrity or'')+';INVALID_OUTCOME: '+str(error)
    receipt={'schema':'bhsm.known2023.fixed_terminal_polish_supervisor.v4','execution_complete':code==0 and not timeout and integrity is None and len(terminals)==32 and outcome_present and outcome_valid,'worker_returncode':code,'timeout':timeout,'source_integrity_error':integrity,'outcome_present':outcome_present,'outcome_identity_and_null_acceptance_valid':outcome_valid,'data_generation_or_rng_calls':0,'optimization_continuations_requested':32,'known_BH_recovery_accepted':False,'accepted_mass_interval':None,'elapsed_seconds':time.monotonic()-initial}
    write_new(args.output/'SUPERVISOR_TERMINAL_v1.json',receipt);print(json.dumps(receipt));return 0 if receipt['execution_complete']else 1

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception:traceback.print_exc();raise
