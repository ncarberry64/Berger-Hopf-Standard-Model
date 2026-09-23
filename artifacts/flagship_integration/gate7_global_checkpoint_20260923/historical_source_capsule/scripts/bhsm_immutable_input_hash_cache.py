"""Cache input digests only while Windows denies writes and replacement."""
from contextlib import contextmanager
import os
from pathlib import Path


@contextmanager
def cache_hashes(targets,*,excluded_roots=()):
    """Retain read-only native handles until the numerical invocation ends.

    Every hash convention keeps its original function. Windows FILE_SHARE_READ
    denies writes/deletion while a digest is reused. Output directories are
    excluded so candidate writes and atomic publication remain unaffected.
    Other operating systems use the original functions without caching.
    """
    stats=dict(enabled=os.name=='nt',hash_requests=0,original_hash_calls=0,cache_hits=0,locked_files=0)
    if os.name!='nt':
        yield stats
        return
    import ctypes as c
    from ctypes import wintypes as w
    kernel=c.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,w.HANDLE]
    kernel.CreateFileW.restype=w.HANDLE
    kernel.CloseHandle.argtypes=[w.HANDLE];kernel.CloseHandle.restype=w.BOOL
    invalid=c.c_void_p(-1).value
    excluded=tuple(Path(path).resolve() for path in excluded_roots)
    handles={};digests={};originals=[];seen=set()

    def wrap(original,identity):
        def hashed(path):
            stats['hash_requests']+=1
            resolved=Path(path).resolve()
            if any(resolved.is_relative_to(root) for root in excluded):
                stats['original_hash_calls']+=1
                return original(path)
            key=str(resolved).casefold()
            if key not in handles:
                handle=kernel.CreateFileW(str(resolved),0x80000000,0x00000001,None,3,0x80,None)
                if handle==invalid:raise c.WinError(c.get_last_error())
                handles[key]=handle;stats['locked_files']+=1
            cache_key=(identity,key)
            if cache_key not in digests:
                stats['original_hash_calls']+=1
                digests[cache_key]=original(resolved)
            else:stats['cache_hits']+=1
            return digests[cache_key]
        return hashed

    try:
        for module,name in targets:
            identity=(id(module),name)
            if identity in seen:continue
            seen.add(identity)
            original=getattr(module,name)
            originals.append((module,name,original))
            setattr(module,name,wrap(original,identity))
        yield stats
    finally:
        for module,name,original in reversed(originals):setattr(module,name,original)
        for handle in handles.values():kernel.CloseHandle(handle)
