"""Reuse hashes only when actual writes are excluded, and preserve output writes."""
import hashlib
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from bhsm_immutable_input_hash_cache import cache_hashes


@pytest.mark.skipif(os.name!='nt',reason='Windows native sharing guarantee')
def test_cached_file_cannot_be_written_or_replaced_until_context_exit(tmp_path):
    path=tmp_path/'input.dat';path.write_bytes(b'original');calls=[]
    def raw(path):calls.append(path);return hashlib.sha256(path.read_bytes()).hexdigest()
    module=SimpleNamespace(sha=raw)
    with cache_hashes([(module,'sha')]) as stats:
        first=module.sha(path);assert module.sha(path)==first and len(calls)==1
        with pytest.raises(PermissionError):path.write_bytes(b'changed')
        replacement=tmp_path/'replacement.dat';replacement.write_bytes(b'changed')
        with pytest.raises(PermissionError):replacement.replace(path)
        assert module.sha(path)==first and stats['cache_hits']==2
    assert module.sha is raw
    path.write_bytes(b'changed')
    with cache_hashes([(module,'sha')]):assert module.sha(path)!=first


def test_output_paths_remain_uncached_and_functions_restore_on_failure(tmp_path):
    output=tmp_path/'output';output.mkdir();path=output/'candidate.dat';path.write_bytes(b'a')
    def raw(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    module=SimpleNamespace(sha=raw)
    with pytest.raises(ArithmeticError):
        with cache_hashes([(module,'sha')],excluded_roots=[output]):
            first=module.sha(path);path.write_bytes(b'b')
            assert module.sha(path)!=first
            raise ArithmeticError('retain scientific failure')
    assert module.sha is raw
    path.write_bytes(b'c')


def test_raw_and_normalized_hash_conventions_remain_distinct(tmp_path):
    path=tmp_path/'input.py';path.write_bytes(b'a\r\nb\r\n')
    module=SimpleNamespace(raw=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(),
        normalized=lambda p:hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest())
    raw,normalized=module.raw(path),module.normalized(path)
    with cache_hashes([(module,'raw'),(module,'normalized'),(module,'raw')]):
        assert module.raw(path)==raw and module.normalized(path)==normalized and raw!=normalized
