"""Actual canonical forces and density trace on the saved coupled reset candidate."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_shifted_boundary_source import canonical_reset_chart
from bhsm.interface.action_extension_global_spin_reset_ae2 import action_definition
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,output):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve all coupled canonical/trace candidates')
    refs={}
    def read(path,expected=None):
        p=ROOT/path;b=p.read_bytes();h=sha256(b).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same candidate/action source changed: '+str(path))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(source_folder/'result.json');refs.update(md['input_hashes'])
    state=read(source_folder/'application.npz',md['archives']['application.npz']['sha256'])
    raw,reference=state['raw_pair'],state['reference_pair']
    phase,_=retained_input('outgoing',refs);rep=phase['representation']
    a=holomorphic_two_arm_action(raw,reference,rep,**md['action_parameters'])
    R=a['master_lift'];eta=R.T@raw.reshape(-1);vi,yi=a['velocity_indices'],a['algebraic_indices']
    parent=a['parent'];pg=parent['gradient'];G=a['gradient'];H=a['hessian']
    graph_Pi=G[vi];standalone_parent_Pi=pg[106:212]
    # Source germ is explicit, not silently changed to a previous real Pi.
    graph_constitutive=np.r_[G[vi]-graph_Pi,G[yi]]
    parent_same_graph_target=np.r_[pg[106:212]-graph_Pi[:106],pg[212:]]
    xids=np.r_[np.arange(106),252+np.arange(106)]
    n=106;full_velocity=eta[vi]
    Eparent=eta[106:212]@pg[106:212]-parent['value']
    Egraph=full_velocity@graph_Pi-a['value']
    Echild=Egraph-Eparent-a['reference_clock_work']
    fields={};coframe=[]
    for arm,x in enumerate(raw):
        q,v,m,delta,dr,wall,Cstar=_geometry_variables(x[:100]);f=_fields(12,q,v,m,wall)
        radius=f['A']*f['B']/_sqrt(f['A']*f['A']+f['B']*f['B'])
        U=f['C']*(dr+f['beta'])/f['N'];lapse=f['N']*_sqrt(1-U*U)
        slope=np.zeros(100,complex);slope[:37]=x[37:74];slope[98]=x[99]
        coframe.append((radius,lapse))
        for name,jet in(('R4',radius),('induced_lapse',lapse),('wall_U',U)):
            fields[f'arm_{arm}_{name}']=np.array(jet.value)
            fields[f'arm_{arm}_{name}_raw_geometry_first']=jet.gradient
            fields[f'arm_{arm}_{name}_raw_geometry_second']=jet.hessian
        fields[f'arm_{arm}_R4_coordinate_rate_from_actual_velocity']=np.array(radius.gradient@slope)
        fields[f'arm_{arm}_R4_proper_rate_from_actual_velocity']=np.array((radius.gradient@slope)/lapse.value)
        fr=canonical_central_frame(x,rep)
        fields[f'arm_{arm}_named_frame_covectors']=fr['named_frame_covectors']
        fields[f'arm_{arm}_literal_gauge_generators']=fr['literal_generators']
        fields[f'arm_{arm}_graph_gauge_source_pairing']=fr['literal_generators'].T@np.r_[graph_Pi[arm*n:(arm+1)*n],G[yi[arm*40:(arm+1)*40]]]
    Rp,Rc=(x[0]for x in coframe);d=18
    chart=canonical_reset_chart(Rp.value**1.5*np.eye(d),Rc.value**1.5*np.eye(d),np.eye(d))
    # All derivatives are analytic real-coordinate jets. The common frame
    # I is the retained gauge coordinate quotient, not a new seam phase.
    log_first=np.zeros(536,complex);log_second=np.zeros((536,536),complex)
    for sign,offset,r in((-1,0,Rp),(1,268,Rc)):
        sl=slice(offset,offset+100)
        log_first[sl]+=sign*1.5*r.gradient/r.value
        log_second[sl,sl]+=sign*1.5*(r.hessian/r.value-np.outer(r.gradient,r.gradient)/r.value**2)
    ratio=chart['canonical_value_reset'][0,0]
    scalar_first=ratio*log_first
    scalar_second=ratio*(log_second+np.outer(log_first,log_first))
    tr=[holomorphic_moving_trace(x)for x in raw]
    arrays=dict(raw_pair=raw,reference_pair=reference,master_lift=R,
        full_joint_gradient=G,full_joint_Hessian=H,
        parent_standalone_gradient=pg,parent_standalone_Hessian=parent['hessian'],
        joint_canonical_Pi=graph_Pi,parent_standalone_Pi=standalone_parent_Pi,
        joint_canonical_position_force=G[xids],parent_standalone_position_force=pg[:106],
        joint_algebraic_constraint_rows=G[yi],parent_standalone_algebraic_rows=pg[212:],
        parent_joint_minus_standalone_algebraic_rows=G[yi[:40]]-pg[212:],
        parent_joint_minus_standalone_Pi=graph_Pi[:106]-standalone_parent_Pi,
        parent_with_joint_Pi_original_constitutive_rows=parent_same_graph_target,
        joint_with_its_action_Pi_original_constitutive_rows=graph_constitutive,
        joint_temporal_face_dual=a['temporal_cotangent'],
        joint_temporal_face_dual_first=a['temporal_cotangent_first'],
        actual_reference_clock_work=np.array(a['reference_clock_work']),
        parent_energy=np.array(Eparent),child_energy_with_reference_work=np.array(Echild),
        incoming_outgoing_geometric_trace_values=np.array([x['value']for x in tr]),
        original226_candidate_rows=state['original226_rows'],
        **fields,**{k:v for k,v in chart.items()if isinstance(v,np.ndarray)},
        canonical_density_ratio_raw_first=scalar_first,
        canonical_density_ratio_raw_second=scalar_second,
        outgoing_analytic_conormal_reset=-chart['analytic_covector_reset'],
        outgoing_Hilbert_conormal_reset=-chart['Hilbert_covector_reset'])
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    if p.stat().st_size>=10*1024**2:raise ValueError('split complete canonical trace arrays rather than prune')
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/path).read_bytes()).hexdigest()!=h for path,h in refs.items()):raise RuntimeError('same coupled candidate or action pins changed')
    norm=lambda x:float(np.linalg.norm(x));maxabs=lambda x:float(np.max(abs(x)))
    record=dict(classification='EVALUATED_SAME_COMPLEX_RESET_CANDIDATE_CANONICAL_FORCE_AND_HALF_DENSITY_TRACE',
        input_hashes=refs,archives={'application.npz':dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        supplied_reset_status=md['status'],all_original226_rows_max=md['original226_rows_max'],
        coupled_reset_tolerance=md['tolerance'],full_reset_guard_passed=md['original226_rows_max']<=md['tolerance'],
        joint_incoming_algebraic_max=maxabs(G[yi[:40]]),joint_child_algebraic_max=maxabs(G[yi[40:]]),
        parent_standalone_algebraic_max=maxabs(pg[212:]),
        incoming_graph_minus_parent_standalone_algebraic_max=maxabs(G[yi[:40]]-pg[212:]),
        joint_incoming_minus_parent_standalone_Pi_norm=norm(graph_Pi[:106]-standalone_parent_Pi),
        parent_with_joint_Pi_constitutive_max=maxabs(parent_same_graph_target),
        action_generated_joint_Pi_norm=norm(graph_Pi),
        action_generated_joint_force_norm=norm(G[xids]),
        parent_standalone_force_norm=norm(pg[:106]),
        geometric_trace_value_difference_max=maxabs(tr[1]['value']-tr[0]['value']),
        half_density_value_reset_I_defect=maxabs(chart['canonical_value_reset']-np.eye(d)),
        analytic_value_dual_pairing_defect=maxabs(chart['analytic_covector_reset'].T@chart['canonical_value_reset']-np.eye(d)),
        half_density_ratio_real=float(ratio.real),half_density_ratio_imag=float(ratio.imag),
        parent_radius=[Rp.value.real,Rp.value.imag],child_radius=[Rc.value.real,Rc.value.imag],
        parent_induced_lapse=[coframe[0][1].value.real,coframe[0][1].value.imag],
        child_induced_lapse=[coframe[1][1].value.real,coframe[1][1].value.imag],
        trace_owner=action_definition()['trace_graph'],
        raw_reset_scope='retained common spin/gauge coordinate frame I, all original fields and derivative branches transported together; not a new physical seam parameter',
        density_owner='chi_point=R4^(3/2)psi_point/V; fixed angular normalization cancels in reset ratio',
        lapse_used_as_spinor_amplitude=False,
        bosonic_canonical_momenta_identified_with_spinor_square_conormals=False,
        new_arm_proper_clock_spans_or_energy_envelope_phase_selected=False,
        canonical_Pi_computed_from_same_action_not_historical_real_packets=True,
        parent_own_algebraic_compatibility_inferred_from_joint_rows=False,
        graph_canonical_force_is_not_standalone_parent_force=True,
        original_action_or_parameters_changed=False,action_parameters=md['action_parameters'],
        physical_Bin_Bout_first_hit_or_Pauli_selected=False,
        exact_next_application='retain joint inherited-profile backreaction in canonical parent/child continuation; bind the selected simple oriented first-hit and its moving trace/source jets before canonical-stop/Friedrichs exterior attachment; no old eigenline or z=E^2 substitution',
        error_scope='binary analytic same536 action and complete value/first/second density trace on the saved finite conditional reset candidate; no physical branch, pole, LSZ or observable enclosure')
    p=out/'result.json';p.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),
        parent_standalone_algebraic_max=record['parent_standalone_algebraic_max'],
        joint_incoming_algebraic_max=record['joint_incoming_algebraic_max'],
        Pi_difference_norm=record['joint_incoming_minus_parent_standalone_Pi_norm'],
        density_reset_I_defect=record['half_density_value_reset_I_defect'],
        reset_guard_passed=record['full_reset_guard_passed'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,
        default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.source_folder,a.output)
