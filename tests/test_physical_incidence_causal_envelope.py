import copy
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_physical_incidence_causal_envelope as producer


def fixture():
    arrays=dict(stored_output_maps=np.ones((2,3,4)))
    record=dict(interval=4,scope='PHYSICAL_MIDPOINT_DF_AND_FROZEN_ENDPOINT_OUTPUT_CONSTRUCTION_ERROR',
        physical_midpoint_DF_incidence_error_enclosed=True,combined_endpoint_output_bounds_replace_stored_construction_bounds=True,
        output_map_error_bounds=dict(left={},right={}),
        operand_binary64_SHA256={k:producer.incidence.campaign.array_sha(v) for k,v in arrays.items()})
    return record,arrays


def test_incidence_cannot_replace_output_errors_without_its_physical_scope():
    record,arrays=fixture();producer.validate_incidence(record,4,arrays)
    for key,value in [('interval',5),('scope','STORED_ONLY'),('physical_midpoint_DF_incidence_error_enclosed',False),
                      ('combined_endpoint_output_bounds_replace_stored_construction_bounds',False)]:
        changed=copy.deepcopy(record);changed[key]=value
        with pytest.raises(RuntimeError):producer.validate_incidence(changed,4,arrays)


def test_both_output_maps_and_unchanged_operands_are_required():
    record,arrays=fixture();record['output_map_error_bounds'].pop('left')
    with pytest.raises(RuntimeError):producer.validate_incidence(record,4,arrays)
    record,arrays=fixture();arrays['stored_output_maps'][0,0,0]+=1
    with pytest.raises(RuntimeError):producer.validate_incidence(record,4,arrays)
