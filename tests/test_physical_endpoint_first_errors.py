import json
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_physical_endpoint_first_errors as producer


def test_endpoint_cache_requires_unchanged_data_and_binding(tmp_path):
    path=tmp_path/'endpoint_001.npz';mid=np.zeros((99,74));radius=np.full((99,74),1/32)
    np.savez_compressed(path,error_mid=mid,error_radius=radius,node=np.asarray(1),
                       fingerprint=np.asarray('bound'),precision_bits=np.asarray(256))
    record=dict(node=1,binding={'array':'same'},fingerprint='bound',
                data_SHA256=producer.campaign.cache.file_sha(path),outward_export_contains_Arb_source=True)
    path.with_suffix('.json').write_text(json.dumps(record))
    loaded=producer.load_cached(path,1,{'array':'same'},'bound')
    assert np.array_equal(loaded[0],mid) and np.array_equal(loaded[1],radius)
    with pytest.raises(RuntimeError):producer.load_cached(path,1,{'array':'changed'},'bound')
    with path.open('ab') as stream:stream.write(b'changed')
    with pytest.raises(RuntimeError):producer.load_cached(path,1,{'array':'same'},'bound')


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),-1.])
def test_invalid_error_radius_fails(bad):
    with pytest.raises(ValueError):producer.validate_arrays(np.zeros((99,74)),np.full((99,74),bad))


@pytest.mark.parametrize('nodes',['0','371','1,1'])
def test_only_distinct_noninitial_endpoint_nodes_are_accepted(nodes):
    with pytest.raises(ValueError):producer.parse_nodes(nodes)
