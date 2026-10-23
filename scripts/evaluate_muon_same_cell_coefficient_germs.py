"""Evaluate same-background source coefficient germs on both chronological arms."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_same_cell_coefficient_germs import same_cell_coefficient_germs,divided_coefficient_germs
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve earlier coefficient applications')
    arrays={};rows=[];hashes={}
    for side in ('incoming','outgoing'):
        folder=('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
            else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        phase=load_profile_preserving_phase(folder);hashes.update(phase['input_hashes'])
        if phase['receipt']['steps']!=1:raise ValueError('bind the same changing-current one-cell domain')
        span=phase['receipt']['span'];stage=phase['arrays'][phase['stage_key']][0];tm=span/2
        kw={}if side=='incoming'else dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
        def evaluate(t):return same_cell_coefficient_germs(stage,tm,t,phase['representation'],**kw)
        z,w=np.polynomial.legendre.leggauss(6)
        # Same two halves as the tent and smooth DG weak source.
        u=np.concatenate(((z+1)*abs(span)/4,(z+3)*abs(span)/4))
        times=u+(span if side=='incoming'else 0.)
        apps=[evaluate(float(t))for t in times]
        arrays[side+'_coordinate_time']=times
        arrays[side+'_chronological_coordinate_weights']=np.tile(w*abs(span)/4,2)
        names=tuple(apps[0]['germs'])
        for name in names:arrays[side+'_'+name]=np.array([a['germs'][name]for a in apps])
        arrays[side+'_explicit_inherited_clock']=np.array([a['explicit_inherited_clock']for a in apps])
        anchor=evaluate(tm)
        divided={order:[divided_coefficient_germs(evaluate,float(t),tm,quadrature_order=order)
            for t in times]for order in (4,8)}
        for name in names:
            for order in (4,8):arrays[side+'_'+name+'_divided_'+str(order)]=np.array([a[name]for a in divided[order]])
        fd_errors={};eps=1e-6
        plus=evaluate(tm+eps);minus=evaluate(tm-eps)
        for name in names:
            fd_errors[name]=float(abs((plus['germs'][name][0]-minus['germs'][name][0])/(2*eps)-anchor['germs'][name][1]))
        rec=dict(side=side,length=abs(span),future_coordinate_time_origin=span if side=='incoming'else 0.,
            midpoint_germs={name:jet.tolist()for name,jet in anchor['germs'].items()},
            midpoint_first_difference_absolute_errors=fd_errors,
            divided_derivative_quadrature_4_8_max_difference=float(max(np.max(abs(arrays[side+'_'+name+'_divided_4']-
                arrays[side+'_'+name+'_divided_8']))for name in names)),
            inherited_clock_first_norm=float(np.linalg.norm(arrays[side+'_explicit_inherited_clock'][:,1])))
        rows.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    for name in ('src/bhsm/interface/muon_same_cell_coefficient_germs.py',
        'src/bhsm/interface/muon_profile_preserving_phase_sample.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_birth_finite_normal_trace_graph.py',
        'src/bhsm/interface/muon_birth_inherited_finite_normal_phase.py',
        'src/bhsm/interface/muon_inherited_lepton_temporal_weak_action.py',
        'tests/test_muon_same_cell_coefficient_germs.py',Path(__file__).relative_to(ROOT).as_posix()):
        hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in hashes.items()):
        raise RuntimeError('consumed same-cell coefficient owner changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_SAME_BACKGROUND_COEFFICIENT_AND_STABLE_DIVIDED_GERMS',
        records=rows,input_hashes=hashes,archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,
            sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        current_consumer='exact source-directed weak-trial enrichment of b²/R,b²/N,b*g/R,b*gprime/N and inherited kappa placements',
        computational_basis_selects_physical_covariance=False,
        derivative_order=['value','future-coordinate first','future-coordinate second'],
        variable_At_time_derivative_substituted=False,
        physical_history_or_cutoff_or_Pauli_selected=False,
        error_scope='binary64 analytic action jets and inside-cell coefficient evaluation; finite differences and4/8Gauss divided derivatives are diagnostics, not uniform continuum, response or anomaly enclosures')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],archive=result['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.output)
