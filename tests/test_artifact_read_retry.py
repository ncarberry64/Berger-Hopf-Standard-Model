"""A transient read may retry; invalid data and unrelated access errors may not."""
import errno
import pytest
from bhsm.interface.artifact_read_retry import retry_read_check


def test_scoped_permission_retry_returns_original_validation_result(tmp_path):
    calls=[];events=[];value=object()
    def check(arg):
        calls.append(arg)
        if len(calls)<3:raise PermissionError(errno.EACCES,'denied',str(tmp_path/'row.json'))
        return value
    wrapped=retry_read_check(check,[tmp_path],attempts=3,delay=0,on_retry=lambda *e:events.append(e))
    assert wrapped(7) is value and calls==[7,7,7] and len(events)==2


@pytest.mark.parametrize('kind',['invalid_data','outside_root','persistent'])
def test_failures_are_not_hidden(tmp_path,kind):
    calls=[]
    error=(ValueError('hash or parse mismatch') if kind=='invalid_data' else
        PermissionError(errno.EACCES,'denied',str(tmp_path/'row.json' if kind=='persistent' else tmp_path.parent/'other.json')))
    def check():calls.append(1);raise error
    with pytest.raises(type(error)) as caught:
        retry_read_check(check,[tmp_path],attempts=3,delay=0)()
    assert caught.value is error
    assert len(calls)==(3 if kind=='persistent' else 1)
