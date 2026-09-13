"""Bounded retries of read-only checks after scoped artifact access denials."""
import errno
from functools import wraps
from pathlib import Path
import time


def retry_read_check(check,roots,*,attempts=120,delay=.25,on_retry=None):
    """Retry a pure validation call, never a numerical producer or file write.

    All successful bytes still pass through the original validation. Parse,
    hash, binding and arithmetic failures propagate immediately. Persistent
    permissions errors propagate after the bounded retry window.
    """
    if type(attempts) is not int or attempts<1 or not 0<=delay<=1:
        raise ValueError('bounded retry policy required')
    allowed=tuple(Path(root).resolve() for root in roots)
    if not allowed:raise ValueError('explicit artifact roots required')
    @wraps(check)
    def wrapped(*args,**kwargs):
        for attempt in range(attempts):
            try:return check(*args,**kwargs)
            except PermissionError as error:
                name=error.filename
                transient=(getattr(error,'winerror',None) in (5,32,33)
                    or (getattr(error,'winerror',None) is None and error.errno==errno.EACCES))
                scoped=name is not None and any(Path(name).resolve().is_relative_to(root) for root in allowed)
                if not transient or not scoped or attempt+1==attempts:raise
                if on_retry:on_retry(Path(name),attempt+1,error)
                time.sleep(delay)
    return wrapped
