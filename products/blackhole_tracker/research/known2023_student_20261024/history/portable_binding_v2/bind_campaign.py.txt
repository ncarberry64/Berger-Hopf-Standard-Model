"""Verify portable research sources; optionally prepare a fresh point-fit binding.

Default: metadata/source verification only. No network, scientific provider import,
observation generation, likelihood or fitting. Explicit --prepare writes commands
and an UNADMITTED freeze, never executes them or claims known-BH recovery.
"""
import argparse
import base64
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parent
NATIVE_SHA = 'd2409db410e113872781494ca4d73db57d2a44fd65146c4e7ec2f40828448428'
RUNTIME = {'python':'3.11.9','numpy':'1.26.4','scipy':'1.12.0','astropy':'6.0.0'}
CONFIG = {'starts':16,'candidate':'ST6_SEEING','numerical_time_origin_jd_tdb':2455765.,
          'angular_reference_jd_tdb':2456000.,'worker_wall_seconds':1740.,
          'per_start_wall_seconds':100.,'supervisor_wall_seconds':1800.,
          'journal_max_bytes':256*1024*1024}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def pin(path):
    path=Path(path).resolve();raw=path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':sha(raw)}

def load_json(raw):
    return json.loads(raw.decode('utf-8'),parse_constant=lambda x:(_ for _ in()).throw(ValueError('Nonfinite JSON: '+x)))

def actual_runtime():
    return dict(python=sys.version.split()[0], **{name:importlib.metadata.version(name) for name in ('numpy','scipy','astropy')})

def verify_sources(root=ROOT, core_path=None):
    root=Path(root).resolve();manifest_path=root/'SOURCE_MANIFEST_v2.json'
    manifest=load_json(manifest_path.read_bytes());sources=[]
    for expected in manifest['members']:
        name=expected['relative_path'];relative=PurePosixPath(name)
        if not isinstance(name,str) or '\\'in name or ':'in name or relative.is_absolute() or '..'in relative.parts or str(relative)!=name:
            raise ValueError('Unsafe source manifest path')
        path=root.joinpath(*relative.parts)
        if not path.resolve().is_relative_to(root):raise ValueError('Source path escapes research root')
        found=pin(path)
        if found['bytes']!=expected['bytes']or found['sha256']!=expected['sha256']:
            raise ValueError('Reviewed portable source differs: '+name)
        sources.append(found)
    core=Path(core_path).resolve()if core_path else root.parents[1]/'bhtracker/joint_mass_v2.py'
    found=pin(core)
    if found['sha256']!=manifest['geometry_provider']['sha256']:
        raise ValueError('Reviewed geometry provider differs')
    sources += [found,pin(manifest_path)]
    return {'source_files':sources,'core_path':str(core),'student_directory':str(root/'providers'),
            'source_manifest_sha256':sha(manifest_path.read_bytes()),'sources_verified':True,
            'default_action':'METADATA_ONLY_NO_MODEL_OR_NETWORK','scientific_acceptance':False}

def verify_input(raw,purpose,registry):
    document=load_json(raw);identity=sha(raw)
    if purpose=='AUTHENTIC2023':
        if identity!=NATIVE_SHA or document.get('schema')!='bhtracker.native_joint_mass.v1' or document.get('simulation_only')is True:
            raise ValueError('Only exact registered authentic2023 bytes are admitted')
        if (len(document['photometry']),len(document['astrometry']))!=(12521,21):raise ValueError('Native selected row counts differ')
    elif purpose=='WHOLLY_INVENTED':
        if identity not in registry.get('wholly_invented_sha256',[])or document.get('simulation_only')is not True or document.get('data_version')!='SYNTHETIC_KNOWN2023_ST6_CONTROL_v1':
            raise ValueError('Exact registered wholly invented fixture required')
    elif purpose=='ACTUAL_CADENCE_CONTROL':
        if identity not in registry.get('actual_cadence_sha256',[])or document.get('schema')!='bhsm.known2023.generated_control.v1'or document.get('simulation_only')is not True or document.get('scope')!='CONDITIONAL_SIMULATION_AT_AUTHENTIC_CADENCE':
            raise ValueError('Exact generated daughter/registry required')
        parent_raw=base64.b64decode(document['parent_native_bytes_base64'],validate=True)
        if sha(parent_raw)!=NATIVE_SHA or document['parent_native_sha256']!=NATIVE_SHA:raise ValueError('Unchanged registered parent required')
        parent=load_json(parent_raw)
        for generated_key,parent_key,numeric in [('generated_photometry','photometry',('generated_magnitude',)),('generated_astrometry','astrometry',('generated_north_mas','generated_east_mas'))]:
            generated=document[generated_key]
            if [r['parent_source_row_id']for r in generated]!=[r['source_row_id']for r in parent[parent_key]]:raise ValueError('Every parent identity/order requires exactly one replacement')
            if not all(type(r[k])in(int,float)and math.isfinite(r[k])for r in generated for k in numeric):raise ValueError('Finite generated values required; no native fallback')
    else:raise ValueError('Explicit registered purpose required')
    return identity

def prepare(input_path,purpose,output,*,registry_path=None,root=ROOT,core_path=None,runtime=None,method='periodic-trust-v3'):
    root=Path(root).resolve();binding=verify_sources(root,core_path)
    if method not in ('original-v2','periodic-trust-v3'):raise ValueError('Explicit reviewed numerical method required')
    runtime=actual_runtime()if runtime is None else runtime
    if runtime!=RUNTIME:raise ValueError('Preparing this reviewed campaign requires exact runtime '+repr(RUNTIME))
    input_path=Path(input_path).resolve();raw=input_path.read_bytes()
    if purpose=='WHOLLY_INVENTED'and registry_path is None:registry_path=root/'invented_fixture_v1/CONTROL_REGISTRY_v1.json'
    registry=load_json(Path(registry_path).read_bytes())if registry_path else {}
    verify_input(raw,purpose,registry)
    freeze={'schema':'bhsm.known2023.prospective_campaign_freeze.v2','status':'PREPARED_NOT_EXECUTION_ADMITTED',
        'purpose':purpose,'native_fit_admitted':False,'source_files':binding['source_files'],
        'input':pin(input_path),'core_path':binding['core_path'],'student_directory':binding['student_directory'],
        'runtime':dict(RUNTIME),'configuration':dict(CONFIG),'scientific_acceptance':{
            'accepted_mass_interval':None,'known_black_hole_recovery_accepted':False,'adequacy':'NOT_REFIT_CALIBRATED','coverage':'NOT_CALIBRATED'}}
    freeze['numerical_method']=method
    if registry_path:freeze['control_registry']=pin(registry_path)
    output=Path(output).resolve();output.mkdir(parents=False,exist_ok=False)
    freeze_path=output/'POINT_FREEZE.json'
    freeze_raw=(json.dumps(freeze,indent=2,allow_nan=False)+'\n').encode('utf-8')
    with freeze_path.open('xb')as stream:stream.write(freeze_raw)
    script='run_known2023_point_v3.py'if method=='periodic-trust-v3'else'run_known2023_point_v2.py'
    command=[sys.executable,'-B',str(root/script),'--freeze',str(freeze_path),
        '--freeze-sha256',sha(freeze_raw),'--output',str(output/'point_output')]
    if purpose!='WHOLLY_INVENTED':command+=['--admission','EXACT_REVIEWED_EXECUTION_RECEIPT.json','--admission-sha256','EXACT_RECEIPT_SHA256']
    receipt={'schema':'bhsm.known2023.portable_binding.v1','freeze':pin(freeze_path),'commands_not_executed':[command],
        'purpose':purpose,'numerical_method':method,'runtime':runtime,'native_or_model_calls':0,'scientific_acceptance':False,
        'requires_separate_reviewed_exact_execution_receipt':purpose!='WHOLLY_INVENTED'}
    with (output/'BINDING_RECEIPT.json').open('x',encoding='utf-8')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    return receipt

def verify_existing(path):
    path=Path(path);freeze=load_json(path.read_bytes())
    for expected in freeze['source_files']+[freeze['input']]+([freeze['control_registry']]if freeze.get('control_registry')else[]):
        found=pin(expected['path'])
        if found['bytes']!=expected['bytes']or found['sha256']!=expected['sha256']:raise ValueError('Existing binding bytes differ: '+expected['path'])
    return {'freeze':pin(path),'all_bound_bytes_verified':True,'native_or_model_calls':0,'scientific_acceptance':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--purpose',choices=('WHOLLY_INVENTED','AUTHENTIC2023','ACTUAL_CADENCE_CONTROL'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--registry',type=Path)
    parser.add_argument('--core-path',type=Path)
    parser.add_argument('--method',choices=('original-v2','periodic-trust-v3'),default='periodic-trust-v3')
    parser.add_argument('--verify-existing',type=Path)
    args=parser.parse_args()
    if args.verify_existing:
        if args.prepare:parser.error('--prepare and --verify-existing are separate actions')
        result=verify_existing(args.verify_existing)
    elif args.prepare:
        if not args.input or not args.purpose or not args.output:parser.error('--prepare requires --input --purpose --output')
        result=prepare(args.input,args.purpose,args.output,registry_path=args.registry,core_path=args.core_path,method=args.method)
    else:result=verify_sources(core_path=args.core_path)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
