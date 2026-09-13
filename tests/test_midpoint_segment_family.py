from copy import deepcopy
import pytest
from bhsm.interface.midpoint_segment_family import validate_midpoint_segment_family


def records():
    eigen = dict(validation_passed=True, uniform_action_eigenpair_enclosed=True,
                 witness_contained=True, positive_original_reference_overlap=True,
                 action_domain_bound=True, uniform_actual_HS_midpoint_eigenpair_enclosed=True, selected_zero_based_index_verified=24,
                 segment_inertia_lower_rational='1/7', original_reference_overlap_lower_rational='1/8',
                 trials=[dict(rows=[dict(coordinate=i, strict_inclusion=True, strict_contraction=True,
                                        inclusion_margin_lower_rational='1/9',
                                        contraction_margin_lower_rational='1/10') for i in range(62)])])
    value = dict(validation_passed=True, uniform_actual_HS_midpoint_field_enclosed=True,
                 positive_physical_G_norm=True, scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN',
                 physical_G_norm_lower_rational='1/11')
    return eigen, value


def test_missing_row_or_zero_margin_cannot_be_replaced_by_success_flags():
    eigen, value = records()
    assert validate_midpoint_segment_family(eigen, value)['bordered_implicit_jacobian_invertible']
    missing = deepcopy(eigen)
    missing['trials'][0]['rows'].pop(17)
    with pytest.raises(ValueError):
        validate_midpoint_segment_family(missing, value)
    eigen['trials'][0]['rows'][17]['contraction_margin_lower_rational'] = '0'
    with pytest.raises(ValueError):
        validate_midpoint_segment_family(eigen, value)


@pytest.mark.parametrize('which,key', [('eigen', 'segment_inertia_lower_rational'),
                                      ('eigen', 'original_reference_overlap_lower_rational'),
                                      ('value', 'physical_G_norm_lower_rational')])
def test_singular_or_unoriented_family_rejected(which, key):
    eigen, value = records()
    (eigen if which == 'eigen' else value)[key] = '-1/1000000000000000000000000000000'
    with pytest.raises(ValueError):
        validate_midpoint_segment_family(eigen, value)


@pytest.mark.parametrize('missing', ['eigen', 'field', 'scope'])
def test_endpoint_certificate_cannot_stand_in_for_actual_midpoint(missing):
    eigen, value = records()
    if missing == 'eigen':
        eigen.pop('uniform_actual_HS_midpoint_eigenpair_enclosed')
    elif missing == 'field':
        value.pop('uniform_actual_HS_midpoint_field_enclosed')
        value['uniform_physical_value_enclosed'] = True
    else:
        value['scope'] = 'SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE'
    with pytest.raises(ValueError):
        validate_midpoint_segment_family(eigen, value)
