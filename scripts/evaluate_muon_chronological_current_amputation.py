"""Execute full-body endpoint/amputation contacts on the corrected graph.

This evaluates an explicit piecewise-constant unsquared current germ
obtained from every original holomorphic quadrature edge.  It retains
the discarded within-edge variation as a measured coefficient operand,
not an error enclosure or a physical stationary exterior assumption.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_chronological_current_amputation import (
    nonstationary_endpoint_amputation,exterior_current_pole_matrix)
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def materialize(action_folder,body_folder,output,*,energy):
    action=ROOT/action_folder;base=ROOT/body_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every boundary/amputation application')
    refs={}
    def read(p,expected=None):
        h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same corrected current body changed')
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    am=read(action/'result.json');md=read(base/'result.json');refs.update(am['input_hashes']);refs.update(md['input_hashes'])
    if md['classification']!='EVALUATED_CORRECTED_WHOLE_CHRONOLOGICAL_FULL18_CURRENT_BODY_AND_COORDINATE_FIRST_GERM':
        raise ValueError('actual converged chronological full18 current coefficients required')
    inc=read(action/'original_n1_angular_and_source_incidence.npz',am['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    pieces=[read(p,md['archives'][p.name]['sha256'])for p in
        sorted(base.glob('corrected_full18_body_points_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))]
    q={k:np.concatenate([a[k]for a in pieces])for k in pieces[0]};del pieces
    if not np.array_equal(q['original_quadrature_index'],np.arange(3832)):
        raise ValueError('every source cell and corner current germ required')
    edge=q['original_rows'][:,0,0].real.astype(int)
    if not np.array_equal(q['original_rows'][:,1,0].real,edge+1):raise ValueError('exact original neighbor incidence required')
    alpha=lepton_current_hilbert_representation()['alpha'];Eang=inc['angular_derivatives']
    angular=-1j*sum(np.kron(a,e)for a,e in zip(alpha,Eang))
    full=np.array([np.kron(H,np.eye(2))+angular/R for H,R in zip(q['Hcan'],q['R'])])
    weight=q['original_measure'];h=np.zeros(1150,complex)
    H0=np.zeros((1150,18,18),complex);H1=np.zeros((1150,36,36),complex)
    for j in range(1150):
        at=np.flatnonzero(edge==j);h[j]=sum(weight[at])
        if not len(at) or h[j]==0:raise ValueError('no original edge can be omitted or collapsed')
        H0[j]=np.einsum('q,qab->ab',weight[at],q['Hcan'][at])/h[j]
        H1[j]=np.einsum('q,qab->ab',weight[at],full[at])/h[j]
    body0var=max(float(np.max(abs(q['Hcan'][edge==j]-H0[j])))for j in range(1150))
    body1var=max(float(np.max(abs(full[edge==j]-H1[j])))for j in range(1150))
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),
        'src/bhsm/interface/muon_chronological_current_amputation.py','tests/test_muon_chronological_current_amputation.py',
        'scripts/evaluate_muon_reached_trace_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);archives={};records=[]
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split complete current coefficients without deleting rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for start in range(0,1150,64):
        stop=min(start+64,1150);sl=slice(start,stop)
        save(f'original_full_body_edge_germs_{start}.npz',dict(edge_start=np.array(start),edge_stop_exclusive=np.array(stop),
            proper_steps=h[sl],full18_n0_body=H0[sl],full36_n1_spectator_body=H1[sl],
            edge_incidence=inc['edge_incidence'][sl]))
    for n,body in((0,H0),(1,H1)):
        print(json.dumps(dict(stage='original_fullbody_nonstationary_amputation',degree=n,dimension=body.shape[-1],edges=len(body))),flush=True)
        a=nonstationary_endpoint_amputation(h,body,energy=energy)
        d=body.shape[-1];finite=exterior_current_pole_matrix(a['energy_shifted_core_trace'],
            a['energy_shifted_core_trace_first'],np.eye(d),np.zeros((d,d)))
        arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
        arrays.update({k:v for k,v in finite.items()if isinstance(v,np.ndarray)})
        save(f'fullbody_degree_{n}_amputation.npz',arrays)
        records.append(dict(degree=n,dimension=d,all3_families_charged_neutral_negative_fibers_retained=True,
            exact_n1_spectator_count=2 if n==1 else 1,
            proper_clock_span_real=float(sum(h).real),proper_clock_span_imag=float(sum(h).imag),
            source_response_norm=float(np.linalg.norm(a['continued_source_response'])),
            source_energy_first_norm=float(np.linalg.norm(a['continued_source_energy_first'])),
            canonical_core_trace_norm=float(np.linalg.norm(a['canonical_core_trace'])),
            final_endpoint_return_norm=float(np.linalg.norm(a['final_endpoint_return'])),
            nonstationary_left_contact_norm=float(np.linalg.norm(a['nonstationary_left_amputation_contact'])),
            nonstationary_right_contact_norm=float(np.linalg.norm(a['nonstationary_right_amputation_contact'])),
            left_original_amputation_residual_max=float(np.max(abs(a['left_amputation_original_rows']))),
            right_original_amputation_residual_max=float(np.max(abs(a['right_amputation_original_rows']))),
            finite_initial_zero_boundary_pole_matrix_difference_max=float(np.max(abs(finite['exterior_pole_matrix']-np.eye(d)))),
            finite_initial_zero_boundary_energy_derivative_max=float(np.max(abs(finite['exterior_pole_matrix_energy_first'])))))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h0 for p,h0 in refs.items()):raise RuntimeError('same current amputation pins changed')
    result=dict(classification='EVALUATED_CORRECTED_FULL_BODY_NONSTATIONARY_CURRENT_ENDPOINT_AND_EXTERIOR_POLE_EQUATION',
        input_hashes=refs,archives=archives,records=records,source_energy_anchor=energy,original_temporal_nodes=1151,
        original_source_cells=384,original_corner_returns=383,
        projection='edge H=int_original_measure H/int_original_measure; exact exponential integration of that explicit germ only',
        within_original_edge_full18_body_variation_max=body0var,within_original_edge_full36_body_variation_max=body1var,
        within_edge_variation_assigned_zero_or_bounded=False,
        endpoint_amputation_relation='(E-Hf)R=I-exp(E*L)U+C_nonstationary_left; literal right counterpart retained',
        exterior_pole_relation='det(Bin(E)+Bout(E)*exp(E*L)U)=0 on the SAME complete action trace/frame',
        exterior_residue_relation='ell^T derivative_E[Bin+Bout*exp(E*L)U]r on actual exterior-compatible null traces',
        retained_initial_zero_free_final_boundary_has_pole_matrix_I=True,
        retained_finite_current_inverse_has_physical_mass_poles=False,
        same_converged_classical_body_not_old_FE2_or_positive_reference=True,
        physical_exterior_Bin_Bout_or_LSZ_evaluated=False,source_FE2_extension_to_physical_exterior_evaluated=False,
        physical_mass_lifetime_matching_solved=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 exact matrix-exponential identities on the explicit full-body edge germ. Within-edge coefficient variation is measured but not bounded in the current, and original operator formation/native graded/domain/exterior/physical matching are not enclosed.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),records=records)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action-folder',type=Path,required=True)
    p.add_argument('--body-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--energy',type=float,default=0.)
    a=p.parse_args();materialize(a.action_folder,a.body_folder,a.output,energy=a.energy)
