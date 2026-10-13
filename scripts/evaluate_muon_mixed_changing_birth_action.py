"""Direct mixed-coordinate application of the retained changing action.

The outer-work check is consumed by the full coupled matching application.
Conditional coordinate endpoint controls do not select a physical state.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_mixed_changing_birth_action import (
    mixed_chronological_arm_action,mixed_variation_from_actual_stages,mixed_cell_cotangent,
)
from bhsm.interface.muon_changing_weak_birth_action import inherited_source_weak_blocks,constrained_weak_source_response
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(x):
    if isinstance(x,dict):return{k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[clean(v)for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.generic):return x.item()
    return x


def run(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('retain earlier action applications')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    wf=Path('artifacts/muon_changing_weak_birth_action_20261012/run_1')
    sf=Path('artifacts/muon_changing_canonical_source_20261012/run_3')
    wm=read(wf,'result.json');sm=read(sf,'result.json')
    original=read(wf,'full_changing_weak_operator.npz')
    sectors=read(wf,'signed_sectors_and_area.npz')
    domain=read(wf,'endpoint_domain_and_outer_targets.npz')
    arms={};stages={}
    for side,order in(('incoming',[1,0]),('outgoing',[0,1])):
        stages[side]=[read(sf,f'{side}_{k:04d}_actual_base.npz')for k in order]
        H=([s['stage_Hessian']for s in stages[side]]if side=='incoming'
           else original['stage_full_joint_Hessians'][:,252:,252:])
        arms[side]=mixed_chronological_arm_action(H,[s['stage_gradient']for s in stages[side]],original[side+'_steps'])
    inherited=inherited_source_weak_blocks(arms['outgoing']['cell_lifts'],arms['outgoing']['steps'],
        original['stage_full_joint_Hessians'],original['stage_parent_source_Hessians'],
        original['stage_full_joint_gradients'],original['stage_parent_source_gradients'],original['outgoing_reference_times'])
    P=np.zeros((1048,1048),complex)
    P[:398,:398]=arms['incoming']['mixed_to_nodes'];P[398:796,398:796]=arms['outgoing']['mixed_to_nodes'];P[796:,796:]=np.eye(252)
    W=np.zeros_like(P);W[:398,:398]=arms['incoming']['matrix'];W[398:796,398:796]=arms['outgoing']['matrix']
    W[398:796,796:]=inherited['child_to_source'];W[796:,398:796]=inherited['source_to_child'];W[796:,796:]=inherited['source_self']
    G=np.r_[arms['incoming']['gradient'],arms['outgoing']['gradient'],inherited['source_gradient']]
    # Only covectors/maps are transported from the formed nodal packet.
    # The quadratic action W is built directly from original cell jets.
    Cbulk_node=np.vstack((domain['outer_coordinate_map'][:,:796],-domain['parent_birth_source_position_match'][:,:796],
        domain['birth_value_trace73'][:,:796],domain['named_cell_temporal_frames'][:,:796]))
    Csource=np.vstack((domain['outer_coordinate_map'][:,796:],-domain['parent_birth_source_position_match'][:,796:],
        domain['birth_value_trace73'][:,796:],domain['named_cell_temporal_frames'][:,796:]))
    Cbulk=Cbulk_node@P[:796,:796];ports=domain['both_birth_attachment_and_proper_normal_maps']@P
    out.mkdir(parents=True)
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>=10*1024**2:raise ValueError('split complete application arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('direct_mixed_action.npz',dict(matrix=W,gradient=G,mixed_to_nodes=P,
        incoming_cell_lifts=arms['incoming']['cell_lifts'],outgoing_cell_lifts=arms['outgoing']['cell_lifts'],
        endpoint_constraint_map=Cbulk,source_constraint_map=Csource,both_birth_port_maps=ports,
        transported_constitutive_endpoint_map=read(Path('artifacts/muon_weak_birth_source_domain_20261012/run_1'),
            'own_parent_source_endpoint_domain.npz')['original_constitutive_domain_map']@P,
        direct_minus_transported_formed_action=W-P.T@original['matrix']@P))
    reports={}
    for case in('normal_basis','area_source'):
        old=read(wf,case+'_source_conditioned_weak_attempt.npz');alpha=old['parent_birth_source_high_low']
        # Explicit area covector is affine in gamma, already independent
        # of the varied background. Transporting that covector is safe.
        f0=P.T@old['full_source_gradient_high_low']
        rhs=old['original_rhs'][796:]
        f=f0[:796]+W[:796,796:]@alpha
        print(json.dumps(dict(stage='direct_mixed_conditional_solve',case=case)),flush=True)
        a=constrained_weak_source_response(W[:796,:796],f,Cbulk,rhs,ports[5,:796])
        complete=np.vstack((a['solution'],alpha));node=P@complete
        cot=[];control=[];stationary_forces=[]
        for side,offset,order in(('incoming',0,[1,0]),('outgoing',398,[0,1])):
            ss=stages[side]
            H=np.array([s['stage_Hessian']for s in ss])if side=='incoming'else original['stage_full_joint_Hessians'][:,252:,252:]
            variations=np.einsum('kij,jb->kib',arms[side]['cell_lifts'],complete[offset:offset+398])
            gcase=np.zeros((2,252,2),complex)
            # Recover original literal cell sources, with inherited profile
            # feedback and area contact in exactly the saved source direction.
            dirs=[read(sf,f'{side}_{k:04d}_{case}_source_response.npz')for k in order]
            for j,d in enumerate(dirs):
                gcase[j,:,0]=d['source_gradient_high'];gcase[j,:,1]=d['source_gradient_low']
            original_work=mixed_cell_cotangent(H,gcase,arms[side]['steps'],variations)
            force=original_work['original_cell_forces']
            stationary_forces.append(force)
            cot.append(original_work['cotangent'])
            born=read(sf,case+'_consumed_birth_'+('parent'if side=='incoming'else'child')+'_source.npz')
            ends=[read(sf,f'{side}_{k:04d}_{case}_endpoint_source_response.npz')for k in order]
            x0=(ends[0]['direction_high'][:106]if side=='incoming'else born['direction_high'][:106])
            x1=(ends[0]['direction_low'][:106]if side=='incoming'else born['direction_low'][:106])
            actual=np.stack([np.column_stack((d['stage_direction_high'],d['stage_direction_low']))for d in dirs])
            control.append(mixed_variation_from_actual_stages(np.column_stack((x0,x1)),actual))
        flux=np.vstack((*cot,(W@complete+f0)[796:]))
        original_work_difference=P.T@flux-(W@complete+f0)
        outer=domain['outer_cotangent_selector']@flux-old['outer_canonical_target_high_low']
        known=np.vstack((*control,alpha));known_nodes=P@known
        # No formed-matrix multiplication enters this original work check.
        save(case+'_mixed_application.npz',dict(solution=complete,nodal_solution=node,original_control_mixed=known,
            original_control_nodes=known_nodes,original_saddle_rows=a['original_saddle_rows'],
            original_constraint_rows=a['original_constraint_rows'],reactions=a['reactions'],
            original_cell_forces=np.array(stationary_forces),literal_nodal_cotangent=flux,
            original_work_representation_difference=original_work_difference,
            outer_cotangent_defect=outer,mixed_source_gradient=f0,literal_pairing_difference=a['literal_pairing_difference']))
        reports[case]=dict(saddle_max=float(np.max(abs(a['original_saddle_rows']))),constraint_max=float(np.max(abs(a['original_constraint_rows']))),
            quadratic_stationarity_difference_max=float(np.max(abs(a['quadratic_action_stationarity_difference']))),
            outer_cotangent_defect_norms=[float(np.linalg.norm(v))for v in outer.T],
            outer_cotangent_defect_max=float(np.max(abs(outer))),
            original_work_representation_difference_max=float(np.max(abs(original_work_difference))),
            old_vs_direct_control_nodes_max=float(np.max(abs(known_nodes-old['original_source_control_high_low']))),
            physical_outer_matching=False,source_endpoint146_bound_in_conditional_solve=False,
            formed_nodal_action_reused=False,all_cell_action_coefficients_held_at_same_actual_stage=True)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_mixed_changing_birth_action.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='EVALUATED_DIRECT_CHANGING_ACTION_COORDINATES_AND_COMPLETE_OUTER_WORK',
        archives=archives,input_hashes=pins,applications=reports,
        direct_minus_formed_action_max=float(np.max(abs(W-P.T@original['matrix']@P))),
        action_parameters=sm['action_parameters'],physical_state_or_mode_selected=False,
        scope='Same reached four finite cells. This application corrects the weak representation and retains conditional endpoint defects; it is an input to the coupled birth/formation/exterior solve, not physical normalization or an anomaly estimate.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='direct_mixed_complete',sha256=sha256(p.read_bytes()).hexdigest(),applications=reports)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
