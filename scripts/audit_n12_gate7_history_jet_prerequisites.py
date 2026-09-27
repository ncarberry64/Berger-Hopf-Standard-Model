"""Audit saved first-jet operands without calling any scientific producer.

This is a prerequisite certificate, not a physical history-jet certificate.
In particular the selected-line border must never be read as Dlambda.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from flint import arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'artifacts/flagship_integration'
EVIDENCE = ROOT.parent / 'BHSM-ae32-crossing-correction'
DF = EVIDENCE / 'artifacts/flagship_integration/.primal_mean_value_component_centered_endpoint_uniform_df_work/endpoint_013'
FIBER = BASE / 'gate7_descriptor_fiber_owner_20260926/report.json'
TANGENT = BASE / 'gate7_reduced_fiber_tangents_20260926/report.json'
FIXED = BASE / 'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
HISTORICAL = BASE / 'BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS.json'
AFFINE = BASE / 'BHSM_N12_GATE7_EXACT_AFFINE_72D_HISTORY_FIRST_JET.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def interval(value):
    return dict(lower_exact=str(value.lower().fmpq()),
                upper_exact=str(value.upper().fmpq()),
                midpoint_diagnostic=float(value.mid()),
                radius_upper_diagnostic=float(value.rad().upper()))


def calculate():
    ctx.prec = 512
    sources = {}

    def bind(path, expected=None):
        actual = digest(path)
        if expected is not None and actual != expected:
            raise ValueError('source hash mismatch: ' + str(path))
        key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path.resolve())
        sources[key] = actual

    def record(path):
        bind(path)
        return json.loads(path.read_bytes())

    fiber = record(FIBER)
    tangent = record(TANGENT)
    bind(TANGENT.with_name('arrays.npz'), tangent['arrays_SHA256'])
    node = fiber['node13']
    bind(FIXED, fiber['source_SHA256'][FIXED.relative_to(ROOT).as_posix()])
    df = record(DF / 'record.json')
    receipt = record(DF / 'reproduction.json')
    bind(DF / 'record.json', receipt['record_SHA256'])
    bind(DF / 'derivative.npz', df['data_SHA256'])
    if not (receipt['byte_identical'] and receipt['independent_recomputation']
            and df['report']['validation_passed']
            and df['report']['uniform_physical_first_derivatives_enclosed']):
        raise ValueError('paired uniform derivative certificate required')
    # Bind its selected-eigenpair witness to the recovered fiber owner packet.
    point_files = []
    for name, sha in fiber['source_SHA256'].items():
        if name.endswith('endpoint_013\\record.json') or name.endswith('endpoint_013\\eigenpair.npz'):
            p = Path(name)
            relative = p.relative_to(EVIDENCE).as_posix()
            if df['binding']['files'].get(relative) != sha:
                raise ValueError('eigenpair family mismatch')
            bind(p, sha)
            point_files.append(p)
    if len(point_files) != 2:
        raise ValueError('both exact point witnesses required')
    with np.load(FIXED) as z:
        state, weights = z['projected_states'][13], z['state_weights']
    point_data = next(p for p in point_files if p.suffix == '.npz')
    with np.load(point_data) as z:
        if not (all(fmpq(str(a)) == fmpq(*float(b).as_integer_ratio()) for a, b in
                    zip(z['center_state_mid_q'], state, strict=True))
                and all(fmpq(str(r)) == 0 for r in z['center_state_rad_q'])):
            raise ValueError('point witness does not bind the frozen state exactly')
    with np.load(DF / 'derivative.npz') as z:
        keys = sorted(z.files)
        center = fmpq(str(z['raw_domain_mid_q'][98]))
        radius = fmpq(str(z['raw_domain_rad_q'][98]))
        contractions = [interval(arb(str(c)) + arb(0, arb(str(r)))) for c, r in
                        zip(z['descriptor_contractions_mid_q'], z['descriptor_contractions_rad_q'])]
        border_norm = float(np.linalg.norm([float(arb(str(v))) for v in z['point_line_center_mid_q'][-1]]))
    if center != fmpq(node['s13_exact']):
        raise ValueError('different descriptor center')
    upper_lambda = fmpq(node['lambda_owner']['upper_exact'])
    separation = center - radius - upper_lambda
    ratio = (center - upper_lambda) / radius
    if not separation > 0:
        raise ValueError('fixed-state relabel adjudication changed')
    historical = record(HISTORICAL)
    bind(HISTORICAL.with_suffix('.npz'), historical['data_SHA256'])
    with np.load(HISTORICAL.with_suffix('.npz')) as z:
        same_center = np.array_equal(state, z['center_state'])
        same_weights = np.array_equal(weights, z['state_weights'])
        distance = np.linalg.norm((z['center_state'] - state) * weights)
        width = np.max(z['lambda_first_action_upper'] - z['lambda_first_action_lower'])
    affine = record(AFFINE)
    bind(AFFINE.with_suffix('.npz'), affine['data_SHA256'])
    if affine['claim_boundary']['nonlinear_exact_solution_family_first_jet_transfer'] != 'OPEN':
        raise ValueError('historical jet authority changed; reassess')
    code = [
        'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py',
        'src/bhsm/interface/centered_coupled_variation_residual.py',
        'scripts/diagnose_n12_gate7_centered_uniform_derivatives.py',
        'scripts/n12_gate7_coupled_normalization_derivative_refinement.py',
    ]
    for name in code:
        bind(EVIDENCE / name, df['binding']['files'][name])
        bind(ROOT / name)
        # Preserve both byte hashes; Windows checkouts may differ only by CRLF.
        if (ROOT / name).read_text(encoding='utf-8') != (EVIDENCE / name).read_text(encoding='utf-8'):
            raise ValueError('source implementation differs: ' + name)
    for name in [
        'scripts/certify_n12_c2_signed_first_coefficient_vectors.py',
        'scripts/materialize_n12_gate7_exact_affine_72d_history_first_jet.py',
        'src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py',
        'theory/n12_c2_descriptor_fiber_denominator.md',
    ]:
        bind(ROOT / name)
    bind(Path(__file__).resolve())
    return dict(
        status='SAVED_OPERAND_HISTORY_JET_PREREQUISITES_CHECKED',
        result_scope='Validated saved-operand prerequisites and domain obstruction; no new physical jet.',
        base_commit='eef4149c7d0df292eb40731df2e35490dfafa18c',
        source_SHA256=sources,
        recovered_owner='EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED',
        node13=dict(s13_exact=node['s13_exact'], lambda_owner=node['lambda_owner'],
                    frozen_fiber_residual=node['residual_physical']),
        fixed_state_relabel=dict(
            descriptor_domain_center_exact=str(center), descriptor_domain_radius_exact=str(radius),
            descriptor_domain_lower_exact=str(center-radius), descriptor_domain_upper_exact=str(center+radius),
            lambda_below_domain=True, separation_lower_exact=str(separation),
            separation_lower_diagnostic=float(separation), shift_over_radius_lower_exact=str(ratio),
            shift_over_radius_diagnostic=float(ratio),
            scope='Only relabeling s at the unchanged Y13 is excluded from this saved derivative domain. No assertion that the tube has no fiber-consistent state.'),
        saved_derivative=dict(
            certified_scope=df['report']['scope'], arrays=keys,
            full_rayleigh_covector_saved=False,
            line_border_is_eigenvalue_derivative=False,
            point_line_border_norm_diagnostic=border_norm,
            cpsi_Dlambda_Psi=contractions[0], R_Dlambda_Vhard=contractions[1],
            cpsi_sign_certified_positive=fmpq(contractions[0]['lower_exact']) > 0,
            scope='The two contractions are uniform along their existing action-owned directions; they are not the 98-component covector or its 66-column pullback.'),
        historical_covector=dict(reference_node=historical['reference_node'],
            same_center=same_center, same_action_weights=same_weights,
            weighted_center_distance_diagnostic=float(distance),
            maximum_component_width_diagnostic=float(width),
            transferable_to_node13=False),
        historical_jet=dict(status=affine['status'], claim_boundary=affine['claim_boundary'],
            nonlinear_transfer_certified=False),
        comparisons=dict(old_vs_owner=tangent['paired_history_reduced_tangent_comparison'],
            old_vs_new=None, owner_vs_new=None,
            new_rank=None, new_orientation=None, new_projector_uncertainty=None,
            new_state_residual=None, new_intrinsic_residual=None,
            equivalence_within_certified_uncertainty='NOT_ADJUDICABLE_WITHOUT_NEW_JET'),
        exact_missing_derivative='The same-history enclosure of g13(v)=D3 A_N12(Y13_star)[(0,psi13_star),(0,psi13_star),W_state^-1 v], with certified selected-line and center uncertainty. A separate point contraction can supply g at the frozen Y13, but does not supply the corrected shooting history.',
        next_single_owner='Fiber-constrained interval-13 center/Jacobian packet, including the unprojected signed Rayleigh row and the fixed-label physical parameter lift inside the differentiated solve.',
        geometry='At fixed action-owned fiber label ds/dxi=0, impose g13 J13=0 inside the solve. The earlier arc-parameterized augmented history does not by itself certify this fixed-label lift.',
        reclassification='NONE: prior 66D candidates remain candidates; Outcome A/B cannot be decided.',
        independent_descriptor_column_added=False, scientific_producers_run=False,
        center_modified=False, new_history_jet_certified=False, center_certificate_promoted=False,
        tolerances_changed=False, Layer_C_rebound=False, nonlinear_campaign_started=False,
        surface_core_continuation_performed=False, SURFACE_CORE_COMPACTIFICATION='CONDITIONAL',
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = calculate()
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'report.json').write_bytes((json.dumps(report, sort_keys=True, indent=2) + '\n').encode())
    print(report['status'])
    print(json.dumps(report['fixed_state_relabel'], indent=2))


if __name__ == '__main__':
    main()
