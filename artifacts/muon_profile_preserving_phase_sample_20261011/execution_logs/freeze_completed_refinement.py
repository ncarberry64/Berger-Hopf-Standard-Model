"""Pin completed independent replays without running any producer again."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parents[1]

def save(path,data):
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')

pairs=[];files=[];dependencies={}
for stem in ('incoming_sample','outgoing_sample','incoming_2steps','incoming_4steps','outgoing_2steps','outgoing_4steps'):
    for filename in ('result.json','application.npz'):
        paths=[folder/f'{stem}_run_{run}'/filename for run in (1,2)]
        first,second=[p.read_bytes()for p in paths]
        if first!=second:raise ValueError('replay changed: '+stem+'/'+filename)
        files.extend(paths)
        pairs.append(dict(application=stem,filename=filename,byte_identical=True,bytes=len(first),sha256=sha256(first).hexdigest()))
    receipt=json.loads((folder/f'{stem}_run_1/result.json').read_text())
    dependencies.update(receipt['input_hashes'])

rows=[]
for side in ('incoming','outgoing'):
    first=ROOT/('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    paths=[first]+[folder/f'{side}_{n}steps_run_1'for n in (2,4)]
    arrays=[]
    for steps,path in zip((1,2,4),paths):
        md=json.loads((path/'result.json').read_text())
        with np.load(path/'application.npz',allow_pickle=False)as z:arrays.append({k:z[k].copy()for k in ('x_final','p_final')})
        rows.append(dict(side=side,steps=steps,all_stages_converged=all(s['status']=='REPRESENTED_PHASE_TOLERANCE'for s in md['stages']),
            maximum_stage_scaled_residual=max(s['scaled_residual']for s in md['stages']),
            represented_stage_ranks=sorted({h['rank']for s in md['stages']for h in s['history']})))
    for k in ('x_final','p_final'):
        errors=[float(np.linalg.norm(arrays[n+1][k]-arrays[n][k]))for n in (0,1)]
        rows.append(dict(side=side,quantity=k,one_to_two_norm=errors[0],two_to_four_norm=errors[1],ratio=errors[0]/errors[1],
            interpretation='observed refinement of the same finite signed interval, not a certified continuum or physical-history error'))

sample_norms=[]
for side in ('incoming','outgoing'):
    with np.load(folder/f'{side}_sample_run_1/application.npz',allow_pickle=False)as z:
        norms=np.linalg.norm(z['W_coordinate_time'],axis=(1,2));proper=np.linalg.norm(z['W_proper_time'],axis=(1,2))
        sample_norms.append(dict(side=side,samples=len(norms),aggregate_Frobenius_coordinate_rate=float(np.linalg.norm(z['W_coordinate_time'])),
            individual_coordinate_rate_norms=norms.tolist(),individual_proper_rate_norms=proper.tolist(),
            aggregate_is_over_all_sample_axes=True))

for path,digest in dependencies.items():
    if sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('consumed owner changed: '+path)
summary=dict(classification='VERIFIED_SAME_GERM_PROFILE_PRESERVING_SAMPLE_AND_TEMPORAL_REFINEMENT',pairs=pairs,refinement=rows,
    sample_norms=sample_norms,sampling_scope='solved midpoint cells: x affine, v/y fixed per cell; explicit parent/reference affine clock composed once',
    physical_history_or_mode_or_cutoff_or_Pauli_selected=False,
    error_scope='independent byte replay and observed binary64 temporal refinement only; no rigorous action-rounding or continuum error bound')
save(folder/'refinement_pair_verification.json',summary)
files.extend([folder/'sample_verification.json',folder/'refinement_verification.json',folder/'refinement_verification_run_2.json',folder/'refinement_pair_verification.json'])
files.extend(sorted((folder/'execution_logs').glob('*')))
files.extend([ROOT/'src/bhsm/interface/muon_profile_preserving_phase_sample.py',ROOT/'tests/test_muon_profile_preserving_phase_sample.py'])
pins={}
for path in files:
    data=path.read_bytes()
    if len(data)>10*1024**2:raise ValueError('publication cap exceeded: '+str(path))
    if path.suffix in ('.json','.py','.txt')and b'\r\n'in data:raise ValueError('text is not canonical LF: '+str(path))
    pins[path.relative_to(ROOT).as_posix()]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
manifest=dict(classification=summary['classification'],files=pins,dependencies=dependencies,
    proper_rate_norm_scope='aggregate sampler receipt norms are Frobenius over every sample; individual point norms are recorded in refinement_pair_verification.json',
    physical_history_or_mode_or_cutoff_or_Pauli_selected=False,error_scope=summary['error_scope'])
save(folder/'publication_manifest.json',manifest)
print(json.dumps(dict(files=len(pins),manifest_sha256=sha256((folder/'publication_manifest.json').read_bytes()).hexdigest(),refinement=rows,sample_norms=sample_norms),sort_keys=True))
