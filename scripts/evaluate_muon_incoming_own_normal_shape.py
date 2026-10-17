"""Incoming OWN-parent proper-normal drive, chronological weak action/returns.

The authoritative negative proof steps are reversed chronologically; no
joint parent Hessian or child born parameter is used as incoming dynamics.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_actual_normal_shape_source import proper_normal_shape_coefficient,mixed_normal_shape_weak_source
from bhsm.interface.muon_normal_shape_weak_consumption import integrate_shape_rate_contact,weak_shape_action_pairing
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_coupled_phase_trace_projection import _solve
from bhsm.interface.muon_complex_endpoint_area_action import original_endpoint_area_coefficient
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(source,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve incoming own-action applications')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    md=read(source,'result.json');phase,_=retained_input('incoming',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    tracefolder=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1');trace=read(tracefolder,'application.npz')
    bases=[read(source,f'incoming_{k:04d}_actual_base.npz')for k in range(2)]
    ends=[read(source,f'incoming_{k:04d}_actual_endpoint.npz')for k in range(2)]
    birthraw=P@bases[0]['initial_master']
    if not np.array_equal(birthraw,trace['raw_pair'][0]):raise ValueError('same common actual birth parent required')
    F=canonical_central_frame(birthraw,rep)['named_frame_covectors'];cases=('normal_basis','area_source')
    # Times increase from past endpoint -> stage1 -> endpoint0 -> stage0 ->birth.
    points=[dict(name='far',time=ends[1]['endpoint_time'].item(),master=ends[1]['endpoint_master'],raw=ends[1]['endpoint_raw'],
        G=ends[1]['endpoint_gradient'],H=ends[1]['endpoint_Hessian'],base_rows=ends[1]['endpoint_original146_rows'],endpoint_index=1)]
    for k in (1,0):
        b=bases[k];points.append(dict(name=f'cell_{k:04d}',time=b['time'].item(),master=b['stage_master'],raw=b['stage_raw'],
            G=b['stage_gradient'],H=b['stage_Hessian'],base_rows=b['original358_rows'],stage_index=k,positive_step=-b['step'].item()))
        if k==1:points.append(dict(name='corner',time=ends[0]['endpoint_time'].item(),master=ends[0]['endpoint_master'],raw=ends[0]['endpoint_raw'],
            G=ends[0]['endpoint_gradient'],H=ends[0]['endpoint_Hessian'],base_rows=ends[0]['endpoint_original146_rows'],endpoint_index=0))
    points.append(dict(name='birth',time=0j,master=bases[0]['initial_master'],raw=birthraw,G=trace['parent_standalone_gradient'],
        H=trace['parent_standalone_Hessian'],base_rows=np.r_[trace['parent_standalone_gradient'][106:212]-bases[0]['initial_Pi'],trace['parent_standalone_gradient'][212:]]))
    out.mkdir(parents=True)
    def save(name,obj):
        p=out/name;_compressed_npz(p,{k:v for k,v in obj.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split own-parent action')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    records=[]
    for p in points:
        H,G,eta=p['H'],p['G'],p['master'];D=H[106:,106:];rhs=np.r_[G[:106]-H[106:212,:106]@eta[106:212],-H[212:,:106]@eta[106:212]]
        K=np.block([[D,F.T],[F,np.zeros((2,2),complex)]]);z=_solve(K,np.r_[rhs,np.zeros(2)])[0];rate=np.r_[eta[106:212],z[:146]]
        a=proper_normal_shape_coefficient(p['raw'],P);area=original_endpoint_area_coefficient(p['raw'],P)
        def apply(gg,hh):
            s=mixed_normal_shape_weak_source(gg,hh,rate,a['value'],a['gradient'],a['hessian'],normal_position=37,
                normal_velocity=143,amplitude=1,amplitude_coordinate_first=0)
            return s,integrate_shape_rate_contact(s,gg,hh@rate,a['gradient'],a['hessian'],rate,normal_position=37,normal_velocity=143)
        s,c=apply(G,H);sa,ca=apply(area['gradient'],area['hessian']);p.update(source=s,consumed=c,area_source=sa,area_consumed=ca)
        dirs=[];high=[];low=[];audits=[]
        for case in cases:
            if 'stage_index'in p:
                q=read(source,f"incoming_{p['stage_index']:04d}_{case}_source_response.npz");hi,lo=q['stage_direction_high'],q['stage_direction_low'];audit=q['original_rows']
            elif 'endpoint_index'in p:
                q=read(source,f"incoming_{p['endpoint_index']:04d}_{case}_endpoint_source_response.npz");hi,lo=q['direction_high'],q['direction_low'];audit=q['original_rows']
            else:
                q=read(source,case+'_consumed_birth_parent_source.npz');hi,lo=q['direction_high'],q['direction_low'];audit=q['original_rows']
            dirs.append(hi+lo);high.append(hi);low.append(lo);audits.append(float(np.max(abs(audit))))
        p['directions']=np.column_stack(dirs)
        save(p['name']+'_own_shape_drive.npz',dict(**{k:v for k,v in c.items()if isinstance(v,np.ndarray)},
            original_own_Hessian=H,original_own_gradient=G,source_state=s['full_weak_state_source'],source_rate=s['full_weak_phase_rate_source'],
            normal_shape_direction=s['shape_direction'],actual_own_parent_rate=rate,original_rate_rows=D@z[:146]-rhs,
            named_rate_frame_reactions=z[146:],raw=p['raw'],master=eta,coordinate_time=np.array(p['time']),
            source_directions_high=np.column_stack(high),source_directions_low=np.column_stack(low),
            original_base_rows=p['base_rows'],source_original_rows_max=np.array(audits),
            common_area_gradient_per_gamma=area['gradient'],common_area_Hessian_per_gamma=area['hessian'],
            area_integrated_weak_bulk_source=ca['integrated_weak_bulk_source'],area_source_rate=sa['full_weak_phase_rate_source'],
            area_normal_EL_coefficient=ca['original_normal_canonical_equation']))
        rec=dict(point=p['name'],coordinate_time=clean(p['time']),own_base_rows_max=float(np.max(abs(p['base_rows']))),
            actual_source_original_rows_max=audits,own_rate_original146_max=float(np.max(abs(D@z[:146]-rhs))),
            own_normal_rate_equation=clean(c['original_normal_canonical_equation'].item()),
            full_shape_source_norm=float(np.linalg.norm(s['full_weak_state_source'])),rate_contact_norm=float(np.linalg.norm(s['full_weak_phase_rate_source'])),
            area_normal_EL_coefficient=clean(ca['original_normal_canonical_equation'].item()))
        records.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    mids=[p for p in points if'stage_index'in p];corner=points[2]
    def combine(area=False):
        sk,ck=('area_source','area_consumed')if area else('source','consumed')
        return weak_shape_action_pairing([p[ck]['integrated_weak_bulk_source']for p in mids],[p['directions']for p in mids],
            [p['positive_step']for p in mids],points[0][sk]['full_weak_phase_rate_source'],points[0]['directions'],
            points[-1][sk]['full_weak_phase_rate_source'],points[-1]['directions'],
            [corner[sk]['full_weak_phase_rate_source']],[corner['directions']],
            [corner[sk]['full_weak_phase_rate_source']],[corner['directions']])
    full=combine();ar=combine(True)
    save('complete_incoming_own_normal_drive.npz',dict(**full,**{'area_'+k:v for k,v in ar.items()},
        chronological_cell_order=np.array([1,0]),chronological_positive_steps=np.array([p['positive_step']for p in mids]),
        actual_common_birth_parent_raw=birthraw,actual_common_birth_parent_Pi=bases[0]['initial_Pi'],
        birth_original_shape_directions=np.column_stack([read(source,case+'_consumed_birth_parent_source.npz')['direction_high']for case in cases]),
        actual_far_outward_base_conormal=-ends[1]['endpoint_Pi'],actual_birth_outward_base_conormal=bases[0]['initial_Pi']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            pp=Path(path);pins[pp.relative_to(ROOT).as_posix()]=sha256(pp.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('own incoming/source action changed')
    result=dict(classification='EXECUTED_CHRONOLOGICAL_INCOMING_OWN_PARENT_PROPER_NORMAL_DRIVE',input_hashes=pins,archives=archives,records=records,
        action_parameters=md['action_parameters'],chronological_order=[1,0],cases=list(cases),
        complete_parent_drive=clean(full['complete_shape_action_pairing']),area_parent_drive_per_gamma=clean(ar['complete_shape_action_pairing']),
        initial_far_rate_contact=clean(full['initial_rate_contact']),final_birth_rate_contact=clean(full['final_rate_contact']),
        parent_own_Hessian_not_joint_parent_block=True,own_parent_explicit_clock_zero_by_autonomous_action=True,
        incoming_reset_birth_outward_conormal_sign='+Pi_parent',incoming_far_sign='-Pi_parent',
        same_germ_true_face_corner_contacts_supplied=True,
        historical_gammaNone_momentum_not_independent_environment=True,
        original_two_source_variations_are_conditional_normal_area_controls=True,
        physical_incoming_environment_mode_or_formation_admitted=False,
        error_scope='Actual original own-parent positive-chronological action/source history from reversed negative proof steps. Binary canonical rate/weak midpoint and true face contacts, no action/continuum/physical exterior error enclosure.')
    pp=out/'result.json';pp.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='incoming_own_shape_drive_complete',result_sha256=sha256(pp.read_bytes()).hexdigest(),drive=result['complete_parent_drive'],area=result['area_parent_drive_per_gamma']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=Path('artifacts/muon_changing_canonical_source_20261012/run_3'));p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.source,a.output)
