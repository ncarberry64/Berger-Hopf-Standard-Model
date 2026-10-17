"""One focused retained-tail run; old temporal/cut/endpoint caches immutable."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cjson(z):return dict(real=float(np.real(z)),imag=float(np.imag(z)))


def run(root,out,history_root,retained_input,shift):
    if out.exists():raise FileExistsError('new dedicated output required')
    out.mkdir(parents=True);(out/'points').mkdir();began=time.perf_counter();sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_prefix_time_element import retained_arc_first_action,attached_geometry,moving_coefficients,spatial_weak_actions
    from bhsm.interface.muon_retained_tail_core import endpoint_element,stop_regular_moments,terminal_core_element,tail_response,attach_core_tail
    b=root/'artifacts';refs=dict(cut=b/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        step=b/'flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.npz',
        geometry=b/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        radial=b/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        norm=b/'muon_radial_inclusion_action_20261004/replay_reference/full_normalization.json',
        contact=b/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=b/'muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        future=b/'muon_prefix_time_element_20261004/future_run_2/retained_arc_time_element.npz',
        partial=b/'muon_prefix_time_element_20261004/assembly_run_1/partial_coupled_temporal_KM.npz',
        module=root/'src/bhsm/interface/muon_retained_tail_core.py',script=Path(__file__),
        inherited_machinery=root/'src/bhsm/interface/muon_prefix_time_element.py',
        stop_owner=root/'src/bhsm/interface/ae4_current_c2_canonical_stop_domain_bridge.py',
        stop_record=b/'action_extension/BHSM_AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE.json',
        reset_owner=root/'src/bhsm/interface/action_extension_global_spin_reset_ae2.py',
        material_owner=root/'src/bhsm/interface/ae31_c2_chiral_green_domain.py')
    if retained_input:
        h=read(retained_input/'retained_tail_points.npz');meta=json.loads((retained_input/'retained_tail_points.json').read_text())
    else:
        primary=history_root/'artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz'
        back=history_root/'artifacts/current_runtime/dop853_system_integration_current_finer/coupled_children/backreaction/arrays.npz'
        modes=history_root/'artifacts/current_runtime/current_physical_mode_response/report.json'
        hd=read(primary);bd=read(back);mj=json.loads(modes.read_text());idx=np.arange(2,48)
        if sha(primary).upper()!=mj['center_SHA256'] or not np.array_equal(hd['centers'],bd['states']):raise ValueError('different history')
        if not np.array_equal(hd['action_rates'],bd['action_rates']):raise ValueError('different action rates')
        h=dict(node_indices=idx,states=hd['centers'][idx],action_rates=hd['action_rates'][idx],state_weights=hd['state_weights'],
            signed_descriptors=hd['signed_descriptors'][idx],action_lengths=hd['action_lengths'][idx],branch_reference=hd['branch_reference'],
            proper_time_density=bd['proper_time_density'][idx],proper_times=bd['proper_times'][idx],
            radius_action_covectors=bd['radius_action_covectors'][idx],log_radius=bd['log_radius'][idx],
            inherited_Hermite_midpoint_state_position_defects=hd['Hermite_midpoint_state_position_defects'][2:],
            inherited_Hermite_midpoint_state_rate_defects=hd['Hermite_midpoint_state_rate_defects'][2:])
        meta=dict(point_records=mj['rows'][2:],source_records={name:dict(path=str(p),sha256=sha(p)) for name,p in
            dict(primary_history=primary,clock=back,mode_report=modes,
                clock_producer=history_root/'scripts/run_n12_current_child_parent_backreaction.py').items()},
            same_source='unchanged A0/spin0 source column with inherited hat,Tb and independent photon insertion',
            scope='retained numerical point centers and same-action tangents; continuous interval history not certified')
    np.savez_compressed(out/'retained_tail_points.npz',**h);save(out/'retained_tail_points.json',meta)
    refs.update(retained_points=out/'retained_tail_points.npz',point_provenance=out/'retained_tail_points.json')
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--short'),reference='524ed90689bd5923c249bba2e699abf627e703cd'))
    data={k:read(refs[k]) for k in ('cut','step','geometry','radial','contact','corrected','future','partial')}
    cut=data['cut'];S=cut['independent_source_map'];basis={};norm=json.loads(refs['norm'].read_text())
    d=S.shape[1];dim=2*d;source=np.r_[np.zeros(d),cut['source_coordinates']]
    for n in (1,3):
        xi=data['contact'][f'Xi_A_unit_n{n}'][:,:,data['corrected']['source_image_probe_columns']]
        flat=xi.transpose(1,3,4,0,2).reshape(64,n+1,n+1,32);basis[n]=np.einsum('omki,ij->omkj',flat,S)
    future=data['future'];jac=float(future['clock_tau_x'][1])
    value={k:future['Legendre_density_'+k].sum(axis=0) for k in ('A','B','C','M')}
    points=[dict(A=value['A']/jac,B=value['B'],C=value['C']*jac,M=value['M']/jac,
        Ms=future['right_trace_Cauchy_Gram'],clock_density=float(h['proper_time_density'][0]))]
    for i in range(1,len(h['node_indices'])-1):
        node=int(h['node_indices'][i]);f=retained_arc_first_action(h['states'][i],h['action_rates'][i],h['state_weights'],
            float(h['proper_time_density'][i]),float(h['signed_descriptors'][i]),meta['point_records'][i])
        g=attached_geometry(f['y'],data['step']['endpoint_predictor_center'],data['geometry'])
        s,a,r=moving_coefficients(f,g,data['contact'],cut,norm,data['geometry'])
        p=spatial_weak_actions(s,basis,data['radial'],cut,r);p['clock_density']=float(h['proper_time_density'][i])
        point_arrays=dict(**p,**a,actual_state=h['states'][i],Y_tau=f['Y_tau'],volume=s['volume'],Cauchy=s['cauchy'])
        np.savez_compressed(out/'points'/f'node_{node:02d}.npz',**point_arrays)
        directH=float(h['radius_action_covectors'][i]@h['action_rates'][i]/h['proper_time_density'][i])
        save(out/'points'/f'node_{node:02d}.json',dict(first_action=f['result'],attachment=r,
            direct_radius_H=directH,H_difference=r['H']-directH,node=node,arc=float(h['action_lengths'][i])))
        points.append({key:p[key] for key in ('A','B','C','M','Ms','clock_density')})
        save(out/'checkpoint.json',dict(stage='tail interior points',last_saved_node=node,reused_node2=True,
            new_field_campaigns=0,source_image_quotients=0,earlier_element_replays=0))
        if node%10==0:print(json.dumps(dict(stage='tail point saved',node=node,elapsed_seconds=time.perf_counter()-began)),flush=True)
    # Terminal arc derivative is finite even though the proper-time jet is
    # singular. Evaluate the instantaneous inclusion and its ARC variation.
    if h['signed_descriptors'][-1]!=0 or h['proper_time_density'][-1]!=0:raise ValueError('different stop chart')
    if meta['point_records'][-1]['selected_branch']!=24:raise ValueError('different stop branch')
    Yarc=h['action_rates'][-1]/h['state_weights']
    if np.linalg.norm(Yarc[:37])!=0:raise ValueError('retained stop q_arc limit differs')
    fs=dict(y=h['states'][-1],qnom=Yarc[:37],mnom=Yarc[74:98])
    gs=attached_geometry(fs['y'],data['step']['endpoint_predictor_center'],data['geometry'])
    ss,astop,rstop=moving_coefficients(fs,gs,data['contact'],cut,norm,data['geometry'])
    last_da=float(h['action_lengths'][-1]-h['action_lengths'][-2])
    stop=stop_regular_moments(ss,basis,data['radial'],cut,Yarc[74:98],last_da)
    terminal=terminal_core_element(points[-1],stop,last_da,source)
    np.savez_compressed(out/'terminal_core_element.npz',**terminal,**{'stop_'+k:v for k,v in stop.items()},
        actual_stop_state=fs['y'],Y_arc=Yarc,volume=ss['volume'],Cauchy=ss['cauchy'],u=ss['u'],p=ss['p'])
    save(out/'terminal_core_element.json',dict(coordinate='x=(arc-92)/(arc_stop-92)',
        stop_arc=float(h['action_lengths'][-1]),proper_clock='rho_arc=rho46*(1-x)',
        trial_phi='(1-x)^2; canonical minimal-core cutoff limit, not selected exhaustive terminal graph',
        terminal_regular_action='rho F0_W=-u*iGamma0*Lnu_arc/(2nu);rho F0_p=0;F1 finite',
        cutoff_form_error_order='O(epsilon^2) in declared moment model; coefficient unevaluated',
        normalisation= dict(I=rstop['I'],I_arc=rstop['I_tau']),projection=dict(B=rstop['bulk_B'],B_arc=rstop['bulk_B_tau'],
            Cauchy_B=rstop['Cauchy_B'],Cauchy_B_arc=rstop['Cauchy_B_tau']),physical_terminal_graph=None))
    elements=[]
    for i in range(len(points)-1):
        e=endpoint_element(points[i],points[i+1],float(h['action_lengths'][i+1]-h['action_lengths'][i]),source)
        elements.append(e)
    np.savez_compressed(out/'tail_interior_elements.npz',K=np.array([e['K'] for e in elements]),M=np.array([e['M'] for e in elements]),
        f=np.array([e['f'] for e in elements]),hierarchical_K=np.array([e['hierarchical_K'] for e in elements]),
        hierarchical_M=np.array([e['hierarchical_M'] for e in elements]),endpoint_to_hierarchical=np.array([e['endpoint_to_hierarchical'] for e in elements]),
        temporal_scales=np.array([e['scale'] for e in elements]),node2_A=points[0]['A'],node2_B=points[0]['B'],node2_C=points[0]['C'],node2_M=points[0]['M'],node2_Ms=points[0]['Ms'])
    tail=tail_response(elements,terminal,source,shift)
    dual=tail['stationary_conormal_dual'];Ms=points[0]['Ms']
    riesz=np.linalg.solve(Ms,dual)
    # Independent sampled conormal comparison; not used as the stationary
    # discrete return. The solve's conormal is its weak-model boundary row.
    da=float(h['action_lengths'][1]-h['action_lengths'][0]);p2=points[0]
    sampled=-(p2['B'].conj().T@source+p2['C']@(tail['solution'][1]-source)/(da*p2['clock_density']))
    scalar_keys=('maximum_interior_backward_residual','maximum_pivot_condition','interior_source_rhs_norm')
    np.savez_compressed(out/'tail_response.npz',**{k:v for k,v in tail.items() if k not in scalar_keys},
        stationary_conormal_Riesz=riesz,node2_Cauchy_pairing=Ms,sampled_trial_conormal_dual=sampled,
        original_source_trace=source)
    # Add the core response to the existing partial system. No old element
    # or joining equation is rebuilt, no missing owned block is assigned0.
    part=data['partial'];last_trace=np.zeros((dim,len(part['K'])),complex)
    I=np.eye(dim);scale=float(future['temporal_basis_scale'])
    last_trace[:,-2*dim:]=np.hstack((I,scale*I/2))
    attached=attach_core_tail(part,last_trace,tail,shift)
    np.savez_compressed(out/'partial_system_with_tail_core.npz',**attached)
    result=dict(classification='evaluated complete retained-tail minimal-core numerical model, not full owned exterior response',
        nodes=[2,47],action_arc_range=h['action_lengths'][[0,-1]].tolist(),
        proper_duration=float(h['proper_times'][-1]-h['proper_times'][0]),interior_elements=len(elements),terminal_core_elements=1,
        same_source_nonzero=True,shift=cjson(shift),native_length=None,
        stationary_core_solution_shape=list(tail['solution'].shape),
        interior_equation_absolute_residual=float(np.linalg.norm(tail['equation_residual'])),
        interior_equation_backward_residual=tail['maximum_interior_backward_residual'],
        input_trace_residual=float(np.linalg.norm(tail['solution'][0]-source)),
        conormal_identity_absolute_residual=float(np.linalg.norm(tail['stationary_conormal_identity_residual'])),
        stationary_core_conormal_dual_norm=float(np.linalg.norm(dual)),
        stationary_core_conormal_Riesz_norm=float(np.linalg.norm(riesz)),
        sampled_trial_conormal_difference=float(np.linalg.norm(dual-sampled)),
        required_output_contraction=cjson(tail['output_contraction']),
        homogeneous_boundary_output=cjson(tail['homogeneous_output_contraction']),
        affine_source_return_norm=float(np.linalg.norm(tail['r'])),
        interior_source_rhs_norm=tail['interior_source_rhs_norm'],maximum_pivot_condition=tail['maximum_pivot_condition'],
        source_load_class='geometric M projection of SAME continued retained p; never silently omitted',
        source_trace_class='response application to supplied source-reached node2 trace; not a solved physical exterior trace',
        assembled_partial_with_core_tail=True,full_owned_source_solved=False,
        next_missing=dict(operand='source-restricted owned seam/domain pullback for full W/p inclusion',
            equation='q_owned[iota_Wp X]=q5_can[X]+q_owned_seam[iota_Wp X];iota_Wp^-1 V_F=closure(Dmin_Wp) in q5_can+q_owned_seam+m',
            producer='AE4 canonical minimal form plus total material/reset wall-spinor inclusion and constraint complex',
            consumer='promote core-tail Schur component to full coupled exterior source solve',
            physical_terminal_load_to_select=False),
        unevaluated_terms=dict(owned_wall_reset_seam=None,constraint_complex_pullback=None,relative_completion=None,
            propagation_complement_bound=None),
        error_scope=dict(temporal='degree1 weak-density interior and regular terminal moment models; interpolation remainder unbounded',
            history='same-action numerical centers only; no new interval-continuum authority',
            radial='unchanged nodal8-point/cell prescription; continuum/roundoff bounds absent',
            terminal='minimal-core cutoff membership derived; exhaustive owned-domain identification not derived',
            residual='binary64 model equation diagnostic, not continuum error or Pauli accuracy'),
        execution=dict(new_interior_action_points=44,reused_node2=True,new_regular_stop_action=1,
            old_element_replays=0,new_history_integrations=0,new_field_campaigns=0,native_heat=0,physical_transfer_directions=0),
        physical_a_mu=None,physical_g_mu=None,elapsed_seconds=time.perf_counter()-began)
    save(out/'result.json',result)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_RETAINED_TAIL_CORE_20261005',stage='tail reduced and consumed',
        arrays=['tail_interior_elements.npz','terminal_core_element.npz','tail_response.npz','partial_system_with_tail_core.npz'],
        assembled='all remaining retained-tail core elements plus saved partial system',solved='inhomogeneous tail core with given source trace',
        full_owned_source_solved=False,next=result['next_missing'],physical_prediction=False))
    save(out/'output_hashes.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--history-root',type=Path);p.add_argument('--retained-input',type=Path);p.add_argument('--shift',type=complex,required=True)
    a=p.parse_args()
    if not a.history_root and not a.retained_input:p.error('retained-input or history-root required')
    run(a.repository.resolve(),a.output.resolve(),a.history_root,a.retained_input,a.shift)
