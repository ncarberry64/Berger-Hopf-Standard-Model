"""Bind actual changing canonical stages to their full18 current first jets.

Default integration is the original initial-held/free-final fundamental
identity source A chi=-I at continued-energy anchor0. It is an operator
application, not a physical muon source or exterior pole. An optional
owned-moments archive substitutes explicit complete J/L/D and all jets.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_current_source import (
    holomorphic_current_stage,source_varied_unsquared_current_chain,
    attach_current_chain_first,two_term_complex_sum,
)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,side,case,output,moments=None):
    src=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve each actual full18 source application')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('source must belong to the calling checkout')
        b=p.read_bytes();digest=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=digest
        if expected is not None and digest!=expected:raise ValueError('same changing stage archive changed')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(src/'result.json')
    phase,_=retained_input('outgoing',pins);rep=phase['representation']
    if side not in ('incoming','outgoing')or case not in ('normal_basis','area_source'):
        raise ValueError('named actual arm and source required')
    names=sorted(n for n in md['archives']if n.startswith(side+'_')and n.endswith('_'+case+'_source_response.npz'))
    if not names:raise ValueError('no evaluated actual source stages; failed/missing arms are not zero-filled')
    out.mkdir(parents=True);stages=[];rows=[];steps=[]
    def save(name,data):
        p=out/name;_compressed_npz(p,{k:v for k,v in data.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split compact full18 operands')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for name in names:
        a=read(src/name,md['archives'][name]['sha256'])
        dirs=lambda key:np.stack((a[key+'_high'],a[key+'_low']),axis=-1)
        stage=holomorphic_current_stage(a['stage_raw'],dirs('stage_raw_direction'),
            a['parent_source_stage_raw'],dirs('parent_source_stage_raw_direction'),
            a['reference_stage_pair'],dirs('reference_stage_direction'),rep,
            side='parent'if side=='incoming'else'child')
        stage['coordinate_time']=a['coordinate_time'];stage['coordinate_time_step']=a['coordinate_time_step']
        stage['supplied_raw_direction_high']=a['stage_raw_direction_high']
        stage['supplied_raw_direction_low']=a['stage_raw_direction_low']
        for key in ('Hcan_first','induced_lapse_first','R4_first','total_profile_first','full_wall_connection_first'):
            hi,lo=two_term_complex_sum(stage[key][0],stage[key][1])
            stage[key+'_combined_high']=np.asarray(hi);stage[key+'_combined_low']=np.asarray(lo)
        save(name.replace('_source_response.npz','_full18_current_stage.npz'),stage)
        stages.append(stage);steps.append(complex(a['coordinate_time_step']))
        rows.append(dict(source_archive=name,Hcan_norm=float(np.linalg.norm(stage['Hcan'])),
            Hcan_source_high_norm=float(np.linalg.norm(stage['Hcan_first'][0])),Hcan_source_low_norm=float(np.linalg.norm(stage['Hcan_first'][1])),
            parent_source_is_actual_supplied_affine_stage=side=='outgoing',induced_lapse=[stage['induced_lapse'].item().real,stage['induced_lapse'].item().imag]))
    q=len(stages);d=18;k=2
    if moments is None:
        J=-np.broadcast_to(np.eye(d,dtype=complex),(q,d,d)).copy()
        L=np.zeros_like(J);D=np.zeros_like(J)
        dJ=np.zeros((q,k,d,d),complex);dL=dJ.copy();dD=dJ.copy()
        scope='original initial-held/free-final fundamental identity source A chi=-I; full output coordinate basis, not physical muon current or spin state'
    else:
        m=read(Path(moments));J,L,D=(m[n]for n in ('right_source','literal_left','direct_density'))
        dJ,dL,dD=(m[n]for n in ('right_source_first','literal_left_first','direct_density_first'))
        scope='explicit caller-owned current source/target moments and all high/low source contacts; no new source choice'
    chain=source_varied_unsquared_current_chain(np.array(steps),np.array([a['induced_lapse']for a in stages]),
        np.array([a['Hcan']for a in stages]),J,L,D,coordinate_steps_first=np.zeros((q,k),complex),
        lapse_first=np.array([a['induced_lapse_first']for a in stages]),body_first=np.array([a['Hcan_first']for a in stages]),
        right_source_first=dJ,literal_left_first=dL,direct_density_first=dD,energy=0j,energy_first=np.zeros(k,complex))
    for key in ('trace_first','source_return_first','initial_target_first','direct_current_first','proper_clock_span_first'):
        hi,lo=two_term_complex_sum(chain[key][0],chain[key][1]);chain[key+'_combined_high']=np.asarray(hi);chain[key+'_combined_low']=np.asarray(lo)
    save('unsquared_current_source_first.npz',chain)
    # This is the actually owned computational initial trace, with final
    # output a coordinate readout. It is explicitly not physical Bi/Bf.
    nr=J.shape[-1];nl=L.shape[1]
    target=np.eye(d)if moments is None else np.zeros((nl,d),complex)
    boundary=dict(initial_boundary=np.eye(d),final_boundary=np.zeros((d,d)),boundary_source=np.zeros((d,nr)),
        initial_target=np.zeros_like(target),final_target=target,direct_current=np.zeros((target.shape[0],nr)))
    if moments is not None and nl!=d:
        # The original integrated target already has nl rows. No final
        # coordinate readout is appended to an unrelated target space.
        boundary['final_target']=np.zeros((nl,d));boundary['initial_target']=np.zeros((nl,d))
    first={n:np.zeros((k,)+np.shape(a),complex)for n,a in boundary.items()}
    attached=attach_current_chain_first(chain,boundary,first)
    save('owned_initial_trace_Gamma_f_application.npz',attached)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_holomorphic_current_source.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same producer/source bytes changed')
    result=dict(classification='EVALUATED_CHANGING_CANONICAL_FULL18_HOLOMORPHIC_CURRENT_SOURCE_GERM',
        input_hashes=pins,archives=archives,source_folder=source_folder.as_posix(),side=side,case=case,stage_count=q,stages=rows,
        original_coordinate_time_step_orientation_preserved=True,parent_reference_values_and_directions_supplied=True,
        high_low_directions_applied_separately_before_each_body_current_product=True,compensated_combination_remainder_saved=True,
        source_scope=scope,continued_external_energy_anchor=0.,internal_external_energy_derivative_not_selected=True,
        actual_Gamma_initial_held_matrix_identity_max=float(np.max(abs(attached['boundary_matrix']-np.eye(d)))),
        source_transpose_current_identity_max=float(np.max(abs(attached['current']-attached['independent_transpose_current']))),
        first_transpose_current_identity_max=float(np.max(abs(attached['current_first']-attached['independent_transpose_current_first']))),
        no_parent_future_grafted_into_child_affine_source=True,mechanical_profile_pp_minus_rp_plus_rc_count=1,
        trace_map_used_only_from_retained_representation_not_old_background=True,
        initial_held_free_final_computational_domain=True,physical_Bi_Bf_or_event_or_pole_LSZ_Pauli_selected=False,
        physical_mixed_or_internal_loop_derivatives_not_assigned_zero=True,
        all_actual_source_response_files_consumed_even_if_final_rows_fail=True,
        error_scope='binary full18 holomorphic coefficient/analytic derivative and exact constant-stage exponential application; no stage truncation, physical domain or anomaly enclosure')
    path=out/'result.json';path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(path.read_bytes()).hexdigest(),stages=q,first_transpose_max=result['first_transpose_current_identity_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,required=True)
    p.add_argument('--side',choices=('incoming','outgoing'),required=True);p.add_argument('--case',choices=('normal_basis','area_source'),required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--moments',type=Path)
    a=p.parse_args();materialize(a.source_folder,a.side,a.case,a.output,a.moments)
