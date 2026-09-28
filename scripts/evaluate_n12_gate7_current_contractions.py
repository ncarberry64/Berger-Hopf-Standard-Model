"""Evaluate new contractions from frozen packets; no science producer calls.

The complete q66 is not replaced by any subsystem output. This replay binds
the new evaluator to the current normal response, contracts the current C2
zeta element model, and preserves the exact common-functional subtraction.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import digest, encoded, restore, bound
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from bhsm.interface.gate7_current_action import (
    ActionBase, ActionSector, ImplicitAction, evaluate_gate7_current_action,
)
from bhsm.interface.arb_zeta_contractions import zeta_first

BASE = ROOT/'artifacts/flagship_integration'
SHARED = BASE/'current_incoming_response_20260928/run2'
LOCAL = BASE/'formation_op_current_20260928/local_run1'
CORE = BASE/'gate7_current_history_20260927/core'
FRAME = BASE/'gate7_formation_action_basis_20260928/run1'


def packet(folder):
    report = json.loads((folder/'report.json').read_bytes())
    if digest(folder/'arrays.npz') != report['arrays_SHA256']:
        raise ValueError('frozen packet hash changed: '+str(folder))
    return report, np.load(folder/'arrays.npz')


def scalar(a):
    return dict(midpoint=float(a.mid()), radius_upper=float(a.rad()),
                lower=str(a.lower().fmpq()), upper=str(a.upper().fmpq()))


def calculate(out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    sr, shared = packet(SHARED)
    lr, local = packet(LOCAL)
    cr, core = packet(CORE)
    fr, frame = packet(FRAME)
    # Source identity is bound through the archived common-state packets.
    for folder in (LOCAL, FRAME):
        expected = sr['source_SHA256'][(folder/'arrays.npz').relative_to(ROOT).as_posix()]
        if digest(folder/'arrays.npz') != expected:
            raise ValueError('current shared/local/frame source identity differs')
    state_replay = restore(shared, 'current_raw_state')-restore(local, 'current_incoming_state_raw')
    if not all(v.contains(0) for v in state_replay.entries()):
        raise ValueError('current incoming centers differ')
    base = ActionBase(sr['arrays_SHA256'], sr['arrays_SHA256'], 'pointwise-no-duration',
                      sr['arrays_SHA256'], 'no-temporal-contact-in-local-subsystem', fr['arrays_SHA256'])
    A = restore(shared, 'local_internal_internal_jacobian')
    X = restore(shared, 'local_internal_input_partial')
    Dn = restore(shared, 'local_internal_internal_first')
    arrays = dict(current_state_replay=state_replay)
    local_replays = {}
    def unavailable_launch(v):
        raise ValueError('local packet does not own the complete incoming 73-direction incidence')
    for name, index in [('selected_eigenvalue', 61), ('hard_response_border', 123)]:
        gradient = arb_mat(124, 1); gradient[index, 0] = 1
        sector = ActionSector(name, base, arb_mat(66, 1), gradient)
        query = ImplicitAction(base, A, X, unavailable_launch, (sector,), (name,),
                               'Current 124-variable local subsystem only',
                               {'uniform_neighborhood': None, 'omitted_history': None},
                               normal_residual=restore(shared, 'local_internal_residual'))
        result = evaluate_gate7_current_action(query, {'q66': True})
        truth = arb_mat(66, 1, [Dn[index, j] for j in range(66)])
        replay = result['q66']-truth
        if not all(v.contains(0) for v in replay.entries()):
            raise ArithmeticError('saved normal derivative and new adjoint disagree')
        arrays[name+'_first_66'] = result['q66']
        arrays[name+'_forward_adjoint_replay'] = replay
        local_replays[name] = bound(replay)
    total_local = restore(local, 'local_action_partial_66')
    zeta_local = restore(shared, 'zeta_coordinate_density_first_66').transpose()
    boundary_split = sum((restore(local, s+'_local_partial_66') for s in
                          ['boundary_scalar_vacuum', 'boundary_vector_vacuum', 'boundary_Weyl_vacuum']), arb_mat(66, 1))
    arrays['local_attached_density_partial_66'] = total_local
    arrays['local_zeta_density_partial_66'] = zeta_local
    arrays['local_classical_density_partial_66'] = total_local-zeta_local
    arrays['frozen_split_boundary_minus_unsplit_zeta'] = boundary_split-zeta_local
    # Integration by parts of the existing finite-N temporal action: this
    # terminal cotangent needs no incoming history. No on-shell cancellation
    # is assumed for the remaining classical Euler/multiplier residual.
    gradient = restore(local, 'local_action_gradient_raw')
    state = restore(shared, 'current_raw_state')
    Qraw = restore(frame, 'Q66_current_raw')
    momentum = arb_mat(1, 37, [gradient[37+i, 0] for i in range(37)])
    Qq = arb_mat(37, 66, [Qraw[i, j] for i in range(37) for j in range(66)])
    pi_v = sum((gradient[37+i, 0]*state[37+i, 0] for i in range(37)), arb(0))
    classical_density = restore(local, 'local_action_value')[0, 0]-restore(shared, 'zeta_coordinate_density_value')[0, 0]
    arrays['incoming_terminal_momentum_pullback_66'] = (momentum*Qq).transpose()
    arrays['incoming_terminal_classical_time_covector'] = arb_mat([[classical_density-pi_v]])
    # The following is the current finite-element coefficient model, not a
    # claim about a complete incoming/C2 history or its physical interpolation error.
    x = restore(core, 'log_radius').entries()
    h = restore(core, 'proper_durations').entries()
    dx = restore(core, 'log_radius_first_73')
    dh = restore(core, 'proper_duration_first_73')
    zeta = zeta_first(x, h, dx, dh, coefficient=arb(float(59/30)))
    arrays['current_C2_prefix_zeta_value'] = arb_mat([[zeta['value']]])
    for k in ('first', 'coefficient_first', 'duration_first'):
        arrays['current_C2_prefix_zeta_'+k+'_73'] = zeta[k]
    for z in (shared, local, core, frame):
        z.close()
    sources = [Path(__file__), ROOT/'src/bhsm/interface/gate7_current_action.py',
               ROOT/'src/bhsm/interface/arb_heat_pencil_contractions.py',
               ROOT/'src/bhsm/interface/arb_zeta_contractions.py',
               ROOT/'src/bhsm/interface/heat_zeta_mixed_boundary_launch.py',
               ROOT/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py',
               ROOT/'theory/n12_finite_endpoint_zero_source_force_functional.md',
               ROOT/'docs/GATE7_CURRENT_CALCULATION_SCOPE.md']
    for folder in (SHARED, LOCAL, CORE, FRAME):
        sources.extend([folder/'arrays.npz', folder/'report.json'])
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    report = dict(
        status='CURRENT_SUBSYSTEM_ADJOINT_AND_SIGNED_ZETA_CONTRACTIONS_REPLAYED',
        base_commit='034310b64080a0c71736c183c3e33b95d69ec6ec',
        local_base_SHA256=base.digest,
        local_subsystem_replays=local_replays,
        current_C2_prefix_zeta_value=scalar(zeta['value']),
        current_C2_prefix_zeta_first=bound(zeta['first']),
        current_C2_prefix_zeta_coefficient_first=bound(zeta['coefficient_first']),
        current_C2_prefix_zeta_duration_first=bound(zeta['duration_first']),
        local_boundary_split_rounding_replay=bound(arrays['frozen_split_boundary_minus_unsplit_zeta']),
        incoming_terminal_momentum_pullback=bound(arrays['incoming_terminal_momentum_pullback_66']),
        incoming_terminal_classical_time_covector=scalar(classical_density-pi_v),
        classical_boundary_reduction=dict(
            identity='D integral L_cl dt = [pi*dq_total+(L_cl-pi*v)*dt]_ends + integral [(L_cl,q-D_t pi)*dq_fixed_time+L_cl,m*dm_fixed_time] dt',
            evaluated='Current incoming terminal pi*Qq and L_cl-pi*v only',
            unevaluated='Other endpoint, moving endpoint time, and contracted Euler/multiplier residual',
            caveat='The attached-action flow is not assumed stationary for L_classical after vacuum subtraction'),
        signed_cancellation=dict(
            equation='Gamma_attached_zeta-Gamma_SM_zeta+Gamma_heat = Gamma_classical+Gamma_heat',
            owner='Same -c*N/R term, same c=binary64(59/30), d_tau=N*d_t, same coefficient/duration realization',
            derivatives='Cancellation holds before q/H/B contraction, including moving duration and internal/normal response',
            no_history_heat_zeroing=True,
            split_sector_rounding='Saved binary64 sector shares replayed separately; they do not define a second vacuum functional'),
        representation_scope='New exact contraction algebra and frozen-packet numerical applications; no complete current action realization supplied',
        q66=None, H66_u=None, B66x73_v=None,
        root_solved=False, root_certificate=False,
        physical_history_interpolation_error=None,
        full_graded_heat_error=None,
        uniform_neighborhood_error=None,
        action_producers_run=False, prefix_propagated=False,
        complete_current_force_evaluated=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    ledger = dict(
        authority='docs/GATE7_CURRENT_CALCULATION_SCOPE.md',
        rows=[
            dict(input='fixed Q66 and reset frame', classification='NECESSARY', retained='frozen source hashes'),
            dict(input='124 local normal variables', classification='SLAVED', retained='directional/adjoint solve, frozen current response'),
            dict(input='attached vacuum and prescribed zeta subtraction', classification='REDUNDANT', retained='one shared functional identity; subtract before support'),
            dict(input='incoming classical action', classification='HISTORY-COMPRESSIBLE', retained='terminal covector evaluated; other endpoint and contracted Euler/multiplier residual retained'),
            dict(input='joint graded heat', classification='HISTORY-COMPRESSIBLE', retained='pencil/transfer trace contractions including interior spectrum; current complete coefficients still unsupplied'),
            dict(input='current C2 finite prefix', classification='CHILD-SPECIFIC', retained='frozen coefficient/duration packet; finite-prefix contractions only'),
            dict(input='fixed external data', classification='ENVIRONMENT-SPECIFIC', retained='J_ext=0; all internal contact/transport retained'),
        ],
        next_contraction=dict(
            existing_obligation='Projected same-action force / coupled KKT realization',
            consumed_term='Q66^T D Gamma_classical + Q66^T D Gamma_heat after common normal elimination',
            smallest_representation='Classical endpoint plus contracted Euler/multiplier residual and joint heat trace with owned endpoint/domain errors',
            why_endpoint_packet_insufficient='Endpoint density and a local 124-variable solve do not determine either integrated contraction',
            full_history_storage_required=False),
        complete_q66_evaluated=False)
    (out/'BHSM_SUFFICIENT_STATE_LEDGER.json').write_bytes(encoded(ledger))
    print(json.dumps({k:report[k] for k in ('status','local_subsystem_replays','current_C2_prefix_zeta_value','current_C2_prefix_zeta_first')}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    calculate(p.parse_args().out)
