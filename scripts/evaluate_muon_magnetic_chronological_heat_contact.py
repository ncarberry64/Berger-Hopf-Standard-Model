"""Contract true-birth chronological mean with the SAME magnetic direct heat."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.muon_magnetic_chronological_heat_contact import (
    raw_mean_export_radii,chronological_mean_heat_application,
)
from evaluate_muon_reached_trace_action import deterministic_archive


def read_packet(folder,json_name,archive_name,classification):
    path=Path(folder);path=path if path.is_absolute() else ROOT/path
    data=(path/json_name).read_bytes();r=json.loads(data)
    if r['classification']!=classification:raise ValueError('required evaluated producer differs')
    refs=dict(r['input_hashes'])
    for p,h in refs.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    data_a=(path/archive_name).read_bytes();h=r.get('numerical_sha256',r.get('archive',{}).get('sha256'))
    if sha256(data_a).hexdigest()!=h:raise ValueError('evaluated input archive changed')
    refs[(path/json_name).relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    refs[(path/archive_name).relative_to(ROOT).as_posix()]=h
    with np.load(path/archive_name,allow_pickle=False) as f:a={k:f[k].copy() for k in f.files}
    return r,a,refs


def materialize(output,*,mean_directory,direct_directory):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier chronological applications')
    md,ma,refs=read_packet(mean_directory,'result.json','application.npz',
        'EVALUATED_TRUE_BIRTH_SOURCE_DRIVEN_CHRONOLOGICAL_MEAN_APPLICATION')
    dd,da,more=read_packet(direct_directory,'source_heat.json','source_heat.npz',
        'EVALUATED_ACTIVE_MAGNETIC_GAUGE_PLUS_H_SAME_CELL_HEAT_SOURCE_PAIR')
    for p,h in more.items():
        if p in refs and refs[p]!=h:raise ValueError('direct source and actual mean use different owners')
        refs[p]=h
    arrays={};records=[];gap=dd['common_zero_Y_gap']
    for side in ('incoming','outgoing'):
        candidates=[p for p in refs if p.endswith('/result.json') and 'attached_phase_'+side+'_' in p]
        if len(candidates)!=1:raise ValueError('unique consumed actual same-arm phase required')
        phase=json.loads((ROOT/candidates[0]).read_bytes())
        bound=load_attached_endpoint(phase['consumed_paired_endpoint_path'],side=side,repository=ROOT,
            radial_points=phase['radial_points'],cap_points=phase['cap_points'])
        base=ma[side+'_raw_midpoint']
        if not np.array_equal(base,da[side+'_raw_fields']):raise ValueError('mean and direct heat are at different base coefficients')
        mean=ma[side+'_future_raw_midpoint_mean']
        P=ma[side+'_coordinate_lift'];rad=raw_mean_export_radii(P,
            ma[side+'_application_midpoint_velocity_algebraic_lift_export_error_upper'])
        arrays[side+'_actual_future_raw_mean']=mean;arrays[side+'_actual_future_raw_mean_export_radius']=rad
        arrays[side+'_raw_base']=base
        for q in (.25,1.,4.):
            label=side+'_q_'+str(q).replace('.','p')
            direct=da[label+'_paired_middle_minus_light_Y2_source_pair_available_source_pair']
            a=chronological_mean_heat_application(base,bound['representation'],mean,rad,
                length=abs(phase['span']),cutoff=q/gap,direct_source_pair=direct)
            for k,v in a.items():
                if isinstance(v,np.ndarray):arrays[label+'_'+k]=v
            arrays[label+'_target_raw_cotangent']=a['target']['paired_middle_minus_light_raw_cotangent']
            arrays[label+'_mean_Y4_directional_tail_estimate']=a['mean_Y4_directional_tail_estimate']['estimate']
            arrays[label+'_active3_graded_direct_plus_mean']=a['graded_direct_plus_chronological_mean'][:3,:3]
            row=dict(side=side,q_probe=q,cutoff_probe=q/gap,
                chronological_coordinate_time=-abs(phase['span'])/2 if side=='incoming' else abs(phase['span'])/2,
                actual_raw_mean_norm=float(np.linalg.norm(mean)),
                mean_contact_trace=float(np.trace(a['mean_contact'])),
                mean_contact_norm=float(np.linalg.norm(a['mean_contact'])),
                graded_direct_plus_mean_trace=float(np.trace(a['graded_direct_plus_chronological_mean']).real),
                graded_direct_plus_mean_norm=float(np.linalg.norm(a['graded_direct_plus_chronological_mean'])),
                exact_stored_pair_maximum_radius=float(np.max(a['mean_contact_upper']-a['mean_contact_lower'])/2),
                quadrature16_32_contraction_difference_norm=float(np.linalg.norm(a['target_refinement_pair'])),
                mean_directional_Y4_tail_estimate_maximum=float(np.max(a['mean_Y4_directional_tail_estimate']['estimate'])),
                mean_Y4_norm_arithmetic_outward_certified=False,
                parent_fixed_birth_q_normal_restriction=True,
                original_mean_arithmetic_certificate=md['applications'][side]['stored_action_arithmetic_certificate'])
            records.append(row);print(json.dumps(dict(stage='actual_chronological_DGamma',**row),sort_keys=True),flush=True)
    for name in ('muon_magnetic_chronological_heat_contact','muon_magnetic_chronological_mean_response',
        'muon_primal_cell_native_heat','muon_birth_attached_phase'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('complete lossless archive exceeds publication cap')
    r=dict(classification='EVALUATED_SAME_MAGNETIC_CELL_DIRECT_PLUS_TRUE_BIRTH_CHRONOLOGICAL_MEAN_HEAT',
        input_hashes=refs,archive=dict(path='application.npz',sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),bytes=(out/'application.npz').stat().st_size),
        common_gap_probe=gap,records=records,active_source_indices=[0,1,2],inactive_padded_source_indices=[3,4,5,6,7],
        mean_source='true-E1 canonical second-mean, source g_v once, propagated through actual same-action incoming/outgoing cells; future raw rates retained',
        previous_per_arm_initial_held_mean_substituted=False,
        first_field_contact_and_both_ordered_insertions_retained=True,complex_Grassmann_statistics_factor=.5,statistics_applied_once=True,
        source_normalization='actual measured e R4²/2 magnetic source once; no extra Tb,QNORM,Haar or scalar2Re factor',
        cutoff_role='one common numerical q/gap probe across arms; physical birth-plus formation value and jets remain separate',
        overlap_scope='unsubtracted finite fermion component; no full continuum local coefficient inferred from partial tent trace; scalar-H1 open topology is distinct; shared continuum QED-VP matching/subtraction remains separate',
        full_moving_geometric_birth_mean_and_full_native_domain_completed=False,
        graded_P_cycle_ghost_relative_eta_external_LSZ_or_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        exact_stored_contraction_error_scope='Arb192 target(binary64) times certified exact-stored discrete mean plus per-entry export radii; target formation, source/assembly and Dg-step errors not enclosed',
        other_errors='direct contour/lag/Y4 ledger inherited; mean target16/32 difference and analytic non-outward directionalY4 estimate separate; no continuum/tent/cutoff/physical matching enclosure')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=r['classification'],archive=r['archive'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mean-directory',type=Path,default=Path('artifacts/muon_magnetic_chronological_mean_response_20261011/run_1'))
    p.add_argument('--direct-directory',type=Path,default=Path('artifacts/muon_magnetic_native_source_heat_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.output,mean_directory=a.mean_directory,direct_directory=a.direct_directory),sort_keys=True))
