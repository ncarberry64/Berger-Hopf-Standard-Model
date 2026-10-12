"""Apply original reset rows to supplied local normal trial directions."""
from __future__ import annotations
import numpy as np


def frequency_master_trial_lifts(frequency_taylor,ordering,*,left=False):
    """Restore original504 x/v/y directions through quadratic frequency.

    The local polynomial uses x(omega), y(omega), with v_right=i*omega*x
    and v_left=-i*omega*x. Coefficients are Taylor coefficients. No
    conjugation, projection, fitted mode or source-domain correction enters.
    """
    a=np.asarray(frequency_taylor,complex);order=np.asarray(ordering)
    if (a.ndim!=2 or a.shape[0]<292 or a.shape[1]!=3 or order.shape!=(504,)
            or not np.issubdtype(order.dtype,np.integer)
            or not np.array_equal(np.sort(order),np.arange(504))
            or not np.isfinite(a).all()):
        raise ValueError('complete paired normal Taylor coefficients and original504 permutation required')
    phase=a[:292];ordered=np.zeros((504,3),complex)
    ordered[:212]=phase[:212];ordered[424:]=phase[212:]
    ordered[212:424,1:]=(-1j if left else 1j)*phase[:212,:2]
    master=np.empty_like(ordered);master[order]=ordered
    return master


def kinetic_master_trial_lifts(phase_lift,ordering):
    """The supplied true-Lyy trial varies v/y at held x, not position."""
    a=np.asarray(phase_lift,complex).reshape(-1);order=np.asarray(ordering)
    if a.shape!=(292,)or order.shape!=(504,)or not np.isfinite(a).all():
        raise ValueError('complete v212/y80 kinetic trial and original504 permutation required')
    ordered=np.r_[np.zeros(212,complex),a];master=np.empty_like(ordered);master[order]=ordered
    return master[:,None]


def original_reset_trial_application(jacobian,lifts,groups):
    """Keep every original reset row and identify group-wise violations.

    J*r_trial is a perturbation-domain test at the supplied candidate. It
    is distinct from the candidate's nonlinear residual and from a
    physical mode or Pauli error. No dependent Ward row is dropped.
    """
    J=np.asarray(jacobian,complex);D=np.asarray(lifts,complex)
    if J.shape!=(226,504)or D.ndim!=2 or D.shape[0]!=504 or not np.isfinite(J).all()or not np.isfinite(D).all():
        raise ValueError('all original226 Jacobian rows and same504 trial directions required')
    response=J@D;summary={}
    membership=[]
    for name,value in groups.items():
        ids=np.asarray(value['indices']if isinstance(value,dict)else value,int)
        if ids.ndim!=1 or not len(ids)or np.any(ids<0)or np.any(ids>=226):
            raise ValueError('complete original group incidence required')
        membership.extend(ids.tolist());rows=response[ids]
        summary[name]=dict(indices=ids.tolist(),max_abs_by_coefficient=np.max(abs(rows),axis=0).tolist(),
            norm_by_coefficient=np.linalg.norm(rows,axis=0).tolist())
    if sorted(membership)!=list(range(226)):
        raise ValueError('reset group incidence must cover every original row exactly once')
    return dict(master_trial_lifts=D,all_original226_trial_rows=response,groups=summary,
        max_abs_by_coefficient=np.max(abs(response),axis=0),
        norm_by_coefficient=np.linalg.norm(response,axis=0),
        original_rows_projected_or_deleted=0,trial_domain_compatibility_is_not_base_convergence=True)
