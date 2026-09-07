import copy
import hashlib
import json
from pathlib import Path

import pytest
from tools.materialize_museum_science import ROOT, TARGET, COPIES, build, reviewed_outputs, source_bytes


def test_collection_preserves_all_sources_without_promoting_screens():
    payload = build()
    assert len(payload['particles']) == 19
    assert len(payload['prediction_ledger']) == 34
    assert not payload['FULL_BHSM_COMPLETE']
    assert payload['approved_outputs'] == []
    for p in (TARGET, *COPIES):
        assert json.loads(source_bytes(ROOT / p)) == payload
    assert any(r['sector'] == 'pmns_effective' and r['status'] == 'EFFECTIVE_EXTENSION_SCREEN' for r in payload['prediction_ledger'])


def fixture_entry(tmp_path, **changes):
    source = tmp_path / 'artifacts/reviewed.json'
    source.parent.mkdir(exist_ok=True)
    record = dict(classification='DERIVED_POINT_PREDICTION', value=.1, particle='muon', observable='a',
                  units='dimensionless', uncertainty_note='test fixture only',
                  action_version='test-action', domain='test-domain', source_revision='test-revision',
                  physical_promotion_ready=True, experimental_target_used=False,
                  gates=dict(gate7_closed=True, action_selected_external_state=True,
                             physical_units_fixed=True, ward_identity_closed=True,
                             renormalization_fixed=True, moment_definition_fixed=True))
    record.update(changes)
    source.write_text(json.dumps({'result': record}), encoding='utf-8')
    entry = dict(id='test-muon-a', exhibit='magnetic', particle='muon', observable='a',
                 label='test fixture', source_path='artifacts/reviewed.json', source_pointer='/result',
                 source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 reviewed_by='test fixture', review_record='test-only review')
    return {'outputs': [entry]}, source


def test_reviewed_output_requires_source_owned_promotion_and_no_fit(tmp_path):
    intake, source = fixture_entry(tmp_path)
    assert reviewed_outputs(tmp_path, intake)[0]['result']['value'] == .1
    for changes in [dict(classification='SCREEN'), dict(experimental_target_used=True),
                    dict(physical_promotion_ready=False), dict(gates={}), dict(particle='electron'),
                    dict(value=float('nan')), dict(classification='DERIVED_INTERVAL_PREDICTION', value=[2,1])]:
        intake, source = fixture_entry(tmp_path, **changes)
        with pytest.raises(ValueError):
            reviewed_outputs(tmp_path, intake)


def test_hash_drift_duplicates_and_missing_review_cannot_enter_the_museum(tmp_path):
    intake, source = fixture_entry(tmp_path)
    source.write_text(source.read_text(encoding='utf-8') + ' ', encoding='utf-8')
    with pytest.raises(ValueError, match='hash'):
        reviewed_outputs(tmp_path, intake)
    intake, _ = fixture_entry(tmp_path)
    duplicate = copy.deepcopy(intake)
    duplicate['outputs'] *= 2
    with pytest.raises(ValueError, match='Duplicate'):
        reviewed_outputs(tmp_path, duplicate)
    intake['outputs'][0]['review_record'] = ''
    with pytest.raises(ValueError, match='review'):
        reviewed_outputs(tmp_path, intake)


def test_primary_exhibits_collider_and_other_work_are_not_replaced_by_comparisons():
    page = (ROOT / 'museum/app/page.tsx').read_text(encoding='utf-8')
    primary = (ROOT / 'museum/app/prototype-science.tsx').read_text(encoding='utf-8')
    cosmic = ' '.join((ROOT / 'museum/app/cosmic-enclosure.tsx').read_text(encoding='utf-8').split())
    assert page.index('<PrototypeScience') < page.index('<ScienceGallery') < page.index('id="research-exhibit"')
    for title in ('Magnetic moments in motion', 'Standard Model predictions', 'Standard Model equivalence', 'Forces unifying', 'Collision theatre'):
        assert title in primary
    assert "['01', '08']" in page and "useState('01')" in page
    theatre = (ROOT / 'museum/app/collision-theatre.tsx').read_text(encoding='utf-8')
    assert 'collisionDemo(' in theatre and 'CMS' in theatre
    assert 'SIMULATED COLLISION' in theatre
    assert 'Decay channel stability' not in primary and 'Full magnetic-moment tracker' not in primary
    magnetic = (ROOT / 'museum/app/magnetic-lab.tsx').read_text(encoding='utf-8')
    assert 'references.magnetic.map' in magnetic and 'row.moment.toExponential' in magnetic
    assert 'larmorHz(row.moment, 0.1)' in magnetic
    assert 'onPointerMove' not in magnetic and 'setMagnet' not in magnetic
    assert 'row.uncertainty' in magnetic and 'vector lengths are normalized' in magnetic
    assert '<CosmicEnclosure motion={motion}' in page
    assert page.index('cosmologyExhibit.title') < page.index('<CosmicEnclosure') < page.index('<footer>')
    for text in ('White-hole surface release', 'Cooling, flows and active topology', 'Smooth surface / heat death', 'SPECULATIVE CONCEPTUAL SIMULATION', 'not observational data'):
        assert text in cosmic
