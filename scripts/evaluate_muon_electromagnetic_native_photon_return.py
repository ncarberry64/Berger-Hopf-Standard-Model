"""Apply the executed paired fermion source form to its coupled photon action.

Both forms are pullbacks to the same eight compact source coefficients.
The stored midpoint heat restriction is retained explicitly.  This is
not an assertion that those source coefficients are physical soft momentum,
or that the partial trace is the completed disjoint native functional.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_electromagnetic_source_photon_action import (
    executed_electromagnetic_photon_quadratic_action,stable_native_photon_return,
)
from evaluate_muon_native_product_factor_graph import serial,deterministic_npz


def materialize(pair_directory,responses,output,*,precision_bits=192):
    folder=Path(pair_directory);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve executed applications')
    md=json.loads((folder/'source_pair.json').read_bytes())
    if md['classification']!='EVALUATED_SAME_ELECTROMAGNETIC_CELL_GRADED_DIRECT_PLUS_MEAN_FERMION_SOURCE_PAIR':
        raise ValueError('same-background contact, both insertions and mean required')
    archive=folder/md['archive']['path'];data=archive.read_bytes()
    if len(data)!=md['archive']['bytes'] or sha256(data).hexdigest()!=md['archive']['sha256']:
        raise ValueError('executed source pair changed')
    hashes=dict(md['input_hashes'])
    for name,digest in hashes.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('consumed action changed: '+name)
    for p in (folder/'source_pair.json',archive,Path(__file__),
              ROOT/'src/bhsm/interface/muon_electromagnetic_source_photon_action.py'):
        hashes[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    with np.load(archive,allow_pickle=False) as f:pairs={k:f[k].copy() for k in f.files}
    arrays={};arms=[]
    for side,response in responses.items():
        print(json.dumps(dict(stage='coupled_source_action_and_stable_native_photon_return',side=side)),flush=True)
        bare=executed_electromagnetic_photon_quadratic_action(response,repository=ROOT)
        if bare['side']!=side:raise ValueError('same response arm required')
        for name,digest in bare['input_hashes'].items():
            if name in hashes and hashes[name]!=digest:
                raise ValueError('bare and native forms must consume the SAME response: '+name)
            # The mean/direct binder reads the first-field arrays, whereas
            # the bare action additionally reads the weak-form archive.  The
            # identical hashed producer receipt owns BOTH sets of arrays.
            # Verify that receipt before accepting this transitive binding.
            if name not in md['input_hashes']:
                path=ROOT/name;owner=path.parent/'result.json'
                rel=owner.relative_to(ROOT).as_posix()
                if rel not in md['input_hashes'] or sha256(owner.read_bytes()).hexdigest()!=md['input_hashes'][rel]:
                    raise ValueError('native source pair did not bind bare response owner: '+name)
                record=json.loads(owner.read_bytes())['array_archives'].get(path.name)
                if record is None or record['sha256']!=digest:
                    raise ValueError('bare weak form is not in the same producer receipt: '+name)
            hashes[name]=digest
        for name,value in bare.items():
            if isinstance(value,np.ndarray):arrays[side+'_bare_'+name]=value
        arm=next(a for a in md['arms'] if a['side']==side);rows=[]
        for application in arm['applications']:
            q=application['q_probe'];frames=[]
            for frame in ('temporal','radial'):
                label=side+'_q_'+str(q).replace('.','p')+'_'+frame
                R=pairs[label+'_graded_source_pair']
                a=stable_native_photon_return(bare['source_quadratic_action'],R,precision_bits=precision_bits)
                arrays[label+'_applied_graded_form']=R
                for name,value in a.items():
                    if isinstance(value,np.ndarray):arrays[label+'_'+name]=value
                frames.append(dict(frame=frame,stable_native_return_norm=float(np.linalg.norm(a['stable_native_return'])),
                    inverse_residual_upper=a['exact_stored_inverse_residual_upper'],
                    return_identity_defect_upper=a['exact_stored_return_identity_defect_upper'],
                    native_form_lost_in_binary64_addition=a['native_form_lost_in_binary64_addition'],
                    spectral_conditioning_shift_added=False))
            rows.append(dict(q_probe=q,cutoff_probe=application['cutoff_probe'],frames=frames))
        arms.append(dict(side=side,action_parameters=bare['action_parameters'],
            source_action_eigenvalues=bare['source_quadratic_eigenvalues'].tolist(),
            full_raw_vs_reduced_action_relative_difference=bare['full_raw_vs_reduced_action_relative_difference'],
            source_action_symmetry_rounding_norm=bare['source_action_symmetry_rounding_norm'],applications=rows))
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:
        raise RuntimeError('consumed source changed during application')
    out.mkdir(parents=True);data=deterministic_npz(arrays);(out/'response.npz').write_bytes(data)
    result=dict(classification='EVALUATED_STABLE_PHOTON_RETURN_OF_SAME_BACKGROUND_PARTIAL_FERMION_SOURCE_FORM',
        input_hashes=hashes,archive=dict(path='response.npz',bytes=len(data),sha256=sha256(data).hexdigest()),arms=arms,
        precision_bits=precision_bits,photon_equation='(A0+R)U=I; native_return=-A0^(-1) R U=U-A0^(-1)',
        source_action='full unreduced Maxwell/Higgs on the actual coupled488 source solution; complete temporal and conormal contacts',
        source_scope='eight inherited compact-pulse coefficients; midpoint coefficient-cell native approximation pulled back through the same actual first responses',
        same_background_and_source_owners_verified=True,contact_both_insertions_and_mean_retained=True,
        microscopic_fermion_statistics_inserted_once=True,full_local_overlap_subtraction_applied=False,
        completed_disjoint_R_ind=False,physical_EM_current_or_soft_transfer_selected=False,
        complete_a_mu=None,complete_g_mu=None,complete_observable=False,
        error_scope='outward exact stored finite source inverse/return only; bare action formation and quadrature, midpoint heat restriction, higher Y, full domain/trace, relative completion, local overlap, cutoff and normalized Pauli errors excluded')
    (out/'result.json').write_text(json.dumps(serial(result),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],arms=arms)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pair-directory',type=Path,required=True)
    p.add_argument('--incoming-response',type=Path,required=True);p.add_argument('--outgoing-response',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();print(json.dumps(materialize(a.pair_directory,
        dict(incoming=a.incoming_response,outgoing=a.outgoing_response),a.output,precision_bits=a.precision_bits),sort_keys=True))
