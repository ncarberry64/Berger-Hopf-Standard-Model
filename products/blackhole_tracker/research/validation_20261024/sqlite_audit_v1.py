"""Durable, hash-checked gzip-JSON evidence storage; no inference or RNG.

DELETE journal and synchronous FULL are required. Each stage is committed
before returning. A failure permanently latches this writer. Integrity and
sealing never assert that an analysis or confidence claim succeeded.
"""
from copy import deepcopy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3

SCHEMA="bhsm_photometry_sqlite_audit/1"
STAGES={"REQUEST","OUTER_INPUT","OBSERVED_PROFILE","GENERATED","FITTED","FINAL_ORDINATE","FAILURE"}
MAX_PAYLOAD=16*1024*1024


class AuditStoreError(RuntimeError):pass
class AuditStoreLatched(AuditStoreError):pass
class AuditIntegrityError(AuditStoreError):pass


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")


def digest(blob):return hashlib.sha256(blob).hexdigest()
def file_digest(path):
    value=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):value.update(block)
    return value.hexdigest()


def _integer(value,name,minimum=0):
    if isinstance(value,bool) or not isinstance(value,int) or value<minimum:raise ValueError(name+" has invalid integer type/range")


def _test_key(case_id,parameter):
    if not isinstance(case_id,str) or not case_id or len(case_id)>256 or any(c in case_id for c in "\r\n\0"):
        raise ValueError("invalid case identity")
    if parameter not in ("tE_days","u0"):raise ValueError("unsupported parameter identity")
    return case_id,parameter


def _roster(expected_tests):
    values=[_test_key(*row) for row in expected_tests]
    if not values or len(values)!=len(set(values)):raise ValueError("expected-test roster must be nonempty and unique")
    return tuple(values)


def _decode(blob,raw_bytes,raw_sha,compressed_sha,limit):
    if not isinstance(blob,bytes) or digest(blob)!=compressed_sha:raise AuditIntegrityError("compressed payload hash mismatch")
    _integer(raw_bytes,"canonical_bytes")
    if raw_bytes>limit:raise AuditIntegrityError("declared payload exceeds resource limit")
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(blob),mode="rb") as archive:raw=archive.read(limit+1)
    except (OSError,EOFError) as exc:raise AuditIntegrityError("gzip payload corrupt or partial") from exc
    if len(raw)!=raw_bytes or len(raw)>limit or digest(raw)!=raw_sha:raise AuditIntegrityError("canonical payload size/hash mismatch")
    try:value=json.loads(raw)
    except (ValueError,UnicodeError) as exc:raise AuditIntegrityError("payload is not JSON") from exc
    if canonical(value)!=raw:raise AuditIntegrityError("payload is not canonical finite JSON")
    return value


class AuditStore:
    def __init__(self,path,protocol_sha256,expected_tests,*,max_payload_bytes=MAX_PAYLOAD,max_database_bytes=8*1024**3):
        if not isinstance(protocol_sha256,str) or re.fullmatch(r"[0-9a-f]{64}",protocol_sha256) is None:raise ValueError("exact protocol SHA256 required")
        _integer(max_payload_bytes,"max_payload_bytes",1);_integer(max_database_bytes,"max_database_bytes",1)
        if max_payload_bytes>MAX_PAYLOAD:raise ValueError("payload limit exceeds closed prototype resource domain")
        self.path=Path(path).resolve();self.expected=_roster(expected_tests);self._expected_set=frozenset(self.expected)
        self.max_payload_bytes=max_payload_bytes;self.max_database_bytes=max_database_bytes
        self.latched_error=None;self.sealed=False;self._connection=None
        # Exclusive ownership before SQLite opens it: refusal never writes an old database.
        descriptor=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(descriptor)
        try:
            self._connection=sqlite3.connect(self.path,timeout=10,isolation_level=None)
            assert self._connection.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower()=="delete"
            self._connection.execute("PRAGMA synchronous=FULL")
            self._connection.execute("PRAGMA trusted_schema=OFF")
            self._connection.execute("BEGIN IMMEDIATE")
            self._connection.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY,value BLOB NOT NULL) WITHOUT ROWID")
            self._connection.execute("CREATE TABLE records(case_id TEXT NOT NULL,parameter TEXT NOT NULL,slot INTEGER NOT NULL,stage TEXT NOT NULL,canonical_bytes INTEGER NOT NULL,canonical_sha256 TEXT NOT NULL,compressed_sha256 TEXT NOT NULL,payload BLOB NOT NULL,PRIMARY KEY(case_id,parameter,slot,stage)) WITHOUT ROWID")
            metadata={"schema":SCHEMA,"protocol_sha256":protocol_sha256,"expected_tests":[list(x) for x in self.expected],"max_payload_bytes":max_payload_bytes,"max_logical_database_bytes":max_database_bytes,"sealed":False,"journal_mode":"DELETE","synchronous":"FULL"}
            for key,value in metadata.items():self._connection.execute("INSERT INTO metadata VALUES(?,?)",(key,canonical(value)))
            if self._connection.execute("PRAGMA page_size").fetchone()[0]*self._connection.execute("PRAGMA page_count").fetchone()[0]>max_database_bytes:
                raise AuditStoreError("database initialization exceeds resource budget")
            self._connection.commit()
        except Exception as exc:
            self._latch(exc)
            self.close()
            raise AuditStoreError("audit-store initialization failed; new partial file retained") from exc

    def _latch(self,error):
        if self.latched_error is None:self.latched_error=type(error).__name__+": "+str(error)
        if self._connection is not None:
            try:self._connection.rollback()
            except sqlite3.Error:pass

    def put(self,case_id,parameter,slot,stage,payload):
        if self.latched_error is not None:raise AuditStoreLatched(self.latched_error)
        if self.sealed or self._connection is None:raise AuditStoreError("writer is sealed or closed")
        try:
            key=_test_key(case_id,parameter)
            if key not in self._expected_set:raise ValueError("test key outside fixed roster")
            _integer(slot,"slot",-1)
            if stage not in STAGES:raise ValueError("unknown stage")
            if (stage in ("GENERATED","FITTED") and slot<0) or (stage in ("REQUEST","OUTER_INPUT","OBSERVED_PROFILE","FINAL_ORDINATE") and slot!=-1):raise ValueError("invalid stage/slot identity")
            raw=canonical(payload)
            if len(raw)>self.max_payload_bytes:raise ValueError("payload resource budget exceeded")
            compressed=gzip.compress(raw,compresslevel=5,mtime=0)
            con=self._connection
            if con.execute("PRAGMA journal_mode").fetchone()[0].lower()!="delete" or con.execute("PRAGMA synchronous").fetchone()[0]!=2:
                raise AuditStoreError("writer durability settings changed")
            con.execute("BEGIN IMMEDIATE")
            if stage=="FITTED" and con.execute("SELECT 1 FROM records WHERE case_id=? AND parameter=? AND slot=? AND stage='GENERATED'",(case_id,parameter,slot)).fetchone() is None:
                raise AuditStoreError("fitted stage lacks a previously committed generated stage")
            con.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?)",(case_id,parameter,slot,stage,len(raw),digest(raw),digest(compressed),compressed))
            page_size=con.execute("PRAGMA page_size").fetchone()[0];pages=con.execute("PRAGMA page_count").fetchone()[0]
            if page_size*pages>self.max_database_bytes:raise AuditStoreError("database resource budget exceeded")
            con.commit()
            return {"key":[case_id,parameter,slot,stage],"canonical_bytes":len(raw),"canonical_sha256":digest(raw),"compressed_sha256":digest(compressed),"durably_committed":True}
        except Exception as exc:
            self._latch(exc)
            raise AuditStoreLatched(self.latched_error) from exc

    def seal(self):
        if self.latched_error is not None:raise AuditStoreLatched(self.latched_error)
        if self.sealed or self._connection is None:raise AuditStoreError("writer is sealed or closed")
        try:
            report=verify(self.path,include_record_metadata=False)
            if report["missing_final_tests"]:raise AuditStoreError("cannot seal without every planned final record")
            self._connection.execute("BEGIN IMMEDIATE")
            self._connection.execute("UPDATE metadata SET value=? WHERE key='sealed'",(canonical(True),))
            self._connection.commit();self.sealed=True
        except Exception as exc:
            self._latch(exc);raise AuditStoreLatched(self.latched_error) from exc
        self.close()
        return verify(self.path,require_sealed=True,include_record_metadata=False)

    def close(self):
        if self._connection is not None:
            try:self._connection.rollback()
            finally:self._connection.close();self._connection=None


def verify(path,*,expected_protocol_sha256=None,require_sealed=False,include_payloads=False,include_record_metadata=True):
    """Read-only verification, including incomplete-stage and missing-test evidence.

Hot-journal recovery, if required, is never attempted against this source.
Use recover_copy into a fresh location after a writer has stopped.
"""
    if include_payloads and not include_record_metadata:raise ValueError("payload collection requires record metadata collection")
    path=Path(path).resolve()
    if not path.is_file():raise AuditIntegrityError("audit database unavailable")
    try:
        con=sqlite3.connect(path.as_uri()+"?mode=ro",uri=True,timeout=10,isolation_level=None)
        con.execute("PRAGMA query_only=ON");con.execute("PRAGMA trusted_schema=OFF")
        if con.execute("PRAGMA quick_check").fetchone()[0]!="ok":raise AuditIntegrityError("SQLite quick_check failed")
        metadata={}
        for key,value in con.execute("SELECT key,value FROM metadata"):
            if not isinstance(value,bytes):raise AuditIntegrityError("metadata is not canonical typed JSON")
            decoded=json.loads(value)
            if canonical(decoded)!=value:raise AuditIntegrityError("noncanonical metadata")
            metadata[key]=decoded
        if set(metadata)!={"schema","protocol_sha256","expected_tests","max_payload_bytes","max_logical_database_bytes","sealed","journal_mode","synchronous"}:raise AuditIntegrityError("metadata roster mismatch")
        if metadata.get("schema")!=SCHEMA:raise AuditIntegrityError("schema mismatch")
        if not isinstance(metadata.get("protocol_sha256"),str) or re.fullmatch(r"[0-9a-f]{64}",metadata["protocol_sha256"]) is None:raise AuditIntegrityError("malformed protocol binding")
        if not isinstance(metadata.get("sealed"),bool):raise AuditIntegrityError("invalid seal type")
        if metadata.get("journal_mode")!="DELETE" or metadata.get("synchronous")!="FULL":raise AuditIntegrityError("durability declaration mismatch")
        if expected_protocol_sha256 is not None and metadata.get("protocol_sha256")!=expected_protocol_sha256:raise AuditIntegrityError("protocol binding mismatch")
        expected=_roster(metadata["expected_tests"]);expected_set=frozenset(expected)
        _integer(metadata["max_payload_bytes"],"max_payload_bytes",1)
        if metadata["max_payload_bytes"]>MAX_PAYLOAD:raise AuditIntegrityError("metadata payload resource limit outside prototype domain")
        _integer(metadata["max_logical_database_bytes"],"max_logical_database_bytes",1)
        if con.execute("PRAGMA page_size").fetchone()[0]*con.execute("PRAGMA page_count").fetchone()[0]>metadata["max_logical_database_bytes"]:raise AuditIntegrityError("committed logical database exceeds declared budget")
        if require_sealed and metadata.get("sealed") is not True:raise AuditIntegrityError("audit database is not sealed")
        records=[];generated=set();fitted=set();finals=set();record_count=0;record_metadata_hash=hashlib.sha256()
        for case_id,parameter,slot,stage,length,raw_sha,compressed_sha,blob in con.execute("SELECT case_id,parameter,slot,stage,canonical_bytes,canonical_sha256,compressed_sha256,payload FROM records ORDER BY case_id,parameter,slot,stage"):
            if _test_key(case_id,parameter) not in expected_set or stage not in STAGES:raise AuditIntegrityError("record outside fixed identity contract")
            _integer(slot,"slot",-1)
            if (stage in ("GENERATED","FITTED") and slot<0) or (stage in ("REQUEST","OUTER_INPUT","OBSERVED_PROFILE","FINAL_ORDINATE") and slot!=-1):raise AuditIntegrityError("record stage/slot mismatch")
            value=_decode(blob,length,raw_sha,compressed_sha,metadata["max_payload_bytes"])
            item={"key":[case_id,parameter,slot,stage],"canonical_bytes":length,"canonical_sha256":raw_sha,"compressed_sha256":compressed_sha}
            record_metadata_hash.update(canonical(item));record_count+=1
            if include_payloads:item["payload"]=value
            if include_record_metadata:records.append(item)
            if stage=="GENERATED":generated.add((case_id,parameter,slot))
            if stage=="FITTED":fitted.add((case_id,parameter,slot))
            if stage=="FINAL_ORDINATE":finals.add((case_id,parameter))
        if fitted-generated:raise AuditIntegrityError("fitted data lacks generated evidence")
        missing=[list(x) for x in expected if x not in finals]
        if metadata.get("sealed") is True and missing:raise AuditIntegrityError("sealed roster is incomplete")
        return {"schema":SCHEMA,"integrity_ok":True,"metadata":metadata,"record_count":record_count,"records":records,"record_metadata_sha256":record_metadata_hash.hexdigest(),"record_metadata_collected":include_record_metadata,
            "missing_final_tests":missing,"generated_without_fit_unknown":[list(x) for x in sorted(generated-fitted)],
            "all_planned_final_records_present":not missing,"analysis_success_or_coverage_inferred":False,
            "qualification":"Integrity/sealing is not a numerical or coverage certificate; missing stages remain explicit unknowns."}
    except (sqlite3.Error,ValueError,KeyError,TypeError,OSError) as exc:
        if isinstance(exc,AuditIntegrityError):raise
        raise AuditIntegrityError("database corrupt, partial, malformed or needs explicit recovery copy") from exc
    finally:
        if 'con' in locals():con.close()


def recover_copy(source,target):
    """Recover only a new owned copy after writer termination; preserve source."""
    source=Path(source).resolve();target=Path(target).resolve()
    if not source.is_file():raise AuditStoreError("source unavailable")
    if Path(str(source)+"-wal").exists() or Path(str(source)+"-shm").exists():raise AuditStoreError("WAL source not admitted by DELETE-journal contract")
    paths=[source]+([Path(str(source)+"-journal")] if Path(str(source)+"-journal").exists() else [])
    before={str(p):file_digest(p) for p in paths}
    # No overwriting, including preexisting destination sidecars.
    if target.exists() or any(Path(str(target)+s).exists() for s in ("-journal","-wal","-shm")):raise FileExistsError("fresh recovery target required")
    for path in paths:
        destination=target if path==source else Path(str(target)+"-journal")
        with path.open("rb") as src,destination.open("xb") as dst:
            shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
    con=sqlite3.connect(target,isolation_level=None)
    try:
        con.execute("PRAGMA synchronous=FULL")
        if con.execute("PRAGMA quick_check").fetchone()[0]!="ok":raise AuditIntegrityError("recovery copy integrity failure")
    finally:con.close()
    if before!={str(p):file_digest(p) for p in paths}:raise AuditStoreError("source changed during recovery-copy operation")
    return {"source_hashes_preserved":before,"recovered_copy_sha256":file_digest(target),"verification":verify(target),"source_modified":False}
