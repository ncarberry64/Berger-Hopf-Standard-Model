from copy import deepcopy
from fractions import Fraction
import pytest
from bhsm.interface.history_completion_budget import completion_budget
from bhsm.interface.global_physical_remainder_checkpoint import evaluate, PROOF_FLAGS


def ledger():
    result = completion_budget([.125, .0625], [[.125, 0], [0, .25]],
                               [1, .5], [0, 0], [0, 0])
    result['interval14_debit_count'] = 1
    return result


def certificate():
    return dict(method='GLOBAL_SHARED_PARAMETER_REMAINDER_HESSIAN',
        ledger_SHA256='A', radius_exact=['1', '1/2'], history_intervals=list(range(370)),
        proof_artifact_SHA256='B', kappa_upper_exact=['1/4', '1/4'],
        **dict.fromkeys(PROOF_FLAGS, True))


def test_unknown_is_not_zero_and_targets_are_not_bounds():
    r = evaluate(ledger(), 'A')
    assert r['classification'] == 'INCOMPLETE_REMAINDER_INFORMATION'
    assert all(x['certified_full_lhs_upper'] is None for x in r['inequalities'])
    assert not r['target_is_a_proved_bound']


def test_radial_hessian_bound_controls_value_and_derivative_with_distinct_scaling():
    r = evaluate(ledger(), 'A', certificate())
    assert r['global_physical_contraction_certified']
    assert Fraction(r['inequalities'][0]['certified_full_lhs_upper']['exact']) == Fraction(3, 8)
    assert Fraction(r['inequalities'][1]['certified_full_lhs_upper']['exact']) == Fraction(1, 4)
    assert Fraction(r['inequalities'][2]['certified_full_lhs_upper']['exact']) == Fraction(1, 2)
    assert not r['Gate7_closed'] and not r['FULL_BHSM_COMPLETE']


@pytest.mark.parametrize('field,value', [('radius_exact',['1','1/3']),
    ('history_intervals',list(range(369))), ('ledger_SHA256','OLD'),
    ('booked_functions_excluded_exactly_once',False),
    ('zero_value_and_derivative_at_center',False),
    ('common_parameters_preserved_through_output',False),
    ('required_independent_reproduction_passed',False)])
def test_incomplete_or_mismatched_proof_cannot_promote(field, value):
    c=certificate();c[field]=value
    with pytest.raises(ValueError):evaluate(ledger(),'A',c)


def test_equality_at_derivative_threshold_does_not_certify_strict_contraction():
    c=certificate();c['kappa_upper_exact']=['1/4','3/4']
    r=evaluate(ledger(),'A',c)
    assert r['inequalities'][2]['rigorous_margin']['exact']=='0'
    assert r['classification']=='INSUFFICIENT_ENCLOSURE'
    assert not r['physical_inequality_violation_proved']


def test_double_booking_and_inconsistent_allowance_are_rejected():
    x=ledger();x['interval14_debit_count']=2
    with pytest.raises(ValueError):evaluate(x,'A')
    x=deepcopy(ledger());x['rows'][0]['remaining_self_map_allowance']['exact']='1'
    with pytest.raises(ValueError):evaluate(x,'A')
