"""Evaluate the same magnetic boundary action with the true-birth native mean."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_chronological_native_return import enclosed_chronological_magnetic_return
from bhsm.interface.muon_magnetic_source_photon_action import executed_magnetic_photon_quadratic_action
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,contact_directory,*,precision_bits=192):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    folder=Path(contact_directory);folder=folder if folder.is_absolute() else ROOT/folder
    if out.exists():raise FileExistsError('preserve previous boundary applications')
    md=json.loads((folder/'result.json').read_bytes())
    if md['classification']!='EVALUATED_SAME_MAGNETIC_CELL_DIRECT_PLUS_TRUE_BIRTH_CHRONOLOGICAL_MEAN_HEAT':
        raise ValueError('same-background contact and true-birth chronological mean required')
    if md['active_source_indices']!=[0,1,2] or md['inactive_padded_source_indices']!=[3,4,5,6,7]:
        raise ValueError('the actual magnetic source has three axes and the retained exact zero inclusion')
    archive=folder/md['archive']['path'];data=archive.read_bytes()
    if len(data)!=md['archive']['bytes'] or sha256(data).hexdigest()!=md['archive']['sha256']:
        raise ValueError('consumed chronological application changed')
    refs=dict(md['input_hashes'])
    for name,digest in refs.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('consumed owner changed: '+name)
    for path in (folder/'result.json',archive,Path(__file__),ROOT/'src/bhsm/interface/muon_chronological_native_return.py',
                 ROOT/'src/bhsm/interface/muon_magnetic_native_return_enclosure.py',ROOT/'src/bhsm/interface/muon_magnetic_source_photon_action.py'):
        refs[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
    with np.load(archive,allow_pickle=False) as f:contacts={key:f[key].copy() for key in f.files}
    arrays={};records=[]
    for side in ('incoming','outgoing'):
        names=[name for name in refs if name.endswith('/result.json') and
               '/muon_electromagnetic_soft_magnetic_source_' in name and '/'+side+'_run_' in name]
        if len(names)!=1:raise ValueError('unique actual same-arm magnetic source owner required')
        response=(ROOT/names[0]).parent
        print(json.dumps(dict(stage='same_action_chronological_native_boundary_return',side=side)),flush=True)
        bare=executed_magnetic_photon_quadratic_action(response,repository=ROOT)
        if bare['side']!=side:raise ValueError('same arm required')
        for name,digest in bare['input_hashes'].items():
            if name in refs and refs[name]!=digest:raise ValueError('bare and native background/source differ: '+name)
            if name not in refs:
                path=ROOT/name;owner=path.parent/'result.json';rel=owner.relative_to(ROOT).as_posix()
                if rel not in refs or sha256(owner.read_bytes()).hexdigest()!=refs[rel]:
                    raise ValueError('bare weak action not bound by the native source producer: '+name)
                record=json.loads(owner.read_bytes())['array_archives'].get(path.name)
                if record is None or record['sha256']!=digest:raise ValueError('bare weak archive has another owner')
            refs[name]=digest
        arrays[side+'_bare_source_action']=bare['source_quadratic_action']
        for row in (r for r in md['records'] if r['side']==side):
            label=side+'_q_'+str(row['q_probe']).replace('.','p')
            direct=contacts[label+'_direct_source_contact_and_both_insertions']
            mean=contacts[label+'_mean_contact']
            if any(np.any(a[3:]) or np.any(a[:,3:]) for a in (direct,mean)):
                raise ValueError('literal exact stored direct/mean source inclusion differs')
            # The physical domain has three coordinates. The upstream
            # encloser may outward-round exact padded zeros to subnormals;
            # select the actual source inclusion, preserving those full
            # intervals in the immutable producer, before padding here.
            result=enclosed_chronological_magnetic_return(bare['source_quadratic_action'],
                direct[:3,:3],contacts[label+'_mean_contact_lower'][:3,:3],
                contacts[label+'_mean_contact_upper'][:3,:3],precision_bits=precision_bits)
            for name,value in result.items():
                if isinstance(value,np.ndarray):arrays[label+'_'+name]=value
            record=dict(side=side,q_probe=row['q_probe'],common_cutoff_probe=row['cutoff_probe'],
                stable_native_boundary_return_norm=float(np.linalg.norm(result['stable_native_return'])),
                interval_inverse_residual_upper=result['interval_inverse_residual_upper'],
                interval_return_identity_defect_upper=result['interval_return_identity_defect_upper'],
                bare_source_action_eigenvalues=np.linalg.eigvalsh(bare['source_quadratic_action'][:3,:3]).tolist(),
                full_raw_vs_reduced_action_relative_difference=bare['full_raw_vs_reduced_action_relative_difference'])
            records.append(record);print(json.dumps(record,sort_keys=True),flush=True)
    if any(sha256((ROOT/name).read_bytes()).hexdigest()!=digest for name,digest in refs.items()):
        raise RuntimeError('consumed source changed during boundary return')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_SAME_ACTION_MAGNETIC_NATIVE_RETURN_WITH_TRUE_BIRTH_CHRONOLOGICAL_MEAN',
        input_hashes=refs,archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,
            sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),records=records,
        photon_equation='(A0+R)U=I; native_return=-A0^-1 R U=U-A0^-1',
        source_action='unreduced Maxwell/Higgs on actual sourced488 fields; material temporal and conormal contacts retained',
        native_source_form='same-background direct contact and both ordered insertions plus actual true-birth propagated mean; fermion +1/2 once',
        active_source_indices=[0,1,2],inactive_padded_axes=[3,4,5,6,7],precision_bits=precision_bits,
        inherited_parent_fixed_q_normal_mean_restriction=True,proper_time_cutoff_physically_selected=False,
        full_quantum_photon_covariance_or_disjoint_R_ind_or_Pauli_completed=False,
        local_overlap_subtraction_applied=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='Arb inverse/return of exact stored bare/direct and certified stored chronological mean entry intervals; source/target formation, Y/tent/continuum, full native/domain completion and external Pauli matching excluded')
    if result['archive']['bytes']>10*1024**2:raise ValueError('lossless archive exceeds retained publication cap')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--contact-directory',type=Path,default=Path('artifacts/muon_magnetic_chronological_heat_contact_20261011/run_1'))
    p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();print(json.dumps(materialize(a.output,a.contact_directory,precision_bits=a.precision_bits),sort_keys=True))
