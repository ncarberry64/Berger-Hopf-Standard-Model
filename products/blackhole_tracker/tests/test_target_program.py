"""Investigation priorities must retain their evidence origin and open gates."""
import json
from urllib.request import urlopen
import pytest
from bhtracker import target_program as program
from test_local_app import service


def test_primary_candidate_is_not_an_engine_mass_or_new_discovery():
    value=program.target_program()
    target=value['primary_investigation_target']
    assert target['event_id']=='Gaia18ajz'
    assert target['investigation_category']=='Potential black hole'
    assert 'PREVIOUSLY_PUBLISHED' in target['novelty_status']
    assert all(v is None for v in target['engine_measurements'].values())
    assert len(target['literature_alternatives'])==8
    assert {r['mass_prior'] for r in target['literature_alternatives']}=={'StellarIMF','DarkIMF'}
    for mode in ('GO-','GO+'):
        for prior in ('StellarIMF','DarkIMF'):
            selected=[r for r in target['literature_alternatives'] if r['photometric_mode']==mode and r['mass_prior']==prior]
            assert {r['branch'] for r in selected}=={'Near','Far'}
            assert sum(r['published_branch_weight'] for r in selected)==pytest.approx(1)
    assert not value['publication_gate']['ready']
    assert not value['known_black_hole_validation_benchmark']['independent_engine_recovery_accepted']
    value['publication_gate']['ready']=True
    assert not program.target_program()['publication_gate']['ready']


def test_target_program_edits_are_refused(tmp_path,monkeypatch):
    edited=tmp_path/'target.json';raw=program.PROGRAM.read_bytes()
    edited.write_bytes(raw.replace(b'"ready": false',b'"ready": true'))
    monkeypatch.setattr(program,'PROGRAM',edited)
    with pytest.raises(ValueError,match='reviewed source'):program.target_program()


def test_installed_target_route_and_evidence_export_payload(service):
    for path in ('/targets','/targets/','/targets.js','/targets.css'):
        with urlopen(service+path,timeout=10) as response:
            assert response.status==200 and len(response.read())>100
    with urlopen(service+'/api/targets',timeout=10) as response:
        value=json.loads(response.read())
    assert value==program.target_program()
    assert value['primary_investigation_target']['engine_measurements']['mass_msun'] is None
