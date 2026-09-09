import copy
from fractions import Fraction
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_physical_first_causal_envelope as producer


def test_all_quadratic_cross_terms_and_local_pair_factor_are_outward():
    blocks=[3.,5.,7.];a=[2.,4.];e=[1/16,1/32]
    uu,cu,cc=map(Fraction,blocks);au,ac=map(Fraction,a);eu,ec=map(Fraction,e)
    exact=2*(uu*(2*au*eu+eu**2)+2*cu*(au*ec+ac*eu+eu*ec)+cc*(2*ac*ec+ec**2))
    upper=producer.coordinate_pullback_from_block_bounds(blocks,a,e)
    assert Fraction(upper)>=exact
    assert Fraction(upper)-exact<Fraction(1,10**12)
    assert producer.coordinate_pullback_from_block_bounds(blocks,a,[0.,0.])==0


@pytest.mark.parametrize('bounds',[[1.,-1.],[float('nan'),1.],[float('inf'),1.],[1.]])
def test_invalid_coordinate_bounds_fail_closed(bounds):
    with pytest.raises(ValueError):producer.coordinate_pullback_from_block_bounds([1.,2.,3.],[1.,1.],bounds)


def fixture(index):
    arrays=dict(basis=np.eye(3),coordinates=np.ones((3,4)),output=np.ones((2,3)))
    base=dict(basis=arrays['basis'].copy(),approximate_coordinates=arrays['coordinates'].copy(),output=arrays['output'].copy())
    scope='PHYSICAL_FIRST_DERIVATIVE_AND_STORED_CONSTRUCTION_COORDINATE_ERROR'
    record=dict(interval=index,scope=scope,physical_first_derivative_error_enclosed=True,
        common_projector_derivative_consistency_enclosed=True,
        physical_endpoint_certificates=[dict(node=n) for n in (index,index+1) if n],coordinate_error=dict(scope=scope),
        operand_binary64_SHA256={k:producer.coordinates.endpoint.campaign.array_sha(v) for k,v in arrays.items()})
    return record,arrays,base


def test_both_adjacent_endpoints_required_except_fixed_initial_endpoint():
    for index in (0,4):
        record,arrays,base=fixture(index)
        producer.validate_coordinate_point(record,index,arrays,base)
        record['physical_endpoint_certificates'].pop()
        with pytest.raises(RuntimeError):producer.validate_coordinate_point(record,index,arrays,base)


def test_changed_operands_or_unproven_scope_cannot_enter_physical_envelope():
    record,arrays,base=fixture(4)
    for key,value in [('interval',5),('scope','STORED_ONLY'),('physical_first_derivative_error_enclosed',False),
                      ('common_projector_derivative_consistency_enclosed',False)]:
        changed=copy.deepcopy(record);changed[key]=value
        with pytest.raises(RuntimeError):producer.validate_coordinate_point(changed,4,arrays,base)
    base['approximate_coordinates'][0,0]+=1
    with pytest.raises(RuntimeError):producer.validate_coordinate_point(record,4,arrays,base)
    record,arrays,base=fixture(4);arrays['output'][0,0]+=1
    with pytest.raises(RuntimeError):producer.validate_coordinate_point(record,4,arrays,base)


def test_conflicting_source_bindings_are_rejected():
    target={'same':'a'}
    producer.merge_sources(target,{'same':'a','new':'b'})
    assert target=={'same':'a','new':'b'}
    with pytest.raises(RuntimeError):producer.merge_sources(target,{'same':'changed'})
