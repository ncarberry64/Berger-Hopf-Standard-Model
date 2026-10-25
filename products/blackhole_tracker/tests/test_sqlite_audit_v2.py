"""Wholly invented storage/transaction controls; no inference or noise draws."""
from contextlib import closing
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

HELPER=Path(__file__).resolve().parents[1]/"research/validation_20261024/sqlite_audit_v1.py"
spec=importlib.util.spec_from_file_location("photometry_sqlite_audit_controls",HELPER)
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
PROTOCOL="0"*64


class TestSQLiteAudit(unittest.TestCase):
    def setUp(self):
        root=os.environ.get("BHSM_SQLITE_TEST_ARTIFACT_DIR")
        if root:
            self.directory=Path(tempfile.mkdtemp(prefix=self._testMethodName+"_",dir=root));self.temporary=None
        else:
            self.temporary=tempfile.TemporaryDirectory();self.directory=Path(self.temporary.name)
        self.writers=[]

    def tearDown(self):
        for writer in self.writers:writer.close()
        if self.temporary is not None:self.temporary.cleanup()

    def writer(self,**kwargs):
        obj=audit.AuditStore(self.directory/"audit.sqlite",PROTOCOL,[("CASE","tE_days")],**kwargs)
        self.writers.append(obj);return obj

    def test_01_durable_roundtrip_and_complete_record_roster(self):
        writer=self.writer()
        self.assertEqual(writer._connection.execute("PRAGMA synchronous").fetchone()[0],2)
        self.assertEqual(writer._connection.execute("PRAGMA journal_mode").fetchone()[0],"delete")
        payload={"synthetic":True,"magnitudes":[18.,17.9],"nullable":None}
        writer.put("CASE","tE_days",0,"GENERATED",payload)
        payload["magnitudes"][0]=-999.
        writer.put("CASE","tE_days",0,"FITTED",{"statistic":1.2,"known_BH":False})
        writer.put("CASE","tE_days",-1,"FINAL_ORDINATE",{"decision":"INCLUDED"})
        result=writer.seal()
        self.assertTrue(result["integrity_ok"] and result["all_planned_final_records_present"])
        self.assertEqual(result["generated_without_fit_unknown"],[])
        self.assertFalse(result["analysis_success_or_coverage_inferred"])
        payloads=audit.verify(writer.path,expected_protocol_sha256=PROTOCOL,require_sealed=True,include_payloads=True)
        generated=next(r for r in payloads["records"] if r["key"][3]=="GENERATED")
        self.assertEqual(generated["payload"]["magnitudes"],[18.,17.9])

    def test_02_existing_output_refuses_without_modification(self):
        path=self.directory/"audit.sqlite";path.write_bytes(b"prior bytes")
        before=path.read_bytes()
        with self.assertRaises(FileExistsError):self.writer()
        self.assertEqual(path.read_bytes(),before)

    def test_03_duplicate_key_latches_and_keeps_original(self):
        writer=self.writer();writer.put("CASE","tE_days",0,"GENERATED",{"value":1})
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"GENERATED",{"value":2})
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"FITTED",{})
        report=audit.verify(writer.path,include_payloads=True)
        self.assertEqual(report["record_count"],1)
        self.assertEqual(report["records"][0]["payload"],{"value":1})

    def test_04_fitted_without_prior_generated_commit_is_rejected(self):
        writer=self.writer()
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"FITTED",{})
        self.assertEqual(audit.verify(writer.path)["record_count"],0)

    def test_05_canonical_hash_corruption_fails_closed(self):
        writer=self.writer();writer.put("CASE","tE_days",0,"GENERATED",{"value":1});writer.close()
        with closing(sqlite3.connect(writer.path)) as connection:
            with connection:connection.execute("UPDATE records SET canonical_sha256=?",("f"*64,))
        with self.assertRaises(audit.AuditIntegrityError):audit.verify(writer.path)

    def test_06_partial_compressed_payload_fails_even_with_updated_compressed_hash(self):
        writer=self.writer();writer.put("CASE","tE_days",0,"GENERATED",{"value":1});writer.close()
        with closing(sqlite3.connect(writer.path)) as connection:
            with connection:
                blob=connection.execute("SELECT payload FROM records").fetchone()[0][:-5]
                connection.execute("UPDATE records SET payload=?,compressed_sha256=?",(blob,hashlib.sha256(blob).hexdigest()))
        with self.assertRaises(audit.AuditIntegrityError):audit.verify(writer.path)

    def test_07_missing_fit_and_final_are_unknown_not_success(self):
        writer=self.writer();writer.put("CASE","tE_days",0,"GENERATED",{})
        report=audit.verify(writer.path)
        self.assertEqual(report["generated_without_fit_unknown"],[["CASE","tE_days",0]])
        self.assertEqual(report["missing_final_tests"],[["CASE","tE_days"]])
        with self.assertRaises(audit.AuditStoreLatched):writer.seal()
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"FITTED",{})

    def test_08_protocol_type_and_finite_payload_guards(self):
        writer=self.writer()
        with self.assertRaises(audit.AuditIntegrityError):audit.verify(writer.path,expected_protocol_sha256="1"*64)
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"GENERATED",{"bad":float("nan")})

    def test_09_precommit_failure_rolls_back_and_latches(self):
        writer=self.writer();writer.put("CASE","tE_days",0,"GENERATED",{"immutable":True})
        underlying=writer._connection
        class Proxy:
            def execute(self,*args):return underlying.execute(*args)
            def rollback(self):return underlying.rollback()
            def close(self):return underlying.close()
            def commit(self):raise OSError("invented precommit disk failure")
        writer._connection=Proxy()
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"FITTED",{})
        report=audit.verify(writer.path)
        self.assertEqual(report["record_count"],1)
        self.assertEqual(report["generated_without_fit_unknown"],[["CASE","tE_days",0]])

    def test_10_postcommit_acknowledgement_failure_remains_latched(self):
        writer=self.writer();writer.put("CASE","tE_days",0,"GENERATED",{})
        underlying=writer._connection
        class Proxy:
            def execute(self,*args):return underlying.execute(*args)
            def rollback(self):return underlying.rollback()
            def close(self):return underlying.close()
            def commit(self):underlying.commit();raise OSError("invented lost commit acknowledgement")
        writer._connection=Proxy()
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"FITTED",{})
        self.assertEqual(audit.verify(writer.path)["record_count"],2)
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",-1,"FINAL_ORDINATE",{})

    def test_11_writer_crash_recovers_only_a_fresh_copy(self):
        path=self.directory/"crashed.sqlite"
        child=r'''
import gzip,hashlib,importlib.util,os,sys
spec=importlib.util.spec_from_file_location("audit_child",sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
w=m.AuditStore(sys.argv[2],"0"*64,[("CASE","tE_days")])
w.put("CASE","tE_days",-1,"OBSERVED_PROFILE",{"committed":True})
c=w._connection;c.execute("PRAGMA cache_size=2");c.execute("BEGIN IMMEDIATE")
text="".join(hashlib.sha256(str(i).encode()).hexdigest() for i in range(8000))
for slot in range(6):
 raw=m.canonical({"invented":text,"slot":slot});blob=gzip.compress(raw,mtime=0)
 c.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?)",("CASE","tE_days",slot,"GENERATED",len(raw),m.digest(raw),m.digest(blob),blob))
os._exit(23)
'''
        result=subprocess.run([sys.executable,"-I","-B","-c",child,str(HELPER),str(path)],capture_output=True,timeout=20)
        self.assertEqual(result.returncode,23)
        before={str(p):audit.file_digest(p) for p in [path,Path(str(path)+"-journal")] if p.exists()}
        recovered=audit.recover_copy(path,self.directory/"recovered.sqlite")
        self.assertFalse(recovered["source_modified"])
        self.assertEqual(recovered["verification"]["record_count"],1)
        self.assertFalse(recovered["verification"]["all_planned_final_records_present"])
        self.assertEqual(before,{p:audit.file_digest(p) for p in before})

    def test_12_recovery_target_refuses_existing_bytes(self):
        writer=self.writer();writer.close()
        target=self.directory/"existing.sqlite";target.write_bytes(b"keep")
        with self.assertRaises(FileExistsError):audit.recover_copy(writer.path,target)
        self.assertEqual(target.read_bytes(),b"keep")

    def test_13_partial_database_file_is_not_accepted(self):
        writer=self.writer();writer.close()
        partial=self.directory/"partial.sqlite";partial.write_bytes(writer.path.read_bytes()[:40])
        with self.assertRaises(audit.AuditIntegrityError):audit.verify(partial)

    def test_14_payload_resource_limit_latches_without_insert(self):
        writer=self.writer(max_payload_bytes=32)
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"GENERATED",{"large":"X"*100})
        self.assertEqual(audit.verify(writer.path)["record_count"],0)

    def test_15_invalid_roster_and_bool_slot_are_closed(self):
        with self.assertRaises(ValueError):audit.AuditStore(self.directory/"invalid.sqlite",PROTOCOL,[("C","u0"),("C","u0")])
        self.assertFalse((self.directory/"invalid.sqlite").exists())
        writer=self.writer()
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",True,"GENERATED",{})

    def test_16_modified_durability_settings_are_detected(self):
        writer=self.writer();writer._connection.execute("PRAGMA synchronous=OFF")
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"GENERATED",{})
        self.assertEqual(audit.verify(writer.path)["record_count"],0)


    def test_17_streamed_summary_matches_full_record_metadata(self):
        writer=self.writer()
        writer.put("CASE","tE_days",0,"GENERATED",{"x":[1,2]})
        writer.put("CASE","tE_days",0,"FITTED",{"q":1.})
        writer.put("CASE","tE_days",-1,"FINAL_ORDINATE",{"decision":"UNRESOLVED"})
        full=audit.verify(writer.path)
        summary=audit.verify(writer.path,include_record_metadata=False)
        self.assertEqual(summary["records"],[])
        self.assertEqual(summary["record_count"],3)
        self.assertEqual(summary["record_metadata_sha256"],full["record_metadata_sha256"])
        self.assertEqual(summary["record_metadata_sha256"],audit.digest(b"".join(audit.canonical(x) for x in full["records"])))
        self.assertIsInstance(writer.expected,tuple)
        self.assertIsInstance(writer._expected_set,frozenset)
        self.assertFalse(writer.seal()["record_metadata_collected"])


    def test_18_request_and_shared_outer_input_stages_are_durable(self):
        writer=self.writer()
        writer.put("CASE","tE_days",-1,"REQUEST",{"slots":list(range(199)),"outer_seed":[3,0,0]})
        writer.put("CASE","tE_days",-1,"OUTER_INPUT",{"input_sha256":"invented","magnitudes":[18.,17.]})
        report=audit.verify(writer.path,include_payloads=True)
        self.assertEqual(report["record_count"],2)
        self.assertEqual({r["key"][3] for r in report["records"]},{"REQUEST","OUTER_INPUT"})
        with self.assertRaises(audit.AuditStoreLatched):writer.put("CASE","tE_days",0,"REQUEST",{})

    def test_19_transaction_commit_and_close_release_file_without_gc(self):
        path=self.directory/"resource_release.sqlite"
        self.assertTrue(path.resolve().is_relative_to(self.directory.resolve()))
        with closing(sqlite3.connect(path)) as connection:
            with connection:
                connection.execute("CREATE TABLE fixture(value INTEGER)")
                connection.execute("INSERT INTO fixture VALUES(19)")
        # Keep the connection strongly referenced: closing cannot depend on GC.
        retained_connection=connection
        with self.assertRaises(sqlite3.ProgrammingError):retained_connection.execute("SELECT 1")
        with closing(sqlite3.connect(path)) as checked:
            self.assertEqual(checked.execute("SELECT value FROM fixture").fetchone()[0],19)
        with self.assertRaises(sqlite3.ProgrammingError):checked.execute("SELECT 1")
        moved=self.directory/"resource_release_renamed.sqlite"
        path.rename(moved);self.assertTrue(moved.is_file())
        moved.unlink();self.assertFalse(moved.exists());self.assertFalse(path.exists())
