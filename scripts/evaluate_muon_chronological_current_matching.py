"""Apply whole-graph source pairing and its computational normalization forms.

No physical external pole is assigned by this finite boundary inverse.
The complex analytic dual, Hilbert Gram and independently reflected base
are kept as different operands until their owned matching is established.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_chronological_current_matching import (
    current_transfer_chunk,current_test_forms,continued_base_dual_images)
from bhsm.interface.muon_transported_native_pairing import transported_native_vertices
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_source_directed_em_normal_current import holomorphic_charge_projection
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES


def materialize(current_folder,output):
    base=ROOT/current_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every matching action application')
    refs={}
    def read(p,expected=None):
        h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same current/action operand changed: '+str(p))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
    md=read(base/'result.json');refs.update(md['input_hashes'])
    if md['current_kind']!='literal':raise ValueError('all original coupled literal source rows required')
    action=ROOT/'artifacts/muon_chronological_n1_field_action_20261011/run_1'
    am=read(action/'result.json');refs.update(am['input_hashes'])
    native=ROOT/'artifacts/muon_transported_native_pairing_20261011/run_1'
    nm=read(native/'result.json')
    incidence_folder=ROOT/'artifacts/muon_nonlinear_chronological_n0_action_20261011/run_2'
    im=read(incidence_folder/'result.json')
    inc=read(incidence_folder/'chronological_field_incidence.npz',im['archives']['chronological_field_incidence.npz']['sha256'])
    state_folder=ROOT/am['classical_base'];sm=read(state_folder/'result.json')
    x=np.r_[np.zeros((1,84),complex),np.concatenate([
        read(p,sm['archives'][p.name]['sha256'])['field_coefficients']
        for p in sorted(state_folder.glob('iteration_1_state_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))])]
    pieces=[read(p,am['archives'][p.name]['sha256']) for p in
            sorted(action.glob('owned_current_point_sources_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))]
    points={k:np.concatenate([a[k] for a in pieces]) for k in pieces[0]}
    pieces=[read(p,nm['archives'][p.name]['sha256']) for p in
            sorted(native.glob('native_coframe_nodes_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))]
    native_points={k:np.concatenate([a[k] for a in pieces]) for k in pieces[0]}
    if not (x.shape==(1151,84) and len(points['measure'])==len(native_points['measure'])==3832):
        raise ValueError('the same complete converged base and all corner points required')
    if not np.array_equal(points['rows'],native_points['rows']):raise ValueError('original chronological incidence changed')
    operator_refs={k:sha256((ROOT/k).read_bytes()).hexdigest() for k in
                   ('src/bhsm/interface/muon_chronological_current_matching.py',
                    'tests/test_muon_chronological_current_matching.py',Path(__file__).relative_to(ROOT).as_posix())}
    refs.update(operator_refs)
    out.mkdir(parents=True);archives={}
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split complete consumer matrices')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    family=md['family'];fi=FAMILY_INDICES[family];reduction=homogeneous_scalar_degree_reduction(1)
    E=reduction['full_real_angular_derivatives'];alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi]
    angular=sum(np.kron(-1j*a,e) for a,e in zip(alpha,E))
    G=lepton_unit_trace_gauge_representation()['generators'][:,fi][:,:,fi]
    W=inc['original_n0_wall_coordinate_map'];body=[];dual_def=[];reflection_def=[];shifts=[];Q=[]
    right_bodies=[];literal_bodies=[];reflected_bodies=[];wall_coefficients=[]
    vertex_def=[];charge_def=[];Hdef=[];coframe_def=[];mass_comm=[];total_comm=[]
    for iq in range(3832):
        q={k:v[iq] for k,v in native_points.items()};point={k:v[iq] for k,v in points.items()}
        v=sum(complex(p)*x[int(j.real)] for j,p,d in q['rows']);c=W@v
        maps=transported_native_vertices(q['R'],q['N'],q['Rsharp'],q['Nsharp'],family=family)
        H0=q['H18'][np.ix_(fi,fi)];Hs0=q['Hsharp18'][np.ix_(fi,fi)]
        a=continued_base_dual_images(H0,Hs0,c,maps['vertices'],maps['vertices_sharp'])
        right_bodies.append(a['right_body']);literal_bodies.append(a['literal_analytic_dual_body'])
        reflected_bodies.append(a['separately_reflected_base_body']);wall_coefficients.append(c)
        H=a['right_body'];body.append(np.kron(H,np.eye(4))+angular/q['R'])
        dual_def.append(np.linalg.norm(a['literal_minus_Hilbert_dagger']))
        reflection_def.append(np.linalg.norm(a['reflected_minus_Hilbert_dagger']))
        shifts.append(np.linalg.norm(H-H0))
        vertex_def.append(np.max(abs(point['current_vertices'][family-1]-maps['vertices'])))
        Hdef.append(np.max(abs(point['updated_H_realified']-(q['raw_fields'][-8:-4]+c[20:]))))
        coframe_def.append(max(abs(point['N']-q['N']),abs(point['R']-q['R']),
                               abs(point['measure']-q['original_holomorphic_measure'])))
        s=holomorphic_charge_projection(point['updated_H_realified'])['unit_Tr16_charge_coefficients']
        charge=1j*np.einsum('c,cij->ij',s,G);Q.append(charge)
        temporal=np.einsum('c,cij->ij',s,maps['vertices'][:4])
        charge_def.append(max(np.max(abs(charge@charge+charge)),np.max(abs(q['N']*temporal+charge))))
        # Only the Yukawa/H sector is required to commute with its own
        # unbroken charge. Active charged gauge fields need not commute.
        from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
        HM=_higgs_mass_realified(point['updated_H_realified'])[np.ix_(fi,fi)]
        mass_comm.append(np.linalg.norm(charge@HM-HM@charge))
        total_comm.append(np.linalg.norm(charge@H-H@charge))
    body=np.array(body);Q=np.array(Q)
    for start in range(0,3832,128):
        stop=min(start+128,3832);sl=slice(start,stop)
        save(f'converged_body_and_dual_nodes_{start}.npz',dict(original_quadrature_start=np.array(start),
            right_body=np.array(right_bodies[sl]),literal_analytic_dual_body=np.array(literal_bodies[sl]),
            separately_reflected_base_body=np.array(reflected_bodies[sl]),
            converged_wall_coordinate_increment=np.array(wall_coefficients[sl]),selected_charge=Q[sl],
            same_current_temporal_values=points['current_FE2_values'][sl],same_original_measure=points['measure'][sl],
            same_native_geometric_measure=native_points['measure'][sl],same_original_rows=points['rows'][sl]))
    at=np.flatnonzero(inc['quadrature_provenance'][:,5].real==(0 if md['source_side']=='incoming' else 1))
    forms=current_test_forms(points['current_FE2_values'][at],points['measure'][at],native_points['measure'][at],body[at])
    save('complete_current_test_forms.npz',dict(**{k:v for k,v in forms.items() if isinstance(v,np.ndarray)},
        current_test_shape=np.array([2,6,4]),source_column_shape=np.array([6,2,6,4]),
        quadrature_source_indices=at,body_shift_norm=np.array(shifts),literal_dual_Hilbert_defect=np.array(dual_def),
        separately_reflected_base_Hilbert_defect=np.array(reflection_def),charge_identity_defect=np.array(charge_def),
        selected_charge_Yukawa_commutator_norm=np.array(mass_comm),selected_charge_total_body_commutator_norm=np.array(total_comm)))
    # Complete cross-external columns, rather than the six diagonal48
    # contractions exported by the separate source solves. Rows stream;
    # the full field inverse is never constructed.
    total=np.zeros((288,288),complex);check=np.zeros_like(total);spectators=[]
    for spectator in range(2):
        transfer=np.zeros_like(total);transpose=np.zeros_like(total)
        for start in range(0,1150,8):
            arrays={k:[] for k in ('original_literal_left_transpose_source','original_literal_right_current_source',
                                  'original_current_response','original_transpose_current_adjoint')}
            for spin in range(6):
                name=f'spectator_{spectator}_external_{spin}_nodes_{start+1}.npz'
                a=read(base/name,md['archives'][name]['sha256'])
                if not np.array_equal(a['source_column_indices'],np.arange(spin*48,(spin+1)*48)):
                    raise ValueError('same external/current column order required')
                for k in arrays:arrays[k].append(a[k])
            a={k:np.concatenate(v,axis=2) for k,v in arrays.items()}
            t=current_transfer_chunk(*(a[k] for k in arrays));transfer+=t['source_transfer'];transpose+=t['transpose_transfer']
            if start%128==0:print(json.dumps(dict(stage='complete288_source_pair',spectator=spectator,nodes_done=min(start+8,1150))),flush=True)
        save(f'spectator_{spectator}_complete288_transfer.npz',dict(source_transfer=transfer,independent_transpose_transfer=transpose))
        total+=transfer;check+=transpose
        spectators.append(dict(spectator=spectator,transfer_norm=float(np.linalg.norm(transfer)),
            independent_transpose_difference_max=float(np.max(abs(transfer-transpose)))))
    save('complete288_source_transfer.npz',dict(source_transfer=total,independent_transpose_transfer=check,
        complete_both_spectators=True,source_column_shape=np.array([6,2,6,4])))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same matched operands changed')
    result=dict(classification='EVALUATED_COMMON_GRAPH_COMPLETE_SOURCE_TRANSFER_AND_SEPARATE_MATCHING_FORMS',input_hashes=refs,archives=archives,
        source_side=md['source_side'],family=family,complete_external_C6_columns=6,complete_internal_tests=48,
        complete_original_current_and_adjoint_columns=288,records=spectators,complete_transfer_norm=float(np.linalg.norm(total)),
        complete_transpose_pairing_difference_max=float(np.max(abs(total-check))),
        temporal_Hilbert_Gram_eigenvalues=np.linalg.eigvalsh(forms['temporal_Hilbert_Gram']).tolist(),
        temporal_analytic_Gram_Hilbert_difference_norm=float(np.linalg.norm(forms['temporal_analytic_Gram']-forms['temporal_Hilbert_Gram'])),
        same_current_vertex_difference_max=float(max(vertex_def)),same_base_H_coordinate_difference_max=float(max(Hdef)),
        same_coframe_and_original_measure_difference_max=float(max(coframe_def)),
        converged_body_shift_norm_max=float(max(shifts)),literal_analytic_dual_Hilbert_difference_norm_max=float(max(dual_def)),
        separately_reflected_base_Hilbert_difference_norm_max=float(max(reflection_def)),
        charge_current_identity_defect_max=float(max(charge_def)),selected_charge_Yukawa_commutator_norm_max=float(max(mass_comm)),
        selected_charge_total_body_commutator_norm_max=float(max(total_comm)),
        classical_base_actual_residual_max=sm['actual_classical_residual_max'],
        original_Gauss_frame_connector_and_final_natural_returns_retained=True,
        independent_source_transpose_is_Hilbert_adjoint=False,source_coefficients_conjugated=False,
        positive_native_reference_substituted=False,finite_computational_test_Gram_is_external_LSZ=False,
        physical_pole_charge_body_lifetime_matching=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 source-paired action transfer on all original current rows and both spectators; analytic body/test forms and independently positive computational Gram. Literal complex base-dual comparison is evaluated. No physical exterior/pole amputation, graded mean/overlap, lifetime identification or anomaly enclosure is inferred.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),transfer_norm=result['complete_transfer_norm'],
                         dual_difference=result['literal_analytic_dual_Hilbert_difference_norm_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--current-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.current_folder,a.output)
