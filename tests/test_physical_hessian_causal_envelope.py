import copy
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_physical_hessian_causal_envelope as consumer


def midpoint():
    return dict(interval=4,
        scope='SELECTED_PHYSICAL_HESSIAN_AND_ENDPOINT_DF_ERRORS_AT_STORED_FRAMES_WITH_FROZEN_OUTPUT_MAP',
        physical_Hessian_at_this_midpoint_enclosed=True,
        physical_first_derivative_error_enclosed_at_stored_frames=True,
        common_projector_derivative_consistency_enclosed=True,
        physical_point_certificate=dict(interval=4, all_rows_present=True, direction_pairs=4950, input_dimension=99),
        local_pair_uniform_quadratic_coefficient_upper=.1,
        physical_error_pullback=dict(local_pair_uniform_quadratic_coefficient_upper=.1))


def endpoint():
    return dict(node=370,
        scope='SELECTED_PHYSICAL_ENDPOINT_HESSIAN_ERROR_WITH_PHYSICAL_MIDPOINT_DF_AND_FROZEN_OUTPUT_CONSTRUCTION',
        rows=74, direction_pairs=2775, physical_Hessian_at_this_endpoint_enclosed=True,
        exact_normalized_projector_direction_errors_included=True,
        physical_midpoint_DF_incidence_error_enclosed=True,
        combined_output_bound_replaces_stored_construction_bound=True,
        components=[dict(interval=369, output_label='right', single_endpoint_quadratic_coefficient_upper=.2,
                         physical_error_pullback=dict(total_error_pullback_frobenius_upper=.2))])


def test_midpoint_requires_physical_df_and_complete_hessian():
    record = midpoint()
    assert consumer.validate_midpoint(record, 4) == .1
    record['physical_first_derivative_error_enclosed_at_stored_frames'] = False
    with pytest.raises(RuntimeError, match='Hessian/DF'):
        consumer.validate_midpoint(record, 4)
    record = midpoint()
    record['physical_point_certificate']['all_rows_present'] = False
    with pytest.raises(RuntimeError, match='all 99'):
        consumer.validate_midpoint(record, 4)


def test_endpoint_requires_physical_incidence_and_unique_terminal_slot():
    record = endpoint()
    assert consumer.validate_endpoint(record, 370) == {(369, 'right'): .2}
    record['physical_midpoint_DF_incidence_error_enclosed'] = False
    with pytest.raises(RuntimeError, match='incidence'):
        consumer.validate_endpoint(record, 370)
    record = endpoint()
    record['components'].append(copy.deepcopy(record['components'][0]))
    with pytest.raises(RuntimeError, match='duplicate'):
        consumer.validate_endpoint(record, 370)


def test_coefficient_must_match_certified_pullback():
    record = midpoint()
    record['local_pair_uniform_quadratic_coefficient_upper'] = 0.
    with pytest.raises(RuntimeError, match='differs'):
        consumer.validate_midpoint(record, 4)
    record = endpoint()
    record['components'][0]['single_endpoint_quadratic_coefficient_upper'] = 0.
    with pytest.raises(RuntimeError, match='inconsistent'):
        consumer.validate_endpoint(record, 370)
