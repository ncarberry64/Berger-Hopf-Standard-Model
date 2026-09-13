from copy import deepcopy
import pytest
from bhsm.interface.affine_segment_family import validate_segment_family


def records():
    eigen = dict(validation_passed=True, uniform_action_eigenpair_enclosed=True,
                 witness_contained=True, positive_original_reference_overlap=True,
                 action_domain_bound=True, selected_zero_based_index_verified=24,
                 segment_inertia_lower_rational='1/7', original_reference_overlap_lower_rational='1/8',
                 trials=[dict(rows=[dict(coordinate=i, strict_inclusion=True, strict_contraction=True,
                                        inclusion_margin_lower_rational='1/9',
                                        contraction_margin_lower_rational='1/10') for i in range(62)])])
    value = dict(validation_passed=True, uniform_physical_value_enclosed=True,
                 positive_physical_G_norm=True, scope='SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE',
                 physical_G_norm_lower_rational='1/11')
    return eigen, value


def test_missing_row_or_zero_margin_cannot_be_replaced_by_success_flags():
    eigen, value = records()
    assert validate_segment_family(eigen, value)['bordered_implicit_jacobian_invertible']
    missing = deepcopy(eigen)
    missing['trials'][0]['rows'].pop(17)
    with pytest.raises(ValueError):
        validate_segment_family(missing, value)
    eigen['trials'][0]['rows'][17]['contraction_margin_lower_rational'] = '0'
    with pytest.raises(ValueError):
        validate_segment_family(eigen, value)


@pytest.mark.parametrize('which,key', [('eigen', 'segment_inertia_lower_rational'),
                                      ('eigen', 'original_reference_overlap_lower_rational'),
                                      ('value', 'physical_G_norm_lower_rational')])
def test_singular_or_unoriented_family_rejected(which, key):
    eigen, value = records()
    (eigen if which == 'eigen' else value)[key] = '-1/1000000000000000000000000000000'
    with pytest.raises(ValueError):
        validate_segment_family(eigen, value)
