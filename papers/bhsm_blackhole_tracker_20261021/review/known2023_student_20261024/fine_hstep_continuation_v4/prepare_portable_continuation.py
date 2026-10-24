"""Prepare portable source/state paths only. Never execute scientific code."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(p):
    p=Path(p).resolve();raw=p.read_bytes();return {'path':str(p),'bytes':len(raw),'sha256':sha(raw)}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    for name in ('research-source-dir','geometry-source','native-input','control-input','control-registry','output'):parser.add_argument('--'+name,type=Path)
    args=parser.parse_args();requirements=load(ROOT/'PORTABLE_SOURCE_REQUIREMENTS_v1.json');mapping=load(ROOT/'PREPARED32_STATE_MAP_v1.json')
    if not args.prepare:
        print(json.dumps({'prepared_states':len(mapping['states']),'action':'DESCRIBE_ONLY_NO_SCIENTIFIC_IMPORT_NETWORK_OR_EXECUTION','requirements':requirements,'scientific_acceptance':False},indent=2));return
    if any(getattr(args,n)is None for n in ('research_source_dir','geometry_source','native_input','control_input','control_registry','output')):parser.error('--prepare requires every explicit source/input/registry/output path')
    runtime=dict(python=sys.version.split()[0],**{n:importlib.metadata.version(n)for n in ('numpy','scipy','astropy')})
    historical=load(ROOT/'HISTORICAL_FREEZE_v4_1.json')
    if runtime!=historical['runtime']:raise ValueError('Exact reviewed runtime required')
    for name,path in [('native',args.native_input),('control',args.control_input),('registry',args.control_registry),('geometry',args.geometry_source)]:
        if pin(path)['sha256']!=requirements[name+'_sha256']:raise ValueError('Exact known '+name+' bytes required')
    for row in requirements['research_sources']:
        if pin(args.research_source_dir/row['relative_path'])['sha256']!=row['sha256']:raise ValueError('Reviewed source differs')
    for row in mapping['states']:
        if pin(ROOT/row['relative_path'])['sha256']!=row['sha256']:raise ValueError('Prepared state differs')
    if pin(ROOT/'continue_saved_terminal_polish_v4.py')['sha256']!=requirements['driver_sha256']:raise ValueError('Driver differs')
    args.output.mkdir(parents=False,exist_ok=False);source_files=[]
    for row in requirements['research_sources']:
        name=row['relative_path'];target=args.output/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(args.research_source_dir/name,target)
        if pin(target)['sha256']!=row['sha256']:raise ValueError('Source changed during copy')
        source_files.append(pin(target))
    for name in ['continue_saved_terminal_polish_v4.py','prepare_portable_continuation.py','PORTABLE_SOURCE_REQUIREMENTS_v1.json','PREPARED32_STATE_MAP_v1.json']:
        target=args.output/name;shutil.copyfile(ROOT/name,target);source_files.append(pin(target))
    source_files.append(pin(args.geometry_source));campaigns=[];bound=[]
    for purpose,input_path in [('AUTHENTIC2023',args.native_input),('ACTUAL_CADENCE_CONTROL',args.control_input)]:
        states=[]
        for row in mapping['states']:
            if row['purpose']!=purpose:continue
            target=args.output/row['relative_path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['relative_path'],target)
            states.append(dict(start_index=row['start_index'],historical_original_terminal_sha256=row['original_full_terminal_sha256'],**pin(target)))
        campaign={'purpose':purpose,'input':pin(input_path),'states':states}
        if purpose=='ACTUAL_CADENCE_CONTROL':campaign['registry']=pin(args.control_registry);bound.append(pin(args.control_registry))
        campaigns.append(campaign);bound += [pin(input_path)]+states
    keys=['state_count','difference_step','polish_iterations','score_tolerance','max_scaled_step','maximum_model_calls','state_seconds','worker_seconds','supervisor_seconds','journal_max_bytes','runtime','numerical_time_origin_jd_tdb','angular_reference_jd_tdb']
    freeze={k:historical[k]for k in keys};freeze.update(schema='bhsm.known2023.portable_prepared_continuation.v4',status='FRESH_BINDING_NOT_EXECUTION_ADMITTED',source_files=source_files,bound_artifacts=bound,campaigns=campaigns,core_path=str(args.geometry_source.resolve()),student_directory=str((args.output/'providers').resolve()),initial_phase_fits_allowed=0,saved_terminal_optimization_continuations_allowed=32,data_generation_allowed=0,random_draws_allowed=0,mass_profile_calls_allowed=0,accepted_mass_interval=None,known_BH_recovery_accepted=False)
    file=args.output/'PREPARED_CONTINUATION_FREEZE.json'
    with file.open('x',encoding='utf-8')as stream:json.dump(freeze,stream,indent=2);stream.write('\n')
    command=[sys.executable,'-B',str((args.output/'continue_saved_terminal_polish_v4.py').resolve()),'--freeze',str(file.resolve()),'--freeze-sha256',pin(file)['sha256'],'--admission','NEW_EXACT_REVIEWED_EXECUTION_RECEIPT.json','--admission-sha256','NEW_RECEIPT_SHA256','--output',str((args.output/'execution_output').resolve())]
    receipt={'schema':'bhsm.known2023.portable_continuation_preparation.v1','freeze':pin(file),'command_not_executed':command,'states':32,'native_data_copied':False,'scientific_imports_model_fits_rng_network_calls':0,'historical_admissions_do_not_apply_to_this_new_binding':True,'accepted_mass_interval':None,'known_BH_recovery_accepted':False}
    with(args.output/'PREPARATION_RECEIPT.json').open('x',encoding='utf-8')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
