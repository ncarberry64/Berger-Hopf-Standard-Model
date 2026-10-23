"""Evaluate explicit cutoff derivative on actual chronological raw268 means."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_magnetic_cutoff_mean_contact import actual_cell_even_y_cutoff_target
from bhsm.interface.muon_magnetic_chronological_heat_contact import exact_stored_mean_target_pair
from bhsm.interface.muon_primal_cell_native_heat import actual_cell_heat_polynomial
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(source,output):
    source=Path(source);source=source if source.is_absolute() else ROOT/source
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier applications')
    b=(source/'result.json').read_bytes();r=json.loads(b)
    if r['classification']!='EVALUATED_SAME_MAGNETIC_CELL_DIRECT_PLUS_TRUE_BIRTH_CHRONOLOGICAL_MEAN_HEAT':
        raise ValueError('actual same-background chronological heat contact required')
    refs=dict(r['input_hashes'])
    for p,h in refs.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed action changed: '+p)
    data=(source/'application.npz').read_bytes()
    if sha256(data).hexdigest()!=r['archive']['sha256']:raise ValueError('chronological mean values changed')
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
    refs[(source/'application.npz').relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    with np.load(source/'application.npz',allow_pickle=False) as f:stored={k:f[k].copy() for k in f.files}
    arrays={};rows=[]
    for side in ('incoming','outgoing'):
        candidates=[p for p in refs if p.endswith('/result.json') and 'attached_phase_'+side+'_' in p]
        if len(candidates)!=1:raise ValueError('same-arm actual phase required')
        phase=json.loads((ROOT/candidates[0]).read_bytes())
        bound=load_attached_endpoint(phase['consumed_paired_endpoint_path'],side=side,repository=ROOT,
            radial_points=phase['radial_points'],cap_points=phase['cap_points'])
        p=actual_cell_heat_polynomial(stored[side+'_raw_base'],bound['representation'],length=abs(phase['span']))
        m=stored[side+'_actual_future_raw_mean'];rad=stored[side+'_actual_future_raw_mean_export_radius']
        for row in (z for z in r['records'] if z['side']==side):
            c=row['cutoff_probe'];t=actual_cell_even_y_cutoff_target(p,c)
            k=t['paired_middle_minus_light_raw_cutoff_cotangent'];a=exact_stored_mean_target_pair(k,m,rad)
            label=side+'_q_'+str(row['q_probe']).replace('.','p')
            arrays[label+'_raw_cutoff_target']=k
            for name in ('center','lower','upper'):arrays[label+'_partial_cutoff_mean_contact_'+name]=a[name]
            arrays[label+'_graded_partial_cutoff_mean_contact']=.5*a['center']
            z=dict(side=side,q_probe=row['q_probe'],cutoff_probe=c,
                ordinary_partial_cutoff_mean_contact_trace=float(np.trace(a['center'])),
                graded_partial_cutoff_mean_contact_trace=float(np.trace(a['center'])/2),
                partial_cutoff_mean_contact_norm=float(np.linalg.norm(a['center'])),
                exact_stored_target_pair_maximum_radius=float(np.max(a['upper']-a['lower'])/2),
                boundary_L2_positive_series_tail_upper=t['boundary_L2_positive_series_tail_upper'],
                boundary_L3_positive_series_tail_upper=t['boundary_L3_positive_series_tail_upper'])
            rows.append(z);print(json.dumps(dict(stage='actual_partial_cutoff_DGamma',**z),sort_keys=True),flush=True)
    for name in ('muon_magnetic_cutoff_mean_contact','muon_common_cutoff_green_kernel','muon_primal_cell_native_heat'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_EXPLICIT_CUTOFF_DERIVATIVE_OF_TRUE_BIRTH_CHRONOLOGICAL_MEAN_HEAT',
        input_hashes=refs,archive=dict(path='application.npz',sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),bytes=(out/'application.npz').stat().st_size),
        records=rows,statistics_factor=.5,partial_at_fixed_actual_fields_and_mean=True,
        direct_firstfield_pair_cutoff_derivative_included=False,
        complete_overlap_or_relative_native_cutoff_cancellation_claimed=False,
        physical_formation_cutoff_value_or_total_branch_jets_selected=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='Arb192 saved cutoff target times exact-stored discrete mean export; boundary series tails exact stored spectra only; binary target formation, upstream action/source,Dg and continuum/cutoff matching excluded')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=md['classification'],archive=md['archive'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_magnetic_chronological_heat_contact_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.source,a.output),sort_keys=True))
