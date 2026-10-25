"""Invented supervisor/storage/count controls; no model or confirmation draws."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import os
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[1]/"research/validation_20261024/confirm_photometry_v2.py"
spec=importlib.util.spec_from_file_location("confirmation_driver_controls",SOURCE)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)


class TestConfirmationSupervisor(unittest.TestCase):
    def setUp(self):
        root=os.environ.get("BHSM_CONFIRM_TEST_ARTIFACT_DIR")
        if root:
            self.directory=Path(tempfile.mkdtemp(prefix=self._testMethodName+"_",dir=root))
        else:
            self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.directory=Path(self.temp.name)

    def prepare_fake(self):
        freeze={"cases":driver.roster(),"initial_ledger":driver.initial_ledger(driver.roster()),"source_pins":[],"parents":[],
            "protocol":{"truths":[],"resources":{"whole_campaign_wall_seconds":20,"whole_output_bytes_including_sidecars":1024**3}}}
        path=self.directory/"freeze.json";driver.save(path,freeze)
        admission=self.directory/"admission.json";driver.save(admission,{"confirmation_authorized":True,"freeze_sha256":driver.pin(path)["sha256"]})
        return SimpleNamespace(freeze=str(path),admission=str(admission),output=str(self.directory/"output"))

    def test_01_fixed_roster_unique_and_balanced_for_every_worker(self):
        cases=driver.roster();self.assertEqual(len(cases),4096)
        self.assertEqual(len({c["case_id"] for c in cases}),4096)
        for worker in range(4):
            own=[c for c in cases if c["worker"]==worker]
            self.assertEqual([sum(c["cadence"]==k for c in own) for k in range(2)],[512,512])
        self.assertEqual([c["cadence"] for c in cases[:8]],[0,1]*4)
        with self.assertRaises(ValueError):driver.roster(True)

    def test_02_all8192_initial_identities_are_explicit_unknown_misses(self):
        rows=driver.initial_ledger(driver.roster())
        self.assertEqual(len(rows),8192);self.assertEqual(len({r["test_id"] for r in rows}),8192)
        self.assertTrue(all(r["status"]=="NOT_ATTEMPTED_UNKNOWN" and r["available_and_included"] is False for r in rows))

    def test_03_four_metric_CP_uses_all_fixed_denominators(self):
        rows=driver.initial_ledger(driver.roster())
        for row in rows:
            row["status"]="RETURNED_DECISIVE";row["available_and_included"]=row["replicate"]<1945
        result=driver.summarize_ledger(rows)
        self.assertTrue(result["precision_coverage_gates_pass"])
        self.assertEqual([c["available_and_included"] for c in result["primary_four_metrics"]],[1945]*4)
        self.assertTrue(all(c["denominator"]==2048 for c in result["primary_four_metrics"]))
        self.assertFalse(result["BH_mass_or_known_recovery_validated"])

    def test_04_unknowns_are_misses_and_never_removed(self):
        rows=driver.initial_ledger(driver.roster())
        for row in rows:
            row["status"]="NUMERICALLY_UNRESOLVED_MISS" if row["replicate"]<120 else "RETURNED_DECISIVE"
            row["available_and_included"]=row["replicate"]>=120
        result=driver.summarize_ledger(rows)
        self.assertTrue(result["all8192_processed"]);self.assertFalse(result["all8192_decisive"])
        self.assertEqual([c["miss_or_excluded"] for c in result["primary_four_metrics"]],[120]*4)

    def test_05_unattempted_denominators_never_report_calibration(self):
        result=driver.summarize_ledger(driver.initial_ledger(driver.roster()))
        self.assertFalse(result["all8192_processed"]);self.assertFalse(result["precision_coverage_gates_pass"])
        self.assertEqual([c["miss_or_excluded"] for c in result["primary_four_metrics"]],[2048]*4)

    def test_06_missing_roster_row_refuses_aggregate(self):
        rows=driver.initial_ledger(driver.roster())[:-1]
        with self.assertRaises(ValueError):driver.summarize_ledger(rows)

    def test_07_existing_output_is_untouched_on_refusal(self):
        args=self.prepare_fake();out=Path(args.output);out.mkdir();keep=out/"existing";keep.write_bytes(b"keep")
        with patch.object(driver,"check"),self.assertRaises(FileExistsError):driver.run(args)
        self.assertEqual(list(out.iterdir()),[keep]);self.assertEqual(keep.read_bytes(),b"keep")

    def test_08_missing_admission_refuses_before_output_or_process(self):
        args=self.prepare_fake();value=driver.load(args.admission);value["confirmation_authorized"]=False
        Path(args.admission).write_bytes(driver.raw(value))
        with patch.object(driver,"check"),patch.object(driver.subprocess,"Popen",side_effect=AssertionError("not admitted")),self.assertRaises(ValueError):driver.run(args)
        self.assertFalse(Path(args.output).exists())

    def test_09_mocked_children_retain_all8192_on_missing_databases(self):
        args=self.prepare_fake();calls=[]
        class Child:
            returncode=0
            def poll(self):return 0
            def wait(self,timeout=None):return 0
        def launch(command,**kwargs):calls.append((command,kwargs));return Child()
        with patch.object(driver,"check"),patch.object(driver.subprocess,"Popen",side_effect=launch):driver.run(args)
        self.assertEqual(len(calls),4)
        for command,options in calls:
            self.assertIn("-I",command);self.assertIn("-B",command)
            for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):self.assertEqual(options["env"][name],"1")
            self.assertNotIn("PYTHONPATH",options["env"])
        complete=driver.load(Path(args.output)/"CONFIRMATION_COMPLETED.json")
        self.assertEqual(complete["records"],8192);self.assertFalse(complete["summary"]["precision_coverage_gates_pass"])
        self.assertEqual(len(driver.load(Path(args.output)/"ALL8192_FINAL_LEDGER.json")),8192)

    def test_10_prelaunch_deadline_after_log_setup_starts_no_child(self):
        args=self.prepare_fake();clock=iter([0.,0.,21.]+[21.]*50)
        with patch.object(driver,"check"),patch.object(driver.time,"monotonic",side_effect=lambda:next(clock)),patch.object(driver.subprocess,"Popen",side_effect=AssertionError("must not launch after deadline")) as launching:
            driver.run(args)
        self.assertEqual(launching.call_count,0)
        result=driver.load(Path(args.output)/"CONFIRMATION_COMPLETED.json")
        self.assertFalse(result["summary"]["precision_coverage_gates_pass"])
        self.assertIn("budget",result["stop_reason"])

    def test_11_aggregate_report_failure_preserves_terminal_identity_ledger(self):
        args=self.prepare_fake()
        class Child:
            returncode=0
            def poll(self):return 0
            def wait(self,timeout=None):return 0
        with patch.object(driver,"check"),patch.object(driver.subprocess,"Popen",return_value=Child()),patch.object(driver,"summarize_ledger",side_effect=RuntimeError("invented report failure")):
            driver.run(args)
        self.assertEqual(len(driver.load(Path(args.output)/"ALL8192_FINAL_LEDGER.json")),8192)
        self.assertFalse(driver.load(Path(args.output)/"CONFIRMATION_COMPLETED.json")["summary"]["precision_coverage_gates_pass"])

    def test_12_worker_request_failure_stops_before_every_draw_and_fit(self):
        args=self.prepare_fake();freeze=driver.load(args.freeze);freeze["cases"]=[driver.roster()[0]]
        freeze["protocol"]["resources"].update(logical_database_bytes_per_worker=1024**2,per_ordinate_wall_seconds=1)
        Path(args.freeze).write_bytes(driver.raw(freeze))
        admission=driver.load(args.admission);admission["freeze_sha256"]=driver.pin(args.freeze)["sha256"]
        Path(args.admission).write_bytes(driver.raw(admission));Path(args.output).mkdir()
        args.worker=0;args.worker_seconds=20.;args.admission_sha=driver.pin(args.admission)["sha256"]
        class FailedWriter:
            def put(self,*a):raise OSError("invented request-commit failure")
            def close(self):pass
        store=FailedWriter()
        fake_storage=SimpleNamespace(AuditStore=lambda *a,**k:store,verify=lambda *a,**k:{"integrity_ok":False})
        with patch.object(driver,"check"),patch.object(driver,"storage_module",return_value=fake_storage),patch.object(driver,"request_payload",return_value={}),patch.object(driver,"draw_outer",side_effect=AssertionError("no RNG after commit failure")) as draw,patch("bhtracker.photometry_inference.monte_carlo_ordinate",side_effect=AssertionError("no fit after commit failure")) as fitting,patch.object(driver,"pin",side_effect=lambda p:{"path":str(p),"bytes":0,"sha256":"0"*64} if str(p).endswith("audit.sqlite") else {"path":str(p),"bytes":len(Path(p).read_bytes()),"sha256":driver.sha(Path(p).read_bytes())}),self.assertRaises(SystemExit):
            driver.run_worker(args)
        self.assertEqual(draw.call_count,0);self.assertEqual(fitting.call_count,0)

    def test_13_CP_only_and_combined_old_gross_gate_are_not_conflated(self):
        rows=driver.initial_ledger(driver.roster())
        for row in rows:
            row["status"]="RETURNED_DECISIVE";row["available_and_included"]=row["replicate"]<1980
        result=driver.summarize_ledger(rows)
        self.assertTrue(all(c["precision_equivalence_pass"] for c in result["primary_four_metrics"]))
        self.assertTrue(all(not c["combined_exact_primary_gate_pass"] for c in result["primary_four_metrics"]))
        self.assertFalse(result["precision_coverage_gates_pass"])

    def full_saved_mock(self,*,returncode=0,missing_receipt=False,wrong_worker=False,sealed=True):
        args=self.prepare_fake();freeze=driver.load(args.freeze)
        def report():return {"integrity_ok":True,"metadata":{"sealed":sealed},"all_planned_final_records_present":True}
        class Child:
            def __init__(self,code):self.returncode=code
            def poll(self):return self.returncode
            def wait(self,timeout=None):return self.returncode
        def launch(command,**kwargs):
            worker=int(command[command.index("--worker")+1]);own=Path(args.output)/f"worker_{worker}";own.mkdir()
            db=own/"audit.sqlite";db.write_bytes(b"INVENTED_MOCKED_DATABASE_NO_MODEL")
            record={"schema":"bhsm.photometry_v2.confirmation_worker_completion.v1","worker":worker,"planned_ordinates":2048,"completed_ordinates":2048,
                "stop_reason":None,"elapsed_seconds":1.,"verification":report(),"source_changes":[],"database":driver.pin(db),"scientific_acceptance_inferred":False}
            if wrong_worker and worker==0:record["worker"]=True
            if not missing_receipt or worker!=0:driver.save(own/"WORKER_COMPLETED.json",record)
            return Child(returncode if worker==0 else 0)
        def read(db,frozen):
            worker=int(Path(db).parent.name.split("_")[1])
            def records():
                for case in freeze["cases"]:
                    if case["worker"]!=worker:continue
                    for parameter in driver.PARAMETERS:
                        yield (case["case_id"],parameter),{"confirmation_identity":{"case":case,"parameter":parameter},
                            "rank_bounds":{"decision":"INCLUDED" if case["replicate"]<1945 else "EXCLUDED"},"audit_failure":None,
                            "attempted_slots":10,"observed_profile":{"status":"INVENTED_MOCKED_PROFILE"}}
            return report(),records()
        with patch.object(driver,"check"),patch.object(driver.subprocess,"Popen",side_effect=launch),patch.object(driver,"read_final_rows",side_effect=read):driver.run(args)
        return driver.load(Path(args.output)/"CONFIRMATION_COMPLETED.json"),driver.load(Path(args.output)/"ALL8192_FINAL_LEDGER.json")

    def test_14_all_terminal_nonzero_cannot_pass_even_with_valid_full8192(self):
        result,rows=self.full_saved_mock(returncode=2)
        self.assertFalse(result["summary"]["precision_coverage_gates_pass"])
        self.assertEqual(len(rows),8192);self.assertEqual(result["worker_returncodes"],[2,0,0,0])
        self.assertIsNotNone(result["stop_reason"])
        self.assertTrue(all(not r["available_and_included"] for r in rows if r["worker"]==0))
        self.assertTrue(all("decision" in r for r in rows))

    def test_15_missing_worker_completion_invalidates_retained_final_rows(self):
        result,rows=self.full_saved_mock(missing_receipt=True)
        self.assertFalse(result["summary"]["precision_coverage_gates_pass"])
        self.assertTrue(all(r["status"]=="WORKER_COMPLETION_UNVERIFIED_MISS" for r in rows if r["worker"]==0))

    def test_16_mismatched_typed_worker_completion_refuses(self):
        result,_=self.full_saved_mock(wrong_worker=True)
        self.assertFalse(result["summary"]["precision_coverage_gates_pass"])
        self.assertTrue(result["audit_errors"])

    def test_17_unsealed_databases_never_validate_even_with_full_rows(self):
        result,rows=self.full_saved_mock(sealed=False)
        self.assertFalse(result["summary"]["precision_coverage_gates_pass"])
        self.assertTrue(all(r["status"]=="WORKER_COMPLETION_UNVERIFIED_MISS" for r in rows))

    def test_18_complete_zero_exit_sealed_mocked_campaign_can_pass(self):
        result,_=self.full_saved_mock()
        self.assertTrue(result["summary"]["precision_coverage_gates_pass"])
        self.assertEqual(result["audit_errors"],[])

    def test_19_vanished_journal_is_zero_but_other_io_failures_propagate(self):
        class Vanished:
            def is_file(self):return True
            def stat(self):raise FileNotFoundError("invented DELETE-journal unlink")
        class Kept:
            def is_file(self):return True
            def stat(self):return SimpleNamespace(st_size=123)
        with patch.object(driver.Path,"rglob",return_value=iter([Vanished(),Kept()])):
            self.assertEqual(driver.disk_bytes(self.directory),123)
        class Inaccessible(Vanished):
            def stat(self):raise PermissionError("invented real storage error")
        with patch.object(driver.Path,"rglob",return_value=iter([Inaccessible()])),self.assertRaises(PermissionError):driver.disk_bytes(self.directory)

    def test_20_stop_persistence_failure_terminates_all_children_before_wait(self):
        args=self.prepare_fake();events=[];children=[]
        class Child:
            def __init__(self,index):self.returncode=None;self.index=index
            def poll(self):return self.returncode
            def terminate(self):events.append(("TERMINATE",self.index));self.returncode=-15
            def wait(self,timeout=None):
                events.append(("WAIT",self.index))
                self_outer.assertIsNotNone(self.returncode)
                return self.returncode
        self_outer=self
        def launch(*a,**k):
            child=Child(len(children));children.append(child);return child
        original_save=driver.save
        def save(path,value):
            if Path(path).name=="STOP_REQUEST.json":
                events.append(("STOP_WRITE_FAILURE",None));raise OSError("invented full stop-request disk")
            return original_save(path,value)
        clock=iter([0.]*9+[21.]*100)
        with patch.object(driver,"check"),patch.object(driver.time,"monotonic",side_effect=lambda:next(clock)),patch.object(driver.subprocess,"Popen",side_effect=launch),patch.object(driver,"save",side_effect=save):
            driver.run(args)
        terminated=[i for i,e in enumerate(events) if e[0]=="TERMINATE"]
        waits=[i for i,e in enumerate(events) if e[0]=="WAIT"]
        self.assertEqual(len(terminated),4);self.assertEqual(len(waits),4);self.assertLess(max(terminated),min(waits))
        result=driver.load(Path(args.output)/"CONFIRMATION_COMPLETED.json")
        self.assertIn("invented full stop-request disk",result["stop_request_persistence_error"])
        self.assertFalse(result["summary"]["precision_coverage_gates_pass"])
