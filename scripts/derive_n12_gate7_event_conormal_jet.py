"""Complete the native event contribution without selecting a seam embedding.

Consume frozen parent-sector g/H; compute only the new contracted D3 needed
for the configuration lift. This is a native point jet, not a 7x73 certificate.
"""
import argparse
import ast
import json
import math
from pathlib import Path
import numpy as np
from flint import arb, arb_mat, ctx
import derive_n12_gate7_parent_sector_jets as s
from checkpoint_n12_gate7_66d_tangent_binding import bound, digest, encoded
from diagnose_n12_gate7_eight_reaction_center import block, identity

r = s.r
A = r.A
BASE = r.center.BASE / 'gate7_parent_sectors_20260927'
OWNERS = {
    'aether_n3_required_child_cauchy_flux_v17_93.py': ['_canonical_pair', 'required_child_cauchy_flux'],
    'aether_n3_child_constraint_cauchy_match_v17_94.py': ['_metric_radial_flux_covector'],
    'aether_n3_complete_child_chart_reconstruction_v18_24.py': ['_child_rows', 'complete_child_chart_reconstruction'],
    'aether_n3_constraint_solved_orbit_v16_08.py': ['exact_euler_dirac_acceleration'],
    'aether_cross_resolution_reconnaissance_v21_35.py': ['_canonical_pair_at_order', '_child_rows_at_order'],
}


def calculate(out):
    ctx.prec = 512
    prior = json.loads((BASE / 'report.json').read_bytes())
    if digest(BASE / 'arrays.npz') != prior['arrays_SHA256']:
        raise ValueError('frozen native packet changed')
    a = r.load(BASE / 'arrays.npz')
    Y, weights = a['parent_center'], a['weights']
    H = r.mat(a['hessian_owner'])
    U = arb_mat(98, 98)
    for i in range(98): U[i, i] = 1 / weights[i]
    B, signs, t, sech = r.attachment(Y[:37])
    dB = r.attachment_variation(r.arr(U), signs, t, sech)
    K, L, target = r.kkt(H, B, 0)
    # Only maps and a new contracted third derivative; no g/H producer rerun.
    with r.center.sparse.use_optimized_mixed(A), r.center.factored.use_ball_factored_integrand(A, Y):
        maps = [A._dense_mapping(A._integrand(Y, n, 0).maps) for n in range(A.POINTS)]
        eye = r.zeros((98, 98))
        for i in range(98): eye[i, i] = 1
        lq, lm = r.components(L, 0)
        legs = np.concatenate((lq + lm, lq), axis=1)
        third = np.asarray(A._contracted_action(Y, [eye[:, :, None, None],
            legs[:, None, :, None], r.arr(U)[:, None, None, :]], maps), dtype=object)
    KL = r.zeros((63, 2, 98))
    for k in range(98):
        KL[:37, :, k] = third[:37, :2, k]
        KL[39:, :, k] = third[74:, 2:, k]
        db = r.mat(dB[:, :, k])
        KL[:37, :, k] += r.arr(db.transpose() * block(L, [37, 38], range(2)))
        KL[37:39, :, k] = r.arr(db * block(L, range(37), range(2)))
    DL = -K.solve(r.mat(KL.reshape(63, 196)))
    sk = [arb((-1)**(j+1)) for j in range(12)]
    uq = sum((Y[1+j] * sk[j] for j in range(12)), arb(0))
    wq = sum((Y[13+j] * signs[j] for j in range(12)), arb(0))
    vq = sum((Y[25+j] * signs[j] for j in range(12)), arb(0))
    lapse = sum((Y[74+j] * sk[j] for j in range(12)), arb(0)).exp()
    radius = arb(float(A.RADIUS0)) * Y[0].exp()
    root2 = arb(math.sqrt(2.0))
    aa, bb, cc = radius*(uq+vq).exp()/root2, radius*(uq-vq).exp()/root2, radius*(uq+wq).exp()
    pref = 3*lapse*aa**3*bb**3/cc
    raw = arb_mat(63, 1); logarithm = arb_mat(1, 98); logarithm[0, 0] = 5
    for j in range(12):
        raw[25+j, 0] = 2*pref*signs[j]
        logarithm[0, 1+j] = 5*sk[j]
        logarithm[0, 13+j] = -signs[j]
        logarithm[0, 74+j] = sk[j]
    draw = raw * logarithm * U
    value = L.transpose() * raw
    direct = L.transpose() * draw
    adjoint = L.transpose() * draw
    eta = K.solve(raw)
    lift_part = arb_mat(2, 98)
    for k in range(98):
        dl = arb_mat([[DL[i, j*98+k] for j in range(2)] for i in range(63)])
        d = dl.transpose() * raw
        corr = eta.transpose() * r.mat(KL[:, :, k])
        for j in range(2):
            direct[j, k] += d[j, 0]
            lift_part[j, k] = d[j, 0]
            adjoint[j, k] -= corr[0, j]
    replay = direct - adjoint
    if not all(v.contains(0) for v in replay.entries()):
        raise ArithmeticError('event conormal derivative replay failed')
    native7 = arb_mat(r.mat(a['native_trace_momentum_jet']).tolist() + direct.tolist())
    r.save_arrays(out/'arrays.npz', dict(native_event_7x98=native7,
        event_conormal=value, event_conormal_derivative=direct,
        conormal_lift_contribution=lift_part, conormal_covector_contribution=L.transpose()*draw,
        common_configuration_K=K, common_configuration_lift=L,
        common_configuration_lift_derivative=DL, adjoint_direct_replay=replay))
    provenance = {}
    for filename, names in OWNERS.items():
        path = r.ROOT/'src/bhsm/interface'/filename
        source = path.read_text(encoding='utf-8'); lines = source.splitlines()
        provenance[str(path)] = dict(SHA256=digest(path), functions={
            f.name: dict(start=f.lineno, end=f.end_lineno, text='\n'.join(lines[f.lineno-1:f.end_lineno]))
            for f in ast.parse(source).body if isinstance(f, ast.FunctionDef) and f.name in names})
    report = dict(status='CANONICAL_DYNAMIC_FLUX_OWNER_AND_NATIVE_EVENT_SEVEN_ROW_JET_DERIVED',
        owner_equation='R_flux=DP_child[X_child]-F_child+Gamma_child+Gamma_event',
        event_derivative='D Gamma_event[u]=(DLq[u])^T radial + Lq^T D radial[u]',
        child_derivative='D2P_child[X_child,u]+DP_child[DX_child u]-DF_child[u]+D Gamma_child[u]',
        event_momentum_rate_added=False, dynamic_flux_owner_exists=True,
        native_response_shape=[7,98], material_response_7x73_derived=False,
        point_key='frozen parent-sector parent_center; historical reset center_state[:98]',
        current_environment_identified=False, fixed_environment_variation=0,
        new_environment_inputs=0, finite_difference_used=False,
        frozen_gradient_hessian_reused=True, frozen_scientific_producers_rerun=False,
        new_calculation='configuration-lift contracted D3 at the same stored native point',
        replay=dict(adjoint_direct=bound(replay), lift=bound(K*L-target),
                    differentiated_lift=bound(K*DL+r.mat(KL.reshape(63,196))),
                    inverse=bound(K*K.inv()-identity(63))),
        derivative_norm=bound(direct), lift_contribution_norm=bound(lift_part),
        radial_contribution_norm=bound(L.transpose()*draw),
        provenance=provenance,
        source_SHA256={str(p):digest(p) for p in (Path(__file__), Path(r.__file__),
            Path(A.__file__), Path(r.center.sparse.__file__), Path(r.center.factored.__file__),
            BASE/'arrays.npz', BASE/'report.json', BASE/'role_scope.json')},
        arrays_SHA256=digest(out/'arrays.npz'),
        remaining_composition='fixed-environment material/seam map, explicit frame terms, and base-point binding',
        Gate7_closed=False, FULL_BHSM_COMPLETE=False, tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps(dict(status=report['status'], replay=report['replay']), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(); args.out.mkdir(parents=True, exist_ok=False); calculate(args.out)
