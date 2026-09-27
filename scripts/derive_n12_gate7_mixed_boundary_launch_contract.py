"""Derive the narrow mixed-reaction contract from frozen current first jets.

No prefix, historical action, heat spectrum or generic second jet is run.
Uninstantiated physical inputs remain null rather than becoming test seeds.
"""
import argparse
import ast
import json
from pathlib import Path
import sys
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from derive_n12_gate7_current_spectral_coefficients import interval
from bhsm.interface.heat_zeta_mixed_boundary_launch import OBJECT

BASE=ROOT/'artifacts/flagship_integration'


def calculate(out):
    ctx.prec=512
    frozen=[]
    for name,sub in [('gate7_current_spectral_20260927',''),('gate7_current_history_20260927','core'),
                     ('gate7_launch_response_20260927','')]:
        folder=BASE/name/sub;report=json.loads((folder/'report.json').read_bytes())
        if digest(folder/'arrays.npz')!=report['arrays_SHA256']:
            raise ValueError('frozen input differs: '+str(folder))
        frozen.extend([folder/'arrays.npz',folder/'report.json'])
    a=load(BASE/'gate7_current_spectral_20260927/arrays.npz')
    V=a['inverse_radius_squared_value'][0,0];W=a['inverse_radius_value'][0,0]
    dx=arb_mat(a['log_R4_first_73'].tolist())
    # Coefficient-coordinate partials only: x is log R4. These are not seven
    # material boundary directions and are never promoted to their place.
    arrays={'unit_scalar_V_xx':arb_mat([[4*V]]),'unit_scalar_V_xbp_coefficient':arb_mat([[-2*V]]),
            'unit_scalar_partial_x_launch':dx*(4*V),
            'unit_Weyl_W_xx':arb_mat([[W]]),'unit_Weyl_W_xbp_coefficient':arb_mat([[-W]]),
            'unit_Weyl_partial_x_launch':dx*W,
            'independent_reset_frame_source_7x73':arb_mat(7,73),
            'independent_fermion_delta_contact_7x73':arb_mat(7,73)}
    owners={
        'aether_ae2_one_seam_descriptor.py':['_element','assemble_ae2_one_seam_descriptor'],
        'aether_forward_common_source_incidence.py':['forward_weyl_log_radius_jets','forward_hs_scalar_log_radius_jets','forward_oneform_ghost_log_radius_jets'],
        'forward_finite_endpoint_heat_force.py':['heat_regulator_value_and_force','piecewise_linear_zeta_coefficient_cotangent'],
        'ae2_covariant_seam_response.py':['covariant_effective_event_load_jet','transition_covariant_derivative'],
        'joint_boundary_port_reduction.py':['reduce_seven_port','moving_port_jet'],
        'heat_zeta_mixed_boundary_launch.py':['heat_pair_7x73','element_mixed','zeta_element_mixed','reduce_mixed_reactions','reduce_implicit_mixed']}
    provenance={};sources=frozen+[Path(__file__)]
    for file,names in owners.items():
        path=ROOT/'src/bhsm/interface'/file;sources.append(path)
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        provenance[file]={node.name:dict(first_line=node.lineno,last_line=node.end_lineno)
                         for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names}
    for rel in ['artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json',
                'artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json',
                'artifacts/flagship_integration/BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json',
                'artifacts/flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json']:
        sources.append(ROOT/rel)
    out.mkdir(parents=True,exist_ok=False);save_arrays(out/'arrays.npz',arrays)
    report=dict(object=OBJECT,status='MIXED_TERM_NOT_ELIMINATED_NARROW_CONTRACTION_RECIPE_DERIVED',
        physical_7x73_materialized=False,
        pair_formula='Re Tr(DQ(P)[P_j] P_ba), Q=exp(-ell^2 P)/(2P)',
        genuine_mixed_formula='Re Tr(Q(P) P_ba,j); stream only 7x73 scalars',
        stationary_schur='Gamma_bp - lambda^T F_p, F_n^T lambda=Gamma_bn^T; requires F=Gamma_n or owned bordered stationary equivalent',
        history_sector_general_adjoint='eta=F_n^-T Gamma_history,n^T; L=Gamma_history-eta^T F; Phi_b=-F_n^-1 F_b; F_n^T lambda=(L_bn+Phi_b^T L_nn)^T; H_red=L_bp+Phi_b^T L_np-lambda^T F_p',
        elimination_result='Adjoints remove explicit Phi_bp, not genuine P_bp or the contracted F_bp terms in L.',
        existing_incidence_scope='Mixed log-radius vertices at supplied fixed temporal graph/profile; not the complete moving-duration, material-seed or implicit-history mixed jet.',
        nonaffine_current_coefficients=dict(unit_scalar_V_xx=interval(4*V),unit_Weyl_W_xx=interval(W)),
        coefficient_partial_is_not_boundary_seed=True,
        moving_seed=dict(ordinary_derivative='D(DGamma[B_a])[P_j]=H_red[P_j,B_a]+DGamma[D_Pj B_a]',
                         requested_minus='H_red[P_j,B_a]-DGamma[D_Pj B_a]',
                         connection_corrected='D(DGamma[B_a])[P_j]-DGamma[D_Pj B_a]=H_red[P_j,B_a]',
                         current_material_connection_bound=False),
        contacts=[
            dict(owner='independent reset frame source',classification='ZERO',reason='nabla U_R=0; transport remains ALREADY_INCLUDED in covariant child jets'),
            dict(owner='independent fermion delta-supported W_phys',classification='ZERO',reason='AE2 S_Sigma_F=0'),
            dict(owner='transverse gauge Wentzell',classification='ACTIVE',reason='W=K_F*c_group*sqrt(Delta1); mixed radius/moving-form jets retained'),
            dict(owner='scalar/topographic local response',classification='ACTIVE',reason='Nonaffine radius potential and owned scalar-source incidence retained; no independent scalar delta term inferred'),
            dict(owner='pair/contact vertices',classification='ALREADY_INCLUDED',reason='Pair DQ[P_j]P_b and mixed/contact Q P_bj are assembled once, not added again as independent forces'),
            dict(owner='descriptor/constraint/history normal response',classification='INTERNAL_REACTION',reason='Compose through common F and objective adjoint; not zeroed')],
        required_numerical_inputs=['Current joint operator and owned common spectral/form frame',
            'Seven material boundary seeds, their operator first variations and material derivatives',
            'Formation/reset/contact first pullbacks at the same current center',
            'Contracted mixed coefficient/duration/seed incidences x_bj and h_bj, or equivalent adjoint contractions',
            'Full internal F_n,F_b,F_p and contracted Lagrange-adjoint mixed blocks for the history-only objective'],
        R_history_7x73=None,R_reset_total_7x73=None,R_complete_7x73=None,
        row_norms=None,cancellation_factor=None,complete_rank=None,
        prefix_rebuilt=False,historical_actions_run=False,generic_second_operator_jet_computed=False,
        arbitrary_seeds_used_for_physical_data=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_lines=provenance,source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(report['status']);print('Full physical 7x73 materialized:',report['physical_7x73_materialized'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);calculate(p.parse_args().out)
