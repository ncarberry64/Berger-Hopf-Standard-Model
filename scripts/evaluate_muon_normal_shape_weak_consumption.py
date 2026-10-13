"""Consume actual proper-normal source on all67 weak directions and all faces."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_actual_normal_shape_source import proper_normal_shape_coefficient,mixed_normal_shape_weak_source
from bhsm.interface.muon_normal_shape_weak_consumption import integrate_shape_rate_contact,weak_shape_action_pairing
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_child_action import _affine_geometry
from bhsm.interface.muon_holomorphic_joint_reference_clock import joint_reference_explicit_clock
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_coupled_phase_trace_projection import _solve
from bhsm.interface.muon_stored_fiber_canonical_tangent import stored_endpoint_constitutive_tangent
from bhsm.interface.muon_holomorphic_geometry_direction import geometry_first_application
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(history,geometry_return,shape_source,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every full shape weak application')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    hm=read(history,'result.json');rm=read(geometry_return,'result.json');sm=read(shape_source,'result.json')
    origin=next(p for p in hm['input_hashes']if p.endswith('candidate.npz'));base=read(Path(origin).parent,Path(origin).name)
    returned=read(geometry_return,'actual_base_boundary_and_source_scope.npz')
    finalsource=read(shape_source,'actual_shape_source_and_embedding.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    F=canonical_central_frame(base['raw_pair'][1],rep)['named_frame_covectors']
    parent_rate_raw=np.zeros(268,complex);parent_rate_raw[:37]=base['raw_pair'][0,37:74];parent_rate_raw[98]=base['raw_pair'][0,99]
    parent_profile_rate=P.T@parent_rate_raw
    points=[];cells=[]
    points.append(dict(name='initial',t=0j,raw=base['raw_pair'][1],canonical_high=returned['initial_fiber_high'],canonical_low=returned['initial_fiber_low']))
    for k in range(hm['steps']):
        stage=read(history,f'step_{k:04d}_stage.npz');directions=read(geometry_return,f'cell_{k:04d}_all67_original_canonical_rows.npz')
        end=read(history,f'step_{k:04d}_endpoint.npz')
        points.append(dict(name=f'cell_{k:04d}',t=stage['coordinate_time'].item(),raw=stage['stage_raw'],
            phase_high=directions['stage_direction_high'],phase_low=directions['stage_direction_low'],step=stage['coordinate_step'].item()))
        points.append(dict(name='final'if k==hm['steps']-1 else f'corner_{k:04d}',t=end['coordinate_time'].item(),raw=end['endpoint_raw'],
            canonical_high=directions['canonical_final_high'],canonical_low=directions['canonical_final_low']))
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split weak shape arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    records=[]
    for point in points:
        t,raw=point['t'],point['raw'];parent=_affine_geometry(base['raw_pair'][0],t)
        ref=np.array([_affine_geometry(v,t)for v in base['reference_pair']]);pair=np.array([parent,raw])
        a=holomorphic_two_arm_action(pair,ref,rep,**hm['action_parameters']);H=a['hessian'];G=a['gradient'];eta=P.T@raw
        clock=joint_reference_explicit_clock(pair,ref,rep,a,nu_squared_action=hm['action_parameters']['nu_squared_action'])
        # The parent-born PARAMETER is held. Its evaluated affine profile
        # clock is explicit inherited forcing, not future parent dynamics.
        inherited_clock=clock['gradient_clock_first'][252:]+H[252:,:252]@parent_profile_rate
        Hc=H[252:,252:];Gc=G[252:];D=Hc[106:,106:]
        rhs=np.r_[Gc[:106]-Hc[106:212,:106]@eta[106:212]-inherited_clock[106:212],
            -Hc[212:,:106]@eta[106:212]-inherited_clock[212:]]
        K=np.block([[D,F.T],[F,np.zeros((2,2),complex)]]);r=np.r_[rhs,np.zeros(2,complex)];z=_solve(K,r)[0]
        child_rate=np.r_[eta[106:212],z[:146]];born_rate=np.zeros(252,complex);rate=np.r_[born_rate,child_rate]
        # Only the child needs Dt Pi_s in the integration-by-parts identity.
        Gt=H@rate+clock['gradient_clock_first']+H[:,:252]@parent_profile_rate
        af=proper_normal_shape_coefficient(raw,P);da=np.r_[np.zeros(252,complex),af['gradient']]
        dd=np.zeros((504,504),complex);dd[252:,252:]=af['hessian']
        def apply(gg,hh,ggt):
            s=mixed_normal_shape_weak_source(gg,hh,rate,af['value'],da,dd,normal_position=289,
                normal_velocity=395,amplitude=1,amplitude_coordinate_first=0)
            # master child v37 is252+106+37=395, not396.
            c=integrate_shape_rate_contact(s,gg,ggt,da,dd,rate,normal_position=289,normal_velocity=395)
            return s,c
        s,c=apply(G,H,Gt);ga=a['area_gradient_per_gamma'];ha=a['area_Hessian_per_gamma']
        sa,ca=apply(ga,ha,ha@rate)
        if 'phase_high'in point:
            dh,dl=point['phase_high'],point['phase_low'];admission=np.array([])
        else:
            ep=stored_endpoint_constitutive_tangent(Hc,F,point['canonical_high'],point['canonical_low'])
            dh,dl=ep['direction_high'],ep['direction_low'];admission=ep['original_rows']
        delta=np.vstack((np.zeros_like(dh),dh+dl))
        # Endpoint born source is a parameter cotangent, not a parent bulk.
        J=np.eye(252,dtype=complex);J[np.arange(37),106+np.arange(37)]+=t;J[37,143]+=t
        born_source=J.T@c['integrated_weak_bulk_source'][:252]
        body=geometry_first_application(raw,(P@s['shape_direction'][252:])[:,None])
        point.update(source=s,consumed=c,area_source=sa,area_consumed=ca,delta=delta,born_source=born_source)
        rec=dict(point=point['name'],time=clean(t),child_rate_original146_max=float(np.max(abs(D@z[:146]-rhs))),
            child_rate_framed148_max=float(np.max(abs(K@z-r))),named_rate_reactions=clean(z[146:]),
            actual_normal_canonical_rate_residual=clean(c['original_normal_canonical_equation'].item()),
            original_phase_variation146_max=float(np.max(abs(admission)))if admission.size else None,
            state_source_norm=float(np.linalg.norm(s['full_weak_state_source'])),rate_contact_norm=float(np.linalg.norm(s['full_weak_phase_rate_source'])),
            integrated_bulk_norm=float(np.linalg.norm(c['integrated_weak_bulk_source'])),
            equation_contact_norm=float(np.linalg.norm(c['canonical_equation_shape_contact'])),
            weak_source_formula_defect_max=float(np.max(abs(c['integrated_minus_ordinary_and_equation']))),
            area_normal_EL_coefficient=clean(ca['original_normal_canonical_equation'].item()),
            born_parameter_cotangent_norm=float(np.linalg.norm(born_source)))
        records.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
        save(point['name']+'_shape_weak_application.npz',dict(**{k:v for k,v in c.items()if isinstance(v,np.ndarray)},
            full_state_source=s['full_weak_state_source'],full_rate_source=s['full_weak_phase_rate_source'],
            ordinary_H_shape_source=s['ordinary_action_shape_source'],moving_embedding_source=s['moving_embedding_action_source'],
            all67_phase_direction_high=dh,all67_phase_direction_low=dl,
            all67_original_phase_rows=admission,full_joint_Ly=G[a['algebraic_indices']],
            born_source_parameter_cotangent=born_source,born_parameter_rate=born_rate,
            inherited_profile_clock=H[252:,:252]@parent_profile_rate,reference_only_clock=clock['gradient_clock_first'][252:],
            original_child_rate_rows=D@z[:146]-rhs,named_rate_reactions=z[146:],
            actual_child_master_rate=child_rate,raw_pair=pair,reference_pair=ref,
            geometry_first_values=np.array([body['first'][key][0]for key in body['first']]),
            area_full_state_source=sa['full_weak_state_source'],area_full_rate_source=sa['full_weak_phase_rate_source'],
            area_integrated_weak_bulk_source=ca['integrated_weak_bulk_source'],
            area_rate_source_time_first=ca['weak_phase_rate_source_time_first'],
            area_canonical_equation_shape_contact=ca['canonical_equation_shape_contact'],
            coordinate_time=np.array(t)))
    mids=[p for p in points if p['name'].startswith('cell_')];corners=[p for p in points if p['name'].startswith('corner_')]
    def combine(kind):
        C='consumed'if kind=='base'else'area_consumed';S='source'if kind=='base'else'area_source'
        return weak_shape_action_pairing([p[C]['integrated_weak_bulk_source']for p in mids],[p['delta']for p in mids],
            [p['step']for p in mids],points[0][S]['full_weak_phase_rate_source'],points[0]['delta'],
            points[-1][S]['full_weak_phase_rate_source'],points[-1]['delta'],
            [p[S]['full_weak_phase_rate_source']for p in corners],[p['delta']for p in corners],
            [p[S]['full_weak_phase_rate_source']for p in corners],[p['delta']for p in corners])
    combined=combine('base');area=combine('area')
    born=sum(p['step']*p['born_source']for p in mids)
    save('complete_all67_normal_shape_weak_response.npz',dict(**combined,
        **{'area_'+k:v for k,v in area.items()},born_parameter_integrated_source_cotangent=born,
        actual_birth226_rows=read(geometry_return,'actual_endpoint_geometry_and_all67_natural_return.npz')['actual_birth226_rows'],
        original_all67_mechanical_boundary_work_max=np.array(rm['all67_complete_boundary_work_max'])))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            p=Path(path);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_normal_shape_weak_consumption.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual weak domain or source changed')
    result=dict(classification='EXECUTED_ACTUAL_MOVING_NORMAL_WEAK_SOURCE_AND_ALL67_NATURAL_TEMPORAL_RETURNS',
        input_hashes=pins,archives=archives,records=records,action_parameters=hm['action_parameters'],
        complete_all67_shape_pairing_max=float(np.max(abs(combined['complete_shape_action_pairing']))),
        complete_all67_shape_pairing_norm=float(np.linalg.norm(combined['complete_shape_action_pairing'])),
        bulk_shape_pairing_max=float(np.max(abs(combined['bulk_shape_action_pairing']))),
        initial_rate_contact_max=float(np.max(abs(combined['initial_rate_contact']))),
        final_rate_contact_max=float(np.max(abs(combined['final_rate_contact']))),
        corner_rate_contact_max=float(np.max(abs(combined['coefficient_corner_rate_contact']))),
        area_complete_shape_pairing_max=float(np.max(abs(area['complete_shape_action_pairing']))),
        born_source_integrated_cotangent_norm=float(np.linalg.norm(born)),
        original_birth226_max=rm['original_birth226_max'],original_all67_clock_scaled_mechanical_work=rm['all67_clock_scaled_complete_boundary_work_max'],
        all_original_phase_Gauss_and_rate_equations_preserved=True,
        parent_born_parameter_held_not_future_parent_bulk=True,
        actual_affine_parent_profile_clock_classified_explicit_inherited_child_source=True,
        original_incoming_parent_own_rate_drive_and_opposite_orientation_not_replaced=True,
        both_weak_covectors_consumed_by_IBP_with_all_faces=True,
        coefficient_corner='same declared continuous true-action face germ on BOTH sides; explicit equal-rate-contact subtraction supplied, not extrapolated midpoint rate or moving physical-reset germ',
        area_EL_not_assumed_zero_along_gammaNone_base=True,
        actual_child_rate_rows_are_not_an_admission_certificate=True,
        physical_outgoing_environment_formation_or_selected_mode_admitted=False,
        next_coupled_equation='Use the born-source endpoint cotangent and full signed weak natural return in the original reset/natural/energy equations, with own incoming canonical/source environment and actual outgoing constrained geometry support; retain all67 shooting directions and common gamma(c) formation/pole equations. The recorded nonzero original rows cannot be replaced by a three-port fit.',
        error_scope='Actual complex signed midpoint action and true face coefficient applications; analytic reference clock and implicit-normal geometry jets, binary canonical rate solves and exact-stored supplied phase variations. Fixed temporal midpoint quadrature/source support and action/exterior errors are not enclosed.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='all67_actual_shape_weak_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        full_pairing_max=result['complete_all67_shape_pairing_max'],initial_contact_max=result['initial_rate_contact_max'],final_contact_max=result['final_rate_contact_max'],
        area_pairing_max=result['area_complete_shape_pairing_max']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history',type=Path,default=Path('artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_1'))
    p.add_argument('--geometry-return',type=Path,default=Path('artifacts/muon_reached_geometry_canonical_return_20261012/run_1'))
    p.add_argument('--shape-source',type=Path,default=Path('artifacts/muon_actual_normal_shape_source_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.history,a.geometry_return,a.shape_source,a.output)
