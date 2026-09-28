"""Assemble the current sufficient-state ledger without claiming completion."""
import argparse
import json
from pathlib import Path
from flint import arb, arb_mat, ctx
import build_n12_current_incoming_response as build


def calculate(first, repeat, secants, out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new ledger output directory required')
    for name in ('arrays.npz', 'report.json'):
        if (first/name).read_bytes() != (repeat/name).read_bytes():
            raise ArithmeticError('current internal response repeat differs: '+name)
    report = json.loads((first/'report.json').read_bytes())
    for path, expected in report['source_SHA256'].items():
        if build.digest(build.ROOT/path) != expected:
            raise ValueError('shared response source changed: '+path)
    data = build.verified_packet(first, ['lapse_value', 'current_descriptor', 'augmented_rate',
        'internal_scalars', 'descriptor_lookback_proper_clock', 'log_lapse_first_66',
        'proper_log_radius_rate_first_66', 'formal_zero_descriptor_duration_coefficient_first_66',
        'formal_radius_history_coefficient_first_66'])
    N, s = data['lapse_value'][0, 0], data['current_descriptor'][0, 0]
    normG, rate_s = data['internal_scalars'][4, 0], data['augmented_rate'][98, 0]
    replay = -N*s/(normG*rate_s)-data['descriptor_lookback_proper_clock'][0, 0]
    if not replay.contains(0):
        raise ArithmeticError('proper clock conventions disagree')
    endpoint = arb_mat(data['log_lapse_first_66'].tolist()+data['proper_log_radius_rate_first_66'].tolist())
    da = data['formal_zero_descriptor_duration_coefficient_first_66']
    seed = da.transpose()/sum((v*v for v in da.entries()), arb(0)).sqrt()
    witness = seed-endpoint.transpose()*(endpoint*endpoint.transpose()).solve(endpoint*seed)
    witness /= sum((v*v for v in witness.entries()), arb(0)).sqrt()
    endpoint_replay = endpoint*witness
    duration_witness = da*witness
    history_witness = data['formal_radius_history_coefficient_first_66']*witness
    if not all(v.contains(0) for v in endpoint_replay.entries()) or duration_witness[0, 0].contains(0):
        raise ArithmeticError('endpoint-compression witness did not separate internal clock dependence')
    rows = []
    def add(variable, classification, local, memory, slaved, independent, affects, removable, evidence):
        rows.append(dict(variable=variable, classification=classification, local_current_state=local,
            history_memory_required=memory, slaved=slaved, independent=independent,
            affects_q66=affects[0], affects_H66=affects[1], affects_B66x73=affects[2],
            removable_without_changing_predictions=removable, evidence=evidence))
    add('Frozen ten local sector values, gradients and Q66 curvature', 'CURRENTLY AVAILABLE', True,
        False, False, False, ['retained']*3, False, '6ccc130e local_run1; consumed unchanged')
    add('Endpoint log radius', 'REDUNDANT / DERIVED FROM ANOTHER OPERAND', True, False, True, False,
        ['no independent fixed-child first variation', 'moving-reset curvature retained', 'launch radius response retained'],
        'Independent radius input removable; geometric dependence retained',
        'Saved Q66 annihilator; current scalar/gauge and Weyl coefficient first contractions enclose zero')
    add('Endpoint log lapse, lapse and proper log-radius rate', 'CURRENTLY AVAILABLE', True, False, True, False,
        ['retained']*3, False, 'Derived from current raw state; full 66-column first maps saved in shared packet')
    add('Selected local eigenline/eigenvalue, hard response and normalization', 'CURRENTLY AVAILABLE', True,
        'Values needed along history, not just at endpoint', True, False, ['retained']*3, False,
        'One 124-variable local internal residual and 124x66 response, with forward/adjoint replay')
    add('Classical geometry/eta/velocity/lapse/shift and fixed Hopf inertia along incoming history',
        'REQUIRES COEFFICIENT PROPAGATION', False, True, 'Owned dynamics; numerical history unsolved', None,
        ['retained']*3, False, 'x(tau) alone is insufficient for the classical attached action')
    add('Incoming x(tau); unit scalar/gauge V and Weyl W', 'REQUIRES COEFFICIENT PROPAGATION',
        'Endpoint coefficients available', True, True, False, ['retained']*3, False,
        'V=exp(-2x), W=exp(-x); nonzero D(a*radius_rate) proves fixed endpoint radius does not erase path response')
    add('Incoming descriptor amplitude, proper duration and moving quadrature weights',
        'REQUIRES DURATION PROPAGATION', 'Clock coefficient and first map available', True,
        'Must be bound by owned history/endpoint equations', None, ['retained']*3, False,
        'Formal T=a*A^2 germ is not a selected finite duration; current candidate descriptor excludes zero')
    add('Current incoming launch/query 73-column incidence', 'REQUIRES COEFFICIENT PROPAGATION', False,
        True, 'Requires current connection/event-hit and moving-reset incidence', None,
        ['parameterized base', 'parameterized base', 'required'], False,
        'Available 73D chart is at downstream node13; reset_match_complete declares first_73_jet_certified=false')
    add('Incoming M11, child response, common temporal pencil and heat-minus-zeta cotangent',
        'REQUIRES INTERNAL OPERATOR RESPONSE', False, True, True, False, ['retained']*3, False,
        'Single E1/C2 seam, exterior E0 Dirichlet; local internal system is not this complete operator')
    add('Gauge Wentzell and scalar/topographic response; moving attachment',
        'REQUIRES CONTACT RESPONSE', 'Laws and reset point available', True, True, False,
        ['retained']*3, False, 'Zero direct endpoint-radius first term does not zero full contact/mixed response')
    add('Proper zeta density and coordinate-time density', 'DERIVABLE FROM CURRENT LOCAL STATE', True,
        'Their integrals require current history and duration', True, False, ['retained']*3, False,
        'Same original binary64 59/30 constant; proper density first vanishes at endpoint, lapse-weighted first survives')
    add('Independent reset-frame source and independent fermion delta contact',
        'REDUNDANT / DERIVED FROM ANOTHER OPERAND', True, False, False, False, ['owned zero']*3,
        'Yes, only these independent source terms', 'AE2 parallel transport and S_Sigma_F=0; physical transport/contact terms retained')
    add('Longitudinal gauge plus matching complex ghost pair',
        'REDUNDANT / DERIVED FROM ANOTHER OPERAND', True, False, False, False, ['owned signed cancellation']*3,
        'Yes, in retained BRST direct sum', 'Mode-by-mode cancellation; does not remove transverse gauge')
    add('Absolute proper-time origin', 'REDUNDANT / DERIVED FROM ANOTHER OPERAND', False, False,
        False, False, ['absent in endpoint-labelled representation']*3,
        'Yes, as an absolute label only', 'No Q66 time/gauge column identified or removed')
    secant_report = json.loads((secants/'report.json').read_bytes())
    if build.digest(secants/'arrays.npz') != secant_report['arrays_SHA256']:
        raise ValueError('secant packet changed')
    output = dict(object='FORMATION_SUFFICIENT_STATE_LEDGER', rows=rows,
        complete_common_incoming_family=False, globally_minimal=False,
        independent_input_count_after_assembly=None, endpoint_reset_tangent_dimension_retained=66,
        full_internal_dimension=None, numerically_solved_local_internal_dimension=124,
        q66=None, H66=None, B66x73=None, stationary_root_claimed=False,
        physical_duration_selected=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        proper_clock_convention_replay=build.bound(arb_mat([[replay]])),
        endpoint_compression_witness=dict(
            scope='Formal local clock germ only; not a complete-history input count',
            unit_direction_66=[build.scalar(v) for v in witness.entries()],
            endpoint_log_lapse_and_proper_rate_replay=build.bound(endpoint_replay),
            formal_duration_coefficient_response=build.scalar(duration_witness[0, 0]),
            formal_radius_history_coefficient_response=build.scalar(history_witness[0, 0]),
            result='Even fixing endpoint radius, lapse and radius rate does not remove the local internal clock response'),
        simplifications=[
            'D_Q x_endpoint, D_Q V_endpoint and D_Q W_endpoint enclose zero; no independent endpoint radius column.',
            'D_Q zeta_proper_density_endpoint encloses zero; D_Q zeta_coordinate_density_endpoint survives lapse.',
            'The formal history term D(a*v) is nonzero: no full spectral/history/heat cancellation follows.',
            'D tau has lapse and local internal terms. Endpoint fixed radius supplies no duration cancellation.',
            'Direct seam-radius first terms vanish only at fixed child; moving/launch/mixed contact terms remain.',
            'No whole-history variable is certified HISTORY_COMPRESSIBLE for the complete action from endpoint data alone.',
        ],
        shared_packet=first.relative_to(build.ROOT).as_posix(),
        repeat_packet=repeat.relative_to(build.ROOT).as_posix(), byte_identical=True,
        prototype_not_authoritative='run1 used an instrumented evaluator before frozen-source preservation was restored; retain only as a development record',
        incomplete_development_secants='secants1 contains arrays only; report serialization failed and was fixed before complete repeated secant runs',
        scope_boundary='New current numerical local response and formal clock germ. Complete finite history, endpoint binding, temporal/contact/heat elimination, and incoming launch incidence remain unevaluated.',
        source_SHA256={p.relative_to(build.ROOT).as_posix(): build.digest(p) for p in (
            Path(__file__), first/'arrays.npz', first/'report.json', repeat/'arrays.npz', repeat/'report.json',
            secants/'arrays.npz', secants/'report.json',
            build.BASE/'formation_op_current_20260928/dependencies.json',
            build.BASE/'formation_op_current_20260928/dependency_run1_complete/report.json',
            build.CANDIDATE.with_name('report.json'),
            build.BASE/'gate7_launch_response_20260927/report.json',
            build.ROOT/'theory/n12_gate7_external_birth_source_role_supersession.md',
            build.ROOT/'theory/n12_gate7_current_formation_action_ownership.md',
            build.ROOT/'scripts/derive_n12_gate7_mixed_boundary_launch_contract.py',
        )})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build.encoded(output))
    print('Formation sufficient-state ledger saved; full q66/H66/B66x73 remain unevaluated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--first', type=Path, required=True)
    parser.add_argument('--repeat', type=Path, required=True)
    parser.add_argument('--secants', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    calculate(args.first.resolve(), args.repeat.resolve(), args.secants.resolve(), args.out.resolve())
