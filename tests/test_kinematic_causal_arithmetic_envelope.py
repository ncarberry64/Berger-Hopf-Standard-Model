from pathlib import Path
import copy
import sys
import pytest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_kinematic_causal_arithmetic_envelope as producer


def record():
    return dict(interval=4,scope='NORMALIZED_MIDPOINT_CONSTRUCTION_AND_SOLVE_FROM_EXACT_STORED_OPERANDS',
        exact_stored_first_derivatives_only=True,
        construction=dict(combined_bound_replaces_stored_target_coordinate_solve_bound=True),
        combined_stored_tensor_pullback=dict(scope='STORED_OUTPUT_TENSOR_PULLBACK_OF_CERTIFIED_COORDINATE_ERRORS'))


def test_wrong_point_or_unproven_scope_cannot_enter_replacement():
    producer.validate_point(record(),4)
    for field,value in [('interval',5),('scope','PHYSICAL'),('exact_stored_first_derivatives_only',False)]:
        bad=copy.deepcopy(record());bad[field]=value
        with pytest.raises(RuntimeError):producer.validate_point(bad,4)


def test_combined_bound_must_explicitly_replace_previous_solve_error():
    bad=record();bad['construction']['combined_bound_replaces_stored_target_coordinate_solve_bound']=False
    with pytest.raises(RuntimeError):producer.validate_point(bad,4)


def test_historical_byte_hash_and_new_shape_hash_are_verified_separately():
    value=np.array([[1.,2.],[3.,4.]])
    old_hash=producer.prior.coordinate.old.coordinate._array_hash(value)
    new_hash=producer.construction.campaign.array_sha(value)
    assert old_hash!=new_hash
    row=dict(operand_binary64_SHA256={'basis':old_hash},output_map_SHA256=old_hash)
    producer.match_prior_operands(row,{'basis':value},value)
    with pytest.raises(RuntimeError):
        producer.match_prior_operands(row,{'basis':value+1},value)
    row['operand_binary64_SHA256']['basis']=new_hash
    with pytest.raises(RuntimeError):
        producer.match_prior_operands(row,{'basis':value},value)
