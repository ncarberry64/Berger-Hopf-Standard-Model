import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_selected_physical_hessian_pullbacks as producer


def test_aggregate_requires_current_physical_binding(tmp_path,monkeypatch):
    monkeypatch.setattr(producer.campaign,'load_inputs',lambda i: ({},{'current':1},'fingerprint'))
    monkeypatch.setattr(producer.campaign,'point_directory',lambda i:tmp_path)
    (tmp_path/'binding.json').write_text(json.dumps({'current':2}))
    with pytest.raises(ValueError,match='binding'):
        producer.aggregate_point(0)


def test_aggregate_refuses_partial_physical_rows(tmp_path,monkeypatch):
    monkeypatch.setattr(producer.campaign,'load_inputs',lambda i: ({},{'current':1},'fingerprint'))
    monkeypatch.setattr(producer.campaign,'point_directory',lambda i:tmp_path)
    (tmp_path/'binding.json').write_text(json.dumps({'current':1}))
    with pytest.raises(FileNotFoundError):
        producer.aggregate_point(0)
