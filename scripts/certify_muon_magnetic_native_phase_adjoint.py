"""Outward source/adjoint contractions of the executed native phase systems."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.muon_primal_native_phase_adjoint import native_phase_named_border
from bhsm.interface.muon_native_adjoint_arithmetic import certify_native_adjoint_contractions
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(application_directory,output,*,precision_bits=192):
    folder=Path(application_directory);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier certificates')
    md=json.loads((folder/'result.json').read_text(encoding='utf8'))
    if md['classification']!='EVALUATED_CHRONOLOGICAL_NATIVE_TARGET_ADJOINT_ON_ACTUAL_CUBIC_MEAN_LOAD':
        raise ValueError('actual chronological native target application required')
    if sha256((folder/'application.npz').read_bytes()).hexdigest()!=md['array_archive']['sha256']:
        raise ValueError('executed contraction archive changed')
    hashes=dict(md['input_hashes'])
    refs=[folder/'result.json',folder/'application.npz',Path(__file__),ROOT/'src/bhsm/interface/muon_native_adjoint_arithmetic.py']
    hashes.update({p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    with np.load(folder/'application.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
    exports={};records=[]
    for side in ('incoming','outgoing'):
        names=[name for name in hashes if name.endswith('/result.json') and f'attached_phase_{side}_1steps_run_1/' in name]
        if len(names)!=1:raise ValueError('unique unchanged actual primal cell required')
        phase=json.loads((ROOT/names[0]).read_text(encoding='utf8'))
        rep=load_attached_endpoint(phase['consumed_paired_endpoint_path'],side=side)['representation']
        J=arrays[side+'_chronological_J']
        for frame in ('temporal','radial'):
            print(json.dumps(dict(stage='exact_stored_native_target_adjoint',side=side,frame=frame)),flush=True)
            K=native_phase_named_border(J,rep,frame=frame)['matrix'];size=len(J)
            keys=[side+'_q_'+str(q).replace('.','p')+'_'+frame for q in (.25,1.,4.)]
            F=arrays[keys[0]+'_phase_source_rows'].reshape(size,-1)
            if not all(np.array_equal(F,arrays[key+'_phase_source_rows'].reshape(size,-1)) for key in keys):
                raise ValueError('cutoff target must share one exact executed source load')
            rhs=np.vstack((-F,np.zeros((2,F.shape[1]))))
            readout=np.zeros((5,size+2))
            for j,key in enumerate(keys):readout[j,:size]=arrays[key+'_phase_target_row']
            readout[3:,size:]=np.eye(2)
            cert=certify_native_adjoint_contractions(K,rhs,readout,precision_bits=precision_bits)
            label=side+'_'+frame
            for name,value in cert.items():
                if isinstance(value,np.ndarray):exports[label+'_'+name]=value
            refs=np.array([arrays[key+'_native_mean_response_pair'].ravel() for key in keys])
            lower,upper=cert['contraction_lower'][:3],cert['contraction_upper'][:3]
            maximum_difference=float(np.max(np.maximum(abs(refs-lower),abs(refs-upper))))
            records.append(dict(side=side,frame=frame,precision_bits=precision_bits,
                exact_stored_adjoint_residual_upper=cert['exact_stored_adjoint_residual_upper'],
                independent_first_column_forward_adjoint_difference_upper=cert['independent_first_column_forward_adjoint_difference_upper'],
                contraction_lower=lower.reshape(3,8,8).tolist(),contraction_upper=upper.reshape(3,8,8).tolist(),
                q_probes=[.25,1.,4.],binary64_contraction_absolute_difference_upper=maximum_difference,
                auxiliary_Gauss_reaction_lower=cert['contraction_lower'][3:].reshape(2,8,8).tolist(),
                auxiliary_Gauss_reaction_upper=cert['contraction_upper'][3:].reshape(2,8,8).tolist(),
                original_rows_removed=False,stored_operator_certified_invertible=cert['stored_operator_certified_invertible']))
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:
        raise RuntimeError('consumed application changed during certification')
    out.mkdir(parents=True);archive=out/'certificate.npz';deterministic_archive(archive,exports)
    result=dict(classification='OUTWARD_EXACT_STORED_CHRONOLOGICAL_NATIVE_ADJOINT_CONTRACTIONS',input_hashes=hashes,
        archive=dict(path=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),
        applications=records,all64_source_pair_contractions_enclosed=True,
        full_forward_mean_response_materialized=False,physical_Pauli_or_anomaly_enclosed=False,
        error_scope='exact supplied binary64 phaseJacobian, native target row and complete action load; source/operator formation, cutoff selection, continuum, completion, overlap and softPauli errors excluded')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],
        checks=[{k:r[k] for k in ('side','frame','exact_stored_adjoint_residual_upper','binary64_contraction_absolute_difference_upper')} for r in records])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--application-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--precision-bits',type=int,default=192);a=p.parse_args()
    print(json.dumps(materialize(a.application_directory,a.output,precision_bits=a.precision_bits),sort_keys=True))
