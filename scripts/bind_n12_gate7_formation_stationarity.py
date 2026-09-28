"""Bind current reset inputs to the coupled stationary-history equation set."""
import argparse
import ast
import json
from pathlib import Path
import sys
from flint import arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,bound
from differentiate_n12_gate7_fiber_constrained_center import save_arrays

BASE=ROOT/'artifacts/flagship_integration'
PACKET=BASE/'gate7_current_formation_stationarity_20260927'


def calculate(out):
    ctx.prec=512
    report=json.loads((PACKET/'run1/report.json').read_bytes())
    if digest(PACKET/'run1/arrays.npz')!=report['arrays_SHA256']:raise ValueError('current point data changed')
    for name in ('arrays.npz','report.json'):
        if (PACKET/'run1'/name).read_bytes()!=(PACKET/'run2'/name).read_bytes():raise ValueError('repeat mismatch')
    a=load(PACKET/'run1/arrays.npz');m=lambda name:arb_mat(a[name].tolist())
    parent=-m('E1_momentum');child=m('C2_momentum')
    static_flux=m('C2_conormal')+m('E1_conormal')-m('C2_force')
    arrays=dict(signed_parent_local_momentum=parent,signed_child_local_momentum=child,
        forward_local_momentum_balance=parent+child,
        local_flux_force_conormal_piece=static_flux,
        outgoing_regularized_arc_momentum_rate=m('C2_momentum_arc_derivative'))
    functions={
        'src/bhsm/interface/aether_full_reset_action_jacobian.py':('full_reset_residual','full_reset_action_jacobian'),
        'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py':('_canonical_pair_at_order','_child_rows_at_order'),
        'src/bhsm/interface/forward_finite_endpoint_heat_force.py':('heat_regulator_value_and_force','piecewise_linear_zeta_coefficient_cotangent'),
        'src/bhsm/interface/formation_stationarity_kkt.py':('assemble_stationarity','stationary_first_jet')}
    provenance={}
    for relative,names in functions.items():
        source=(ROOT/relative).read_text(encoding='utf-8');lines=source.splitlines()
        provenance[relative]={node.name:dict(first_line=node.lineno,last_line=node.end_lineno,
            text='\n'.join(lines[node.lineno-1:node.end_lineno])) for node in ast.parse(source).body
            if isinstance(node,ast.FunctionDef) and node.name in names}
    sources=[ROOT/name for name in functions]
    sources += [Path(__file__),PACKET/'run1/report.json',PACKET/'run1/arrays.npz',
        BASE/'gate7_current_spectral_20260927/report.json',BASE/'gate7_current_history_20260927/core/report.json',
        BASE/'BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json',
        BASE/'BHSM_N12_FORCE_ADJOINT_PULLBACK.json',
        ROOT/'scripts/bind_n12_gate7_geometric_material_port.py',
        ROOT/'scripts/audit_n12_finite_terminal_directed_center.py',
        ROOT/'scripts/solve_n12_gate7_fiber_constrained_center.py',
        ROOT/'scripts/recenter_n12_gate7_current_history_box.py',
        ROOT/'src/bhsm/interface/physical_hs_value.py']
    out=Path(out);out.mkdir(parents=True,exist_ok=False);save_arrays(out/'arrays.npz',arrays)
    result=dict(status='CURRENT_COUPLED_STATIONARITY_EQUATIONS_BOUND_ACTION_COVECTOR_UNINSTANTIATED',
        unknowns=dict(physical_parameters=73,terminal_incoming_state=98,
            incoming_independent_reset_rows=32,incoming_reset_compatible_directions=66,
            terminal_KKT_coordinates_if_history_internals_slaved=130,
            independent_environment_inputs=0,
            history_internals='Incoming coefficients, duration/amplitude, contact and operator internal variables must be solved or eliminated by their owned equations; their current numerical dimension/normal inverse is not supplied by a terminal reset Jacobian.',
            seam_reactions='Momentum/flux are action outputs or internal multipliers, not 73 new reactions'),
        equations=dict(reset='R(p,y)=0 (32 incoming-sensitive rows); outgoing 26 rows retained as compatibility checks',
            stationary='Gamma_red,y + R_y^T mu = 0',
            equivalent_tangent='Z^T Gamma_red,y = 0, columns of Z span ker R_y',
            first_jet='[[Gamma_yy+sum mu_a R_a,yy, R_y^T],[R_y,0]] [y_p;mu_p] = -[Gamma_yp+sum mu_a R_a,yp;R_p]',
            internal='F_history(p,y,n)=0; Gamma_red composes n and owned moving endpoints before differentiation',
            external='J_ext=0; retained internal action/contact responses remain active'),
        forward_orientation=dict(parent='E1 = stored second half, branch23',child='C2 = stored first half, branch24',
            momentum='P_C2-P_E1',flux='G_C2+DP_C2[X_C2]-F_C2+G_E1; history additions must use the same common reduction'),
        local_momentum_balance=bound(parent+child),local_force_conormal_piece=bound(static_flux),
        local_flux_piece_is_not_full_flux=True,
        terminal_flux_scope='No division by signed descriptor zero is made. The regularized arc momentum derivative is not the physical-time momentum derivative; complete material boundary limits must come from the solved formation/reset history.',
        complete_parent_reaction=None,complete_child_reaction=None,full_stationarity_residual=None,
        full_flux_residual=None,full_stationarity_jacobian_rank=None,
        null_directions=[dict(column=i,classification='UNRESOLVED_UPSTREAM_RESET_TANGENT',
            reason='Current history stationarity derivative not instantiated; gauge/time/physical-modulus status not inferred from reset rank') for i in range(66)],
        missing_object='CURRENT_CENTER_REDUCED_INCOMING_FORMATION_CONTACT_ACTION_COVECTOR_AND_NORMAL_LAUNCH_JETS',
        missing_object_definition='Gamma_red,y (or its 66 reset-tangent contractions), the Lagrangian normal Hessian, and the total 73-column mixed forcing, from the current incoming coefficient/duration path and retained signed heat-minus-zeta/contact adjoint',
        missing_physics_claim=False,new_environment_or_selector_introduced=False,
        stationary_history_solved=False,current_73_formation_jet_computed=False,
        same_action_normal_transversality_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_lines=provenance,source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in sources},arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(result))
    print(result['status']);print('Forward local momentum balance',result['local_momentum_balance']['approximate_upper'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();calculate(a.out)
