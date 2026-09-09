import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('frozen_map_certificate',
    ROOT/'scripts/certify_n12_gate7_frozen_causal_map_construction.py')
certificate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(certificate)


def test_source_bindings_reject_missing_stale_and_outside_paths(tmp_path,monkeypatch):
    monkeypatch.setattr(certificate,'ROOT',tmp_path)
    with pytest.raises(RuntimeError,match='Nonempty'):
        certificate._verify_bindings({})
    data = tmp_path/'source.txt'
    data.write_text('frozen')
    digest = certificate.center._sha(data)
    certificate._verify_bindings({'source.txt':digest})
    data.write_text('changed')
    with pytest.raises(RuntimeError,match='Changed'):
        certificate._verify_bindings({'source.txt':digest})
    with pytest.raises(RuntimeError,match='Changed'):
        certificate._verify_bindings({'../escape.txt':digest})


@pytest.mark.parametrize('field,value', [('validation_passed',False),
    ('artifact','wrong'),('status','INCOMPLETE'),('data_SHA256','wrong')])
def test_complete_center_and_exact_data_hash_required(tmp_path,monkeypatch,field,value):
    monkeypatch.setattr(certificate.center,'DATA',tmp_path/'center.npz')
    certificate.center.DATA.write_bytes(b'center')
    record = dict(artifact='BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER',
                  status='SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED', validation_passed=True,
                  data_SHA256=certificate.center._sha(certificate.center.DATA))
    record[field] = value
    with pytest.raises(RuntimeError,match='Complete unchanged'):
        certificate._verify_center(record)


def test_map_operands_must_be_bound_by_center(tmp_path,monkeypatch):
    monkeypatch.setattr(certificate.center,'DATA',tmp_path/'center.npz')
    certificate.center.DATA.write_bytes(b'center')
    record = dict(artifact='BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER',
        status='SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED',validation_passed=True,
        data_SHA256=certificate.center._sha(certificate.center.DATA),inputs={})
    with pytest.raises(RuntimeError,match='lacks frozen-map'):
        certificate._verify_center(record)
