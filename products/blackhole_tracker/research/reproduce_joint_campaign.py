#!/usr/bin/env python
"""Portable reproduction of the internally frozen exploratory2023 joint campaign.

python product/research/reproduce_joint_campaign.py --sourcepack SOURCE.zip --output NEWDIR
Use --verify-only to verify/import the exact observations without refitting.
"""
import argparse,datetime,gzip,hashlib,json,os,platform,shutil,stat,subprocess,sys,zipfile
from pathlib import Path,PurePosixPath,PureWindowsPath

SOURCEPACK_SHA256='71d36a03e4ba275e91bea62f4784a5193f34ad32d3777b637453f91151bafa99'
REFERENCE_INPUT_SHA256='d4fc2bfc9320c7eab8a33b93517f68f035a5d498ffb35ff548a638648143af96'
SCIENCE_SHA256='6eaf050481fc23aebf4b929e49fdab57e324ee80eb08e1547b69f056269eeaaa'
EXPECTED_SOURCES={'joint_mass_v2.py':SCIENCE_SHA256,'joint_benchmark_v2.py':'83f599f7cdd616690fdcbf61f30ec05145719cc5b343d083cfe4c0a45ff940a6','joint_workflow_v2.py':'3597564b3f7cf628fd13d003ad18fb5aff7f03aea644e86ece0664d75b7e1698'}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_same_or_new(path,data):
    path=Path(path)
    if path.exists():
        if path.read_bytes()!=data:raise ValueError(f'Refusing to replace different existing bytes: {path}')
    else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
def write_json(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def source_directory(source,out):
    if source.is_dir():return source
    if digest(source)!=SOURCEPACK_SHA256:raise ValueError('Sourcepack ZIP hash differs from the frozen artifact')
    target=(out/'sourcepack').resolve();target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        for item in archive.infolist():
            name=item.filename;part=PurePosixPath(name)
            if part.is_absolute() or PureWindowsPath(name).drive or '..' in part.parts or '\\' in name or stat.S_ISLNK(item.external_attr>>16):raise ValueError('Unsafe sourcepack archive entry')
            destination=(target/Path(*part.parts)).resolve()
            if not destination.is_relative_to(target):raise ValueError('Sourcepack entry escapes requested output')
            if not item.is_dir():write_same_or_new(destination,archive.read(item))
    return target/'portable_2023_benchmark_v1'


def locate_layout(repository):
    script_product=Path(__file__).resolve().parents[1]
    if repository is None:
        product=script_product
        repo=next((p for p in product.parents if (p/'.git').exists()),product.parent)
    else:
        repo=repository.resolve();candidates=[repo/'product',repo/'products/blackhole_tracker',repo]
        product=next((p for p in candidates if (p/'bhtracker/joint_mass_v2.py').is_file()),None)
        if product is None:raise ValueError('No development product/ or formal products/blackhole_tracker/ package found')
    return repo,product

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sourcepack',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--repository',type=Path,default=None);parser.add_argument('--verify-only',action='store_true');parser.add_argument('--stages',default='baselines,profiles,predictions,controls,summary',help='Comma-separated stages; import/source verification always runs')
    a=parser.parse_args();stages={token.strip() for token in a.stages.split(',')};unknown=stages-{'baselines','profiles','predictions','controls','summary'}
    if unknown:parser.error('Unknown stage(s): '+','.join(sorted(unknown)))
    repo,product=locate_layout(a.repository);out=a.output.resolve();source=a.sourcepack.resolve();out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(product))
    for name,expected in EXPECTED_SOURCES.items():
        if digest(product/'bhtracker'/name)!=expected:raise ValueError('Frozen source differs: '+name+'; use the recorded version or declare a new analysis')
    from bhtracker.joint_mass_v2 import JointData
    from bhtracker.joint_benchmark_v2 import import_2023_benchmark
    from bhtracker.provenance import project_citation,VERSION
    resource=Path(__file__).resolve().parent/'joint_campaign_drivers';drivers=json.loads((resource/'ORIGINAL_DRIVER_MANIFEST.json').read_text())
    for name,record in drivers['files'].items():
        if digest(resource/name)!=record['sha256']:raise ValueError(f'Original driver hash mismatch: {name}')
        write_same_or_new(out/name,(resource/name).read_bytes())
    write_same_or_new(out/'ORIGINAL_DRIVER_MANIFEST.json',(resource/'ORIGINAL_DRIVER_MANIFEST.json').read_bytes())
    raw=source_directory(source,out);data=import_2023_benchmark(raw)
    if data.sha256!=REFERENCE_INPUT_SHA256:raise ValueError('Derived input differs from frozen study. Use the recorded Python/NumPy/SciPy/Astropy environment and inspect derived clock metadata; do not silently reuse reference results.')
    inputfile=out/'JOINT_2023_NATIVE_INPUT_v1.json'
    if inputfile.exists():
        if JointData(json.loads(inputfile.read_text())).sha256!=data.sha256:raise ValueError('Refusing to replace a different existing joint dataset')
    else:write_same_or_new(inputfile,(json.dumps(data.document,separators=(',',':'))+'\n').encode())
    environment={'python':platform.python_version(),**{name:__import__(name).__version__ for name in ['numpy','scipy','astropy']}}
    receiptfile=out/'PORTABLE_REPRODUCTION_MANIFEST.json'
    if receiptfile.exists():
        previous=json.loads(receiptfile.read_text())
        if previous['environment']!=environment:raise ValueError('Resume environment differs; use a new output directory to retain prior results')
    receipt={'schema':'bhtracker.portable_joint_reproduction.v1','sourcepack_sha256':SOURCEPACK_SHA256 if source.is_file() else None,'source_directory':str(raw),'scientific_source_sha256':SCIENCE_SHA256,'frozen_sources_sha256':EXPECTED_SOURCES,'package_root':str(product),'repository_cwd':str(repo),'input_sha256':data.sha256,'input_transport_sha256':digest(inputfile),'hash_algorithm':'bhtracker.canonical_numeric_json.v2','project_citation':project_citation(),'product_version':VERSION,'environment':environment,'driver_manifest':drivers,'commands':[],'no_automatic_mass_or_BH_acceptance':True}
    if receiptfile.exists():receipt['commands']=json.loads(receiptfile.read_text()).get('commands',[])
    write_json(receiptfile,receipt)
    if a.verify_only:print(json.dumps({'verified':True,'photometric_rows':len(data.document['photometry']),'astrometric_rows':len(data.document['astrometry']),'input_sha256':data.sha256}));return
    env=dict(os.environ);env['PYTHONPATH']=str(product)+os.pathsep+env.get('PYTHONPATH','')
    sys.path.insert(0,str(resource))
    import run_v2_blocked_prediction as utc_driver
    import run_v2_1_blocked_prediction as night_driver
    partitions={}
    for kind,driver in [('utc',utc_driver),('night',night_driver)]:
        training,held=driver.partition(data.document);partitions[kind]=(JointData(training).sha256,[r['source_row_id'] for r in held])
    linksfile=out/'REPRODUCTION_OUTPUT_LINKS.json';links=json.loads(linksfile.read_text()) if linksfile.exists() else {}
    def options_for(code):
        return {'noise_model':'calibrated_marginal_ou' if code=='G2' else 'native_marginal_ou','gp':code!='G0','cross_filter_correlation':0.,'astrometric_jitter_mas':0.,'source_parallax_prior':None,'free_filter_offsets':True,'astrometric_lens_light':False,'exposure_time_choice':'all_midpoints_equal_weight'}
    def fit_valid(value,code,input_sha,maxeval=None):
        if value.get('schema')!='bhtracker.native_joint_mass_result.v2' or value.get('scientific_source_sha256')!=SCIENCE_SHA256:raise ValueError('Existing fit lacks the exact result schema/source pin')
        if value.get('input_sha256')!=input_sha or value.get('input_hash_algorithm')!='bhtracker.canonical_numeric_json.v2':raise ValueError('Existing fit has different/missing input hash identity')
        if 'dataset_input' not in value or JointData(value['dataset_input']).sha256!=input_sha:raise ValueError('Existing fit content does not match its declared native input hash')
        if value.get('model_options')!=options_for(code):raise ValueError('Existing fit belongs to a different G0/G1/G2 likelihood')
        if maxeval is not None and value.get('fit_configuration',{}).get('max_nfev')!=maxeval:raise ValueError('Existing fit used a different evaluation contract')
    def validate(path,kind,code,base,maxeval=None):
        value=json.loads(path.read_text());reference=json.loads((out/base).read_text()) if base else None
        if kind=='fit':fit_valid(value,code,data.sha256,maxeval)
        elif kind=='profile':
            if value.get('schema')!='bhtracker.joint_mass_profile.v2' or len(value.get('rows',[]))!=31:raise ValueError('Existing profile is not the complete frozen31-point scan')
            import math
            masses=[10**(-1+3*k/30) for k in range(31)]
            if any(abs(math.log(r['mass_msun']/m))>1e-12 for r,m in zip(value['rows'],masses)):raise ValueError('Existing profile grid differs')
            if abs(value['reference_objective_deviance']-reference['objective_deviance'])>1e-8:raise ValueError('Existing profile has a different baseline minimum')
        elif kind=='refined':
            if value.get('schema')!='bhtracker.joint_mass_refined_support.v1' or value.get('baseline')!=base or value.get('scientific_source_sha256')!=SCIENCE_SHA256 or len(value.get('rows',[]))<31:raise ValueError('Existing refined support lacks baseline/source/grid linkage')
        elif kind in ['utc','night']:
            train_sha,held_ids=partitions[kind];training_path=path.with_name(path.name.replace('_PREDICTION.json','_TRAIN.json'));training=json.loads(training_path.read_text());fit_valid(training,code,train_sha,600)
            if value.get('status')=='TRAINING_SEARCH_UNRESOLVED':
                if 'best_internal_state' in training:raise ValueError('Inconsistent failed training prediction')
            elif value.get('schema')!='bhtracker.joint_blocked_predictive_score.v1' or value.get('full_input_sha256')!=data.sha256 or value.get('training_input_sha256')!=train_sha or value.get('heldout_source_row_ids')!=held_ids or value.get('training_fitted_parameters')!=training.get('parameters'):raise ValueError('Existing prediction lacks exact partition/training-state linkage')
        elif kind=='controls':
            if value.get('schema')!='bhtracker.joint_parametric_diagnostics.v2' or value.get('base_result')!=base or value.get('observed_diagnostics')!=reference['diagnostics'] or value.get('observed_residual_structure')!=reference['residual_structure']:raise ValueError('Existing controls have a different baseline')
            count=value.get('control_count',-1)
            if not 0<=count<=20 or len(value.get('controls',[]))!=count:raise ValueError('Incomplete/malformed control count')
            firstseed=2026102300 if code=='G2' else 2026102200
            for k,row in enumerate(value['controls']):
                if row.get('simulation')!=k or row.get('seed')!=firstseed+k:raise ValueError('Existing controls changed frozen seeds')
                artifact=out/(Path(base).stem+f'_CONTROL_{k:02d}.json.gz')
                if artifact.exists():
                    with gzip.open(artifact,'rt') as stream:control=json.load(stream)
                    full=control['full_fit'];trained=control['training_fit']
                    if trained.get('scientific_source_sha256')!=SCIENCE_SHA256 or trained.get('model_options')!=options_for(code):raise ValueError('Control training-state source/likelihood mismatch')
                    if full.get('scientific_source_sha256')!=SCIENCE_SHA256 or full.get('model_options')!=options_for(code) or full['dataset_input']['metadata']['simulation_control'].get('generating_result')!=base:raise ValueError('Control full-state source/likelihood/generator mismatch')
        identity={'output_sha256':digest(path),'baseline':base,'baseline_sha256':digest(out/base) if base else None,'kind':kind,'candidate':code}
        if path.name in links and links[path.name]!=identity:raise ValueError('Existing output/baseline changed after its audit linkage was recorded')
        links[path.name]=identity;write_json(linksfile,links)
        return value
    def run(label,args,expected=None,complete=None,kind=None,code=None,base=None,maxeval=None):
        if expected is not None and expected.exists():
            existing=validate(expected,kind,code,base,maxeval)
            if complete is None or complete(existing):return
            snapshot=out/'preserved_resume_snapshots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');snapshot.mkdir(parents=True)
            for f in out.glob(expected.stem.replace('_PARAMETRIC_CONTROLS20','')+'*'):
                if f.is_file():shutil.copy2(f,snapshot/f.name)
            links.pop(expected.name,None);write_json(linksfile,links)
        record={'label':label,'argv':[str(x) for x in args],'cwd':str(repo),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};receipt['commands'].append(record);write_json(receiptfile,receipt)
        print(label,flush=True)
        with (out/(label+'.log')).open('w',encoding='utf-8') as log:completed=subprocess.run([str(x) for x in args],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT)
        record['exit_code']=completed.returncode;record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write_json(receiptfile,receipt)
        if completed.returncode:raise RuntimeError(f'{label} failed; inspect its retained log')
        if expected is not None:validate(expected,kind,code,base,maxeval)
    candidates=[('G0','JOINT_V2_G0_DIAGONAL16',[]),('G1','JOINT_V2_G1_MARGINAL16',['--gp']),('G2','JOINT_V2_G2_CALIBRATED16',['--gp','--options','{"noise_model":"calibrated_marginal_ou"}'])]
    if 'baselines' in stages:
        for code,stem,options in candidates:
            run(stem,[sys.executable,'-m','bhtracker.joint_workflow_v2','fit',inputfile,out/(stem+'.json'),*options],out/(stem+'.json'),kind='fit',code=code,maxeval=600)
            run(stem+'_CONTINUATION',[sys.executable,out/'continue_v2.py',stem+'.json'],out/(stem+'_CONTINUED.json'),kind='fit',code=code,maxeval=1800)
    for code,stem,options in candidates[1:]:
        baseline=stem+'_CONTINUED.json';profile='JOINT_V2_'+code+'_MASS_PROFILE31.json'
        if 'profiles' in stages:
            run(code+'_PROFILE31',[sys.executable,'-m','bhtracker.joint_workflow_v2','profile',inputfile,out/baseline,out/profile],out/profile,kind='profile',code=code,base=baseline)
            refined='JOINT_V2_'+code+'_MASS_REFINED_SUPPORT.json';run(code+'_PROFILE_REFINEMENT',[sys.executable,out/'refine_v2_profiles.py',baseline,profile,refined],out/refined,kind='refined',code=code,base=baseline)
        if 'predictions' in stages:
            run(code+'_ORIGINAL_UTC_CONDITIONAL_DIAGNOSTIC',[sys.executable,out/'run_v2_blocked_prediction.py',baseline],out/(Path(baseline).stem+'_BLOCKED_PREDICTION.json'),kind='utc',code=code,base=baseline)
            run(code+'_V2_1_NIGHT_PREDICTION',[sys.executable,out/'run_v2_1_blocked_prediction.py',baseline],out/(Path(baseline).stem+'_V2_1_BLOCKED_PREDICTION.json'),kind='night',code=code,base=baseline)
        if 'controls' in stages:
            file=out/(Path(baseline).stem+'_PARAMETRIC_CONTROLS20.json');run(code+'_PARAMETRIC20',[sys.executable,out/'run_v2_parametric_controls.py',baseline],file,lambda r:r.get('control_count')==20 and all((out/(Path(baseline).stem+f'_CONTROL_{k:02d}.json.gz')).exists() for k in range(20)),kind='controls',code=code,base=baseline)
    if 'summary' in stages:
        table=[]
        for code,stem,options in candidates:
            result=json.loads((out/(stem+'_CONTINUED.json')).read_text());fit_valid(result,code,data.sha256,1800);table.append({'candidate':code,'solver_status':result['status'],'conditional_mass_point_msun':result['parameters']['mass_msun'],'accepted_mass_measurement':False,'failed_structure_bins':result['residual_structure']['failed_bins'],'active_search_bounds':result['nonlinear_active_bounds'],'numerical_convergence':result['numerical_convergence']})
        write_json(out/'PORTABLE_CAMPAIGN_SUMMARY.json',{'schema':'bhtracker.portable_campaign_summary.v1','candidates':table,'interpretation':'No automatic physical acceptance. Apply frozen profile, noise, predictive, timing/calibration and darkness gates; retain every inadequate result.','all_source_rows_preserved':15533,'new_discoveries_claimed':[]})

if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,FileNotFoundError) as error:
        print('Reproduction stopped: '+str(error),file=sys.stderr);raise SystemExit(2)
