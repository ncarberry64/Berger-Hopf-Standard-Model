import hashlib,importlib.util,json
from pathlib import Path
from types import SimpleNamespace
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('df_aggregate_test',ROOT/'scripts/certify_n12_gate7_full_direct_df_reproduction.py')
aggregate=importlib.util.module_from_spec(spec);spec.loader.exec_module(aggregate)
backend=aggregate.backend


def test_backend_changes_only_workspace_and_attestation(monkeypatch):
    p=backend.producer
    monkeypatch.setattr(backend,'INSTALLED',False)
    monkeypatch.setattr(p,'WORK',backend.ROOT/'artifacts/flagship_integration/.direct_physical_jacobian_work')
    monkeypatch.setattr(p,'ALGORITHM','ORIGINAL_TEST')
    monkeypatch.setattr(p,'binding',lambda:dict(algorithm=p.ALGORITHM,files={}))
    worker,point_inputs,cache=p.worker,p.point_inputs,p.load_cached
    assert backend.install_backend() is p
    assert backend.install_backend() is p
    result=p.binding()
    assert p.WORK==backend.WORK and result['algorithm']==backend.ALGORITHM
    assert result['campaign_workspace']==backend.WORK.relative_to(backend.ROOT).as_posix()
    assert result['files'][Path(backend.__file__).relative_to(backend.ROOT).as_posix()]==p.values.sha(Path(backend.__file__))
    assert p.worker is worker and p.point_inputs is point_inputs and p.load_cached is cache


def test_backend_refuses_a_different_workspace(monkeypatch,tmp_path):
    monkeypatch.setattr(backend,'INSTALLED',False)
    monkeypatch.setattr(backend.producer,'WORK',tmp_path)
    with pytest.raises(RuntimeError,match='one direct derivative backend'):
        backend.install_backend()


@pytest.fixture
def batches(tmp_path):
    work=tmp_path/'full';work.mkdir()
    expected=dict(algorithm='TEST_ONLY',files={})
    # Point digests are a virtual artifact store; JSON manifests and receipts
    # are real bytes. These tests exercise coverage and attestation joining,
    # not the separately tested physical derivative arithmetic.
    registry={}
    def sha(path):
        if path in registry:return registry[path]
        return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    def verify(record):
        for name,digest in record['files'].items():
            if sha(tmp_path/name)!=digest:raise RuntimeError('changed artifact')
    p=SimpleNamespace(WORK=work,binding=lambda:expected,file_key=lambda path:path.relative_to(tmp_path).as_posix(),
                      values=SimpleNamespace(sha=sha,verify_binding=verify))
    def make(indices):
        endpoints=sorted({n for i in indices for n in (i,i+1)})
        files={}
        for stage,points in (('endpoint',endpoints),('midpoint',indices)):
            for i in points:
                for ext in ('json','npz'):
                    path=work/f'{stage}_{i:03d}.{ext}'
                    registry.setdefault(path,hashlib.sha256(str(path).encode()).hexdigest().upper())
                    files[p.file_key(path)]=registry[path]
        directory=work/'batches'/f'{indices[0]:03d}_{indices[-1]:03d}';directory.mkdir(parents=True)
        manifest=dict(binding=expected,endpoints=endpoints,midpoints=indices,files=files)
        mp=directory/'manifest.json';mp.write_text(json.dumps(manifest))
        receipt=dict(byte_identical=True,independent_recomputation=True,points=len(endpoints)+len(indices),manifest_SHA256=sha(mp))
        rp=directory/'reproduction.json';rp.write_text(json.dumps(receipt))
        return mp,rp
    return p,registry,make


def test_overlapping_batches_prove_exact_full_coverage_without_double_counting(batches):
    p,_,make=batches
    groups=[list(range(185)),list(range(185,370))]
    for group in groups:make(group)
    manifest,proofs=aggregate.aggregate_batches(p,groups)
    assert manifest['endpoints']==list(range(371)) and manifest['midpoints']==list(range(370))
    assert len(manifest['files'])==1482 and len(proofs)==4
    assert manifest['all_741_DF_covered'] is True and manifest['physical_Z1_recertified'] is False


def test_incomplete_independent_coverage_is_not_promoted(batches):
    p,_,make=batches
    make(list(range(369)))
    with pytest.raises(RuntimeError,match='all 741'):
        aggregate.aggregate_batches(p,[list(range(369))])


def test_cache_reuse_cannot_replace_an_independent_batch(batches):
    p,_,make=batches
    _,path=make([0])
    receipt=json.loads(path.read_text());receipt['independent_recomputation']=False
    path.write_text(json.dumps(receipt))
    with pytest.raises(RuntimeError,match='independently reproduced batch'):
        aggregate.aggregate_batches(p,[[0]])


def test_changed_point_artifact_invalidates_its_batch(batches):
    p,registry,make=batches
    make([0]);registry[next(iter(registry))]='CHANGED'
    with pytest.raises(RuntimeError,match='changed artifact'):
        aggregate.aggregate_batches(p,[[0]])


def test_batch_manifest_change_invalidates_receipt(batches):
    p,_,make=batches
    path,_=make([0]);path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(RuntimeError,match='independently reproduced batch'):
        aggregate.aggregate_batches(p,[[0]])
