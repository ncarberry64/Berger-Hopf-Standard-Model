"""Record the nonlinear lift obligation from frozen inputs; no model producers."""
import argparse
import json
from pathlib import Path

import numpy as np
from flint import arb, ctx

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, amat, bound, digest, encoded, frob
from diagnose_n12_gate7_eight_reaction_center import identity


def calculate():
    ctx.prec=512
    base=ROOT/BASE
    center=base/'gate7_8reaction_center_20260926'
    owner=base/'gate7_full_shooting_owner_20260926'
    tube=base/'gate7_physical_tube_20260924/interval_013/certificate.json'
    shared=base/'gate7_shared_models_20260924'
    inputs=shared/'execution/left_repeat_inputs.json'
    paths=[center/'report.json',center/'arrays.npz',owner/'report.json',owner/'arrays.npz',
           tube,inputs,shared/'manifest.json',
           ROOT/'scripts/regenerate_n12_gate7_shared_site_models.py',
           ROOT/'scripts/materialize_n12_gate7_shared_history_cells.py',Path(__file__)]
    c=json.loads((center/'report.json').read_bytes())
    o=json.loads((owner/'report.json').read_bytes())
    t=json.loads(tube.read_bytes());s=json.loads(inputs.read_bytes())
    manifest=json.loads((shared/'manifest.json').read_bytes())
    if digest(center/'arrays.npz')!=c['arrays_SHA256'] or digest(owner/'arrays.npz')!=o['arrays_SHA256']:
        raise ValueError('frozen center array changed')
    if digest(inputs)!=manifest['files']['execution/left_repeat_inputs.json']['SHA256']:
        raise ValueError('frozen shared-domain input changed')
    if s['radius_exact']!=t['radius_exact'] or not o['center_replay_passes']:
        raise ValueError('inconsistent inherited checkpoint')
    # Read the existing inverse proposal. Do not extract or invert a new block.
    with np.load(center/'arrays.npz') as z:
        Q=amat(z['M_qq']);R=amat(z['M_qq_inverse'])
        inverse_norm_diagnostic=float(np.linalg.norm(z['M_qq_inverse'],2))
    residual=frob(identity(8)-R*Q)
    if not residual<1:raise ValueError('stored inverse replay failed')
    upper=(frob(R)/(1-residual)).upper()
    return dict(status='STOP_MISSING_NONLINEAR_ENDPOINT_HISTORY_LIFT',
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in paths},
        frozen_base_commit='35b37277c5e5590eee992ae2b51dc89cc0a0234b',interval=13,
        physical_radius_order=['longitudinal','transverse'],physical_radius_exact=t['radius_exact'],
        shared_parameter_order=s['parameter_order'],shared_parameter_groups=s['groups'],
        state_symbol_count=150,direction_symbol_count=300,
        center_sigma_min_diagnostic=c['Mqq_sigma_min_diagnostic'],
        center_inverse_operator_norm_diagnostic=inverse_norm_diagnostic,
        stored_center_inverse_norm_upper_exact=str(upper.fmpq()),
        stored_center_inverse_norm_upper_diagnostic=float(upper),
        stored_center_inverse_norm_method='Frobenius proposal norm divided by one minus outward inverse defect; stored binary64 block only',
        stored_center_inverse_defect=bound(identity(8)-R*Q),
        inherited_actual_center_rounding_defect=o['actual_chain_reaction_block_defect'],
        first_missing_object='Owner-bound nonlinear lift (p,q)->(Y13,Y14) into the frozen endpoint groups, with common parameter identity, derivative enclosures and reaction-domain inclusion.',
        required_lift_data=['Y13,Y14 values and first/mixed jets on the same p,q domain',
            'Outward inclusion in the unchanged endpoint longitudinal intervals and transverse Euclidean balls',
            'Owned eight-reaction domain and signed residual at its predictor',
            'Off-center transport of the physical boundary/descriptor row identity and signed flow/rounding defects'],
        evidence_scope='The inspected center-owner and linked shared-rate chain supplies center lift matrices and independent affine endpoint groups, not this nonlinear child/reaction pullback.',
        variation_bound=None,uniform_inverse_bound=None,boundary_self_map_bounds=None,
        descriptor_self_map_bound=None,reaction_domain_radii=None,
        uniform_invertibility_certified=False,self_map_certified=False,nonlinear_slaving_certified=False,
        physical_radius_changed=False,scientific_producers_run=False,center_block_reextracted=False,
        mixed_curvature_reduction_performed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report=calculate()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('xb') as stream:stream.write(encoded(report))
    print(report['status'])
    print('center inverse norm diagnostic:',report['center_inverse_operator_norm_diagnostic'])
    print('center inverse norm upper:',report['stored_center_inverse_norm_upper_diagnostic'])


if __name__=='__main__':main()
