"""Input boundary tests; numerical causal arithmetic is tested independently."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
from flint import arb

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('causal_quadratic_consumer_test',ROOT/'scripts/certify_n12_gate7_direct_causal_quadratic.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


def test_exact_full_source_inventory_and_repeat_receipt(tmp_path,monkeypatch):
    monkeypatch.setattr(p.local.df,'file_key',lambda path:path.name)
    files={f'{family}_{pair}.{ext}':'test-only' for family in ('LL','LT','TT')
           for pair in ('00','01','10','11') for ext in ('npz','json')}
    manifest=dict(algorithm=p.producer.ALGORITHM,interval=13,complete_local_source_blocks=True,files=files)
    path=tmp_path/'manifest.json';p.producer.hessian.write_json(path,manifest)
    receipt=dict(byte_identical=True,independent_recomputation=True,manifest_SHA256=p.local.df.values.sha(path))
    p.verify_manifest(13,manifest,receipt,path)
    with pytest.raises(RuntimeError):p.verify_manifest(13,manifest,dict(receipt,independent_recomputation=False),path)
    del manifest['files']['TT_11.npz']
    with pytest.raises(RuntimeError):p.verify_manifest(13,manifest,receipt,path)


def test_changed_common_operands_and_missing_physical_provenance_fail(tmp_path):
    base=dict(axes_SHA256='axes',causal_maps_SHA256='maps')
    raw={p.local.df.file_key(path):p.local.df.values.sha(path) for path in (
        Path(p.producer.__file__),p.producer.THEORY,Path(p.producer.quadratic.__file__),Path(p.producer.second.__file__))}
    for stage,index in (('endpoint',13),('midpoint',13),('endpoint',14)):
        for name in ('manifest.json','reproduction.json'):
            raw[p.local.df.file_key(p.producer.hessian.point_directory(stage,index)/name)]='fixture-only'
    source=dict(inputs={},raw_inputs=raw,**base)
    record=p.producer.metadata(13,'LT','01',source)
    path=tmp_path/'LT_01.npz';path.write_bytes(b'explicit validator fixture, not numerical input')
    record['data_SHA256']=p.local.df.values.sha(path);p.producer.hessian.write_json(path.with_suffix('.json'),record)
    p.verify_record(13,'LT','01',record,path,base)
    with pytest.raises(RuntimeError,match='common operands'):
        p.verify_record(13,'LT','01',record,path,dict(base,axes_SHA256='changed'))
    del raw[p.local.df.file_key(p.producer.hessian.point_directory('endpoint',14)/'reproduction.json')]
    p.producer.hessian.write_json(path.with_suffix('.json'),record)
    with pytest.raises(RuntimeError,match='paired physical Hessian'):
        p.verify_record(13,'LT','01',record,path,base)


def test_rational_source_reader_rejects_incomplete_tensor(tmp_path):
    paths={}
    for pair in ('00','01','10','11'):
        path=tmp_path/f'LL_{pair}.npz';paths[13,'LL',pair]=path
        mid,rad=p.local.df.values.hs.rational_balls(np.full((74,1),arb(1,.125),dtype=object))
        np.savez_compressed(path,Q_mid_q=mid,Q_rad_q=rad)
    blocks=p.read_interval(dict(paths=paths),13,'LL')
    assert all(block.shape==(74,1) and block[0,0].contains(arb(1)) for block in blocks.values())
    np.savez_compressed(paths[13,'LL','11'],Q_mid_q=mid[:-1],Q_rad_q=rad[:-1])
    with pytest.raises(RuntimeError,match='complete rational'):p.read_interval(dict(paths=paths),13,'LL')


def test_full_default_and_explicit_subset_have_distinct_coverage_paths():
    assert p.indices_or_all(None)==list(range(370))
    assert p.result_path(None).name=='BHSM_N12_GATE7_FULL_DIRECT_CAUSAL_QUADRATIC.json'
    assert p.result_path([13]).name=='BHSM_N12_GATE7_SELECTED_013_DIRECT_CAUSAL_QUADRATIC.json'
    assert p.result_path(list(reversed(range(370))))==p.result_path(None)
    for values in ([],[13,13],[-1],[370],[True]):
        with pytest.raises(ValueError):p.indices_or_all(values)


def test_shared_inputs_are_not_rehashed_per_interval_but_conflicts_fail(monkeypatch):
    calls=[]
    def verified_merge(inputs,raw,additional):
        calls.append(dict(additional));raw.update(additional)
    monkeypatch.setattr(p.local.residual,'merge_verified_raw_sources',verified_merge)
    raw={};p.merge_raw({},raw,{'common':'A','first':'B'})
    p.merge_raw({},raw,{'common':'A','second':'C'})
    assert calls==[{'common':'A','first':'B'},{'second':'C'}]
    with pytest.raises(RuntimeError,match='inconsistent shared'):
        p.merge_raw({},raw,{'common':'changed'})
    assert len(calls)==2
