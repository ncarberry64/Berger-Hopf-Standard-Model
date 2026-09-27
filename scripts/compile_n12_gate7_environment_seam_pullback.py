"""Compile the frozen weak response's seam coupling; no new action evaluations."""
import argparse
import ast
import json
from pathlib import Path
from flint import arb_mat,ctx
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,bound
from diagnose_n12_gate7_eight_reaction_center import block,identity
import solve_n12_gate7_fiber_constrained_center as c

ROOT=c.ROOT
BASE=c.BASE/'gate7_comoving_interface_20260927'


def compile_packet(out):
    ctx.prec=512
    source=BASE/'feedback13/arrays.npz'
    prior=json.loads((BASE/'feedback13/report.json').read_bytes())
    if digest(source)!=prior['arrays_SHA256']:raise ValueError('frozen feedback changed')
    a=load(source)
    value=c.matrix(a['rate_acceleration_affine'])
    J=block(value,range(61),[1,2])
    gram=J.transpose()*J;inverse=gram.inv()
    invproposal=arb_mat(2,2,[x.mid() for x in inverse.entries()])
    defect=bound(identity(2)-invproposal*gram)
    if defect['approximate_upper']>=1:raise ArithmeticError('feedback rank unverified')
    att=block(c.matrix(a['attachment_acceleration_affine']),range(2),[1,2])
    save_arrays(out/'arrays.npz',dict(environment_reaction_to_child_acceleration=J,
        environment_reaction_to_attachment_acceleration=att,
        coupling_Gram=gram,coupling_Gram_inverse=inverse))
    specs={
        'src/bhsm/interface/full_field_moving_reset_graph_decision.py':['first_moving_domain_variation'],
        'src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py':['weighted_cotangent_momentum_map'],
        'src/bhsm/interface/event_normal_weyl_riccati.py':['weyl_riccati_rhs','weyl_geometry_jet_rhs'],
        'src/bhsm/interface/aether_forward_history_weyl_first_jet.py':[],
        'src/bhsm/interface/moving_seam_response.py':[]}
    sources={str(source):digest(source),str(BASE/'feedback13/report.json'):digest(BASE/'feedback13/report.json'),str(Path(__file__)):digest(Path(__file__))}
    provenance={}
    for name,functions in specs.items():
        p=ROOT/name;sources[str(p)]=digest(p);content=p.read_text(encoding='utf-8');lines=content.splitlines()
        provenance[name]={f.name:dict(start=f.lineno,end=f.end_lineno,text='\n'.join(lines[f.lineno-1:f.end_lineno])) for f in ast.parse(content).body if isinstance(f,ast.FunctionDef) and f.name in functions}
    documents=[ROOT/'theory/n12_gate7_outgoing_flow_tail_closure.md',
        ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json',
        Path('C:/Users/carbe/Downloads/BHSM_ENVIRONMENT_BOUNDARY_GRAPH_ENCLOSURE_v0.4.md')]
    for p in documents:sources[str(p)]=digest(p)
    report=dict(status='ENVIRONMENT_SEAM_COMPOSITION_DERIVED_REALIZATION_OPEN',
        delta_environment_state=0,independent_environment_inputs=0,
        equation='Dnu=nu_Y|rho*DY + nu_rho*Drho_env; Drho_env includes the moving-seam pullback at fixed e0',
        coupled_balance='Kp=Cp+O*Ep; Kq=Cq+O*Eq; Dq=-Kq^-1*Kp; T=Tp+Tq*Dq',
        first_missing_representation='An owner-bound native environment trace/reaction first jet together with the embedding, frame, normal and measure pullback jet induced by the 73 p/q state directions at interval 13.',
        response_required_shape=[7,73],intrinsic_columns=66,reaction_columns=7,
        reaction_q_columns_required=True,
        physical_environment_response_constructed=False,physical_tangent_comparison_completed=False,
        coupling_rank_certified=2,coupling_Gram_inverse_defect=defect,
        coupling_norm_raw_units=bound(J),
        reuse_decisions={
            'material_pullback':'Reuse D(P r)=DP r+P Dr, including density, normal and moved projector contributions in DP.',
            'canonical_momentum':'Differentiate the existing weighted inverse-adjoint transport; native value derivative is mandatory.',
            'dynamic_flux':'Requires the same-action native dynamic-flux shape jet, including momentum material-rate derivative; not determined by trace values alone.',
            'Riccati':'Valid along an owned arm-normal displacement given M and L; not a seven-row response or general shape derivative without an owner map.',
            'parent_provenance':'Stored spectral M_E0 value/jet is open. This does not by itself prove a local seven-row realization needs the whole spectral parent campaign.',
            'v04':'Defines W_E schematically; does not instantiate its Hessian, shape jet or seam embedding.',
            'fixed_rho_checkpoint':'Its missing nu_rho*Drho term is now available as a signed rank-two coupling. No zero Drho assumption is made.'},
        source_lines=provenance,source_SHA256=sources,arrays_SHA256=digest(out/'arrays.npz'),
        scientific_action_producers_run=False,Layer_C_rebound=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','coupling_rank_certified','coupling_Gram_inverse_defect')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);compile_packet(a.out)
