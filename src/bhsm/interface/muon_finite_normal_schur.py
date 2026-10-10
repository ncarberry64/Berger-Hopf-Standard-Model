"""One normal response of a recorded finite, real action Hessian.

This is a congruence-scaled indefinite block solve.  Multipliers, Gauss
coordinates and scalar coefficients remain in the internal block.  The
normal coordinate is a supplied representation index, not a selected
mechanical mode.  The result is neither a physical impedance nor a
formation/cutoff condition.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np


def normal_schur_application(hessian, *, normal_index=61, rank_tolerance=1e-11):
    """Solve K delta=-B and return D+B^T delta in real coefficient duals.

    For a numerically singular block the discarded source and residual are
    exported.  The value is then only the retained-range contraction: the
    routine never identifies it with a uniquely defined full response.
    """
    h=np.asarray(hessian,float)
    if h.ndim!=2 or h.shape[0]!=h.shape[1] or h.shape[0]<2 or not np.isfinite(h).all():
        raise ValueError('a finite square real action Hessian is required')
    if type(normal_index) is not int or not 0<=normal_index<len(h):
        raise ValueError('an explicit represented normal coordinate is required')
    if not np.isfinite(rank_tolerance) or not 0<rank_tolerance<1:
        raise ValueError('a finite relative numeric rank cutoff is required')
    symmetry_defect=float(np.max(abs(h-h.T)))
    symmetry_scale=max(float(np.max(abs(h))),1.)
    if symmetry_defect>1e-10*symmetry_scale:
        raise ValueError('the supplied rows are not a symmetric real action Hessian')
    h=(h+h.T)/2
    internal=np.delete(np.arange(len(h)),normal_index)
    k=h[np.ix_(internal,internal)];b=h[internal,normal_index];d=float(h[normal_index,normal_index])
    scale=1/np.sqrt(np.maximum(np.max(abs(k),axis=1),1e-30))
    eigenvalues,u=np.linalg.eigh(scale[:,None]*k*scale[None,:])
    cutoff=float(rank_tolerance*max(float(np.max(abs(eigenvalues))),1e-30))
    active=abs(eigenvalues)>cutoff
    rhs=scale*b;projected=u[:,active].T@rhs
    delta=-scale*(u[:,active]@(projected/eigenvalues[active]))
    # Refine against the original dual rows, using the same retained range.
    # No new rank choice or constraint elimination is made in refinement.
    for _ in range(2):
        remainder=scale*(k@delta+b)
        delta-=scale*(u[:,active]@((u[:,active].T@remainder)/eigenvalues[active]))
    residual=k@delta+b
    discarded=u[:,~active].T@rhs
    response=d+float(b@delta)
    lifted=np.zeros(len(h));lifted[normal_index]=1.;lifted[internal]=delta
    return dict(internal_indices=internal,normal_index=normal_index,internal_hessian=k,
        source_B=b,normal_D=d,internal_response=delta,linear_residual=residual,
        scaled_linear_residual=scale*residual,discarded_scaled_source=discarded,
        internal_congruence_scale=scale,scaled_eigenvalues=eigenvalues,
        rank=int(np.count_nonzero(active)),nullity=int(np.count_nonzero(~active)),
        rank_tolerance=float(rank_tolerance),numeric_eigenvalue_cutoff=cutoff,
        symmetry_defect=symmetry_defect,source_norm=float(np.linalg.norm(b)),
        linear_residual_norm=float(np.linalg.norm(residual)),
        relative_linear_residual=float(np.linalg.norm(residual)/max(np.linalg.norm(b),1e-30)),
        response_z=response,lifted_direction=lifted,
        quadratic_pairing=float(lifted@h@lifted),
        identity_defect=float(lifted@h@lifted-response-delta@residual),
        retained_range_only=bool(np.any(~active)),positive_minimum_assumed=False,
        multipliers_or_Gauss_eliminated=False)


def materialize_normal_response(application_directory, output_directory, *, normal_index=61):
    """Consume recorded final Hessian and preserve exact input-byte receipts."""
    from .muon_parent_retarded_hypercharge import _deterministic_npz
    source=Path(application_directory);output=Path(output_directory)
    if output.exists():
        raise FileExistsError('preserve prior applications; choose a new output directory')
    receipt_bytes=(source/'result.json').read_bytes();data_bytes=(source/'application.npz').read_bytes()
    receipt=json.loads(receipt_bytes)
    data_hash=sha256(data_bytes).hexdigest()
    if data_hash!=receipt['numerical_sha256']:
        raise ValueError('recorded action Hessian bytes disagree with their producer receipt')
    with np.load(source/'application.npz',allow_pickle=False) as data:
        h=data['updated_hessian'];base_residual=data['updated_residual'];coefficients=data['updated_coefficients']
    result=normal_schur_application(h,normal_index=normal_index)
    arrays={k:v for k,v in result.items() if isinstance(v,np.ndarray)}
    arrays.update(recorded_hessian=h,recorded_base_residual=base_residual,recorded_coefficients=coefficients)
    output.mkdir(parents=True);_deterministic_npz(output/'application.npz',arrays)
    metadata={k:v for k,v in result.items() if not isinstance(v,np.ndarray)}
    metadata.update(scope='EVALUATED_REDUCED_FINITE_PARAMETER_TRIAL_NORMAL_RESPONSE',
        pairing='real coefficient action duals; no additional factor2 or Gram inserted',
        normal_coordinate='index61: represented compact material-normal coefficient of the consumed producer',
        internal_coordinates='all remaining geometry,24 multiplier,gauge includingAt/Ar,and Higgs coefficients',
        equation='K_internal delta=-B_normal; z=D_normal+B_normal^T delta',
        action_parameters=receipt['action_parameters'],
        base_residual_norm=float(np.linalg.norm(base_residual)),
        finite_base_scope=receipt['scope'],finite_base_iteration_status=receipt['iteration_status'],
        unprojected_constraint_density_max=receipt.get('final_unprojected_constraint_density_max'),
        contact_provenance='recorded same-action full Hessian: cap metric/normal/velocity, full5 Maxwell curvature/shift/Gram, intrinsic Higgs measure/connection/quartic; derivative-form contacts included once',
        sector_hessians_in_source_archive='sector Hessians are initial-iterate diagnostics; no final-sector split is inferred from them',
        base_action_input_hashes=receipt['input_hashes'],
        consumed_application_sha256=data_hash,consumed_receipt_sha256=sha256(receipt_bytes).hexdigest(),
        producer_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        numerical_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        physical_mode_selected=False,physical_impedance_identified=False,formation_zero_identified=False,
        stationary_E1_claim=False,physical_Pauli_contraction=False,
        finite_residual_is_pointwise_action_solution=False,
        error_scope='floating-point finite block application; numeric rank and residual are not a continuum or rigorous enclosure')
    (output/'result.json').write_text(json.dumps(metadata,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return metadata


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(materialize_normal_response(args.application,args.output),sort_keys=True))
