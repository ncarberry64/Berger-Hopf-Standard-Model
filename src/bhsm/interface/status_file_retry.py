"""Retry only explicitly named Windows progress-file sharing failures."""
from contextlib import contextmanager
from pathlib import Path
import time


@contextmanager
def retry_status_writes(module,paths,*,attempts=120,delay=.25,on_retry=None):
    """Leave scientific artifact writes and the original encoded bytes unchanged.

    A status reader or synchronizer can briefly deny Windows atomic replacement.
    Only named status targets and WinError 5/32/33 are retried; no file is deleted.
    """
    if type(attempts) is not int or attempts<1 or not 0<=delay<=1:
        raise ValueError('bounded retry policy required')
    targets={Path(path).resolve() for path in paths}
    original=module.write_json

    def write(path,record):
        if Path(path).resolve() not in targets:return original(path,record)
        for attempt in range(attempts):
            try:return original(path,record)
            except PermissionError as error:
                if getattr(error,'winerror',None) not in (5,32,33) or attempt+1==attempts:raise
                if on_retry:on_retry(Path(path),attempt+1,error)
                time.sleep(delay)

    module.write_json=write
    try:yield
    finally:module.write_json=original
