"""Apply the explicit source-clock guard to every frozen corrected point."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_charge_source_clock_contract import validated_source_clock_higgs_first
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each actual source-clock contract application')
    refs={}
    def read(path,expected=None):
        path=ROOT/path;digest=sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest!=expected:raise ValueError('frozen clock operand changed')
        refs[path.relative_to(ROOT).as_posix()]=digest
        if path.suffix=='.json':return json.loads(path.read_bytes())
        with np.load(path,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    def shards(folder,prefix):
        md=read(folder/'result.json')
        names=sorted((n for n in md['archives']if n.startswith(prefix)),
                     key=lambda n:int(Path(n).stem.rsplit('_',1)[1]))
        arrays=[read(folder/n,md['archives'][n]['sha256'])for n in names]
        if not arrays:raise ValueError('complete frozen clock corpus required')
        return {k:np.concatenate([a[k]for a in arrays])for k in arrays[0]}
    base=Path('artifacts/muon_common_domain_charge_source_clock_20261011/run_1')
    points=shards(base,'common_domain_charge_and_weak_action_points_')
    body=shards(Path('artifacts/muon_chronological_current_body_20261011/run_1'),
                'corrected_full18_body_points_')
    old=Path('artifacts/muon_nonlinear_chronological_n0_action_20261011/run_2')
    md=read(old/'result.json')
    incidence=read(old/'chronological_field_incidence.npz',
        md['archives']['chronological_field_incidence.npz']['sha256'])
    W=incidence['original_n0_wall_coordinate_map'];pr=incidence['quadrature_provenance']
    if (len(body['N'])!=3832 or not np.array_equal(body['original_rows'],points['original_rows'])
            or not np.array_equal(points['graph_part'],pr[:,6].real.astype(int))):
        raise ValueError('clock guard must act on all3832 SAME original points')
    errors=[];rates=[]
    for q in range(3832):
        value=validated_source_clock_higgs_first(body['H_coordinate_first'][q],
            W[20:]@body['field_coordinate_rate'][q],int(points['graph_part'][q]),
            points['coordinate_slope'][q],body['original_right_clock'][q],body['N'][q])
        errors.append(float(np.max(abs(value['H_source_clock_first']-points['H_source_clock_first'][q]))))
        rates.append(value['analytic_coordinate_source_clock_rate'])
    if max(errors)!=0:raise ValueError('guard changed the already frozen numerical application')
    for name in(Path(__file__).relative_to(ROOT).as_posix(),
                'src/bhsm/interface/muon_charge_source_clock_contract.py',
                'src/bhsm/interface/muon_common_domain_charge_source_clock.py',
                'tests/test_muon_charge_source_clock_contract.py',
                'scripts/evaluate_muon_reached_trace_action.py'):
        refs[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    p=out/'actual_source_clock_contract.npz'
    ordinary=points['graph_part']==0
    deterministic_archive(p,dict(original_quadrature_index=np.arange(3832),
        graph_part=points['graph_part'],ordinary_source_mask=ordinary,
        original_right_clock=body['original_right_clock'],
        analytic_coordinate_source_clock_rate=np.asarray(rates),
        frozen_first_germ_difference=np.asarray(errors)))
    result=dict(classification='EVALUATED_ACTUAL_UNIT_SOURCE_CLOCK_CONTRACT_ON_FROZEN_CORRECTED_CHARGE',
        input_hashes=refs,archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        original_points=3832,ordinary_source_points=int(np.sum(ordinary)),
        ordinary_source_right_clock_difference_max=float(np.max(abs(body['original_right_clock'][ordinary]-1))),
        frozen_numerical_first_germ_difference_max=max(errors),
        nonunit_ordinary_source_clock_rejected=True,connector_clocks_not_rescaled=True,
        earlier_frozen_charge_sources_and_outputs_modified=False,
        physical_charge_pole_LSZ_or_Pauli_assigned=False)
    if any(sha256((ROOT/name).read_bytes()).hexdigest()!=digest for name,digest in refs.items()):
        raise ValueError('source-clock guard inputs changed during application')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),
                         ordinary_source_points=result['ordinary_source_points'],
                         right_clock_difference_max=result['ordinary_source_right_clock_difference_max'],
                         first_germ_difference_max=max(errors))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    materialize(p.parse_args().output)
