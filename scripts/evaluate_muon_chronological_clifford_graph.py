"""Execute the whole retained chronological Clifford spectral pencil."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_continued_action_reality import actual_source_curve_coefficients,action_reality_coefficient
from bhsm.interface.muon_euclidean_cell_sewing import source_cell_endpoint
from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_open_action_vertices
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_chronological_clifford_graph import (
    chronological_clifford_blocks,chronological_pencil_blocks,chronological_clifford_field_trace)
from bhsm.interface.muon_chronological_spectral_blocks import (
    homogeneous_scalar_degree_reduction,chronological_spectral_factor,
    chronological_selected_inverse,chronological_source_solve,chronological_source_residual)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def actual_chronological_quadrature(phases,curves,nodes,*,connector_refinement=1,progress=None):
    """All source cells and two complex legs through every owned real corner.

    A common trace is imposed at the actual real corner only. The two
    displaced complex endpoints remain distinct nodes with their own
    interval action. Initial-only deletion is performed by the assembler.
    """
    n=int(connector_refinement)
    if n<1:raise ValueError('positive actual connector subdivision required')
    ordered=[(side,int(cell))for side in('incoming','outgoing')
        for cell in sorted(set(nodes[side]['source_cell'].tolist()))]
    endpoints={(side,cell,end):source_cell_endpoint(phases[side],curves[side],cell,end)
        for side,cell in ordered for end in('left','right')}
    q=[];provenance=[];edges=[];corners=[];node=0
    def add(side,anchor,z,measure,w,ws,rows,kind,cell,slope):
        a=action_reality_coefficient(phases[side],float(anchor),complex(z))
        b=action_reality_coefficient(phases[side],float(anchor),complex(z).conjugate())
        q.append(dict(H18=a['Hcan'],Hsharp18=b['Hcan'],R=a['geometry']['R4'],Rsharp=b['geometry']['R4'],
            N=a['geometry']['N'],Nsharp=b['geometry']['N'],rows=rows,measure=complex(measure),
            right_clock=complex(w),reflected_clock=complex(ws),raw_fields=a['raw'],raw_fields_sharp=b['raw']))
        provenance.append((anchor,z,measure,w,ws,0 if side=='incoming'else 1,kind,cell,slope))
    gx,gw=np.polynomial.legendre.leggauss(4)
    for pos,(side,cell)in enumerate(ordered):
        idx=np.flatnonzero(nodes[side]['source_cell']==cell)
        length=float(np.sum(nodes[side]['weight'][idx]))
        center=float(nodes[side]['proper_center'][idx[0]]) if 'proper_center'in nodes[side] else float(
            np.sum(nodes[side]['weight'][idx]*nodes[side]['proper_time'][idx])/length)
        left=center-length/2
        for iq in idx:
            u=(nodes[side]['proper_time'][iq]-left)/length
            add(side,nodes[side]['coordinate_anchor'][iq],nodes[side]['coordinate_offset'][iq],
                nodes[side]['weight'][iq],1,1,((node,1-u,-1/length),(node+1,u,1/length)),0,cell,0j)
        edges.append((node,node+1,0,0 if side=='incoming'else 1,cell));node+=1
        if pos<len(ordered)-1:
            rs,rc=ordered[pos+1];a=endpoints[side,cell,'right'];b=endpoints[rs,rc,'left']
            if abs(a['owned_real_boundary']-b['owned_real_boundary'])>1e-20:
                raise ValueError('the chronological source cells do not share their owned real corner')
            boundary=a['owned_real_boundary'];start_node=node
            for leg,(ss,cc,start,stop,anchor)in enumerate((
                (side,cell,a['coordinate_endpoint'],boundary,a['coordinate_anchor']),
                (rs,rc,boundary,b['coordinate_endpoint'],b['coordinate_anchor']))):
                slope=complex(stop)-complex(start)
                if slope==0:raise ValueError('zero corner leg needs an exact domain reduction rather than duplicate traces')
                for j in range(n):
                    for x,g in zip(gx,gw):
                        v=(x+1)/2;t=complex(start)+(j+v)*slope/n;z=t-anchor
                        ar=action_reality_coefficient(phases[ss],anchor,z)
                        ash=action_reality_coefficient(phases[ss],anchor,z.conjugate())
                        w=1j*ar['geometry']['N']*slope;ws=-1j*ash['geometry']['N']*slope.conjugate()
                        add(ss,anchor,z,g*w/(2*n),w,ws,((node,1-v,-n),(node+1,v,n)),leg+1,cc,slope)
                    edges.append((node,node+1,leg+1,0 if ss=='incoming'else 1,cc));node+=1
                if leg==0:real_node=node
            corners.append((start_node,real_node,node,boundary,b['coordinate_endpoint']-a['coordinate_endpoint']))
        if progress is not None and(pos%32==31 or pos==len(ordered)-1):
            progress(dict(stage='actual_chronological_germs',source_cells=pos+1,total_source_cells=len(ordered),
                trace_nodes=node+1,quadrature_nodes=len(q)))
    return dict(quadrature=q,temporal_nodes=node+1,source_cells=len(ordered),corners=len(corners),
        quadrature_provenance=np.array(provenance,complex),edge_incidence=np.array(edges,int),
        corner_incidence=np.array(corners,complex),initial_right_trace_node=0,final_natural_trace_node=node,
        chronological_birth_real_trace_node=int(next(c[1]for c in corners if c[3]==0.)),
        connector_refinement=n)


def family_quadrature(common,family,*,vertices=False):
    fi=FAMILY_INDICES[family]
    for q in common:
        r=dict(q,H=q['H18'][np.ix_(fi,fi)],Hsharp=q['Hsharp18'][np.ix_(fi,fi)])
        if vertices:
            r['vertices']=euclidean_open_action_vertices(q['R'],q['N'],family=family)['vertices']
            r['vertices_sharp']=euclidean_open_action_vertices(q['Rsharp'],q['Nsharp'],family=family)['vertices']
        yield r


def materialize(output,*,connector_refinement,maximum_degree,families):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous chronological applications')
    refs={};archives={};records=[]
    def read(p):
        refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    ep=ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2';er=read(ep/'result.json');cutoff=er['cutoff']
    phases,curves,nodes={},{},{}
    for side in('incoming','outgoing'):
        phases[side],_=retained_input(side,refs)
        curves[side]=actual_source_curve_coefficients(*(read(ROOT/f'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/{side}_{name}.npz')for name in('phase','velocity','contacts')))
        nodes[side]=read(ep/(side+'_nodes.npz'))
    def progress(r):print(json.dumps(r,sort_keys=True),flush=True)
    graph=actual_chronological_quadrature(phases,curves,nodes,connector_refinement=connector_refinement,progress=progress)
    # Source files are pinned before spectral factorization and never changed
    # by materialization or by a failed branch diagnostic.
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            p=Path(path)
            try:rel=p.relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_chronological_clifford_graph.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,a)
        if p.stat().st_size>=10*1024**2:raise RuntimeError('split actual complete coefficient arrays before publication')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('chronological_graph_incidence.npz',{k:v for k,v in graph.items()if isinstance(v,np.ndarray)})
    for first in range(0,len(graph['quadrature']),192):
        row=graph['quadrature'][first:first+192]
        save(f'coefficient_nodes_{first}.npz',{k:np.array([r[k]for r in row])for k in(
            'H18','Hsharp18','R','Rsharp','N','Nsharp','rows','measure','right_clock','reflected_clock','raw_fields','raw_fields_sharp')})
    hilbert=lepton_current_hilbert_representation()
    spectral_points=(0j,1j/cutoff,-1j/cutoff)
    sumg={j:np.zeros((graph['temporal_nodes']-1,24),complex)for j in range(3)}
    for family in families:
        fi=FAMILY_INDICES[family];alpha=hilbert['alpha'][:,fi][:,:,fi]
        degree_grad={j:np.zeros_like(sumg[j])for j in range(3)}
        for degree in range(maximum_degree+1):
            reduction=homogeneous_scalar_degree_reduction(degree);E=reduction['angular_derivatives']
            b=chronological_clifford_blocks(family_quadrature(graph['quadrature'],family),
                temporal_nodes=graph['temporal_nodes'],angular_derivatives=E,alpha=alpha)
            for start in range(0,len(b['K_diagonal']),128):
                save(f'family_{family}_degree_{degree}_pencil_blocks_{start}.npz',
                    {k:v[start:start+128]for k,v in b.items()if isinstance(v,np.ndarray)})
            for iz,z in enumerate(spectral_points):
                D,U,L=chronological_pencil_blocks(b,z);f=chronological_spectral_factor(D,U,L)
                selected=chronological_selected_inverse(f)
                g=chronological_clifford_field_trace(family_quadrature(graph['quadrature'],family,vertices=True),
                    selected,temporal_nodes=graph['temporal_nodes'],angular_derivatives=E,alpha=alpha,
                    trace_multiplicity=reduction['trace_multiplicity'])
                degree_grad[iz]+=.5*g
                # Actual all-row source applications, not only a logdet.
                rhs=[np.zeros((b['block_width'],6),complex)for _ in D]
                birth=graph['chronological_birth_real_trace_node']-1
                rhs[birth][:6]=np.eye(6)
                u=chronological_source_solve(f,rhs);r=chronological_source_residual(f,u,rhs)
                umax=max(float(np.max(abs(x)))for x in u)
                absolute=max(float(np.max(abs(x)))for x in r)
                relative=max(float(np.max(abs(x)))/(float(np.max(abs(D[j])))+1e-300)/max(umax,1e-300)for j,x in enumerate(r))
                rec=dict(loop_family=family,degree=degree,spectator_trace_multiplicity=reduction['trace_multiplicity'],
                    spectral_point=[z.real,z.imag],temporal_blocks=len(D),block_width=b['block_width'],
                    log_absolute_determinant=f['log_absolute_determinant'],determinant_phase=[f['determinant_phase'].real,f['determinant_phase'].imag],
                    field_trace_norm=float(np.linalg.norm(g)),birth_source_response_max=umax,
                    source_original_row_absolute_residual=absolute,source_original_row_scaled_residual=relative)
                records.append(rec);progress(rec)
                save(f'family_{family}_degree_{degree}_spectral_{iz}_field_trace.npz',dict(field_trace=g))
                for start in range(0,len(D),128):
                    save(f'family_{family}_degree_{degree}_spectral_{iz}_selected_blocks_{start}.npz',dict(
                        selected_diagonal=np.asarray(selected['diagonal'][start:start+128]),
                        selected_upper=np.asarray(selected['upper'][start:start+128]),
                        selected_lower=np.asarray(selected['lower'][start:start+128]),
                        birth_source_response=np.asarray(u[start:start+128]),
                        birth_source_original_residual=np.asarray(r[start:start+128]),row_start=np.array(start)))
        for iz,g in degree_grad.items():
            sumg[iz]+=g;save(f'family_{family}_spectral_{iz}_starting_degree_trace.npz',dict(field_trace_statistics_half=g))
    save('all_executed_closed_lepton_spectral_field_trace.npz',{f'spectral_{i}':g for i,g in sumg.items()})
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source changed during chronological application')
    record=dict(classification='EVALUATED_WHOLE_CHRONOLOGICAL_REFLECTED_CLIFFORD_PENCIL_AND_SOURCE_DIRECTED_SPECTRAL_RETURNS',
        input_hashes=refs,archives=archives,source_cells=graph['source_cells'],restored_two_leg_corners=graph['corners'],
        temporal_nodes=graph['temporal_nodes'],quadrature_nodes=len(graph['quadrature']),
        initial_right_trace_node=0,final_natural_trace_node=graph['final_natural_trace_node'],
        birth_real_trace_node=graph['chronological_birth_real_trace_node'],connector_refinement=connector_refinement,
        executed_closed_lepton_families=list(families),maximum_starting_degree=maximum_degree,
        cutoff_probe=cutoff,records=records,scalar_driving_current_removed_does_not_remove_induced_H=True,
        holomorphic_measure_and_independent_reflected_coframe_retained=True,
        pure_field_mass_first_variation_zero_at_fixed_geometry=True,
        geometry_clock_corner_or_total_cutoff_variations_included=False,
        spectral_points_are_not_a_heat_contour_integral=True,window_underflow_zero_not_used=True,
        angular_starting_complement_or_relative_exterior_or_overlap_included=False,
        numerical_outer_face_is_physical_E0=False,physical_relative_domain_or_Pauli_identified=False,
        physical_a_mu=None,error_scope='binary64 original-row and selected-inverse diagnostics; no physical Pauli enclosure')
    (out/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--connector-refinement',type=int,default=1);p.add_argument('--maximum-degree',type=int,default=3)
    p.add_argument('--families',type=int,nargs='+',choices=(0,1,2),default=[0,1,2])
    a=p.parse_args();materialize(a.output,connector_refinement=a.connector_refinement,
        maximum_degree=a.maximum_degree,families=a.families)
