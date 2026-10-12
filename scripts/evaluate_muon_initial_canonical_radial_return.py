"""Apply the actual initial canonical radial boundary on the frozen global action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_initial_canonical_field_return import initial_canonical_field_return
from bhsm.interface.muon_native_reset_friedrichs_return import chain_apply
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every canonical boundary application')
    pins={};archives={}
    def read(folder,name):
        p=folder/name;raw=p.read_bytes();h=sha256(raw).hexdigest()
        if name!='result.json'and h!=receipts[folder]['archives'][name]['sha256']:
            raise ValueError('same original action/source changed: '+str(p))
        pins[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(raw)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    action=ROOT/'artifacts/muon_chronological_n1_field_action_20261011/run_1'
    source=ROOT/'artifacts/muon_common_graph_radial_matching_20261011/run_1'
    receipts={folder:read(folder,'result.json')for folder in(action,source)}
    for r in receipts.values():pins.update(r['input_hashes'])
    inc=read(action,'original_n1_angular_and_source_incidence.npz')
    face=read(action,'original_n1_initial_face_reactions.npz')
    names=sorted((k for k in receipts[action]['archives']if k.startswith('original_reduced_n1_KKT_blocks_')),
        key=lambda k:int(Path(k).stem.rsplit('_',1)[1]))
    n=1150;d=176;field=168;At=32;birth=575
    D=np.zeros((n,d,d),complex);U=np.zeros((n-1,d,d),complex);L=U.copy()
    for name in names:
        z=read(action,name);start=int(z['node_start'])-1;stop=int(z['node_stop_exclusive'])-1
        D[start:stop]=z['KKT_diagonal'];ue=start+len(z['KKT_upper'])
        U[start:ue]=z['KKT_upper'];L[start:ue]=z['KKT_lower']
    sources=[read(source,f'spectator_{s}_radial_pairing.npz')for s in range(2)]
    rhs=np.zeros((n,d,8),complex);left=rhs.copy()
    for s,z in enumerate(sources):
        rhs[birth-1,:,4*s:4*s+4]=z['right_source']
        left[birth-1,:,4*s:4*s+4]=z['literal_left_source']
    # One factor/actual boundary map serves both exact n1 spectators;
    # no multiplicity replaces their different source columns.
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_initial_canonical_field_return.py',
        'scripts/evaluate_muon_reached_trace_action.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise RuntimeError('split all actual original rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    print(json.dumps(dict(stage='original_initial_canonical_boundary_factor',nodes=n+1,block=d,source_columns=8)),flush=True)
    a=initial_canonical_field_return(D,U,L,rhs,left,face['initial_to_first_Hessian'],
        frame_rows=inc['frame_rows_per_reduced_node'],gauss_count=At,field_count=field,
        consume_diagonal=True,evaluate_original_residual=False)
    del D
    x=a['initial_canonical_response'];p=a['initial_canonical_literal_adjoint']
    norms=dict(original_rows=0.,Gauss_rows=0.,frame_rows=0.,transpose_rows=0.,
        dynamic_bulk_rows=0.,initial_admissible_conormal=float(np.max(abs(a['initial_admissible_conormal']))))
    for name in names:
        z=read(action,name);start=int(z['node_start'])-1;stop=int(z['node_stop_exclusive'])-1
        r=np.einsum('nij,njc->nic',z['KKT_diagonal'],x[start:stop])-rhs[start:stop]
        rp=np.einsum('nji,njc->nic',z['KKT_diagonal'],p[start:stop])-left[start:stop]
        if start:
            r[0]+=L[start-1]@x[start-1];rp[0]+=U[start-1].T@p[start-1]
        for j in range(start,stop):
            if j<n-1:r[j-start]+=U[j]@x[j+1];rp[j-start]+=L[j].T@p[j+1]
            if j>start:r[j-start]+=L[j-1]@x[j-1];rp[j-start]+=U[j-1].T@p[j-1]
        expected=np.zeros_like(r);expectedp=np.zeros_like(r)
        if stop==n:expected[-1]=a['final_dynamic_force']
        if start==0:expectedp[0,:field]=-(a['admissible_dynamic_map'].T@face['initial_to_first_Hessian']).T@a['adjoint_initial_boundary_reaction']
        err=r-expected;perr=rp-expectedp
        norms['original_rows']=max(norms['original_rows'],float(np.max(abs(err))))
        norms['Gauss_rows']=max(norms['Gauss_rows'],float(np.max(abs(r[:,:At]))))
        norms['frame_rows']=max(norms['frame_rows'],float(np.max(abs(r[:,field:]))))
        norms['transpose_rows']=max(norms['transpose_rows'],float(np.max(abs(perr))))
        if stop==n:err=err[:-1]
        if len(err):norms['dynamic_bulk_rows']=max(norms['dynamic_bulk_rows'],float(np.max(abs(err[:,At:field]))))
        save(f'original_canonical_response_nodes_{start+1}.npz',dict(node_start=np.array(start+1),
            natural_response=a['natural_response'][start:stop],initial_canonical_response=x[start:stop],
            final_force_response=a['final_force_response'][start:stop],
            initial_canonical_literal_adjoint=p[start:stop],original_action_rows=r,
            expected_original_action_boundary_rows=expected,original_transpose_rows=rp,
            expected_original_transpose_boundary_rows=expectedp))
    J=a['admissible_dynamic_map'];before=x[:birth-1,:field]
    prec=float(np.max(abs(before)))
    save('initial_and_final_canonical_boundary.npz',{k:v for k,v in a.items()
        if isinstance(v,np.ndarray)and k not in('natural_response','initial_canonical_response',
            'final_force_response','initial_canonical_literal_adjoint')})
    save('actual_birth_final_and_source_pairings.npz',dict(
        birth_response=x[birth-1],final_response=x[-1],birth_adjoint=p[birth-1],final_adjoint=p[-1],
        actual_right_birth_sources=rhs[birth-1],literal_left_birth_sources=left[birth-1],
        natural_pairing=np.einsum('nic,nij->cj',left,a['natural_response']),
        canonical_pairing=a['initial_canonical_source_Green'],
        independent_transpose_pairing=a['independent_transpose_source_Green'],
        held_initial_complete_field=np.zeros((field,8),complex),
        before_source_field_max=np.array(prec)))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):
        raise RuntimeError('frozen original action/source or executable changed')
    result=dict(classification='EVALUATED_ORIGINAL_GLOBAL_INITIAL_CANONICAL_RADIAL_BOUNDARY_SOURCE_RETURN',
        input_hashes=pins,archives=archives,original_nodes=1151,birth_node=birth,
        source='same canonical radial dual2r x realn1 four columns for each exact spectator; positive original coefficient-dual source',
        original_Gauss_rows_per_node=32,named_frame_rows_per_node=8,original_field_rows_per_node=168,
        initial_coordinate_trace='all original fields held0 by the frozen numerical graph',
        initial_canonical_equation='J.T H01 x1=0 on the explicit dynamic coordinate frame quotient; complete cotangent and frame reactions retained',
        final_boundary='all final Gauss/frame rows retained; final dynamic source solved from initial momentum rather than set0',
        original_boundary_map_numeric_rank=a['final_source_to_initial_conormal_numeric_rank'],
        original_boundary_map_dimension=J.shape[1],
        original_boundary_map_condition=a['final_source_to_initial_conormal_condition'],
        original_before_source_field_max=prec,
        original_initial_Gauss_trace_cotangent_max=float(np.max(abs(a['initial_Gauss_trace_cotangent']))),
        source_transpose_pairing_difference_max=float(np.max(abs(a['source_transpose_pairing_difference']))),
        final_admissible_adjoint_trace_max=float(np.max(abs(a['adjoint_final_admissible_trace']))),
        final_dynamic_force_norm=float(np.linalg.norm(a['final_dynamic_force'])),
        initial_canonical_Green_norm=float(np.linalg.norm(a['initial_canonical_source_Green'])),
        residual_diagnostics=norms,
        retarded_zero_before_source_domain_certified=False,
        finite_Galerkin_boundary_or_coefficient_error_enclosed=False,
        physical_native_Feynman_covariance_or_Pauli_identified=False,
        source_or_transpose_coefficient_conjugated=False,
        numerical_null_eigenvectors_deleted=False,physical_a_mu=None,physical_g_mu=None)
    pth=out/'result.json';pth.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='initial_canonical_boundary_complete',result_sha256=sha256(pth.read_bytes()).hexdigest(),
        before_source_max=prec,boundary_rank=result['original_boundary_map_numeric_rank'],
        boundary_dimension=J.shape[1],condition=result['original_boundary_map_condition'],residuals=norms)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
