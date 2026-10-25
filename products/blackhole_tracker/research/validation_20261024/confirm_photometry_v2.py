"""Prospectively frozen primary-four conditional photometry confirmation.

No default observations or network. --prepare does not draw or evaluate a model.
--run requires an exact root admission; all planned misses stay in denominators.
"""
from copy import deepcopy
import argparse
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import time

PRODUCT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PRODUCT))
for _name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):os.environ[_name]="1"
PARAMETERS=("tE_days","u0")
SEED_POLICY="NULL_RAW_PEAK_WIDTH12_V1"


def raw(value):return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def load(path):return json.loads(Path(path).read_bytes())
def sha(value):return hashlib.sha256(value).hexdigest()
def pin(path):
    path=Path(path).resolve();digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):digest.update(block)
    return {"path":str(path),"bytes":path.stat().st_size,"sha256":digest.hexdigest()}
def save(path,value):
    with Path(path).open("xb") as stream:stream.write(raw(value));stream.flush();os.fsync(stream.fileno())
def checked(item):
    if pin(item["path"])!=item:raise ValueError("pinned source/input changed: "+item["path"])
    return Path(item["path"])
def runtime():
    import numpy,scipy
    return {"python":platform.python_version(),"executable":sys.executable,"numpy":numpy.__version__,"scipy":scipy.__version__,"sqlite":sqlite3.sqlite_version}
def storage_module():
    path=PRODUCT/"research/validation_20261024/sqlite_audit_v1.py"
    spec=importlib.util.spec_from_file_location("confirmation_sqlite_storage",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
def disk_bytes(path):
    total=0
    for p in Path(path).rglob("*"):
        try:
            if p.is_file():total+=p.stat().st_size
        except FileNotFoundError:
            # A different worker may have just deleted its DELETE-journal sidecar.
            continue
    return total


def roster(n=2048):
    if isinstance(n,bool) or not isinstance(n,int) or n<1:raise ValueError("invalid replication count")
    return [{"case_id":f"cell{cell}_rep{rep:04d}","cadence":cell,"replicate":rep,
             "worker":(rep+2*cell)%4} for rep in range(n) for cell in range(2)]


def initial_ledger(cases):
    return [{**case,"parameter":parameter,"test_id":case["case_id"]+"_"+parameter,
             "status":"NOT_ATTEMPTED_UNKNOWN","available_and_included":False}
            for case in cases for parameter in PARAMETERS]


def preparation(args):
    from bhtracker.observations import UnresolvedPhotometry
    protocol=load(args.protocol)
    if protocol["purpose"]!="PRIMARY4_FRESH_INDEPENDENT_CONFIRMATION":raise ValueError("incorrect protocol purpose")
    if protocol["primary"]["datasets_per_cadence"]!=2048 or protocol["primary"]["metrics"]!=4:raise ValueError("primary denominator changed")
    parents=[Path(args.parent0),Path(args.parent1)]
    rows=[len(UnresolvedPhotometry(load(p)).rows) for p in parents]
    if rows!=[954,965]:raise ValueError("cadence row counts differ")
    sources=[Path(__file__),PRODUCT/"research/validation_20261024/sqlite_audit_v1.py",
        PRODUCT/"bhtracker/photometry_inference.py",PRODUCT/"bhtracker/photometry.py",
        PRODUCT/"bhtracker/observations.py",PRODUCT/"tests/test_photometry_inference.py",
        PRODUCT/"tests/test_sqlite_audit_v1.py",PRODUCT/"tests/test_confirmation_photometry_v2.py",Path(args.protocol)]
    sources += [Path(p) for p in args.evidence]
    cases=roster()
    record={"schema":"bhsm.photometry_v2.primary4_confirmation_freeze.v1",
        "purpose":protocol["purpose"],"source_pins":[pin(p) for p in sources],"parents":[pin(p) for p in parents],
        "runtime":runtime(),"protocol":protocol,"cases":cases,"initial_ledger":initial_ledger(cases),
        "source_preparation_model_RNG_calls":0,"confirmation_draws_before_admission":0}
    save(args.freeze,record)
    print(json.dumps({"freeze":pin(args.freeze),"cases":len(cases),"ordinates":len(record["initial_ledger"]),"model_or_RNG_calls":0}))


def check(freeze):
    if freeze["purpose"]!="PRIMARY4_FRESH_INDEPENDENT_CONFIRMATION":raise ValueError("purpose mismatch")
    if runtime()!=freeze["runtime"]:raise ValueError("runtime differs from freeze")
    for item in freeze["source_pins"]+freeze["parents"]:checked(item)
    if freeze["cases"]!=roster() or freeze["initial_ledger"]!=initial_ledger(freeze["cases"]):raise ValueError("frozen identity roster changed")
    if freeze["protocol"]["inference"]["seed_policy"]!=SEED_POLICY:raise ValueError("seed policy changed")


def draw_outer(parent,truth,entropy):
    """Independent image-summed formula; generator truth never goes to the fitter."""
    import numpy as np
    from bhtracker.observations import UnresolvedPhotometry
    data=UnresolvedPhotometry(parent)
    generator=np.random.Generator(np.random.PCG64(np.random.SeedSequence(entropy)))
    before=deepcopy(generator.bit_generator.state)
    u2=truth["u0"]**2+((data.times-truth["t0"])/truth["tE_days"])**2
    amplification=(u2+2)/np.sqrt(u2*(u2+4))
    mean=truth["baseline_magnitude"]-2.5*np.log10(1+truth["source_fraction"]*(amplification-1))
    noise=data.errors*generator.standard_normal(len(data.rows))
    document=data.to_dict();document["sources"]=[]
    document["metadata"]={"synthetic":True,"purpose":"FRESH_PRIMARY4_CONFIRMATION",
        "sampling_parent_sha256":data.sha256,"inherited_instrument_metadata_role":"Parent sampling/error context only; all child brightness is synthetic."}
    if "relative_time_combination_assumption" in data.document.get("metadata",{}):
        document["metadata"]["relative_time_combination_assumption"]=deepcopy(data.document["metadata"]["relative_time_combination_assumption"])
    document["transformations"]=[{"operation":"SYNTHETIC_MAGNITUDE_REPLACEMENT","parent_input_sha256":data.sha256,"all_rows_replaced":True}]
    token=sha(raw(entropy))[:24]
    for i,(row,y) in enumerate(zip(document["rows"],mean+noise)):
        row["cadence_parent_source_row_id"]=row["source_row_id"]
        row["source_row_id"]=f"SYNTHETIC:PHOTOMETRY_V2_CONFIRMATION:{token}:{i}"
        for key in ("native_fields","source_file","source_line","source_sha256"):row.pop(key,None)
        row["magnitude"]=float(y);row["quality_flags"]=[*row.get("quality_flags",[]),"SYNTHETIC_MAGNITUDE"]
    child=UnresolvedPhotometry(document)
    compact={"input_sha256":child.sha256,"parent_input_sha256":data.sha256,"magnitudes":child.magnitudes.tolist(),
        "row_count":len(child.rows),"source_row_id_rule":f"SYNTHETIC:PHOTOMETRY_V2_CONFIRMATION:{token}:<zero_based_row_index>",
        "parent_row_id_order_sha256":sha(raw([r["source_row_id"] for r in data.rows])),
        "entropy":entropy,"rng_before":before,"rng_after":generator.bit_generator.state,"noise_sha256":sha(noise.tobytes()),
        "lineage_contract":"Reconstruct from frozen cadence parent with draw_outer's exact metadata/row replacement; no native brightness is retained."}
    return child,compact


def compact_bootstrap(payload,parent,seed):
    from bhtracker.observations import UnresolvedPhotometry
    child=UnresolvedPhotometry(payload)
    if len(child.rows)!=len(parent.rows):raise ValueError("generated row count changed")
    token=sha(json.dumps(seed,separators=(",",":")).encode())[:24]
    if child.document.get("metadata",{}).get("parent_input_sha256")!=parent.sha256 or child.document.get("sources")!=[]:
        raise ValueError("bootstrap lineage contract changed")
    if child.times.tolist()!=parent.times.tolist() or child.errors.tolist()!=parent.errors.tolist():raise ValueError("bootstrap time/error sampling changed")
    for i,(row,original) in enumerate(zip(child.rows,parent.rows)):
        if row["source_row_id"]!=f"SYNTHETIC:BOOTSTRAP:{token}:{i}" or row.get("bootstrap_parent_source_row_id")!=original["source_row_id"] or row["instrument"]!=original["instrument"]:
            raise ValueError("bootstrap row identity changed")
    return {"input_sha256":child.sha256,"parent_input_sha256":parent.sha256,"magnitudes":child.magnitudes.tolist(),
        "row_count":len(child.rows),"source_row_id_rule":f"SYNTHETIC:BOOTSTRAP:{token}:<zero_based_row_index>",
        "parent_row_id_order_sha256":sha(raw([r["source_row_id"] for r in parent.rows])),"seed":seed,
        "lineage_contract":"Exact _synthetic_document metadata/row replacement; parent retained once in OUTER_INPUT."}


def request_payload(case,parameter,freeze):
    from bhtracker.photometry_inference import _seed_slots
    protocol=freeze["protocol"];cell=case["cadence"];rep=case["replicate"]
    prefix=protocol["entropy"]["prefix"]
    outer_seed=prefix+[3,0,cell,rep]
    bootstrap_entropy=prefix+[3,1,cell,rep,PARAMETERS.index(parameter)]
    value=protocol["truths"][cell][parameter]
    return {"case":case,"parameter":parameter,"tested_null_value":value,"outer_seed":outer_seed,
        "bootstrap_entropy":bootstrap_entropy,"all199_seed_slots":_seed_slots(bootstrap_entropy,parameter,value,199),
        "fitter_truth_nuisance_supplied":False,"method":"NULL12_FREE1","seed_policy":SEED_POLICY}


def run_worker(args):
    started=time.monotonic()
    freeze=load(args.freeze);check(freeze)
    admission=load(args.admission)
    if pin(args.admission)["sha256"]!=args.admission_sha or admission.get("confirmation_authorized") is not True or admission["freeze_sha256"]!=pin(args.freeze)["sha256"]:
        raise ValueError("exact root confirmation admission missing")
    protocol=freeze["protocol"];out=Path(args.output);worker=args.worker
    cases=[case for case in freeze["cases"] if case["worker"]==worker]
    own=out/f"worker_{worker}";own.mkdir(exist_ok=False)
    audit=storage_module();writer=audit.AuditStore(own/"audit.sqlite",pin(args.freeze)["sha256"],
        [(c["case_id"],p) for c in cases for p in PARAMETERS],max_database_bytes=protocol["resources"]["logical_database_bytes_per_worker"])
    ordinal_start=None;latched=None;completed=0
    from bhtracker.photometry_inference import monte_carlo_ordinate
    parents=[load(item["path"]) for item in freeze["parents"]]
    def limits():
        nonlocal latched
        if latched is not None:raise RuntimeError(latched)
        if (out/"STOP_REQUEST.json").exists():latched="SUPERVISOR_STOP_REQUEST"
        elif time.monotonic()-started>args.worker_seconds:latched="WORKER_WHOLE_BUDGET"
        elif ordinal_start is not None and time.monotonic()-ordinal_start>protocol["resources"]["per_ordinate_wall_seconds"]:latched="ORDINATE_WALL_BUDGET"
        elif disk_bytes(out)>protocol["resources"]["whole_output_bytes_including_sidecars"]:latched="GLOBAL_DISK_BUDGET"
        if latched is not None:raise RuntimeError(latched)
    try:
        for case in cases:
            ordinal_start=None;limits()
            requests={p:request_payload(case,p,freeze) for p in PARAMETERS}
            for parameter in PARAMETERS:
                writer.put(case["case_id"],parameter,-1,"REQUEST",requests[parameter])
            # Both requests commit before ANY outer draw; a write failure stops all RNG.
            limits()
            data,outer=draw_outer(parents[case["cadence"]],protocol["truths"][case["cadence"]],requests["tE_days"]["outer_seed"])
            writer.put(case["case_id"],"tE_days",-1,"OUTER_INPUT",outer)
            for parameter in PARAMETERS:
                ordinal_start=time.monotonic();limits();request=requests[parameter]
                def callback(stage,slot,payload):
                    nonlocal latched
                    try:
                        limits()
                        value=compact_bootstrap(payload,data,request["all199_seed_slots"][slot]) if stage=="GENERATED" else payload
                        writer.put(case["case_id"],parameter,slot,stage,value)
                    except Exception as exc:
                        if latched is None:latched="AUDIT_STAGE_FAILURE: "+type(exc).__name__+": "+str(exc)
                        raise
                result=monte_carlo_ordinate(data,parameter,request["tested_null_value"],entropy=request["bootstrap_entropy"],
                    audit_callback=callback,**protocol["inference"])
                if result["audit_failure"] is not None or latched is not None:
                    raise RuntimeError("PERMANENT_AUDIT_LATCH: "+str(result["audit_failure"]))
                limits()
                result["confirmation_identity"]={"case":case,"parameter":parameter,"elapsed_seconds":time.monotonic()-ordinal_start}
                writer.put(case["case_id"],parameter,-1,"FINAL_ORDINATE",result)
                completed+=1
        ordinal_start=None;limits()
        verification=writer.seal()
    except Exception as exc:
        if latched is None:latched=type(exc).__name__+": "+str(exc)
        writer.close()
        try:verification=audit.verify(own/"audit.sqlite",include_record_metadata=False)
        except Exception as failure:verification={"integrity_ok":False,"error":type(failure).__name__+": "+str(failure)}
    finally:writer.close()
    changed=[]
    for source in freeze["source_pins"]+freeze["parents"]:
        try:
            if pin(source["path"])!=source:changed.append(source["path"])
        except OSError:changed.append(source["path"])
    terminal={"schema":"bhsm.photometry_v2.confirmation_worker_completion.v1","worker":worker,"planned_ordinates":2*len(cases),"completed_ordinates":completed,
        "stop_reason":latched,"elapsed_seconds":time.monotonic()-started,"verification":verification,
        "source_changes":changed,"database":pin(own/"audit.sqlite"),"scientific_acceptance_inferred":False}
    save(own/"WORKER_COMPLETED.json",terminal)
    if latched is not None or changed:raise SystemExit(2)


def read_final_rows(database,freeze):
    """Decode saved final payloads only after every process has stopped."""
    audit=storage_module();report=audit.verify(database,expected_protocol_sha256=pin(freeze)["sha256"],include_record_metadata=False)
    def rows():
        con=sqlite3.connect(Path(database).resolve().as_uri()+"?mode=ro",uri=True)
        try:
            for case_id,parameter,slot,stage,length,raw_sha,compressed_sha,blob in con.execute("SELECT * FROM records WHERE stage='FINAL_ORDINATE' ORDER BY case_id,parameter"):
                value=audit._decode(blob,length,raw_sha,compressed_sha,audit.MAX_PAYLOAD)
                yield (case_id,parameter),value
        finally:con.close()
    return report,rows()


def worker_completion_errors(worker,returncode,terminal,database,verification,expected):
    """A final row alone never certifies worker execution or a successful seal."""
    errors=[]
    if type(returncode) is not int or returncode!=0:errors.append("WORKER_RETURN_CODE_NOT_ZERO")
    if not isinstance(terminal,dict):return errors+["MISSING_OR_MALFORMED_WORKER_COMPLETION"]
    required={"schema","worker","planned_ordinates","completed_ordinates","stop_reason","elapsed_seconds","verification","source_changes","database","scientific_acceptance_inferred"}
    if set(terminal)!=required:errors.append("WORKER_COMPLETION_FIELD_ROSTER")
    if terminal.get("schema")!="bhsm.photometry_v2.confirmation_worker_completion.v1":errors.append("WORKER_COMPLETION_SCHEMA")
    for name,value in (("worker",worker),("planned_ordinates",expected),("completed_ordinates",expected)):
        if type(terminal.get(name)) is not int or terminal[name]!=value:errors.append("WORKER_COMPLETION_"+name)
    if "stop_reason" not in terminal or terminal["stop_reason"] is not None:errors.append("WORKER_STOP_OR_FAILURE_RETAINED")
    if type(terminal.get("source_changes")) is not list or terminal["source_changes"]!=[]:errors.append("WORKER_SOURCE_CHANGED_OR_UNVERIFIED")
    if raw(terminal.get("database"))!=raw(pin(database)):errors.append("WORKER_DATABASE_PIN_MISMATCH")
    if raw(terminal.get("verification"))!=raw(verification):errors.append("WORKER_VERIFICATION_DIFFERS_FROM_FRESH_AUDIT")
    if verification.get("integrity_ok") is not True or verification.get("metadata",{}).get("sealed") is not True or verification.get("all_planned_final_records_present") is not True:
        errors.append("WORKER_DATABASE_NOT_VERIFIED_SEALED_COMPLETE")
    if terminal.get("scientific_acceptance_inferred") is not False:errors.append("WORKER_SCIENTIFIC_SCOPE_CHANGED")
    elapsed=terminal.get("elapsed_seconds")
    if isinstance(elapsed,bool) or not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed) or elapsed<0:errors.append("WORKER_ELAPSED_UNVERIFIED")
    return errors


def summarize_ledger(ledger):
    from scipy.stats import beta,binomtest
    cells=[]
    for cadence in range(2):
        for parameter in PARAMETERS:
            rows=[r for r in ledger if r["cadence"]==cadence and r["parameter"]==parameter]
            if len(rows)!=2048:raise ValueError("fixed denominator changed")
            included=sum(r["available_and_included"] for r in rows);available=sum(r["status"]=="RETURNED_DECISIVE" for r in rows)
            # Bonferroni simultaneous99% CP across the four NEW primary metrics.
            tail=.01/(2*4)
            lower=0. if included==0 else float(beta.ppf(tail,included,2048-included+1))
            upper=1. if included==2048 else float(beta.ppf(1-tail,included+1,2048-included))
            gross=float(binomtest(included,2048,.95).pvalue)
            cells.append({"cadence":cadence,"parameter":parameter,"denominator":2048,"available":available,
                "available_and_included":included,"miss_or_excluded":2048-included,"simultaneous99_CP":[lower,upper],
                "precision_equivalence_pass":1921<=included<=1986,"exact_CP_equivalence_inclusion_count_bounds":[1921,1986],
                "combined_exact_primary_gate_pass":1921<=included<=1979,"exact_combined_inclusion_count_bounds":[1921,1979],
                "old_gross_alpha_0_01_over28_p":gross,
                "old_gross_threshold_pass":gross>=.01/28})
    completed=all(r["status"] in ("RETURNED_DECISIVE","NUMERICALLY_UNRESOLVED_MISS") for r in ledger)
    decisive=all(r["status"]=="RETURNED_DECISIVE" for r in ledger)
    return {"primary_four_metrics":cells,
        "all8192_processed":completed,"all8192_decisive":decisive,
        "precision_coverage_gates_pass":completed and all(c["combined_exact_primary_gate_pass"] for c in cells),
        "scope":"Conditional native Gaussian magnitude PSPL at the two frozen cadences/truths; fitted-nuisance MC remains approximate outside separately validated domain.",
        "BH_mass_or_known_recovery_validated":False,"continuous_endpoints_validated":False,"publication_hold_cleared":False}


def run(args):
    started=time.monotonic();freeze=load(args.freeze);check(freeze);admission=load(args.admission)
    if admission.get("confirmation_authorized") is not True or admission["freeze_sha256"]!=pin(args.freeze)["sha256"]:raise ValueError("root confirmation admission required")
    protocol=freeze["protocol"];out=Path(args.output);out.mkdir(exist_ok=False)
    save(out/"FREEZE_COPY.json",freeze);save(out/"ADMISSION_COPY.json",admission)
    save(out/"ALL8192_INITIAL_LEDGER.json",freeze["initial_ledger"])
    save(out/"GENERATING_TRUTHS_SEPARATE_FROM_FITTER.json",protocol["truths"])
    env=os.environ.copy()
    for name in ("PYTHONPATH","PYTHONHOME"):env.pop(name,None)
    env.update(OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",PYTHONNOUSERSITE="1",PYTHONDONTWRITEBYTECODE="1")
    children=[];logs=[];stop_reason=None;stop_persistence_error=None
    def terminate_live_children():
        for child in children:
            if child.poll() is None:child.terminate()
    def retain_stop_request():
        nonlocal stop_persistence_error
        try:
            if not (out/"STOP_REQUEST.json").exists():save(out/"STOP_REQUEST.json",{"reason":stop_reason})
        except OSError as exc:stop_persistence_error=type(exc).__name__+": "+str(exc)
    try:
        for worker in range(4):
            check(freeze);remaining=protocol["resources"]["whole_campaign_wall_seconds"]-(time.monotonic()-started)
            if remaining<=0:raise TimeoutError("prelaunch whole budget")
            log=(out/f"worker_{worker}.log").open("xb");logs.append(log)
            remaining=protocol["resources"]["whole_campaign_wall_seconds"]-(time.monotonic()-started)
            if remaining<=0:raise TimeoutError("prelaunch budget exhausted after audit log setup")
            command=[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--worker",str(worker),"--freeze",str(Path(args.freeze).resolve()),
                "--admission",str(out/"ADMISSION_COPY.json"),"--admission-sha",pin(out/"ADMISSION_COPY.json")["sha256"],"--output",str(out),"--worker-seconds",str(remaining)]
            children.append(subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT))
        while any(child.poll() is None for child in children):
            if time.monotonic()-started>protocol["resources"]["whole_campaign_wall_seconds"]:stop_reason="WHOLE_CAMPAIGN_WALL_LIMIT"
            elif disk_bytes(out)>protocol["resources"]["whole_output_bytes_including_sidecars"]:stop_reason="WHOLE_OUTPUT_DISK_LIMIT"
            elif any(child.poll() is not None and child.returncode!=0 for child in children):stop_reason="WORKER_FAILURE_NO_AUTOMATIC_RETRY"
            if stop_reason:
                terminate_live_children()
                retain_stop_request()
                break
            time.sleep(1.)
    except Exception as exc:
        stop_reason=type(exc).__name__+": "+str(exc)
        terminate_live_children()
        retain_stop_request()
    finally:
        for child in children:
            try:child.wait(timeout=20)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        for log in logs:log.close()
    # The last/all children may already have exited before the monitoring loop.
    if len(children)!=4 or any(child.returncode!=0 for child in children):
        stop_reason=stop_reason or "WORKER_EXIT_FAILURE_AFTER_MONITORING_NO_AUTOMATIC_RETRY"
    if time.monotonic()-started>protocol["resources"]["whole_campaign_wall_seconds"]:
        stop_reason=stop_reason or "WHOLE_CAMPAIGN_WALL_LIMIT_AFTER_LAST_EXIT"
    if disk_bytes(out)>protocol["resources"]["whole_output_bytes_including_sidecars"]:
        stop_reason=stop_reason or "WHOLE_OUTPUT_DISK_LIMIT_AFTER_LAST_EXIT"
    ledger=deepcopy(freeze["initial_ledger"]);lookup={(r["case_id"],r["parameter"]):r for r in ledger};audit_errors=[]
    for worker in range(4):
        database=out/f"worker_{worker}/audit.sqlite"
        if not database.exists():audit_errors.append({"worker":worker,"error":"NO_DATABASE_UNKNOWN"});continue
        try:
            verification,finals=read_final_rows(database,args.freeze)
            receipt_path=out/f"worker_{worker}/WORKER_COMPLETED.json"
            try:terminal=load(receipt_path)
            except (OSError,ValueError):terminal=None
            expected=2*sum(c["worker"]==worker for c in freeze["cases"])
            errors=worker_completion_errors(worker,children[worker].returncode if worker<len(children) else None,terminal,database,verification,expected)
            if errors:audit_errors.append({"worker":worker,"completion_errors":errors})
            for key,result in finals:
                row=lookup[key];identity=result["confirmation_identity"]
                if raw(identity["case"])!=raw({k:row[k] for k in ("case_id","cadence","replicate","worker")}) or identity["parameter"]!=row["parameter"] or row["worker"]!=worker:
                    raise ValueError("saved final identity mismatch")
                decision=result["rank_bounds"]["decision"]
                available=not errors and decision in ("INCLUDED","EXCLUDED") and result["audit_failure"] is None
                row.update({"status":"WORKER_COMPLETION_UNVERIFIED_MISS" if errors else "RETURNED_DECISIVE" if available else "NUMERICALLY_UNRESOLVED_MISS",
                    "available_and_included":available and decision=="INCLUDED","decision":decision,
                    "attempted_slots":result["attempted_slots"],"rank_bounds":result["rank_bounds"],
                    "observed_status":result["observed_profile"]["status"]})
        except Exception as exc:
            audit_errors.append({"worker":worker,"error":type(exc).__name__+": "+str(exc)})
            for row in ledger:
                if row["worker"]==worker:row.update(status="AUDIT_UNVERIFIED_MISS",available_and_included=False)
    # The complete identity ledger is durable before aggregate arithmetic/reporting.
    save(out/"ALL8192_FINAL_LEDGER.json",ledger)
    changes=[]
    for source in freeze["source_pins"]+freeze["parents"]:
        try:
            if pin(source["path"])!=source:changes.append(source["path"])
        except OSError:changes.append(source["path"])
    try:summary=summarize_ledger(ledger)
    except Exception as exc:summary={"aggregate_failed":type(exc).__name__+": "+str(exc),"precision_coverage_gates_pass":False}
    if changes or audit_errors or stop_reason or stop_persistence_error:summary["precision_coverage_gates_pass"]=False
    result={"schema":"bhsm.photometry_v2.primary4_confirmation_completion.v1","records":len(ledger),"summary":summary,
        "stop_reason":stop_reason,"stop_request_persistence_error":stop_persistence_error,"audit_errors":audit_errors,"source_changes":changes,
        "elapsed_seconds":time.monotonic()-started,"worker_returncodes":[c.returncode for c in children],
        "no_automatic_retry":True,"all_planned_identities_retained":len(ledger)==8192,"release_hold_cleared":False}
    save(out/"CONFIRMATION_COMPLETED.json",result)
    print(json.dumps({"receipt":pin(out/"CONFIRMATION_COMPLETED.json"),"elapsed_seconds":result["elapsed_seconds"],"summary":summary}))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--prepare",action="store_true");parser.add_argument("--worker",type=int)
    parser.add_argument("--freeze",required=True);parser.add_argument("--protocol");parser.add_argument("--parent0");parser.add_argument("--parent1")
    parser.add_argument("--evidence",action="append",default=[]);parser.add_argument("--admission");parser.add_argument("--admission-sha")
    parser.add_argument("--output");parser.add_argument("--worker-seconds",type=float)
    args=parser.parse_args()
    if args.prepare:preparation(args)
    elif args.worker is not None:run_worker(args)
    else:run(args)
