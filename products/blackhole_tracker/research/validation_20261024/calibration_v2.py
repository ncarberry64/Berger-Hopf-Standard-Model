"""Bounded development pilot for nonregular photometric inference.

Prepare writes source/runtime/data pins only. Run requires a separate exact
root admission. This four-draw pilot is never an independent coverage result.
"""
from copy import deepcopy
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

PRODUCT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PRODUCT))


def raw_json(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")


def pin(path):
    path=Path(path);blob=path.read_bytes()
    return {"path":str(path.resolve()),"bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest()}


def save(path,value):
    with Path(path).open("xb") as stream:
        stream.write(raw_json(value));stream.flush();os.fsync(stream.fileno())


def save_gzip(path,value):
    with Path(path).open("xb") as stream:
        with gzip.GzipFile(filename="",fileobj=stream,mode="wb",mtime=0,compresslevel=5) as archive:
            archive.write(raw_json(value))
        stream.flush();os.fsync(stream.fileno())


def load(path):return json.loads(Path(path).read_bytes())


def runtime():
    import numpy,scipy
    return {"python":platform.python_version(),"executable":sys.executable,"numpy":numpy.__version__,"scipy":scipy.__version__}


def check(freeze):
    assert runtime()==freeze["runtime"]
    for item in freeze["source_pins"]+freeze["parents"]:
        assert pin(item["path"])==item


def prepare(args):
    from bhtracker.observations import UnresolvedPhotometry
    sources=[Path(__file__),PRODUCT/"bhtracker/photometry_inference.py",PRODUCT/"bhtracker/photometry.py",PRODUCT/"bhtracker/observations.py",PRODUCT/"tests/test_photometry_inference.py"]
    parents=[Path(args.parent0),Path(args.parent1)]
    counts=[len(UnresolvedPhotometry(load(p)).rows) for p in parents]
    assert counts==[954,965]
    record={"schema":"bhsm.photometry_v2.development_pilot_freeze.v1","purpose":"FOUR_OUTER_DRAW_DEVELOPMENT_ONLY",
        "source_pins":[pin(p) for p in sources],"parents":[pin(p) for p in parents],"runtime":runtime(),
        "cadence_rows":counts,"outer_draws":4,"replicates_per_cadence":2,"parameters":["tE_days","u0"],"ordinate_tests":8,
        "truth":[{"t0":3155.835691,"tE_days":200.,"u0":.3,"source_fraction":.65,"baseline_magnitude":18.},
                 {"t0":2727.69093,"tE_days":25.,"u0":.3,"source_fraction":.65,"baseline_magnitude":18.}],
        "entropy":{"prefix":[20261025,1346917938],"outer_stage":0,"bootstrap_stage":1,"confirmation_reserved_stage":3},
        "inference":{"slots":199,"starts":12,"max_nfev":1500,"noise_scale":1.,"confidence_level":.95,"lazy":True,
            "generation":"constrained-null fitted nuisance only; approximate plugin bootstrap","reference_search":"12free+12null+1null-seeded-free refinement per statistic"},
        "inference_options":{"slots":199,"starts":12,"max_nfev":1500,"noise_scale":1.,"confidence_level":.95,"lazy":True},
        "limits":{"batch_wall_seconds":1200,"per_ordinate_wall_seconds":240,"saved_bytes":536870912},
        "threads":{"OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1"},
        "truth_separation":"Truth remains in separate generator/audit record. Fitter sees synthetic data and tested null value only; never truth nuisance or truth initialization.",
        "storage":"Each outer sampling document once; bootstrap stores magnitudes+canonical inputhash and rowidentity rule, seeds, full outcomes. Native parents referenced by hash, never repeated.",
        "not_confirmation":True,"release_hold_cleared":False}
    save(args.freeze,record)
    print(json.dumps({"freeze":pin(args.freeze),"calls":0}))


def outer_draw(parent,truth,seed):
    import numpy as np
    from bhtracker.observations import UnresolvedPhotometry
    data=UnresolvedPhotometry(parent)
    rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))
    before=deepcopy(rng.bit_generator.state)
    # Independent image-summed PSPL formula; do not call inference predictor.
    u2=truth["u0"]**2+((data.times-truth["t0"])/truth["tE_days"])**2
    amplification=(u2+2)/np.sqrt(u2*(u2+4))
    mean=truth["baseline_magnitude"]-2.5*np.log10(1+truth["source_fraction"]*(amplification-1))
    noise=data.errors*rng.standard_normal(len(data.rows))
    child=data.to_dict();child["sources"]=[]
    child["metadata"]={"synthetic":True,"purpose":"DEVELOPMENT_PILOT_ONLY","sampling_parent_sha256":data.sha256,
                       "inherited_instrument_metadata_role":"Original time/error sampling context only; no native child brightness."}
    if "relative_time_combination_assumption" in data.document.get("metadata",{}):
        child["metadata"]["relative_time_combination_assumption"]=deepcopy(data.document["metadata"]["relative_time_combination_assumption"])
    child["transformations"]=[{"operation":"SYNTHETIC_MAGNITUDE_REPLACEMENT","parent_input_sha256":data.sha256,"all_rows_replaced":True}]
    token=hashlib.sha256(raw_json(seed)).hexdigest()[:24]
    for index,(row,y) in enumerate(zip(child["rows"],mean+noise)):
        row["cadence_parent_source_row_id"]=row["source_row_id"]
        row["source_row_id"]=f"SYNTHETIC:PHOTOMETRY_V2_PILOT:{token}:{index}"
        for key in ("native_fields","source_file","source_line","source_sha256"):row.pop(key,None)
        row["magnitude"]=float(y)
        row["quality_flags"]=[*row.get("quality_flags",[]),"SYNTHETIC_MAGNITUDE"]
    return UnresolvedPhotometry(child),{"seed":seed,"rng_before":before,"rng_after":rng.bit_generator.state,
        "noise_sha256":hashlib.sha256(noise.tobytes()).hexdigest(),"sampling_parent_sha256":data.sha256}


def worker(args):
    freeze=load(args.freeze);check(freeze)
    spec=load(args.spec);out=Path(spec["output"])
    admission=load(spec["root_admission_path"])
    assert pin(spec["root_admission_path"])["sha256"]==spec["root_admission_sha256"]
    assert admission["freeze_sha256"]==pin(args.freeze)["sha256"] and admission["development_pilot_authorized"] is True
    out.mkdir(exist_ok=False)
    save(out/"ATTEMPT_STARTED.json",spec)
    from bhtracker.observations import UnresolvedPhotometry
    from bhtracker.photometry_inference import _seed_slots,monte_carlo_ordinate
    dataset=UnresolvedPhotometry(load(spec["dataset"]))
    assert dataset.sha256==spec["input_sha256"]
    seeds=_seed_slots(spec["entropy"],spec["parameter"],spec["value"],199)
    save(out/"ALL199_SEED_SLOTS.json",seeds)
    start=time.monotonic()
    journal=(out/"AUDIT.jsonl").open("xb")
    def audit(stage,slot,payload):
        if time.monotonic()-start>freeze["limits"]["per_ordinate_wall_seconds"]:
            raise TimeoutError("declared ordinate budget")
        if sum(p.stat().st_size for p in Path(spec["batch_output"]).rglob("*") if p.is_file())>freeze["limits"]["saved_bytes"]:
            raise OSError("declared storage budget")
        path=out/f"slot_{slot:03d}_{stage}.json.gz"
        if stage=="GENERATED":
            child=UnresolvedPhotometry(payload)
            token=hashlib.sha256(json.dumps(seeds[slot],separators=(",",":")).encode()).hexdigest()[:24]
            compact={"input_sha256":child.sha256,"magnitudes":[r["magnitude"] for r in child.rows],
                "row_count":len(child.rows),"parent_input_sha256":dataset.sha256,"seed":seeds[slot],
                "source_row_id_rule":f"SYNTHETIC:BOOTSTRAP:{token}:<zero_based_row_index>",
                "parent_row_id_order_sha256":hashlib.sha256(raw_json([r["source_row_id"] for r in dataset.rows])).hexdigest()}
            save_gzip(path,compact)
        else:save_gzip(path,payload)
        journal.write(raw_json({"stage":stage,"slot":slot,"payload":pin(path)}));journal.flush();os.fsync(journal.fileno())
    try:
        result=monte_carlo_ordinate(dataset,spec["parameter"],spec["value"],entropy=spec["entropy"],
            audit_callback=audit,**freeze["inference_options"])
        save_gzip(out/"FULL_ORDINATE_RESULT.json.gz",result)
        terminal={"test_id":spec["test_id"],"status":"RETURNED" if result["audit_failure"] is None else "RETURNED_AUDIT_UNRESOLVED","elapsed_seconds":time.monotonic()-start,
            "decision":result["rank_bounds"]["decision"],"attempted_slots":result["attempted_slots"],
            "p_bounds":result["rank_bounds"],"observed_status":result["observed_profile"]["status"],
            "result":pin(out/"FULL_ORDINATE_RESULT.json.gz"),"audit_failure":result["audit_failure"]}
    except Exception as exc:
        terminal={"test_id":spec["test_id"],"status":"FAILED_UNKNOWN","error":type(exc).__name__+": "+str(exc),"elapsed_seconds":time.monotonic()-start}
    finally:journal.close()
    terminal["not_confirmation"]=True
    save(out/"TERMINAL.json",terminal)


def run(args):
    global _created_output
    batch_start=time.monotonic();freeze=load(args.freeze);check(freeze)
    admission=load(args.admission)
    assert admission["freeze_sha256"]==pin(args.freeze)["sha256"] and admission["development_pilot_authorized"] is True
    out=Path(args.output);out.mkdir(exist_ok=False)
    _created_output=out
    save(out/"FREEZE_COPY.json",freeze);save(out/"ADMISSION_COPY.json",admission)
    ledger=[{"test_id":f"cell{cell}_rep{replicate}_{parameter}","status":"NOT_ATTEMPTED_UNKNOWN"}
            for cell in range(2) for replicate in range(2) for parameter in freeze["parameters"]]
    save(out/"ALL8_INITIAL_LEDGER.json",ledger)
    # Truth is separate from all fitter input and is never used for initialization.
    save(out/"GENERATING_TRUTHS.json",freeze["truth"])
    specs=[]
    for cell,parent_pin in enumerate(freeze["parents"]):
        parent=load(parent_pin["path"])
        for replicate in range(2):
            index=2*cell+replicate;seed=freeze["entropy"]["prefix"]+[0,cell,replicate]
            dataset,audit=outer_draw(parent,freeze["truth"][cell],seed)
            dataset_path=out/f"outer_{index}_INPUT.json";save(dataset_path,dataset.to_dict())
            save(out/f"outer_{index}_GENERATION.json",audit)
            for parameter_index,parameter in enumerate(freeze["parameters"]):
                test_id=f"cell{cell}_rep{replicate}_{parameter}"
                spec={"test_id":test_id,"dataset":str(dataset_path),"input_sha256":dataset.sha256,
                    "parameter":parameter,"value":freeze["truth"][cell][parameter],
                    "entropy":freeze["entropy"]["prefix"]+[1,index,parameter_index],
                    "output":str(out/test_id),"batch_output":str(out),
                    "root_admission_path":str(Path(args.admission).resolve()),"root_admission_sha256":pin(args.admission)["sha256"]}
                spec_path=out/(test_id+"_SPEC.json");save(spec_path,spec);specs.append((spec,spec_path))
    assert [s["test_id"] for s,p in specs]==[r["test_id"] for r in ledger]
    env=os.environ.copy()
    for name in ("PYTHONPATH","PYTHONHOME"):env.pop(name,None)
    env.update(freeze["threads"]);env.update(PYTHONNOUSERSITE="1",PYTHONDONTWRITEBYTECODE="1")
    for index,(spec,spec_path) in enumerate(specs):
        remaining=freeze["limits"]["batch_wall_seconds"]-(time.monotonic()-batch_start)
        if remaining<=0:break
        check(freeze)
        command=[sys.executable,"-B",str(Path(__file__).resolve()),"--worker","--freeze",str(Path(args.freeze).resolve()),"--spec",str(spec_path)]
        remaining=freeze["limits"]["batch_wall_seconds"]-(time.monotonic()-batch_start)
        if remaining<=0:break
        with (out/(spec["test_id"]+".log")).open("xb") as log:
            try:
                completed=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,
                    timeout=min(remaining,freeze["limits"]["per_ordinate_wall_seconds"]),check=False)
                terminal_path=Path(spec["output"])/"TERMINAL.json"
                if terminal_path.exists():
                    candidate=load(terminal_path)
                    if candidate.get("test_id")==spec["test_id"]:
                        ledger[index]=candidate
                    else:ledger[index]={"test_id":spec["test_id"],"status":"WORKER_IDENTITY_MISMATCH_UNKNOWN"}
                else:ledger[index]={"test_id":spec["test_id"],"status":"WORKER_FAILED_UNKNOWN"}
                ledger[index]["returncode"]=completed.returncode
                if completed.returncode!=0:ledger[index]["status"]="WORKER_NONZERO_UNKNOWN"
            except subprocess.TimeoutExpired:
                ledger[index]={"test_id":spec["test_id"],"status":"SUPERVISOR_TIMEOUT_UNKNOWN"}
        save(out/(spec["test_id"]+"_SUPERVISOR_TERMINAL.json"),ledger[index])
    check(freeze)
    save(out/"ALL8_TERMINAL_LEDGER.json",ledger)
    result={"schema":"bhsm.photometry_v2.development_pilot_result.v1","not_confirmation":True,"planned_ordinates":8,
        "terminal_records":ledger,"elapsed_seconds":time.monotonic()-batch_start,"source_pins_unchanged":True,
        "all_planned_cases_retained":len(ledger)==8,"status":"ALL_RETURNED" if all(r["status"]=="RETURNED" for r in ledger) else "FINISHED_WITH_UNRESOLVED_OR_UNATTEMPTED","release_hold_cleared":False}
    save(out/"PILOT_COMPLETED.json",result)
    print(json.dumps({"elapsed_seconds":result["elapsed_seconds"],"statuses":[r["status"] for r in ledger],"receipt":pin(out/"PILOT_COMPLETED.json")}))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--prepare",action="store_true");parser.add_argument("--worker",action="store_true")
    parser.add_argument("--freeze",type=Path,required=True);parser.add_argument("--parent0");parser.add_argument("--parent1")
    parser.add_argument("--admission");parser.add_argument("--output");parser.add_argument("--spec")
    args=parser.parse_args()
    if args.prepare:
        prepare(args)
    elif args.worker:worker(args)
    else:
        _created_output=None
        try:run(args)
        except Exception as exc:
            if _created_output is not None:
                initial_path=_created_output/"ALL8_INITIAL_LEDGER.json"
                if initial_path.exists():
                    ledger=load(initial_path)
                    for i,row in enumerate(ledger):
                        terminal=_created_output/(row["test_id"]+"_SUPERVISOR_TERMINAL.json")
                        if terminal.exists():
                            candidate=load(terminal)
                            if candidate.get("test_id")==row["test_id"]:ledger[i]=candidate
                    save(_created_output/"FAILED_BATCH_TERMINAL_LEDGER.json",ledger)
                save(_created_output/"BATCH_FAILURE.json",{"error":type(exc).__name__+": "+str(exc),"not_confirmation":True})
            raise
