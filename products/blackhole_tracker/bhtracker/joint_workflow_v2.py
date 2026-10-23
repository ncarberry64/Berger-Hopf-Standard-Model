"""Auditable command-line entry for the separate experimental joint route.

python -m bhtracker.joint_workflow_v2 import DIRECTORY OUTPUT.json
python -m bhtracker.joint_workflow_v2 fit INPUT.json OUTPUT.json [--gp]
python -m bhtracker.joint_workflow_v2 profile INPUT.json RESULT.json OUTPUT.json
python -m bhtracker.joint_workflow_v2 replay RESULT.json
"""
import argparse,hashlib,json,platform,sys
from pathlib import Path
import numpy as np
from .joint_mass_v2 import JointData,JointModel,fit_joint,profile_joint_mass


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def replay(result,*,rtol=2e-10,atol=2e-8):
    data=JointData(result['dataset_input'])
    if data.sha256!=result['input_sha256']:raise ValueError('exported joint input hash mismatch')
    scientific=hashlib.sha256((Path(__file__).parent/'joint_mass_v2.py').read_bytes()).hexdigest()
    if result['scientific_source_sha256']!=scientific:raise ValueError('scientific source version differs; explicit migration required')
    actual=JointModel(data,**result['model_options']).evaluate(np.array(result['best_internal_state']),details=True)
    pairs=[('objective_deviance',actual['objective_deviance']),('photometric_predictions_magnitude',actual['photometric_predictions_magnitude']),('astrometric_predictions_NE_mas',actual['astrometric_predictions_NE_mas'])]
    checks={name:bool(np.allclose(np.asarray(result[name]),value,rtol=rtol,atol=atol)) for name,value in pairs}
    return {'schema':'bhtracker.joint_replay.v2','passed':all(checks.values()),'checks':checks,'input_sha256':data.sha256,'scientific_source_sha256':scientific,'max_photometric_difference_mag':float(np.max(abs(np.array(result['photometric_predictions_magnitude'])-actual['photometric_predictions_magnitude']))),'max_astrometric_difference_mas':float(np.max(abs(np.array(result['astrometric_predictions_NE_mas'])-actual['astrometric_predictions_NE_mas'])))}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('import');q.add_argument('directory');q.add_argument('output');q.add_argument('--all-ogle-rows',action='store_true');q.add_argument('--clock-offset-seconds',type=float,default=0.)
    q=sub.add_parser('fit');q.add_argument('input');q.add_argument('output');q.add_argument('--gp',action='store_true');q.add_argument('--starts',type=int,default=16);q.add_argument('--max-nfev',type=int,default=600);q.add_argument('--options',help='Explicit JSON likelihood sensitivity options');q.add_argument('--initial-result',help='Retain all converged states from previous result as initial states')
    q=sub.add_parser('profile');q.add_argument('input');q.add_argument('result');q.add_argument('output');q.add_argument('--max-nfev',type=int,default=600);q.add_argument('--masses',help='Comma-separated masses; default31 logspaced0.1..100')
    q=sub.add_parser('replay');q.add_argument('result')
    a=p.parse_args(argv)
    if a.command=='import':
        from .joint_benchmark_v2 import import_2023_benchmark
        d=import_2023_benchmark(a.directory,all_ogle_rows=a.all_ogle_rows,clock_offset_seconds=a.clock_offset_seconds);write(a.output,d.document);print(d.sha256);return
    if a.command=='replay':
        receipt=replay(read(a.result));print(json.dumps(receipt));return 0 if receipt['passed'] else 1
    d=JointData(read(a.input))
    if a.command=='profile':
        result=read(a.result);masses=np.logspace(-1,2,31) if not a.masses else [float(x) for x in a.masses.split(',')];write(a.output,profile_joint_mass(d,result,masses,max_nfev=a.max_nfev));return
    options=json.loads(a.options) if a.options else {};options.setdefault('gp',a.gp)
    states=None
    if a.initial_result:states=[row['internal_state'] for row in read(a.initial_result)['all_starts'] if row.get('converged')]
    result=fit_joint(d,starts=a.starts,max_nfev=a.max_nfev,initial_states=states,**options)
    from .interpretation import with_surface_geometry_interpretation
    result=with_surface_geometry_interpretation(result)
    result['environment']={name:__import__(name).__version__ for name in ['numpy','scipy','astropy']};result['environment']['python']=platform.python_version()
    result['workflow_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    write(a.output,result)
    print(json.dumps({'status':result['status'],'parameters':result.get('parameters'),'diagnostics':result.get('diagnostics'),'numerical_convergence':result.get('numerical_convergence'),'surface_geometry_interpretation':result['surface_geometry_interpretation']}))

if __name__=='__main__':sys.exit(main())
