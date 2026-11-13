"""Safeguarded residual minimization for all complex canonical action rows.

The trust region is a numerical residual solver. It does not regularize
the action or delete a constraint or a singular direction. All original
rows and named frame reactions are returned, and successful optimizer
termination alone is not accepted as canonical compatibility.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import least_squares


def safeguarded_complex_constitutive(eta, momentum, evaluate, frame, *,
        max_evaluations=80, tolerance=2e-9, checkpoint=None,
        algebraic_target=None, starting_reactions=None):
    eta=np.asarray(eta,complex).copy(); momentum=np.asarray(momentum,complex)
    n=len(momentum); C=np.asarray(frame['named_frame_covectors'],complex)
    Z=np.asarray(frame['literal_generators'],complex); k=len(eta)-n
    if C.shape!=(2,k) or Z.shape!=(k,2) or len(eta)<=2*n:
        raise ValueError('same full complex action and two named central frames required')
    fixed=eta[:n].copy(); reference=eta[n:].copy()
    reaction=np.zeros(2,complex) if starting_reactions is None else np.asarray(starting_reactions,complex)
    target=np.zeros(k-n,complex) if algebraic_target is None else np.asarray(algebraic_target,complex)
    if target.shape!=(k-n,) or reaction.shape!=(2,):
        raise ValueError('complete original algebraic residual target and reactions required')
    def application(z):
        coefficients=np.r_[fixed,z[:k]]; a=evaluate(coefficients)
        g=np.asarray(a['gradient'],complex); D=np.asarray(a['hessian'],complex)[n:,n:]
        r=np.r_[g[n:2*n]-momentum,g[2*n:]-target]
        f=np.r_[r+C.T@z[k:],C@(z[:k]-reference)]
        J=np.block([[D,C.T],[C,np.zeros((2,2),complex)]])
        return coefficients,a,r,f,J
    start=np.r_[reference,reaction]; initial=application(start)
    # Fixed row normalization supplies one consistent numerical merit.
    # Positive variable scales are coordinate magnitudes at the retained
    # starting germ. Neither choice changes the original action equations.
    scale=1/np.maximum(np.max(abs(initial[-1]),axis=1),1.)
    variable_scale=np.maximum(abs(start),1.)
    def realify(z):return np.r_[z.real,z.imag]
    def complexify(x):return x[:k+2]+1j*x[k+2:]
    cache={}; records=[]; invalid_trials=[]; evaluations=0
    def get(x):
        nonlocal evaluations
        if 'x' in cache and np.array_equal(cache['x'],x):
            return cache['app']
        z=complexify(x); evaluations+=1
        a=application(z)
        if any(not np.isfinite(v).all() for v in a[2:]):
            raise FloatingPointError('nonfinite original action derivative')
        cache.update(x=np.asarray(x).copy(),app=a)
        return a
    def fun(x):
        try:return realify(scale*get(x)[3])
        except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError) as exc:
            invalid_trials.append(dict(evaluation=evaluations,reason=str(exc)))
            # The optimizer rejects this inadmissible action chart trial.
            # Infinity is not an evaluated action row and is never saved
            # as a scientific residual or a boundary source.
            return np.full(2*(k+2),np.inf)
    def jac(x):
        coefficients,a,r,f,J=get(x); S=scale[:,None]*J
        record=dict(accepted_iteration=len(records),evaluation=evaluations,
            fixed_merit=float(np.linalg.norm(scale*f)),
            original_constitutive_max=float(np.max(abs(r))),
            momentum_residual_max=float(np.max(abs(r[:n]))),
            algebraic_residual_max=float(np.max(abs(r[n:]))),
            gauge_source_max=float(np.max(abs(Z.T@r))),
            velocity_algebraic_change_norm=float(np.linalg.norm(coefficients[n:]-reference)))
        records.append(record)
        if checkpoint is not None:
            checkpoint(record,coefficients,complexify(x)[k:],a,r,f,J,scale)
        return np.block([[S.real,-S.imag],[S.imag,S.real]])
    result=least_squares(fun,realify(start),jac=jac,method='trf',
        x_scale=np.r_[variable_scale,variable_scale],max_nfev=max_evaluations,
        ftol=1e-13,xtol=1e-13,gtol=None)
    coefficients,a,r,f,J=application(complexify(result.x))
    status=('ORIGINAL_COMPLEX_CONSTITUTIVE_TOLERANCE'
        if np.max(abs(r))<=tolerance and np.max(abs(f[-2:]))<=tolerance
        else 'NUMERICAL_OPTIMIZER_TERMINATED_WITH_ORIGINAL_RESIDUAL')
    return dict(status=status,coefficients=coefficients,action=a,
        original_constitutive_rows=r,framed_rows=f,framed_Jacobian=J,
        frame_reactions=complexify(result.x)[k:],row_scale=scale,
        variable_scale=variable_scale,history=records,invalid_chart_trials=invalid_trials,
        original_momentum_target=momentum,algebraic_target=target,
        literal_generator_image=J[:k,:k]@Z,literal_gauge_source=Z.T@r,
        optimizer_status=int(result.status),optimizer_message=str(result.message),
        total_action_evaluations=evaluations,
        numerical_trust_region_not_action_regularization=True,
        exact_rows_or_numerical_singular_directions_deleted=False,
        fixed_position_defect=coefficients[:n]-fixed)
