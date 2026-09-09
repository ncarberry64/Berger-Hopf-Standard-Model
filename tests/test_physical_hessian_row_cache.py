import copy
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from bhsm.interface import physical_hessian_row_cache as cache
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_physical_midpoint_hessian_errors as producer


def save(path,row,fingerprint='target'):
    m=np.arange(2*(3-row),dtype=float).reshape(2,3-row)+row
    r=np.full(m.shape,1/32)
    cache.save_row(path,m,r,row,fingerprint,{'kind':'test'},dimension=3,outputs=2)
    return m,r


def test_complete_rows_preserve_triangular_entries_and_symmetry(tmp_path):
    originals=[save(tmp_path/f'row_{i:03d}.npz',i) for i in range(3)]
    mid,radius,records=cache.assemble_rows(tmp_path,'target',dimension=3,outputs=2)
    assert np.array_equal(mid,mid.transpose(0,2,1))
    assert len(records)==3
    for row,(m,r) in enumerate(originals):
        assert np.array_equal(mid[:,row,row:],m)
        assert np.array_equal(radius[:,row,row:],r)


def test_missing_row_is_not_filled_with_zero(tmp_path):
    save(tmp_path/'row_000.npz',0);save(tmp_path/'row_002.npz',2)
    with pytest.raises(FileNotFoundError):cache.assemble_rows(tmp_path,'target',dimension=3,outputs=2)


def test_changed_payload_hash_fails(tmp_path):
    path=tmp_path/'row_000.npz';save(path,0)
    with path.open('ab') as stream:stream.write(b'changed')
    with pytest.raises(ValueError,match='hash'):cache.load_row(path,0,'target',dimension=3,outputs=2)


def test_wrong_fingerprint_and_overwrite_fail(tmp_path):
    path=tmp_path/'row_000.npz';save(path,0)
    with pytest.raises(ValueError):cache.load_row(path,0,'different',dimension=3,outputs=2)
    before=path.read_bytes()
    with pytest.raises(FileExistsError):save(path,0)
    assert path.read_bytes()==before


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-1.])
def test_bad_radius_fails_before_writing(tmp_path,value):
    with pytest.raises(ValueError):
        cache.save_row(tmp_path/'bad.npz',np.ones((2,3)),np.full((2,3),value),0,'target',{},dimension=3,outputs=2)
    assert not (tmp_path/'bad.npz').exists()


def test_legacy_adoption_requires_identical_inputs_and_computational_sources():
    old=dict(arrays={'state':'statehash'},precision_bits=256,original_kernel_sha256='kernel',
             original_provenance={'action':'frozen'},sources={'old.py':'old','kernel.py':'same'})
    new=copy.deepcopy(old);new['sources']={'new.py':'new','cache.py':'cache','kernel.py':'same'}
    producer.verify_legacy_binding(old,new,'new.py','cache.py')
    for key in ('arrays','original_kernel_sha256','original_provenance'):
        bad=copy.deepcopy(new);bad[key]='changed'
        with pytest.raises(ValueError):producer.verify_legacy_binding(old,bad,'new.py','cache.py')
    new['sources']['kernel.py']='changed'
    with pytest.raises(ValueError):producer.verify_legacy_binding(old,new,'new.py','cache.py')


@pytest.mark.parametrize('text',['0,0','370','-1'])
def test_campaign_rejects_duplicate_or_out_of_range_midpoints(text):
    with pytest.raises(ValueError):producer.parse_intervals(text)
