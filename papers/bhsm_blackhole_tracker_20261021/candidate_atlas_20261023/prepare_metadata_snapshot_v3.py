"""Create a portable factual metadata snapshot without redistributing observations.

This preparation is separate from offline rebuilding. It verifies the original
input bytes and extracts only fields used by the candidate-inventory rules.
Native photometry, the complete2025 observational input, full article HTML and
the complete2015 catalog are deliberately absent from the snapshot.
"""
from pathlib import Path
import importlib.util
import json
import copy

HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("atlas_v3",HERE/"build_inventory_v3.py")
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

def main():
    original=json.loads((HERE/"INPUT_FREEZE_v2.json").read_bytes())
    sources={}; originals={}
    for role,entry in original["sources"].items():
        value=Path(entry["path"]).read_bytes()
        if len(value)!=entry["bytes"] or M.digest(value)!=entry["sha256"]:
            raise ValueError("Original source changed: "+role)
        originals[role]=value
        sources[role]=copy.deepcopy(entry)
    pilot=json.loads(originals["pilot_results"])
    selected={e["event_id"].rsplit("-",1)[1] for e in pilot}
    selected_lines=[line for line in originals["catalog2015"].decode().splitlines()
                    if line.strip() and line.split()[0] in selected]
    if len(selected_lines)!=100: raise ValueError("100 selected primary catalog rows")
    parser=M.TableParser("S2.T1.2"); parser.feed(originals["reanalysis2021"].decode("utf-8"))
    if not parser.rows: raise ValueError("2021 factual table absent")
    bench=json.loads(originals["benchmark_input"])
    minimal_bench={key:bench[key] for key in ["schema","data_version","target","sky_position_icrs_deg"]}
    snapshots={role:value for role,value in originals.items() if not role.startswith("older_native:") and role!="readme2016"}
    snapshots["catalog2015"]=("\n".join(selected_lines)+"\n").encode()
    snapshots["reanalysis2021"]=M.json_bytes({"table_id":"S2.T1.2","role":"PRINTED_FACTUAL_TABLE_CELLS_ONLY_NOT_ARTICLE_HTML","rows":parser.rows})
    snapshots["benchmark_input"]=M.json_bytes(minimal_bench)
    audit={"schema":"bhsm.candidate_inventory.native_availability_audit.v1",
           "status":"ORIGINAL_RAW_HASHES_VERIFIED_AT_SNAPSHOT_PREPARATION_NO_FIT_OR_REDUCTION",
           "native_observations_redistributed":False,"records":{}}
    acquisition=json.loads(originals["older_acquisition"])
    for row in acquisition["records"]:
        role="older_native:"+row["event_id"]; raw=originals[role]
        n=len(raw.decode().splitlines())
        if n!=row["numeric_rows"] or M.digest(raw)!=row["sha256"]: raise ValueError("Native acquisition mismatch")
        audit["records"][row["event_id"]]={"sha256":M.digest(raw),"bytes":len(raw),"numeric_rows":n,
            "original_bytes_verified_at_snapshot_preparation":True,"requested_url":row["requested_url"],
            "native_version":row["native_version"],"clock_scale":None,"covariance":None}
    snapshots["native_availability_audit"]=M.json_bytes(audit)
    sources["native_availability_audit"]={"path":None,"bytes":len(snapshots["native_availability_audit"]),
        "sha256":M.digest(snapshots["native_availability_audit"]),"url":None,"role":"DERIVED_PREPARATION_INTEGRITY_RECEIPT_NOT_OBSERVATIONS"}
    destination=HERE/"metadata_sources_v3"
    destination.mkdir(exist_ok=False)
    for role,entry in sources.items():
        if role not in snapshots:
            entry.update({"snapshot_path":None,"omission_reason":"RAW_OBSERVATIONS_NOT_BUNDLED" if role.startswith("older_native:") else "SOURCE_HASH_METADATA_ONLY_NOT_NEEDED_BY_ASSEMBLY"})
            continue
        suffix=".txt" if role in {"catalog2015","catalog2016","modes2016"} else ".json"
        name=role+suffix; payload=snapshots[role]
        with (destination/name).open("xb") as handle: handle.write(payload)
        entry.update({"snapshot_path":"metadata_sources_v3/"+name,"snapshot_bytes":len(payload),"snapshot_sha256":M.digest(payload)})
    derivations={"catalog2015":"100 original printed catalog lines selected by the already frozen pilot IDs; original full-catalog hash retained. No observation rows.",
        "reanalysis2021":"Only primary Table1 factual printed cells, including all8 event rows/modes and headers; no article HTML or narrative copied.",
        "benchmark_input":"Only schema, data-version, target and source-direction fields from the original native input; no photometry or astrometry rows.",
        "native_availability_audit":"26 raw-file hashes, byte sizes, original row counts and acquisition versions independently checked before snapshot creation; raw photometry not bundled and not reverified by offline rebuild.",
        "other_metadata":"Byte-identical existing derived results, aliases, protocols, factual catalogs and published fit-mode summaries. These are metadata, not manufactured observations."}
    freeze={"schema":"bhsm.blackhole_tracker.candidate_inventory_input_freeze.v3",
        "status":"SOURCE_FACT_SNAPSHOTS_ONLY_NO_MODEL_OR_FIT_CALLS","scientific_as_of":"2026-10-23",
        "verification_scope":"OFFLINE_METADATA_REBUILD_FROM_FACTUAL_SNAPSHOTS","formal_BHSM_repository":M.FORMAL,
        "formal_source_commit":M.COMMIT,"builder_sha256":M.digest((HERE/"build_inventory_v3.py").read_bytes()),
        "snapshot_preparer_sha256":M.digest(Path(__file__).read_bytes()),
        "original_input_freeze_v2_sha256":M.digest((HERE/"INPUT_FREEZE_v2.json").read_bytes()),
        "source_snapshot_derivations":derivations,"sources":sources}
    # Confirm nothing in the original source graph changed while extracting.
    for role,value in originals.items():
        if Path(original["sources"][role]["path"]).read_bytes()!=value:
            raise ValueError("Original source changed during snapshot preparation")
    with (HERE/"INPUT_FREEZE_v3.json").open("xb") as handle: handle.write(M.json_bytes(freeze))
    print(json.dumps({"status":"PORTABLE_FACTUAL_METADATA_SNAPSHOT_CREATED","original_sources_verified":len(originals),
        "snapshot_files":len(snapshots),"snapshot_bytes":sum(map(len,snapshots.values())),"raw_observations_bundled":0,
        "freeze_sha256":M.digest((HERE/"INPUT_FREEZE_v3.json").read_bytes())},indent=2))

if __name__=="__main__": main()
