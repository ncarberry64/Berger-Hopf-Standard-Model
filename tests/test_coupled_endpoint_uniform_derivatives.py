"""Endpoint derivatives require the full endpoint field and inherited response."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as pilot


def test_point_field_cannot_replace_the_uniform_endpoint_field(tmp_path,monkeypatch):
    monkeypatch.setattr(pilot.values,'WORK',tmp_path)
    monkeypatch.setattr(pilot.values,'load_inputs',lambda index:dict(binding={}))
    directory=tmp_path/'endpoint_013';directory.mkdir()
    record=dict(binding={},algorithm=pilot.values.ALGORITHM,endpoint=13,report=dict(
        validation_passed=True,uniform_physical_value_enclosed=False))
    (directory/'record.json').write_text(json.dumps(record));(directory/'reproduction.json').write_text('{}')
    with pytest.raises(RuntimeError,match='complete endpoint tube'):pilot.load_inputs(13)


def test_full_endpoint_basis_cannot_claim_a_midpoint_domain(monkeypatch):
    visits=[]
    def batch(source,start,stop):
        visits.extend(range(start,stop))
        return np.full((99,stop-start),arb(1)),np.full((2,62,stop-start),arb(0)),[]
    monkeypatch.setattr(pilot,'evaluate_batch',batch)
    monkeypatch.setattr(pilot.p,'verify_sources',lambda binding:None)
    arrays,report=pilot.evaluate(dict(raw_domain=np.full(99,arb(0)),binding={}))
    assert visits==list(range(99)) and arrays['derivative'].shape==(99,99)
    assert report['uniform_physical_first_derivatives_enclosed']
    assert report['actual_HS_midpoint_domain_enclosed'] is False
    assert report['scope']=='SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE'
    assert report['physical_quotient_identified'] is False
