"""Apply the original full coupled field action on the restored corner graph."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_continued_action_reality import actual_source_curve_coefficients,action_reality_coefficient
from bhsm.interface.muon_em_normal_connector_source import source_cell_field_chart,connector_wall_source_coefficients
from bhsm.interface.muon_euclidean_cell_sewing import source_cell_endpoint
from bhsm.interface.muon_reflected_clifford_connector_action import reflected_clock_pair
from bhsm.interface.muon_saved_wall_complex_coefficients import saved_original_wall_coefficient_family,forms_at_complex_offset
from bhsm.interface.muon_continued_connector_field_action import (
    common_field_proper_forms,continued_field_weak_action,continued_field_wall_inverse,
    joint_literal_wall_current_sources,joint_wall_current_responses)
from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_open_action_vertices
from bhsm.interface.muon_source_directed_em_normal_current import holomorphic_charge_projection
from bhsm.interface.muon_normal_matched_photon_current import complete_normal_current_gaunt
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


CASES=dict(incoming_internal=('incoming',96,'incoming',97),
    outgoing_internal=('outgoing',96,'outgoing',97),birth=('incoming',191,'outgoing',0))


def actual_field_corner_quadrature(phases,curves,nodes,field_family,*,case,family,refinement):
    ls,lc,rs,rc=CASES[case];n=refinement;count=2*n+3
    a=source_cell_endpoint(phases[ls],curves[ls],lc,'right')
    b=source_cell_endpoint(phases[rs],curves[rs],rc,'left')
    if a['owned_real_boundary']!=b['owned_real_boundary']:raise ValueError('actual shared real corner required')
    q=[];provenance=[];maps=[]
    def add(side,anchor,z,rows,measure,w,ws,part):
        form=forms_at_complex_offset(side,float(anchor),z,family=field_family)
        original=common_field_proper_forms(form['Lorentz_forms'],form['N'],form['At_count'])
        body=action_reality_coefficient(phases[side],anchor,z)
        V=euclidean_open_action_vertices(body['geometry']['R4'],body['geometry']['N'],family=family)['vertices']
        charge=holomorphic_charge_projection(body['raw'][-8:-4])
        selected=np.zeros_like(V)
        selected[:20]=np.einsum('cd,fcij->fdij',charge['projection'],V[:20].reshape(5,4,6,6)).reshape(20,6,6)
        q.append(dict(forms=original['forms'],rows=rows,measure=measure,right_clock=w,
            selected_vertices_common=selected))
        provenance.append([anchor,complex(z),measure,w,ws,0 if side=='incoming'else 1,part])
        maps.append(form['wall_trace_map'])
    for side,cell,rowids in((ls,lc,(0,1)),(rs,rc,(2,3))):
        idx=np.flatnonzero(nodes[side]['source_cell']==cell)
        chart=source_cell_field_chart(nodes[side],cell)
        length=float(np.sum(nodes[side]['weight'][idx]));left=chart['proper_center']-length/2
        for iq in idx:
            u=(nodes[side]['proper_time'][iq]-left)/length
            add(side,float(nodes[side]['coordinate_anchor'][iq]),nodes[side]['coordinate_offset'][iq],
                ((rowids[0],1-u,-1/length),(rowids[1],u,1/length)),nodes[side]['weight'][iq],1,1,0)
    connector_nodes=[1,*range(4,count),2];gx,gw=np.polynomial.legendre.leggauss(4)
    for seg,(side,cell,start,stop) in enumerate(((ls,lc,a['coordinate_endpoint'],a['owned_real_boundary']),
                                               (rs,rc,b['owned_real_boundary'],b['coordinate_endpoint']))):
        chart=source_cell_field_chart(nodes[side],cell);slope=complex(stop)-complex(start)
        for j in range(n):
            for x,g in zip(gx,gw):
                v=(x+1)/2;s=(j+v)/n;t=complex(start)+s*slope
                source=connector_wall_source_coefficients(phases[side],chart,t,family=family,quadrature_order=8)
                clocks=reflected_clock_pair(source['right_geometry']['N'],source['reflected_geometry']['N'],slope)
                add(side,chart['coordinate_anchor'],t-chart['coordinate_anchor'],
                    ((connector_nodes[seg*n+j],1-v,-n),(connector_nodes[seg*n+j+1],v,n)),
                    g/(2*n)*clocks['right_clock'],clocks['right_clock'],clocks['reflected_clock'],seg+1)
    P=maps[0]
    if any(not np.array_equal(P,p)for p in maps[1:]):raise ValueError('common original wall coefficient representation changed')
    # Same-field shared-corner reference: retain the two source-cell
    # actions and identify their endpoint trace, without connector action.
    sewn=[dict(r,rows=tuple(({0:0,1:1,2:1,3:2}[j],p,d)for j,p,d in r['rows']))
          for r,pr in zip(q,provenance)if pr[-1]==0]
    return dict(quadrature=q,sewn_quadrature=sewn,temporal_nodes=count,
        wall_trace_map=P,quadrature_provenance=np.asarray(provenance,complex),
        connector_nodes=np.array(connector_nodes),initial_trace_node=0,final_natural_trace_node=3,
        source_clock_origin_shift=nodes['incoming']['total_proper_clock']if ls!=rs else 0.,
        coordinate_endpoint_displacement=b['coordinate_endpoint']-a['coordinate_endpoint'])


def materialize(output,*,case,family,refinement):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous field/current applications')
    refs={};archives={}
    def read(p):
        refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    ep=ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2';er=read(ep/'result.json')
    phases,curves,nodes={}, {}, {}
    for side in('incoming','outgoing'):
        phases[side],_=retained_input(side,refs)
        curves[side]=actual_source_curve_coefficients(*(read(ROOT/f'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/{side}_{name}.npz')for name in('phase','velocity','contacts')))
        nodes[side]=read(ep/(side+'_nodes.npz'))
        nodes[side]['total_proper_clock']=next(r['total_proper_clock']for r in er['records']if r['side']==side)
    ff=saved_original_wall_coefficient_family(repository=ROOT);refs.update(ff['input_hashes'])
    cp=ROOT/'artifacts/muon_affine_band_current_covectors_20261011/run_2'
    cr=read(cp/'result.json');C=read(cp/'application.npz');refs.update(cr['input_hashes'])
    for rel in('src/bhsm/interface/muon_continued_connector_field_action.py','src/bhsm/interface/muon_saved_wall_complex_coefficients.py',
        'tests/test_muon_continued_connector_field_action.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,a)
        if p.stat().st_size>=10*1024**2:raise RuntimeError('full original rows must be split before publication')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    graph=actual_field_corner_quadrature(phases,curves,nodes,ff,case=case,family=family,refinement=refinement)
    arm=ff['arms'][CASES[case][0]]['arrays'];frames=arm['central_radial_frame_indices']
    action=continued_field_weak_action(graph['quadrature'],temporal_nodes=graph['temporal_nodes'],At_count=64,frame_indices=frames)
    print(json.dumps(dict(stage='original_field_assembly',case=case,temporal_nodes=graph['temporal_nodes'],
        field_rows=len(action['original_Hessian']),Gauss_rows=len(action['Gauss_rows']),frame_rows=len(action['frame_rows']))),flush=True)
    inv=continued_field_wall_inverse(action,graph['wall_trace_map'])
    print(json.dumps(dict(stage='full_field_wall_inverse',original_row_residual=inv['original_action_row_residual_max'],
        Gauss_row_residual=inv['original_Gauss_row_residual_max'],frame_residual=inv['frame_residual_max'],
        wall_Green_norm=float(np.linalg.norm(inv['wall_source_Green'])))),flush=True)
    gaunt=complete_normal_current_gaunt()['gaunt'];side=CASES[case][2]
    tests=C[f'{side}_family_{family}_C_literal_left_tests']
    src=joint_literal_wall_current_sources(graph['quadrature'],temporal_nodes=graph['temporal_nodes'],
        wall_fields=24,right_harmonics=4,even_gaunt=gaunt,left_tests=tests)
    response=joint_wall_current_responses(inv,src)
    sewn=continued_field_weak_action(graph['sewn_quadrature'],temporal_nodes=3,At_count=64,frame_indices=frames)
    old=continued_field_wall_inverse(sewn,graph['wall_trace_map'])
    # Explicit trace injection, not an assertion that the connector is
    # equivalent to the old sewing. Both original cell traces remain.
    T=np.zeros((graph['temporal_nodes']-1,2));T[0,0]=1;T[1,0]=1;T[2,1]=1
    compare=np.kron(T,np.eye(96))@old['wall_source_Green']@np.kron(T.T,np.eye(96))
    save('wall_inverse_and_graph.npz',dict(wall_source_Green=inv['wall_source_Green'],
        wall_Green_sewn_reference=old['wall_source_Green'],sewn_trace_injection=T,
        restricted_sewn_wall_Green=compare,wall_trace_map=graph['wall_trace_map'],
        quadrature_provenance=graph['quadrature_provenance'],connector_nodes=graph['connector_nodes'],
        Gauss_rows=action['Gauss_rows'],frame_indices=frames))
    for key,obj,size in(('original_Hessian',action,64),('original_all_trace_Hessian',action,64),
            ('field_wall_source_response',inv,128),('original_action_row_residual',inv,128),
            ('initial_face_reaction',inv,128),('frame_reactions',inv,128)):
        a=obj[key]
        for start in range(0,len(a),size):save(key+f'_{start}.npz',{key:a[start:start+size],
            'row_start':np.array(start),'full_shape':np.array(a.shape)})
    save('literal_right_current_and_u.npz',dict(literal_right_current=src['literal_right_current'],wall_u=response['wall_u']))
    # C sources and p remain factored by soft axis/internal slot; no
    # arbitrary scalar Pauli projection or obsolete FE2 bridge is added.
    for axis in range(3):
        a=src['C_literal_left_current'][axis]
        for start in range(0,a.shape[1],64):save(f'C_left_axis_{axis}_internal_{start}.npz',
            dict(C_literal_left_current=a[:,start:start+64],internal_start=np.array(start),full_shape=np.array(a.shape)))
        a=response['wall_p'][:,axis]
        for start in range(0,len(a),48):save(f'wall_p_axis_{axis}_row_{start}.npz',
            dict(wall_p=a[start:start+48],row_start=np.array(start),full_shape=np.array(a.shape)))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    record=dict(classification='EVALUATED_ORIGINAL_COUPLED_FIELD_CONNECTOR_INVERSE_AND_LITERAL_EM_C_CURRENT_IMAGES',
        input_hashes=refs,archives=archives,case=case,outer_family=family,cells_per_segment=refinement,
        full_field_count=336,temporal_nodes=graph['temporal_nodes'],original_action_rows=len(action['original_Hessian']),
        original_Gauss_rows=len(action['Gauss_rows']),named_frame_rows=len(action['frame_rows']),
        original_row_residual=inv['original_action_row_residual_max'],Gauss_row_residual=inv['original_Gauss_row_residual_max'],
        frame_residual=inv['frame_residual_max'],wall_inverse_norm=float(np.linalg.norm(inv['wall_source_Green'])),
        restored_wall_inverse_minus_injected_sewn_norm=float(np.linalg.norm(inv['wall_source_Green']-compare)),
        wall_u_norm=float(np.linalg.norm(response['wall_u'])),wall_p_norm=float(np.linalg.norm(response['wall_p'])),
        C_covectors='unsubtracted action affine-band LOCAL-symbol tests; no scalar counterterm or physical LSZ promotion',
        common_coordinates='material At_L, Ar_L, Ai_L and realified H; proper At_E=-i At_L/N applied pointwise once',
        initial_trace_node=0,final_natural_trace_node=3,initial_zero_face_is_physical_E0=False,
        lateral_and_Gauss_contacts_retained=True,scalar_driving_current_removed=True,induced_H_response_retained=True,
        new_domain_rectangular_fermion_bridge_applied=False,old_FE2_heat_mean_or_source_covariance_grafted=False,
        physical_relative_heat_contour_or_Pauli_identified=False,physical_a_mu=None,
        coefficient_extension='same saved five-node cubic original Lorentz M/B/K; complex coframe independently evaluated',
        error_scope='binary64 action inverse/clock quadrature and original interpolation diagnostics; no full source-bridge/heat/exterior/LSZ error bound')
    (out/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in record.items()if k not in('input_hashes','archives')},sort_keys=True),flush=True)
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--case',choices=list(CASES),required=True);p.add_argument('--family',type=int,choices=(1,2),required=True)
    p.add_argument('--refinement',type=int,choices=(2,4),required=True)
    a=p.parse_args();materialize(a.output,case=a.case,family=a.family,refinement=a.refinement)
