"""Near-tied objective values must not prefer a less stationary solution."""
from copy import deepcopy
import json
import numpy as np
import pytest
from scipy.optimize import OptimizeResult
from bhtracker.inference import _select_multistart


def candidate(residual,jacobian,active=None,success=True):
    jac=np.asarray(jacobian,dtype=float)
    return OptimizeResult(fun=np.asarray(residual,dtype=float),jac=jac,
                          active_mask=np.zeros(jac.shape[1]) if active is None else np.asarray(active),success=success)


def test_roundoff_tie_prefers_stationary_state_independently_of_parameter_units():
    # The first residual has a reducible component. The second has only a
    # last-digit change in the irreducible component, as in an evaluated fit.
    for scale in [1e-6,1.,1e6]:
        away=candidate([1e-7,1.],[[scale],[0.]])
        stationary=candidate([0.,1.+1e-13],[[scale],[0.]])
        assert away.fun@away.fun<stationary.fun@stationary.fun
        selected,receipt=_select_multistart([away,stationary])
        assert selected is stationary and receipt['selected_start']==1


def test_materially_better_likelihood_is_not_overridden_by_stationarity():
    better=candidate([1e-6,1.],[[1.],[0.]])
    worse=candidate([0.,1.001],[[1.],[0.]])
    assert _select_multistart([better,worse])[0] is better


def test_bound_stationarity_uses_feasible_one_sided_gradient():
    boundary_optimum=candidate([1.,1.],[[1.],[0.]],active=[-1])
    feasible_descent_remains=candidate([-1.,1.],[[1.],[0.]],active=[-1])
    assert _select_multistart([feasible_descent_remains,boundary_optimum])[0] is boundary_optimum


def test_failed_lower_minimum_is_not_hidden_by_a_distant_converged_state():
    unresolved=candidate([0.,1.],[[1.],[0.]],success=False)
    converged=candidate([0.,2.],[[1.],[0.]])
    assert _select_multistart([unresolved,converged])[0] is unresolved


def test_invalid_numerical_candidate_cannot_win_or_hide_a_materially_lower_objective():
    valid=candidate([0.,1.],[[1.],[0.]])
    invalid=candidate([0.,1.],[[np.nan],[0.]])
    nonfinite=candidate([np.inf,1.],[[1.],[0.]])
    penalty=candidate([1e8,1e8],[[0.],[0.]])
    selected,receipt=_select_multistart([invalid,nonfinite,penalty,valid])
    assert selected is valid and receipt['numerically_invalid_starts']==[0,1]
    assert receipt['candidate_stationarity'][:2]==[None,None]
    assert receipt['candidate_chi2'][1] is None
    assert json.loads(json.dumps(receipt,allow_nan=False))['candidate_chi2'][1] is None
    # An invalid derivative at a materially better state cannot be discarded
    # while certifying a different, worse minimum.
    invalid.fun=np.array([0.,.5])
    with pytest.raises(ValueError,match='minimum-objective'):
        _select_multistart([invalid,valid])
    with pytest.raises(ValueError,match='finite objective'):
        _select_multistart([nonfinite])


def test_last_digit_objective_order_does_not_change_the_selected_physical_state(monkeypatch):
    import bhtracker.inference as module
    from bhtracker.examples import make_example
    original=module.least_squares;solved=[]
    def record(*args,**kwargs):
        value=original(*args,**kwargs);solved.append(deepcopy(value));return value
    monkeypatch.setattr(module,'least_squares',record)
    data,_=make_example('nearby_motion');baseline=module.fit(data,starts=2)
    minimum=min(float(s.fun@s.fun) for s in solved)
    for direction in [-1,1]:
        pending=iter(enumerate(solved))
        def perturbed(*args,**kwargs):
            i,value=next(pending);value=deepcopy(value)
            target=minimum+direction*(i+1)*1e-11
            value.fun*=np.sqrt(target/float(value.fun@value.fun))
            return value
        monkeypatch.setattr(module,'least_squares',perturbed)
        changed=module.fit(data,starts=2)
        np.testing.assert_array_equal(changed['predictions'],baseline['predictions'])
        assert changed['estimates']==baseline['estimates']
        assert changed['optimizer_selection']['selected_start']==baseline['optimizer_selection']['selected_start']
