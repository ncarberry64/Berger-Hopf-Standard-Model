"""Execute transported corrected fields on the reflected coframe-L2 graph."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_transported_native_pairing import transported_native_quadrature,finite_native_form_lower_comparison
from bhsm.interface.muon_continued_coefficient_first_germ import geometry_first_germ
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_chronological_clifford_graph import (
    chronological_clifford_blocks,chronological_pencil_blocks,chronological_clifford_field_trace)
from bhsm.interface.muon_chronological_spectral_blocks import (
    homogeneous_scalar_degree_reduction,chronological_spectral_factor,
    chronological_selected_inverse,chronological_source_solve,chronological_source_residual)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def load_corrected_chronological_coefficients(folder,refs):
    folder=ROOT/folder;p=folder/'result.json';md=json.loads(p.read_bytes())
    refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    def read(name):
        p=folder/name;h=md['archives'][name]['sha256']
        if sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('corrected original graph changed')
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    incidence=read('chronological_graph_incidence.npz');allq=[]
    names=sorted((k for k in md['archives']if k.startswith('coefficient_nodes_')),key=lambda n:int(Path(n).stem.rsplit('_',1)[-1]))
    for name in names:
        a=read(name)
        for j in range(len(a['H18'])):
            q={k:v[j]for k,v in a.items()}
            q['rows']=tuple((int(row[0].real),complex(row[1]),complex(row[2]))for row in q['rows'])
            allq.append(q)
    if len(allq)!=md['quadrature_nodes']:raise ValueError('all original chronological coefficient rows required')
    return md,incidence,allq


def actual_clock_derivative(provenance):
    def apply(index,q):
        row=provenance[index];kind=int(row[6].real);slope=complex(row[8])
        if kind==0:return 0j,0j
        first=[]
        for key,sl in(('raw_fields',slope),('raw_fields_sharp',slope.conjugate())):
            raw=q[key];d=np.zeros_like(raw);d[:37]=sl*raw[37:74];d[98]=sl*raw[99]
            first.append(geometry_first_germ(raw,d)['first']['N'])
        return 1j*first[0]*slope,-1j*first[1]*slope.conjugate()
    return apply


def materialize(output,*,input_folder,maximum_degree=3,families=(0,1,2)):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve existing transported applications')
    refs={};md,incidence,q=load_corrected_chronological_coefficients(input_folder,refs)
    for name in('muon_transported_native_pairing','muon_continued_coefficient_first_germ',
        'muon_chronological_clifford_graph','muon_chronological_spectral_blocks'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);files={};records=[]
    def save(name,a):
        p=out/name;_compressed_npz(p,a)
        if p.stat().st_size>10*1024*1024:raise RuntimeError('publication archive cap exceeded')
        files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('original_graph_incidence.npz',incidence)
    derivatives=actual_clock_derivative(incidence['quadrature_provenance'])
    rep=lepton_current_hilbert_representation()
    for family in families:
        native=transported_native_quadrature(q,family=family,clock_derivatives=derivatives)
        nq=native['quadrature'];trans=native['pairing_transitions'];fi=FAMILY_INDICES[family]
        if family==families[0]:
            save('pairing_density_and_contact.npz',{k:np.array([t[k]for t in trans])for k in(
                'native_geometric_measure','original_holomorphic_measure','native_coframe_norm',
                'reflected_coframe_metric','reflection_rounding_defect','dual_density_ratio',
                'logarithmic_dual_density_derivative','analytic_left_density_connection')})
            for start in range(0,len(q),192):
                sub=q[start:start+192];ts=trans[start:start+192]
                coefficients={k:np.array([qi[k]for qi in sub])for k in(
                    'H18','Hsharp18','N','Nsharp','R','Rsharp','right_clock','reflected_clock',
                    'raw_fields','raw_fields_sharp','rows')}
                coefficients.update(measure=np.array([t['native_geometric_measure']for t in ts]),
                    original_holomorphic_measure=np.array([qi['measure']for qi in sub]),
                    dual_density_ratio=np.array([t['dual_density_ratio']for t in ts]),
                    analytic_left_density_connection=np.array([t['analytic_left_density_connection']for t in ts]))
                save(f'native_coframe_nodes_{start}.npz',coefficients)
        alpha=rep['alpha'][:,fi][:,:,fi]
        for degree in range(maximum_degree+1):
            angular=homogeneous_scalar_degree_reduction(degree);E=angular['angular_derivatives']
            blocks=chronological_clifford_blocks(nq,temporal_nodes=md['temporal_nodes'],angular_derivatives=E,alpha=alpha)
            lower=finite_native_form_lower_comparison(nq,temporal_nodes=md['temporal_nodes'],angular_derivatives=E,alpha=alpha)
            save(f'family_{family}_degree_{degree}_lower_comparison.npz',
                {k:v for k,v in lower.items()if isinstance(v,np.ndarray)})
            for start in range(0,len(blocks['K_diagonal']),128):
                save(f'family_{family}_degree_{degree}_native_blocks_{start}.npz',
                    {k:v[start:start+128]for k,v in blocks.items()if isinstance(v,np.ndarray)})
            D,U,L=chronological_pencil_blocks(blocks,0.)
            factor=chronological_spectral_factor(D,U,L);sel=chronological_selected_inverse(factor)
            trace=chronological_clifford_field_trace(nq,sel,temporal_nodes=md['temporal_nodes'],
                angular_derivatives=E,alpha=alpha,trace_multiplicity=angular['trace_multiplicity'])
            width=blocks['block_width'];rhs=np.zeros((md['temporal_nodes']-1,width,width),complex)
            rhs[md['birth_real_trace_node']-1]=np.eye(width)
            response=chronological_source_solve(factor,rhs);res=np.array(chronological_source_residual(factor,response,rhs))
            for start in range(0,len(response),128):
                save(f'family_{family}_degree_{degree}_birth_return_{start}.npz',dict(
                    birth_source_response=response[start:start+128],original_row_residual=res[start:start+128]))
            save(f'family_{family}_degree_{degree}_field_trace.npz',dict(field_resolvent_trace=trace))
            diagonal_defect=float(np.max(abs(blocks['K_diagonal']-blocks['K_diagonal'].conj().transpose(0,2,1))))
            directed_defect=float(np.max(abs(blocks['K_upper']-blocks['K_lower'].conj().transpose(0,2,1))))
            record=dict(loop_family=family,degree=degree,field_resolvent_trace_norm=float(np.linalg.norm(trace)),
                birth_source_residual_max=float(np.max(abs(res))),
                K_diagonal_Hermitian_defect=diagonal_defect,K_directed_adjoint_defect=directed_defect,
                total_native_geometric_measure=float(sum(t['native_geometric_measure']for t in trans)),
                original_total_holomorphic_measure=[float(sum(qi['measure']for qi in q).real),float(sum(qi['measure']for qi in q).imag)],
                maximum_left_density_connection=float(max(abs(t['analytic_left_density_connection'])for t in trans)),
                finite_form_lower_comparison={k:v for k,v in lower.items()if not isinstance(v,np.ndarray)})
            records.append(record);print(json.dumps(record,sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed coefficient or source changed')
    result=dict(classification='EVALUATED_CORRECTED_TRANSPORTED_NATIVE_FACTOR_ON_REFLECTED_COFRAME_L2_CORE',
        input_hashes=refs,archives=files,records=records,temporal_nodes=md['temporal_nodes'],
        birth_real_trace_node=md['birth_real_trace_node'],families=list(families),maximum_degree=maximum_degree,
        original_holomorphic_measure_retained_and_exported=True,
        native_pairing='right coframe w ds and reflected ws ds give positive Hermitian metric ws*w; geometric density sqrt(ws*w) ds times original reference quadrature',
        density_coordinate_equivalence_claimed=False,
        original_action_comparison='bar_old=bar_native/rho generates left density connection −(rho_prime/rho)/ws; omitting it does not recover the original analytic square',
        native_temporal_coordinate_map='a_tau=−i At_L; independently reflected a_tau_sharp=+i At_Lsharp; vertices and background rotated together',
        corner_condition='right value shared at each original node; native weak conormal (mu/ws) A u balanced at every interior row, final natural row retained',
        complete_physical_OS_contour_reset_exterior_or_relative_domain_proved=False,
        native_field_resolvent_trace_is_complete_heat_gradient=False,
        infinite_angular_starting_complement_included=False,physical_a_mu=None,
        error_scope='independently reflected finite coefficient graph, original row/clock/density applications; no physical exterior, overlap, complete heat or continuum/observable error enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--input-folder',type=Path,default=Path('artifacts/muon_chronological_clifford_graph_20261011/run_1'))
    p.add_argument('--maximum-degree',type=int,default=3);p.add_argument('--families',type=int,nargs='+',default=[0,1,2])
    a=p.parse_args();materialize(a.output,input_folder=a.input_folder,maximum_degree=a.maximum_degree,families=tuple(a.families))
