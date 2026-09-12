"""Guard against substituting point-only fields for uniform midpoint inputs."""
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_affine_hs_midpoint_domain as pilot


@pytest.mark.parametrize('uniform,paired',[(False,True),(True,False)])
def test_point_only_or_unpaired_field_is_rejected_before_domain_assembly(tmp_path,monkeypatch,uniform,paired):
    monkeypatch.setattr(pilot.values,'WORK',tmp_path)
    monkeypatch.setattr(pilot.values,'load_inputs',lambda index:dict(binding={}))
    directory=tmp_path/'endpoint_013';directory.mkdir()
    data=directory/'value.npz';data.write_bytes(b'unread invalid array fixture')
    report=dict(validation_passed=True,uniform_physical_value_enclosed=uniform,
        scope='SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE',positive_physical_G_norm=True,physical_G_norm_lower_rational='1/10')
    record=dict(algorithm=pilot.values.ALGORITHM,endpoint=13,binding={},report=report,data_SHA256=pilot.p.values.sha(data))
    path=directory/'record.json';path.write_bytes(pilot.p.geometry.encoded(record))
    (directory/'reproduction.json').write_text(json.dumps(dict(record_SHA256=pilot.p.values.sha(path),
        byte_identical=True,independent_recomputation=paired)))
    with pytest.raises(RuntimeError,match='paired uniform'):pilot.load_endpoint(13)
