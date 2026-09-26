"""Cheap local implicit-system dimension gate using only frozen Newton blocks."""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import ctx

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, amat, mid, bound, digest, encoded


def calculate():
    ctx.prec=512
    base=ROOT/BASE
    matrix=base/'gate7_66d_checkpoint_20260926/newton/M_13.npz'
    matrix_report=json.loads(matrix.with_name('report.json').read_bytes())
    owner=base/'gate7_full_shooting_owner_20260926'
    owner_report=json.loads((owner/'report.json').read_bytes())
    if digest(matrix)!=matrix_report['arrays_SHA256'] or digest(owner/'arrays.npz')!=owner_report['arrays_SHA256']:
        raise ValueError('frozen block hash changed')
    with np.load(matrix) as z:M=z['M_13']
    with np.load(owner/'arrays.npz') as z:N=z['left_reduced_block']
    # Grant elimination of the endpoint state-normal/boundary variables.
    # One left descriptor remains, and all 74 right coefficients are unknown.
    K=np.column_stack((N[:,73],M))
    aM=amat(M);n=amat(N[:,73:74]);right=-aM.solve(n)
    v=np.r_[1.,mid(right)[:,0]]
    residual=bound(aM*amat(v[1:,None])+n)
    singular=np.linalg.svd(K,compute_uv=False)
    paths=[matrix,matrix.with_name('report.json'),owner/'arrays.npz',owner/'report.json',
        ROOT/'theory/n12_gate7_augmented_fixed_descriptor_newton.md',
        ROOT/'theory/n12_gate7_correlated_descriptor_newton.md',
        ROOT/'scripts/materialize_n12_gate7_augmented_fixed_descriptor_newton_endpoint_candidate.py',
        ROOT/'scripts/audit_n12_gate7_within_seam_constraint_center_obstruction.py',
        ROOT/'scripts/audit_n12_gate7_correlated_descriptor_newton_midpoint_replay.py',
        ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py',Path(__file__)]
    report=dict(status='STOP_LOCAL_INTERNAL_SYSTEM_NOT_SQUARE',
        frozen_base_commit='310035e63baab59d8cf2a941792782cc8f6e0715',
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in paths},
        external_physical_dimension=66,
        internal_ledger=dict(left_state_complement=32,left_descriptor=1,right_augmented_state=99,total=132),
        projected_equation_ledger=dict(left_constraints=25,left_interface=7,right_constraints=25,reduced_shooting=74,total=131),
        full_equation_ledger=dict(left_constraints=25,left_interface=7,right_constraints=25,full_shooting=99,total=156),
        after_granting_state_graphs=dict(unknowns=75,equations=74),
        center_matrix_shape=list(K.shape),center_matrix_definition='K_cut=[N13[:,73] | M13]; columns are left descriptor proof coordinate and all right reduced coordinates',
        numerical_row_rank=int(np.linalg.matrix_rank(K)),nullity=1,
        rank_authority='Frozen invertibility of the 74x74 M13 submatrix implies exact full row rank of the stored K_cut, hence one-dimensional nullspace.',
        nonzero_singular_values_diagnostic=singular.tolist(),
        smallest_nonzero_singular_value_diagnostic=float(singular[-1]),
        injectivity_minimum_gain=0,positive_singular_value_condition_diagnostic=float(singular[0]/singular[-1]),
        invertible_internal_jacobian=False,inverse_replay_residual=None,
        exact_null_formula='(1,-M13^-1 N13 e_s)',stored_null_vector_replay=residual,
        interval_solve_null_replay=bound(aM*right+n),
        null_right_descriptor_proof_component=float(v[-1]),
        null_right_state_coefficient_norm=float(np.linalg.norm(v[1:74])),
        physical_null_interpretation='Vary the left carried descriptor with left state fixed; the right state/descriptor respond through the frozen shooting linearization. One proof unit is 1e-7 physical descriptor units; the direction may be scaled arbitrarily.',
        first_missing_equation='An owner-bound scalar left-descriptor initial/fiber condition, with center and nonlinear authority for this local child family.',
        equation_scope='The owned 25 constraints and seven state-interface rows do not depend on the separately carried descriptor. The shooting descriptor row transports its value. The frozen eigenvalue-minus-descriptor diagnostic is not silently promoted to an additional equation.',
        normal_compatibility_scope='Using all 99 shooting rows plus both endpoint constraint sets gives 156 equations for 132 internal unknowns; 25 normal shooting compatibility identities would be needed to justify a square reduction. Their recorded residuals are not treated as zero.',
        old_Mqq_modified=False,old_Mqq_schur_replay_performed=False,
        old_Mqq_schur_replay_skip_reason='Mandatory non-square-system stop occurs before a square larger internal Schur problem exists.',
        nonlinear_proof_attempted=False,physical_radii_changed=False,scientific_producers_run=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return report,dict(K_cut=K,null_vector=v,left_descriptor_column=N[:,73])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report,arrays=calculate();args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue());report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['status'],report['center_matrix_shape'],report['numerical_row_rank'])
    print('stored null replay:',report['stored_null_vector_replay']['approximate_upper'])


if __name__=='__main__':main()
