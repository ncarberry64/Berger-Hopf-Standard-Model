"""Consume reached all67/source3 matrices in the actual Noether boundary work."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_reached_geometry_green_source import canonical_green_source_cell
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(source,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve complete source work')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    md=read(source,'result.json');initial=read(source,'actual_base_boundary_and_source_scope.npz')
    cells=len(md['history']);uh,ul=initial['initial_fiber_high'],initial['initial_fiber_low'];vh=np.zeros((212,3),complex);vl=vh.copy()
    out.mkdir(parents=True);records=[];total_source=np.zeros((67,3),complex);total_asym=total_source.copy();total_frame=total_source.copy();initial_boundary=None
    for k in range(cells):
        u=read(source,f'cell_{k:04d}_all67_original_canonical_rows.npz');v=read(source,f'cell_{k:04d}_zero_Cauchy_geometry_source.npz')
        # Stage H is the exact action input already pinned by the producer.
        key=next(p for p in md['input_hashes']if p.endswith(f'step_{k:04d}_stage.npz'))
        stage=read(Path(key).parent,Path(key).name)
        if sha256((ROOT/key).read_bytes()).hexdigest()!=md['input_hashes'][key]:raise ValueError('same actual full stage action required')
        a=canonical_green_source_cell(stage['stage_Hessian'],stage['coordinate_step'].item(),
            uh,ul,u['canonical_final_high'],u['canonical_final_low'],vh,vl,v['canonical_final_high'],v['canonical_final_low'],
            u['stage_direction_high'],u['stage_direction_low'],v['stage_direction_high'],v['stage_direction_low'],
            v['source_gradient'],u['frame_reaction_rows'],v['frame_reaction_rows'])
        p=out/f'cell_{k:04d}_all67_geometry_source_work.npz';_compressed_npz(p,{x:y for x,y in a.items()if isinstance(y,np.ndarray)})
        archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        if initial_boundary is None:initial_boundary=a['initial_boundary_pairing']
        total_source+=a['full_source_work'];total_asym+=a['literal_action_asymmetry_work'];total_frame+=a['named_frame_work']
        rec=dict(cell=k,green_identity_upper=a['green_identity_upper'],source_work_max=float(np.max(abs(a['full_source_work']))),
            literal_asymmetry_work_max=float(np.max(abs(a['literal_action_asymmetry_work']))),named_frame_work_upper=a['named_frame_work_upper'])
        records.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
        uh,ul=u['canonical_final_high'],u['canonical_final_low'];vh,vl=v['canonical_final_high'],v['canonical_final_low']
    final_boundary=a['final_boundary_pairing'];closure=final_boundary-initial_boundary-total_source-total_asym-total_frame
    p=out/'complete_all67_geometry_source_work.npz';_compressed_npz(p,dict(initial_boundary=initial_boundary,final_boundary=final_boundary,
        full_source_work=total_source,literal_asymmetry_work=total_asym,named_frame_work=total_frame,
        rounded_export_closure=closure))
    archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for p in (Path(__file__),ROOT/'src/bhsm/interface/muon_reached_geometry_green_source.py',ROOT/'tests/test_muon_reached_geometry_green_source.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual source/action image changed')
    result=dict(classification='EXECUTED_ALL67_REACHED_GEOMETRY_SOURCE_NOETHER_BOUNDARY_PAIRING',input_hashes=pins,archives=archives,records=records,
        full_source_work_max=float(np.max(abs(total_source))),full_source_work_norm=float(np.linalg.norm(total_source)),
        natural_final_boundary_pairing_max=float(np.max(abs(final_boundary))),rounded_export_closure_max=float(np.max(abs(closure))),
        literal_action_asymmetry_work_max=float(np.max(abs(total_asym))),named_frame_work_max=float(np.max(abs(total_frame))),
        original_birth226_max=md['original_birth226_max'],all67_force_mismatch_retained=md['all67_clock_scaled_complete_boundary_work_max'],
        no_reset_trace_imposed_as_bulk_force=True,full_source_gradient_before_any_port_restriction=True,
        retarded_source_domain_not_identified_as_outgoing_environment_DtN=True,
        physical_formation_pole_or_normalization_admitted=False,
        error_scope='Literal supplied actual complex midpoint H/source images and both endpoint canonical cotangents. Arithmetic upper bounds concern this stored identity only, not physical action or exterior accuracy.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='all67_geometry_source_work_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),source_work_max=result['full_source_work_max'],export_closure_max=result['rounded_export_closure_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=Path('artifacts/muon_reached_geometry_canonical_return_20261012/run_1'));p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.source,a.output)
