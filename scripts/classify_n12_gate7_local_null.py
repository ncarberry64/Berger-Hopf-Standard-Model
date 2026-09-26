"""Classify the frozen local null without evaluating any scientific producer.

Angles are center diagnostics in declared coordinates, never a replacement for
an owner-bound coupled time generator or an environment compatibility map.
"""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

from checkpoint_n12_gate7_66d_tangent_binding import (
    ROOT, BASE, FIXED, PHYSICAL, SCALE, amat, mid, bound, digest, encoded,
)

BASE_COMMIT = 'd44d75bf60a1a783777795fcd395f6d95d259e7e'
LOCAL = ROOT/BASE/'gate7_local_child_flow_dimension_20260926'
BINDING = ROOT/BASE/'gate7_66d_checkpoint_20260926/binding'
SPLIT = ROOT/BASE/'gate7_8reaction_center_20260926'
QUOTIENT = ROOT/BASE/'BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json'
PROVENANCE = {
    'theory/n12_reset_time_quotient_generator_audit.md': [(1,30)],
    'theory/n12_continuum_singular_hitting_reset_relation.md': [(75,105)],
    'theory/n12_intrinsic_time_quotient_force_root.md': [(1,46)],
    'src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py': [(73,75),(108,129),(135,145)],
    'scripts/audit_n12_gate7_constraint_descriptor_hermite_collocation_candidate.py': [(67,77)],
    'scripts/materialize_n12_gate7_augmented_fixed_descriptor_newton_endpoint_candidate.py': [(68,76),(165,189)],
    'scripts/audit_n12_gate7_correlated_descriptor_newton_midpoint_replay.py': [(49,89)],
    'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py': [(3199,3218),(3273,3282)],
    'artifacts/flagship_integration/gate7_8reaction_center_20260926/source/bhsm_gate7_stageB_direct_interface.py': [(91,136)],
    'theory/bhsm_environmental_child_compatibility_selection.md': [(36,44),(125,143),(202,211),(265,304)],
    'theory/bhsm_environment_conditioned_reset_selector_recovery.md': [(36,50),(131,150)],
}


def line_comparison(a, b):
    """Unoriented principal angle plus oriented overlap; no scientific tolerance."""
    a = a/np.linalg.norm(a)
    b = b/np.linalg.norm(b)
    overlap = float(a@b)
    residual = float(np.linalg.norm(a-overlap*b))
    return dict(signed_overlap=overlap,
                principal_angle_degrees=float(np.degrees(np.arctan2(residual, abs(overlap)))),
                unit_projection_residual=residual)


def calculate():
    ctx.prec = 512
    sources = {}

    def verify(path, expected=None):
        actual = digest(path)
        if expected is not None and actual != expected:
            raise ValueError('frozen source changed: '+str(path))
        sources[path.relative_to(ROOT).as_posix()] = actual

    for folder in (LOCAL, BINDING, SPLIT):
        meta = json.loads((folder/'report.json').read_bytes())
        verify(folder/'report.json')
        verify(folder/'arrays.npz', meta['arrays_SHA256'])
    binding = json.loads((BINDING/'report.json').read_bytes())
    for path in (ROOT/FIXED, ROOT/PHYSICAL):
        verify(path, binding['source_SHA256'][str(path)])
    verify(QUOTIENT)
    quotient = json.loads(QUOTIENT.read_bytes())
    # This audit is an explicit negative owner finding, not a guessed generator.
    if quotient['dimension_statement']['explicit_generator_certified_in_current_checkpoint']:
        raise ValueError('quotient authority changed; review the new generator first')
    provenance = {}
    for name, ranges in PROVENANCE.items():
        path = ROOT/name
        verify(path)
        lines = path.read_text(encoding='utf-8').splitlines()
        provenance[name] = [dict(start=a, end=b, text='\n'.join(lines[a-1:b])) for a,b in ranges]
    verify(Path(__file__))
    with np.load(LOCAL/'arrays.npz') as z:
        K = z['K_cut']; saved_null = z['null_vector']
    with np.load(ROOT/FIXED) as z:
        rates = z['exact_endpoint_augmented_rates'][13:15]
        gradient = z['descriptor_gradient_action_diagnostic'][13:15]
        weights = z['state_weights']
    with np.load(ROOT/PHYSICAL) as z:
        B = z['endpoint_physical_tangent_action'][13:15]
        endpoint_df = z['endpoint_augmented_Jacobian_action'][13:15]
    with np.load(SPLIT/'arrays.npz') as z:
        P = z['trial_transform']; An = z['interface_normalized']
        XZ = z['child_basis_physical']; XL = z['boundary_complement_physical']
    with np.load(BINDING/'arrays.npz') as z:
        child = z['node_014_child_augmented']
        X = z['node_014_fixed_into_physical']

    # Exact definition over stored binary64 coefficients, then Arb enclosure of
    # its positive-left-component Euclidean unit normalization in proof units.
    right = -amat(K[:,1:]).solve(amat(K[:,0:1]))
    v = arb_mat([[arb(1)]]+[[right[i,0]] for i in range(74)])
    length = sum((v[i,0]**2 for i in range(75)), arb(0)).sqrt()
    unit = v/length
    u = mid(unit)[:,0]
    split = amat(P).solve(arb_mat([[unit[i,0]] for i in range(1,75)]))
    split_center = mid(split)[:,0]
    # Endpoint vectors use action-weighted states and physical descriptors.
    endpoints = np.zeros((2,99))
    endpoints[0,98] = SCALE*u[0]
    endpoints[1,:98] = B[1]@u[1:74]
    endpoints[1,98] = SCALE*u[-1]
    flow_reduced = np.array([
        np.r_[np.linalg.lstsq(B[i],rates[i,:98],rcond=None)[0],rates[i,98]/SCALE]
        for i in range(2)
    ])
    # This is only the orthogonal coordinate projection into the cut slice.
    # The omitted left state makes it NOT an exact lift of the flow.
    projected_flow = np.r_[flow_reduced[0,-1],flow_reduced[1]]
    null_pair = np.r_[np.zeros(73),u]
    pair_flow = flow_reduced.ravel()
    state_child = B[1]@XZ
    state_boundary = B[1]@XL
    qc = np.linalg.qr(state_child,mode='reduced')[0]
    qb = np.linalg.qr(state_boundary,mode='reduced')[0]
    child_proj = qc@(qc.T@endpoints[1,:98])
    boundary_proj = qb@(qb.T@endpoints[1,:98])
    oblique_child = state_child@split_center[:66]
    oblique_boundary = state_boundary@split_center[66:73]
    # Existing descriptor fiber is an implicated scalar owner, NOT an imposed
    # environment condition. Its nonlinear binding to this family is unproved.
    event_null = np.einsum('ij,ij->i',gradient,endpoints[:,:98])
    event_arc = np.einsum('ij,ij->i',gradient,rates[:,:98])
    event_fs = event_arc/rates[:,98]
    fiber = (event_null-endpoints[:,98])/SCALE
    interface_null = An@np.linalg.solve(X,u[1:74])
    child_q = np.linalg.qr(child,mode='reduced')[0]
    augmented_child_projection = child_q@(child_q.T@u[1:])
    h = 0.25
    midpoint = (endpoints[0]+endpoints[1])/2+h*(endpoint_df[0]@endpoints[0]-endpoint_df[1]@endpoints[1])/8
    arrays = dict(unit_null=u, left_descriptor_normalized_null=mid(v)[:,0],
        unit_null_lower_exact=np.array([str(unit[i,0].lower().fmpq()) for i in range(75)]),
        unit_null_upper_exact=np.array([str(unit[i,0].upper().fmpq()) for i in range(75)]),
        null_endpoints_action_physical=endpoints, null_right_split=split_center,
        null_midpoint_incidence_action_physical=midpoint,
        null_right_state_raw=endpoints[1,:98]/weights,
        null_pair_reduced=null_pair, flow_pair_reduced=flow_reduced,
        flow_pair_action_physical=rates, projected_flow_75_diagnostic=projected_flow,
        null_state_child_orthogonal_projection=child_proj,
        null_state_boundary_orthogonal_projection=boundary_proj,
        null_state_child_oblique_component=oblique_child,
        null_state_boundary_oblique_component=oblique_boundary,
        null_right_augmented_child_orthogonal_projection=augmented_child_projection,
        diagnostic_event_covectors=gradient, right_normalized_interface_on_null=interface_null)
    report = dict(
        status='UNRESOLVED_OWNER_SCALAR', classification='UNRESOLVED',
        base_commit=BASE_COMMIT, source_SHA256=sources, source_line_provenance=provenance,
        authority='Exact stored-matrix null enclosure; all angles/projections/event-gradient evaluations are center diagnostics, not tube or quotient certificates.',
        exact_unit_null_formula='(1,-M13^-1 N13 e_s)/sqrt(1+||M13^-1 N13 e_s||_2^2), positive left component',
        normalization='Euclidean in the 75 reduced proof coordinates; descriptor trial scale 1e-7, test scale 1e6; not an owned quotient metric.',
        exact_unit_null_replay=bound(amat(K)*unit),
        exact_unit_normalization_replay=bound(unit.transpose()*unit-amat([[1.]])),
        stored_unit_null_replay=bound(amat(K)*amat(u[:,None])),
        stored_old_null_difference=bound(v-amat(saved_null[:,None])),
        null_blocks=dict(left_state_norm=0.,left_boundary_norm=0.,left_descriptor_proof=float(u[0]),
            left_descriptor_physical=float(endpoints[0,98]),right_state_coefficient_norm=float(np.linalg.norm(u[1:74])),
            right_state_action_norm=float(np.linalg.norm(endpoints[1,:98])),right_descriptor_proof=float(u[-1]),
            right_descriptor_physical=float(endpoints[1,98]),right_boundary_split=split_center[66:73].tolist(),
            independent_midpoint_or_eigenline_response_variables=0,
            midpoint_interpretation='Dependent HS incidence is saved; no new internal unknowns.'),
        quotient_owner=dict(status=quotient['status'],fixed_event_fiber=67,retained_quotient_count=66,
            explicit_coupled_generator_available=False,owned_75_coordinate_lift_available=False,
            known_coupled_generator_angle=None,known_coupled_generator_event_evaluation=None,
            action_metric_quotient_overlap=None,
            reason='The stored audit explicitly leaves the 196D coupled hybrid generator and induced fixed-event quotient open; local child flow was rejected as that generator.'),
        stored_forward_flow_comparison=dict(
            parameter='normalized cancelled-field arc, not proper time; F_s obtained at each endpoint by dividing its state rate by its descriptor rate',
            exact_lift_into_75_slice_exists=False,
            omitted_left_state_action_norm=float(np.linalg.norm(rates[0,:98])),
            omitted_left_state_reduced_norm=float(np.linalg.norm(flow_reduced[0,:73])),
            tangent_projection_residuals=[float(np.linalg.norm(B[i]@flow_reduced[i,:73]-rates[i,:98])) for i in range(2)],
            projected_75_comparison=line_comparison(u,projected_flow),
            full_148_reduced_pair_comparison=line_comparison(null_pair,pair_flow),
            full_148_Fs_pair_comparison=line_comparison(null_pair,(flow_reduced/rates[:,98,None]).ravel()),
            action_state_pair_comparison=line_comparison(endpoints[:,:98].ravel(),rates[:,:98].ravel()),
            caveat='The projected 75-vector drops a unit left state rate and is not a gauge lift. The state-only action norm has no supplied descriptor extension owning a time quotient.'),
        event=dict(owner='Dlambda is the selected-eigenvalue state covector, not ds on the independent proof descriptor.',
            Dlambda_unit_null=event_null.tolist(),Dlambda_arc_flow=event_arc.tolist(),
            Dlambda_Fs=event_fs.tolist(),Dlambda_Fs_identity='Dlambda[G/Delta]=Delta/Delta=1 in the exact field owner',
            ds_unit_null=endpoints[:,98].tolist(),
            diagnostic_fiber_covector_on_null_proof_units=fiber.tolist(),
            fiber_covector='(Dlambda dy - ds)/1e-7; existing fiber candidate, NOT an environment covector'),
        projections=dict(right_child_oblique_coordinate_norm=float(np.linalg.norm(split_center[:66])),
            right_boundary_oblique_coordinate_norm=float(np.linalg.norm(split_center[66:73])),
            right_child_oblique_action_norm=float(np.linalg.norm(oblique_child)),
            right_boundary_oblique_action_norm=float(np.linalg.norm(oblique_boundary)),
            right_split_reconstruction=bound(amat(P)*split-arb_mat([[unit[i,0]] for i in range(1,75)])),
            right_child_orthogonal_action_norm=float(np.linalg.norm(child_proj)),
            right_child_orthogonal_action_residual=float(np.linalg.norm(endpoints[1,:98]-child_proj)),
            right_boundary_orthogonal_action_norm=float(np.linalg.norm(boundary_proj)),
            right_augmented_child_orthogonal_proof_norm=float(np.linalg.norm(augmented_child_projection)),
            right_augmented_child_orthogonal_proof_residual=float(np.linalg.norm(u[1:]-augmented_child_projection)),
            right_normalized_interface_action_norm=float(np.linalg.norm(interface_null)),
            descriptor_axes_proof_norm=float(np.linalg.norm(u[[0,-1]])),
            interpretation='Child and action-Hessian boundary complement are an oblique direct split, not orthogonal energies. Their large components cancel. Separate Euclidean subspace projections are not additive.'),
        environment=dict(compatibility_covector_E_available=False,E_on_null=None,
            proof_descriptor_to_environment_mapping_available=False,
            fixed_left_state_interface_derivative_on_null=[0.]*7,
            reason='The seven frozen interface rows take a 98-state and fixed event coordinates/momentum/flux, with no independent carried descriptor. The typed environment tuple supplies no source-level map to s13.'),
        decision=dict(case_A_established=False,case_B_established=False,
            neither_removal_justified=True,physical_non_gauge_theorem_claimed=False,
            meaning='UNRESOLVED_OWNER_SCALAR names a missing owner binding, not a proof that the true coupled gauge cannot explain it.',
            first_missing_object='The owner-bound induced coupled time generator/coordinate lift at node 13, or an environment-to-carried-descriptor compatibility covector. The known child flow cannot be substituted.',
            targeted_scalar_followup='The existing lambda(Y)=s fiber has nonzero derivative on this null, but its identification with the carried local family and nonlinear initial/history datum is unproved. Do not impose it from a diagnostic.'),
        quotient_matrix_rank=None,quotient_condition=None,quotient_or_environment_condition_imposed=False,
        old_8x8_extraction_repeated=False,center_reaction_replay_repeated=False,
        nonlinear_work_attempted=False,scientific_producers_run=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return report, arrays


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    report, arrays = calculate()
    args.out.mkdir(parents=True,exist_ok=False)
    buffer = io.BytesIO()
    np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue())
    report['arrays_SHA256'] = digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['status'])
    print(json.dumps(report['stored_forward_flow_comparison'],indent=2))


if __name__ == '__main__':
    main()
