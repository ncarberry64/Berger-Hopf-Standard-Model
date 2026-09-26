"""Frozen center algebra only. Fail closed on reaction replay; no producers."""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

from checkpoint_n12_gate7_66d_tangent_binding import (
    ROOT, FIXED, amat, mid, frob, bound, digest, encoded,
)

CAPSULE = ROOT/'artifacts/flagship_integration/gate7_66d_checkpoint_20260926'
OUTPUT = ROOT/'artifacts/flagship_integration/gate7_8reaction_center_20260926'
DIRECT = OUTPUT/'source/BHSM_GATE7_STAGEB_DIRECT_INTERFACE_20260925_163714.npz'


def block(a, rows, cols):
    """Keep Arb radii when selecting blocks."""
    return arb_mat([[a[i,j] for j in cols] for i in rows])


def identity(n):
    return arb_mat(np.eye(n, dtype=int).tolist())


def rank_certificate(a):
    """Certify column independence of a stored matrix via a Gram inverse."""
    gram = a.transpose()*a
    residual = frob(identity(a.ncols())-gram.inv()*gram)
    return dict(columns=a.ncols(), gram_inverse_residual=bound(identity(a.ncols())-gram.inv()*gram),
                full_column_rank=bool(residual<1))


def action_hessian_lift(tangent, hessian, interface):
    """Reuse the Stage-B Hessian right inverse, without assuming positivity."""
    restricted = tangent.transpose()*hessian*tangent
    response = restricted.solve(interface.transpose())
    return restricted, response*(interface*response).inv()


def calculate():
    ctx.prec = 512
    sources = {}
    def verify(path, expected):
        actual = digest(path)
        if actual != expected:
            raise ValueError('frozen hash mismatch: '+str(path))
        sources[str(path.relative_to(ROOT))] = actual
    receipt = json.loads((CAPSULE/'reproduction.json').read_bytes())
    for name, record in receipt.items():
        verify(CAPSULE/name, record['SHA256'])
    mr = json.loads((CAPSULE/'newton/report.json').read_bytes())
    for path, expected in mr['source_SHA256'].items():
        verify(ROOT/path, expected)
    br = json.loads((CAPSULE/'binding/report.json').read_bytes())
    verify(ROOT/FIXED, br['source_SHA256'][str(ROOT/FIXED)])
    verify(DIRECT, '8005D5060E631EB9A7C65C42CF3ECFD64B2CE7A0C1900E44762CF9AD81278B10')
    for path in (Path(__file__), OUTPUT/'source/bhsm_gate7_stageB_direct_interface.py'):
        sources[str(path.relative_to(ROOT))] = digest(path)
    with np.load(CAPSULE/'BHSM_GATE7_STAGEB_RANK_REFINEMENT_20260925_173630.npz') as z:
        A = amat(z['node_014_R23'])
        Z = amat(z['node_014_child_coeff_null_73x66'])
    with np.load(DIRECT) as d:
        T = amat(d['node_014_constraint_tangent_action'])
        H = amat(d['node_014_H_action_98x98'])
    adjudication = json.loads((CAPSULE/'BHSM_GATE7_STAGEB_FINAL_NUMERICAL_ADJUDICATION_20260925_180354.json').read_bytes())
    rows = adjudication['rows'][1]['rowwise']
    scales = np.array([row['fixed_scale'] for row in rows])
    # Historical fixed row normalization; no new threshold or Euclidean lift.
    An = amat(np.diag(1/scales))*A
    HT, L = action_hessian_lift(T,H,An)
    with np.load(CAPSULE/'binding/arrays.npz') as b:
        X = amat(b['node_014_fixed_into_physical'])
        expected_s = amat(b['node_014_child_augmented'][73:74])
        family = b['node_014_family']
        launch = amat(b['node_014_launch_state'])
    with np.load(ROOT/FIXED) as f:
        flow_s = f['exact_endpoint_augmented_rates'][14,98]/1e-7
    graph = launch.transpose().solve(amat(np.r_[family[73],flow_s][:,None])).transpose()
    P = identity(74)
    state = X*arb_mat([[Z[i,j] if j<66 else L[i,j-66] for j in range(73)] for i in range(73)])
    for i in range(73):
        for j in range(73):
            P[i,j] = state[i,j]
    Pinv = P.inv()
    # Explicit dual residual coordinates, not an asserted boundary equation.
    test = Pinv.transpose()
    with np.load(CAPSULE/'newton/M_13.npz') as z:
        M = amat(z['M_13'])
    N = test.transpose()*M*P
    pp = block(N,range(66),range(66))
    pq = block(N,range(66),range(66,74))
    qp = block(N,range(66,74),range(66))
    qq = block(N,range(66,74),range(66,74))
    inv = qq.inv()
    proposed_inverse = amat(mid(inv))
    left = identity(8)-proposed_inverse*qq
    right = identity(8)-qq*proposed_inverse
    full_rank = bool(frob(left)<1)
    if not full_rank:
        raise ValueError('reaction block has no validated inverse: stop before slaving')
    D = -inv*qp
    Db = block(D,range(7),range(66))
    Ds = block(D,[7],range(66))
    child_error = arb(br['nodes'][1]['child_reprojection_error']['exact_upper'])
    gram_error = arb(br['nodes'][1]['gram_error_upper_physical'])
    descriptor_allowance = frob(graph)*child_error/(1-gram_error).sqrt()
    # Lower bound the exact stored-coefficient replay discrepancy.
    descriptor_difference = sum((v*v for v in (Ds-expected_s).entries()),arb(0)).sqrt()
    expected = arb_mat([[arb(0) if i<7 else expected_s[0,j] for j in range(66)] for i in range(8)])
    expected_residual = qp+qq*expected
    boundary_error = An*Z+An*L*Db
    singular = np.linalg.svd(mid(qq),compute_uv=False)
    bsingular = np.linalg.svd(mid(boundary_error),compute_uv=False)
    arrays = dict(child_basis_fixed=mid(Z), interface_raw=mid(A), interface_normalized=mid(An),
        interface_scales=scales, action_restricted_Hessian=mid(HT), boundary_complement_fixed=mid(L),
        child_basis_physical=mid(X*Z), boundary_complement_physical=mid(X*L),
        trial_transform=mid(P), test_transform=mid(test), trial_transform_inverse=mid(Pinv),
        descriptor_proof_direction=np.eye(74)[:,73],
        M_pp=mid(pp), M_pq=mid(pq), M_qp=mid(qp), M_qq=mid(qq), M_qq_inverse=mid(inv),
        Dphi_0_candidate=mid(D), expected_descriptor_proof_row=mid(expected_s),
        expected_reaction_residual=mid(expected_residual), boundary_replay_error=mid(boundary_error))
    report = dict(
        status='STOP_CENTER_REACTION_REPLAY_FAILED', node=14, interval=13,
        source_SHA256=sources, precision_bits=512,
        coordinate_authority='Algebraic dual coordinates of the existing shooting residual; NOT identified with Stage-B boundary/descriptor residual equations.',
        lift_formula='H_T=T^T H_action T; A_n=diag(1/frozen_scale) R23; L=H_T^-1 A_n^T (A_n H_T^-1 A_n^T)^-1',
        normalization='Seven boundary coordinates are interface residual divided by the frozen final-adjudication row scales.',
        interface_order=[row['label'] for row in rows],
        descriptor_trial_scale=1e-7, descriptor_test_scale=1e6,
        transformation='trial P=diag(X[Z,L],1); test=P^-T; N=P^-1 M_13 P. The original 1e-7/1e6 frames remain outside these coefficient transforms.',
        ranks=dict(child=rank_certificate(Z), boundary=rank_certificate(L), combined=rank_certificate(state), reaction=8),
        child_interface_residual=bound(An*Z), boundary_interface_identity_error=bound(An*L-identity(7)),
        action_orthogonality_residual=bound(Z.transpose()*HT*L),
        transformation_condition_2_diagnostic=float(np.linalg.cond(mid(P))),
        matrix_roundtrip_error=bound(P*N*Pinv-M),
        stored_transform_roundtrip_error=bound(amat(mid(P))*amat(mid(N))*amat(mid(Pinv))-M),
        Mqq_singular_values_diagnostic=singular.tolist(), Mqq_sigma_min_diagnostic=float(singular[-1]),
        Mqq_sigma_max_diagnostic=float(singular[0]), Mqq_condition_2_diagnostic=float(singular[0]/singular[-1]),
        Mqq_determinant=str(qq.det()), full_M13_condition_2=mr['condition_2'],
        inverse_left_residual=bound(left), inverse_right_residual=bound(right),
        slaving_equation_replay_error=bound(qq*D+qp),
        expected_fixed_environment_boundary_rows='Zero in the frozen null directions, with explicit A_n Z residual retained.',
        boundary_reaction_row_norms_diagnostic=np.linalg.norm(mid(Db),axis=1).tolist(),
        boundary_replay_operator_norm_diagnostic=float(bsingular[0]),
        boundary_replay_error=bound(boundary_error),
        descriptor_expected_row_norm_diagnostic=float(np.linalg.norm(mid(expected_s))),
        descriptor_candidate_row_norm_diagnostic=float(np.linalg.norm(mid(Ds))),
        descriptor_replay_difference_lower=str(descriptor_difference.lower().fmpq()),
        descriptor_replay_difference_diagnostic=float(descriptor_difference.mid()),
        descriptor_reprojection_allowance_upper=str(descriptor_allowance.upper().fmpq()),
        descriptor_reprojection_allowance_diagnostic=float(descriptor_allowance.upper()),
        descriptor_replay_exceeds_stored_reprojection_allowance=bool(descriptor_difference>descriptor_allowance),
        expected_full_reaction_equation_residual=bound(expected_residual),
        Case_B_child_reprojection_allowance=br['nodes'][1]['child_reprojection_error'],
        first_missing_object='Owner-bound identity linking seven fixed-environment boundary residuals and the causal descriptor graph to the chosen eight shooting-residual equations, including the left-endpoint/history forcing derivative. M_13 alone is only the right-endpoint shooting partial.',
        source_uncertainty_scope='Arb bounds certify algebra on frozen binary64 inputs and the retained Case-B allowance. Stage-B finite-difference uncertainty and physical M variation are not promoted to rigorous interval authority.',
        center_slaving_validated=False, nonlinear_attempted=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
    )
    return report, arrays


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    report,arrays=calculate()
    args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO()
    np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue())
    report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','Mqq_condition_2_diagnostic','descriptor_replay_difference_diagnostic','descriptor_reprojection_allowance_diagnostic','boundary_replay_operator_norm_diagnostic')},indent=2))


if __name__=='__main__':
    main()
