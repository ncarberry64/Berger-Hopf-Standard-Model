"""Bounded two-sided attachment audit using frozen operands and pure charts.

No action, Hessian, reset, endpoint, or shooting producer is executed.
"""
import argparse
import ast
import io
import json
from pathlib import Path

import numpy as np

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, FIXED, SCALE, digest, encoded

NULL = ROOT/BASE/'gate7_local_null_classification_20260926'
BIND = ROOT/BASE/'gate7_66d_checkpoint_20260926/binding'
RESET = ROOT/BASE/'BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz'
CHART = 'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'
PROVENANCE = {
    CHART: [(2751,2795),(3199,3218),(3273,3282)],
    'src/bhsm/interface/aether_full_reset_action_jacobian.py': [(248,278),(335,358),(396,410),(565,635)],
    'src/bhsm/interface/aether_n3_event_attachment_state_incidence_v17_89.py': [(38,65)],
    'src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py': [(28,48),(73,87),(108,145),(197,217)],
    'scripts/audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate.py': [(67,77)],
    'scripts/materialize_n12_gate7_augmented_fixed_descriptor_newton_endpoint_candidate.py': [(68,76),(180,195)],
    'scripts/certify_n12_candidate_positive_duration_persistence.py': [(81,84)],
    'src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py': [(217,225)],
    'artifacts/flagship_integration/gate7_8reaction_center_20260926/source/bhsm_gate7_stageB_direct_interface.py': [(91,136)],
    'theory/n12_event_normal_two_sided_seam_correction.md': [(1,51)],
    'theory/n12_gate7_ae2_one_seam_direct_descriptor.md': [(1,48)],
    'theory/n12_gate7_two_seam_closed_operator_assembly.md': [(1,73)],
    'theory/n12_ae2_child_boundary_hamiltonian_non_supersession.md': [(1,44)],
    'theory/bhsm_owner_authorized_encapsulation_interface_action.md': [(65,99),(263,328)],
    'theory/bhsm_covariant_interface_seam_selection_audit.md': [(34,54),(73,108),(207,221)],
}


def chart_helpers():
    """Load only the three pure owned chart functions; no module side effects."""
    tree = ast.parse((ROOT/CHART).read_text(encoding='utf-8'))
    wanted = {'_trace_jacobian_at_order','_attachment_jacobian_at_order','_attachment_coordinates_at_order'}
    nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    if len(nodes) != 3:
        raise ValueError('owned chart function set changed')
    namespace = {'np':np,'dimensions':lambda order: {'coordinates':1+3*order}}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),CHART,'exec'),namespace)
    return tuple(namespace[name] for name in ('_trace_jacobian_at_order','_attachment_jacobian_at_order','_attachment_coordinates_at_order'))


def calculate():
    sources = {}
    def verify(path, expected=None):
        sha = digest(path)
        if expected is not None and sha != expected:
            raise ValueError('frozen source changed: '+str(path))
        sources[path.relative_to(ROOT).as_posix()] = sha
    for directory in (NULL,BIND):
        report = json.loads((directory/'report.json').read_bytes())
        verify(directory/'report.json');verify(directory/'arrays.npz',report['arrays_SHA256'])
    binding = json.loads((BIND/'report.json').read_bytes())
    verify(ROOT/FIXED,binding['source_SHA256'][str(ROOT/FIXED)])
    reset_meta = json.loads(RESET.with_suffix('.json').read_bytes())
    verify(RESET,reset_meta['data']['SHA256']);verify(RESET.with_suffix('.json'))
    provenance = {}
    for name,ranges in PROVENANCE.items():
        verify(ROOT/name)
        lines = (ROOT/name).read_text(encoding='utf-8').splitlines()
        provenance[name] = [dict(start=a,end=b,text='\n'.join(lines[a-1:b])) for a,b in ranges]
    verify(Path(__file__))
    with np.load(NULL/'arrays.npz') as z:
        unit = z['unit_null'];directions = z['null_endpoints_action_physical']
    with np.load(ROOT/FIXED) as z:
        states = z['projected_states'][13:15];weights = z['state_weights']
        descriptors = z['independent_signed_descriptors'][13:15]
        norms = z['cancelled_field_action_norm'][13:15]
        norm_s = z['cancelled_norm_descriptor_derivative'][13:15]
        norm_y = z['cancelled_norm_state_gradient_action'][13:15]
    with np.load(BIND/'arrays.npz') as z:
        child = z['node_014_child_state']
    with np.load(RESET) as z:
        J = z['analytic_full_reset_jacobian'];joint = z['center_state']
        reset_weights = z['state_weights'];normalization = z['normalization_coordinates']
    trace,attachment,_ = chart_helpers()
    T = trace(12)
    boundary = np.vstack((T,attachment(12,normalization)[1]))
    gram = (boundary/reset_weights[:37])@(boundary/reset_weights[:37]).T
    values,vectors = np.linalg.eigh(gram)
    normalizer = (vectors*values**(-0.5))@vectors.T
    reset_raw = np.zeros((4,196))
    reset_raw[:,:37] = -np.vstack((T,attachment(12,joint[:37])[1]))/reset_weights[:37]
    reset_raw[:,98:135] = np.vstack((T,attachment(12,joint[98:135])[1]))/reset_weights[:37]
    reset_replay = normalizer@reset_raw-J[26:30]
    endpoint_rows = np.array([np.vstack((T,attachment(12,y[:37])[1]))/weights[:37] for y in states])
    boundary_action = np.einsum('ijk,ik->ij',endpoint_rows,directions[:,:37])
    signs = (-1.)**np.arange(1,13)
    lapse = np.exp(states[:,74:86]@signs)
    lapse_action = lapse*((directions[:,74:86]/weights[74:86])@signs)
    norm_action = np.einsum('ij,ij->i',norm_y,directions[:,:98])+norm_s*directions[:,98]
    density = lapse*descriptors/norms
    density_action = lapse_action*descriptors/norms+lapse*directions[:,98]/norms-lapse*descriptors*norm_action/norms**2
    # Every evaluated fixed-event reset row has only event/child state columns.
    # The null's left state is zero. With the opposite state held fixed, its
    # induced reset-state direction is zero; no node-13-to-reset map is assumed.
    fixed_opposite_state_direction = np.zeros(196)
    row_ledger = [
        dict(name='fourth_attachment_configuration',DB=0.,scope='Left state and fixed opposite state; exact structural zero.'),
        dict(name='three_configuration_traces',DB=[0.]*3,scope='Same fixed-opposite-state restriction.'),
        dict(name='relative_depth_identity_minus_scale_plus_radius_plus_depth',DB=0.,scope='Identically zero pullback at every state.'),
        dict(name='two_canonical_momentum_matches',DB=[0.]*2,scope='Stored reset rows 55:57; state-only, fixed opposite side.'),
        dict(name='two_persistence_dynamic_flux_rows',DB=[0.]*2,scope='Owned state-only interface with fixed event flux; no independent s argument.'),
        dict(name='boundary_lapse_difference_if_compared_at_fixed_opposite_state',DB=0.,scope='State-only lapse; no separate lapse-equality condition found in the 57 reset rows.'),
        dict(name='proper_time_density',DB=float(density_action[0]),scope='Derived clock density, NOT an owned two-sided matching equation.'),
        dict(name='full_seam_attachment_stationarity_or_boundary_graph_response',DB=None,scope='No owner-bound derivative of opposite arm/trace/map with respect to s13 is supplied.'),
    ]
    arrays = dict(unit_null=unit,reset_configuration_rows_raw_action=reset_raw,
        reset_boundary_normalizer=normalizer,reset_configuration_replay=reset_replay,
        fixed_opposite_state_direction=fixed_opposite_state_direction,
        stored_reset_rows_on_fixed_state_direction=J@fixed_opposite_state_direction,
        endpoint_boundary_rows_action=endpoint_rows,endpoint_boundary_on_null=boundary_action,
        right_attachment_on_child=endpoint_rows[1,3]@child[:37],
        endpoint_lapse=lapse,endpoint_lapse_on_null=lapse_action,
        endpoint_proper_time_density=density,endpoint_proper_time_density_on_null=density_action)
    report = dict(status='TWO_SIDED_SCALAR_OWNER_NOT_YET_DERIVED',
        base_commit='ed61d89c3a7946f5cd4f5af9e321771dabe2edc1',
        source_SHA256=sources,source_line_provenance=provenance,
        normalization='Use frozen unit null; physical ds=1e-7*d_descriptor_proof. Test scale 1e6 is not a physical datum.',
        reset_rows=dict(event_constraints=[0,25],event_selected_eigenvalue=[25,26],boundary_configuration=[26,30],child_constraints=[30,55],canonical_momentum=[55,57],slice_convention='zero-based half-open'),
        fixed_event_ledger='25 child constraint/energy + 4 boundary configuration + 2 canonical momentum = 31',
        attachment_formula='u_b=sum((-1)^k q_u,k); v_b=sum((-1)^j q_v,j); q_w=q0+u_b-log(cosh(2v_b))/2; x_D=q0-q_w; fourth raw row=x_D(child)-x_D(event)',
        normalized_reset_configuration_replay_maxabs=float(np.max(np.abs(reset_replay))),
        descriptor=dict(meaning='Independently carried signed selected eigenvalue of the child reduced raw Euler-Dirac Hessian L_zz, z=(velocity,multipliers). It represents lambda(Y) on the physical descriptor fiber.',
            not_identified_as=['boundary lapse','proper time','environment descriptor','relative attachment depth','seam spectral parameter z'],
            lapse_map='N_boundary=exp(sum((-1)^k m_k)); a function of the 98-state multipliers',
            proper_time_map='d tau/d arc=N_boundary*s/||G(Y,s)||',
            attachment_map='x_D=x_D(q); partial x_D/partial independently carried s at fixed state = 0',
            paired_map='(Y_event,Y_child,s_child) -> (x_D(event),x_D(child),N(event),N(child),s_child); no owned inverse or additional equation tying s_child to the two-sided quantities'),
        candidate_evaluations=row_ledger,
        local_left_attachment_on_null=float(boundary_action[0,3]),
        right_attachment_on_null_diagnostic=float(boundary_action[1,3]),
        right_attachment_on_complete_child_norm_diagnostic=float(np.linalg.norm(arrays['right_attachment_on_child'])),
        right_row_caveat='Node 14 is a later history endpoint, not the opposite side of the seam. Adding its fixed attachment row would act nontrivially on the frozen 66D tangent; no persistence descendant authorizes that substitution.',
        boundary_graph=dict(formula='q_e=C(F_B)q_c; p_c+C(F_B)^*p_e=J_enc, with opposite outward conormals; intersect L_child with the pulled-back opposite-side graph',
            seam_operator='S=M_e+U_R^dagger M_c U_R+W_phys; local W=0 does not erase the opposite arm',
            missing_object='A source-bound lift from (s13,p,q) to both boundary traces/attachment/arm responses and its derivative, selecting a scalar row of the existing seam equations at the same physical interface.',
            node13_node14_not_identified_as_two_seam_sides=True),
        rank_consequence='Any additional left-state-only row is zero on the exact local null; appending it cannot raise rank to 75. No legitimate nonzero scalar row has been recovered.',
        center_75_system_formed=False,center_75_rank=None,center_75_condition=None,inverse_replay=None,
        physical_child_tangent_changed=False,boundary_split_changed=False,reaction_replay_repeated=False,
        nonlinear_work_attempted=False,scientific_producers_run=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return report,arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report,arrays=calculate();args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue())
    report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['status']);print(json.dumps(report['candidate_evaluations'],indent=2))


if __name__=='__main__':main()
