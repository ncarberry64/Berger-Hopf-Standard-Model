"""Checkpoint a same-branch finite D5 bulk family and consume its event ports."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,platform,sys
import numpy as np
import scipy
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_d5_complement_bulk_response import solve_incoming_complement_bulk_family
from bhsm.interface.muon_d5_child_corner_incidence import birth_corner_incidence
from bhsm.interface.retained_response.finite_time_response import write_npz


def pin(path):return sha256(path.read_bytes()).hexdigest()


def owners():
    return {Path(m.__file__).resolve().relative_to(ROOT).as_posix():pin(Path(m.__file__))
        for n,m in sorted(sys.modules.items())
        if n.startswith('bhsm.') and getattr(m,'__file__',None)
        and Path(m.__file__).resolve().is_relative_to(ROOT)
        and n!='bhsm.interface.muon_d5_complement_event_return'}


def save_groups(output,arrays,prefix):
    groups={}
    for key,value in arrays.items():
        if not isinstance(value,np.ndarray):continue
        group='shared'
        for p in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate',
                  'plus_seed','minus_seed','minus_LR','minus_RL'):
            if key.startswith(p+'_'):group=p;break
        groups.setdefault(group,{})[key]=value
    result={}
    for group,values in sorted(groups.items()):
        path=output/(prefix+'_'+group+'.npz')
        if path.exists():raise FileExistsError('preserve saved application '+str(path))
        write_npz(path,values)
        result[path.name]=dict(sha256=pin(path),bytes=path.stat().st_size,
            keys=sorted(values))
    return result


def load_groups(output,manifest):
    arrays={}
    for name,md in manifest.items():
        path=output/name
        if pin(path)!=md['sha256']:raise ValueError('saved field identity changed: '+name)
        with np.load(path,allow_pickle=False) as z:
            arrays.update({k:z[k].copy(order='K') for k in z.files})
    return arrays


def run(output,*,resume=False,core_only=False,radial_steps=1,reuse_core_from=None):
    output=Path(output)
    base=ROOT/'artifacts/muon_formed_event_domain_application_20261019/run_2'
    old=json.loads((base/'result.json').read_bytes())
    prior=base/'formed_event_domain_application.npz'
    if pin(prior)!=old['arrays']['sha256']:raise ValueError('completed E1 arrays changed')
    for rel,h in old['input_sha256'].items():
        if pin(ROOT/rel)!=h:raise ValueError('completed input identity changed: '+rel)
    pins={p.relative_to(ROOT).as_posix():pin(p) for p in (prior,base/'result.json')}
    with np.load(prior,allow_pickle=False) as z:cached={k:z[k].copy() for k in z.files}
    folder=ROOT/'artifacts/muon_retained_response_20261018/inputs'
    history=folder/'incoming_history.npz';metadata=folder/'history_metadata.json'
    md=json.loads(metadata.read_bytes())
    if md['histories']!='PROVISIONAL_NOT_COLLIDER_SOLUTIONS':raise ValueError('retained history scope changed')
    samples=md['sides']['incoming'];times=np.array([s['time'] for s in samples])
    with np.load(history,allow_pickle=False) as z:
        raw=np.array([z[s['label']+'_raw_fields'] for s in samples])
        rates=np.array([z[s['label']+'_raw_coordinate_time_derivative'] for s in samples])
    for p in (history,metadata):pins[p.relative_to(ROOT).as_posix()]=pin(p)
    cp=output/'core_result.json'
    if resume:
        core=json.loads(cp.read_bytes())
        if core['radial_steps']!=radial_steps:raise ValueError('resume numerical chart changed')
        for rel,h in core['input_sha256'].items():
            if pin(ROOT/rel)!=h:raise ValueError('resume core input changed: '+rel)
        arrays=load_groups(output,core['archives'])
    elif reuse_core_from is not None:
        if output.exists():raise FileExistsError('preserve completed applications')
        source=Path(reuse_core_from)
        core=json.loads((source/'core_result.json').read_bytes())
        if core['radial_steps']!=radial_steps:raise ValueError('reuse core numerical chart changed')
        for rel,h in core['input_sha256'].items():
            if pin(ROOT/rel)!=h:raise ValueError('reuse core input changed: '+rel)
        arrays=load_groups(source,core['archives'])
        output.mkdir(parents=True)
        archives=save_groups(output,arrays,'bulk')
        if archives!=core['archives']:raise ValueError('rematerialized core bytes differ')
        cp.write_bytes((source/'core_result.json').read_bytes())
        print(json.dumps(dict(stage='IDENTICAL_CORE_REUSED',core_sha256=pin(cp))),flush=True)
    else:
        if output.exists():raise FileExistsError('preserve completed runs; use --resume for saved core')
        output.mkdir(parents=True)
        before=owners()
        arrays,report=solve_incoming_complement_bulk_family(times,raw,rates,
            saved_endpoint=cached,radial_steps=radial_steps)
        after=owners()
        if any(after.get(k)!=v for k,v in before.items()):
            raise ValueError('core execution owners changed during application')
        pins.update(owners())
        core=dict(schema='bhsm.d5-complement-core.v1',parent_head='e02747f2cb98494a5743c75c53c2f7f6f83bc4eb',
            input_sha256=pins,radial_steps=radial_steps,report=report,
            archives=save_groups(output,arrays,'bulk'))
        cp.write_text(json.dumps(core,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        print(json.dumps(dict(stage='CORE_SAVED',core_sha256=pin(cp),report=report)),flush=True)
    if core_only:return core
    if (output/'result.json').exists():raise FileExistsError('preserve completed consumer')
    from bhsm.interface.muon_d5_complement_event_return import consume_solved_bulk_family
    returned,consumed=consume_solved_bulk_family(arrays)
    corner={}
    for side in ('incoming','outgoing'):
        a,r=birth_corner_incidence(cached[side+'_raw268'],cached[side+'_raw_coordinate_time_derivative268'])
        returned.update({'corner_'+side+'_'+k:v for k,v in a.items()});corner[side]=r
    for key,value in cached.items():
        if key.startswith('native_incidence_'):returned['reused_'+key]=value
    result=dict(schema='bhsm.d5-complement-event-application.v1',
        parent_head=core['parent_head'],classification='PROVISIONAL_INCOMING_BULK_SOLUTION_FAMILY_CONSUMED_IN_ORIGINAL_EVENT_AND_JACOBI_ROWS',
        core_record_sha256=pin(cp),core_report=core['report'],
        input_sha256={**core['input_sha256'],**owners(),
            'src/bhsm/interface/muon_d5_complement_event_return.py':pin(ROOT/'src/bhsm/interface/muon_d5_complement_event_return.py'),
            Path(__file__).relative_to(ROOT).as_posix():pin(Path(__file__))},
        archives=save_groups(output,returned,'returned'),event_consumption=consumed,
        original_birth_corner_incidence=corner,
        preserved_native_clock_density_contact=old['evaluated_native_incidence_contacts'],
        preserved_ancestry=old['preserved_ancestry'],
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        physical_guard=2e-10,physical_admission=False,
        full_normal_profile_normalizations=None,physical_outer_residual=None,
        full_child_D5_residual=None,full_event_residual=None,full_formation_residual=None,
        whole_local_removal_repeated=False,seam_added_as_bulk_mass=False,
        NEXT_OPERAND='match the saved incoming bulk Cauchy/Green family to the actual event/child and retarded outer equations; determine the retained homogeneous data and independent normal profiles jointly with mechanical formation KKT')
    (output/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(stage='EVENT_APPLICATION_SAVED',result_sha256=pin(output/'result.json'),
        event_consumption=consumed)),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--resume',action='store_true')
    p.add_argument('--core-only',action='store_true')
    p.add_argument('--radial-steps',type=int,default=1)
    p.add_argument('--reuse-core-from',type=Path)
    a=p.parse_args();run(a.output_dir,resume=a.resume,core_only=a.core_only,
        radial_steps=a.radial_steps,reuse_core_from=a.reuse_core_from)
