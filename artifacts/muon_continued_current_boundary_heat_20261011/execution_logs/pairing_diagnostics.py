"""Contract saved responses in their actual temporal L2/current pairing."""
from pathlib import Path
from hashlib import sha256
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_continued_current_boundary_heat import temporal_variable_gram
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(number):
    folder=ROOT/'artifacts/muon_continued_current_boundary_heat_20261011'/f'run_{number}'
    destination=folder.parent/f'pairing_run_{number}'
    if destination.exists():raise FileExistsError('preserve preceding pairing diagnostics')
    md=json.loads((folder/'result.json').read_bytes());refs={}
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    arrays={};records=[];previous={}
    for steps in (16,32):
        path=folder/f'joined_{steps}.npz';expected=md['array_archives'][path.name]['sha256']
        if sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('actual heat response changed')
        refs[path.relative_to(ROOT).as_posix()]=expected
        with np.load(path,allow_pickle=False)as a:data={k:a[k].copy()for k in a.files}
        source_folder=ROOT/'artifacts/muon_continued_current_factor_20261011/run_1'
        parts=[]
        for side in ('incoming','outgoing'):
            source=source_folder/f'{side}_{steps}.npz'
            refs[source.relative_to(ROOT).as_posix()]=sha256(source.read_bytes()).hexdigest()
            with np.load(source,allow_pickle=False)as a:parts.append(a['target_left_map'].copy())
        left=np.array([np.kron(a,np.eye(4))for a in np.concatenate(parts)])
        weighted=data['proper_cell_weights'][:,None,None]*left/2
        weighted[:-1]+=data['proper_cell_weights'][1:,None,None]*left[1:]/2
        target=weighted.transpose(1,0,2).reshape(24,-1)
        M=temporal_variable_gram(data['proper_cell_weights'],24)
        for label in ('c0','cprobe'):
            for axis in range(3):
                norms={};currents={}
                for key in ('response','square_contact','numerator_contact','Dirichlet_reference_response','boundary_return_response'):
                    value=data[f'{label}_magnetic_{axis}_'+key]
                    squared=float(np.trace(value.conj().T@M@value).real)
                    norms[key]=np.sqrt(max(0.,squared))
                    currents[key]=target@value
                    arrays[f'{steps}_{label}_{axis}_current_'+key]=currents[key]
                token=(label,axis)
                prior=previous.get(token)
                row=dict(steps_per_arm=steps,label=label,source_axis=axis,
                    proper_Gram_kernel_norms=norms,literal_current_kernel_norms={k:float(np.linalg.norm(v))for k,v in currents.items()},
                    full_current_refinement_difference=None if prior is None else float(np.linalg.norm(currents['response']-prior)),
                    current_domain_return_identity_max=float(np.max(abs(currents['response']-currents['Dirichlet_reference_response']-currents['boundary_return_response']))))
                previous[token]=currents['response'];records.append(row)
    for p in ('src/bhsm/interface/muon_continued_current_boundary_heat.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    destination.mkdir();archive=destination/'application.npz';_compressed_npz(archive,arrays)
    result=dict(classification='EVALUATED_SAVED_CURRENT_HEAT_RESPONSE_CANONICAL_PAIRING_DIAGNOSTICS',input_hashes=refs,
        archive=dict(bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),records=records,
        pairing='same actual proper-cell variable Gram and literal unit-charge n1 target; input kernel columns are canonical I6, not a selected state',
        no_physical_norm_or_Pauli_promotion=True,error_scope='binary64 saved-array pairings and refinements; no continuum or quantum/native error bound')
    (destination/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':materialize(int(sys.argv[1]))
