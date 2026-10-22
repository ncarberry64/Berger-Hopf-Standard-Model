"""Dispatch independent frozen mass-profile points without changing their search.

The serial function initializes each mass from the same fixed baseline modes.
This driver changes scheduling only; it does not pass any cross-mass warm start.
"""
import argparse,concurrent.futures,datetime,hashlib,json,os,sys,time
from pathlib import Path

SCIENCE='6eaf050481fc23aebf4b929e49fdab57e324ee80eb08e1547b69f056269eeaaa'
MODEL=None
DATA=None
BASE=None

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def initialize(product,inputfile,baseline):
    global MODEL,DATA,BASE
    for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
    sys.path.insert(0,product)
    if sha(Path(product)/'bhtracker/joint_mass_v2.py')!=SCIENCE:raise ValueError('Frozen scientific source mismatch')
    from bhtracker.joint_mass_v2 import JointData,profile_joint_mass
    MODEL=profile_joint_mass;DATA=JointData(json.loads(Path(inputfile).read_text()));BASE=json.loads(Path(baseline).read_text())

def point(task):
    index,mass=task;started=time.time()
    value=MODEL(DATA,BASE,[mass],max_nfev=600,mode_limit=8)
    return index,value,{'worker_pid':os.getpid(),'elapsed_seconds':time.time()-started}

def main():
    p=argparse.ArgumentParser();p.add_argument('--product',required=True);p.add_argument('--input',required=True);p.add_argument('--baseline',required=True);p.add_argument('--output',required=True);p.add_argument('--workers',type=int,default=3);a=p.parse_args()
    if not 1<=a.workers<=4:raise ValueError('bounded workers must be1..4')
    for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
    import numpy as np
    masses=[float(x) for x in np.logspace(-1,2,31)];output=Path(a.output);folder=output.with_suffix('');folder.mkdir(parents=True,exist_ok=True)
    baseline=json.loads(Path(a.baseline).read_text());records={};results={}
    receipt={'schema':'bhtracker.parallel_profile_dispatch.v1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'driver_sha256':sha(__file__),'scientific_source_sha256':SCIENCE,'baseline_sha256':sha(a.baseline),'input_transport_sha256':sha(a.input),'input_sha256':baseline['input_sha256'],'workers':a.workers,'blas_threads_per_worker':1,'max_nfev':600,'mode_limit':8,'mass_grid_msun':masses,'cross_mass_warm_starts':False,'serial_process_preserved':True,'completed':[]}
    pending=[]
    for i,mass in enumerate(masses):
        path=folder/f'point_{i:02d}.json'
        if path.exists():
            saved=json.loads(path.read_text())
            if saved['baseline_sha256']!=receipt['baseline_sha256'] or saved['driver_sha256']!=receipt['driver_sha256'] or saved['value']['rows'][0]['mass_msun']!=mass:raise ValueError('Existing point linkage differs')
            results[i]=saved['value'];records[i]=saved['execution']
        else:pending.append((i,mass))
    # Range-spanning scheduling provides early checkpoints. The result order is fixed.
    priority={0:0,15:1,30:2};pending.sort(key=lambda pair:(priority.get(pair[0],3),pair[0]))
    write(folder/'dispatch.json',receipt)
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(str(Path(a.product).resolve()),str(Path(a.input).resolve()),str(Path(a.baseline).resolve()))) as pool:
        futures={pool.submit(point,task):task for task in pending}
        for future in concurrent.futures.as_completed(futures):
            i,value,execution=future.result();results[i]=value;records[i]=execution
            path=folder/f'point_{i:02d}.json';write(path,{'baseline_sha256':receipt['baseline_sha256'],'driver_sha256':receipt['driver_sha256'],'value':value,'execution':execution})
            receipt['completed']=[{'index':j,'mass_msun':masses[j],'point_sha256':sha(folder/f'point_{j:02d}.json'),**records[j]} for j in sorted(results)];write(folder/'dispatch.json',receipt)
            print(json.dumps({'completed':len(results),'index':i,'mass_msun':masses[i],'status':value['rows'][0]['status'],'elapsed_seconds':execution['elapsed_seconds']}),flush=True)
    reference=results[0];aggregate={**reference,'rows':[results[i]['rows'][0] for i in range(31)]}
    if any(value['configuration']!=reference['configuration'] or value['reference_objective_deviance']!=reference['reference_objective_deviance'] for value in results.values()):raise ValueError('Point configurations differ')
    write(output,aggregate);receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt['aggregate_sha256']=sha(output);receipt['complete']=True;write(folder/'dispatch.json',receipt)

if __name__=='__main__':main()
