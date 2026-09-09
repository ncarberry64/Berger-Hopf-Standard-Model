import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('causal_arithmetic_certificate',
    ROOT/'scripts/certify_n12_gate7_stored_causal_arithmetic_envelope.py')
certificate=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(certificate)


@pytest.mark.parametrize('key,value',[('validation_passed',False),('scope','wrong'),
    ('causal_maps_SHA256','different'),('coverage',dict(intervals=369,nodes=370,complete=False))])
def test_arithmetic_sources_require_complete_scope_and_exact_common_map(tmp_path,monkeypatch,key,value):
    monkeypatch.setattr(certificate.coordinate,'ROOT',tmp_path)
    data=tmp_path/'source.bin';data.write_bytes(b'frozen')
    record=dict(artifact='source',scope='scope',validation_passed=True,causal_maps_SHA256='same',
        coverage=dict(intervals=370,nodes=371,complete=True),
        inputs={'source.bin':certificate.center._sha(data)})
    certificate._verify_record(record,'source','scope','same')
    record[key]=value
    with pytest.raises(RuntimeError,match='Complete same-map'):
        certificate._verify_record(record,'source','scope','same')
