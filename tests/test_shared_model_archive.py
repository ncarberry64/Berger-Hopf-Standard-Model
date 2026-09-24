import importlib.util
import json
from pathlib import Path
import pytest


def module():
    path=Path(__file__).resolve().parents[1]/'scripts/freeze_n12_gate7_shared_models.py'
    spec=importlib.util.spec_from_file_location('freeze_shared',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def test_parts_reconstruct_exactly_and_detect_changed_chunk(tmp_path):
    m=module();a=tmp_path/'first';b=tmp_path/'repeat'
    a.write_bytes(bytes(range(256))*3);b.write_bytes(a.read_bytes())
    record=m.split_verified(a,b,tmp_path/'frozen',100)
    assert record['logical_bytes']==768 and len(record['parts'])==8
    m.restore_archive(tmp_path/'frozen',tmp_path/'restored')
    assert (tmp_path/'restored').read_bytes()==a.read_bytes()
    (tmp_path/'frozen'/record['parts'][0]['file']).write_bytes(b'bad')
    with pytest.raises(ValueError):m.restore_archive(tmp_path/'frozen',tmp_path/'bad_restore')


def test_a_repeat_cannot_be_the_same_file_or_changed_bytes(tmp_path):
    m=module();a=tmp_path/'first';b=tmp_path/'repeat'
    a.write_bytes(b'first');b.write_bytes(b'changed')
    with pytest.raises(ValueError):m.split_verified(a,a,tmp_path/'same')
    with pytest.raises(ValueError):m.split_verified(a,b,tmp_path/'different')


def test_family_binding_rejects_a_different_value_family_or_radius(tmp_path):
    m=module();base=tmp_path/'artifacts/flagship_integration'
    record=base/'.coupled_endpoint_uniform_df_work/endpoint_013/record.json'
    record.parent.mkdir(parents=True)
    tails=['.affine_eigenpair_pilot_work/endpoint_013/eigenpair.npz',
           '.affine_physical_value_pilot_work/endpoint_013/value.npz']
    paths=[base/tail for tail in tails]
    bindings={'artifacts/flagship_integration/'+tail:str(i) for i,tail in enumerate(tails)}
    data={'binding':{'files':bindings},'radius_longitudinal_rational':'1/8',
          'radius_transverse_rational':'1/16'}
    record.write_text(json.dumps(data))
    metadata={'site':'left','radius_exact':['1/8','1/16'],
              'source_SHA256':{str(record):'record',**{str(p):str(i) for i,p in enumerate(paths)}}}
    assert len(m.verify_site_binding(metadata)['same_family_data'])==2
    bindings['artifacts/flagship_integration/'+tails[1]]='different-family'
    record.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='different physical-family'):
        m.verify_site_binding(metadata)
    bindings['artifacts/flagship_integration/'+tails[1]]='1'
    data['radius_transverse_rational']='1/32'
    record.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='unchanged original radii'):
        m.verify_site_binding(metadata)
