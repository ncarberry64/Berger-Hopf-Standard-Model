import gzip,json
from io import StringIO
import pytest
from bhsm.interface.adaptive_expression_reader import AdaptiveReader,read_graph
from bhsm.interface.streamed_expression_artifact import read_graph as original


def test_large_metadata_and_nodes_are_identical_to_frozen_reader(tmp_path):
    payload={'format':'SHARED_EXPRESSION_DAG_V1','affine_enclosures':{'large':['1/3']*100000},
        'nodes':[['constant','1'],['linear',[[0,'2']]]],'roots':{'result':1},'tail':1234567890123456789}
    p=tmp_path/'graph.json.gz';p.write_bytes(gzip.compress(json.dumps(payload).encode(),mtime=0))
    nodes=[];fast=read_graph(p,lambda i,n:nodes.append(n))
    assert fast==original(p)
    assert nodes==payload['nodes']


def test_value_at_a_buffer_boundary_and_trailing_data():
    r=AdaptiveReader(StringIO('12345678901234567890 '))
    r.buffer='';r.position=0
    assert r.value()==12345678901234567890
    assert r.character()==''
    with pytest.raises(json.JSONDecodeError):AdaptiveReader(StringIO('{')).value()
