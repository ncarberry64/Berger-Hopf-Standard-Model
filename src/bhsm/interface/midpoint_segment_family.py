"""Check analytic preconditions recorded by the retained paired actual midpoint certificates.

The caller must verify source identity, independent receipts and actual midpoint domain identity.
This is specific to the smooth retained action and its normalized bordered
eigenpair equations; report flags alone do not prove a new action smooth.
"""
from fractions import Fraction


def _positive(value):
    try:
        return Fraction(value) > 0
    except (ValueError, TypeError, ZeroDivisionError):
        return False


def validate_midpoint_segment_family(eigen, value):
    for key in ('validation_passed', 'uniform_action_eigenpair_enclosed',
                'witness_contained', 'positive_original_reference_overlap', 'action_domain_bound',
                'uniform_actual_HS_midpoint_eigenpair_enclosed'):
        if eigen.get(key) is not True:
            raise ValueError('missing paired eigenpair condition: ' + key)
    if eigen.get('selected_zero_based_index_verified') != 24:
        raise ValueError('retained selected eigenpair required')
    for key in ('segment_inertia_lower_rational', 'original_reference_overlap_lower_rational'):
        if not _positive(eigen.get(key)):
            raise ValueError('strict analytic margin required: ' + key)
    trials = eigen.get('trials', [])
    rows = trials[-1].get('rows', []) if trials else []
    if len(rows) != 62 or [row.get('coordinate') for row in rows] != list(range(62)):
        raise ValueError('complete ordered bordered eigenpair rows required')
    for row in rows:
        if (row.get('strict_inclusion') is not True or row.get('strict_contraction') is not True
                or not _positive(row.get('inclusion_margin_lower_rational'))
                or not _positive(row.get('contraction_margin_lower_rational'))):
            raise ValueError('strict self-inclusion and invertibility on every row required')
    if (value.get('validation_passed') is not True
            or value.get('uniform_actual_HS_midpoint_field_enclosed') is not True
            or value.get('positive_physical_G_norm') is not True
            or value.get('scope') != 'ACTUAL_HS_MIDPOINT_OUTER_DOMAIN'
            or not _positive(value.get('physical_G_norm_lower_rational'))):
        raise ValueError('strict positive physical norm on the same tube required')
    return dict(positive_action_inertia=True, unique_oriented_eigenpair_on_tube=True,
                bordered_implicit_jacobian_invertible=True, positive_physical_norm=True)
