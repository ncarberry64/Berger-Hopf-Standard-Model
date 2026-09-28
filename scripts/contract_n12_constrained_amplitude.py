"""Bind the amplitude KKT convention and contract frozen temporal operands.

No action, eigenline, history or derivative producer is rerun. The saved
signed point is not relabelled as a positive-amplitude formation member.
"""
import argparse
import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from evaluate_n12_gate7_current_contractions import packet, scalar, SHARED, LOCAL, FRAME, BASE
from checkpoint_n12_gate7_66d_tangent_binding import restore, bound, digest, encoded
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from contract_n12_current_temporal_residual import block, POINT
from bhsm.interface.formation_amplitude import orbit_cut_endpoint

TEMPORAL = BASE/'current_temporal_residual_20260928/run2'


def calculate(out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    sr, z = packet(SHARED); lr, l = packet(LOCAL); fr, f = packet(FRAME)
    tr, t = packet(TEMPORAL); pr, p = packet(POINT)
    for folder in (SHARED, LOCAL, FRAME, POINT):
        key = (folder/'arrays.npz').relative_to(ROOT).as_posix()
        if digest(ROOT/key) != tr['source_SHA256'][key]:
            raise ValueError('temporal packet does not bind this source: '+key)
    y = restore(z, 'current_raw_state')
    g = restore(l, 'local_action_gradient_raw')
    density = restore(l, 'local_action_value')[0, 0]
    weights = restore(f, 'action_coordinate_weights')
    rate = restore(z, 'augmented_rate'); drate = restore(z, 'augmented_rate_first_66')
    raw = arb_mat(98, 1, [rate[i, 0]/weights[i, 0] for i in range(98)])
    draw = arb_mat(98, 66, [drate[i, j]/weights[i, 0] for i in range(98) for j in range(66)])
    nu = restore(t, 'coordinate_clock')[0, 0]
    dnu = restore(t, 'coordinate_clock_first_66')
    sy = restore(t, 'source_state'); st = restore(t, 'source_time')[0, 0]
    dsy = restore(t, 'source_state_first'); dst = restore(t, 'source_time_first')
    ds_arc = rate[98, 0]
    if ds_arc.contains(0):
        raise ValueError('regular descriptor chart required')
    ys = raw/ds_arc; ts = nu/ds_arc
    result = orbit_cut_endpoint(density=density, momentum=block(g, range(37, 74), [0]),
        velocity=block(y, range(37, 74), [0]), state_amplitude=ys,
        coordinate_time_amplitude=ts, state_source=sy, time_source=st)
    ward_first = raw.transpose()*dsy+sy.transpose()*draw+nu*dst+st*dnu
    replays = {k: v for k, v in result.items() if k.endswith('replay')}
    replays['temporal_tangential_first_66'] = ward_first
    if not all(v.contains(0) for m in replays.values() for v in m.entries()):
        raise ArithmeticError('moving-cut endpoint/source identity failed')
    zeta = restore(z, 'zeta_coordinate_density_value')[0, 0]
    subtraction = zeta*ts  # -D Gamma_zeta = +L_zeta*dt_birth/dA
    classical = -(density-zeta)*ts
    # Endpoint-labelled coordinates: terminal R=R(p,y) has no explicit A.
    # This is a PARTIAL derivative; R_y*y_A is retained by the implicit solve.
    terminal_J = restore(p, 'incoming_constraint_J')
    terminal_RA = arb_mat(terminal_J.nrows(), 1)
    arrays = {**{'endpoint_'+k: arb_mat([[v]]) for k, v in result.items() if not k.endswith('replay')},
        **replays, 'current_signed_descriptor': restore(z, 'current_descriptor'),
        'current_cut_state_direction': ys, 'current_cut_time_direction': arb_mat([[ts]]),
        'point_zeta_subtraction_cut': arb_mat([[subtraction]]),
        'point_classical_cut': arb_mat([[classical]]),
        'terminal_reset_explicit_amplitude_partial': terminal_RA,
        'terminal_reset_state_partial': terminal_J,
        'attached_to_classical_replay': arb_mat([[result['endpoint']+subtraction-classical]])}
    files = [Path(__file__), ROOT/'src/bhsm/interface/formation_amplitude.py',
        ROOT/'src/bhsm/interface/gate7_current_action.py',
        ROOT/'src/bhsm/interface/formation_stationarity_kkt.py',
        ROOT/'theory/n12_constrained_joint_amplitude_row.md',
        ROOT/'theory/n12_desingularized_finite_history_operator_parameter.md',
        ROOT/'theory/n12_compact_history_endpoint_role_provenance.md',
        ROOT/'theory/n12_gate7_incoming_amplitude_zeta_cotangent.md',
        ROOT/'scripts/derive_n12_gate7_formation_stationarity_inputs.py']
    for folder in (SHARED, LOCAL, FRAME, TEMPORAL, POINT):
        files.extend([folder/'arrays.npz', folder/'report.json'])
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    report = dict(status='CONSTRAINED_AMPLITUDE_ROW_BOUND_CURRENT_ENDPOINT_CONTRACTIONS_REPLAYED',
        base_commit='20484ee66f6c52faf836c967e1d962cf4c0b75c4',
        convention='L=Gamma+mu^T R-eta^T F; mu=-lambda for the user minus-sign convention',
        amplitude_owner='Signed incoming descriptor at the moving birth endpoint of the existing fixed-terminal family',
        amplitude_eliminated=False, amplitude_fixed_from_external_source=False,
        explicit_amplitude_determining_birth_constraint_found=False,
        terminal_constraint_partial=dict(shape=[32, 1], value='exactly zero at fixed terminal y,p',
            total_derivative='R_A+R_y*y_A; R_y*y_A is not discarded'),
        current_signed_descriptor=scalar(restore(z, 'current_descriptor')[0, 0]),
        point_cut_contributions={k: scalar(result[k]) for k in ('configuration', 'clock', 'endpoint', 'leibniz')},
        point_cut_zeta_subtraction=scalar(subtraction), point_cut_classical=scalar(classical),
        replays={k: bound(v) for k, v in replays.items()},
        constrained_amplitude_report=dict(raw_partial_Gamma_joint=None,
            constraint_multiplier_contribution=None, endpoint_event_contribution=None,
            contact_heat_contribution=None, final_constrained_amplitude_row=None,
            reason='No solved positive-amplitude joint realization/multipliers or full-domain heat cotangent supplied by frozen point packets'),
        interpretation='The current negative signed-descriptor point supplies a local algebra replay, not a positive-amplitude force or a new selected birth endpoint',
        sufficient_heat_contraction='Full coupled-domain graded Dirichlet birth conormal heat pressure, including interior spectrum and the owned remainder',
        no_temporal_residual_zeroing=True, no_internal_block_zeroing=True,
        q66=None, complete_amplitude_row_evaluated=False,
        new_scientific_producer_calls=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={path.relative_to(ROOT).as_posix(): digest(path) for path in files},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    ledger = dict(authority='docs/GATE7_CURRENT_CALCULATION_SCOPE.md',
        existing_obligation='Same-action constrained force/root',
        consumed_equation='F_A=Gamma_A+mu^T R_A-eta^T F_A_internal, F_n^T eta=Gamma_n+R_n^T mu',
        rows=[dict(input='formation amplitude', classification='NECESSARY',
                   retained='Existing constrained saddle coordinate; no independent birth law'),
              dict(input='constraint/event multipliers', classification='SLAVED',
                   retained='Existing saddle unknowns; not set from J_ext=0'),
              dict(input='temporal orbit-cut response', classification='HISTORY-COMPRESSIBLE',
                   retained='Endpoint contraction and proved tangential source cancellation; general physical directions still need their adjoint'),
              dict(input='joint birth heat pressure', classification='HISTORY-COMPRESSIBLE',
                   retained='One scalar full-domain graded spectral contraction for the amplitude row'),
              dict(input='complete incoming trajectory storage', classification='REDUNDANT',
                   retained='Not required by the contraction interface')],
        remaining='Instantiate the same joint internal graph and signed heat/contact contraction as functions of the unsolved amplitude',
        report_SHA256=digest(out/'report.json'))
    (out/'BHSM_SUFFICIENT_STATE_LEDGER.json').write_bytes(encoded(ledger))
    for obj in (z, l, f, t, p): obj.close()
    print(json.dumps({k: report[k] for k in ('status', 'point_cut_contributions', 'point_cut_classical', 'replays')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out)
