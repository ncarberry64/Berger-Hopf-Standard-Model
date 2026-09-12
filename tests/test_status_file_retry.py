"""Transient telemetry locks must not change bytes or mask artifact failures."""
import json
from types import SimpleNamespace
import pytest
from bhsm.interface.status_file_retry import retry_status_writes


def sharing_error(code=32):
    error=PermissionError('temporary sharing failure');error.winerror=code;return error


def test_transient_status_failure_retries_identical_payload_and_restores_writer(tmp_path):
    target=tmp_path/'active_state.json';calls=[]
    def writer(path,record):
        data=(json.dumps(record,sort_keys=True)+'\n').encode();calls.append(data)
        if len(calls)<3:raise sharing_error()
        path.write_bytes(data)
    module=SimpleNamespace(write_json=writer)
    with retry_status_writes(module,[target],attempts=3,delay=0):module.write_json(target,dict(completed_rows=27))
    assert len(calls)==3 and calls[0]==calls[1]==calls[2]==target.read_bytes()
    assert module.write_json is writer


@pytest.mark.parametrize('status,code,expected',[(False,32,1),(True,2,1),(True,5,3)])
def test_other_files_other_errors_and_retry_exhaustion_remain_failures(tmp_path,status,code,expected):
    target=tmp_path/'active_state.json';calls=[]
    def writer(path,record):calls.append(path);raise sharing_error(code)
    module=SimpleNamespace(write_json=writer)
    with pytest.raises(PermissionError):
        with retry_status_writes(module,[target],attempts=3,delay=0):
            module.write_json(target if status else tmp_path/'certificate.json',dict(x=1))
    assert len(calls)==expected and module.write_json is writer
