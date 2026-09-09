import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('stored_covariance_certificate',
    ROOT/'scripts/certify_n12_gate7_stored_covariance_formation.py')
certificate=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(certificate)


def _record():
    return dict(artifact='BHSM_N12_GATE7_STORED_PULLBACK_ASSEMBLY',validation_passed=True,
        scope='RECONSTRUCTED_LOCAL_TENSOR_ASSEMBLY_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY',
        coverage=dict(intervals=370,nodes=371,complete=True),rows=[dict(interval=i) for i in range(370)])


@pytest.mark.parametrize('key,value',[('validation_passed',False),('scope','wrong'),
    ('coverage',{}),('rows',[dict(interval=i) for i in reversed(range(370))])])
def test_complete_ordered_assembly_required(key,value):
    record=_record()
    assert len(certificate._assembly_rows(record))==370
    record[key]=value
    with pytest.raises(RuntimeError):certificate._assembly_rows(record)


def test_local_tensor_binding_is_exact():
    local=np.ones((2,4,4))
    row=dict(local_tensor_SHA256=certificate.assembly._array_hash(local))
    certificate._verify_local_tensor(local,row)
    local[0,0,0]=np.nextafter(local[0,0,0],np.inf)
    with pytest.raises(RuntimeError,match='differs'):
        certificate._verify_local_tensor(local,row)
