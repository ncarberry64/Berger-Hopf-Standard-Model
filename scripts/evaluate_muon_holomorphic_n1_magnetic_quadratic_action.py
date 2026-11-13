"""Consume full changing-row and both causal magnetic response slots, once."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_holomorphic_n1_magnetic_quadratic_action import signed_magnetic_quadratic_source_motion
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(d3_folder,output):
    d3=ROOT/d3_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve reached quadratic-action application')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('same calling checkout required')
        b=p.read_bytes();h=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=h
        if expected is not None and h!=expected:raise ValueError('same supplied action/source pin differs')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    dm=read(d3/'result.json')
    if dm['classification']!='EVALUATED_ACTUAL_CAUSAL_SIGNED_N1_MAGNETIC_D3S_AND_CLASSICAL_MIXED_ACTION':
        raise ValueError('completed actual causal D3 field contraction required')
    pins.update(dm['input_hashes']);source=ROOT/dm['source_folder'];md=read(source/'result.json',dm['source_result_sha256'])
    get=lambda name:read(source/name,md['archives'][name]['sha256'])
    points=get('actual_zero_Cauchy_magnetic_source_points.npz');prefix=get('actual_zero_Cauchy_magnetic_prefix.npz')
    mixed=read(d3/'classical_mixed_action_and_source.npz',dm['archives']['classical_mixed_action_and_source.npz']['sha256'])
    if any(not np.array_equal(points[n],mixed[n])for n in('cell','sigma','scale')):raise ValueError('same causal source quadrature required')
    order=prefix['original_stage_order'];forms=[];first=[]
    for j in order:
        forms.append(get(f'stage_{j}_original_signed_forms.npz'))
        dirs=[get(f'stage_{j}_original_signed_forms_first_{label}.npz')for label in('high','low')]
        first.append({n:np.array([d[n]for d in dirs])for n in('K','B_forward','B_reverse','M')})
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_holomorphic_n1_magnetic_quadratic_action.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual source/action executable changed')
    out.mkdir(parents=True);values={};records=[]
    for i,j in enumerate(points['cell']):
        a=signed_magnetic_quadratic_source_motion(forms[int(j)],first[int(j)],points['total_field'][i],
            points['total_coordinate_rate'][i],points['total_field_first'][i],points['total_coordinate_rate_first'][i])
        for n in('K','B_forward','B_reverse','M','total'):
            a['field_only_D3_motion_'+n]=.5*mixed[n][i]
            a['geometry_profile_coframe_complement_'+n]=a['coefficient_motion_'+n]-a['field_only_D3_motion_'+n]
        for name,v in a.items():values.setdefault(name,[]).append(v)
        record=dict(point_index=i,cell=int(j),sigma=float(points['sigma'][i]),
            coefficient_motion_norm=float(np.linalg.norm(a['coefficient_motion_total'])),
            field_only_D3_motion_norm=float(np.linalg.norm(a['field_only_D3_motion_total'])),
            geometry_profile_coframe_complement_norm=float(np.linalg.norm(a['geometry_profile_coframe_complement_total'])),
            left_response_motion_norm=float(np.linalg.norm(a['left_response_motion_total'])),
            right_response_motion_norm=float(np.linalg.norm(a['right_response_motion_total'])),
            total_first_norm=float(np.linalg.norm(a['total_first_total'])))
        records.append(record);print(json.dumps(dict(stage='full_signed_quadratic_source_motion',side=md['side'],case=md['case'],**record),sort_keys=True),flush=True)
    arrays={name:np.array(v)for name,v in values.items()};scale=points['scale']
    integrated={name:np.einsum('q,q...->...',scale,v,optimize=True)for name,v in arrays.items()}
    arrays.update({'integrated_'+n:v for n,v in integrated.items()})
    arrays.update({'uncancelled_point_absolute_'+n:np.einsum('q,q...->...',abs(scale),np.abs(v),optimize=True)for n,v in values.items()})
    arrays.update(scale=scale,cell=points['cell'],sigma=points['sigma'],original_stage_order=order)
    p=out/'quadratic_action_and_complete_supplied_direction.npz';_compressed_npz(p,arrays)
    if p.stat().st_size>=10*1024**2:raise ValueError('compact actual action contractions below10MiB required')
    archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    summary=lambda a:dict(norm=float(np.linalg.norm(a)),maximum=float(np.max(abs(a))),
        trace_real=[float(np.trace(v).real)for v in a]if a.ndim==3 else float(np.trace(a).real),
        trace_imaginary=[float(np.trace(v).imag)for v in a]if a.ndim==3 else float(np.trace(a).imag))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual source/action executable changed')
    result=dict(classification='EVALUATED_FULL_SUPPLIED_DIRECTION_SIGNED_MAGNETIC_QUADRATIC_ACTION_DERIVATIVE',
        input_hashes=pins,archives=archives,d3_folder=d3_folder.as_posix(),source_folder=dm['source_folder'],
        side=md['side'],case=md['case'],source_points=len(points['cell']),point_records=records,
        action_parameters=dm['action_parameters'],integrated={n:summary(v)for n,v in integrated.items()},
        point_high_low_separately_consumed=True,full_original336_At_Gauss_H_and_profile_rows_retained=True,
        full_stage_coefficient_derivative_M_BF_BR_K_applied=True,
        both_independent_causal_field_response_slots_applied=True,source_wall_and_induced_Higgs_response_retained=True,
        existing_D3_field_partial_compared_with_actual_full_coefficient_motion=True,
        actual_geometry_density_coframe_mechanical_parent_reference_and_H_contacts_not_assigned_zero=True,
        direct_area_field_quadratic_derivative_zero_by_area_geometry_only_action_dependency=True,
        fixed_supplied_numerical_time_steps_and_quadrature_measure=True,
        changing_physical_endpoint_event_clock_span_gamma_law_or_native_heat_mean_not_completed=True,
        analytic_coefficient_dual='literal transpose, not Hilbert conjugation',
        formula='.5 B_a^T deltaForms B_b + .5 deltaB_a^T Forms B_b + .5 B_a^T Forms deltaB_b; every K/BF/BR/M value-rate placement',
        temporal_pullback='same saved -i coordinate-time quadrature measure, unchanged for this supplied source application',
        next_action_relation='these supplied-direction field/current/third-action terms require action-selected birth/exterior and native signed-to-positive/operator source matching before own heat mean, overlap subtraction and physical pole/residue normalization',
        physical_pole_LSZ_or_a_mu_selected=False,
        error_scope='complete supplied binary stage-row polynomial/source derivative and causal response first on finite C2/Hermite/constant-stage/15-point prefix; no fresh action-coefficient or outward physical enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),pins=len(pins),
        coefficient_motion=result['integrated']['coefficient_motion_total'],geometry_complement=result['integrated']['geometry_profile_coframe_complement_total'],
        left_response=result['integrated']['left_response_motion_total'],right_response=result['integrated']['right_response_motion_total'],
        total=result['integrated']['total_first_total'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--d3-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.d3_folder,a.output)
