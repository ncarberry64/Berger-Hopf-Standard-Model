"""Apply the actual unit EM current to the same changing full18 source germ."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_holomorphic_em_current import changing_unit_em_current
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(current_folder,output):
    src=ROOT/current_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve each changing EM current application')
    pins={}
    def read(p,expected=None):
        b=p.read_bytes();digest=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=digest
        if expected is not None and digest!=expected:raise ValueError('same full18 stage changed')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(src/'result.json');source=ROOT/md['source_folder'];raw_md=read(source/'result.json')
    stages=[];hc=[];dh=[];steps=[];admission=[]
    for row in md['stages']:
        name=row['source_archive'];raw=read(source/name,raw_md['archives'][name]['sha256'])
        name=name.replace('_source_response.npz','_full18_current_stage.npz')
        stages.append(read(src/name,md['archives'][name]['sha256']))
        hc.append(raw['stage_raw'][260:264]);dh.append(np.stack((raw['stage_raw_direction_high'][260:264],raw['stage_raw_direction_low'][260:264]),axis=-1))
        steps.append(raw['coordinate_time_step'].item())
    a=changing_unit_em_current(steps,stages,hc,dh)
    proof={k:v for k,v in a.items()if isinstance(v,np.ndarray)and (k.endswith('_rows')or k.startswith(('charge','unit_Tr16','canonical_current','fixed_Y','literal_')))}
    current={k:v for k,v in a.items()if isinstance(v,np.ndarray)and k not in proof}
    out.mkdir(parents=True);archives={}
    for name,data in [('actual_unit_em_moments_and_charge_rows.npz',proof),('actual_unit_em_current_and_source_placements.npz',current)]:
        p=out/name;_compressed_npz(p,data);archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_holomorphic_em_current.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=s for p,s in pins.items()):raise ValueError('same current source changed')
    norm=lambda x:float(np.linalg.norm(x));maximum=lambda x:float(np.max(abs(x)))
    record=dict(classification='EVALUATED_ACTUAL_CHANGING_FULL18_UNIT_EM_CURRENT_AND_SOURCE_MOTION',
        input_hashes=pins,archives=archives,side=md['side'],case=md['case'],stage_count=len(stages),current_folder=current_folder.as_posix(),
        unit_current_owner='H-selected realified s(H), Q=i*s.G; original material At current JR=-Q/N and independent literal LT=JR.T',
        temporal_test='unit constant full18 coordinate source/target functions on supplied two-stage component; no old FE2 coefficients or exterior spin/pole selection',
        actual_source_norm=norm(a['literal_right']),actual_source_first_high_norm=norm(a['literal_right_first'][:,0]),actual_source_first_low_norm=norm(a['literal_right_first'][:,1]),
        current_norm=norm(a['whole_current']),current_first_high_norm=norm(a['whole_current_first'][0]),current_first_low_norm=norm(a['whole_current_first'][1]),
        operator_and_clock_first_norm=norm(a['operator_and_clock_first']),right_current_motion_first_norm=norm(a['right_current_motion_first']),left_current_motion_first_norm=norm(a['left_current_motion_first']),
        first_placement_sum_rows_max=maximum(a['first_placement_sum_rows']),independent_transpose_value_max=maximum(a['whole_current']-a['independent_transpose_current']),independent_transpose_first_max=maximum(a['whole_current_first']-a['independent_transpose_current_first']),
        charge_identity_max=maximum(a['charge_idempotence_rows']),charge_identity_first_max=maximum(a['charge_idempotence_first_rows']),generator_current_rows_max=maximum(a['canonical_current_coframe_rows']),generator_current_first_rows_max=maximum(a['canonical_current_coframe_first_rows']),
        fixed_Y_mass_charge_rows_max=maximum(a['fixed_Y_mass_charge_rows']),fixed_Y_mass_charge_first_rows_max=maximum(a['fixed_Y_mass_charge_first_rows']),
        high_low_source_terms_retained_before_operator_and_current_products=True,standalone_direct_density_is_zero_only_in_defined_J_transpose_A_inverse_J_component=True,
        named_field_saddle_or_new_frame_reaction_not_introduced=True,whole_operator_gauge_phase_endpoint_contacts_not_assigned_zero=True,
        original_negative_incoming_steps_preserved=md['side']=='incoming',incoming_component_is_backward_control_not_a_past_to_birth_retarded_source=md['side']=='incoming',
        Gamma_initial_held_identity_is_not_physical_Gamma2=True,physical_F1_charge_LSZ_pole_mass_lifetime_or_soft_Pauli_selected=False,
        quantum_contact_both_insertions_own_mean_relative_returns_overlap_not_combined=True,
        error_scope='binary exact supplied constant-stage full18 source/analytic-dual current and first placements; no stage truncation, exterior, loop, charge normalization or anomaly enclosure')
    p=out/'result.json';p.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),current_norm=record['current_norm'],current_first_norm=record['current_first_high_norm'],transpose_max=record['independent_transpose_first_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--current-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.current_folder,a.output)
