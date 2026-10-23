"""Join cached prefix, cut-to-first-node and future weak elements by trace."""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(root,prefix,future,clock,out):
    if out.exists():raise FileExistsError('fresh output required')
    out.mkdir(parents=True);sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_prefix_time_element import integrate_linear_density_element,consume_prefix_element
    cut_path=root/'artifacts/muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz'
    cut=read(cut_path);pre=read(prefix/'prefix_time_element.npz');fut=read(future/'retained_arc_time_element.npz')
    history=read(future/'retained_future_points.npz');cl=read(clock)
    if not (np.array_equal(cl['states'][1:3],history['states']) and
            np.array_equal(cl['proper_time_density'][1:3],history['proper_time_density'])):
        raise ValueError('connecting clock differs from evaluated future element')
    clock0=float(cl['proper_time_density'][0]);clock1=float(cl['proper_time_density'][1]);da=float(cl['action_lengths'][1]-cl['action_lengths'][0])
    save(out/'clock_input.json',dict(path=str(clock),sha256=sha(clock),node_indices=[0,1],
        proper_time_density=[clock0,clock1],action_width=da,proper_duration=float(cl['proper_durations'][0]),
        classification='retained numerical cancelled-arc clock; no new endpoint extraction',
        point0_clock_is_not_extended_constantly=True))
    dim=len(cut['source_coordinates'])*2;local=cut['local_cut_K_Wp_timejet']
    left=dict(A=local[:dim,:dim],B=local[:dim,dim:],C=local[dim:,dim:],
        M=cut['local_cut_M_Wp'],tau_x=da*clock0)
    # Values at the first future face recovered from the evaluated density
    # coefficients. No cut action/contraction or future action is repeated.
    node1={k:fut['Legendre_density_'+k][0]-fut['Legendre_density_'+k][1] for k in ('A','B','C','M')}
    old_jac=float(fut['clock_tau_x'][0])
    right=dict(A=node1['A']/old_jac,B=node1['B'],C=node1['C']*old_jac,
        M=node1['M']/old_jac,tau_x=da*clock1)
    scale=da*(clock0+clock1)/2
    K,M,polys=integrate_linear_density_element([left,right],scale)
    bridge,receipt=consume_prefix_element(K,M,cut,scale)
    receipt.update(kind='cut0-to-future1 cached-density connecting element',
        left_face='step1222 cut / retained future node0; internal matching face',
        right_face='retained future node1/action_arc2; internal matching face')
    bridge.update(temporal_basis_scale=np.array(scale),clock_tau_x=np.array([da*clock0,da*clock1]))
    for k,v in polys.items():bridge['Legendre_density_'+k]=v
    np.savez_compressed(out/'cut_to_future1_element.npz',**bridge)
    pieces=[pre,bridge,fut];size=2*dim;total=3*size
    KK=np.zeros((total,total),complex);MM=KK.copy();load=np.zeros(total,complex);cot=load.copy();source=load.copy()
    traces=[]
    for i,p in enumerate(pieces):
        rows=slice(i*size,(i+1)*size)
        KK[rows,rows]=p['element_K'];MM[rows,rows]=p['element_M']
        load[rows]=p['source_weak_rhs'];cot[rows]=p['source_form_cotangent']
        source[rows]=p['source_constant_coefficients'];traces.append(p['hierarchical_to_endpoint_coefficients'])
    # Total W/p trace continuity; no complement projection is discarded.
    # The matrices act in hierarchical coordinates, avoiding inverses of the
    # tiny prefix basis scale or cancellation of large nodal time blocks.
    J=np.zeros((2*dim,total),complex)
    J[:dim,:size]=traces[0][dim:];J[:dim,size:2*size]=-traces[1][:dim]
    J[dim:,size:2*size]=traces[1][dim:];J[dim:,2*size:]=-traces[2][:dim]
    trace_gram=np.zeros((2*dim,2*dim),complex)
    trace_gram[:dim,:dim]=cut['local_cut_Cauchy_Wp']
    trace_gram[dim:,dim:]=fut['left_trace_Cauchy_Gram']
    np.savez_compressed(out/'partial_coupled_temporal_KM.npz',K=KK,M=MM,trace_continuity=J,
        interface_Cauchy_Gram=trace_gram,source_coefficients=source,source_weak_rhs=load,
        source_form_cotangent=cot,left_total_source_trace=traces[0][:dim]@source[:size],
        right_total_source_trace=traces[2][dim:]@source[-size:])
    result=dict(assembled='three connected source-reached local Dirac temporal elements',
        coordinates='hierarchical W/p coefficients; moving projection and connected source output retained',
        proper_domain='physical prefix1222 through cut0 and future action_arc0..4; reset and canonical stop unchanged',
        element_shapes=[list(p['element_K'].shape) for p in pieces],coupled_K_shape=list(KK.shape),
        trace_constraint_shape=list(J.shape),original_source_trace_residual=float(np.linalg.norm(J@source)),
        source_load='assembled from each unprojected original source before time-jet application',
        bridge_source_history_energy=receipt['source_element_energy'],
        total_partial_source_energy=float(np.vdot(source,cot).real),
        bridge_proper_duration=scale,
        solution=None,stationary_residual=None,stationary_conormal=None,
        solver_not_invoked='this partial local Dirac form is not the full same-owner exterior operator',
        remaining_required_action=dict(block='continuation trace row at future node2, action_arc4',
            equation='q_tail,0^owner(v,u_s)+s<m_tail(v,u_s)> =0 with inherited material/reset/canonical-stop graph',
            consumer='coupled exterior weak source solve after assembly of all owned blocks',
            point_coefficients='later retained numerical point records available; tail weak/domain/interface/completion action not assembled here',
            physical_boundary_selection_missing=False),
        other_owner_terms=dict(wall_Higgs_interface=None,gauge_constraints_BRST=None,relative_completion=None),
        error_scope='exact integrals of declared density models, binary64 forms; bridge/future interpolation and continuum remainder unevaluated',
        physical_a_mu=None,physical_g_mu=None)
    save(out/'result.json',result);save(out/'bridge_assembly.json',receipt)
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in
        dict(prefix=prefix/'prefix_time_element.npz',future=future/'retained_arc_time_element.npz',
             history=future/'retained_future_points.npz',clock=clock,cut=cut_path,
             script=Path(__file__),module=root/'src/bhsm/interface/muon_prefix_time_element.py').items()})
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    for k in ('prefix','future','clock','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.prefix,a.future,a.clock,a.output)
