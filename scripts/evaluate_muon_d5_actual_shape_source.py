"""Consume the actual child's direct proper-normal coefficient source.

This fixed-time child channel holds parent/reference SOURCE directions,
while retaining their actual pp-rp+rc values. It does not replace the
common-birth incoming/source/reset contacts or the classical induced
response to the separately retained state/rate weak covectors.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_current_source import holomorphic_current_stage
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients,d5_sigma_foliation_eta,d5_material_green_trace
from bhsm.interface.muon_d5_shape_coefficient_source import d5_coefficient_source
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace,moving_d5_material_trace_frame
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(shape_source,output,energy):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every source-channel application')
    pins={};archives={}
    def read(p):
        p=ROOT/shape_source/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    receipt=read(Path('result.json'));data=read(Path('actual_shape_source_and_embedding.npz'))
    pins.update(receipt['input_hashes'])
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];P=phase['coordinates']['lift'];full=full_d5_localized_lepton_trace()
    raw=data['raw_pair'][1];parent=data['raw_pair'][0];refs=data['reference_pair'];b=P@data['shape_direction'][252:]
    zero=np.zeros((268,1),complex);rz=np.zeros((2,268,1),complex)
    if np.max(abs(data['shape_direction'][:252]))!=0:raise ValueError('this is the explicitly child-only direct channel')
    stage=holomorphic_current_stage(raw,b[:,None],parent,zero,refs,rz,rep,side='child')
    wallrep=dict(rep,rho=np.array([WALL]),gauge_basis=rep['wall_trace_map'].transpose(2,0,1)[None,:,None])
    bind=lambda r:d5_trial_stage_coefficients(raw,b[:,None],parent,zero,refs,rz,r,r['rho'],side='child')
    c,cw=bind(rep),bind(wallrep);out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split compact full source images')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('actual_full18_current_and_direct_shape.npz',dict(**stage,actual_raw_pair=data['raw_pair'],actual_reference_pair=refs,
        direct_child_raw_shape=b,actual_coordinate_time=data['coordinate_time'],
        full_classical_weak_state_source=data['full_weak_state_source'],full_classical_weak_rate_source=data['full_weak_phase_rate_source']))
    records=[]
    for eps in(1,-1):
        for branch in('particle','conjugate'):
            g=full['gamma5D_'+branch];generators=full['unitTr16_gauge_particle'];generators=generators if branch=='particle'else generators.conj()
            normal=d5_sigma_foliation_eta(c,gamma=g,carrier_count=16,angular_count=1,sheet_orientation=eps)
            nw=d5_sigma_foliation_eta(cw,gamma=g,carrier_count=16,angular_count=1,sheet_orientation=eps)
            source=d5_coefficient_source(c,gamma=g,generators=generators,eta=normal['sigma_normal_eta_contact'],
                eta_first=normal['sigma_normal_eta_contact_first'][0],energy=energy,sheet_orientation=eps)
            green=d5_material_green_trace(cw,gamma=g,carrier_count=16,angular_count=1,sheet_orientation=eps,point_index=0)
            U=(nw['sigma_normal_timelike_component']/nw['sigma_normal_radial_component'])[0]
            dU=((nw['sigma_normal_timelike_component_first']*nw['sigma_normal_radial_component']-
                nw['sigma_normal_timelike_component']*nw['sigma_normal_radial_component_first'])/nw['sigma_normal_radial_component']**2)[0,0]
            boost=moving_d5_material_trace_frame(-eps*U,-eps*dU,full_representation=full)
            save(f'eta_{eps:+d}_{branch}_D5_direct_coefficient_source.npz',dict(**source,
                sigma_normal_eta_contact=normal['sigma_normal_eta_contact'],sigma_normal_eta_contact_first=normal['sigma_normal_eta_contact_first'],
                **green,spin_frame128=boost['spin_boost128'],spin_frame_source_first128=boost['spin_boost_first128'],
                spin_frame_inverse128=boost['spin_boost_inverse128'],spin_frame_inverse_source_first128=boost['spin_boost_inverse_first128']))
            records.append(dict(eta_sheet=eps,representation=branch,
                D5_coefficient_source_norm=float(np.linalg.norm(source['direct_source_D5_zero_order'])),
                D5_time_principal_source_norm=float(np.linalg.norm(source['direct_source_D5_time_principal'])),
                D5_radial_principal_source_norm=float(np.linalg.norm(source['direct_source_D5_radial_principal'])),
                actual_normal_eta_source_norm=float(np.linalg.norm(normal['sigma_normal_eta_contact_first'])),
                wall_Dirac_bar_Green_source_norm=float(np.linalg.norm(green['original_Dirac_bar_Green_matrix_first'])),
                wall_spin_frame_source_norm=float(np.linalg.norm(boost['spin_boost_first128']))))
    checks=[]
    for step in(2e-5,1e-5):
        pair=[holomorphic_current_stage(raw+sign*step*b,b[:,None],parent,zero,refs,rz,rep,side='child')for sign in(-1,1)]
        checks.append(dict(step=step,body_source_difference=float(np.linalg.norm((pair[1]['Hcan']-pair[0]['Hcan'])/(2*step)-stage['Hcan_first'][0])),
            current_vertex_source_difference=float(np.linalg.norm((pair[1]['canonical_wall_current_vertices']-pair[0]['canonical_wall_current_vertices'])/(2*step)-stage['canonical_wall_current_vertices_first'][0]))))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_d5_shape_coefficient_source.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same actual source/history coefficients required')
    result=dict(classification='EVALUATED_ACTUAL_CHILD_DIRECT_PROPER_NORMAL_D5_AND_CURRENT_COEFFICIENT_SOURCE',input_hashes=pins,archives=archives,
        actual_coordinate_time=data['coordinate_time'].item(),energy=energy,source_amplitude=data['normal_amplitude'].item(),
        source_coordinate_time_first=data['normal_amplitude_coordinate_first'].item(),direct_raw_shape_norm=float(np.linalg.norm(b)),
        full18_body_source_norm=float(np.linalg.norm(stage['Hcan_first'])),full18_current_vertex_source_norm=float(np.linalg.norm(stage['canonical_wall_current_vertices_first'])),
        induced_surface_clock_source=stage['induced_lapse_first'][0],surface_radius_source=stage['R4_first'][0],records=records,
        actual_material_wall_f_source=cw['eta_profile_first'][0,0],actual_material_wall_sigma_source=cw['sigma_first'][0,0],
        directional_controls=checks,actual_pp_minus_rp_plus_rc_values_counted_once=True,
        parent_reference_shape_directions_held_at_fixed_time=True,parent_time_parameter_not_a_future_solved_parent_rate=True,
        incoming_normal_parent_born_reset_constraint_contacts_pending_full_common_source=True,
        full504_classical_state_and_rate_weak_covectors_retained_not_spinor_J=True,
        induced_classical_response_to_g_eta_and_g_rate_not_replaced_by_direct_b=True,
        source_maps_before_normal_mode_or_spinor_projection=True,
        normalized_normal_mode_and_physical_trace_source_firsts_unassigned=True,
        represented_scope='full Spin4/SM16 particle/conjugate coefficients on n0 and original48 radial source points; strong-gauge, off-mode/radial/angular and physical source/domain complements explicit',
        errors_not_enclosed=True,physical_Gamma2_pole_charge_LSZ_Pauli_or_native_observable_admitted=False,physical_a_mu=None,physical_g_mu=None)
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),body_source_norm=result['full18_body_source_norm'],current_source_norm=result['full18_current_vertex_source_norm'],records=records),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--shape-source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--energy',type=float,required=True)
    a=p.parse_args();materialize(a.shape_source,a.output,a.energy)
