"""Catalog/replay invariants, including browser/Python number semantics."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from bhtracker import candidate_atlas as atlas


def fixture():
    def event(name, ra, tier):
        return dict(event_id=name, known_aliases=['INVENTED-ALIAS-'+name], cohorts=['INVENTED_COHORT'],
            tier=tier, quality_flags=['REVIEW_ONLY'], provenance=[{'url':'https://example.invalid/invented'}],
            source_direction=dict(role='SOURCE_EVENT_DIRECTION',ra_deg=ra,dec_deg=-30.0 if ra is not None else None,
                epoch=None,uncertainty=None,frame='catalog_equatorial',equinox='J2000'),
            lens=dict.fromkeys(atlas.LENS_FIELDS),map_eligibility=dict(sky_marker=ra is not None,
                three_dimensional=False,propagate_position=False),
            accepted_engine_black_hole=False,new_black_hole_interpretation=False)
    return dict(schema_version=atlas.SCHEMA,metadata=dict(formal_BHSM_repository=atlas.REPOSITORY,status='INVENTED_TEST_ONLY'),
        events=[event('INVENTED-02',None,'REVIEW_REQUIRED'),event('INVENTED-01',267.0,'BLACK_HOLE_SEARCH_TARGET')])


class CandidateAtlasTests(unittest.TestCase):
    def test_unknown_quantities_stay_null_and_no_mass_is_inferred(self):
        data=atlas.validate_inventory(fixture()); result=atlas.summary(data)
        self.assertEqual(result['selected'],2)
        self.assertEqual(result['source_directions'],1)
        self.assertIsNone(result['independently_inferred_lens_mass'])
        for field in atlas.LENS_FIELDS:
            changed=deepcopy(data);changed['events'][0]['lens'][field]=0
            with self.subTest(field=field),self.assertRaises(ValueError):atlas.validate_inventory(changed)

    def test_event_direction_does_not_supply_lens_epoch_or_propagation(self):
        for key,value in [('three_dimensional',True),('propagate_position',True),('sky_marker',False)]:
            changed=fixture();changed['events'][1]['map_eligibility'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):atlas.validate_inventory(changed)
        changed=fixture();changed['events'][1]['source_direction']['role']='LENS_POSITION'
        with self.assertRaises(ValueError):atlas.validate_inventory(changed)

    def test_invalid_coordinate_bool_missing_counterpart_and_duplicates(self):
        for ra in (True,360,float('inf'),-1):
            changed=fixture();changed['events'][1]['source_direction']['ra_deg']=ra
            with self.subTest(ra=ra),self.assertRaises(ValueError):atlas.validate_inventory(changed)
        changed=fixture();changed['events'][1]['source_direction']['dec_deg']=None
        with self.assertRaises(ValueError):atlas.validate_inventory(changed)
        changed=fixture();changed['events'].append(deepcopy(changed['events'][0]))
        with self.assertRaises(ValueError):atlas.validate_inventory(changed)

    def test_filters_sort_missing_direction_and_no_outcome_dropped(self):
        data=fixture();before=deepcopy(data)
        for sort in ('event_id','ra_deg','tier'):
            self.assertEqual([e['event_id']for e in atlas.filter_events(data,{**atlas.default_filters(),'sort':sort})],
                             ['INVENTED-01','INVENTED-02'])
        selected=atlas.filter_events(data,{**atlas.default_filters(),'query':'alias-invented-01'})
        self.assertEqual(len(selected),1)
        self.assertEqual(len(atlas.filter_events(data,{**atlas.default_filters(),'tier':'REVIEW_REQUIRED'})),1)
        self.assertEqual(len(atlas.filter_events(data,{**atlas.default_filters(),'cohort':'UNAVAILABLE'})),0)
        self.assertEqual(data,before)

    def test_replay_preserves_CRLF_UTF8_and_all_unselected_records(self):
        data=fixture();data['metadata']['note']='INVENTED Unicode σ'
        text=json.dumps(data,ensure_ascii=False,indent=2).replace('\n','\r\n')+'\r\n'
        bundle=atlas.create_replay(text,{**atlas.default_filters(),'tier':'BLACK_HOLE_SEARCH_TARGET'},created_utc='2026-10-23T00:00:00Z')
        restored=atlas.validate_replay(bundle)
        self.assertEqual(restored['inventory_json'].encode(),text.encode())
        self.assertEqual(len(restored['inventory']['events']),2)
        self.assertEqual(len(restored['filtered_events']),1)
        self.assertEqual(restored['inventory_utf8_sha256'],hashlib.sha256(text.encode()).hexdigest())

    def test_replay_rejects_byte_tamper_and_rehashed_filter_or_record_tamper(self):
        bundle=atlas.create_replay(json.dumps(fixture()))
        changed=deepcopy(bundle);changed['payload_json']+=' '
        with self.assertRaises(ValueError):atlas.validate_replay(changed)
        for mode in ('ids','filters','records','inventory','repository'):
            changed=deepcopy(bundle);p=json.loads(changed['payload_json'])
            if mode=='ids':p['selected_event_ids'].pop()
            elif mode=='filters':p['filters']['tier']='REVIEW_REQUIRED'
            elif mode=='records':p['filtered_events'][0]['quality_flags'].append('ALTERED')
            elif mode=='inventory':p['inventory_json']+=' '
            else:p['repository']='https://example.invalid'
            changed['payload_json']=json.dumps(p);changed['payload_sha256']=atlas.text_sha256(changed['payload_json'])
            with self.subTest(mode=mode),self.assertRaises(ValueError):atlas.validate_replay(changed)

    def test_browser_numeric_spelling_is_allowed_but_booleans_are_distinct(self):
        bundle=atlas.create_replay(json.dumps(fixture()))
        p=json.loads(bundle['payload_json']);p['filtered_events'][0]['source_direction']['ra_deg']=267
        bundle['payload_json']=json.dumps(p);bundle['payload_sha256']=atlas.text_sha256(bundle['payload_json'])
        atlas.validate_replay(bundle)
        p['filtered_events'][0]['map_eligibility']['sky_marker']=1
        bundle['payload_json']=json.dumps(p);bundle['payload_sha256']=atlas.text_sha256(bundle['payload_json'])
        with self.assertRaises(ValueError):atlas.validate_replay(bundle)

    def test_literature_benchmark_cannot_be_own_engine_recovery(self):
        data=fixture();b=deepcopy(data['events'][1]);b.update(event_id='INVENTED-BENCHMARK',
            classification_source='LITERATURE',tracker_recovery_status='NOT_ESTABLISHED_NUMERICAL_STAGE_UNRESOLVED',
            cohorts=['SEPARATE_KNOWN_SYSTEM_BENCHMARK'])
        data['benchmarks']=[b];atlas.validate_inventory(data)
        self.assertEqual(atlas.summary(data)['separate_benchmarks'],1)
        self.assertEqual(atlas.summary(data)['events'],2)
        for key,value in [('accepted_engine_black_hole',True),('classification_source','ENGINE'),
                          ('tracker_recovery_status','CONFIRMED')]:
            changed=deepcopy(data);changed['benchmarks'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):atlas.validate_inventory(changed)

    def test_strict_finite_JSON(self):
        for value in ('{"a":1,"a":2}','{"a":NaN}','{"a":1e999}','{"constructor":0}',
                      '{"catalog_id":9007199254740993}'):
            with self.subTest(value=value),self.assertRaises(ValueError):atlas.read_json(value)

    def test_null_location_conflicting_counts_and_replay_source_raise_valueerror(self):
        for bad in (None,[]):
            data=fixture();data['events'][0]['map_eligibility']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):atlas.validate_inventory(data)
        data=fixture();data['metadata']['counts']=dict(unique_events=2,sky_markers=1,new_BH_interpretations=0,
            independently_measured_lens_mass_in_atlas=0,tier_counts={t:sum(e['tier']==t for e in data['events'])for t in atlas.TIERS})
        atlas.validate_inventory(data)
        data['metadata']['counts']['independently_measured_lens_mass_in_atlas']=1
        with self.assertRaises(ValueError):atlas.validate_inventory(data)
        bundle=atlas.create_replay(json.dumps(fixture()));payload=json.loads(bundle['payload_json'])
        payload['data_source']['inventory_utf8_sha256']='0'*64
        bundle['payload_json']=json.dumps(payload);bundle['payload_sha256']=atlas.text_sha256(bundle['payload_json'])
        with self.assertRaises(ValueError):atlas.validate_replay(bundle)

    def test_file_loading_does_not_normalize_native_text(self):
        text=json.dumps(fixture(),indent=2).replace('\n','\r\n')+'\r\n'
        with tempfile.TemporaryDirectory()as directory:
            path=Path(directory)/'inventory.json';path.write_bytes(text.encode())
            _,loaded=atlas.load_inventory(path)
            self.assertEqual(loaded,text)


if __name__=='__main__':unittest.main()
