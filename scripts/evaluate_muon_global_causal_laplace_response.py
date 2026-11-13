"""Consume the already solved global impulse in its original complex-clock Laplace action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_global_causal_laplace_response import (
    global_causal_laplace_response,global_laplace_weak_boundary_identity)
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve all global causal action applications')
    folders={k:ROOT/p for k,p in dict(
        trajectory='artifacts/muon_initial_canonical_radial_return_20261011/run_1',
        clock='artifacts/muon_transported_native_pairing_20261011/run_1',
        frequencies='artifacts/muon_causal_radial_matching_20261011/run_1').items()}
    pins={};receipts={};archives={}
    def read(folder,name):
        p=folder/name;h=sha256(p.read_bytes()).hexdigest()
        if name!='result.json'and h!=receipts[folder]['archives'][name]['sha256']:
            raise ValueError('consumed same action/source changed: '+str(p))
        pins[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    for folder in folders.values():
        receipts[folder]=read(folder,'result.json');pins.update(receipts[folder]['input_hashes'])
    tf=folders['trajectory'];cf=folders['clock'];ff=folders['frequencies']
    names=sorted((k for k in receipts[tf]['archives']if k.startswith('original_canonical_response_nodes_')),
        key=lambda k:int(Path(k).stem.rsplit('_',1)[1]))
    chunks=[read(tf,k)for k in names]
    x=np.r_[np.zeros((1,176,8),complex),np.concatenate([a['initial_canonical_response']for a in chunks])]
    action_rows=np.concatenate([a['original_action_rows']for a in chunks])
    endpoints=read(tf,'initial_and_final_canonical_boundary.npz')
    source=read(tf,'actual_birth_final_and_source_pairings.npz')
    qs=[read(cf,k)for k in sorted((k for k in receipts[cf]['archives']if k.startswith('native_coframe_nodes_')),
        key=lambda k:int(Path(k).stem.rsplit('_',1)[1]))]
    rows=np.concatenate([q['rows']for q in qs]);w=np.concatenate([q['right_clock']for q in qs])
    m=np.concatenate([q['original_holomorphic_measure']for q in qs])
    rates=[];labels=[]
    for side in('incoming','outgoing'):
        z=read(ff,f'{side}_causal_application.npz')
        for i in range(4):rates.append(z[f'data_causal_boundary_applications_{i}_laplace_rate'].item());labels.append(f'{side}_recorded_action_rate_{i}')
    rates=np.array(rates,complex);left=source['literal_left_birth_sources'];birth=575
    a=global_causal_laplace_response(rows,w,m,x,left,rates,birth_node=birth)
    b=np.zeros_like(action_rows);b[birth-1]=source['actual_right_birth_sources']
    initial=np.r_[endpoints['initial_complete_action_cotangent'],np.zeros((8,8),complex)]
    weak=global_laplace_weak_boundary_identity(action_rows,b,left,a['proper_clock_nodes'],rates,
        initial,endpoints['final_dynamic_force'],birth_node=birth)
    # The two reduced spectators share a numerical factor only.  They are
    # distinct summands of the angular domain.  Sum their diagonal4 blocks,
    # never the artificial cross-spectator entries of a multi-RHS batch.
    trace_spectators=lambda z:z[...,:4,:4]+z[...,4:,4:]
    projected={k:trace_spectators(v)for k,v in {**a,**weak}.items()
        if isinstance(v,np.ndarray)and v.shape[-2:]==(8,8)}
    for rel in(Path(__file__),'src/bhsm/interface/muon_global_causal_laplace_response.py',
        'tests/test_muon_global_causal_laplace_response.py','scripts/evaluate_muon_reached_trace_action.py'):
        p=Path(rel);p=p if p.is_absolute()else ROOT/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,arrays):
        p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>=10*1024**2:raise RuntimeError('split complete numerical action arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('complete_global_scalar_Laplace_action.npz',dict(recorded_rate_labels=np.array(labels),
        **{k:v for k,v in a.items()if isinstance(v,np.ndarray)and k!='radial_pairing_at_quadrature'},
        **weak,**{'same_angular_direct_sum_'+k:v for k,v in projected.items()},
        same_angular_direct_sum_inverse_action_Laplace_Green=-projected['global_future_Laplace_Green'],
        same_angular_direct_sum_natural_equal_time_Green=trace_spectators(source['natural_pairing']),
        same_angular_direct_sum_canonical_equal_time_Green=trace_spectators(source['canonical_pairing'])))
    for start in range(0,len(rows),128):
        sl=slice(start,start+128)
        save(f'actual_Laplace_field_pairing_points_{start}.npz',dict(rows=rows[sl],
            original_holomorphic_measure=m[sl],right_clock=w[sl],
            proper_clock_points=a['proper_clock_points'][sl],
            same_angular_direct_sum_radial_pairing_at_quadrature=projected['radial_pairing_at_quadrature'][sl],
            full_computational_batch_radial_pairing_at_quadrature=a['radial_pairing_at_quadrature'][sl]))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):
        raise RuntimeError('consumed global action/source/clock changed')
    future=a['future_source_domain_mask'];dt=a['relative_proper_clock_points'][future]
    records=[]
    for i,s in enumerate(rates):
        G=projected['global_future_Laplace_Green'][i]
        records.append(dict(label=labels[i],action_Laplace_rate=dict(real=float(s.real),imag=float(s.imag)),
            finite_driven_radial_trace_average=dict(real=float(np.trace(G).real/4),imag=float(np.trace(G).imag/4)),
            finite_inverse_action_radial_trace_average=dict(real=float(-np.trace(G).real/4),imag=float(-np.trace(G).imag/4)),
            future_radial_Green_norm=float(np.linalg.norm(G)),
            before_source_radial_Laplace_norm=float(np.linalg.norm(projected['before_source_Laplace_pairing'][i])),
            actual_final_canonical_source_norm=float(np.linalg.norm(projected['final_canonical_endpoint_contact'][i])),
            variable_action_source_endpoint_identity_max=float(np.max(abs(projected['global_weak_source_endpoint_identity'][i])))))
    result=dict(classification='EVALUATED_GLOBAL_ORIGINAL_CANONICAL_IMPULSE_LAPLACE_KERNEL_AND_ACTION_ENDPOINTS',
        input_hashes=pins,archives=archives,records=records,
        original_nodes=1151,birth_node=575,all_source_and_corner_edges_retained=1150,
        original_Gauss_and_frame_rows_retained=True,
        source_section='the SAME recorded canonical birth radial2r section; original complex dual coefficients held; two exact angular spectators summed independently',
        numerical_cross_spectator_batch_currents_identified_as_physical=False,
        source_frequency_units='exact earlier recorded action-frequency probes; no physical energy unit/pole fitted',
        proper_clock_span=dict(real=float(a['proper_clock_nodes'][-1].real),imag=float(a['proper_clock_nodes'][-1].imag)),
        after_birth_proper_clock_real_range=[float(min(dt.real)),float(max(dt.real))],
        after_birth_proper_clock_imag_range=[float(min(dt.imag)),float(max(dt.imag))],
        clock_quadrature_antiderivative_closure_max=float(np.max(abs(a['clock_quadrature_antiderivative_closure']))),
        inverse_action_Green_sign='minus positive-action-source driven response, as the same C(-is) owner',
        static_local_C_minus_is_replaces_time_varying_global_action=False,
        finite_endpoint_and_source_contacts_dropped=False,
        complex_clock_replaced_by_absolute_positive_measure=False,
        other_inverse_or_new_classical_background_solve_executed=False,
        high_frequency_connector_growth='negative Re(delta_tau) is retained; the earlier real-prefix log64 quadrature cannot be transferred without evaluating its growing/oscillatory global integrand',
        physical_retarded_Lorentz_contour_or_quantum_Feynman_covariance_selected=False,
        full_soft_integral_or_native_Pauli_enclosure_claimed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 original-source/canonical trajectory and retained complex-clock quadrature; polynomial clock lift and finite-element/quadrature/physical-domain errors are not enclosed')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='global_causal_Laplace_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        records=records,clock_closure=result['clock_quadrature_antiderivative_closure_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
