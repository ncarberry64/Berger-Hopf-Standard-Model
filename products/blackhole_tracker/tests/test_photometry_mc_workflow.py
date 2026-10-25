"""Invented workflow/state controls, including no-arithmetic tracing equivalence."""
from copy import deepcopy
from io import BytesIO
import base64
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import numpy as np
from bhtracker.observations import UnresolvedPhotometry
from bhtracker import photometry,photometry_inference as kernel
from bhtracker import photometry_mc as mc,photometry_mc_replay as replay
from bhtracker._photometry_mc_trace import capture_evaluation_states,evaluate_saved_state,TRACE_SCHEMA


def data_fixture(fraction=.65,large=False):
    times=np.r_[np.linspace(900,980,10),np.linspace(990,1030,30),np.linspace(1050,1160,10)]
    offset=2450000. if large else 0.
    t0=1010.+offset;times=times+offset
    u2=.3**2+((times-t0)/25.)**2
    amp=(u2+2)/np.sqrt(u2*(u2+4))
    magnitudes=18.-2.5*np.log10(1+fraction*(amp-1))
    origin=0. if large else 2450000.
    document={'schema':'bhsm_unresolved_observations/1','observable':'apparent_magnitude','common_numeric_origin_jd':origin,
        'metadata':{'synthetic':True,'role':'WHOLLY_INVENTED_ENGINEERING_CONTROL'},'sources':[],'transformations':[],
        'instruments':{'Aé':{'filter':'I','calibration':'Wholly invented','time':{'reference':'HJD','unit':'day','numeric_origin_jd':origin,'clock_scale':'UNSPECIFIED'}}},
        'rows':[{'source_row_id':f'INVENTED:é:{i}','instrument':'Aé','native_time':float(t),'magnitude':float(y),'magnitude_error':.025,'quality_flags':[]} for i,(t,y) in enumerate(zip(times,magnitudes))]}
    parameters={'t0':t0,'tE_days':25.,'u0':.3,'instruments':{'Aé':{'baseline_magnitude':18.,'source_fraction':fraction}}}
    return UnresolvedPhotometry(document),parameters


def strip_trace(value):
    if isinstance(value,dict):return {k:strip_trace(v) for k,v in value.items() if k!='saved_numerical_state'}
    if isinstance(value,list):return [strip_trace(v) for v in value]
    return value


def manual_profile(data,parameters):
    """A finite feasible state, not an optimizer result; only forward evaluation."""
    model=photometry._Model(data,1.,False,False)
    x=np.array([(parameters['t0']-model.center)/model.scale,math.log(parameters['tE_days']),math.log(parameters['u0']),18.,parameters['instruments']['Aé']['source_fraction']])
    decoded=model.decode(x);residual=model.evaluate(x);q=float(residual@residual)
    def search(serial):
        trace={'schema':TRACE_SCHEMA,'search_call_index':serial,'trial_index':0,
            'full_transformed_state_hex':[float(v).hex() for v in x],'parameter_names':model.parameter_names,
            'time_center_hex':model.center.hex(),'time_scale_hex':model.scale.hex(),'numeric_origin_jd_hex':data.common_origin_jd.hex(),
            'noise_scale_hex':float(1.).hex(),'equal_instrument_weight':False,'allow_negative_blend':False,'paired_physical_parameters':deepcopy(decoded)}
        trial={'start':0,'objective_chi_square':q,'parameters':deepcopy(decoded),'saved_numerical_state':trace,'resolved':True}
        return {'objective_chi_square':q,'parameters':deepcopy(decoded),'saved_numerical_state':deepcopy(trace),'starts':[trial],'global_optimality_certified':False}
    free=search(2);null=search(1)
    return {'input_sha256':data.sha256,'parameter':'tE_days','value':25.,'status':'INVENTED_FEASIBLE_STATE_NO_OPTIMIZATION',
        'statistic':0.,'raw_profile_delta_chi_square':0.,'unrestricted':free,'null_constrained':null,
        'all_unrestricted_searches':[free],'physical_identification':{'mass_msun':None,'lens_distance_pc':None,'theta_E_mas':None,'pi_E':None}}


def invented_child(parent,seed):
    # Reconstruct deterministic supplied magnitudes; do not call an RNG.
    doc=parent.to_dict();doc['sources']=[]
    doc['metadata']={'synthetic':True,'kind':'PARAMETRIC_BOOTSTRAP_MAGNITUDES','parent_input_sha256':parent.sha256,
        'inherited_instrument_metadata_role':'Parent time/error/calibration context only; every child brightness is synthetic and original source files remain with the immutable parent.'}
    doc['transformations']=[{'operation':'SYNTHETIC_MAGNITUDE_REPLACEMENT','parent_input_sha256':parent.sha256,'all_rows_replaced':True,'original_source_files_embedded':False}]
    token=mc.digest(json.dumps(seed,separators=(',',':')).encode())[:24]
    for i,row in enumerate(doc['rows']):
        row['bootstrap_parent_source_row_id']=row['source_row_id'];row['source_row_id']=f'SYNTHETIC:BOOTSTRAP:{token}:{i}'
        row['magnitude']+=.001*math.sin(i);row['quality_flags']=[*row['quality_flags'],'SYNTHETIC_MAGNITUDE']
    return UnresolvedPhotometry(doc)


def mocked_mc(data,parameter,value,*,entropy,audit_callback,**options):
    _,parameters=data_fixture(1.,True)
    parameters['t0']=1010. if data.common_origin_jd else 2451010.
    observed=manual_profile(data,parameters);observed.update(parameter=parameter,value=value)
    seeds=kernel._seed_slots(entropy,parameter,value,199)
    audit_callback('OBSERVED_PROFILE',-1,observed)
    child=invented_child(data,seeds[0]);audit_callback('GENERATED',0,child.to_dict())
    fitted=manual_profile(child,parameters);fitted.update(parameter=parameter,value=value)
    audit_callback('FITTED',0,fitted)
    slots=[{'slot':i,'seed':seed,'status':'NOT_ATTEMPTED_UNKNOWN'} for i,seed in enumerate(seeds)]
    slots[0].update(status='ORDERING_UNRESOLVED_UNKNOWN',input_sha256=child.sha256,statistic=0.,numerical_status=fitted['status'])
    return {'schema':kernel.SCHEMA,'kind':'NULL_CONSTRAINED_NUISANCE_PLUGIN_BOOTSTRAP_APPROXIMATE','input_sha256':data.sha256,
        'parameter':parameter,'value':value,'confidence_level':.95,'rank_bounds':kernel.rank_p_bounds(0,199),
        'observed_profile':observed,'slots':slots,'audit_failure':None,'attempted_slots':1,'coverage_claim':False}


class MCWorkflowControls(unittest.TestCase):
    def setUp(self):
        base=os.environ.get('BHSM_MC_APP_TEST_ARTIFACT_DIR')
        if base:self.root=Path(tempfile.mkdtemp(prefix=self._testMethodName+'_',dir=base))
        else:
            self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)

    def completed_fixture(self,large=True):
        data,_=data_fixture(1.,large)
        original=(json.dumps(data.to_dict(),indent=2,ensure_ascii=False)+'\n').replace('\n','\r\n').encode('utf-8')
        workspace=mc.MCWorkspace(original,{'tE_days':[25.]},[8675309],self.root/'workspace')
        with patch.object(mc,'monte_carlo_ordinate',side_effect=mocked_mc):result=workspace._execute()
        mc.save(workspace.directory/'result.json',result)
        return workspace,original

    def test_01_plan_is_no_fit_exact_fixed_method_and199slots(self):
        data,_=data_fixture();original=mc.canonical(data.to_dict())
        with patch.object(mc,'monte_carlo_ordinate',side_effect=AssertionError('plan must not fit')):
            value=mc.plan({'input_base64':base64.b64encode(original).decode(),'grids':{'tE_days':[25.,50.],'u0':[.3]},'entropy':[1,2]})
        self.assertEqual(value['analysis_optimizer_or_RNG_calls'],0)
        self.assertEqual(value['summary']['input_utf8_sha256'],mc.digest(original))
        self.assertEqual(value['request']['method'],mc.METHOD)
        self.assertEqual(len(value['request']['nodes']),3)
        self.assertTrue(all(len(n['all199_seed_slots'])==199 for n in value['request']['nodes']))
        self.assertEqual(value['request']['evidence_scope']['validation_status'],'PENDING')

    def test_02_invalid_fields_booleans_domains_and_duplicate_nodes_refuse(self):
        data,_=data_fixture();raw=mc.canonical(data.to_dict())
        for grids in ({'mass_msun':[7.]},{'u0':[True]},{'u0':[.3,.3]},{'tE_days':[0.]},{'u0':[.5,.2]}):
            with self.assertRaises(ValueError):mc.make_request(raw,grids,[1])
        with self.assertRaises(ValueError):mc.make_request(raw,{'u0':[.3]},[True])
        with self.assertRaises(ValueError):mc.make_request(raw,{'u0':[.3]},[1],wall_seconds=True)

    def test_03_existing_workspace_refuses_without_overwrite(self):
        data,_=data_fixture();out=self.root/'prior';out.mkdir();p=out/'keep';p.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):mc.MCWorkspace(mc.canonical(data.to_dict()),{'u0':[.3]},[1],out)
        self.assertEqual(p.read_bytes(),b'keep');self.assertEqual(list(out.iterdir()),[p])

    def test_04_rawCRLF_UTF8_generated_audit_export_fullnumerical_roundtrip(self):
        workspace,original=self.completed_fixture()
        blob=replay.export_workspace(workspace.directory)
        with zipfile.ZipFile(BytesIO(blob)) as archive:self.assertEqual(archive.read('input.original.utf8.json'),original)
        checked=replay.replay_bundle(blob,mode='numerical')
        self.assertTrue(checked['verification']['passed']);self.assertGreater(checked['verification']['exact_vector_states_evaluated'],0)
        self.assertEqual(checked['verification']['maximum_absolute_objective_difference'],0.)
        self.assertEqual(checked['verification']['optimizer_or_RNG_calls'],0)
        self.assertEqual(checked['summary']['nodes'][0]['decision'],'UNRESOLVED')
        self.assertFalse(checked['evidence_scope']['global_optimum_certified'])

    def test_05_integrity_is_distinct_and_changed_method_refuses_numeric(self):
        workspace,_=self.completed_fixture();blob=replay.export_workspace(workspace.directory)
        altered=deepcopy(mc.method_pins());altered['photometry.py']['sha256']='0'*64
        with patch.object(mc,'method_pins',return_value=altered):
            quick=replay.replay_bundle(blob,mode='integrity')
            self.assertEqual(quick['verification']['mode'],'INTEGRITY_ONLY');self.assertFalse(quick['verification']['method_sources_match'])
            with self.assertRaisesRegex(ValueError,'source changed'):replay.replay_bundle(blob,mode='numerical')

    def test_06_exact_bound_f1_largeJD_does_not_encode_clip_or_reprofile(self):
        data,physical=data_fixture(1.,True);profile=manual_profile(data,physical)
        trace=profile['unrestricted']['saved_numerical_state']
        self.assertEqual(float.fromhex(trace['full_transformed_state_hex'][-1]),1.)
        with patch.object(photometry._Model,'encode',side_effect=AssertionError('must not reencode physical states')):
            checked=replay.numerical_profile(data,profile,deadline=float('inf'))
        self.assertEqual(checked['maximum_absolute_objective_difference'],0.)
        changed=deepcopy(trace);changed['numeric_origin_jd_hex']=float(1.).hex()
        with self.assertRaises(ValueError):evaluate_saved_state(data,changed,profile['unrestricted']['parameters'])

    def test_07_missing_exact_state_or_changed_pair_refuses_full_replay(self):
        data,physical=data_fixture(1.,True);profile=manual_profile(data,physical)
        del profile['unrestricted']['saved_numerical_state']
        with self.assertRaisesRegex(ValueError,'exact numerical state'):replay.numerical_profile(data,profile,deadline=float('inf'))
        profile=manual_profile(data,physical);profile['unrestricted']['parameters']['t0']+=.0001
        with self.assertRaisesRegex(ValueError,'state pair'):replay.numerical_profile(data,profile,deadline=float('inf'))

    def test_08_cancel_before_child_preserves_all_unknown_and_no_retry(self):
        data,_=data_fixture();workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'u0':[.3,.6]},[1],self.root/'cancel')
        workspace.cancel()
        with patch.object(mc.subprocess,'Popen',side_effect=AssertionError('cancelled before launch')) as launching:result=workspace.run()
        self.assertEqual(launching.call_count,0);self.assertEqual(result['status'],'cancelled')
        self.assertEqual(len(result['nodes']),2);self.assertTrue(all(v['rank_bounds']['unknown']==199 for v in result['nodes'].values()))
        with self.assertRaises(FileExistsError):workspace.run()
        quick=replay.replay_bundle(replay.export_workspace(workspace.directory),mode='integrity')
        self.assertEqual(quick['verification']['mode'],'INTEGRITY_ONLY')

    def test_09_hard_wall_terminates_active_child_and_retains_unknown(self):
        data,_=data_fixture();workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'u0':[.3]},[1],self.root/'timeout',wall_seconds=1)
        class Child:
            returncode=None
            def poll(self):return self.returncode
            def terminate(self):self.returncode=-15
            def wait(self,timeout=None):return self.returncode
        child=Child();clock=iter([0.,2.,2.,2.,2.,2.])
        with patch.object(mc.subprocess,'Popen',return_value=child),patch.object(mc.time,'monotonic',side_effect=lambda:next(clock)):
            result=workspace.run()
        self.assertEqual(child.returncode,-15);self.assertEqual(result['status'],'failed')
        self.assertIn('HARD_WALL',result['failure']);self.assertEqual(result['nodes']['u0_000']['rank_bounds']['decision'],'UNRESOLVED')

    def test_10_numerical_replay_budget_and_bad_archive_fail_closed(self):
        workspace,_=self.completed_fixture();blob=replay.export_workspace(workspace.directory)
        with self.assertRaises(ValueError):replay.replay_bundle(blob,mode='numerical',max_states=1)
        with self.assertRaises((ValueError,zipfile.BadZipFile)):replay.replay_bundle(b'not a zip')
        data,physical=data_fixture();profile=manual_profile(data,physical)
        with self.assertRaises(TimeoutError):replay.numerical_profile(data,profile,deadline=-1.)

    def test_11_copied_store_is_byteexact_and_no_physical_promotion(self):
        package=Path(mc.__file__).resolve().parent
        research=package.parent/'research/validation_20261024/sqlite_audit_v1.py'
        if research.exists():self.assertEqual((package/'_photometry_mc_store.py').read_bytes(),research.read_bytes())
        self.assertTrue(all(value is None for value in mc.UNAVAILABLE.values()))
        self.assertIn('Berger-Hopf-Standard-Model',mc.EVIDENCE['project_citation']['repository_url'])

    def test_12_trace_binds_distinct_vectors_even_if_large_t0_rounds_equal(self):
        data,physical=data_fixture(1.,True);model=kernel._ProfiledModel(data)
        z=model.base.encode(physical)[model.keep];other=z.copy();other[0]=np.nextafter(other[0],np.inf)
        solutions=iter([SimpleNamespace(x=z.copy(),success=True,status=1,message='INVENTED_NO_OPTIMIZER',nfev=1),
                        SimpleNamespace(x=other.copy(),success=True,status=1,message='INVENTED_NO_OPTIMIZER',nfev=1)])
        with patch.object(kernel,'least_squares',side_effect=lambda *a,**k:next(solutions)),capture_evaluation_states():
            report,_=kernel._search(model,starts=2,extra_seeds=[z,other],only_extra_seeds=True)
        a,b=report['starts']
        self.assertEqual(a['parameters']['t0'],b['parameters']['t0'])
        self.assertNotEqual(a['saved_numerical_state']['full_transformed_state_hex'][0],b['saved_numerical_state']['full_transformed_state_hex'][0])
        self.assertEqual([a['saved_numerical_state']['trial_index'],b['saved_numerical_state']['trial_index']],[0,1])

    def test_13_observer_equivalence_bitexact_all_original_fields_calls_and_noise(self):
        # The only real invented MC exercise in this suite, with fixed199slots.
        # Boundary/largeJD and ordinary relative-origin controls are both retained.
        for fraction,large in ((.65,False),(1.,True)):
            data,_=data_fixture(fraction,large);snapshots=[];captured=None
            original_evaluate=photometry._Model.evaluate;original_least=kernel.least_squares;original_child=kernel._synthetic_document
            for tracing in (False,True):
                counts={'evaluate':0,'optimizer':0};children=[];events=[]
                def evaluating(self,*a,**k):counts['evaluate']+=1;return original_evaluate(self,*a,**k)
                def optimizing(*a,**k):counts['optimizer']+=1;return original_least(*a,**k)
                def generated(*a,**k):
                    value=original_child(*a,**k);children.append(value.sha256);return value
                with patch.object(photometry._Model,'evaluate',evaluating),patch.object(kernel,'least_squares',side_effect=optimizing),patch.object(kernel,'_synthetic_document',side_effect=generated):
                    if tracing:
                        with capture_evaluation_states():value=kernel.monte_carlo_ordinate(data,'tE_days',25.,entropy=[8675309,int(large)],audit_callback=lambda *args:events.append(deepcopy(args)),**mc.METHOD)
                    else:value=kernel.monte_carlo_ordinate(data,'tE_days',25.,entropy=[8675309,int(large)],audit_callback=lambda *args:events.append(deepcopy(args)),**mc.METHOD)
                snapshots.append((strip_trace(value),counts,children))
                mc.save(self.root/f'INVENTED_{int(large)}_tracing_{tracing}.json',{'result':value,'calls':counts,'generated_input_hashes':children})
                if tracing:captured=(deepcopy(value),events)
            self.assertEqual(mc.canonical(snapshots[0][0]),mc.canonical(snapshots[1][0]))
            self.assertEqual(snapshots[0][1:],snapshots[1][1:])
            # Recheck every actual observed/MC profile at its exact vector;
            # no optimization, RNG or request convention changes are needed.
            checked=[];generated={}
            for stage,slot,payload in captured[1]:
                if stage=='GENERATED':generated[slot]=UnresolvedPhotometry(payload)
                elif stage in ('OBSERVED_PROFILE','FITTED'):
                    checked.append(replay.numerical_profile(data if stage=='OBSERVED_PROFILE' else generated[slot],payload,deadline=float('inf')))
            self.assertTrue(checked);self.assertTrue(all(c['unique_finite_states_evaluated']>0 for c in checked))
            mc.save(self.root/f'INVENTED_{int(large)}_actual_trace_numerical_replay.json',{'input':data.to_dict(),'events':captured[1],
                'profiles':checked,'no_extra_optimization_or_RNG':True,
                'original_field_and_call_equivalence':True,'source_data_kind':'WHOLLY_INVENTED'})

    def test_14_streamed_export_cap_retains_prefix_and_original_workspace(self):
        workspace,original=self.completed_fixture();path=self.root/'capped.zip'
        with self.assertRaisesRegex(ValueError,'cap exceeded'):replay.export_workspace(workspace.directory,path,max_archive_bytes=64)
        self.assertLessEqual(path.stat().st_size,64)
        self.assertEqual((workspace.directory/'input.original.utf8.json').read_bytes(),original)
        with self.assertRaises(FileExistsError):replay.export_workspace(workspace.directory,path)

    def test_15_transient_Windows_progress_replace_is_bounded_not_audit_retry(self):
        data,_=data_fixture();workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'u0':[.3]},[1],self.root/'progress-race')
        replacing=mc.os.replace;calls=[]
        def transient(*args):
            calls.append(args)
            if len(calls)==1:raise PermissionError('INVENTED_WINDOWS_READER_LOCK')
            return replacing(*args)
        with patch.object(mc.os,'replace',side_effect=transient),patch.object(mc.time,'sleep') as sleeping:
            workspace._progress(stage='INVENTED_UI_STAGE')
        self.assertEqual(len(calls),2);sleeping.assert_called_once_with(.005)
        self.assertEqual(workspace.status()['stage'],'INVENTED_UI_STAGE')
        with patch.object(mc.os,'replace',side_effect=PermissionError('INVENTED_PERSISTENT_DENIAL')) as failure,patch.object(mc.time,'sleep'):
            with self.assertRaises(PermissionError):workspace._progress(stage='NOT_COMMITTED')
        self.assertEqual(failure.call_count,10)

    def test_16_rehashed_result_cannot_replace_committed_final_ordinate(self):
        workspace,_=self.completed_fixture();blob=replay.export_workspace(workspace.directory)
        with zipfile.ZipFile(BytesIO(blob)) as archive:members={i.filename:archive.read(i) for i in archive.infolist()}
        result=json.loads(members['result.json']);result['nodes']['tE_days_000']['attempted_slots']=2
        members['result.json']=mc.canonical(result);manifest=json.loads(members['manifest.json'])
        manifest['files']['result.json']={'bytes':len(members['result.json']),'sha256':mc.digest(members['result.json'])}
        members['manifest.json']=mc.canonical(manifest);buffer=BytesIO()
        with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for name,value in members.items():archive.writestr(name,value)
        with self.assertRaisesRegex(ValueError,'committed final ordinate'):replay.replay_bundle(buffer.getvalue(),mode='integrity')

    def test_17_failed_final_commit_cannot_publish_an_uncommitted_node(self):
        data,_=data_fixture(1.,True);workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'tE_days':[25.]},[1],self.root/'failed-final')
        original_put=mc.store.AuditStore.put
        def committing(writer,case,parameter,slot,stage,value):
            if stage=='FINAL_ORDINATE':raise OSError('INVENTED_FINAL_COMMIT_FAILURE')
            return original_put(writer,case,parameter,slot,stage,value)
        with patch.object(mc,'monte_carlo_ordinate',side_effect=mocked_mc),patch.object(mc.store.AuditStore,'put',committing):result=workspace._execute()
        self.assertEqual(result['status'],'failed');self.assertIn('FINAL_COMMIT_FAILURE',result['failure'])
        self.assertIsNone(result['nodes']['tE_days_000']['observed_profile'])
        self.assertEqual(result['nodes']['tE_days_000']['rank_bounds']['unknown'],199)
        self.assertEqual(result['audit_verification']['missing_final_tests'],[['tE_days_000','tE_days']])

    def test_18_already_exited_child_still_obeys_postexit_deadline(self):
        workspace,_=self.completed_fixture()
        # Preserve worker evidence but remove the fixture-only authoritative
        # result; this new supervisor run owns its result file.
        (workspace.directory/'result.json').unlink()
        workspace.request['resources']['wall_seconds']=1
        # No child request is evaluated in this mock; budget checks precede
        # the deliberately mismatched fixture request/worker acceptance.
        class Child:
            returncode=0
            def poll(self):return 0
            def wait(self,timeout=None):return 0
        clock=iter([0.,2.,2.,2.,2.,2.])
        with patch.object(mc.subprocess,'Popen',return_value=Child()),patch.object(mc.time,'monotonic',side_effect=lambda:next(clock)):
            result=workspace.run()
        self.assertEqual(result['status'],'failed');self.assertIn('HARD_WALL_BUDGET_AFTER_WORKER_EXIT',result['failure'])

    def test_19_local_keyboard_interrupt_retains_cancelled_unknown_terminal(self):
        data,_=data_fixture();workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'u0':[.3]},[1],self.root/'interrupt')
        with patch.object(mc.subprocess,'Popen',side_effect=KeyboardInterrupt):result=workspace.run()
        self.assertEqual(result['status'],'cancelled');self.assertEqual(result['failure'],'CANCELLED_BY_LOCAL_INTERRUPT')
        self.assertEqual(result['nodes']['u0_000']['rank_bounds']['unknown'],199)
        self.assertTrue((workspace.directory/'result.json').is_file())

    def test_20_valid_unrelated_database_cannot_supply_recovered_same_grid_result(self):
        workspace,_=self.completed_fixture();data,_=data_fixture(1.,True);document=data.to_dict()
        document['rows'][0]['magnitude']+=.2
        other=mc.MCWorkspace(mc.canonical(document),{'tE_days':[25.]},[8675309],self.root/'other-input')
        source=workspace.directory/'audit.sqlite';destination=other.directory/'audit.sqlite'
        destination.write_bytes(source.read_bytes());original_pin=mc.file_pin(destination);other.cancel()
        with patch.object(mc.subprocess,'Popen',side_effect=AssertionError('no child for cancelled request')):result=other.run()
        self.assertIsNone(result['audit_database']);self.assertIsNone(result['nodes']['tE_days_000']['observed_profile'])
        self.assertFalse(result['audit_verification']['integrity_ok']);self.assertEqual(mc.file_pin(destination),original_pin)
        self.assertEqual(result['nodes']['tE_days_000']['rank_bounds']['unknown'],199)

    def test_21_last_slot_restore_deadline_cannot_return_completed_integrity(self):
        workspace,_=self.completed_fixture();blob=replay.export_workspace(workspace.directory);clock=[0.]
        original_restore=replay.restore_bootstrap
        def late_restore(*args):
            value=original_restore(*args);clock[0]=2.;return value
        with patch.object(replay.time,'monotonic',side_effect=lambda:clock[0]),patch.object(replay,'restore_bootstrap',side_effect=late_restore):
            with self.assertRaisesRegex(TimeoutError,'wall budget'):replay.replay_bundle(blob,mode='integrity',wall_seconds=1)

    def test_22_oversized_grid_is_refused_before_any_seed_roster_construction(self):
        data,_=data_fixture()
        with patch.object(mc,'_seed_slots',side_effect=AssertionError('oversized request must not derive seeds')) as deriving:
            with self.assertRaises(ValueError):mc.make_request(mc.canonical(data.to_dict()),{'u0':[.1+i*.1 for i in range(18)]},[1])
        self.assertEqual(deriving.call_count,0)

    def test_23_parent_terminal_counts_come_from_committed_child_not_stale_cache(self):
        workspace,_=self.completed_fixture();(workspace.directory/'result.json').unlink()
        workspace.progress.update(completed_nodes=0,committed_bootstrap_fits=0)
        class Child:
            returncode=0
            def poll(self):return 0
            def wait(self,timeout=None):return 0
        with patch.object(mc.subprocess,'Popen',return_value=Child()):value=workspace.run()
        self.assertEqual(value['status'],'complete');self.assertEqual(workspace.status()['completed_nodes'],1)
        self.assertEqual(workspace.status()['committed_bootstrap_fits'],1)
        self.assertEqual(value['committed_progress']['progress_counts_source'],'VERIFIED_COMMITTED_SQLITE_STAGES')
        self.assertEqual(value['committed_progress']['completed_nodes'],1)

    def test_24_no_verified_database_reports_unavailable_counts_not_zero_measurement(self):
        data,_=data_fixture();workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'u0':[.3]},[1],self.root/'no-database')
        value=workspace._recover_stopped('INVENTED_BEFORE_ANY_DATABASE',0.)
        self.assertIsNone(workspace.status()['completed_nodes']);self.assertIsNone(workspace.status()['committed_bootstrap_fits'])
        self.assertFalse(value['committed_progress']['progress_counts_available'])
        self.assertEqual(value['nodes']['u0_000']['rank_bounds']['unknown'],199)

    def test_25_recovered_partial_fit_counts_without_committed_final_node(self):
        data,_=data_fixture(1.,True);workspace=mc.MCWorkspace(mc.canonical(data.to_dict()),{'tE_days':[25.]},[1],self.root/'partial-counts')
        original_put=mc.store.AuditStore.put
        def committing(writer,case,parameter,slot,stage,value):
            if stage=='FINAL_ORDINATE':raise OSError('INVENTED_FINAL_COMMIT_FAILURE')
            return original_put(writer,case,parameter,slot,stage,value)
        with patch.object(mc,'monte_carlo_ordinate',side_effect=mocked_mc),patch.object(mc.store.AuditStore,'put',committing):workspace._execute()
        before=mc.file_pin(workspace.directory/'audit.sqlite');workspace.progress.update(completed_nodes=99,committed_bootstrap_fits=99)
        value=workspace._recover_stopped('INVENTED_PARTIAL_STOP',0.)
        self.assertEqual(value['committed_progress']['completed_nodes'],0)
        self.assertEqual(value['committed_progress']['committed_bootstrap_fits'],1)
        self.assertIsNone(value['nodes']['tE_days_000']['observed_profile'])
        self.assertEqual(mc.file_pin(workspace.directory/'audit.sqlite'),before)
