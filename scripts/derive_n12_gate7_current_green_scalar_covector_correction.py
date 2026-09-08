"""Correct the stored scalar Hessian's covector units with adjoint solves.

The original kernel contracts covectors evaluated on diag(weights) with
metric-coordinate vectors. Those covectors require division by weights.
Only the two affected contractions are recalculated; raw shards stay intact.
This supplies a binary64 center correction, not an outward error bound.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import sys,time,json,hashlib,argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import derive_n12_gate7_current_green_full_transverse_quadratic_center as c
import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery

WORK=ROOT/'artifacts/flagship_integration/.current_green_scalar_covector_correction_work'
ALGORITHM_ID='CURRENT_GREEN_SCALAR_COVECTOR_ADJOINT_CORRECTION_V1'

def _fingerprint():
    digest=hashlib.sha256(ALGORITHM_ID.encode())
    digest.update(recovery._fingerprint().encode())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest().upper()

def _path(kind,index):
    return WORK/f'{kind}_{index:03d}.npz'

def _valid(path,kind,index,fingerprint):
    try:
        with np.load(path) as source:
            value=source['scalar_correction']
            return bool(str(source['kind'].item())==kind and int(source['index'])==index
                and str(source['campaign_fingerprint'].item())==fingerprint
                and str(source['raw_shard_SHA256'].item())==recovery._sha(recovery._path(kind,index))
                and value.shape==(73,73) and np.all(np.isfinite(value))
                and np.isfinite(float(source['elapsed_seconds'])) and float(source['elapsed_seconds'])>0)
    except (OSError,ValueError,KeyError):
        return False

def corrected_tensor(kind,index):
    """Load the current raw tensor plus its separately stored scalar correction."""
    path=_path(kind,index)
    if not _valid(path,kind,index,_fingerprint()):
        raise RuntimeError(f'Current scalar covector correction required: {kind} {index}')
    with np.load(recovery._path(kind,index)) as source:
        tensor=source['quadratic_tensor'].copy();basis=source['transverse_basis'].copy()
    with np.load(path) as source:
        tensor[-1]+=source['scalar_correction']
    return tensor,basis

def correction(state,descriptor,weights,reference,directions):
    """Return the correction to the last output, before symmetrization.

Adjoint bordered solves contract the second eigenvector/response derivatives
against their scalar covectors before forming action derivative tensors.
The raw eigenline orientation is required to agree with its eigenbasis.
"""
    qdim,red=c.QDIM,c.REDUCED
    qw,rw,_,_=c.metric_data()
    gradient,hessian=c._exact_jet(state);gradient=np.asarray(gradient,float);hessian=np.asarray(hessian,float)
    h=.5*(hessian[qdim:,qdim:]+hessian[qdim:,qdim:].T)
    eigenvalues,eigenvectors=np.linalg.eigh(h);psi=eigenvectors[:,c.SELECTED]
    if psi@reference<0: raise RuntimeError('Raw eigenline orientation requires separate correction')
    lift=np.zeros((c.STATE,red));lift[qdim:]=rw[:,None]*np.eye(red)
    u=directions[:c.STATE];n=u.shape[1];raw=u/weights[:,None]
    config=qw*state[qdim:2*qdim];config_v=qw[:,None]*raw[qdim:2*qdim]
    ca=np.zeros(c.STATE);ca[:qdim]=config
    ca_v=np.zeros((c.STATE,n));ca_v[:qdim]=config_v
    ha=hessian/weights[:,None]/weights[None,:]
    force=rw*(np.r_[qw*gradient[:qdim]/weights[:qdim],np.zeros(red-qdim)]-ha[qdim:,:qdim]@config)
    k=np.block([[h-eigenvalues[c.SELECTED]*np.eye(red),psi[:,None]],[psi[None,:],np.zeros((1,1))]])
    response=np.linalg.solve(k,np.r_[force,0.]);hard=response[:-1];bp=response[-1]
    pa=lift@psi;hra=lift@hard
    first=c._signed(state,lift,u,np.column_stack((pa,hra,ca)))
    hp,hh,hc=first[:,:,0],first[:,:,1],first[:,:,2]
    slopes=psi@hp;other=np.arange(red)!=c.SELECTED
    coeff=eigenvectors.T@hp;coeff[other]/=-(eigenvalues[other]-eigenvalues[c.SELECTED])[:,None];coeff[c.SELECTED]=0
    pv=eigenvectors@coeff
    grad_v=hessian@raw
    force_v=rw[:,None]*np.vstack((qw[:,None]*grad_v[:qdim]/weights[:qdim,None],np.zeros((red-qdim,n))))-hc-rw[:,None]*(ha[qdim:,:qdim]@config_v)
    kv_response=np.vstack((hh-hard[:,None]*slopes+bp*pv,pv.T@hard))
    rv=np.linalg.solve(k,np.vstack((force_v,np.zeros((1,n))))-kv_response)
    hv,bv=rv[:-1],rv[-1]
    last=np.column_stack((pa,np.r_[config,rw*hard]))
    cov=c._signed(state,np.diag(weights),pa,last)
    last_cov=c._signed(state,pa,pa,np.diag(weights))
    delta=1/weights-1;cov=cov*delta[:,None];last_cov=last_cov*delta
    cp=rw*(bp*(2*cov[qdim:,0]+last_cov[qdim:])+descriptor*2*cov[qdim:,1])
    ch=descriptor*rw*last_cov[qdim:]
    z=np.linalg.solve(k.T,np.r_[ch,0.]);zt,zs=z[:-1],z[-1]
    cp=cp-bp*zt-zs*hard
    eta=np.linalg.solve(k.T,np.r_[cp,0.]);et,es=eta[:-1],eta[-1]
    za,ea=lift@zt,lift@et
    lambda_coefficient=float(zt@hard+et@psi)
    fourth=c._signed(state,np.column_stack((ea,za,pa)),u,u,np.column_stack((pa,hra,ca)))
    eigen_cross=pv.T@hp
    lambda_vv=fourth[2,:,:,0]+eigen_cross+eigen_cross.T
    e_h_pv=c._signed(state,ea,u,lift@pv)
    eigen_terms=-fourth[0,:,:,0]-e_h_pv-e_h_pv.T
    ev=et@pv
    eigen_terms+=slopes[:,None]*ev[None,:]+ev[:,None]*slopes[None,:]
    eigen_terms-=es*(pv.T@pv)
    # z applied to the raw gradient part of forcing_VV.
    grad_cov=np.zeros(c.STATE);grad_cov[:qdim]=rw[:qdim]*qw*zt[:qdim]/weights[:qdim]
    forcing_second=c._signed(state,weights*grad_cov,u,u)
    forcing_cross=c._signed(state,za,u,ca_v)
    forcing_second-=forcing_cross+forcing_cross.T+fourth[1,:,:,2]
    response_cross=c._signed(state,za,u,lift@hv)
    zh=zt@hv;zp=zt@pv
    response_cross-=slopes[:,None]*zh[None,:]
    response_cross+=zp[:,None]*bv[None,:]+zs*(pv.T@hv)
    total=eigen_terms+forcing_second-fourth[1,:,:,1]+lambda_coefficient*lambda_vv-response_cross-response_cross.T
    numerator=np.r_[descriptor*config,rw*(bp*psi+descriptor*hard)]
    return total/np.linalg.norm(numerator)

def _worker(kind,indices):
    inputs=c._load_inputs();states,ds,tangents=inputs[kind][:3]
    fingerprint=_fingerprint();raw_fingerprint=recovery._fingerprint()
    WORK.mkdir(parents=True,exist_ok=True)
    for index in indices:
        path=_path(kind,index)
        if _valid(path,kind,index,fingerprint):
            continue
        raw=recovery._path(kind,index)
        if not recovery._valid(raw,kind,index,raw_fingerprint):
            raise RuntimeError(f'Validated raw shard required: {kind} {index}')
        raw_sha=recovery._sha(raw)
        with np.load(raw) as source:basis=source['transverse_basis'].copy()
        directions=c._frame(tangents[index])@basis
        started=time.perf_counter()
        value=correction(states[index],float(ds[index]),inputs['weights'],inputs['reference'],directions)
        elapsed=time.perf_counter()-started
        if value.shape!=(73,73) or not np.all(np.isfinite(value)):
            raise RuntimeError('Nonfinite or incompatible scalar correction')
        if _fingerprint()!=fingerprint or recovery._sha(raw)!=raw_sha:
            raise RuntimeError('Correction inputs changed')
        temporary=path.with_suffix('.tmp.npz')
        np.savez_compressed(temporary,scalar_correction=value,kind=np.asarray(kind),index=np.asarray(index),
            raw_shard_SHA256=np.asarray(raw_sha),campaign_fingerprint=np.asarray(fingerprint),
            elapsed_seconds=np.asarray(elapsed))
        temporary.replace(path)
        print(json.dumps(dict(kind=kind,index=index,elapsed_seconds=elapsed,maximum_correction=float(np.max(abs(value))))),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--kind',choices=('endpoint','midpoint'),required=True)
    parser.add_argument('--indices',required=True)
    parser.add_argument('--workers',type=int,default=1)
    args=parser.parse_args();indices=[int(v) for v in args.indices.split(',')]
    allowed=range(1,371) if args.kind=='endpoint' else range(370)
    if len(set(indices))!=len(indices) or not indices or any(i not in allowed for i in indices) or not 1<=args.workers<=6:
        raise ValueError('Distinct valid indices and one to six workers required')
    if args.workers==1:
        _worker(args.kind,indices)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            jobs=[pool.submit(_worker,args.kind,indices[offset::args.workers]) for offset in range(args.workers)]
            for job in as_completed(jobs):job.result()

if __name__=='__main__':
    main()
