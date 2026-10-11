"""Apply canonical fixed-Y currents and both magnetic angular insertions."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_joined_common_y_current import (
    block_current_coefficients,rectangular_block_source_jet,midpoint_current_coefficients)
from bhsm.interface.muon_common_y_current_response import paired_fixed_y_polynomial
from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_current_angular_images
from evaluate_muon_reached_trace_action import deterministic_archive


def angular_action(data,derivatives):
    h=derivatives.shape[1];I=np.eye(6*h);weights=data['proper_cell_weights']
    H0=np.array([np.kron(a,np.eye(h))-1j*sum(np.kron(v,e)for v,e in zip(data['alpha6'],derivatives))/r
        for a,r in zip(data['common_Hcan0'],data['R4'])])
    H1=np.array([np.kron(a,np.eye(h))for a in data['common_Hcan1']])
    return (-1j*I[None]/weights[:,None,None]+H0/2,
        1j*I[None]/weights[:,None,None]+H0/2,H1/2,H1/2,
        np.array([np.kron(a,np.eye(h))for a in data['source_right_map']]),
        np.array([np.kron(a,np.eye(h))for a in data['target_left_map']]))


def source_adjoint_coefficients(action,left,weights,*,split,order):
    d,l,b,c=action[:4]
    weighted=weights[:,None,None]*left/2
    nodal=weighted.copy();nodal[:-1]+=weighted[1:]
    # The represented common birth frame is I; both action and current
    # use that identical transport. A full F_B/U is not inferred.
    def reverse_lower(a):
        out=np.zeros_like(a)
        out[1:]=a[:0:-1].swapaxes(-1,-2)
        return out
    r=nodal.swapaxes(-1,-2)[::-1][None]
    adj=block_current_coefficients(d[::-1].swapaxes(-1,-2),reverse_lower(l),
        b[::-1].swapaxes(-1,-2),reverse_lower(c),r,order=order)
    return adj['coefficients'][:,::-1]


def materialize(output,*,input_folder=Path('artifacts/muon_continued_current_factor_20261011/run_1'),refinements=(16,32,64),order=4):
    out=ROOT/output;folder=ROOT/input_folder
    if out.exists():raise FileExistsError('preserve earlier joined source applications')
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    images=magnetic_current_angular_images();G=images['gaunt_even_odd_source'][:10,:4]
    derivatives=(np.zeros((3,1,1)),images['derivatives']['field_odd'][:,:4,:4],images['derivatives']['even'][:,:10,:10])
    records=[];pending=[];previous={}
    for steps in refinements:
        parts=[]
        for side in('incoming','outgoing'):
            p=folder/f'{side}_{steps}.npz';h=sha256(p.read_bytes()).hexdigest()
            if h!=md['array_archives'][p.name]['sha256']:raise ValueError('canonical coefficient export changed')
            refs[p.relative_to(ROOT).as_posix()]=h
            with np.load(p,allow_pickle=False)as a:parts.append({k:a[k].copy()for k in a.files})
        data={k:np.concatenate([a[k]for a in parts])for k in
            ('common_Hcan0','common_Hcan1','proper_cell_weights','R4','source_right_map','target_left_map','magnetic_Xi0','magnetic_Xi1')}
        data['alpha6']=parts[0]['alpha6'];ys=parts[0]['family_Y'][1:]
        if not np.array_equal(parts[0]['family_Y'],parts[1]['family_Y']):raise ValueError('same fixed family Y required')
        if np.any(data['magnetic_Xi0'][:,:3,4:])or np.any(data['magnetic_Xi1'][:,:3,4:]):
            raise ValueError('nonzero n3 source requires larger angular output; no truncation')
        actions=[angular_action(data,E)for E in derivatives];weights=data['proper_cell_weights'];arrays={};states=[];adjoints=[]
        for n,action in zip((0,1,2),actions):
            r=block_current_coefficients(*action[:4],action[4][None],order=order)
            z=source_adjoint_coefficients(action,action[5],weights,split=steps,order=order)
            current=midpoint_current_coefficients(action[5],weights,r['coefficients'],birth_index=steps,birth_transport=np.eye(len(action[0][0])))
            dual=np.einsum('ktim,tij->kmj',z,action[4])
            arrays[f'angular_{n}_current_coefficients']=current
            arrays[f'angular_{n}_original_residuals']=r['original_recurrence_residuals']
            arrays[f'angular_{n}_current_primal_adjoint_difference']=current-dual
            arrays[f'angular_{n}_birth_trace_coefficients']=r['coefficients'][:,steps-1]
            states.append(r['coefficients']);adjoints.append(z)
        for kind,target,source in(('constant',1,0),('momentum',2,1)):
            forward=[];reverse=[];diffs=[]
            for axis in range(3):
                if kind=='constant':
                    d=np.array([data[f'magnetic_Xi{k}'][:,axis,:4].transpose(0,2,1,3).reshape(2*steps,24,6)/2 for k in(0,1)])
                    dr=np.array([data[f'magnetic_Xi{k}'][:,axis,:4].transpose(0,2,3,1).reshape(2*steps,6,24)/2 for k in(0,1)])
                else:
                    d=np.array([np.einsum('hks,tsij->tihjk',G,data[f'magnetic_Xi{k}'][:,axis,:4]).reshape(2*steps,60,24)/2 for k in(0,1)])
                    dr=np.array([np.einsum('hks,tsij->tikjh',G,data[f'magnetic_Xi{k}'][:,axis,:4]).reshape(2*steps,24,60)/2 for k in(0,1)])
                for placement,ta,sa,delta,collection in(('forward',target,source,d,forward),('reverse',source,target,dr,reverse)):
                    f=rectangular_block_source_jet(states[sa],*actions[ta][:4],delta,delta,order=order)
                    current=midpoint_current_coefficients(actions[ta][5],weights,f['coefficients'],birth_index=steps,birth_transport=np.eye(len(actions[ta][0][0])))
                    # Same analytic transpose-adjoint, before any state or
                    # charge projection; delta source acts on both halves.
                    effective=np.zeros_like(f['coefficients'])
                    for k in range(order+1):
                        for q in range(min(k+1,len(delta))):
                            effective[k]-=delta[q]@states[sa][k-q]
                            effective[k,1:]-=delta[q,1:]@states[sa][k-q,:-1]
                    dual=np.array([sum(np.einsum('tim,tij->mj',adjoints[ta][j],effective[k-j])for j in range(k+1))for k in range(order+1)])
                    arrays[f'{kind}_{placement}_{axis}_original_residuals']=f['original_recurrence_residuals']
                    arrays[f'{kind}_{placement}_{axis}_primal_adjoint_difference']=current-dual
                    collection.append(current);diffs.append(np.linalg.norm(current-dual))
            for placement,value in(('forward',forward),('reverse',reverse)):
                arrays[f'{kind}_{placement}_coefficients']=np.array(value)
                pair=np.array([paired_fixed_y_polynomial(v,*ys)for v in value])
                arrays[f'paired_{kind}_{placement}']=pair
                key=f'{kind}_{placement}'
                records.append(dict(steps_per_arm=steps,kind=kind,placement=placement,
                    paired_current_norm=float(np.linalg.norm(pair)),all_coefficient_primal_adjoint_difference_norm=float(np.linalg.norm(diffs)),
                    refinement_difference=None if key not in previous else float(np.linalg.norm(pair-previous[key]))))
                previous[key]=pair
        arrays['fixed_middle_light_Y']=ys
        pending.append((f'joined_{steps}.npz',arrays))
        print(json.dumps(dict(stage='evaluated_joined_common_Y_and_both_angular_insertions',steps_per_arm=steps,records=records[-4:]),sort_keys=True),flush=True)
    for p in('src/bhsm/interface/muon_joined_common_y_current.py','tests/test_muon_joined_common_y_current.py',Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);files={}
    for name,a in pending:
        p=out/name;deterministic_archive(p,a);files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    r=dict(classification='EVALUATED_JOINED_CANONICAL_COMMON_Y_CURRENT_WITH_BOTH_ANGULAR_SOURCE_DIRECTIONS',input_hashes=refs,array_archives=files,records=records,
        birth_frame='retained homogeneous common canonical frameT=I on C6 and its angular tensor; full worldvolume F_B/U not selected',
        domain='one incoming initial-zero inverse, child inherits actual birth response, outgoing free-final adjoint face retained',
        source='actual canonical delta-H at three charge-owned magnetic axes; both midpoint trace halves, fixed-Y Higgs and temporal -iG/N retained',
        angular_images='constant n1<-n0 and literal reverse; input-n1 to output n0+n2 and literal reverse; all six charged/neutral fibers before any state projection',
        odd_Y_powers_preserved=True,physical_Y_spectral_subtraction=False,physical_covariance_selected=False,
        fermion_current_inverse_component_not_full_Gaussian_quantum_loop=True,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 original joined-action coefficient residuals, literal transpose-adjoint identities and16/32/64 temporal refinements; no magnetic-Y/continuum/exterior/relative-heat or physical Pauli enclosure')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    print(json.dumps(materialize(a.output),sort_keys=True))
