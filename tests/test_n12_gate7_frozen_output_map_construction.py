import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('frozen_output_certificate',
    ROOT/'scripts/certify_n12_gate7_frozen_output_map_construction.py')
certificate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(certificate)


def _record():
    return dict(artifact='BHSM_N12_GATE7_RESOLVED_COORDINATE_CAUSAL_TRANSPORT',
        scope='RESOLVED_COORDINATE_AND_STORAGE_CROSS_ERROR_THROUGH_EXACT_STORED_TENSOR_AND_CAUSAL_MAPS_ONLY',
        validation_passed=True,coverage=dict(intervals=370,nodes=371,complete=True),
        rows=[dict(interval=i) for i in range(370)])


@pytest.mark.parametrize('field,value',[('validation_passed',False),('artifact','wrong'),
    ('scope','wrong'),('coverage',{}),('rows',[dict(interval=i) for i in reversed(range(370))]),
    ('rows',[dict(interval=i) for i in range(369)])])
def test_only_complete_ordered_coordinate_certificate_accepted(field,value):
    good = _record()
    assert len(certificate._coordinate_rows(good)) == 370
    good[field] = value
    with pytest.raises(RuntimeError):
        certificate._coordinate_rows(good)


def test_output_binding_rejects_a_single_last_bit_change():
    original = np.ones((2,3))
    record = dict(output_map_SHA256=certificate.maps_certificate._array_hash(original))
    certificate._match_output(record,original)
    original[0,0] = np.nextafter(original[0,0],np.inf)
    with pytest.raises(RuntimeError,match='differs'):
        certificate._match_output(record,original)
