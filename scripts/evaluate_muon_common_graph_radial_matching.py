"""Canonical radial source on all original common chronological field rows."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_common_graph_radial_matching import common_graph_radial_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,action_folder):
    out=ROOT/output;folder=ROOT/action_folder
    if out.exists():raise FileExistsError('preserve prior common-domain applications')
    md=json.loads((folder/'result.json').read_bytes());pins=dict(md['input_hashes']);archives={}
    pins[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    def read(p,expected=None):
        h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise RuntimeError('original common action changed')
        pins[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    parts=[]
    for p in sorted(folder.glob('original_reduced_n1_KKT_blocks_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1])):
        parts.append(read(p,md['archives'][p.name]['sha256']))
    D=np.concatenate([a['KKT_diagonal']for a in parts]);U=np.concatenate([a['KKT_upper']for a in parts]);L=np.concatenate([a['KKT_lower']for a in parts])
    if len(D)!=1150 or len(U)!=1149 or len(L)!=1149:raise RuntimeError('all original initial-to-final rows required')
    inc=read(folder/'original_n1_angular_and_source_incidence.npz',md['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    initial=read(folder/'original_n1_initial_face_reactions.npz',md['archives']['original_n1_initial_face_reactions.npz']['sha256'])
    loc=ROOT/'artifacts/muon_native_local_overlap_matching_20261011/run_3'
    lm=json.loads((loc/'result.json').read_bytes());pins.update(lm['input_hashes']);pins[(loc/'result.json').relative_to(ROOT).as_posix()]=sha256((loc/'result.json').read_bytes()).hexdigest()
    local=read(loc/'incoming_birth_family_1_local.npz',lm['archives']['incoming_birth_family_1_local.npz']['sha256'])
    H0=local['data_native_node_raw_fields'][-8:-4]
    perm=inc['original_value_permutation'];hv=np.eye(84)[80:][:,perm]
    birth=int(md['birth_real_trace_node']);H=H0+hv@inc['same_n0_field_values'][birth]
    # This is the analytic same-complex-coefficient action section; the
    # opposite harmonic dual alone uses conjugate(U). No coefficient is
    # conjugated, no finite eigenvector is chosen.
    r=H/np.sqrt(H@H)/np.sqrt(2);dual=np.zeros((96,4),complex);dual[80:]=np.kron((2*r)[:,None],np.eye(4))
    results=[];out.mkdir(parents=True)
    def save(name,arrays):
        p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split all complete outputs')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    right=inc['right_current_field_source_lifts'];left=inc['literal_left_current_field_source_lifts']
    for spectator in range(2):
        R=np.zeros((176,4),complex);SL=R.copy();R[:168]=right[spectator]@dual;SL[:168]=left[spectator]@dual
        print(json.dumps(dict(stage='common_radial_factor',spectator=spectator,original_nodes=1151,original_block=176)),flush=True)
        a=common_graph_radial_application(D,U,L,R,SL,birth_index=birth-1,gauss_count=32,field_count=168)
        for start in range(0,1150,64):
            stop=min(1150,start+64);sl=slice(start,stop)
            save(f'spectator_{spectator}_response_{start+1}.npz',dict(node_start=np.array(start+1),
                full_field_response=a['full_field_response'][sl],full_literal_adjoint=a['full_literal_adjoint'][sl],
                original_dynamic_Gauss_frame_residual=a['original_dynamic_Gauss_frame_residual'][sl],
                original_transpose_residual=a['original_transpose_residual'][sl],named_frame_reactions=a['named_frame_reactions'][sl]))
        reaction=initial['initial_to_first_Hessian']@a['full_field_response'][0,:168]
        save(f'spectator_{spectator}_radial_pairing.npz',dict(right_source=R,literal_left_source=SL,
            canonical_radial_boundary_Green=a['canonical_radial_boundary_Green'],
            independent_transpose_radial_Green=a['independent_transpose_radial_Green'],
            source_transpose_pairing_difference=a['source_transpose_pairing_difference'],
            held_initial_face_reaction=reaction,final_natural_field=a['final_natural_field'],
            analytic_radial_section=r,actual_birth_realified_H=H,original_birth_realified_H=H0))
        row=dict(spectator=spectator,radial_trace_average=dict(real=float(np.trace(a['canonical_radial_boundary_Green']).real/4),
            imag=float(np.trace(a['canonical_radial_boundary_Green']).imag/4)),
            original_allrow_residual_max=float(np.max(abs(a['original_dynamic_Gauss_frame_residual']))),
            original_Gauss_residual_max=float(np.max(abs(a['original_Gauss_residual']))),
            original_frame_residual_max=float(np.max(abs(a['original_frame_residual']))),
            original_transpose_residual_max=float(np.max(abs(a['original_transpose_residual']))),
            source_transpose_pairing_difference_max=float(np.max(abs(a['source_transpose_pairing_difference']))))
        results.append(row);print(json.dumps(dict(stage='common_radial_pairing',**row),sort_keys=True),flush=True)
    for p in('src/bhsm/interface/muon_common_graph_radial_matching.py','tests/test_muon_common_graph_radial_matching.py',Path(__file__),
        'src/bhsm/interface/muon_chronological_current_factor.py','scripts/evaluate_muon_reached_trace_action.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise RuntimeError('consumed original action changed')
    result=dict(classification='EVALUATED_COMMON_1151_NODE_ORIGINAL_RADIAL_SOURCE_AND_LITERAL_ADJOINT',input_hashes=pins,archives=archives,records=results,
        original_nodes=1151,field_rows_per_spectator=168,Gauss_rows_per_spectator=32,frame_rows_per_spectator=8,spectators=2,
        birth_node=birth,source='canonical analytic radial dual2r at common birth; all four real n1 source copies; no source Gram division',
        analytic_radial_section_norm_square=dict(real=float((r@r).real),imag=float((r@r).imag)),
        birth_H_classical_update_norm=float(np.linalg.norm(H-H0)),
        boundary='initial trace held; every restored corner and final natural face retained; not the zero-Cauchy inverse or a physical stop',
        same_current_global_boundary_inverse_consumed=True,native_heat_quantum_covariance_or_LSZ_identified=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 complete original common-domain source/transpose application and all-row residuals. No matrix-production/continuum or physical contour/LSZ enclosure. No local Fourier/static Green replaces this boundary inverse.')
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives)),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--action-folder',type=Path,default=Path('artifacts/muon_chronological_n1_field_action_20261011/run_1'))
    a=p.parse_args();materialize(a.output,a.action_folder)
