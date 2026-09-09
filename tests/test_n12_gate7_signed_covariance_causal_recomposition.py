import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('covariance_recomposition_certificate',
    ROOT/'scripts/certify_n12_gate7_signed_covariance_causal_recomposition.py')
certificate=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(certificate)


def _record(tmp_path,monkeypatch):
    path=tmp_path/'covariance.npz';path.write_bytes(b'covariance')
    monkeypatch.setattr(certificate.formation,'DATA',path)
    return dict(artifact='BHSM_N12_GATE7_STORED_COVARIANCE_FORMATION',validation_passed=True,
        scope='EXACT_RECONSTRUCTED_TENSOR_COVARIANCES_ENCLOSED_ABOUT_SAVED_CENTER_ARRAYS',
        coverage=dict(intervals=370,local_covariances=1110,adjacent_covariances=370,complete=True),
        data_SHA256=certificate.center._sha(path))


@pytest.mark.parametrize('key,value',[('validation_passed',False),('data_SHA256','changed'),('coverage',{})])
def test_complete_current_covariance_data_required(tmp_path,monkeypatch,key,value):
    record=_record(tmp_path,monkeypatch);record[key]=value
    with pytest.raises(RuntimeError,match='Complete unchanged'):
        certificate._verify_formation(record)


def test_center_and_axis_bindings_are_required(tmp_path,monkeypatch):
    with pytest.raises(RuntimeError,match='lacks center/axis'):
        certificate._verify_formation(_record(tmp_path,monkeypatch))


def test_parallel_merge_is_order_independent_and_rejects_missing_or_duplicate_nodes():
    chunks=[]
    for start in (1,2):
        nodes=list(range(start,371,2))
        values=[0.]+[None]*370
        for node in nodes:values[node]=float(node)
        chunks.append(dict(coverage=dict(target_nodes=nodes),longitudinal_coefficient_upper=values,
                           transverse_coefficient_upper=values))
    expected=certificate._merge_chunks(chunks)
    assert expected==certificate._merge_chunks(list(reversed(chunks)))
    assert expected['maximum_coefficients_upper']==[370.,370.]
    with pytest.raises(RuntimeError,match='Incomplete'):
        certificate._merge_chunks(chunks[:1])
    with pytest.raises(RuntimeError,match='Duplicated'):
        certificate._merge_chunks(chunks+chunks[:1])
