"""Consume the inherited child bulk action and all prescribed-source returns."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_inherited_magnetic_weak_combination import combine_inherited_magnetic_weak_action
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,faces_folder,output):
    source=ROOT/source_folder;faces=ROOT/faces_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve source-on weak combination')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('same checkout required')
        b=p.read_bytes();h=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=h
        if expected is not None and h!=expected:raise ValueError('same action/source pin differs')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    sm=read(source/'result.json');fm=read(faces/'result.json')
    if not sm['actual_parent_birth_action_reconstituted_at_preserved_free_q_Pi']:
        raise ValueError('actual source-on inherited continuation required')
    pins.update(sm['input_hashes']);pins.update(fm['input_hashes'])
    reports={};prepared=[]
    names=('total_field','canonical_momentum','total_field_first','canonical_momentum_first')
    for case in('normal_basis','area_source'):
        pname=f'{case}_inherited_on_source_points.npz'
        points=read(source/pname,sm['archives'][pname]['sha256'])
        # The face producer defines these prefix keys and records its own
        # canonical state reconstruction. No new inverse or fitted face.
        fname=f'{case}_actual_source_corner.npz'
        a=read(faces/fname,fm['archives'][fname]['sha256'])
        f=[{n:a[prefix+'_'+n]for n in names}for prefix in('initial','final','corner_left','corner_right')]
        original=ROOT/f'artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_{case}_run_1'
        om=read(original/'result.json');forms=[];first=[]
        for j in range(2):
            n=f'stage_{j}_original_signed_forms.npz';forms.append(read(original/n,om['archives'][n]['sha256']))
            dirs=[]
            for label in('high','low'):
                n=f'stage_{j}_original_signed_forms_first_{label}.npz';dirs.append(read(original/n,om['archives'][n]['sha256']))
            first.append({n:np.array([d[n]for d in dirs])for n in('K','M','B_forward','B_reverse')})
        prepared.append((case,points,f,a['named_constraint'],forms,first))
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for name in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_inherited_magnetic_weak_combination.py'):
        pins[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def summary(a):
        return dict(norm=float(np.linalg.norm(a)),maximum=float(np.max(abs(a))))
    for case,points,f,C,forms,first in prepared:
        r=combine_inherited_magnetic_weak_action(forms,first,points,*f,C)
        arrays={n:v for n,v in r.items()if isinstance(v,np.ndarray)}
        arrays.update({'point_'+n:v for n,v in r['points'].items()})
        arrays.update({'integrated_'+n:v for n,v in r['integrated'].items()})
        arrays.update(scale=points['scale'],cell=points['cell'],sigma=points['sigma'])
        p=out/f'{case}_combined_signed_bulk_source_and_returns.npz';_compressed_npz(p,arrays)
        if p.stat().st_size>=10*1024**2:raise ValueError('compact consumer output below10MiB required')
        archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        report=dict(source_points=len(points['cell']),integrated={n:summary(v)for n,v in r['integrated'].items()},
            combined={n:summary(v)for n,v in r.items()if isinstance(v,np.ndarray)},
            fixed_declared_coordinate_interval_and_quadrature=True,
            inherited_source_on_at_birth_and_actual_endpoint_fields_consumed=True,
            coefficient_corner_full_momentum_jump_consumed=True,
            physical_formation_energy_gamma_exterior_and_native_operator_not_solved=True)
        reports[case]=report;print(json.dumps(dict(case=case,**report),sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('consumed action/source changed')
    result=dict(classification='EVALUATED_INHERITED_SIGNED_MAGNETIC_ACTION_SOURCE_AND_TEMPORAL_RETURNS',
        input_hashes=pins,archives=archives,applications=reports,source_folder=source_folder.as_posix(),faces_folder=faces_folder.as_posix(),
        original_K_BF_BR_M_coefficient_and_both_response_slots_consumed=True,
        all_wall_frame_source_work_and_initial_corner_outer_returns_retained=True,
        literal_analytic_dual_not_Hilbert_adjoint=True,quantum_native_mean_insertions_overlap_or_Pauli_completed=False,
        identity_scope='original action independently contracted; .5 q.T Euler plus .5 temporal q.TPi returns used only to check weak integration. No Green cancellation used as native calculation.',
        error_scope='fixed-coordinate signed constant-stage action and declared C1 source quadrature. Closure defects are retained quadrature/representation diagnostics, not a normalized magnetic or a_mu uncertainty.',
        next_owned_application='combine these actual source-on action returns with full coupled birth/formation/energy/tension and exterior trace equations before physical pole, residue, charge and same-background native Pauli matching')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),pins=len(pins),archives=len(archives))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in('source-folder','faces-folder','output'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();materialize(a.source_folder,a.faces_folder,a.output)
