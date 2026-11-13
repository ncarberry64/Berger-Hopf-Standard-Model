"""Consume two actual cached future field/clock records in a temporal element."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(root,out,history_root,retained_input):
    if out.exists():raise FileExistsError('fresh output required')
    out.mkdir(parents=True);began=time.perf_counter();sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_prefix_time_element import (retained_arc_first_action,attached_geometry,
        moving_coefficients,spatial_weak_actions,integrate_linear_density_element,consume_prefix_element)
    b=root/'artifacts';refs=dict(cut=b/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        step=b/'flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.npz',
        geometry=b/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        radial=b/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        norm=b/'muon_radial_inclusion_action_20261004/replay_reference/full_normalization.json',
        contact=b/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=b/'muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        module=root/'src/bhsm/interface/muon_prefix_time_element.py',script=Path(__file__))
    if retained_input:
        h=read(retained_input/'retained_future_points.npz')
        meta=json.loads((retained_input/'retained_future_points.json').read_text())
    else:
        primary=history_root/'artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz'
        back=history_root/'artifacts/current_runtime/dop853_system_integration_current_finer/coupled_children/backreaction/arrays.npz'
        modes=history_root/'artifacts/current_runtime/current_physical_mode_response/report.json'
        hd=read(primary);bd=read(back);mj=json.loads(modes.read_text())
        if not (np.array_equal(hd['centers'],bd['states']) and np.array_equal(hd['action_rates'],bd['action_rates'])
                and np.array_equal(hd['state_weights'],bd['state_weights'])):
            raise ValueError('future history/clock identities disagree')
        if sha(primary).upper()!=mj['center_SHA256']:raise ValueError('mode report belongs to another history')
        idx=np.array([1,2]);h=dict(node_indices=idx,states=hd['centers'][idx],
            action_rates=hd['action_rates'][idx],state_weights=hd['state_weights'],
            branch_reference=hd['branch_reference'],signed_descriptors=hd['signed_descriptors'][idx],
            action_lengths=hd['action_lengths'][idx],proper_time_density=bd['proper_time_density'][idx],
            proper_times=bd['proper_times'][idx],anchor_state=hd['centers'][0],
            descriptor_rates=hd['descriptor_rates'][idx],
            inherited_Hermite_midpoint_state_position_defect=hd['Hermite_midpoint_state_position_defects'][1],
            inherited_Hermite_midpoint_state_rate_defect=hd['Hermite_midpoint_state_rate_defects'][1])
        producer=history_root/'scripts/run_n12_current_child_parent_backreaction.py'
        meta=dict(point_records=[mj['rows'][int(i)] for i in idx],
            source_records={name:dict(path=str(p),sha256=sha(p)) for name,p in
                dict(primary_history=primary,clock=back,mode_report=modes,clock_producer=producer,
                     history_report=primary.with_suffix('.json'),clock_report=back.with_name('report.json')).items()},
            clock_equation='d_tau/d_arc=N_b*sigma/||G||=N_b*(W_q*v).F_arc,q/||W_q*v||^2',
            source_selection='same retained future history, branch24 continuation and original photon source',
            physical_interval_history_certificate=None)
        (out/'producer_clock.py').write_bytes(producer.read_bytes())
    np.savez_compressed(out/'retained_future_points.npz',**h);save(out/'retained_future_points.json',meta)
    refs.update(retained_points=out/'retained_future_points.npz',point_provenance=out/'retained_future_points.json')
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--short')))
    data={k:read(refs[k]) for k in ('cut','step','geometry','radial','contact','corrected')}
    cut=data['cut'];S=cut['independent_source_map'];basis={}
    anchor_delta=(h['anchor_state']-data['step']['endpoint_predictor_center'])*h['state_weights']
    anchor_gap=float(np.linalg.norm(anchor_delta))
    # DOP853 initializes in action coordinates then divides by W on output.
    # Preserve its few-ulp roundtrip, do not demand byte equality or modify
    # either historical state. This is an identity tolerance, not a tube bound.
    roundtrip_tolerance=8*np.finfo(float).eps*(np.linalg.norm(h['anchor_state']*h['state_weights'])+
        np.linalg.norm(data['step']['endpoint_predictor_center']*h['state_weights']))
    if anchor_gap>roundtrip_tolerance:raise ValueError('future/cut anchor mismatch exceeds action roundtrip scope')
    for n in (1,3):
        xi=data['contact'][f'Xi_A_unit_n{n}'][:,:,data['corrected']['source_image_probe_columns']]
        flat=xi.transpose(1,3,4,0,2).reshape(64,n+1,n+1,32)
        basis[n]=np.einsum('omki,ij->omkj',flat,S)
    da=float(np.diff(h['action_lengths'])[0]);points=[];coefficients=[];receipts=[];measure=[]
    for i in range(2):
        f=retained_arc_first_action(h['states'][i],h['action_rates'][i],h['state_weights'],
            float(h['proper_time_density'][i]),float(h['signed_descriptors'][i]),meta['point_records'][i])
        g=attached_geometry(f['y'],data['step']['endpoint_predictor_center'],data['geometry'])
        s,a,r=moving_coefficients(f,g,data['contact'],cut,json.loads(refs['norm'].read_text()),data['geometry'])
        p=spatial_weak_actions(s,basis,data['radial'],cut,r);p['tau_x']=da*h['proper_time_density'][i]
        points.append(p);coefficients.append(a);receipts.append(dict(first_action=f['result'],attachment=r))
        measure.append(dict(volume=s['volume'],Cauchy=s['cauchy']))
        save(out/f'point_{i+1}.json',receipts[-1])
    scale=float(da*np.mean(h['proper_time_density']))
    K,M,polys=integrate_linear_density_element(points,scale)
    arrays,assembly=consume_prefix_element(K,M,cut,scale)
    assembly.update(kind='future local Dirac weak-density interpolant on retained nodes1..2',
        left_face='retained future node1/action_arc2; artificial element face',
        right_face='retained future node2/action_arc4; artificial element face')
    d=S.shape[1];dim=2*d;source=cut['source_coordinates'];full=arrays['source_constant_coefficients'][:dim]
    arrays.update(left_trace_Cauchy_Gram=points[0]['Ms'],right_trace_Cauchy_Gram=points[1]['Ms'],
        left_model_outward_conormal_dual=-points[0]['B'].conj().T@full,
        right_model_outward_conormal_dual=points[1]['B'].conj().T@full,
        actual_states=h['states'],action_Y_tau=np.array([h['action_rates'][i]/h['state_weights']/h['proper_time_density'][i] for i in range(2)]),
        clock_tau_x=np.array([p['tau_x'] for p in points]),temporal_basis_scale=np.array(scale),
        point_volume_density=np.array([m['volume'] for m in measure]),
        point_Cauchy_density=np.array([m['Cauchy'] for m in measure]),radial_weights=cut['radial_weights'])
    for key in ('a0','Lnu_direct','C_tau_nodes','r_tau_nodes','u','p'):
        arrays[key]=np.array([a[key] for a in coefficients])
    for key,v in polys.items():arrays['Legendre_density_'+key]=v
    for n in (1,3):arrays[f'actual_source_Dp_n{n}']=np.array([p[f'Dp_n{n}'] for p in points])
    np.savez_compressed(out/'retained_arc_time_element.npz',**arrays)
    # Source contraction of the degree-one A-density equals its trapezoid
    # moment exactly; no physical field has been frozen across the cell.
    direct=sum(.5*p['tau_x']*np.vdot(source,p['A'][d:2*d,d:2*d]@source).real for p in points)
    result=dict(classification='evaluated same-source future temporal density model; partial coupled exterior assembly',
        node_indices=h['node_indices'].tolist(),action_arcs=h['action_lengths'].tolist(),
        retained_proper_time_interval=h['proper_times'].tolist(),proper_duration=scale,
        anchor_action_roundtrip_gap=anchor_gap,anchor_identity_tolerance=roundtrip_tolerance,
        anchor_scope='action-coordinate multiply/divide roundtrip; historical states preserved',
        proper_clock_interval_identity_error=abs(np.diff(h['proper_times'])[0]-scale),
        temporal_integral=dict(density_degree=1,weak_integrand_degree=3,
            method='exact Legendre moments of endpoint-sampled weak densities',
            field_points='two actual retained states/tangents; no invented interior field',
            temporal_interpolation_bound=None,history_continuum_bound=None),
        source_history_energy=float(direct),source_form_energy=assembly['source_element_energy'],
        direct_form_difference=float(abs(direct-assembly['source_element_energy'])),
        source_first_lapse_rates=arrays['action_Y_tau'][:,74].tolist(),
        a0_change_norm=float(np.linalg.norm(arrays['a0'][1]-arrays['a0'][0])),
        assembly=assembly,error_scope=dict(first_actions='cached numerical centers; no interval tube claim',
            instantaneous_I='full-cap affine nodal integral enclosure, same pairing',
            I_tau='action tangent at each actual state, affine spatial prescription',
            spatial_quadrature='unchanged saved8-point-per-cell grid; continuum/roundoff bound absent',
            temporal='exact integral of explicitly declared degree-one weak densities; interpolation error unbounded',
            inherited_midpoint_state_defect_norm=float(np.linalg.norm(h['inherited_Hermite_midpoint_state_position_defect'])),
            inherited_midpoint_rate_defect_norm=float(np.linalg.norm(h['inherited_Hermite_midpoint_state_rate_defect'])),
            midpoint_defects_are_coefficient_bounds=False),
        execution=dict(new_actual_spatial_action_points=2,new_history_integrations=0,new_field_campaigns=0,
            old_replays=0,exterior_source_solutions=0,heat_evaluations=0),
        physical_a_mu=None,physical_g_mu=None,elapsed_seconds=time.perf_counter()-began)
    save(out/'result.json',result);save(out/'assembly.json',assembly)
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('proper_duration','source_history_energy','source_first_lapse_rates','a0_change_norm','execution','elapsed_seconds')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True);p.add_argument('--history-root',type=Path)
    p.add_argument('--retained-input',type=Path)
    a=p.parse_args()
    if not a.history_root and not a.retained_input:p.error('history-root or immutable retained-input required')
    run(a.repository.resolve(),a.output.resolve(),a.history_root,a.retained_input)
