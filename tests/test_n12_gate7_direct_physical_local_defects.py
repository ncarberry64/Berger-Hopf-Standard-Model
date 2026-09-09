import importlib.util,json
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('physical_defects_test',ROOT/'scripts/certify_n12_gate7_direct_physical_local_defects.py')
consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)


@pytest.fixture
def derivative_pair(tmp_path,monkeypatch):
    monkeypatch.setattr(consumer.df,'ROOT',tmp_path)
    monkeypatch.setattr(consumer.df.values,'ROOT',tmp_path)
    work=tmp_path/'df';work.mkdir();monkeypatch.setattr(consumer.df,'WORK',work)
    files={}
    for stage,points in (('endpoint',[13,14]),('midpoint',[13])):
        for i in points:
            for ext in ('json','npz'):
                path=work/f'{stage}_{i:03d}.{ext}';path.write_bytes(b'fixture')
                files[consumer.df.file_key(path)]=consumer.df.values.sha(path)
    manifest=dict(endpoints=[13,14],midpoints=[13],files=files)
    path=work/'manifest.json';path.write_text(json.dumps(manifest))
    receipt=dict(points=3,byte_identical=True,independent_recomputation=True,manifest_SHA256=consumer.df.values.sha(path))
    return manifest,receipt,path


def test_assembly_requires_both_endpoint_derivatives(derivative_pair):
    manifest,receipt,path=derivative_pair
    consumer.verify_pair(manifest,receipt,path,[13])
    with pytest.raises(RuntimeError,match='both endpoint'):
        consumer.verify_pair(manifest,receipt,path,[14])


def test_reuse_and_incomplete_file_inventory_cannot_supply_assembly(derivative_pair):
    manifest,receipt,path=derivative_pair
    with pytest.raises(RuntimeError,match='independently reproduced'):
        consumer.verify_pair(manifest,dict(receipt,independent_recomputation=False),path,[13])
    manifest['files'].pop(next(iter(manifest['files'])))
    with pytest.raises(RuntimeError,match='exact derivative file inventory'):
        consumer.verify_pair(manifest,receipt,path,[13])


def test_independent_local_assembly_preserves_mismatched_candidate(tmp_path,monkeypatch):
    monkeypatch.setattr(consumer,'WORK',tmp_path)
    source=dict(inputs={},raw_inputs={})
    calls=[]
    def build(index,source):
        calls.append(True)
        return dict(C=np.eye(2)),dict(algorithm=consumer.ALGORITHM,interval=index,
            inputs=source['inputs'],raw_input_SHA256=source['raw_inputs'],validation_passed=True)
    monkeypatch.setattr(consumer,'build_point',build)
    consumer.write_point(13,source)
    first={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    consumer.write_point(13,source,True)
    assert len(calls)==2 and first=={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    def changed(index,source):
        arrays,record=build(index,source);arrays['C']*=2;return arrays,record
    monkeypatch.setattr(consumer,'build_point',changed)
    with pytest.raises(ArithmeticError,match='assembly differs'):
        consumer.write_point(13,source,True)
    assert (tmp_path/'interval_013.npz').read_bytes()==first['interval_013.npz']
    assert (tmp_path/'interval_013.partial.npz').exists()
    assert (tmp_path/'interval_013.repeat_mismatch.json').exists()


def test_assembly_reproduction_cannot_start_without_prior_point(tmp_path,monkeypatch):
    monkeypatch.setattr(consumer,'WORK',tmp_path)
    with pytest.raises(RuntimeError,match='prior point evidence'):
        consumer.write_point(13,dict(inputs={},raw_inputs={}),True)
