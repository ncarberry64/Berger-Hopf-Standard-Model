"""Outward arithmetic bounds for an already evaluated finite normal response.

This certifies exact stored real coefficient matrices.  It does not bound
Galerkin truncation, the nonlinear base defect, physical mode selection,
cutoff matching, or a Pauli contribution.  The indefinite internal KKT
block is not assumed positive or replaced by its smallest eigenvector.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np


def certify_frozen_normal_contraction(k, b, d, delta, *, precision_bits=192,
                                      inverse_preconditioner=None):
    """Bound z=D-B^T K^(-1)B with exact stored symmetric K and source B.

    Q is a computed inverse preconditioner, never a physical input.  Arb
    verifies ||I-QK||_F<1, hence ||K^(-1)||_2<=||Q||_F/(1-||I-QK||_F).
    For r=K*delta+B and symmetric K, the residual-corrected contraction is
    D+B^T delta+delta^T r.  Its exact error is -r^T K^(-1)r, bounded by
    ||K^(-1)||_2 ||r||_2^2.  Every product is evaluated with outward balls.
    """
    from flint import arb, arb_mat, ctx

    k,b,delta=(np.asarray(value,float) for value in (k,b,delta))
    if (k.ndim!=2 or k.shape[0]!=k.shape[1] or len(k)==0
            or b.shape!=(len(k),) or delta.shape!=b.shape
            or not all(np.isfinite(value).all() for value in (k,b,delta))
            or not np.isfinite(d) or not np.array_equal(k,k.T)):
        raise ValueError('finite exact symmetric stored K and matching real vectors required')
    if type(precision_bits) is not int or precision_bits<96:
        raise ValueError('at least96 bits of outward arithmetic required')
    if inverse_preconditioner is None:
        scale=1/np.sqrt(np.maximum(np.max(abs(k),axis=1),1e-30))
        try:
            inverse_preconditioner=(scale[:,None]*np.linalg.inv(scale[:,None]*k*scale[None,:]))*scale[None,:]
        except np.linalg.LinAlgError as error:
            raise ArithmeticError('no inverse preconditioner for this frozen internal block') from error
    q=np.asarray(inverse_preconditioner,float)
    if q.shape!=k.shape or not np.isfinite(q).all():
        raise ValueError('finite square numerical inverse preconditioner required')
    old_precision=ctx.prec
    ctx.prec=precision_bits
    try:
        def matrix(value):
            return arb_mat([[arb(float(entry)) for entry in row] for row in np.asarray(value)])
        def norm(value):
            return sum((value[i,j]**2 for i in range(value.nrows())
                        for j in range(value.ncols())),arb(0)).sqrt()
        def upper(value):
            return float(np.nextafter(float(value.upper()),np.inf))
        K,Q=matrix(k),matrix(q)
        I=matrix(np.eye(len(k)))
        error=norm(I-Q*K)
        if not error<1:
            raise ArithmeticError('inverse preconditioner fails the verified Neumann test')
        inverse_bound=norm(Q)/(1-error)
        B,X=matrix(b[:,None]),matrix(delta[:,None])
        residual=K*X+B
        rho=norm(residual)
        simple=arb(float(d))+(B.transpose()*X)[0,0]
        center=simple+(X.transpose()*residual)[0,0]
        radius=inverse_bound*rho**2
        low=float(np.nextafter(float((center-radius).lower()),-np.inf))
        high=float(np.nextafter(float((center+radius).upper()),np.inf))
        return dict(scope='CERTIFIED_EXACT_STORED_FINITE_NORMAL_MATRIX_ARITHMETIC',
            precision_bits=precision_bits,dimension=len(k),
            Neumann_preconditioner_defect_upper=upper(error),
            inverse_operator_norm_upper=upper(inverse_bound),
            linear_residual_norm_upper=upper(rho),
            simple_contraction_ball=str(simple),
            residual_corrected_center_ball=str(center),
            quadratic_residual_error_upper=upper(radius),
            response_z_interval=[low,high],
            source_norm_upper=upper(norm(B)),response_norm_upper=upper(norm(X)),
            exact_input_convention='each stored binary64 entry is an exact real number',
            positive_internal_operator_assumed=False,
            physical_impedance_or_mode_identified=False,
            continuum_base_native_or_Pauli_error_enclosed=False)
    finally:
        ctx.prec=old_precision


def materialize_certificate(application, output, *, precision_bits=192):
    source,target=Path(application),Path(output)
    if target.exists():
        raise FileExistsError('preserve earlier evidence; choose a fresh output directory')
    receipt=json.loads((source/'result.json').read_text(encoding='utf8'))
    archive=(source/'application.npz').read_bytes()
    if sha256(archive).hexdigest()!=receipt['numerical_sha256']:
        raise ValueError('normal application bytes disagree with its receipt')
    with np.load(source/'application.npz',allow_pickle=False) as data:
        result=certify_frozen_normal_contraction(data['internal_hessian'],data['source_B'],
            receipt['normal_D'],data['internal_response'],precision_bits=precision_bits)
    result.update(input_archive_sha256=sha256(archive).hexdigest(),
        input_receipt_sha256=sha256((source/'result.json').read_bytes()).hexdigest(),
        producer_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        cap_sector_constraint_density_max=receipt['unprojected_constraint_density_max'],
        inherited_density_scope='historical receipt key unprojected_constraint_density_max stores CAP-only density, not total coupled action residual',
        physical_mode_selected=False,complete_observable=False,
        error_scope='only exact saved normal K,B,D arithmetic; producer discretization/rounding, nonlinear residual and native response excluded')
    target.mkdir(parents=True)
    path=target/'certificate.json'
    path.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',
                    encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--application',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--precision-bits',default=192,type=int)
    args=parser.parse_args()
    print(json.dumps(materialize_certificate(args.application,args.output,
                                            precision_bits=args.precision_bits),sort_keys=True))
